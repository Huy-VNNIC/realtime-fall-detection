#!/usr/bin/env python3
"""
TEST WEBCAM - Chạy trên máy local có webcam
Simple version để test nhanh với webcam thật
"""
import cv2
import numpy as np
import time

def test_webcam():
    """Test webcam đơn giản"""
    print("\n" + "="*60)
    print("TEST WEBCAM - FALL DETECTION")
    print("="*60)
    print("\n🎥 Đang mở webcam...")
    
    # Thử các camera index
    for camera_idx in [0, 1, 2]:
        cap = cv2.VideoCapture(camera_idx)
        if cap.isOpened():
            print(f"✓ Webcam tìm thấy tại index: {camera_idx}")
            break
    else:
        print("❌ Không tìm thấy webcam!")
        print("\nKiểm tra:")
        print("  1. Webcam đã được cắm vào?")
        print("  2. Ứng dụng khác đang dùng webcam?")
        print("  3. Permissions webcam OK?")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Get actual resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"📐 Resolution: {width}x{height}")
    
    print("\n" + "="*60)
    print("HƯỚNG DẪN TEST:")
    print("="*60)
    print("  • Nhấn SPACE: Chuyển chế độ test")
    print("  • Nhấn 'q': Thoát")
    print("\nChế độ test:")
    print("  1. RAW - Video gốc")
    print("  2. MOTION - Phát hiện chuyển động")
    print("  3. FALL DETECT - Phát hiện ngã đầy đủ")
    print("="*60 + "\n")
    
    # Background subtractor
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=16,
        detectShadows=False
    )
    
    # Test modes
    modes = ['RAW', 'MOTION', 'FALL_DETECT']
    current_mode = 0
    
    # FPS calculation
    fps_start = time.time()
    frame_count = 0
    fps = 0
    
    print("▶ Bắt đầu! (Mode: RAW)\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Không đọc được frame từ webcam")
            break
        
        display = frame.copy()
        mode = modes[current_mode]
        
        # Process based on mode
        if mode == 'MOTION':
            # Motion detection
            fg_mask = bg_subtractor.apply(frame)
            
            # Find contours
            contours, _ = cv2.findContours(
                fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Draw contours
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:  # Min area
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(display, f"Area: {int(area)}", (x, y-10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        elif mode == 'FALL_DETECT':
            # Full detection
            fg_mask = bg_subtractor.apply(frame)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(
                fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Analyze each contour
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 2000 or area > 100000:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / max(h, 1)
                
                # Determine state
                if aspect_ratio > 1.5:  # Lying
                    color = (0, 0, 255)  # Red
                    status = "NGUY HIEM - NAM"
                    thickness = 3
                elif aspect_ratio > 1.0:  # Bending
                    color = (0, 255, 255)  # Yellow
                    status = "Canh bao"
                    thickness = 2
                else:  # Standing
                    color = (0, 255, 0)  # Green
                    status = "Binh thuong"
                    thickness = 2
                
                # Draw
                cv2.rectangle(display, (x, y), (x+w, y+h), color, thickness)
                
                # Info
                cv2.putText(display, status, (x, y-30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(display, f"AR: {aspect_ratio:.2f}", (x, y-10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Calculate FPS
        frame_count += 1
        if time.time() - fps_start >= 1.0:
            fps = frame_count / (time.time() - fps_start)
            fps_start = time.time()
            frame_count = 0
        
        # Draw UI
        cv2.rectangle(display, (10, 10), (300, 100), (0, 0, 0), -1)
        cv2.rectangle(display, (10, 10), (300, 100), (255, 255, 255), 2)
        
        cv2.putText(display, f"Mode: {mode}", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(display, f"FPS: {fps:.1f}", (20, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display, "SPACE: Change mode | Q: Quit", (20, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Show
        cv2.imshow('Webcam Test - Fall Detection', display)
        
        # Keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n✓ Thoát bởi người dùng")
            break
        elif key == ord(' '):  # Space
            current_mode = (current_mode + 1) % len(modes)
            print(f"→ Chuyển sang mode: {modes[current_mode]}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "="*60)
    print("TEST HOÀN TẤT")
    print("="*60)
    print(f"✓ FPS trung bình: {fps:.1f}")
    print("\nNếu test OK, chạy hệ thống đầy đủ:")
    print("  python3 main.py")
    print()

if __name__ == '__main__':
    try:
        test_webcam()
    except KeyboardInterrupt:
        print("\n\n✓ Dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
