# PROJECT STRUCTURE - Fall Detection System

## 📂 Cấu trúc thư mục chi tiết

```
fall-detection-system/
│
├── 📄 main.py                      # ⭐ MAIN APPLICATION
│   └── FallDetectionSystem class
│       ├── Integrates all components
│       ├── Main processing loop
│       └── Display & monitoring
│
├── 📄 config.yaml                  # Configuration file
├── 📄 requirements.txt             # Python dependencies
├── 📄 quickstart.sh               # Quick start script
├── 📄 README.md                    # Project overview
├── 📄 USAGE_GUIDE.md              # Detailed usage guide
│
├── 📁 core/                        # 🔧 CORE DETECTION MODULES
│   ├── __init__.py
│   ├── detector.py                # OpenCV fall detector
│   │   ├── FallDetector
│   │   ├── Background subtraction
│   │   ├── Contour analysis
│   │   └── Feature extraction
│   │
│   ├── tracker.py                 # Multi-person tracking
│   │   ├── KalmanTracker (Kalman filter)
│   │   ├── PersonTrack (single person)
│   │   ├── MultiPersonTracker (Hungarian matching)
│   │   └── Velocity calculation
│   │
│   ├── state_machine.py          # Fall state machine
│   │   ├── FallState enum (STANDING/FALLING/FALLEN/ALARM)
│   │   ├── PersonStateMachine (per person logic)
│   │   ├── StateMachineManager (multi-person)
│   │   └── State transitions & timers
│   │
│   └── immobility.py             # Immobility detection
│       ├── ImmobilityDetector
│       ├── Motion energy calculation
│       ├── Frame differencing
│       └── Smoothed motion history
│
├── 📁 ai/                          # 🤖 AI/ML COMPONENTS
│   ├── __init__.py
│   ├── feature_extractor.py      # Feature engineering
│   │   ├── FeatureExtractor
│   │   ├── Instant features (per frame)
│   │   ├── Temporal features (over window)
│   │   ├── Statistical aggregation
│   │   └── 39-dimensional feature vector
│   │
│   ├── classifier.py             # ML model wrapper
│   │   ├── FallClassifier (sklearn model)
│   │   ├── Model loading (joblib)
│   │   ├── Prediction with probability
│   │   └── Confidence thresholding
│   │
│   └── models/                   # Trained models
│       └── fall_classifier.pkl   # (created after training)
│
├── 📁 utils/                       # 🛠️ UTILITIES
│   ├── __init__.py
│   ├── config.py                 # Configuration manager
│   │   ├── ConfigManager
│   │   ├── YAML loading
│   │   └── Default config
│   │
│   ├── logger.py                 # Event logging
│   │   ├── EventLogger
│   │   ├── SQLite database
│   │   ├── Event logging
│   │   └── System stats
│   │
│   ├── risk_scorer.py            # Risk scoring
│   │   ├── RiskScorer
│   │   ├── Multi-factor scoring (0-100)
│   │   ├── Risk levels (safe/warning/alarm/emergency)
│   │   └── Weighted components
│   │
│   └── video_buffer.py           # Video recording
│       ├── CircularVideoBuffer (ring buffer)
│       ├── VideoRecorder
│       ├── Snapshot saving
│       └── Clip recording (before/after alarm)
│
├── 📁 api/                         # 📱 iOS APP INTEGRATION
│   ├── __init__.py
│   └── websocket_server.py       # WebSocket API
│       ├── WebSocketServer
│       ├── Real-time alerts
│       ├── Bi-directional messaging
│       └── AlertHandler
│
├── 📁 data/                        # 📊 DATA & TRAINING
│   ├── collector.py              # Data collection tool
│   │   ├── DataCollector
│   │   ├── Realtime feature logging
│   │   └── CSV output
│   │
│   ├── train.py                  # Training pipeline
│   │   ├── ModelTrainer
│   │   ├── Data loading & preprocessing
│   │   ├── Model training (sklearn)
│   │   ├── Evaluation & metrics
│   │   └── Model saving
│   │
│   ├── datasets/                 # Collected datasets
│   │   └── features_*.csv        # (created during collection)
│   │
│   └── training_results/         # Training outputs
│       ├── confusion_matrix.png
│       └── feature_importance.png
│
├── 📁 recordings/                  # 📹 SAVED RECORDINGS
│   ├── snapshots/                # Snapshot images
│   │   └── fall_*.jpg
│   │
│   └── clips/                    # Video clips
│       └── fall_*.mp4
│
└── 📁 logs/                        # 📝 SYSTEM LOGS
    └── fall_detection.db         # SQLite database
```

---

## 🔄 Data Flow

```
Camera Feed
    ↓
[FallDetector] ─→ Detections (bbox, features)
    ↓
[MultiPersonTracker] ─→ Tracked persons (IDs, history)
    ↓
[FeatureExtractor] ─→ Feature vectors (39-dim)
    ↓
[FallClassifier] ─→ ML Prediction (fall probability)
    ↓
[ImmobilityDetector] ─→ Motion energy analysis
    ↓
[StateMachine] ─→ State updates (STANDING/FALLING/FALLEN/ALARM)
    ↓
[RiskScorer] ─→ Risk score (0-100)
    ↓
[VideoRecorder] ─→ Snapshots & clips
    ↓
[AlertHandler] ─→ iOS App notification
    ↓
[EventLogger] ─→ Database logging
```

---

## 🧩 Component Dependencies

### Core Detection Flow:
1. **FallDetector** (OpenCV)
   - Input: Raw frame
   - Output: Detections (bbox + basic features)

2. **MultiPersonTracker** (Kalman + Hungarian)
   - Input: Detections
   - Output: PersonTrack objects with IDs

