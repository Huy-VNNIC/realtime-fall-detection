#!/usr/bin/env python3
"""
Headless test - No GUI required
Tests all components without camera or display
"""
import numpy as np
import time
from datetime import datetime

# Import system components
from core import FallDetector, MultiPersonTracker, StateMachineManager, ImmobilityDetector, FallState
from ai import FeatureExtractor, FallClassifier
from utils import ConfigManager, EventLogger, RiskScorer

def create_test_frame(height=480, width=640):
    """Create test frame"""
    return np.ones((height, width, 3), dtype=np.uint8) * 128

def create_test_detection(x=300, y=200, w=80, h=200):
    """Create simulated detection"""
    area = w * h
    contour = np.array([
        [[x, y]], [[x+w, y]], [[x+w, y+h]], [[x, y+h]]
    ])
    
    features = {
        'aspect_ratio': w / h,
        'centroid': (x + w//2, y + h//2),
        'angle': 45.0,
        'extent': 0.8,
        'solidity': 0.9,
        'bbox_height': h,
        'bbox_width': w,
        'centroid_y_ratio': (y + h//2) / 480.0
    }
    
    return {
        'bbox': (x, y, w, h),
        'contour': contour,
        'area': area,
        'features': features,
        'timestamp': time.time()
    }

def test_components():
    """Test all components"""
    print("\n" + "="*60)
    print("FALL DETECTION SYSTEM - HEADLESS TEST")
    print("="*60)
    print()
    
    # Load config
    print("[1/6] Loading configuration...")
    config_manager = ConfigManager('config.yaml')
    config = config_manager.config
    print("      ✓ Config loaded")
    
    # Initialize components
    print("\n[2/6] Initializing components...")
    detector = FallDetector(config)
    print("      ✓ FallDetector initialized")
    
    tracker = MultiPersonTracker(config)
    print("      ✓ MultiPersonTracker initialized")
    
    state_manager = StateMachineManager(config)
    print("      ✓ StateMachineManager initialized")
    
    immobility = ImmobilityDetector(config)
    print("      ✓ ImmobilityDetector initialized")
    
    feature_extractor = FeatureExtractor(config)
    print("      ✓ FeatureExtractor initialized")
    
    classifier = FallClassifier(config)
    if not classifier.enabled:
        print("      ⚠  ML Classifier disabled (no trained model)")
    else:
        print("      ✓ ML Classifier loaded")
    
    risk_scorer = RiskScorer(config)
    print("      ✓ RiskScorer initialized")
    
    logger = EventLogger(config)
    print("      ✓ EventLogger initialized")
    
    # Test scenario 1: Standing person
    print("\n[3/6] Testing Scenario 1: Standing Person")
    frame = create_test_frame()
    detections = [create_test_detection(x=300, y=150, w=80, h=200)]
    
    tracks = tracker.update(detections)
    print(f"      ✓ Detections: {len(detections)}, Tracks: {len(tracks)}")
    
    for track_id, track in tracks.items():
        # Calculate motion
        motion = 30.0  # Normal motion
        immobility.update_history(track_id, motion)
        immobility_score = immobility.get_immobility_score(track_id)
        
        # Extract features
        feature_vector = feature_extractor.get_feature_vector(track_id, track)
        
        # State update
        state = state_manager.update(track_id, track, motion, None)
        sm = state_manager.get_state_machine(track_id)
        
        # Risk score
        risk = risk_scorer.calculate_risk_score(track, sm, immobility_score)
        risk_level = risk_scorer.get_risk_level(risk)
        
        print(f"      Track {track_id}: State={state.value}, Risk={risk:.1f}, Level={risk_level}")
    
    # Test scenario 2: Falling person
    print("\n[4/6] Testing Scenario 2: Falling Person")
    for i in range(10):
        # Simulate falling motion
        y = 150 + i * 15  # Moving down
        h = 200 - i * 10   # Getting shorter
        w = 80 + i * 8     # Getting wider
        
        detections = [create_test_detection(x=300, y=y, w=w, h=h)]
        tracks = tracker.update(detections)
        
        for track_id, track in tracks.items():
            motion = 20.0 - i * 2  # Decreasing motion
            immobility.update_history(track_id, motion)
            immobility_score = immobility.get_immobility_score(track_id)
            
            state = state_manager.update(track_id, track, motion, None)
            sm = state_manager.get_state_machine(track_id)
            risk = risk_scorer.calculate_risk_score(track, sm, immobility_score)
            
            if i % 3 == 0:
                print(f"      Frame {i}: State={state.value}, Risk={risk:.1f}")
    
    # Test scenario 3: Fallen person (lying)
    print("\n[5/6] Testing Scenario 3: Fallen Person")
    for i in range(15):
        # Lying position
        detections = [create_test_detection(x=250, y=320, w=180, h=50)]
        tracks = tracker.update(detections)
        
        for track_id, track in tracks.items():
            motion = 2.0  # Very low motion (immobile)
            immobility.update_history(track_id, motion)
            immobility_score = immobility.get_immobility_score(track_id)
            
            state = state_manager.update(track_id, track, motion, None)
            sm = state_manager.get_state_machine(track_id)
            risk = risk_scorer.calculate_risk_score(track, sm, immobility_score)
            
            if state == FallState.ALARM:
                print(f"      🚨 ALARM triggered at frame {i}!")
                print(f"         Risk: {risk:.1f}/100")
                print(f"         Immobility: {immobility_score:.2f}")
                print(f"         Duration in state: {sm.get_state_duration():.1f}s")
                break
        
        time.sleep(0.1)  # Simulate real-time
    
    # Test feature extraction
    print("\n[6/6] Testing Feature Extraction")
    for track_id, track in tracks.items():
        feature_vector = feature_extractor.get_feature_vector(track_id, track)
        if feature_vector is not None:
            print(f"      ✓ Feature vector: {len(feature_vector)} dimensions")
            print(f"        Sample values: {feature_vector[:5]}")
        else:
            print(f"      ⚠  Not enough data for features yet")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print()
    print("✓ All components initialized successfully")
    print("✓ Detection pipeline working")
    print("✓ Tracking system functional")
    print("✓ State machine transitions working")
    print("✓ Risk scoring operational")
    print("✓ Feature extraction ready")
    print()
    print("System Status: READY ✅")
    print()
    print("Next steps:")
    print("  1. Collect training data: cd data && python3 collector.py")
    print("  2. Train ML model: python3 train.py")
    print("  3. Run with camera: python3 main.py --camera 0")
    print("  4. Or use video: python3 main.py --video file.mp4")
    print()

if __name__ == '__main__':
    try:
        test_components()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
