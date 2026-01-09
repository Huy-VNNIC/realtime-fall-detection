"""
XGBoost Classifier for Fall Detection
Better performance than Random Forest for structured data
"""
import numpy as np
import joblib
from typing import Dict, Optional
import os


class XGBoostFallClassifier:
    """
    XGBoost-based fall classifier
    Better accuracy and speed than Random Forest
    """
    
    def __init__(self, config: dict):
        self.config = config
        ml_config = config.get('ml_classifier', {})
        
        self.enabled = ml_config.get('use_xgboost', False)
        self.model_path = ml_config.get('xgboost_model_path', 'ai/models/xgboost_fall_classifier.pkl')
        self.confidence_threshold = ml_config.get('confidence_threshold', 0.7)
        
        self.model = None
        self.feature_names = None
        self.xgb_available = False
        
        # Check if XGBoost is available
        try:
            import xgboost as xgb
            self.xgb_available = True
            print("[INFO] XGBoost available")
        except ImportError:
            print("[INFO] XGBoost not available. Install with: pip install xgboost")
            self.enabled = False
        
        # Try to load model
        if self.enabled and self.xgb_available:
            self.load_model()
    
    def load_model(self) -> bool:
        """Load trained XGBoost model"""
        if not os.path.exists(self.model_path):
            print(f"[INFO] XGBoost model not found at {self.model_path}")
            self.enabled = False
            return False
        
        try:
            model_data = joblib.load(self.model_path)
            
            if isinstance(model_data, dict):
                self.model = model_data['model']
                self.feature_names = model_data.get('feature_names', None)
            else:
                self.model = model_data
            
            print(f"[INFO] XGBoost model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load XGBoost model: {e}")
            self.enabled = False
            return False
    
    def predict(self, feature_vector: np.ndarray) -> Optional[Dict]:
        """
        Predict fall probability using XGBoost
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
            import xgboost as xgb
            
            # Reshape for single prediction
            if len(feature_vector.shape) == 1:
                feature_vector = feature_vector.reshape(1, -1)
            
            # Convert to DMatrix for XGBoost
            dmatrix = xgb.DMatrix(feature_vector, feature_names=self.feature_names)
            
            # Predict probability
            proba = self.model.predict(dmatrix)[0]
            
            # XGBoost outputs probability for positive class directly
            fall_proba = float(proba)
            prediction_class = 1 if fall_proba > 0.5 else 0
            confidence = fall_proba if fall_proba > 0.5 else (1 - fall_proba)
            
            result = {
                'class': 'fall' if prediction_class == 1 else 'not_fall',
                'proba': fall_proba,
                'confidence': float(confidence)
            }
            
            return result
            
        except Exception as e:
            print(f"[ERROR] XGBoost prediction failed: {e}")
            return None
    
    def is_confident_fall(self, prediction: Dict) -> bool:
        """Check if prediction is confident fall"""
        if prediction is None:
            return False
        
        return (
            prediction['class'] == 'fall' and 
            prediction['proba'] >= self.confidence_threshold
        )
    
    def get_feature_importance(self) -> Optional[Dict]:
        """Get feature importance from XGBoost model"""
        if not self.enabled or self.model is None:
            return None
        
        try:
            # Get importance scores
            importance_dict = self.model.get_score(importance_type='gain')
            
            # Sort by importance
            sorted_importance = sorted(
                importance_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return dict(sorted_importance)
            
        except Exception as e:
            print(f"[ERROR] Failed to get feature importance: {e}")
            return None
    
    def predict_with_explanation(self, feature_vector: np.ndarray) -> Optional[Dict]:
        """
        Predict with SHAP explanation
        Requires shap package: pip install shap
        """
        prediction = self.predict(feature_vector)
        
        if prediction is None:
            return None
        
        try:
            import shap
            
            # Create explainer
            explainer = shap.TreeExplainer(self.model)
            
            # Get SHAP values
            shap_values = explainer.shap_values(feature_vector)
            
            # Add explanation to result
            prediction['shap_values'] = shap_values.tolist()
            prediction['base_value'] = float(explainer.expected_value)
            
            # Top contributing features
            if self.feature_names:
                abs_shap = np.abs(shap_values[0])
                top_indices = np.argsort(abs_shap)[-5:][::-1]
                
                prediction['top_features'] = [
                    {
                        'name': self.feature_names[i],
                        'value': float(feature_vector[0, i]),
                        'contribution': float(shap_values[0, i])
                    }
                    for i in top_indices
                ]
            
            return prediction
            
        except ImportError:
            print("[INFO] SHAP not available. Install with: pip install shap")
            return prediction
        except Exception as e:
            print(f"[WARNING] SHAP explanation failed: {e}")
            return prediction


class OnlineLearningClassifier:
    """
    Online learning classifier that updates with user feedback
    Implements incremental learning for continuous improvement
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Use SGDClassifier for online learning
        try:
            from sklearn.linear_model import SGDClassifier
            from sklearn.preprocessing import StandardScaler
            
            self.model = SGDClassifier(
                loss='log_loss',  # For probability estimates
                learning_rate='optimal',
                max_iter=1000,
                warm_start=True  # Enable incremental learning
            )
            self.scaler = StandardScaler()
            self.is_fitted = False
            
            print("[INFO] Online learning classifier initialized")
            
        except ImportError:
            print("[ERROR] sklearn not available")
            self.model = None
    
    def partial_fit(self, X: np.ndarray, y: np.ndarray):
        """
        Update model with new data
        Args:
            X: Features (n_samples, n_features)
            y: Labels (n_samples,) - 0 or 1
        """
        if self.model is None:
            return
        
        try:
            # Scale features
            if not self.is_fitted:
                X_scaled = self.scaler.fit_transform(X)
                self.model.partial_fit(X_scaled, y, classes=[0, 1])
                self.is_fitted = True
            else:
                X_scaled = self.scaler.transform(X)
                self.model.partial_fit(X_scaled, y)
            
            print(f"[ONLINE_LEARNING] Model updated with {len(y)} samples")
            
        except Exception as e:
            print(f"[ERROR] Online learning update failed: {e}")
    
    def predict(self, feature_vector: np.ndarray) -> Optional[Dict]:
        """Predict with online model"""
        if not self.is_fitted:
            return None
        
        try:
            # Scale
            if len(feature_vector.shape) == 1:
                feature_vector = feature_vector.reshape(1, -1)
            
            X_scaled = self.scaler.transform(feature_vector)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            proba = self.model.predict_proba(X_scaled)[0]
            
            return {
                'class': 'fall' if prediction == 1 else 'not_fall',
                'proba': float(proba[1]),
                'confidence': float(max(proba))
            }
            
        except Exception as e:
            print(f"[ERROR] Online prediction failed: {e}")
            return None
    
    def add_user_feedback(self, feature_vector: np.ndarray, is_fall: bool):
        """
        Add user feedback to improve model
        Called when user confirms/corrects a prediction
        """
        label = 1 if is_fall else 0
        self.partial_fit(feature_vector, np.array([label]))


# Export
__all__ = ['XGBoostFallClassifier', 'OnlineLearningClassifier']
