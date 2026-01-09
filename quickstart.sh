#!/bin/bash
# Quick Start Script

echo "==================================="
echo "Fall Detection System - Quick Start"
echo "==================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: Please run from project root directory"
    exit 1
fi

# Function to show menu
show_menu() {
    echo ""
    echo "Select option:"
    echo "1) Install dependencies"
    echo "2) Test camera"
    echo "3) Collect training data (fall)"
    echo "4) Collect training data (not_fall)"
    echo "5) Train ML model"
    echo "6) Run system (OpenCV only)"
    echo "7) Run system (with AI)"
    echo "8) Run system (with iOS API)"
    echo "9) View logs"
    echo "0) Exit"
    echo ""
    read -p "Enter choice: " choice
}

install_deps() {
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Done!"
}

test_camera() {
    echo "Testing camera..."
    python -c "import cv2; cap = cv2.VideoCapture(0); print('✓ Camera OK' if cap.isOpened() else '✗ Camera ERROR'); cap.release()"
}

collect_fall_data() {
    echo "Collecting FALL data..."
    echo "Duration (seconds, default 60):"
    read duration
    duration=${duration:-60}
    
    cd data
    python collector.py --mode fall --duration $duration --camera 0
    cd ..
}

collect_normal_data() {
    echo "Collecting NOT_FALL data..."
    echo "Duration (seconds, default 60):"
    read duration
    duration=${duration:-60}
    
    cd data
    python collector.py --mode not_fall --duration $duration --camera 0
    cd ..
}

train_model() {
    echo "Training ML model..."
    cd data
    
    # Check if datasets exist
    if [ ! -d "datasets" ] || [ -z "$(ls -A datasets/*.csv 2>/dev/null)" ]; then
        echo "Error: No training data found!"
        echo "Please collect data first (options 3 and 4)"
        cd ..
        return
    fi
    
    python train.py --input datasets --output ../ai/models/fall_classifier.pkl --model random_forest
    cd ..
}

run_basic() {
    echo "Running system (OpenCV only)..."
    python main.py
}

run_with_ai() {
    echo "Running system (with AI)..."
    
    # Check if model exists
    if [ ! -f "ai/models/fall_classifier.pkl" ]; then
        echo "Error: Model not found!"
        echo "Please train model first (option 5)"
        return
    fi
    
    # Enable ML in config
    python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
config['ml_classifier']['enabled'] = True
with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
print('ML classifier enabled')
"
    
    python main.py
}

run_with_api() {
    echo "Running system (with iOS API)..."
    
    # Enable API in config
    python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
config['ios_api']['enabled'] = True
with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
print('iOS API enabled')
"
    
    # Get IP address
    IP=$(hostname -I | awk '{print $1}')
    echo ""
    echo "WebSocket endpoint: ws://$IP:8080/ws"
    echo ""
    
    python main.py
}

view_logs() {
    echo "Viewing recent logs..."
    
    if [ ! -f "logs/fall_detection.db" ]; then
        echo "No logs found"
        return
    fi
    
    python -c "
import sqlite3
conn = sqlite3.connect('logs/fall_detection.db')
cursor = conn.cursor()

print('\n=== Recent Events ===')
cursor.execute('SELECT timestamp, event_type, track_id, risk_score, state FROM events ORDER BY timestamp DESC LIMIT 10')
rows = cursor.fetchall()
for row in rows:
    print(f'{row[0]} | {row[1]} | Track {row[2]} | Risk: {row[3]:.1f} | {row[4]}')

print('\n=== Event Summary ===')
cursor.execute('SELECT event_type, COUNT(*) FROM events GROUP BY event_type')
rows = cursor.fetchall()
for row in rows:
    print(f'{row[0]}: {row[1]} events')

conn.close()
"
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1) install_deps ;;
        2) test_camera ;;
        3) collect_fall_data ;;
        4) collect_normal_data ;;
        5) train_model ;;
        6) run_basic ;;
        7) run_with_ai ;;
        8) run_with_api ;;
        9) view_logs ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo "Invalid choice" ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
