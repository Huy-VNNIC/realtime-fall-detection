"""
Event Logger
SQLite database để log events
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, Optional
import json


class EventLogger:
    """
    Log fall detection events to SQLite database
    """
    
    def __init__(self, config: dict):
        self.config = config
        monitoring_config = config.get('monitoring', {})
        
        self.enabled = monitoring_config.get('enabled', True)
        self.log_file = monitoring_config.get('log_file', 'logs/fall_detection.db')
        
        # Create logs directory
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Initialize database
        if self.enabled:
            self.init_database()
    
    def init_database(self):
        """Create tables if not exist"""
        try:
            conn = sqlite3.connect(self.log_file)
            cursor = conn.cursor()
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    track_id INTEGER,
                    risk_score REAL,
                    state TEXT,
                    snapshot_path TEXT,
                    video_path TEXT,
                    features TEXT,
                    ml_prediction TEXT,
                    notes TEXT
                )
            ''')
            
            # System stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    fps REAL,
                    cpu_usage REAL,
                    num_tracks INTEGER,
                    num_alarms INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"[LOGGER] Database initialized: {self.log_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize database: {e}")
            self.enabled = False
    
    def log_event(
        self,
        event_type: str,
        track_id: Optional[int] = None,
        risk_score: Optional[float] = None,
        state: Optional[str] = None,
        snapshot_path: Optional[str] = None,
        video_path: Optional[str] = None,
        features: Optional[Dict] = None,
        ml_prediction: Optional[Dict] = None,
        notes: Optional[str] = None
    ):
        """Log a fall detection event"""
        if not self.enabled:
            return
        
        try:
            conn = sqlite3.connect(self.log_file)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            # Convert dicts to JSON
            features_json = json.dumps(features) if features else None
            ml_pred_json = json.dumps(ml_prediction) if ml_prediction else None
            
            cursor.execute('''
                INSERT INTO events (
                    timestamp, event_type, track_id, risk_score, state,
                    snapshot_path, video_path, features, ml_prediction, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, event_type, track_id, risk_score, state,
                snapshot_path, video_path, features_json, ml_pred_json, notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Failed to log event: {e}")
    
    def log_system_stats(
        self,
        fps: float,
        cpu_usage: float,
        num_tracks: int,
        num_alarms: int
    ):
        """Log system statistics"""
        if not self.enabled:
            return
        
        try:
            conn = sqlite3.connect(self.log_file)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO system_stats (
                    timestamp, fps, cpu_usage, num_tracks, num_alarms
                ) VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, fps, cpu_usage, num_tracks, num_alarms))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Failed to log system stats: {e}")
    
    def get_recent_events(self, limit: int = 100) -> list:
        """Get recent events from database"""
        if not self.enabled:
            return []
        
        try:
            conn = sqlite3.connect(self.log_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return rows
            
        except Exception as e:
            print(f"[ERROR] Failed to get events: {e}")
            return []
    
    def get_stats_summary(self, hours: int = 24) -> Dict:
        """Get summary statistics for last N hours"""
        if not self.enabled:
            return {}
        
        try:
            conn = sqlite3.connect(self.log_file)
            cursor = conn.cursor()
            
            # Count events by type
            cursor.execute('''
                SELECT event_type, COUNT(*) 
                FROM events 
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
                GROUP BY event_type
            ''', (hours,))
            
            event_counts = dict(cursor.fetchall())
            
            # Get average stats
            cursor.execute('''
                SELECT AVG(fps), AVG(cpu_usage), AVG(num_alarms)
                FROM system_stats
                WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
            ''', (hours,))
            
            avg_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'event_counts': event_counts,
                'avg_fps': avg_stats[0] if avg_stats[0] else 0,
                'avg_cpu': avg_stats[1] if avg_stats[1] else 0,
                'avg_alarms': avg_stats[2] if avg_stats[2] else 0
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get stats: {e}")
            return {}
