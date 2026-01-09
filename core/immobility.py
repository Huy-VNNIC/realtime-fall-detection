"""
Immobility Detection Module
Phát hiện bất động sau khi ngã
"""
import cv2
import numpy as np
from typing import Tuple
from collections import deque


class ImmobilityDetector:
    """
    Phát hiện immobility bằng motion energy analysis
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.motion_threshold = config['detection']['motion_threshold']
        
        # History of motion energy for smoothing
        self.motion_history = {}  # {track_id: deque}
        self.history_size = 10
        
    def calculate_motion_energy(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> float:
        """
        Tính motion energy trong bbox
        Args:
            prev_frame: Previous frame (grayscale or BGR)
            curr_frame: Current frame (grayscale or BGR)
            bbox: (x, y, w, h)
        Returns:
            Motion energy value (0-255)
        """
        if prev_frame is None or curr_frame is None:
            return 0.0
        
        x, y, w, h = bbox
        
        # Ensure bbox is within frame
        h_frame, w_frame = curr_frame.shape[:2]
        x = max(0, min(x, w_frame - 1))
        y = max(0, min(y, h_frame - 1))
        w = min(w, w_frame - x)
        h = min(h, h_frame - y)
        
        if w <= 0 or h <= 0:
            return 0.0
        
        # Extract ROI
        roi_prev = prev_frame[y:y+h, x:x+w]
        roi_curr = curr_frame[y:y+h, x:x+w]
        
        if roi_prev.shape != roi_curr.shape or roi_prev.size == 0:
            return 0.0
        
        # Convert to grayscale if needed
        if len(roi_prev.shape) == 3:
            roi_prev = cv2.cvtColor(roi_prev, cv2.COLOR_BGR2GRAY)
        if len(roi_curr.shape) == 3:
            roi_curr = cv2.cvtColor(roi_curr, cv2.COLOR_BGR2GRAY)
        
        # Frame difference
        diff = cv2.absdiff(roi_prev, roi_curr)
        
        # Threshold to remove noise
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Motion energy = percentage of moving pixels
        motion_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.size
        motion_energy = (motion_pixels / total_pixels) * 100
        
        return motion_energy
    
    def update_history(self, track_id: int, motion_energy: float):
        """Update motion history for smoothing"""
        if track_id not in self.motion_history:
            self.motion_history[track_id] = deque(maxlen=self.history_size)
        
        self.motion_history[track_id].append(motion_energy)
    
    def get_smoothed_motion(self, track_id: int) -> float:
        """Get smoothed motion energy"""
        if track_id not in self.motion_history:
            return 0.0
        
        history = self.motion_history[track_id]
        if len(history) == 0:
            return 0.0
        
        return np.mean(history)
    
    def is_immobile(self, track_id: int) -> bool:
        """Check if person is immobile"""
        smoothed_motion = self.get_smoothed_motion(track_id)
        return smoothed_motion < self.motion_threshold
    
    def reset_history(self, track_id: int):
        """Reset history for a track"""
        if track_id in self.motion_history:
            del self.motion_history[track_id]
    
    def get_immobility_score(self, track_id: int) -> float:
        """
        Get immobility score (0-1)
        0 = high motion, 1 = completely immobile
        """
        smoothed_motion = self.get_smoothed_motion(track_id)
        
        # Normalize to 0-1 (invert so 1 = immobile)
        score = 1.0 - min(smoothed_motion / 100.0, 1.0)
        return score


class AdvancedImmobilityDetector(ImmobilityDetector):
    """
    Nâng cấp: phát hiện chuyển động của các body parts (nếu có pose)
    Hiện tại chỉ dùng basic version
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        # TODO: Add pose-based immobility detection
        # Check if hands/legs are moving even if body is still
    
    def detect_vital_movements(
        self, 
        bbox: Tuple[int, int, int, int],
        frame: np.ndarray
    ) -> bool:
        """
        Phát hiện chuyển động vi tế (breathing, small movements)
        Placeholder for future enhancement
        """
        # TODO: Implement optical flow analysis
        # TODO: Or use small region analysis for chest movement
        return False