3. **FeatureExtractor** (ML features)
   - Input: PersonTrack
   - Output: 39-dimensional feature vector

4. **FallClassifier** (sklearn)
   - Input: Feature vector
   - Output: {'class': 'fall', 'proba': 0.95}

5. **ImmobilityDetector** (frame diff)
   - Input: Frame + bbox
   - Output: Motion energy score

6. **StateMachine** (logic)
   - Input: Features + ML + motion
   - Output: FallState + timer

7. **RiskScorer** (multi-factor)
   - Input: All above
   - Output: Risk score 0-100

### Recording & Alert Flow:
8. **VideoRecorder** (circular buffer)
   - Continuously buffers frames
   - Saves on alarm trigger

9. **AlertHandler** (notifications)
   - Triggers on ALARM state
   - Sends via WebSocket

10. **EventLogger** (database)
    - Logs all events
    - System statistics

---

## 🎯 Key Classes & Methods

### main.py - FallDetectionSystem
```python
__init__(config_path)         # Initialize all components
run(camera_source)            # Main loop
_process_frame(frame, time)   # Process single frame
_process_person(track_id, ...)# Process single person
_handle_alerts(...)           # Alert logic
_create_display(frame)        # Visualization
```

### core/detector.py - FallDetector
```python
detect_persons(frame)         # Main detection
_extract_contour_features()   # Feature extraction
calculate_motion_energy()     # Motion analysis
```

### core/tracker.py - MultiPersonTracker
```python
update(detections)            # Update tracks
_match_detections_to_tracks() # Hungarian matching
```

### core/state_machine.py - PersonStateMachine
```python
update(track, motion, ml)     # State update
_is_lying_position()          # Lying detection
_is_falling_fast()            # Fall velocity check
```

### ai/feature_extractor.py - FeatureExtractor
```python
extract_instant_features()    # Per-frame features
extract_temporal_features()   # Windowed features
get_feature_vector()          # 39-dim vector
```

### ai/classifier.py - FallClassifier
```python
load_model()                  # Load sklearn model
predict(features)             # Predict + probability
```

### utils/risk_scorer.py - RiskScorer
```python
calculate_risk_score()        # Multi-factor scoring
get_risk_level()              # safe/warning/alarm/emergency
```

---

## 📝 Configuration Structure

```yaml
camera:                       # Camera settings
  source, width, height, fps

detection:                    # OpenCV detection
  background_subtraction:     # MOG2 params
  contour:                    # Area thresholds
  sensitivity:                # Detection sensitivity
  fall_duration_threshold:    # Confirm fall time
  immobility_threshold:       # Immobile alarm time
  motion_threshold:           # Motion energy threshold

risk_scoring:                 # Risk calculation
  enabled: true
  weights:                    # Factor weights
  thresholds:                 # Warning/alarm/emergency

ml_classifier:                # AI model
  enabled: true/false
  model_path:                 # Model file
  confidence_threshold:       # Min confidence

recording:                    # Video recording
  enabled: true
  buffer_seconds:             # Circular buffer size
  save_before/after:          # Clip duration

tracking:                     # Multi-person
  max_disappeared:            # Remove after N frames
  max_distance:               # Matching threshold

roi:                          # Region of Interest
  enabled: true/false
  x, y, width, height:        # ROI coordinates

ios_api:                      # WebSocket API
  enabled: true/false
  host, port:                 # Server address
  alert_cooldown:             # Min time between alerts

monitoring:                   # Logging
  enabled: true
  log_file:                   # SQLite path
  
debug:                        # Visualization
  show_video: true
  show_contours: true
  show_bbox: true
```

---

## 🚀 Execution Order

### Startup:
1. Load config (ConfigManager)
2. Initialize detector, tracker, state machines
3. Load ML model (if enabled)
4. Initialize recorder, logger
5. Start WebSocket server (if enabled)
6. Open camera

### Per Frame:
1. Read frame
2. Add to video buffer
3. Detect persons (OpenCV)
4. Update tracker (Kalman + Hungarian)
5. For each person:
   - Extract features
   - ML prediction
   - Calculate motion energy
   - Update state machine
   - Calculate risk score
   - Check alarm conditions
6. Handle alarms (save, alert)
7. Display frame
8. Log stats (periodic)

### On Alarm:
1. Save snapshot (immediate)
2. Start event recording
3. Send WebSocket alert
4. Log to database
5. Continue recording 5s
6. Save video clip

---

## 💾 Database Schema

### events table:
```sql
id INTEGER PRIMARY KEY
timestamp TEXT
event_type TEXT (ALARM/WARNING/etc)
track_id INTEGER
risk_score REAL
state TEXT
snapshot_path TEXT
video_path TEXT
features TEXT (JSON)
ml_prediction TEXT (JSON)
notes TEXT
```

### system_stats table:
```sql
id INTEGER PRIMARY KEY
timestamp TEXT
fps REAL
cpu_usage REAL
num_tracks INTEGER
num_alarms INTEGER
```

---

## 📊 ML Features (39 dimensions)

### Statistical features (30):
- aspect_ratio: mean, std, min, max, range
- angle: mean, std, min, max, range
- centroid_y: mean, std, min, max, range
- bbox_height: mean, std, min, max, range
- velocity_y: mean, std, min, max, range
- velocity_magnitude: mean, std, min, max, range

### Temporal features (9):
- aspect_ratio_trend
- centroid_y_change
- centroid_y_speed
- height_change
- height_change_ratio
- peak_velocity_y
- current_aspect_ratio
- current_centroid_y
- current_angle

---

**This structure enables:**
- ✅ Modular design (easy to replace components)
- ✅ Clear separation of concerns
- ✅ Easy testing & debugging
- ✅ Scalable (add more features)
- ✅ Production-ready architecture
