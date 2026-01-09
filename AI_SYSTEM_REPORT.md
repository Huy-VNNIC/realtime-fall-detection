# 🤖 AI System Report - Fall Detection

## 📊 Tình trạng hiện tại

### ✅ Đã hoạt động (OpenCV-based)
1. **Background Subtraction** - Phát hiện chuyển động (MOG2)
2. **Contour Analysis** - Phân tích hình dạng vật thể
3. **Kalman Filter Tracking** - Theo dõi nhiều người
4. **State Machine** - Quản lý trạng thái (STANDING → FALLING → FALLEN → ALARM)
5. **Risk Scoring** - Tính điểm nguy cơ 0-100

### ⚠️ Chưa hoạt động (ML-based)
1. **ML Classifier** - Chưa có model được train
   - File cần: `ai/models/fall_classifier.pkl`
   - Status: Missing
   - Impact: Hệ thống dùng rule-based, nhiều false alarm

---

## 🧠 AI System Architecture

### 1. Feature Extraction (39 features)

#### A. Geometric Features (Instant)
```python
1. aspect_ratio          # width/height (>1.5 = lying)
2. angle                 # rotation (90° = horizontal)
3. centroid_x, centroid_y # vị trí trọng tâm
4. bbox_height, bbox_width # kích thước
5. bbox_area            # diện tích
6. extent               # mức độ đầy bbox
7. solidity             # độ đặc
```

#### B. Motion Features (Temporal)
```python
8-12.  velocity_x, velocity_y, velocity_magnitude
13-17. velocity statistics (mean, std, min, max, range)
18-22. aspect_ratio statistics (trend over 30 frames)
23-27. centroid_y statistics (downward movement)
28-32. bbox_height statistics (height decrease)
33-35. peak_velocity_y (sudden drop)
36-39. current_state (last frame features)
```

### 2. ML Classifier Pipeline

```
Raw Frame → Feature Extraction → 39D Vector → ML Model → Prediction
                                                           ↓
                                            {class: 'fall'/'not_fall',
                                             proba: 0.0-1.0,
                                             confidence: 0.0-1.0}
```

**Supported Models:**
- Random Forest (default, best for this problem)
- SVM (Support Vector Machine)
- Logistic Regression
- XGBoost (cần cài thêm)
- Neural Network (cần cài thêm)

### 3. Training Data Collection

**Current system:**
```bash
# Thu thập data ngã (60 giây)
cd data
python collector.py --mode fall --duration 60

# Thu thập data không ngã (60 giây)
python collector.py --mode not_fall --duration 60

# Training
python train.py
```

**Data format:**
- CSV files với 39 features + 1 label
- Saved in `data/datasets/`
- Auto-split: 80% train, 20% test

---

## 🎯 Chức năng AI sẽ mang lại

### 1. Giảm False Alarm (Quan trọng nhất!)
**Vấn đề hiện tại:**
- OpenCV detect mọi chuyển động nhanh → ALARM
- Người ngồi, cúi xuống → False alarm
- Vật rơi, bóng đổ → False alarm

**Với AI:**
- Học pattern thật của ngã (từ data)
- Phân biệt ngã thật vs ngã giả
- Confidence score: chỉ alarm khi > 70%

### 2. Adaptive Learning
- Model học từ môi trường thực tế
- Tự động cải thiện qua thời gian
- Custom cho từng không gian (phòng bệnh viện, nhà riêng, v.v.)

### 3. Multi-stage Detection
```
Stage 1: OpenCV (Fast)  → Candidate detection
Stage 2: ML (Accurate)  → False alarm filter  
Stage 3: Deep Learning  → Context understanding (future)
```

### 4. Context Awareness
- Học thói quen của người dùng
- Detect abnormal behavior
- Time-of-day sensitivity

---

## 🚀 Kế hoạch phát triển AI

### Phase 1: Basic ML (Hiện tại)
✅ Feature extraction (39 features)
✅ Random Forest classifier
✅ Training pipeline
⚠️ Cần: Collect data & train

### Phase 2: Advanced ML (Tuần này)
- [ ] XGBoost integration (better accuracy)
- [ ] Ensemble methods (voting classifier)
- [ ] Online learning (continuous improvement)
- [ ] Auto-retraining based on user feedback

### Phase 3: Deep Learning (Tháng sau)
- [ ] CNN for pose estimation (MediaPipe/OpenPose)
- [ ] LSTM for temporal modeling
- [ ] Attention mechanism
- [ ] Transfer learning from pre-trained models

### Phase 4: Production AI (2-3 tháng)
- [ ] Edge AI optimization (TensorRT/ONNX)
- [ ] Federated learning (privacy-preserving)
- [ ] Explainable AI (why alarm triggered)
- [ ] A/B testing framework

---

## 📈 Performance Metrics (Target)

### OpenCV Only (Current)
- Accuracy: ~70%
- False Positive Rate: ~30% (cao!)
- Latency: 10ms/frame
- CPU Usage: 15%

