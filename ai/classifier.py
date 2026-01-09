"""
ML Classifier Wrapper
Load và sử dụng trained sklearn model
"""
import numpy as np
import joblib
from typing import Dict, Optional
import os


class FallClassifier:
    """
    Wrapper for trained fall detection classifier
    """
    
    def __init__(self, config: dict):
        self.config = config
        ml_config = config.get('ml_classifier', {})
        
        self.enabled = ml_config.get('enabled', False)
        self.model_path = ml_config.get('model_path', 'ai/models/fall_classifier.pkl')
        self.confidence_threshold = ml_config.get('confidence_threshold', 0.7)
        
        self.model = None
        self.feature_names = None
        
        # Try to load model
        if self.enabled:
            self.load_model()
    
    def load_model(self) -> bool:
        """Load trained model from disk"""
        if not os.path.exists(self.model_path):
            print(f"[WARNING] Model not found at {self.model_path}")
            print("ML classifier disabled. Run data/train.py first.")
            self.enabled = False
            return False
        
        try:
            model_data = joblib.load(self.model_path)
            
            # Model can be saved as dict or just the model
            if isinstance(model_data, dict):
                self.model = model_data['model']
                self.feature_names = model_data.get('feature_names', None)
            else:
                self.model = model_data
            
            print(f"[INFO] Model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            self.enabled = False
            return False
    
    def predict(self, feature_vector: np.ndarray) -> Optional[Dict]:
        """
        Predict fall probability
        Args:
            feature_vector: numpy array of features
        Returns:
            {'class': 'fall' or 'not_fall', 'proba': float, 'confidence': float}
        """
        if not self.enabled or self.model is None:
            return None
        
        if feature_vector is None:
            return None
        
        try:
            # Reshape for single prediction
            if len(feature_vector.shape) == 1:
                feature_vector = feature_vector.reshape(1, -1)
            
            # Predict class
            prediction = self.model.predict(feature_vector)[0]
            
            # Get probability if available
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(feature_vector)[0]
                
                # Assuming binary classification: [not_fall, fall]
                fall_proba = proba[1] if len(proba) > 1 else proba[0]
                confidence = max(proba)
            else:
                # Model doesn't support probability
                fall_proba = 1.0 if prediction == 1 else 0.0
                confidence = 1.0
            
            result = {
                'class': 'fall' if prediction == 1 else 'not_fall',
                'proba': float(fall_proba),
                'confidence': float(confidence)
            }
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return None
    
    def is_confident_fall(self, prediction: Dict) -> bool:
        """Check if prediction is confident fall"""
        if prediction is None:
            return False
        
        return (
            prediction['class'] == 'fall' and 
            prediction['proba'] >= self.confidence_threshold
        )
    
    def is_confident_not_fall(self, prediction: Dict) -> bool:
        """Check if prediction is confident not fall"""
        if prediction is None:
            return False
        
        return (
            prediction['class'] == 'not_fall' and 
            prediction['proba'] >= self.confidence_threshold
        )


class DummyClassifier:
    """
    Dummy classifier for testing without trained model
    Always returns 'not_fall'
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.enabled = False
    
    def predict(self, feature_vector: np.ndarray) -> Optional[Dict]:
        """Always return not_fall"""
        return {
            'class': 'not_fall',
            'proba': 0.1,
            'confidence': 0.9
        }
    
    def is_confident_fall(self, prediction: Dict) -> bool:
        return False
    
    def is_confident_not_fall(self, prediction: Dict) -> bool:
        return True
