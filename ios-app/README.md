# Ứng Dụng iOS - Fall Detection System

## 📱 Tổng Quan

Ứng dụng iOS native được xây dựng bằng **SwiftUI** để giám sát và nhận cảnh báo từ hệ thống phát hiện ngã realtime. Ứng dụng kết nối với backend Python qua WebSocket để nhận thông tin theo thời gian thực.

## 🎯 Tính Năng

### ✅ Đã Hoàn Thành

1. **Dashboard Giám Sát**
   - Hiển thị trạng thái kết nối realtime
   - Thống kê hệ thống (FPS, CPU, RAM, số người)
   - Cảnh báo mới nhất
   - Thống kê nhanh (tổng cảnh báo, khẩn cấp, hôm nay)

2. **Quản Lý Cảnh Báo**
   - Danh sách lịch sử cảnh báo
   - Lọc theo mức độ (Warning, Alarm, Emergency)
   - Hiển thị metadata chi tiết
   - Xóa lịch sử

3. **Kết Nối WebSocket**
   - Auto-reconnect với exponential backoff
   - Heartbeat để maintain connection
   - Parse JSON messages từ backend
   - Xử lý alerts, status updates

4. **Thông Báo Push**
   - Local notifications cho cảnh báo mới
   - Phân loại theo mức độ nghiêm trọng
   - Âm thanh và badge
   - Notification khi app ở background

5. **Cài Đặt**
   - Cấu hình server (host, port)
   - Auto-connect
   - Bật/tắt notifications
   - Chọn mức độ cảnh báo tối thiểu

## 📋 Yêu Cầu Hệ Thống

### Phần Cứng
- **Mac** với chip Apple Silicon (M1/M2/M3) hoặc Intel
- **iPhone/iPad** chạy iOS 15.0 trở lên (để test)
- Hoặc có thể dùng **iOS Simulator**

### Phần Mềm
- **macOS** Monterey (12.0) trở lên
- **Xcode** 14.0 trở lên
- **Apple Developer Account** (miễn phí cho development)

## 🚀 Hướng Dẫn Build Chi Tiết

### Bước 1: Cài Đặt Xcode

1. Mở **App Store** trên Mac
2. Tìm kiếm **"Xcode"**
3. Click **"Get"** hoặc **"Download"** (khoảng 7-10GB)
4. Đợi cài đặt hoàn tất (có thể mất 30-60 phút)

Hoặc cài từ Terminal:
```bash
xcode-select --install
```

### Bước 2: Setup Apple Developer Account

1. Mở **Xcode**
2. Vào **Xcode > Settings** (hoặc ⌘,)
3. Chọn tab **"Accounts"**
4. Click **"+"** ở góc dưới bên trái
5. Chọn **"Apple ID"**
6. Đăng nhập bằng Apple ID của bạn (miễn phí)

### Bước 3: Mở Project

1. Mở **Terminal** và di chuyển đến thư mục dự án:
```bash
cd /Users/Admin/Downloads/Caspton_project/realtime-fall-detection/ios-app
```

2. Mở project bằng Xcode:
```bash
open FallDetectionApp.xcodeproj
```

Hoặc double-click vào file `FallDetectionApp.xcodeproj` trong Finder.

### Bước 4: Cấu Hình Signing & Capabilities

1. Trong Xcode, chọn project **"FallDetectionApp"** ở sidebar bên trái
2. Chọn target **"FallDetectionApp"**
3. Chọn tab **"Signing & Capabilities"**

4. **Thay đổi Bundle Identifier** (bắt buộc):
   - Tìm dòng **"Bundle Identifier"**
   - Đổi từ `com.caspton.FallDetectionApp` thành `com.TenCuaBan.FallDetectionApp`
   - Ví dụ: `com.john.FallDetectionApp`

5. **Enable Automatic Signing**:
   - Check vào **"Automatically manage signing"**
   - Chọn **Team**: Chọn Apple ID của bạn
   - Xcode sẽ tự động tạo provisioning profile

### Bước 5: Build và Run trên Simulator

1. Ở thanh toolbar trên cùng, chọn destination:
   - Click vào device selector (bên cạnh nút Play/Stop)
   - Chọn **"iPhone 15 Pro"** hoặc device khác

2. Click nút **Play** (▶) hoặc nhấn **⌘R** để build và run

3. Đợi Xcode compile (lần đầu sẽ mất 2-5 phút)

4. Simulator sẽ tự động mở và app sẽ chạy

### Bước 6: Build và Run trên iPhone Thật (Optional)

#### 6.1. Kết Nối iPhone

1. Cắm iPhone vào Mac bằng cáp USB
2. Unlock iPhone
3. Nếu xuất hiện popup "Trust This Computer", chọn **"Trust"**

#### 6.2. Enable Developer Mode (iOS 16+)

1. Trên iPhone, mở **Settings**
2. Vào **Privacy & Security**
3. Scroll xuống, tìm **"Developer Mode"**
4. Bật **Developer Mode**
5. Restart iPhone

#### 6.3. Build lên iPhone

1. Trong Xcode, chọn iPhone của bạn từ device selector
2. Click nút **Play** (▶) để build
3. Nếu gặp lỗi **"Untrusted Developer"** trên iPhone:
   - Mở **Settings** trên iPhone
   - Vào **General > VPN & Device Management**
   - Tìm Apple ID của bạn
   - Chọn **"Trust"**
