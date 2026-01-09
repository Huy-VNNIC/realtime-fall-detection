"""
Multi-person Tracker
Sử dụng Kalman Filter + Hungarian algorithm để theo dõi nhiều người
"""
import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Dict, Tuple
import time


class KalmanTracker:
    """Simple Kalman filter for 2D position tracking"""
    
    def __init__(self):
        # State: [x, y, vx, vy]
        self.state = np.zeros(4)
        
        # State transition matrix
        self.F = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=float)
        
        # Measurement matrix
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=float)
        
        # Covariance matrices
        self.P = np.eye(4) * 1000  # Large initial uncertainty
        self.Q = np.eye(4) * 0.1   # Process noise
        self.R = np.eye(2) * 10    # Measurement noise
        
    def predict(self):
        """Predict next state"""
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.state[:2]  # Return predicted position
    
    def update(self, measurement: np.ndarray):
        """Update with measurement"""
        # Innovation
        y = measurement - self.H @ self.state
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state
        self.state = self.state + K @ y
        
        # Update covariance
        self.P = (np.eye(4) - K @ self.H) @ self.P


class PersonTrack:
    """Represents a tracked person"""
    
    next_id = 1
    
    def __init__(self, detection: Dict):
        self.track_id = PersonTrack.next_id
        PersonTrack.next_id += 1
        
        # Kalman filter
        self.kalman = KalmanTracker()
        cx, cy = detection['features']['centroid']
        self.kalman.state[:2] = [cx, cy]
        
        # Track history
        self.detections = [detection]
        self.timestamps = [detection['timestamp']]
        self.disappeared = 0
        
        # Features for analysis
        self.last_bbox = detection['bbox']
        self.last_features = detection['features']
        
    def update(self, detection: Dict):
        """Update track with new detection"""
        cx, cy = detection['features']['centroid']
        self.kalman.update(np.array([cx, cy]))
        
        self.detections.append(detection)
        self.timestamps.append(detection['timestamp'])
        self.disappeared = 0
        
        self.last_bbox = detection['bbox']
        self.last_features = detection['features']
        
        # Keep only last N detections
        max_history = 60
        if len(self.detections) > max_history:
            self.detections = self.detections[-max_history:]
            self.timestamps = self.timestamps[-max_history:]
    
    def predict(self) -> Tuple[float, float]:
        """Predict next position"""
        return tuple(self.kalman.predict())
    
    def mark_disappeared(self):
        """Mark as disappeared (no matching detection)"""
        self.disappeared += 1
    
    def get_velocity(self) -> Tuple[float, float]:
        """Calculate velocity from recent detections"""
        if len(self.detections) < 2:
            return 0.0, 0.0
        
        recent = self.detections[-10:]  # Last 10 frames
        times = self.timestamps[-10:]
        
        if len(recent) < 2:
            return 0.0, 0.0
        
        # Extract centroids
        centroids = [d['features']['centroid'] for d in recent]
        
        # Calculate velocities
        vx = (centroids[-1][0] - centroids[0][0]) / max(times[-1] - times[0], 0.001)
        vy = (centroids[-1][1] - centroids[0][1]) / max(times[-1] - times[0], 0.001)
        
        return vx, vy
    
    def get_centroid_y_speed(self) -> float:
        """Vertical speed (important for fall detection)"""
        _, vy = self.get_velocity()
        return abs(vy)


class MultiPersonTracker:
    """
    Tracker cho nhiều người sử dụng Hungarian algorithm
    """
    
    def __init__(self, config: dict):
        self.config = config
        tracking_config = config['tracking']
        
        self.max_disappeared = tracking_config['max_disappeared']
        self.max_distance = tracking_config['max_distance']
        
        self.tracks: Dict[int, PersonTrack] = {}
        
    def update(self, detections: List[Dict]) -> Dict[int, PersonTrack]:
        """
        Update tracks with new detections
        Returns: Dict of active tracks {track_id: PersonTrack}
        """
        # If no tracks exist, create new ones
        if len(self.tracks) == 0:
            for detection in detections:
                track = PersonTrack(detection)
                self.tracks[track.track_id] = track
            return self.tracks
        
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for track in self.tracks.values():
                track.mark_disappeared()
            self._remove_disappeared_tracks()
            return self.tracks
        
        # Both tracks and detections exist - match them
        self._match_detections_to_tracks(detections)
        
        return self.tracks
    
    def _match_detections_to_tracks(self, detections: List[Dict]):
        """Match detections to existing tracks using Hungarian algorithm"""
        
        # Get track IDs and predicted positions
        track_ids = list(self.tracks.keys())
        
        # Build cost matrix (distance between predictions and detections)
        cost_matrix = np.zeros((len(track_ids), len(detections)))
        
        for i, track_id in enumerate(track_ids):
            track = self.tracks[track_id]
            pred_x, pred_y = track.predict()
            
            for j, detection in enumerate(detections):
                det_x, det_y = detection['features']['centroid']
                
                # Euclidean distance
                distance = np.sqrt((pred_x - det_x)**2 + (pred_y - det_y)**2)
                cost_matrix[i, j] = distance
        
        # Hungarian algorithm
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        
        # Track which detections and tracks are matched
        matched_detections = set()
        matched_tracks = set()
        
        # Process matches
        for row, col in zip(row_indices, col_indices):
            if cost_matrix[row, col] > self.max_distance:
                continue  # Too far, ignore match
            
            track_id = track_ids[row]
            detection = detections[col]
            
            self.tracks[track_id].update(detection)
            matched_detections.add(col)
            matched_tracks.add(track_id)
        
        # Handle unmatched tracks (mark disappeared)
        for track_id in track_ids:
            if track_id not in matched_tracks:
                self.tracks[track_id].mark_disappeared()
        
        # Handle unmatched detections (create new tracks)
        for j, detection in enumerate(detections):
            if j not in matched_detections:
                track = PersonTrack(detection)
                self.tracks[track.track_id] = track
        
        # Remove tracks that disappeared too long
        self._remove_disappeared_tracks()
    
    def _remove_disappeared_tracks(self):
        """Remove tracks that have disappeared for too long"""
        to_remove = []
        for track_id, track in self.tracks.items():
            if track.disappeared > self.max_disappeared:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
    
    def get_track(self, track_id: int) -> PersonTrack:
        """Get track by ID"""
        return self.tracks.get(track_id)
    
    def get_all_tracks(self) -> Dict[int, PersonTrack]:
        """Get all active tracks"""
        return self.tracks
