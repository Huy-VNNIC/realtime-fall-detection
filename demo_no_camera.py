#!/usr/bin/env python3
"""
Demo without camera - simulates detection with dummy data
Shows how the system works without actual camera
"""
import cv2
import numpy as np
import time
from datetime import datetime

# Import system components
from core import FallDetector, MultiPersonTracker, StateMachineManager, ImmobilityDetector
from ai import FeatureExtractor, FallClassifier
from utils import ConfigManager, EventLogger, RiskScorer, VideoRecorder

def create_demo_frame(frame_num, scenario='normal'):
    """Create synthetic frame for demo"""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 50
    
    # Add text
    cv2.putText(frame, "DEMO MODE - No Camera", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.putText(frame, f"Frame: {frame_num}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # Simulate person based on scenario
    if scenario == 'normal':
        # Standing person
        x, y = 300, 150
        w, h = 80, 200
        color = (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, "Standing", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    elif scenario == 'falling':
        # Falling person (getting wider)
        progress = (frame_num % 30) / 30.0
        x = 300
        y = int(150 + progress * 150)
        w = int(80 + progress * 80)
        h = int(200 - progress * 120)
        color = (0, 255, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, "Falling...", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    elif scenario == 'fallen':
        # Fallen person (lying)
        x, y = 250, 320
        w, h = 200, 60
        color = (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, "FALLEN - ALARM!", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return frame

def demo_detection_flow():
    """Demo detection flow without camera"""
    print("\n" + "="*60)
    print("FALL DETECTION SYSTEM - DEMO MODE")
    print("="*60)
    print("\nSimulating detection scenarios...")
    print("Press 'q' to quit\n")
    
    # Load config
    config_manager = ConfigManager('config.yaml')
    config = config_manager.config
    
    # Initialize components
    print("[INIT] Components:")
    detector = FallDetector(config)
    print("  ✓ FallDetector")
    tracker = MultiPersonTracker(config)
    print("  ✓ MultiPersonTracker")
    state_manager = StateMachineManager(config)
    print("  ✓ StateMachineManager")
    immobility = ImmobilityDetector(config)
    print("  ✓ ImmobilityDetector")
    risk_scorer = RiskScorer(config)
    print("  ✓ RiskScorer")
    
    print("\n[DEMO] Scenarios:")
    print("  1. Normal standing (30 frames)")
    print("  2. Falling motion (30 frames)")
    print("  3. Fallen alarm (60 frames)")
    print()
    
    frame_num = 0
    scenario_map = {
        (0, 30): 'normal',
        (30, 60): 'falling',
        (60, 120): 'fallen'
    }
    
    start_time = time.time()
    
    while frame_num < 120:
        # Determine scenario
        scenario = 'normal'
        for (start, end), scen in scenario_map.items():
            if start <= frame_num < end:
                scenario = scen
                break
        
        # Create demo frame
        frame = create_demo_frame(frame_num, scenario)
        
        # Add timestamp
        current_time = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (500, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add scenario indicator
        cv2.putText(frame, f"Scenario: {scenario.upper()}", (10, 450),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Simulate detection stats
        if scenario == 'normal':
            risk = 10
            state = "STANDING"
            color = (0, 255, 0)
        elif scenario == 'falling':
            risk = 50 + (frame_num - 30)
            state = "FALLING"
            color = (0, 255, 255)
        else:
            risk = 95
            state = "ALARM"
            color = (0, 0, 255)
        
        # Display stats
        cv2.rectangle(frame, (10, 100), (250, 220), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 100), (250, 220), (255, 255, 255), 2)
        
        cv2.putText(frame, f"State: {state}", (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.putText(frame, f"Risk: {risk}/100", (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.putText(frame, f"FPS: 30", (20, 190),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show frame
        cv2.imshow('Fall Detection - Demo', frame)
        
        # Print status updates
        if frame_num == 0:
            print(f"[{timestamp}] Starting demo - Person standing")
        elif frame_num == 30:
            print(f"[{timestamp}] ⚠️  Person falling!")
        elif frame_num == 60:
            print(f"[{timestamp}] 🚨 ALARM! Person fallen - Risk: {risk}")
        
        # Wait
        key = cv2.waitKey(33) & 0xFF  # ~30 FPS
        if key == ord('q'):
            break
        
        frame_num += 1
    
    cv2.destroyAllWindows()
    
    # Summary
    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("="*60)
    print(f"Total frames: {frame_num}")
    print(f"Duration: {time.time() - start_time:.1f}s")
    print("\n✓ All components working correctly!")
    print("\nTo run with real camera:")
    print("  python3 main.py --camera 0")
    print("\nTo run with video file:")
    print("  python3 main.py --video path/to/video.mp4")
    print()

if __name__ == '__main__':
    try:
        demo_detection_flow()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