4. Run lại từ Xcode

### Bước 7: Cấu Hình Kết Nối

#### 7.1. Khởi Động Backend Python

Trên máy tính chạy backend:
```bash
cd /Users/Admin/Downloads/Caspton_project/realtime-fall-detection
python main.py
```

Backend sẽ hiển thị:
```
[API] WebSocket server starting on 0.0.0.0:8080
```

#### 7.2. Tìm IP Address của Backend

**Trên Windows:**
```bash
ipconfig
```
Tìm dòng **"IPv4 Address"** (ví dụ: `192.168.1.100`)

**Trên Mac/Linux:**
```bash
ifconfig | grep inet
```

#### 7.3. Cấu Hình trong iOS App

1. Mở app trên iPhone/Simulator
2. Vào tab **"Cài Đặt"** (biểu tượng bánh răng)
3. Nhập thông tin:
   - **Host**: IP address của máy chạy backend (ví dụ: `192.168.1.100`)
   - **Port**: `8080`
4. Bật **"Tự động kết nối"**
5. Click **"Kết nối lại"**

#### 7.4. Kiểm Tra Kết Nối

- Vào tab **"Giám Sát"**
- Trạng thái kết nối phải là **"Đã kết nối"** (màu xanh)
- Bạn sẽ thấy thông tin FPS, số người, CPU/RAM

## 🔧 Troubleshooting

### Lỗi "Signing for requires a development team"

**Giải pháp:**
1. Vào **Signing & Capabilities**
2. Thay đổi Bundle Identifier thành unique name
3. Chọn Team là Apple ID của bạn

### Lỗi "Failed to connect to WebSocket"

**Kiểm tra:**
1. Backend Python đang chạy và listen port 8080
2. IP address đúng (cùng mạng với iPhone)
3. Firewall không block port 8080
4. Cấu hình trong `config.yaml`:
```yaml
ios_api:
  enabled: true
  host: "0.0.0.0"
  port: 8080
```

### App không chạy trên iPhone thật

**Giải pháp:**
1. Enable Developer Mode (iOS 16+)
2. Trust Developer Certificate trong Settings
3. Đảm bảo iPhone và Mac cùng Apple ID

### Không nhận được notifications

**Kiểm tra:**
1. Trong app, vào **Cài đặt**
2. Bật **"Bật thông báo"**
3. Nếu popup "Bật quyền thông báo", click vào
4. Trong iOS Settings, bật notifications cho app

## 📱 Cấu Trúc Project

```
FallDetectionApp/
├── FallDetectionApp.xcodeproj/      # Xcode project file
└── FallDetectionApp/
    ├── Info.plist                   # App configuration
    ├── FallDetectionAppApp.swift    # Entry point
    ├── Models/
    │   └── Models.swift             # Data models
    ├── Services/
    │   ├── WebSocketManager.swift   # WebSocket client
    │   └── NotificationManager.swift # Push notifications
    ├── Views/
    │   ├── ContentView.swift        # Main navigation
    │   ├── DashboardView.swift      # Dashboard
    │   ├── AlertListView.swift      # Alert history
    │   └── SettingsView.swift       # Settings screen
    └── Assets.xcassets/             # Images, colors
```

## 🔄 Workflow Phát Triển

### Development

1. Mở project trong Xcode
2. Chỉnh sửa code trong các file Swift
3. Xcode sẽ tự động compile khi bạn save
4. Run lại app để test (⌘R)

### Debugging

1. Set breakpoint bằng cách click vào số dòng
2. Run app ở debug mode
3. Dùng Debug Console để xem log
4. Xem Variables trong Debug Navigator

### Testing trên nhiều devices

1. Window > Devices and Simulators
2. Add thêm simulators (iPhone, iPad)
3. Test app trên nhiều màn hình

## 📦 Export & Distribution

### TestFlight (Internal Testing)

1. Cần **paid Apple Developer Program** ($99/năm)
2. Archive app: Product > Archive
3. Upload lên App Store Connect
4. Mời testers qua email

### Ad Hoc Distribution

1. Tạo provisioning profile Ad Hoc
2. Archive app
3. Export IPA file
4. Cài bằng Apple Configurator hoặc Xcode

## 🔐 Security Notes

**LƯU Ý:** App này chỉ dùng cho mạng nội bộ (local network). Không expose backend ra Internet công cộng.

Nếu cần access từ xa:
- Dùng VPN
- Hoặc setup reverse proxy với SSL (nginx + Let's Encrypt)

## 📊 Features Tương Lai

- [ ] Video streaming từ camera
- [ ] Playback recordings
- [ ] Multiple camera support
- [ ] User authentication
- [ ] Cloud sync
- [ ] Statistics & analytics
- [ ] Export reports (PDF/CSV)
- [ ] Apple Watch companion app

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra console log trong Xcode
2. Kiểm tra backend Python logs
3. Test kết nối WebSocket bằng browser: `http://IP:8080`

## 📝 License

MIT License - Free to use and modify

---

**Phát triển bởi:** Caspton Fall Detection System  
**Phiên bản:** 1.0.0  
**Ngày cập nhật:** 11/01/2026
