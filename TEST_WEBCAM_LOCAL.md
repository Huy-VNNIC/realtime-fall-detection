# 🎥 HƯỚNG DẪN TEST WEBCAM - Máy Local

## 📋 Yêu cầu
- ✅ Máy tính có webcam (laptop hoặc USB webcam)
- ✅ Python 3.7+
- ✅ Môi trường có GUI (không phải server)

---

## 🚀 Cách 1: Test nhanh với script đơn giản

### Bước 1: Copy project về máy local
```bash
# Từ server, zip project
cd /home/dtu/
tar -czf fall-detection.tar.gz "Dectact-camare real time"

# Download về máy local (dùng scp, sftp, hoặc copy qua USB)
# Ví dụ với scp:
scp user@server:/home/dtu/fall-detection.tar.gz ~/Downloads/

# Giải nén trên máy local
cd ~/Downloads
tar -xzf fall-detection.tar.gz
cd "Dectact-camare real time"
```

### Bước 2: Install dependencies
```bash
pip3 install opencv-python numpy
```

### Bước 3: Chạy test webcam
```bash
python3 test_webcam_simple.py
```

**Chế độ test:**
- `RAW` - Video gốc từ webcam
- `MOTION` - Phát hiện chuyển động (contours)
- `FALL_DETECT` - Phát hiện té ngã (với aspect ratio)

**Phím điều khiển:**
- `SPACE` - Chuyển chế độ
- `Q` - Thoát

---

## 🎯 Cách 2: Chạy hệ thống đầy đủ

### Install đầy đủ:
```bash
pip3 install -r requirements.txt
```

### Test installation:
```bash
python3 test_installation.py
```

### Chạy hệ thống:
```bash
python3 main.py
```

Hoặc với camera cụ thể:
```bash
python3 main.py --camera 0
python3 main.py --camera 1  # Nếu có nhiều camera
```

---

## 📹 Test với video file thay vì webcam

Nếu không có webcam hoặc muốn test với video có sẵn:

```bash
# Download video test từ internet
# Hoặc quay video bằng điện thoại

python3 main.py --video path/to/video.mp4
```

**Video test tốt:**
- Độ phân giải: 640x480 hoặc cao hơn
- Format: mp4, avi, mov
- Nội dung: người đi lại, ngồi, đứng, té ngã

---

## 🐛 Troubleshooting

### Lỗi: "Cannot open camera"
```bash
# Kiểm tra camera có sẵn
ls /dev/video*

# Thử các index khác
python3 main.py --camera 1
python3 main.py --camera 2
```

### Lỗi: "cv2.error: display"
- Chạy trên máy có GUI (không phải SSH)
- Nếu dùng WSL: cần X server (VcXsrv, Xming)

### Webcam bị chiếm bởi app khác
- Đóng Zoom, Skype, Teams
- Đóng browser có tab dùng camera

### FPS thấp
```python
# Trong config.yaml, giảm resolution:
camera:
  width: 480   # Từ 640
  height: 360  # Từ 480
```

---

## 🎬 Demo scenarios để test

### 1. Test detection cơ bản:
- Đứng trước camera → màu xanh (safe)
- Đi lại → tracking hoạt động
- Ra khỏi frame → tracking mất

### 2. Test fall detection:
- Đứng → cúi xuống → màu vàng (warning)
- Nằm xuống sàn → màu đỏ (alarm)
- Nằm yên > 5 giây → ALARM trigger

### 3. Test multi-person:
- 2 người cùng vào frame
- Mỗi người có track ID riêng
- Chỉ người nằm mới trigger alarm

---

## 📊 Kết quả mong đợi

✅ **Thành công nếu:**
- Webcam mở được
- FPS > 20
- Phát hiện được người (bbox xanh)
- Khi nằm xuống → báo động đỏ
- Thông tin hiển thị: FPS, tracks, state

❌ **Cần fix nếu:**
- Không mở được camera
- FPS < 10
- Không phát hiện người
- False alarm quá nhiều

---

## 🔧 Điều chỉnh sensitivity

Nếu false alarm nhiều, sửa `config.yaml`:

```yaml
detection:
  sensitivity: 0.8              # Tăng từ 0.7
  fall_duration_threshold: 3.0  # Tăng từ 2.0
  immobility_threshold: 7.0     # Tăng từ 5.0

detection:
  contour:
    min_area: 3000  # Tăng từ 2000 (bỏ qua vật nhỏ)
```

---

## 💡 Tips

1. **Ánh sáng tốt**: Camera cần đủ sáng
2. **Background tĩnh**: Tránh vật chuyển động phía sau
3. **Khoảng cách**: Đứng cách camera 2-3 mét
4. **Nền đơn giản**: Tường trơn tốt hơn nền lộn xộn

---

## 📱 Nếu muốn test iOS API

### Trên máy local:
```bash
# Sửa config.yaml
ios_api:
  enabled: true
  port: 8080

# Chạy
python3 main.py
```

### Trên điện thoại/tablet:
- Kết nối cùng WiFi với máy local
- Lấy IP máy: `ifconfig` (Mac/Linux) hoặc `ipconfig` (Windows)
- WebSocket: `ws://192.168.1.XXX:8080/ws`

---

## 🎯 Next Steps

Sau khi test webcam OK:

1. **Thu data training:**
   ```bash
   cd data
   python3 collector.py --mode fall --duration 60
   python3 collector.py --mode not_fall --duration 60
   ```

2. **Train ML model:**
   ```bash
   python3 train.py
   ```

3. **Enable AI trong config và test lại**

---

**Happy testing! 🚀**
