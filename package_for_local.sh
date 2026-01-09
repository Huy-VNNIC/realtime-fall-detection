#!/bin/bash
# Script để đóng gói project về máy local

echo "=========================================="
echo "PACKAGE PROJECT FOR LOCAL TESTING"
echo "=========================================="
echo ""

PROJECT_DIR="/home/dtu/Dectact-camare real time"
OUTPUT_FILE="fall-detection-system.tar.gz"

cd "$PROJECT_DIR/.." || exit 1

echo "📦 Đang đóng gói project..."
echo ""

# Create tar.gz excluding unnecessary files
tar -czf "$OUTPUT_FILE" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude=".git" \
    --exclude="logs/*.db" \
    --exclude="recordings/*" \
    --exclude="data/datasets/*" \
    --exclude="ai/models/*.pkl" \
    "Dectact-camare real time"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo "✅ Đóng gói thành công!"
    echo ""
    echo "📁 File: $OUTPUT_FILE"
    echo "📊 Size: $SIZE"
    echo ""
    echo "=========================================="
    echo "HƯỚNG DẪN DOWNLOAD VỀ MÁY LOCAL"
    echo "=========================================="
    echo ""
    echo "Cách 1: SCP (nếu có SSH)"
    echo "  scp user@server:$(pwd)/$OUTPUT_FILE ~/Downloads/"
    echo ""
    echo "Cách 2: SFTP"
    echo "  # Dùng SFTP client để download file"
    echo ""
    echo "Cách 3: Copy qua USB/network share"
    echo "  File location: $(pwd)/$OUTPUT_FILE"
    echo ""
    echo "=========================================="
    echo "SAU KHI DOWNLOAD"
    echo "=========================================="
    echo ""
    echo "1. Giải nén:"
    echo "   cd ~/Downloads"
    echo "   tar -xzf $OUTPUT_FILE"
    echo ""
    echo "2. Install:"
    echo "   cd 'Dectact-camare real time'"
    echo "   pip3 install opencv-python numpy pyyaml"
    echo ""
    echo "3. Test webcam:"
    echo "   python3 test_webcam_simple.py"
    echo ""
    echo "4. Hoặc chạy đầy đủ:"
    echo "   pip3 install -r requirements.txt"
    echo "   python3 main.py"
    echo ""
    echo "✨ Done! Xem TEST_WEBCAM_LOCAL.md để biết thêm chi tiết"
    echo ""
else
    echo "❌ Lỗi khi đóng gói"
    exit 1
fi
