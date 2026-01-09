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
        
        # Contour thresholds - TĂNG để loại nhiễu
        contour_config = config['detection']['contour']
        self.min_area = max(contour_config['min_area'], 8000)  # Tăng lên
        self.max_area = contour_config['max_area']
        
        # Frame storage
        self.prev_frame = None
        self.current_frame = None
        self.frame_count = 0
        
        # Auto ROI (center 80% of frame, loại rèm/biên)
        self.auto_roi_enabled = True
        
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
        """Apply region of interest - auto center 80% or manual"""
        roi_config = self.config['roi']
        
        roi_mask = np.zeros_like(mask)
        
        if self.auto_roi_enabled:
            # Auto ROI: giữ 80% giữa khung, bỏ rèm/biên
            h, w = mask.shape
            margin_x = int(w * 0.10)  # Bỏ 10% mỗi bên
            margin_y = int(h * 0.05)  # Bỏ 5% trên/dưới
            roi_mask[margin_y:h-margin_y, margin_x:w-margin_x] = 255
        elif roi_config['enabled']:
            # Manual ROI
            x, y = roi_config['x'], roi_config['y']
            w, h = roi_config['width'], roi_config['height']
            roi_mask[y:y+h, x:x+w] = 255
        else:
            return mask
        
        return cv2.bitwise_and(mask, roi_mask)
    
    def detect_persons(self, frame: np.ndarray) -> List[Dict]:
        """
        Phát hiện người từ frame - CHỈ GIỮ 1 NGƯỜI CHÍNH
        Returns: List of person detections (max 1-2 người)
        """
        self.current_frame = self.preprocess_frame(frame.copy())
        self.frame_count += 1
        
        # Skip first 30 frames (warm-up background model)
        if self.frame_count < 30:
            self.prev_frame = self.current_frame
            return []
        
        # Background subtraction
        fg_mask = self.bg_subtractor.apply(self.current_frame, learningRate=0.001)
        
        # Apply ROI
        fg_mask = self.apply_roi(frame, fg_mask)
        
        # Morphological operations - MẠNH HƠN để merge vỡ
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Collect valid detections
        candidates = []
        frame_h, frame_w = frame.shape[:2]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # FILTER: chỉ giữ bbox giống người
            aspect_ratio = w / max(h, 1)
            
            # Loại bbox quá nhỏ hoặc không giống người
            if h < frame_h * 0.2:  # Chiều cao < 20% khung hình
                continue
            if w < frame_w * 0.05:  # Chiều rộng < 5% khung hình
                continue
            if aspect_ratio < 0.2 or aspect_ratio > 5.0:  # Tỷ lệ kỳ quặc
                continue
            
            candidates.append({
                'contour': contour,
                'bbox': (x, y, w, h),
                'area': area,
                'aspect_ratio': aspect_ratio
            })
        
        # Nếu không có gì → return empty
        if len(candidates) == 0:
            self.prev_frame = self.current_frame
            return []
        
        # MERGE overlapping boxes (NMS)
        candidates = self._merge_overlapping_boxes(candidates)
        
        # CHỈ GIỮ 1-2 BBOX LỚN NHẤT (người chính)
        candidates.sort(key=lambda x: x['area'], reverse=True)
        candidates = candidates[:2]  # Tối đa 2 người (sensitive hơn)
        
        # Build final detections
        detections = []
        for candidate in candidates:
            x, y, w, h = candidate['bbox']
            contour = candidate['contour']
            area = candidate['area']
            
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
    
    def _merge_overlapping_boxes(self, candidates: List[Dict]) -> List[Dict]:
        """Merge overlapping bounding boxes (Simple NMS)"""
        if len(candidates) <= 1:
            return candidates
        
        # Sort by area
        candidates = sorted(candidates, key=lambda x: x['area'], reverse=True)
        
        merged = []
        used = set()
        
        for i, cand_i in enumerate(candidates):
            if i in used:
                continue
            
            x1, y1, w1, h1 = cand_i['bbox']
            
            # Check overlap with remaining
            to_merge = [cand_i]
            for j in range(i + 1, len(candidates)):
                if j in used:
                    continue
                
                x2, y2, w2, h2 = candidates[j]['bbox']
                
                # Calculate IoU
                iou = self._calculate_iou(
                    (x1, y1, x1+w1, y1+h1),
                    (x2, y2, x2+w2, y2+h2)
                )
                
                if iou > 0.3:  # Overlap > 30%
                    to_merge.append(candidates[j])
                    used.add(j)
            
            # Merge boxes
            if len(to_merge) > 1:
                # Take bounding box that covers all
                min_x = min(c['bbox'][0] for c in to_merge)
                min_y = min(c['bbox'][1] for c in to_merge)
                max_x = max(c['bbox'][0] + c['bbox'][2] for c in to_merge)
                max_y = max(c['bbox'][1] + c['bbox'][3] for c in to_merge)
                
                # Merge contours
                all_points = np.vstack([c['contour'] for c in to_merge])
                merged_contour = cv2.convexHull(all_points)
                
                merged.append({
                    'bbox': (min_x, min_y, max_x - min_x, max_y - min_y),
                    'contour': merged_contour,
                    'area': cv2.contourArea(merged_contour),
                    'aspect_ratio': (max_x - min_x) / max(max_y - min_y, 1)
                })
            else:
                merged.append(cand_i)
        
        return merged
    
    def _calculate_iou(self, box1, box2):
        """Calculate Intersection over Union"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Intersection
        xi_min = max(x1_min, x2_min)
        yi_min = max(y1_min, y2_min)
        xi_max = min(x1_max, x2_max)
        yi_max = min(y1_max, y2_max)
        
        if xi_max <= xi_min or yi_max <= yi_min:
            return 0.0
        
        intersection = (xi_max - xi_min) * (yi_max - yi_min)
        
        # Union
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union = area1 + area2 - intersection
        
        return intersection / max(union, 1e-5)
    
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