### With ML (After training)
- Accuracy: ~85-90% 
- False Positive Rate: <10%
- Latency: 15ms/frame
- CPU Usage: 20%

### With Deep Learning (Future)
- Accuracy: >95%
- False Positive Rate: <5%
- Latency: 30ms/frame
- CPU/GPU Usage: 40%

---

## 🔧 Hướng dẫn Train AI Model

### Quick Start (5 phút)

```bash
# Bước 1: Collect data ngã
cd data
python collector.py --mode fall --duration 60
# → Thực hiện: ngã xuống, nằm trên sàn, rolling, v.v.

# Bước 2: Collect data không ngã
python collector.py --mode not_fall --duration 120
# → Thực hiện: đi lại, ngồi, đứng, cúi xuống nhặt đồ, v.v.

# Bước 3: Train model
python train.py --model random_forest
# → Output: ../ai/models/fall_classifier.pkl

# Bước 4: Enable AI
cd ..
# Edit config.yaml: ml_classifier.enabled = true

# Bước 5: Run with AI
python main.py
```

### Advanced Training

```bash
# Train với nhiều models
python train.py --model all  # Test tất cả models

# Cross-validation
python train.py --cv 5

# Grid search hyperparameters
python train.py --optimize

# Export metrics
python train.py --export-metrics results.json
```

---

## 💡 AI Best Practices

### 1. Data Collection Tips
- **Balance classes**: 50% fall, 50% not_fall
- **Diverse scenarios**: nhiều kiểu ngã, nhiều người
- **Edge cases**: ngồi xuống nhanh, nhảy múa, yoga
- **Lighting conditions**: sáng/tối/backlight
- **Min data**: 500 samples mỗi class

### 2. Feature Engineering
- Current: 39 handcrafted features
- Future: Auto feature learning (CNN)
- Add context: time, location, user profile

### 3. Model Selection
- **Random Forest**: Best for small data (<10k samples)
- **XGBoost**: Best for medium data (10k-100k)
- **Deep Learning**: Best for large data (>100k)

### 4. Deployment
- Model versioning (MLflow)
- A/B testing (Champion vs Challenger)
- Monitoring drift (data/concept)
- Rollback mechanism

---

## 🎓 Technical Deep Dive

### Why ML > Rule-based?

**Rule-based (Current without ML):**
```python
if aspect_ratio > 1.5 and velocity_y > threshold:
    return "FALL"  # ❌ Too simple!
```
- Fixed thresholds → không adapt
- Không xử lý được edge cases
- Nhiều false positives

**ML-based:**
```python
# Model learns complex decision boundary
prediction = model.predict(features)  # ✅ Smart!
```
- Learn từ data thực tế
- Handle non-linear patterns
- Confidence scores

### Feature Importance (Example)

Sau khi train, model sẽ cho biết feature nào quan trọng:

```
1. aspect_ratio_trend       (0.25) - Quan trọng nhất!
2. centroid_y_speed        (0.18)
3. height_change_ratio     (0.15)
4. velocity_magnitude_max  (0.12)
5. angle_mean              (0.10)
...
```

→ Giúp optimize detection logic

---

## 🔮 Future AI Roadmap

### Short-term (1-2 tháng)
1. **Pose Estimation**: Detect body keypoints (MediaPipe)
2. **Anomaly Detection**: Unsupervised learning
3. **Multi-modal**: Camera + Wearable sensors

### Mid-term (3-6 tháng)
1. **Video Understanding**: 3D CNN / Transformers
2. **Activity Recognition**: Tổng hợp các hoạt động
3. **Predictive Analytics**: Dự đoán nguy cơ

### Long-term (6-12 tháng)
1. **Edge AI**: Deploy on Raspberry Pi / Jetson Nano
2. **Federated Learning**: Multi-site training
3. **Explainable AI**: Visual explanations
4. **Multimodal Fusion**: Camera + Audio + Radar

---

## 📚 References & Resources

### Papers
- "Deep Learning for Fall Detection" (IEEE)
- "Human Activity Recognition using CNNs" 
- "Temporal Convolutional Networks for Action Recognition"

### Tools
- MediaPipe (Google): Pose estimation
- OpenPose (CMU): Body keypoints
- TensorRT (NVIDIA): GPU acceleration
- MLflow: Model management

### Datasets
- UR Fall Detection Dataset
- Le2i Fall Detection Dataset  
- Multi-camera Fall Dataset

---

## 🎯 Action Items

### Ngay lập tức
- [ ] Collect training data (2 giờ)
- [ ] Train first model (5 phút)
- [ ] Test & validate (30 phút)
- [ ] Fine-tune thresholds (1 giờ)

### Tuần này
- [ ] Implement XGBoost
- [ ] Add online learning
- [ ] Create dashboard for metrics
- [ ] User feedback system

### Tháng này
- [ ] Integrate pose estimation
- [ ] Deep learning prototype
- [ ] Edge deployment test
- [ ] Performance optimization

---

**Status**: 🟡 AI Infrastructure ready, needs training data
**Next Step**: Run data collection script
**ETA to full AI**: 2-3 hours of data collection + training
