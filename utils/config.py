"""
Configuration Manager
Load và validate config từ YAML
"""
import yaml
import os
from typing import Dict, Any


class ConfigManager:
    """Load and manage configuration"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load config from YAML file"""
        if not os.path.exists(self.config_path):
            print(f"[WARNING] Config file not found: {self.config_path}")
            print("Using default configuration")
            return self.get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            print(f"[INFO] Config loaded from {self.config_path}")
            return config
            
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            print("Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'camera': {
                'source': 0,
                'width': 640,
                'height': 480,
                'fps': 30
            },
            'detection': {
                'background_subtraction': {
                    'history': 500,
                    'var_threshold': 16,
                    'detect_shadows': False
                },
                'contour': {
                    'min_area': 2000,
                    'max_area': 100000
                },
                'sensitivity': 0.7,
                'fall_duration_threshold': 2.0,
                'immobility_threshold': 5.0,
                'motion_threshold': 50
            },
            'risk_scoring': {
                'enabled': True,
                'fall_speed_weight': 0.4,
                'immobility_weight': 0.3,
                'lying_duration_weight': 0.3,
                'thresholds': {
                    'warning': 40,
                    'alarm': 65,
                    'emergency': 85
                }
            },
            'ml_classifier': {
                'enabled': False,
                'model_path': 'ai/models/fall_classifier.pkl',
                'confidence_threshold': 0.7,
                'window_size': 30
            },
            'recording': {
                'enabled': True,
                'output_dir': 'recordings',
                'buffer_seconds': 10,
                'save_before': 5,
                'save_after': 5,
                'snapshot_format': 'jpg',
                'video_codec': 'mp4v'
            },
            'tracking': {
                'enabled': True,
                'max_disappeared': 30,
                'max_distance': 100
            },
            'roi': {
                'enabled': False,
                'x': 100,
                'y': 100,
                'width': 400,
                'height': 300
            },
            'ios_api': {
                'enabled': False,
                'host': '0.0.0.0',
                'port': 8080,
                'alert_cooldown': 10
            },
            'monitoring': {
                'enabled': True,
                'log_file': 'logs/fall_detection.db',
                'show_fps': True,
                'show_cpu': True
            },
            'dashboard': {
                'enabled': False,
                'update_interval': 1.0
            },
            'debug': {
                'show_video': True,
                'show_contours': True,
                'show_bbox': True,
                'show_info': True,
                'save_frames': False
            }
        }
    
    def get(self, key: str, default=None):
        """Get config value by key (dot notation supported)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set config value by key (dot notation supported)"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, path: str = None):
        """Save config to YAML file"""
        if path is None:
            path = self.config_path
        
        try:
            with open(path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            print(f"[INFO] Config saved to {path}")
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
