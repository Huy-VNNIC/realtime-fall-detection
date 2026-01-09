# 🚨 AI Fall Detection System - Real-time

> **Hệ thống phát hiện té ngã thời gian thực với AI, không YOLO**
> 
> Realtime fall detection from webcam using OpenCV (no YOLO). State machine + ML classifier to trigger alarms and send alerts to iOS app via WebSocket.

## 🎯 Tính năng chính / Key Features

### Core AI Features
- ✅ **OpenCV-based motion detection** (MOG2 background subtraction)
- ✅ **ML Classifier** (sklearn) phân biệt "fall" vs "not fall" (giảm false alarm)
- ✅ **Risk Scoring System** (0-100 điểm nguy cơ)
- ✅ **Immobility Detection** (phát hiện bất động sau té)
- ✅ **Multi-person tracking** (theo dõi nhiều người với Kalman filter)
- ✅ **State Machine** (STANDING → FALLING → FALLEN → ALARM)

### Product Features
- 📸 **Auto recording**: Snapshot + 10s video clip khi alarm
- 📊 **Real-time dashboard**: FPS, CPU usage, alert statistics
- ⚙️ **Config system**: Sensitivity, ROI, thresholds (YAML)
- 📱 **iOS App integration**: WebSocket API cho real-time alerts
- 🗃️ **SQLite logging**: Event tracking & system statistics
- 📈 **Training pipeline**: Data collection + model training tools

## 📁 Project Structure

```
fall-detection-system/
├── core/                   # Core detection modules
│   ├── detector.py        # Background subtraction + contour analysis
│   ├── tracker.py         # Multi-person tracking (Kalman filter)
│   ├── state_machine.py   # Fall state logic (5 states)
│   └── immobility.py      # Post-fall immobility detection
│
├── ai/                     # AI/ML components
│   ├── feature_extractor.py  # 39-dimensional feature engineering
│   ├── classifier.py          # ML model wrapper (RF/SVM/LR)
│   └── models/                # Trained models (.pkl/.joblib)
│
├── utils/                  # Utilities
│   ├── risk_scorer.py     # Risk scoring algorithm (0-100)
│   ├── video_buffer.py    # Circular buffer + clip save
│   ├── config.py          # Configuration manager (YAML)
│   └── logger.py          # Event logging (SQLite)
│
├── data/                   # Data collection & training
│   ├── collector.py       # Dataset collection tool
│   ├── train.py          # Training pipeline with metrics
│   └── datasets/         # Collected training data
│
├── api/                    # iOS App integration
│   └── websocket_server.py  # WebSocket server for alerts
│
├── main.py                 # Main application
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
└── docs/                  # Documentation
    ├── QUICKSTART.md      # 5-minute quick start
    ├── USAGE_GUIDE.md     # Full usage guide
    └── BUILD_COMPLETE.md  # Feature checklist
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Huy-VNNIC/realtime-fall-detection.git
cd realtime-fall-detection

# Install dependencies
pip3 install -r requirements.txt
```

### 2. Test webcam

```bash
# Quick webcam test (3 modes: RAW/MOTION/FALL_DETECT)
python3 test_webcam_simple.py

# Full system test
python3 test_installation.py
```

### 3. Run system

```bash
# Start with default webcam
python3 main.py

# Or with specific camera index
python3 main.py --camera 0

# Or with video file
python3 main.py --video path/to/video.mp4
```

**Press Q to quit**

## 🎮 Usage Modes

### Mode 1: Basic Detection (No ML)
```bash
python3 main.py
```
- Uses OpenCV background subtraction
- Aspect ratio analysis (lying detection)
- False alarms possible

### Mode 2: With ML Classifier (Recommended)
```bash
# 1. Collect training data
python3 data/collector.py --mode fall
python3 data/collector.py --mode not_fall

# 2. Train model
python3 data/train.py

# 3. Enable ML in config.yaml
# classifier:
#   enabled: true

# 4. Run with ML
python3 main.py
```
- Reduced false alarms
- Better accuracy
- Learns from your environment

## 📊 System Output

