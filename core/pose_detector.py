"""
Pose-based Person Detector using YOLOv8-Pose
Phát hiện người qua keypoints (17 điểm COCO) thay vì contour
"""
import time
import cv2
import numpy as np
from typing import List, Dict
from ultralytics import YOLO


# COCO-17 skeleton edges (để vẽ xương người)
COCO_EDGES = [
    (5, 6),   # vai trái - vai phải
    (5, 7),   # vai trái - khuỷu trái
    (7, 9),   # khuỷu trái - cổ tay trái
    (6, 8),   # vai phải - khuỷu phải
    (8, 10),  # khuỷu phải - cổ tay phải
    (11, 12), # hông trái - hông phải
    (5, 11),  # vai trái - hông trái
    (6, 12),  # vai phải - hông phải
    (11, 13), # hông trái - đầu gối trái
    (13, 15), # đầu gối trái - cổ chân trái
    (12, 14), # hông phải - đầu gối phải
    (14, 16), # đầu gối phải - cổ chân phải
    (0, 1),   # mũi - mắt trái
    (0, 2),   # mũi - mắt phải
    (1, 3),   # mắt trái - tai trái
    (2, 4),   # mắt phải - tai phải
    (0, 5),   # mũi - vai trái
    (0, 6),   # mũi - vai phải
]


