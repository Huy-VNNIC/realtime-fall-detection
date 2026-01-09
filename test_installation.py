#!/usr/bin/env python3
"""
Test script to verify installation
"""
import sys

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV")
    except:
        print("✗ OpenCV - run: pip install opencv-python")
        return False
    
    try:
        import numpy
        print("✓ NumPy")
    except:
        print("✗ NumPy - run: pip install numpy")
        return False
    
    try:
        import sklearn
        print("✓ scikit-learn")
    except:
        print("✗ scikit-learn - run: pip install scikit-learn")
        return False
    
    try:
        import yaml
        print("✓ PyYAML")
    except:
        print("✗ PyYAML - run: pip install pyyaml")
        return False
    
    try:
        import websockets
        print("✓ websockets")
    except:
        print("✗ websockets - run: pip install websockets")
        return False
    
    try:
        import psutil
        print("✓ psutil")
    except:
        print("✗ psutil - run: pip install psutil")
        return False
    
    return True

def test_camera():
    """Test camera access"""
    print("\nTesting camera...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                print(f"✓ Camera working (frame shape: {frame.shape})")
                return True
            else:
                print("✗ Camera opened but cannot read frame")
                return False
        else:
            print("✗ Cannot open camera")
            return False
    except Exception as e:
        print(f"✗ Camera test error: {e}")
        return False

def test_modules():
    """Test custom modules"""
    print("\nTesting custom modules...")
    
    try:
        from core import FallDetector, MultiPersonTracker, StateMachineManager
        print("✓ Core modules")
    except Exception as e:
        print(f"✗ Core modules: {e}")
        return False
    
    try:
        from ai import FeatureExtractor, FallClassifier
        print("✓ AI modules")
    except Exception as e:
        print(f"✗ AI modules: {e}")
        return False
    
    try:
        from utils import ConfigManager, EventLogger, RiskScorer, VideoRecorder
        print("✓ Utils modules")
    except Exception as e:
        print(f"✗ Utils modules: {e}")
        return False
    
    try:
        from api import WebSocketServer, AlertHandler
        print("✓ API modules")
    except Exception as e:
        print(f"✗ API modules: {e}")
        return False
    
    return True

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from utils import ConfigManager
        config = ConfigManager('config.yaml')
        print("✓ Config loaded")
        print(f"  Camera source: {config.config['camera']['source']}")
        print(f"  ML enabled: {config.config['ml_classifier']['enabled']}")
        print(f"  API enabled: {config.config['ios_api']['enabled']}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def main():
    print("="*50)
    print("Fall Detection System - Installation Test")
    print("="*50)
    print()
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test camera
    results.append(("Camera", test_camera()))
    
    # Test modules
    results.append(("Modules", test_modules()))
    
    # Test config
    results.append(("Config", test_config()))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary:")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("\n✓ All tests passed! System ready to use.")
        print("\nQuick start:")
        print("  1. Collect data: cd data && python collector.py --mode fall --duration 60")
        print("  2. Train model: python train.py")
        print("  3. Run system: python ../main.py")
        print("\nOr use: ./quickstart.sh")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
