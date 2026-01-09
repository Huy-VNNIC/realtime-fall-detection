"""
Deep Learning Models for Advanced Fall Detection
Includes CNN, LSTM, Pose estimation, and Transformer-based models
"""
import numpy as np
from typing import Dict, Optional, Tuple
import os

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[INFO] PyTorch not available. Deep learning features disabled.")
    print("      Install with: pip install torch torchvision")


# Define PyTorch models only if available
if TORCH_AVAILABLE:
    class CNNLSTMFallDetector(nn.Module):
        """Hybrid CNN-LSTM model for fall detection"""
        
        def __init__(self, input_shape=(3, 224, 224), lstm_hidden=128, num_classes=2):
            super(CNNLSTMFallDetector, self).__init__()
            
            self.cnn = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.BatchNorm2d(32),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.BatchNorm2d(64),
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.BatchNorm2d(128),
                nn.AdaptiveAvgPool2d((7, 7))
            )
            
            self.lstm_input_size = 128 * 7 * 7
            self.lstm = nn.LSTM(
                input_size=self.lstm_input_size,
                hidden_size=lstm_hidden,
                num_layers=2,
                batch_first=True,
                dropout=0.3
            )
            
            self.fc = nn.Sequential(
                nn.Linear(lstm_hidden, 64),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(64, num_classes)
            )
        
        def forward(self, x):
            batch_size, seq_len, c, h, w = x.size()
            cnn_features = []
            for t in range(seq_len):
                frame = x[:, t, :, :, :]
                features = self.cnn(frame)
                features = features.view(batch_size, -1)
                cnn_features.append(features)
            
            cnn_features = torch.stack(cnn_features, dim=1)
            lstm_out, _ = self.lstm(cnn_features)
            last_output = lstm_out[:, -1, :]
            logits = self.fc(last_output)
            
            return logits
else:
    # Placeholder classes
    class CNNLSTMFallDetector:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch required. Install: pip install torch")


class PoseBasedFallDetector:
    """Pose estimation-based fall detection using MediaPipe"""
    
    def __init__(self):
        self.mp_available = False
        
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_available = True
            print("[INFO] MediaPipe Pose initialized")
        except ImportError:
            print("[INFO] MediaPipe not available. Install with: pip install mediapipe")
    
    def extract_pose_features(self, frame) -> Optional[Dict]:
        """Extract pose keypoints from frame"""
        if not self.mp_available:
            return None
        
        import cv2
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        if not results.pose_landmarks:
            return None
        
        landmarks = results.pose_landmarks.landmark
        
        # Key body parts
        nose = landmarks[0]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        
        # Calculate features
        features = {}
        
        shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_center_y = (left_hip.y + right_hip.y) / 2
        
        vertical_diff = abs(shoulder_center_y - hip_center_y)
        features['body_vertical_angle'] = np.arctan(vertical_diff) * 180 / np.pi
        features['head_height'] = 1.0 - nose.y
        
        shoulder_width = abs(left_shoulder.x - right_shoulder.x)
        body_height = abs(shoulder_center_y - hip_center_y)
        features['body_aspect_ratio'] = shoulder_width / max(body_height, 0.01)
        
        features['hip_height'] = 1.0 - hip_center_y
        features['com_x'] = (nose.x + shoulder_center_y + hip_center_y) / 3
        features['com_y'] = (nose.y + shoulder_center_y + hip_center_y) / 3
        features['pose_confidence'] = np.mean([lm.visibility for lm in landmarks])
        
        return features
    
    def detect_fall_from_pose(self, features: Dict) -> Tuple[bool, float]:
        """Rule-based fall detection from pose features"""
        if not features:
            return False, 0.0
        
        score = 0.0
        
        if features['head_height'] < 0.3:
            score += 0.4
        
        if features['body_aspect_ratio'] > 1.5:
            score += 0.3
        
        if features['body_vertical_angle'] < 45:
            score += 0.2
        
        if features['hip_height'] < 0.25:
            score += 0.1
        
        is_fall = score > 0.6
        
        return is_fall, score


class EnsembleDetector:
    """Ensemble multiple models for robust detection"""
    
    def __init__(self, config: dict):
        self.config = config
        self.models = []
        self.weights = []
        
        self._init_models()
    
    def _init_models(self):
        """Initialize all available models"""
        from ai.classifier import FallClassifier
        ml_model = FallClassifier(self.config)
        if ml_model.enabled:
            self.models.append(('ml', ml_model))
            self.weights.append(0.4)
        
        pose_model = PoseBasedFallDetector()
        if pose_model.mp_available:
            self.models.append(('pose', pose_model))
            self.weights.append(0.3)
        
        if self.weights:
            total = sum(self.weights)
            self.weights = [w / total for w in self.weights]
    
    def predict(self, frame, features, track) -> Dict:
        """Ensemble prediction from multiple models"""
        if not self.models:
            return None
        
        predictions = []
        
        for (model_type, model), weight in zip(self.models, self.weights):
            if model_type == 'ml':
                pred = model.predict(features)
                if pred:
                    predictions.append((pred['proba'], weight))
            
            elif model_type == 'pose':
                pose_features = model.extract_pose_features(frame)
                is_fall, score = model.detect_fall_from_pose(pose_features)
                predictions.append((score if is_fall else 0.0, weight))
        
        if predictions:
            fall_proba = sum(p[0] * p[1] for p in predictions)
            confidence = max(p[0] for p in predictions)
            
            return {
                'class': 'fall' if fall_proba > 0.5 else 'not_fall',
                'proba': fall_proba,
                'confidence': confidence,
                'ensemble_size': len(predictions)
            }
        
        return None


# Export
__all__ = [
    'CNNLSTMFallDetector',
    'PoseBasedFallDetector', 
    'EnsembleDetector'
]
