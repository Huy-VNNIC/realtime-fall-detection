"""
Main Fall Detection Application
Realtime fall detection với tất cả features
"""
import cv2
import time
import argparse
import psutil
from datetime import datetime

# Import modules
from core import (
    FallDetector, 
    MultiPersonTracker, 
    StateMachineManager,
    FallState,
    ImmobilityDetector
)
from core.pose_detector import PoseDetector, draw_skeleton  # ★ Pose-based detector
from ai import FeatureExtractor, FallClassifier
from utils import (
    ConfigManager,
    EventLogger,
    RiskScorer,
    VideoRecorder
)
from api import WebSocketServer, AlertHandler


class FallDetectionSystem:
    """
    Main fall detection system
    Tích hợp tất cả components
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        # Load config
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        
        print("\n" + "="*60)
        print("FALL DETECTION SYSTEM - Professional Edition")
        print("="*60 + "\n")
        
        # Initialize components
        print("[INIT] Initializing components...")
        
        # ★ Dùng PoseDetector thay vì FallDetector (contour-based)
        self.detector = PoseDetector(self.config)
        self.tracker = MultiPersonTracker(self.config)
        self.state_manager = StateMachineManager(self.config)
        self.immobility_detector = ImmobilityDetector(self.config)
        
        # AI components
        self.feature_extractor = FeatureExtractor(self.config)
        self.classifier = FallClassifier(self.config)
        
        # Utilities
        self.logger = EventLogger(self.config)
        self.risk_scorer = RiskScorer(self.config)
        self.recorder = VideoRecorder(self.config)
        
        # API
        self.websocket_server = WebSocketServer(self.config)
        self.alert_handler = AlertHandler(self.config, self.websocket_server)
        
        # System state
        self.frame_count = 0
        self.fps = 0
        self.start_time = time.time()
        
        print("[INIT] Initialization complete!\n")
    
    def run(self, camera_source=None):
        """Run main detection loop"""
        
        # Get camera source
        if camera_source is None:
            camera_source = self.config['camera']['source']
        
        # Open camera
        cap = cv2.VideoCapture(camera_source)
        
        if not cap.isOpened():
            print(f"[ERROR] Cannot open camera: {camera_source}")
            return
        
        # Set camera properties
        cam_config = self.config['camera']
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_config['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_config['height'])
        cap.set(cv2.CAP_PROP_FPS, cam_config['fps'])
        
        # Start API server
        self.websocket_server.start()
        
        print("\n[SYSTEM] Starting detection...")
        print("Press 'q' to quit\n")
        
        # FPS calculation
        fps_start_time = time.time()
        fps_frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[WARNING] Failed to read frame")
                    break
                
                current_time = time.time()
                
                # Process frame
                self._process_frame(frame, current_time)
                
                # Calculate FPS
                fps_frame_count += 1
                if current_time - fps_start_time >= 1.0:
                    self.fps = fps_frame_count / (current_time - fps_start_time)
                    fps_start_time = current_time
                    fps_frame_count = 0
                
                # Display
                if self.config['debug']['show_video']:
                    display = self._create_display(frame)
                    cv2.imshow('Fall Detection System', display)
                
                # Key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n[SYSTEM] Interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.websocket_server.stop()
            print("\n[SYSTEM] Shutdown complete")
    
    def _process_frame(self, frame, timestamp):
        """Process single frame"""
        
        # Add frame to recorder buffer
        self.recorder.add_frame(frame, timestamp)
        
        # Detect persons
        detections = self.detector.detect_persons(frame)
        
        # Update tracker
        tracks = self.tracker.update(detections)
        
        # Process each person
        for track_id, track in tracks.items():
            self._process_person(track_id, track, timestamp, frame)
        
        # Log system stats periodically
        if self.frame_count % 300 == 0:  # Every 10 seconds at 30fps
            self._log_system_stats()
    
    def _process_person(self, track_id, track, timestamp, frame):
        """Process single person track"""
        
        # Calculate motion energy (for immobility)
        motion_energy = self.detector.calculate_motion_energy(track.last_bbox)
        self.immobility_detector.update_history(track_id, motion_energy)
        immobility_score = self.immobility_detector.get_immobility_score(track_id)
        
        # Extract features for ML
        feature_vector = self.feature_extractor.get_feature_vector(track_id, track)
        
        # ML prediction
        ml_prediction = None
        if feature_vector is not None:
            ml_prediction = self.classifier.predict(feature_vector)
        
        # Update state machine
        state = self.state_manager.update(
            track_id, track, motion_energy, ml_prediction
        )
        
        # Get state machine object
        sm = self.state_manager.get_state_machine(track_id)
        
        if sm is None:
            return
        
        # Calculate risk score
        risk_score = self.risk_scorer.calculate_risk_score(
            track, sm, immobility_score, ml_prediction
        )
        
        # Handle alarms
        self._handle_alerts(
            track_id, track, sm, risk_score, 
            timestamp, frame, ml_prediction
        )
    
    def _handle_alerts(
        self, track_id, track, sm, risk_score, 
        timestamp, frame, ml_prediction
    ):
        """Handle alarm/warning triggers"""
        
        risk_level = self.risk_scorer.get_risk_level(risk_score)
        
        # ALARM state
        if sm.current_state == FallState.ALARM:
            if not sm.alarm_triggered or sm.alarm_time is None:
                return
            
            # Check if we already processed this alarm
            time_since_alarm = timestamp - sm.alarm_time
            
            if 0.1 < time_since_alarm < 0.5:  # Process once
                # Save snapshot immediately
                event_id = f"{int(timestamp)}"
                snapshot_path = self.recorder.save_immediate_snapshot(
                    frame, event_id, track_id
                )
                
                # Start recording event
                self.recorder.start_event_recording(timestamp)
                
                # Trigger alarm
                self.alert_handler.trigger_alarm(
                    track_id=track_id,
                    risk_score=risk_score,
                    state=sm.current_state.value,
                    snapshot_path=snapshot_path,
                    features=track.last_features
                )
                
                # Log event
                self.logger.log_event(
                    event_type='ALARM',
                    track_id=track_id,
                    risk_score=risk_score,
                    state=sm.current_state.value,
                    snapshot_path=snapshot_path,
                    features=track.last_features,
                    ml_prediction=ml_prediction
                )
            
            # Stop recording after N seconds
            elif time_since_alarm > 5.0:  # 5 seconds after alarm
                if self.recorder.is_recording_event:
                    event_id = f"{int(sm.alarm_time)}"
                    _, video_path = self.recorder.stop_event_recording(
                        event_id, track_id
                    )
        
        # WARNING level (not full alarm yet)
        elif risk_level == 'warning' and sm.current_state == FallState.FALLING:
            self.alert_handler.trigger_warning(
                track_id=track_id,
                risk_score=risk_score,
                state=sm.current_state.value
            )
    
    def _create_display(self, frame):
        """Create display frame with overlays"""
        display = frame.copy()
        
        # Draw detections and tracks
        tracks = self.tracker.get_all_tracks()
        
        for track_id, track in tracks.items():
            x, y, w, h = track.last_bbox
            
            # Get state and risk
            sm = self.state_manager.get_state_machine(track_id)
            if sm is None:
                continue
            
            state = sm.current_state
            
            # Calculate risk (simplified for display)
            immobility_score = self.immobility_detector.get_immobility_score(track_id)
            risk_score = self.risk_scorer.calculate_risk_score(
                track, sm, immobility_score
            )
            
            # Get color based on risk
            color = self.risk_scorer.get_risk_color(risk_score)
            
            # ★ Vẽ skeleton thay vì bbox (giống hình 4)
            kp = getattr(track, 'last_keypoints', None)
            if kp is not None:
                draw_skeleton(display, kp, kpt_th=0.30, thickness=2)
            
            # Vẫn vẽ bbox mỏng nếu muốn (optional)
            # thickness = 1 if state != FallState.ALARM else 2
            # cv2.rectangle(display, (x, y), (x+w, y+h), color, thickness)
            
            # ★ Draw info giống hình 4: confidence - ID
            pose_conf = track.detections[-1].get('pose_conf', 0.0) if track.detections else 0.0
            info_text = f"{pose_conf:.2f} - id_{track_id} - {state.value}"
            cv2.putText(
                display, info_text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )
            
            # Draw risk score
            risk_text = f"Risk: {risk_score:.0f}"
            cv2.putText(
                display, risk_text, (x, y + h + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )
            
            # ★ Debug: hiển thị pose features (optional, comment out nếu không muốn)
            if self.config.get('debug', {}).get('show_pose_debug', False):
                torso_angle = features.get('torso_angle', 0.0)
                hip_drop = track.get_hip_drop()
                hip_speed = track.get_hip_speed_norm()
                debug_text = f"Angle:{torso_angle:.0f} Drop:{hip_drop:.2f} Speed:{hip_speed:.2f}"
                cv2.putText(
                    display, debug_text, (x, y + h + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1
                )
        
        # Draw system info
        self._draw_system_info(display)
        
        return display
    
    def _draw_system_info(self, frame):
        """Draw system info overlay"""
        h, w = frame.shape[:2]
        
        # Background for info
        cv2.rectangle(frame, (10, 10), (400, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (400, 120), (255, 255, 255), 2)
        
        # System info
        info_lines = [
            f"FPS: {self.fps:.1f}",
            f"Tracks: {len(self.tracker.get_all_tracks())}",
            f"Alarms: {len(self.state_manager.get_alarms())}",
            f"Uptime: {int(time.time() - self.start_time)}s"
        ]
        
        y_offset = 35
        for line in info_lines:
            cv2.putText(
                frame, line, (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )
            y_offset += 25
    
    def _log_system_stats(self):
        """Log system statistics"""
        cpu_usage = psutil.cpu_percent()
        num_tracks = len(self.tracker.get_all_tracks())
        num_alarms = len(self.state_manager.get_alarms())
        
        self.logger.log_system_stats(
            fps=self.fps,
            cpu_usage=cpu_usage,
            num_tracks=num_tracks,
            num_alarms=num_alarms
        )


def main():
    parser = argparse.ArgumentParser(
        description='Fall Detection System - Professional Edition'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Config file path'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=None,
        help='Camera index (override config)'
    )
    parser.add_argument(
        '--video',
        type=str,
        default=None,
        help='Video file path (instead of camera)'
    )
    
    args = parser.parse_args()
    
    # Create system
    system = FallDetectionSystem(config_path=args.config)
    
    # Determine camera source
    camera_source = args.camera
    if args.video:
        camera_source = args.video
    
    # Run
    system.run(camera_source=camera_source)


if __name__ == '__main__':
    main()