class PoseDetector:
    """
    YOLOv8-Pose detector - multi-person
    Thay thế FallDetector (contour-based)
    """
    
    def __init__(self, config: dict):
        self.config = config
        pose_cfg = config.get("pose", {})
        
        # YOLOv8-Pose model
        model_path = pose_cfg.get("model_path", "yolov8n-pose.pt")
        print(f"[POSE] Loading YOLOv8-Pose model: {model_path}")
        self.model = YOLO(model_path)
        
        # Thresholds
        self.conf = float(pose_cfg.get("conf", 0.25))
        self.iou = float(pose_cfg.get("iou", 0.45))
        self.kpt_conf = float(pose_cfg.get("kpt_conf", 0.30))
        self.max_people = int(pose_cfg.get("max_people", 5))
        self.imgsz = int(pose_cfg.get("imgsz", 640))
        
        # Tracking (giữ format cũ để tương thích)
        self.prev_frame = None
        self.current_frame = None
        self.frame_count = 0
        
        # Floor estimation (tự động ước lượng "sàn nhà")
        self.floor_y = None
        self.floor_history = []
        
        print(f"[POSE] Initialized (conf={self.conf}, kpt_conf={self.kpt_conf})")
    
    def detect_persons(self, frame: np.ndarray) -> List[Dict]:
        """
        Phát hiện người qua pose keypoints
        Returns: List[Dict] với format tương thích FallDetector
        """
        self.current_frame = frame.copy()
        self.frame_count += 1
        timestamp = time.time()
        
        # YOLOv8 inference
        results = self.model.predict(
            frame,
            conf=self.conf,
            iou=self.iou,
            imgsz=self.imgsz,
            verbose=False
        )[0]
        
        # Không có keypoints → return empty
        if results.keypoints is None or len(results.keypoints) == 0:
            self.prev_frame = self.current_frame
            return []
        
        # Extract data
        kpts = results.keypoints.data.cpu().numpy()  # (N, 17, 3) => x, y, conf
        boxes = results.boxes.xyxy.cpu().numpy()     # (N, 4)
        confs = results.boxes.conf.cpu().numpy()     # (N,)
        
        # Sort by person confidence (lấy người rõ nhất trước)
        order = np.argsort(-confs)
        
        # Process each person
        detections = []
        H, W = frame.shape[:2]
        
        for idx in order[:self.max_people]:
            kp = kpts[idx]  # (17, 3)
            
            # Lọc keypoints có confidence đủ cao
            valid = kp[:, 2] >= self.kpt_conf
            if valid.sum() < 6:  # Cần ít nhất 6 keypoints
                continue
            
            # Tính bbox từ keypoints (thay vì dùng bbox của YOLO)
            xs, ys = kp[valid, 0], kp[valid, 1]
            x1, y1 = xs.min(), ys.min()
            x2, y2 = xs.max(), ys.max()
            
            # Clamp bbox
            x1, y1 = max(0, int(x1)), max(0, int(y1))
            x2, y2 = min(W - 1, int(x2)), min(H - 1, int(y2))
            bbox = (x1, y1, max(1, x2 - x1), max(1, y2 - y1))
            
            # Extract pose features (thay thế contour features)
            features = self._extract_pose_features(kp, bbox, H, W)
            
            detections.append({
                "bbox": bbox,
                "keypoints": kp,                 # ★ Quan trọng để vẽ skeleton
                "pose_conf": float(confs[idx]),
                "features": features,            # Tương thích với tracker/state_machine
                "timestamp": timestamp,
                "contour": None,                 # Không dùng contour nữa
                "area": bbox[2] * bbox[3],
            })
        
        # Update floor estimation
        self._update_floor_estimation(detections)
        
        self.prev_frame = self.current_frame
        return detections
    
    def _extract_pose_features(self, kp, bbox, H, W) -> Dict:
        """
        Extract features từ keypoints thay vì contour
        Tương thích với format cũ để không phá tracker/state_machine
        """
        # COCO keypoint indices
        # 0: nose, 5/6: shoulders, 11/12: hips, 15/16: ankles
        def get_point(i):
            return kp[i, 0], kp[i, 1], kp[i, 2]
        
        lsx, lsy, lsc = get_point(5)  # left shoulder
        rsx, rsy, rsc = get_point(6)  # right shoulder
        lhx, lhy, lhc = get_point(11) # left hip
        rhx, rhy, rhc = get_point(12) # right hip
        
        # Mid-shoulder và mid-hip
        shoulder_ok = (lsc >= self.kpt_conf and rsc >= self.kpt_conf)
        hip_ok = (lhc >= self.kpt_conf and rhc >= self.kpt_conf)
        
        if shoulder_ok:
            shx, shy = (lsx + rsx) / 2.0, (lsy + rsy) / 2.0
        else:
            shx, shy = None, None
        
        if hip_ok:
            hpx, hpy = (lhx + rhx) / 2.0, (lhy + rhy) / 2.0
        else:
            # Fallback to bbox center
            x, y, w, h = bbox
            hpx, hpy = x + w / 2.0, y + h / 2.0
        
        # ★ TORSO ANGLE (góc thân người)
        # 0° = đứng thẳng, 90° = nằm ngang
        torso_angle = 0.0
        if shoulder_ok and hip_ok:
            dx = hpx - shx
            dy = hpy - shy
            # Tính góc từ vector thân người so với trục dọc
            torso_angle = float(np.degrees(np.arctan2(abs(dx), abs(dy) + 1e-6)))
        
        # ★ HIP DROP & SPEED (để phát hiện ngã)
        # Sẽ tính trong PersonTrack khi có history
        
        # Bbox features (tương thích với code cũ)
        x, y, w, h = bbox
        aspect_ratio = w / max(h, 1)
        centroid_y_ratio = hpy / max(H, 1)
        
        # Floor distance (khoảng cách từ hip đến sàn)
        floor_dist_norm = 1.0
        if self.floor_y is not None:
            floor_dist_norm = abs(self.floor_y - hpy) / max(H, 1)
        
        return {
            "aspect_ratio": float(aspect_ratio),
            "centroid": (int(hpx), int(hpy)),     # ★ Dùng hip làm centroid (ổn định)
            "angle": float(torso_angle),          # Map vào angle cũ
            "torso_angle": float(torso_angle),    # ★ Góc thân người (quan trọng!)
            "extent": 0.0,                        # Không dùng nữa
            "solidity": 0.0,                      # Không dùng nữa
            "bbox_height": int(h),
            "bbox_width": int(w),
            "centroid_y_ratio": float(centroid_y_ratio),
            "floor_dist_norm": float(floor_dist_norm),
            "shoulder_pos": (shx, shy) if shoulder_ok else None,
            "hip_pos": (hpx, hpy),
        }
    
    def _update_floor_estimation(self, detections: List[Dict]):
        """
        Tự động ước lượng "sàn nhà" từ vị trí ankle (cổ chân)
        Dùng để check "nằm sát sàn"
        """
        if len(detections) == 0:
            return
        
        for det in detections:
            kp = det.get("keypoints")
            if kp is None:
                continue
            
            # Lấy ankle (15, 16)
            l_ankle_y, l_ankle_c = kp[15, 1], kp[15, 2]
            r_ankle_y, r_ankle_c = kp[16, 1], kp[16, 2]
            
            if l_ankle_c >= self.kpt_conf:
                self.floor_history.append(l_ankle_y)
            if r_ankle_c >= self.kpt_conf:
                self.floor_history.append(r_ankle_y)
        
        # Giữ 300 frames gần nhất
        if len(self.floor_history) > 300:
            self.floor_history = self.floor_history[-300:]
        
        # Floor = percentile 90 (ankle thấp nhất thường gần sàn)
        if len(self.floor_history) >= 30:
            self.floor_y = np.percentile(self.floor_history, 90)
    
    def calculate_motion_energy(self, bbox) -> float:
        """
        Tính motion energy (tương thích với code cũ)
        Dùng frame difference trong bbox
        """
        if self.prev_frame is None or self.current_frame is None:
            return 0.0
        
        x, y, w, h = bbox
        
        # Clamp bbox
        H, W = self.current_frame.shape[:2]
        x, y = max(0, x), max(0, y)
        w, h = min(W - x, w), min(H - y, h)
        
        if w <= 0 or h <= 0:
            return 0.0
        
        # Extract ROI
        roi_prev = self.prev_frame[y:y+h, x:x+w]
        roi_curr = self.current_frame[y:y+h, x:x+w]
        
        if roi_prev.shape != roi_curr.shape:
            return 0.0
        
        # Convert to grayscale
        if len(roi_prev.shape) == 3:
            roi_prev = cv2.cvtColor(roi_prev, cv2.COLOR_BGR2GRAY)
            roi_curr = cv2.cvtColor(roi_curr, cv2.COLOR_BGR2GRAY)
        
        # Frame difference
        diff = cv2.absdiff(roi_prev, roi_curr)
        motion_energy = np.mean(diff)
        
        return float(motion_energy)


def draw_skeleton(img, kp, kpt_th=0.30, thickness=2, alpha=0.8):
    """
    Vẽ skeleton (xương người) lên ảnh
    Giống hình 4: không vẽ bbox, chỉ vẽ keypoints + edges
    """
    overlay = img.copy()
    
    # Vẽ edges (xương) trước
    for a, b in COCO_EDGES:
        if kp[a, 2] < kpt_th or kp[b, 2] < kpt_th:
            continue
        
        xa, ya = int(kp[a, 0]), int(kp[a, 1])
        xb, yb = int(kp[b, 0]), int(kp[b, 1])
        
        # Màu xanh dương cho xương
        cv2.line(overlay, (xa, ya), (xb, yb), (255, 100, 0), thickness)
    
    # Vẽ keypoints (khớp) sau
    for i, (x, y, c) in enumerate(kp):
        if c < kpt_th:
            continue
        
        # Màu vàng cho keypoints
        cv2.circle(overlay, (int(x), int(y)), 4, (0, 255, 255), -1)
    
    # Blend với alpha
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
