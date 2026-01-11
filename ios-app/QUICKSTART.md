# iOS App Build Instructions - Quick Start

## 🎯 Yêu Cầu Nhanh

- Mac với Xcode 14+
- iOS 15+ (iPhone/iPad hoặc Simulator)
- Backend Python đang chạy

## ⚡ Build Nhanh (5 Phút)

### 1. Cài Xcode
```bash
# Cài từ App Store hoặc:
xcode-select --install
```

### 2. Mở Project
```bash
cd ios-app
open FallDetectionApp.xcodeproj
```

### 3. Đổi Bundle ID
- Chọn project **FallDetectionApp**
- Tab **Signing & Capabilities**
- Đổi **Bundle Identifier**: `com.YourName.FallDetectionApp`
- Chọn **Team**: Your Apple ID

### 4. Run
- Chọn device: **iPhone 15 Pro** (Simulator)
- Click **Play** ▶️ hoặc `⌘R`

### 5. Kết Nối Backend

**Khởi động backend:**
```bash
# Trong thư mục realtime-fall-detection
python main.py
```

**Trong iOS app:**
1. Vào tab **Cài Đặt** ⚙️
2. Nhập **Host**: IP của máy backend (ví dụ: `192.168.1.100`)
3. **Port**: `8080`
4. Bật **Tự động kết nối**
5. Click **Kết nối lại**

## 🔍 Tìm IP Address

**Windows:**
```bash
ipconfig
# Tìm IPv4 Address: 192.168.x.x
```

**Mac/Linux:**
```bash
ifconfig | grep inet
# Tìm inet 192.168.x.x
```

## ✅ Kiểm Tra

- Tab **Giám Sát**: Trạng thái = **Đã kết nối** (xanh lá)
- Hiển thị FPS, số người
- Tab **Cảnh báo**: Nhận alerts từ backend

## 🐛 Lỗi Thường Gặp

### "Signing requires development team"
→ Đổi Bundle ID và chọn Team

### "Failed to connect"
→ Kiểm tra backend đang chạy và IP đúng

### "Untrusted Developer" (iPhone thật)
→ Settings > General > VPN & Device Management > Trust

## 📱 Chạy trên iPhone Thật

1. Cắm iPhone vào Mac
2. Trust computer
3. Enable Developer Mode (iOS 16+)
4. Chọn iPhone trong Xcode
5. Run ▶️

## 📚 Chi Tiết Đầy Đủ

Xem [README.md](README.md) để biết thêm chi tiết về:
- Architecture
- Troubleshooting
- Features
- Distribution

---

**Ready to go!** 🚀
