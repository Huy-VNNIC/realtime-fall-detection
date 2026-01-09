# ⚡ QUICK START - 5 PHÚT

## 1️⃣ Install (30 giây)
```bash
cd "/home/dtu/Dectact-camare real time"
pip install -r requirements.txt
```

## 2️⃣ Test (15 giây)
```bash
python test_installation.py
```

## 3️⃣ Run (ngay lập tức)
```bash
python main.py
```

**Xong! Hệ thống đang chạy.**

---

## 🎯 Nếu muốn AI (khuyên dùng)

### Thu data (5 phút):
```bash
cd data
python collector.py --mode fall --duration 60
python collector.py --mode not_fall --duration 60
```

### Train (30 giây):
```bash
python train.py
```

### Enable AI:
Sửa `config.yaml`:
```yaml
ml_classifier:
  enabled: true
```

### Run lại:
```bash
cd ..
python main.py
```

---

## 📱 Nếu cần iOS API

Sửa `config.yaml`:
```yaml
ios_api:
  enabled: true
```

Endpoint: `ws://YOUR_IP:8080/ws`

---

## 🎮 Menu tiện lợi
```bash
./quickstart.sh
```

---

## 📖 Docs đầy đủ
- **USAGE_GUIDE.md** - Hướng dẫn chi tiết
- **PROJECT_STRUCTURE.md** - Kiến trúc
- **BUILD_COMPLETE.md** - Tổng kết

---

**That's it! Enjoy! 🚀**
