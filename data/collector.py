"""
Data Collection Tool
Thu thập dataset để train ML classifier
"""
import cv2
import numpy as np
import csv
import os
from datetime import datetime
import argparse
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import FallDetector, MultiPersonTracker
from ai import FeatureExtractor
from utils import ConfigManager


class DataCollector:
    """
    Collect training data with labels
    """
    
    def __init__(self, config: dict, label: str, output_dir: str = 'data/datasets'):
        self.config = config
        self.label = label  # 'fall' or 'not_fall'
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        self.detector = FallDetector(config)
        self.tracker = MultiPersonTracker(config)
        self.feature_extractor = FeatureExtractor(config)
        
        # CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = os.path.join(
            output_dir, 
            f"features_{label}_{timestamp}.csv"
        )
        
        # Initialize CSV
        self.init_csv()
        
        # Stats
        self.num_samples = 0
    
    def init_csv(self):
        """Initialize CSV file with headers"""
        feature_names = self.feature_extractor.get_feature_names()
        headers = feature_names + ['label']
        
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        print(f"[COLLECTOR] CSV file created: {self.csv_file}")
        print(f"[COLLECTOR] Label: {self.label}")
        print(f"[COLLECTOR] Features: {len(feature_names)}")
    
    def collect(self, duration: int = 60, camera_source: int = 0):
        """
        Collect data from camera
        Args:
            duration: Collection duration in seconds
            camera_source: Camera index or video file path
        """
        cap = cv2.VideoCapture(camera_source)
        
        if not cap.isOpened():
            print(f"[ERROR] Cannot open camera: {camera_source}")
            return
        
        print(f"\n[COLLECTOR] Starting collection...")
        print(f"Duration: {duration} seconds")
        print(f"Label: {self.label}")
        print(f"\nInstructions:")
        print(f"  - If label='fall': Perform falling motions")
        print(f"  - If label='not_fall': Perform normal activities (walk, sit, bend)")
        print(f"  - Press 'q' to stop early")
        print(f"  - Press 's' to skip current sample")
        print(f"\nStarting in 3 seconds...\n")
        
        cv2.waitKey(3000)
        
        start_time = cv2.getTickCount() / cv2.getTickFrequency()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Check duration
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            elapsed = current_time - start_time
            
            if elapsed >= duration:
                break
            
            # Detect persons
            detections = self.detector.detect_persons(frame)
            
            # Update tracker
            tracks = self.tracker.update(detections)
            
            # Extract features and save
            for track_id, track in tracks.items():
                feature_dict = self.feature_extractor.get_feature_dict_for_logging(
                    track_id, track
                )
                
                if feature_dict is not None:
                    self.save_sample(feature_dict)
            
            # Visualize
            display = self.detector.draw_detections(frame, detections)
            
            # Draw info
            remaining = duration - elapsed
            info_text = f"Label: {self.label} | Time: {remaining:.1f}s | Samples: {self.num_samples}"
            cv2.putText(
                display, info_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )
            
            cv2.imshow('Data Collection', display)
            
            # Key controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Skip current samples
                for track_id in tracks.keys():
                    self.feature_extractor.reset_buffer(track_id)
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n[COLLECTOR] Collection completed!")
        print(f"Total samples: {self.num_samples}")
        print(f"Output file: {self.csv_file}")
    
    def save_sample(self, feature_dict: dict):
        """Save one sample to CSV"""
        feature_names = self.feature_extractor.get_feature_names()
        
        # Create row
        row = [feature_dict.get(name, 0.0) for name in feature_names]
        row.append(self.label)  # Add label
        
        # Write to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        self.num_samples += 1


def main():
    parser = argparse.ArgumentParser(description='Data Collection Tool')
    parser.add_argument(
        '--mode', 
        type=str, 
        required=True,
        choices=['fall', 'not_fall'],
        help='Label for collected data'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Collection duration in seconds (default: 60)'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera index (default: 0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/datasets',
        help='Output directory (default: data/datasets)'
    )
    
    args = parser.parse_args()
    
    # Load config
    config_manager = ConfigManager('../config.yaml')
    config = config_manager.config
    
    # Create collector
    collector = DataCollector(
        config=config,
        label=args.mode,
        output_dir=args.output
    )
    
    # Start collection
    collector.collect(
        duration=args.duration,
        camera_source=args.camera
    )


if __name__ == '__main__':
    main()
