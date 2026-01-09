"""
Video Buffer and Recording System
Circular buffer + auto save clips khi alarm
"""
import cv2
import numpy as np
from collections import deque
from typing import Tuple, Optional
import os
from datetime import datetime
import threading


class CircularVideoBuffer:
    """
    Circular buffer to store recent frames
    Used to save video before and after alarm event
    """
    
    def __init__(self, buffer_seconds: int, fps: int = 30):
        self.buffer_seconds = buffer_seconds
        self.fps = fps
        self.max_frames = buffer_seconds * fps
        
        # Circular buffer
        self.buffer = deque(maxlen=self.max_frames)
        self.timestamps = deque(maxlen=self.max_frames)
    
    def add_frame(self, frame: np.ndarray, timestamp: float):
        """Add frame to buffer"""
        self.buffer.append(frame.copy())
        self.timestamps.append(timestamp)
    
    def get_frames(
        self, 
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> list:
        """
        Get frames in time range
        If no range specified, return all frames
        """
        if start_time is None and end_time is None:
            return list(self.buffer)
        
        frames = []
        for frame, ts in zip(self.buffer, self.timestamps):
            if start_time is not None and ts < start_time:
                continue
            if end_time is not None and ts > end_time:
                break
            frames.append(frame)
        
        return frames
    
    def clear(self):
        """Clear buffer"""
        self.buffer.clear()
        self.timestamps.clear()


class VideoRecorder:
    """
    Manage video recording and snapshot saving
    """
    
    def __init__(self, config: dict):
        self.config = config
        record_config = config.get('recording', {})
        
        self.enabled = record_config.get('enabled', True)
        self.output_dir = record_config.get('output_dir', 'recordings')
        self.buffer_seconds = record_config.get('buffer_seconds', 10)
        self.save_before = record_config.get('save_before', 5)
        self.save_after = record_config.get('save_after', 5)
        self.snapshot_format = record_config.get('snapshot_format', 'jpg')
        self.video_codec = record_config.get('video_codec', 'mp4v')
        
        # Get FPS from config
        self.fps = config.get('camera', {}).get('fps', 30)
        
        # Circular buffer
        self.buffer = CircularVideoBuffer(self.buffer_seconds, self.fps)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'snapshots'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'clips'), exist_ok=True)
        
        # Recording state
        self.is_recording_event = False
        self.event_start_time = None
        self.event_frames = []
    
    def add_frame(self, frame: np.ndarray, timestamp: float):
        """Add frame to circular buffer"""
        if not self.enabled:
            return
        
        self.buffer.add_frame(frame, timestamp)
        
        # If recording event, also save to event frames
        if self.is_recording_event:
            self.event_frames.append((frame.copy(), timestamp))
    
    def start_event_recording(self, event_time: float):
        """Start recording an event (after alarm)"""
        if not self.enabled:
            return
        
        self.is_recording_event = True
        self.event_start_time = event_time
        self.event_frames = []
    
    def stop_event_recording(self, event_id: str, track_id: int) -> Tuple[str, str]:
        """
        Stop recording and save video + snapshot
        Returns: (snapshot_path, video_path)
        """
        if not self.enabled or not self.is_recording_event:
            return None, None
        
        self.is_recording_event = False
        
        # Get frames before event (from circular buffer)
        before_time = self.event_start_time - self.save_before
        frames_before = self.buffer.get_frames(start_time=before_time)
        
        # Combine with event frames
        all_frames = frames_before + [f[0] for f in self.event_frames]
        
        if len(all_frames) == 0:
            return None, None
        
        # Generate filenames
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"fall_{event_id}_track{track_id}_{timestamp_str}"
        
        # Save snapshot (last frame)
        snapshot_path = self._save_snapshot(all_frames[-1], base_filename)
        
        # Save video clip
        video_path = self._save_video(all_frames, base_filename)
        
        return snapshot_path, video_path
    
    def _save_snapshot(self, frame: np.ndarray, base_filename: str) -> str:
        """Save snapshot image"""
        filename = f"{base_filename}.{self.snapshot_format}"
        filepath = os.path.join(self.output_dir, 'snapshots', filename)
        
        cv2.imwrite(filepath, frame)
        print(f"[RECORDER] Snapshot saved: {filepath}")
        
        return filepath
    
    def _save_video(self, frames: list, base_filename: str) -> str:
        """Save video clip"""
        if len(frames) == 0:
            return None
        
        filename = f"{base_filename}.mp4"
        filepath = os.path.join(self.output_dir, 'clips', filename)
        
        # Get frame size
        height, width = frames[0].shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*self.video_codec)
        out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
        
        # Write frames
        for frame in frames:
            out.write(frame)
        
        out.release()
        print(f"[RECORDER] Video clip saved: {filepath} ({len(frames)} frames)")
        
        return filepath
    
    def save_immediate_snapshot(
        self, frame: np.ndarray, event_id: str, track_id: int
    ) -> str:
        """Save snapshot immediately (for quick alerts)"""
        if not self.enabled:
            return None
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"snapshot_{event_id}_track{track_id}_{timestamp_str}"
        
        return self._save_snapshot(frame, base_filename)


class AsyncVideoSaver:
    """
    Save videos asynchronously to avoid blocking main thread
    """
    
    def __init__(self, recorder: VideoRecorder):
        self.recorder = recorder
        self.save_queue = []
        self.lock = threading.Lock()
    
    def queue_save(
        self, frames: list, base_filename: str
    ):
        """Queue video save task"""
        with self.lock:
            self.save_queue.append((frames, base_filename))
        
        # Start save thread
        thread = threading.Thread(target=self._process_queue)
        thread.daemon = True
        thread.start()
    
    def _process_queue(self):
        """Process save queue in background"""
        while True:
            with self.lock:
                if len(self.save_queue) == 0:
                    break
                frames, filename = self.save_queue.pop(0)
            
            self.recorder._save_video(frames, filename)