### Console Display
```
[2026-01-10 12:34:56] INFO - System started
[2026-01-10 12:35:01] INFO - Person detected (ID: 1)
[2026-01-10 12:35:05] WARNING - Risk score: 45 (STANDING)
[2026-01-10 12:35:08] CRITICAL - FALL DETECTED! Risk: 85
[2026-01-10 12:35:08] INFO - Snapshot saved: recordings/alarm_20260110_123508.jpg
[2026-01-10 12:35:18] INFO - Video clip saved: recordings/alarm_20260110_123508.mp4
```

### Video Overlay
- **Green box**: Normal (standing/walking)
- **Yellow box**: Warning (sitting/bending)
- **Red box**: Danger (lying down)
- Risk score + state display
- FPS counter

### Recordings
- `recordings/alarm_YYYYMMDD_HHMMSS.jpg` - Snapshot at alarm moment
- `recordings/alarm_YYYYMMDD_HHMMSS.mp4` - 10s video clip (5s before + 5s after)

### Database Logs
- `logs/fall_detection.db` - SQLite database
  - `events` table: All fall events with timestamps, risk scores
  - `system_stats` table: FPS, CPU usage, alert counts

## 📱 iOS App Integration

```bash
# Start WebSocket server
python3 api/websocket_server.py

# Or enable in config.yaml:
# websocket:
#   enabled: true
#   port: 8765
```

iOS app connects via WebSocket to receive:
- Real-time fall alerts
- Risk score updates
- Person tracking info
- Video frame snapshots

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
detection:
  min_area: 3000           # Minimum contour area
  lying_aspect_ratio: 1.5  # Aspect ratio threshold for lying
  fall_angle: 30           # Fall angle threshold (degrees)

alarm:
  lying_duration: 3.0      # Seconds before alarm
  immobility_duration: 5.0 # Seconds of immobility to confirm

risk_scoring:
  weights:
    fall_speed: 0.4        # 40% weight
    immobility: 0.3        # 30% weight
    lying_duration: 0.3    # 30% weight

classifier:
  enabled: false           # Enable ML classifier
  model_path: data/models/fall_classifier.pkl
```

## 🧪 Testing Tools

| Tool | Purpose |
|------|---------|
| `test_webcam_simple.py` | Quick webcam test (3 modes) |
| `test_installation.py` | Verify all dependencies |
| `test_headless.py` | Test without camera/GUI |
| `demo_no_camera.py` | Demo with simulated data |

## 📈 Performance

- **FPS**: 20-30 on typical laptop (no GPU needed)
- **CPU**: 15-30% on 4-core CPU
- **Latency**: < 100ms detection time
- **Accuracy**: 85-95% with trained ML model

## 🛠️ Development

### Data Collection
```bash
# Collect "fall" samples
python3 data/collector.py --mode fall --samples 100

# Collect "not fall" samples
python3 data/collector.py --mode not_fall --samples 100
```

### Model Training
```bash
python3 data/train.py

# Output:
# - data/models/fall_classifier.pkl
# - data/models/metrics.txt
# - data/models/confusion_matrix.png
# - data/models/feature_importance.png
```

## 📋 Requirements

- Python 3.7+
- OpenCV 4.x
- NumPy
- scikit-learn
- PyYAML
- websockets (for iOS integration)

## 🐛 Troubleshooting

### "Cannot open camera"
```bash
# Try different camera index
python3 main.py --camera 1

# List available cameras
python3 show_info.py
```

### High false alarm rate
```bash
# 1. Adjust sensitivity in config.yaml
# 2. Or train ML classifier with your environment
python3 data/collector.py --mode not_fall
python3 data/train.py
```

### Low FPS
```bash
# Reduce resolution in config.yaml
camera:
  width: 640
  height: 480
```

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Comprehensive usage guide
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code architecture
- [BUILD_COMPLETE.md](BUILD_COMPLETE.md) - Feature checklist
- [TEST_WEBCAM_LOCAL.md](TEST_WEBCAM_LOCAL.md) - Local testing guide

## 👨‍💻 Author

**Huy-VNNIC**
- GitHub: [@Huy-VNNIC](https://github.com/Huy-VNNIC)
- Email: nguyennhathuy11@dtu.edu.vn

## 📄 License

MIT License - Free to use for personal and commercial projects.

## 🙏 Acknowledgments

Built with:
- OpenCV for computer vision
- scikit-learn for machine learning
- Python ecosystem for rapid development

---

**⭐ If this helps you, give it a star!**
