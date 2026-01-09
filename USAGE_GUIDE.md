# HƯỚNG DẪN SỬ DỤNG - Fall Detection System

## 📋 Mục lục

1. [Cài đặt](#cài-đặt)
2. [Thu thập dữ liệu](#thu-thập-dữ-liệu)
3. [Train model AI](#train-model-ai)
4. [Chạy hệ thống](#chạy-hệ-thống)
5. [Tích hợp iOS App](#tích-hợp-ios-app)
6. [Troubleshooting](#troubleshooting)

---

## 1. Cài đặt

### Bước 1: Clone/Download project

```bash
cd /home/dtu/
# Project đã có sẵn trong: Dectact-camare real time/
```

### Bước 2: Install dependencies

```bash
cd "/home/dtu/Dectact-camare real time"
pip install -r requirements.txt
```

**Dependencies chính:**
- opencv-python (computer vision)
- scikit-learn (ML classifier)
- numpy, scipy (tính toán)
- pyyaml (config)
- websockets (iOS API)
- psutil (monitoring)

### Bước 3: Kiểm tra webcam

```bash
# Test webcam
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera ERROR')"
```

---

## 2. Thu thập dữ liệu (Data Collection)

Để train AI classifier, bạn cần thu thập 2 loại data:

### A. Thu thập data "fall" (ngã)

```bash
cd data
python collector.py --mode fall --duration 60 --camera 0
```

**Hướng dẫn:**
- Đứng trong vùng camera
- Thực hiện các động tác: ngã xuống, nằm, té nhào, ngã chậm, ngã nhanh
- Thu 2-3 lần, mỗi lần 60 giây
- Càng đa dạng càng tốt

**Output:** `data/datasets/features_fall_TIMESTAMP.csv`

### B. Thu thập data "not_fall" (không ngã)

```bash
python collector.py --mode not_fall --duration 60 --camera 0
```

**Hướng dẫn:**
- Thực hiện: đi lại, đứng, ngồi, cúi nhặt đồ, duỗi người, vươn vai
- Tránh nằm dài trên sàn
- Thu 2-3 lần, mỗi lần 60 giây

**Output:** `data/datasets/features_not_fall_TIMESTAMP.csv`

### Tips thu data tốt:

✅ **Nên:**
- Thu ít nhất 3 phút mỗi class
- Đa dạng góc quay, tốc độ
- Thu cả ánh sáng tốt và ánh sáng yếu
- Nhiều người khác nhau (nếu có)

❌ **Không:**
- Thu data quá ngắn (< 30s mỗi class)
- Động tác lặp lại y hệt
- Chỉ thu 1 người 1 lần

---

## 3. Train Model AI

Sau khi thu đủ data:

```bash
cd data
python train.py --input datasets --output ../ai/models/fall_classifier.pkl --model random_forest
```

**Parameters:**
- `--input`: Thư mục chứa CSV files
- `--output`: Đường dẫn save model
- `--model`: Loại model (logistic/svm/random_forest)
- `--test-size`: Tỉ lệ test set (default: 0.2)

**Output:**
```
Training completed successfully!
Final accuracy: 0.920
Model saved to: ../ai/models/fall_classifier.pkl

Files created:
  - fall_classifier.pkl (trained model)
  - training_results/confusion_matrix.png
  - training_results/feature_importance.png
```

**Đánh giá model:**
- Accuracy > 0.85: Tốt
- Accuracy 0.75-0.85: Chấp nhận được
- Accuracy < 0.75: Cần thu thêm data

### Nếu accuracy thấp:

1. Thu thêm data (đặc biệt class bị sai)
2. Cân bằng số lượng samples giữa 2 class
3. Thử model khác: `--model svm` hoặc `--model logistic`

---

## 4. Chạy hệ thống

### A. Chạy cơ bản (chỉ OpenCV, không AI)

```bash
cd "/home/dtu/Dectact-camare real time"
python main.py
```

**Chế độ này:**
- Chỉ dùng OpenCV detection
- Không cần trained model
- Vẫn có: risk scoring, immobility, recording

### B. Chạy với AI classifier (sau khi train)

**Bước 1:** Bật ML classifier trong config.yaml:

```yaml
ml_classifier:
  enabled: true  # Đổi thành true
  model_path: "ai/models/fall_classifier.pkl"
  confidence_threshold: 0.7
```

**Bước 2:** Chạy:

```bash
python main.py
```

**Chế độ này:**
- OpenCV + ML classifier
- Giảm false alarm đáng kể
- Độ chính xác cao hơn

### C. Chạy với iOS API

**Bước 1:** Bật API trong config.yaml:

```yaml
ios_api:
  enabled: true
  host: "0.0.0.0"
  port: 8080
```

**Bước 2:** Chạy:

```bash
python main.py
```

**WebSocket endpoint:** `ws://YOUR_IP:8080/ws`

### D. Chạy với video file (thay vì webcam)

```bash
python main.py --video path/to/video.mp4
```

---

## 5. Tích hợp iOS App

### WebSocket Protocol

**Connect:**
```swift
let socket = WebSocket("ws://192.168.1.100:8080/ws")
```

**Message types từ server:**

#### 1. ALARM (ngã nghiêm trọng)
```json
{
  "type": "ALARM",
  "track_id": 1,
  "risk_score": 85.5,
  "state": "alarm",
  "timestamp": 1704800000.123,
  "snapshot": "recordings/snapshots/fall_123_track1_20260109_103000.jpg",
  "clip": "recordings/clips/fall_123_track1_20260109_103000.mp4"
}
```

**iOS action:**
- Hiển thị alert ngay lập tức
- Play sound/vibration
- Show snapshot
- Nút "I'm OK" và "Call Help"

#### 2. WARNING (cảnh báo nhẹ)
```json
{
  "type": "WARNING",
  "track_id": 1,
  "risk_score": 55.2,
  "state": "falling",
  "timestamp": 1704800000.123
}
```

**iOS action:**
- Hiển thị notification nhẹ
- Không cần action ngay

#### 3. STATUS (system update)
```json
{
  "type": "STATUS",
  "data": {
    "fps": 28.5,
    "num_tracks": 1,
    "uptime": 3600
  },
  "timestamp": 1704800000.123
}
```

### iOS gửi message lên server:

#### Acknowledge alert:
```json
{
  "type": "ACK",
  "track_id": 1
}
```

#### Cancel alert ("I'm OK"):
```json
{
  "type": "CANCEL",
  "track_id": 1,
  "user_id": "user123"
}
```

#### Ping (keep alive):
```json
{
  "type": "PING"
}
```

---

## 6. Configuration (config.yaml)

### Điều chỉnh độ nhạy:

```yaml
detection:
  sensitivity: 0.7  # 0.0 - 1.0 (càng cao càng nhạy)
  fall_duration_threshold: 2.0  # giây để confirm fall
  immobility_threshold: 5.0  # giây bất động = alarm
```

### Risk scoring:

```yaml
risk_scoring:
  thresholds:
    warning: 40   # Điểm warning
    alarm: 65     # Điểm alarm
    emergency: 85  # Điểm emergency
```

### ROI (chỉ detect trong khu vực):

```yaml
roi:
  enabled: true
  x: 100      # Tọa độ góc trên-trái
  y: 100
  width: 400  # Kích thước vùng
  height: 300
```

---

## 7. Troubleshooting

### Lỗi: "Camera not found"
```bash
# Kiểm tra camera có sẵn:
ls /dev/video*

# Thử camera index khác:
python main.py --camera 1
```

### Lỗi: "Model not found"
```
[WARNING] Model not found at ai/models/fall_classifier.pkl
ML classifier disabled. Run data/train.py first.
```

**Giải quyết:**
1. Thu data: `cd data && python collector.py --mode fall --duration 60`
2. Train model: `python train.py`
3. Hoặc tắt ML trong config: `ml_classifier.enabled: false`

### FPS thấp (< 15 fps)

**Giải quyết:**
1. Giảm resolution trong config:
```yaml
camera:
  width: 480  # từ 640
  height: 360  # từ 480
```

2. Tắt ML classifier (nếu đang bật)
3. Tắt recording nếu không cần

### False alarms nhiều

**Giải quyết:**
1. Tăng threshold:
```yaml
detection:
  fall_duration_threshold: 3.0  # từ 2.0
  immobility_threshold: 7.0  # từ 5.0
```

2. Train lại model với data tốt hơn
3. Điều chỉnh risk scoring weights

### No detection

**Giải quyết:**
1. Check camera có hoạt động
2. Kiểm tra ánh sáng (cần đủ sáng)
3. Giảm `min_area` trong config:
```yaml
detection:
  contour:
    min_area: 1000  # từ 2000
```

---

## 8. Recordings & Logs

### Recordings

**Location:** `recordings/`
- `snapshots/` - Ảnh snapshot khi alarm
- `clips/` - Video clips 10s (5s trước + 5s sau)

### Logs

**Database:** `logs/fall_detection.db`

**Xem logs:**
```python
import sqlite3
conn = sqlite3.connect('logs/fall_detection.db')
cursor = conn.cursor()

# Recent events
cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 10")
print(cursor.fetchall())

# Stats
cursor.execute("SELECT COUNT(*), event_type FROM events GROUP BY event_type")
print(cursor.fetchall())
```

---

## 9. Advanced: Nâng cấp lên Pose-based (Level 3)

Để nâng cấp lên MediaPipe Pose + LSTM:

1. Cài thêm:
```bash
pip install mediapipe torch
```

2. Thu data với pose keypoints
3. Train sequence model (LSTM/TCN)
4. Integrate vào realtime

*(Chi tiết xem roadmap nâng cấp trong README.md)*

---

## 10. Support & Contact

**Issues:**
- Check logs: `logs/fall_detection.db`
- Test từng component riêng
- Đọc error messages

**Tips:**
- Bắt đầu với config đơn giản
- Test webcam trước
- Thu data tốt = model tốt
- Điều chỉnh threshold theo môi trường thực tế

---

**Good luck! 🚀**
