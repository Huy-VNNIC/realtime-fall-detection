# Cập Nhật Backend để Hỗ Trợ iOS App

## Thay Đổi Cần Thiết

Backend Python hiện tại đã có WebSocket server, nhưng cần đảm bảo cấu hình đúng.

## 1. Kiểm Tra config.yaml

Mở file `config.yaml` và đảm bảo có section này:

```yaml
# iOS API Configuration
ios_api:
  enabled: true
  host: "0.0.0.0"  # Listen trên tất cả interfaces
  port: 8080
  alert_cooldown: 10  # Giây giữa các alert cho cùng người
```

Nếu chưa có, thêm vào cuối file `config.yaml`.

## 2. Khởi Động System

```bash
# Trong thư mục realtime-fall-detection
python main.py
```

Bạn sẽ thấy:
```
[API] WebSocket server starting on 0.0.0.0:8080
```

## 3. Test WebSocket từ Browser (Optional)

Tạo file `test_websocket.html` để test:

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <h1>WebSocket Test</h1>
    <div id="status">Disconnected</div>
    <div id="messages"></div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8080');
        
        ws.onopen = () => {
            document.getElementById('status').textContent = 'Connected';
            document.getElementById('status').style.color = 'green';
        };
        
        ws.onmessage = (event) => {
            const div = document.createElement('div');
            div.textContent = event.data;
            document.getElementById('messages').appendChild(div);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
```

Mở file này trong browser và check kết nối.

## 4. Cho Phép Firewall (Windows)

Nếu không kết nối được từ iPhone:

```powershell
# Mở PowerShell as Administrator
New-NetFirewallRule -DisplayName "Fall Detection API" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

## 5. Test từ iPhone

1. Đảm bảo iPhone và máy tính cùng WiFi
2. Tìm IP của máy tính (Windows: `ipconfig`, Mac: `ifconfig`)
3. Trong iOS app, nhập IP đó vào Host
4. Port: 8080
5. Kết nối

## Cấu Trúc Message Format

WebSocket gửi JSON messages theo format:

### Alert Message
```json
{
  "type": "alert",
  "data": {
    "alert_id": "unique-id",
    "track_id": 1,
    "severity": "EMERGENCY",
    "event_type": "FALL",
    "risk_score": 95,
    "timestamp": "2026-01-11T10:30:00.000Z",
    "location": "Camera 1",
    "message": "Phát hiện té ngã nghiêm trọng!",
    "metadata": {
      "fall_duration": 2.5,
      "immobility_duration": 5.0,
      "position_info": "Nằm xuống"
    }
  }
}
```

### Status Update
```json
{
  "type": "status",
  "data": {
    "is_running": true,
    "active_people": 2,
    "fps": 28.5,
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "timestamp": "2026-01-11T10:30:00.000Z"
  }
}
```

### Heartbeat
```json
{
  "type": "heartbeat"
}
```

## Troubleshooting

### iPhone không kết nối được

1. **Kiểm tra cùng mạng:**
   - iPhone và máy tính phải cùng WiFi
   - Ping từ máy tính đến iPhone

2. **Kiểm tra Firewall:**
   - Windows: Tắt tạm Firewall để test
   - Mac: System Preferences > Security > Firewall

3. **Kiểm tra Backend:**
   ```bash
   # Kiểm tra port đang listen
   netstat -an | findstr 8080
   ```

### Không nhận được alerts

1. **Kiểm tra config:**
   - `ios_api.enabled = true`
   - Backend đã khởi động WebSocket server

2. **Test với camera:**
   - Tạo một fall event
   - Kiểm tra console log
   - Xem iOS app có nhận được không

## Production Setup

Để deploy production:

1. **SSL/TLS:** Dùng `wss://` thay vì `ws://`
2. **Authentication:** Thêm token authentication
3. **Rate Limiting:** Giới hạn số request
4. **Monitoring:** Log tất cả connections

---

**Backend đã sẵn sàng cho iOS app!** ✅
