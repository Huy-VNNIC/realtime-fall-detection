"""
Feature Extractor for ML Classifier
Extract temporal features từ chuỗi frames để train ML model
"""
import numpy as np
from typing import List, Dict
from collections import deque
from core.tracker import PersonTrack


class FeatureExtractor:
    """
    Extract features for fall classification
    Features are extracted over a time window (e.g., 1 second = 30 frames)
    """
    
    def __init__(self, config: dict):
        self.config = config
        ml_config = config.get('ml_classifier', {})
        self.window_size = ml_config.get('window_size', 30)  # frames
        
        # Feature buffers per track
        self.feature_buffers = {}  # {track_id: deque of features}
        
    def extract_instant_features(self, track: PersonTrack) -> Dict:
        """
        Extract features from single frame
        """
        features = track.last_features
        bbox = track.last_bbox
        
        # Basic geometric features
        instant = {
            # Aspect ratio (width/height)
            'aspect_ratio': features['aspect_ratio'],
            
            # Angle (0-180 degrees)
            'angle': features['angle'],
            
            # Centroid position (normalized)
            'centroid_x': features['centroid'][0] / 640.0,  # Assume 640 width
            'centroid_y': features['centroid_y_ratio'],
            
            # Bbox dimensions
            'bbox_height': features['bbox_height'],
            'bbox_width': features['bbox_width'],
            
            # Area
            'bbox_area': bbox[2] * bbox[3],
            
            # Shape features
            'extent': features['extent'],
            'solidity': features['solidity'],
        }
        
        # Velocity features
        vx, vy = track.get_velocity()
        instant['velocity_x'] = vx
        instant['velocity_y'] = vy
        instant['velocity_magnitude'] = np.sqrt(vx**2 + vy**2)
        
        return instant
    
    def update_buffer(self, track_id: int, instant_features: Dict):
        """Add instant features to buffer"""
        if track_id not in self.feature_buffers:
            self.feature_buffers[track_id] = deque(maxlen=self.window_size)
        
        self.feature_buffers[track_id].append(instant_features)
    
    def extract_temporal_features(self, track_id: int) -> Dict:
        """
        Extract temporal features over window
        Returns feature vector for ML classifier
        """
        if track_id not in self.feature_buffers:
            return None
        
        buffer = self.feature_buffers[track_id]
        
        if len(buffer) < 10:  # Need minimum frames
            return None
        
        # Convert buffer to arrays
        feature_arrays = {}
        feature_keys = buffer[0].keys()
        
        for key in feature_keys:
            feature_arrays[key] = np.array([f[key] for f in buffer])
        
        # Compute temporal statistics
        temporal = {}
        
        # For each feature, compute: mean, std, min, max, range
        for key in ['aspect_ratio', 'angle', 'centroid_y', 
                    'bbox_height', 'velocity_y', 'velocity_magnitude']:
            
            if key not in feature_arrays:
                continue
            
            arr = feature_arrays[key]
            
            temporal[f'{key}_mean'] = np.mean(arr)
            temporal[f'{key}_std'] = np.std(arr)
            temporal[f'{key}_min'] = np.min(arr)
            temporal[f'{key}_max'] = np.max(arr)
            temporal[f'{key}_range'] = np.max(arr) - np.min(arr)
        
        # Specific fall indicators
        
        # 1. Aspect ratio trend (increasing = lying down)
        ar_arr = feature_arrays['aspect_ratio']
        if len(ar_arr) >= 2:
            temporal['aspect_ratio_trend'] = ar_arr[-1] - ar_arr[0]
        else:
            temporal['aspect_ratio_trend'] = 0
        
        # 2. Centroid Y change (downward movement)
        cy_arr = feature_arrays['centroid_y']
        if len(cy_arr) >= 2:
            temporal['centroid_y_change'] = cy_arr[-1] - cy_arr[0]
            temporal['centroid_y_speed'] = temporal['centroid_y_change'] / len(cy_arr)
        else:
            temporal['centroid_y_change'] = 0
            temporal['centroid_y_speed'] = 0
        
        # 3. Height change (decreasing = fall)
        h_arr = feature_arrays['bbox_height']
        if len(h_arr) >= 2:
            temporal['height_change'] = h_arr[-1] - h_arr[0]
            temporal['height_change_ratio'] = temporal['height_change'] / max(h_arr[0], 1)
        else:
            temporal['height_change'] = 0
            temporal['height_change_ratio'] = 0
        
        # 4. Peak velocity (sudden movement)
        temporal['peak_velocity_y'] = np.max(np.abs(feature_arrays['velocity_y']))
        
        # 5. Current state features (last frame)
        temporal['current_aspect_ratio'] = ar_arr[-1]
        temporal['current_centroid_y'] = cy_arr[-1]
        temporal['current_angle'] = feature_arrays['angle'][-1]
        
        return temporal
    
    def get_feature_vector(self, track_id: int, track: PersonTrack) -> np.ndarray:
        """
        Get feature vector for ML model
        Returns numpy array ready for prediction
        """
        # Extract instant features and update buffer
        instant = self.extract_instant_features(track)
        self.update_buffer(track_id, instant)
        
        # Extract temporal features
        temporal = self.extract_temporal_features(track_id)
        
        if temporal is None:
            return None
        
        # Create feature vector in consistent order
        feature_names = self.get_feature_names()
        feature_vector = np.array([temporal.get(name, 0.0) for name in feature_names])
        
        return feature_vector
    
    def get_feature_names(self) -> List[str]:
        """
        Get ordered list of feature names
        Must match training data
        """
        base_features = ['aspect_ratio', 'angle', 'centroid_y', 
                        'bbox_height', 'velocity_y', 'velocity_magnitude']
        
        feature_names = []
        
        # Statistical features
        for base in base_features:
            for stat in ['mean', 'std', 'min', 'max', 'range']:
                feature_names.append(f'{base}_{stat}')
        
        # Specific indicators
        feature_names.extend([
            'aspect_ratio_trend',
            'centroid_y_change',
            'centroid_y_speed',
            'height_change',
            'height_change_ratio',
            'peak_velocity_y',
            'current_aspect_ratio',
            'current_centroid_y',
            'current_angle'
        ])
        
        return feature_names
    
    def reset_buffer(self, track_id: int):
        """Clear buffer for a track"""
        if track_id in self.feature_buffers:
            del self.feature_buffers[track_id]
    
    def get_feature_dict_for_logging(
        self, track_id: int, track: PersonTrack
    ) -> Dict:
        """
        Get features as dict for CSV logging (data collection)
        """
        feature_vector = self.get_feature_vector(track_id, track)
        
        if feature_vector is None:
            return None
        
        feature_names = self.get_feature_names()
        feature_dict = {}
        
        for name, value in zip(feature_names, feature_vector):
            feature_dict[name] = value
        
        return feature_dict
