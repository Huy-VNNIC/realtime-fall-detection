# 🎯 TÓM TẮT - Test Webcam Trên Máy Local

## ✅ Đã tạo xong!

Tôi đã tạo đầy đủ hệ thống và công cụ để bạn test với webcam thật.

---

## 📦 File đã đóng gói sẵn

```
/home/dtu/fall-detection-system.tar.gz (52KB)
```

**Chứa toàn bộ code (3,166 lines) + docs**

---

## 🚀 CÁCH TEST NHANH (3 bước)

### Bước 1: Download file về máy local
```bash
# Dùng SCP, SFTP, hoặc copy qua USB
scp user@server:/home/dtu/fall-detection-system.tar.gz ~/Downloads/
```

### Bước 2: Giải nén và install
```bash
cd ~/Downloads
tar -xzf fall-detection-system.tar.gz
cd "Dectact-camare real time"
pip3 install opencv-python numpy pyyaml
```

### Bước 3: Chạy test webcam
```bash
python3 test_webcam_simple.py
```

**Xong! Webcam sẽ mở và bắt đầu detect.**

---

## 🎮 Phím điều khiển

- **SPACE** - Chuyển chế độ (RAW → MOTION → FALL_DETECT)
- **Q** - Thoát

---

## 📹 Chế độ test

### 1. RAW Mode
- Hiển thị video gốc từ webcam
- Kiểm tra webcam hoạt động OK

### 2. MOTION Mode  
- Phát hiện chuyển động
- Vẽ bbox xanh quanh vật thể chuyển động
- Kiểm tra detection cơ bản

### 3. FALL_DETECT Mode
- Phát hiện té ngã đầy đủ
- **Xanh** = Đứng (bình thường)
- **Vàng** = Cúi/ngồi (cảnh báo)
- **Đỏ** = Nằm (NGUY HIỂM)

---

## 🧪 Test scenarios

1. **Đứng trước camera** → Bbox xanh
2. **Cúi xuống** → Bbox vàng
3. **Nằm xuống sàn** → Bbox đỏ + "NGUY HIEM - NAM"
4. **Ra khỏi frame** → Tracking biến mất

---

## 🎯 Kết quả mong đợi

✅ **Thành công nếu:**
- Webcam mở được
- FPS hiển thị > 20
- Phát hiện được người (có bbox)
- Khi nằm xuống → màu đỏ + cảnh báo
- Aspect ratio thay đổi đúng

---

## 🔧 Nếu muốn chạy hệ thống đầy đủ

```bash
# Install full dependencies
pip3 install -r requirements.txt

# Test installation
python3 test_installation.py

# Run full system
python3 main.py

# Với config tùy chỉnh
python3 main.py --camera 0
```

Hệ thống đầy đủ có thêm:
- ✅ Multi-person tracking
- ✅ State machine (STANDING → FALLING → FALLEN → ALARM)
- ✅ Risk scoring (0-100)
- ✅ Immobility detection
- ✅ Auto recording (snapshot + clip)
- ✅ iOS WebSocket API
- ✅ SQLite logging

---

## 📚 Tài liệu

- **TEST_WEBCAM_LOCAL.md** - Hướng dẫn chi tiết
- **QUICKSTART.md** - Quick start 5 phút
- **USAGE_GUIDE.md** - Hướng dẫn đầy đủ
- **BUILD_COMPLETE.md** - Tổng kết features

---

## 💡 Tips

1. **Ánh sáng tốt** - Camera cần đủ sáng
2. **Nền đơn giản** - Tường trơn > nền lộn xộn
3. **Đứng cách 2-3m** - Khoảng cách tối ưu
4. **Background tĩnh** - Tránh vật chuyển động phía sau

---

## 🐛 Troubleshooting

### "Cannot open camera"
```bash
# Thử index khác
python3 test_webcam_simple.py  # Tự động thử 0, 1, 2
```

### FPS thấp
- Đóng các app khác đang dùng camera
- Giảm resolution trong code nếu cần

### False alarm nhiều
- Chuyển sang chế độ MOTION để xem
- Điều chỉnh min_area trong code (dòng 84)

---

## 📊 Tóm tắt files quan trọng

| File | Mục đích |
|------|----------|
| `test_webcam_simple.py` | Test nhanh webcam (không cần full system) |
| `main.py` | Hệ thống đầy đủ (OpenCV + AI + tracking) |
| `test_installation.py` | Kiểm tra dependencies |
| `TEST_WEBCAM_LOCAL.md` | Hướng dẫn chi tiết |
| `config.yaml` | Cấu hình hệ thống |

---

## 🎬 Video demo

Khi chạy `test_webcam_simple.py`, bạn sẽ thấy:
1. Cửa sổ mở với webcam feed
2. FPS hiển thị góc trên
3. Mode hiện tại
4. Bbox màu sắc theo trạng thái
5. Thông tin aspect ratio

---

**Ready to test! Download file và chạy ngay! 🚀**

---

*P/S: Nếu không có webcam, có thể test với video file:*
```bash
python3 main.py --video path/to/video.mp4
```
