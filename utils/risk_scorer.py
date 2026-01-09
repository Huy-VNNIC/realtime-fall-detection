"""
Risk Scoring System
Tính điểm nguy cơ từ 0-100 dựa trên nhiều factors
"""
import numpy as np
from typing import Dict
from core.state_machine import FallState, PersonStateMachine
from core.tracker import PersonTrack


class RiskScorer:
    """
    Calculate risk score (0-100) based on multiple factors
    """
    
    def __init__(self, config: dict):
        self.config = config
        risk_config = config.get('risk_scoring', {})
        
        self.enabled = risk_config.get('enabled', True)
        
        # Weights for different factors
        self.fall_speed_weight = risk_config.get('fall_speed_weight', 0.4)
        self.immobility_weight = risk_config.get('immobility_weight', 0.3)
        self.lying_duration_weight = risk_config.get('lying_duration_weight', 0.3)
        
        # Thresholds
        thresholds = risk_config.get('thresholds', {})
        self.warning_threshold = thresholds.get('warning', 40)
        self.alarm_threshold = thresholds.get('alarm', 65)
        self.emergency_threshold = thresholds.get('emergency', 85)
    
    def calculate_risk_score(
        self,
        track: PersonTrack,
        state_machine: PersonStateMachine,
        immobility_score: float,
        ml_prediction: Dict = None
    ) -> float:
        """
        Calculate risk score (0-100)
        
        Args:
            track: PersonTrack object
            state_machine: PersonStateMachine object
            immobility_score: 0-1, from immobility detector
            ml_prediction: Optional ML classifier output
        
        Returns:
            Risk score 0-100
        """
        if not self.enabled:
            return 0.0
        
        # Component scores (each 0-100)
        fall_speed_score = self._calculate_fall_speed_score(track)
        immobility_component_score = immobility_score * 100
        lying_duration_score = self._calculate_lying_duration_score(state_machine)
        
        # ML classifier boost
        ml_boost = 0
        if ml_prediction and ml_prediction['class'] == 'fall':
            ml_boost = ml_prediction['proba'] * 20  # Up to +20 points
        
        # Weighted sum
        risk_score = (
            fall_speed_score * self.fall_speed_weight +
            immobility_component_score * self.immobility_weight +
            lying_duration_score * self.lying_duration_weight
        ) * 100
        
        # Add ML boost
        risk_score += ml_boost
        
        # State-based adjustments
        risk_score = self._adjust_by_state(risk_score, state_machine)
        
        # Clamp to 0-100
        risk_score = max(0, min(100, risk_score))
        
        return risk_score
    
    def _calculate_fall_speed_score(self, track: PersonTrack) -> float:
        """
        Score based on falling velocity (0-1)
        Fast downward movement = high score
        """
        vy = track.get_centroid_y_speed()
        
        # Normalize velocity (calibrate these values)
        max_fall_velocity = 10.0  # pixels/frame
        normalized = min(vy / max_fall_velocity, 1.0)
        
        return normalized
    
    def _calculate_lying_duration_score(
        self, state_machine: PersonStateMachine
    ) -> float:
        """
        Score based on how long person has been lying (0-1)
        Longer = higher risk
        """
        state = state_machine.current_state
        duration = state_machine.get_state_duration()
        
        if state not in [FallState.FALLEN, FallState.ALARM]:
            return 0.0
        
        # Normalize duration (longer = worse)
        # 0s = 0.0, 30s = 1.0
        max_duration = 30.0
        normalized = min(duration / max_duration, 1.0)
        
        return normalized
    
    def _adjust_by_state(
        self, base_score: float, state_machine: PersonStateMachine
    ) -> float:
        """Adjust score based on current state"""
        state = state_machine.current_state
        
        if state == FallState.STANDING:
            return min(base_score, 30)  # Cap at low risk
        
        elif state == FallState.FALLING:
            return max(base_score, 50)  # Minimum medium risk
        
        elif state == FallState.FALLEN:
            return max(base_score, 60)  # Minimum high risk
        
        elif state == FallState.ALARM:
            return max(base_score, 80)  # Minimum emergency
        
        return base_score
    
    def get_risk_level(self, risk_score: float) -> str:
        """
        Get risk level category
        Returns: 'safe', 'warning', 'alarm', 'emergency'
        """
        if risk_score < self.warning_threshold:
            return 'safe'
        elif risk_score < self.alarm_threshold:
            return 'warning'
        elif risk_score < self.emergency_threshold:
            return 'alarm'
        else:
            return 'emergency'
    
    def get_risk_color(self, risk_score: float) -> tuple:
        """Get color for visualization (BGR)"""
        level = self.get_risk_level(risk_score)
        
        colors = {
            'safe': (0, 255, 0),      # Green
            'warning': (0, 255, 255),  # Yellow
            'alarm': (0, 165, 255),    # Orange
            'emergency': (0, 0, 255)   # Red
        }
        
        return colors.get(level, (255, 255, 255))
    
    def should_trigger_alert(self, risk_score: float) -> bool:
        """Check if risk score warrants an alert"""
        return risk_score >= self.alarm_threshold
