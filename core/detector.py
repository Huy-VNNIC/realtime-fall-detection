"""
Core Fall Detector Module
Sử dụng background subtraction + contour analysis
"""
import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict
import time


class FallDetector:
    """
    OpenCV-based fall detector using background subtraction
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Background subtractor
        bg_config = config['detection']['background_subtraction']
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=bg_config['history'],
            varThreshold=bg_config['var_threshold'],
            detectShadows=bg_config['detect_shadows']
        )
        
        # Contour thresholds
        contour_config = config['detection']['contour']
        self.min_area = contour_config['min_area']
        self.max_area = contour_config['max_area']
        
        # Frame storage
        self.prev_frame = None
        self.current_frame = None
        
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Tiền xử lý frame"""
        # Resize if needed
        if frame.shape[1] > 640:
            scale = 640 / frame.shape[1]
            frame = cv2.resize(frame, None, fx=scale, fy=scale)
        
        # Gaussian blur to reduce noise
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        return frame
    
    def apply_roi(self, frame: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Apply region of interest if enabled"""
        roi_config = self.config['roi']
        if not roi_config['enabled']:
            return mask
        
        roi_mask = np.zeros_like(mask)
        x, y = roi_config['x'], roi_config['y']
        w, h = roi_config['width'], roi_config['height']
        roi_mask[y:y+h, x:x+w] = 255
        
        return cv2.bitwise_and(mask, roi_mask)
    
    def detect_persons(self, frame: np.ndarray) -> List[Dict]:
        """
        Phát hiện người từ frame
        Returns: List of person detections với bbox và features
        """
        self.current_frame = self.preprocess_frame(frame.copy())
        
        # Background subtraction
        fg_mask = self.bg_subtractor.apply(self.current_frame)
        
        # Apply ROI
        fg_mask = self.apply_roi(frame, fg_mask)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate features
            features = self._extract_contour_features(contour, x, y, w, h, area)
            
            detections.append({
                'bbox': (x, y, w, h),
                'contour': contour,
                'area': area,
                'features': features,
                'timestamp': time.time()
            })
        
        self.prev_frame = self.current_frame
        return detections
    
    def _extract_contour_features(
        self, contour, x: int, y: int, w: int, h: int, area: float
    ) -> Dict:
        """Extract features từ contour"""
        
        # Aspect ratio (width/height)
        aspect_ratio = w / max(h, 1)
        
        # Centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = x + w // 2, y + h // 2
        
        # Angle using PCA
        angle = self._get_orientation_angle(contour)
        
        # Extent (area / bbox area)
        bbox_area = w * h
        extent = area / max(bbox_area, 1)
        
        # Solidity (area / convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / max(hull_area, 1)
        
        return {
            'aspect_ratio': aspect_ratio,
            'centroid': (cx, cy),
            'angle': angle,
            'extent': extent,
            'solidity': solidity,
            'bbox_height': h,
            'bbox_width': w,
            'centroid_y_ratio': cy / max(self.current_frame.shape[0], 1)
        }
    
    def _get_orientation_angle(self, contour) -> float:
        """Calculate orientation angle using PCA"""
        if len(contour) < 5:
            return 0.0
        
        # Fit ellipse
        try:
            ellipse = cv2.fitEllipse(contour)
            angle = ellipse[2]  # Angle in degrees
            return angle
        except:
            return 0.0
    
    def calculate_motion_energy(
        self, bbox: Tuple[int, int, int, int]
    ) -> float:
        """
        Tính motion energy trong bbox (frame difference)
        Dùng cho immobility detection
        """
        if self.prev_frame is None or self.current_frame is None:
            return 0.0
        
        x, y, w, h = bbox
        
        # Extract ROI
        roi_prev = self.prev_frame[y:y+h, x:x+w]
        roi_curr = self.current_frame[y:y+h, x:x+w]
        
        if roi_prev.shape != roi_curr.shape:
            return 0.0
        
        # Convert to grayscale if needed
        if len(roi_prev.shape) == 3:
            roi_prev = cv2.cvtColor(roi_prev, cv2.COLOR_BGR2GRAY)
            roi_curr = cv2.cvtColor(roi_curr, cv2.COLOR_BGR2GRAY)
        
        # Frame difference
        diff = cv2.absdiff(roi_prev, roi_curr)
        
        # Motion energy = mean of difference
        motion_energy = np.mean(diff)
        
        return motion_energy
    
    def draw_detections(
        self, frame: np.ndarray, detections: List[Dict], 
        tracked_persons: Optional[List] = None
    ) -> np.ndarray:
        """Draw detections on frame for visualization"""
        output = frame.copy()
        
        for detection in detections:
            x, y, w, h = detection['bbox']
            features = detection['features']
            
            # Draw bbox
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw centroid
            cx, cy = features['centroid']
            cv2.circle(output, (cx, cy), 5, (0, 0, 255), -1)
            
            # Draw info
            info_text = f"AR: {features['aspect_ratio']:.2f}"
            cv2.putText(
                output, info_text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        
        return output
