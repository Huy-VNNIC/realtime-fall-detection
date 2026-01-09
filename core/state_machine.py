"""
State Machine for Fall Detection
Quản lý states: STANDING -> FALLING -> FALLEN -> ALARM
"""
from enum import Enum
import time
from typing import Dict, Optional
from core.tracker import PersonTrack


class FallState(Enum):
    """Fall states"""
    STANDING = "standing"
    BENDING = "bending"
    FALLING = "falling"
    FALLEN = "fallen"
    ALARM = "alarm"


class PersonStateMachine:
    """
    State machine cho một người
    Theo dõi trạng thái và trigger alarm
    """
    
    def __init__(self, track_id: int, config: dict):
        self.track_id = track_id
        self.config = config
        
        # State
        self.current_state = FallState.STANDING
        self.state_start_time = time.time()
        
        # Thresholds
        self.fall_duration_threshold = config['detection']['fall_duration_threshold']
        self.immobility_threshold = config['detection']['immobility_threshold']
        
        # Fall detection criteria
        self.aspect_ratio_threshold = 1.5  # width/height > 1.5 = lying
        self.angle_threshold = (60, 120)   # Angle range for horizontal
        self.centroid_y_threshold = 0.6    # Low in frame
        
        # History
        self.state_history = [(FallState.STANDING, time.time())]
        self.alarm_triggered = False
        self.alarm_time = None
        
    def update(
        self, 
        track: PersonTrack,
        motion_energy: float,
        ml_prediction: Optional[Dict] = None
    ) -> FallState:
        """
        Update state based on features
        Args:
            track: PersonTrack object
            motion_energy: Motion energy in bbox
            ml_prediction: Optional ML classifier output {'class': 'fall', 'proba': 0.9}
        """
        features = track.last_features
        current_time = time.time()
        time_in_state = current_time - self.state_start_time
        
        # Get fall indicators
        is_lying = self._is_lying_position(features)
        is_falling_fast = self._is_falling_fast(track)
        is_immobile = motion_energy < self.config['detection']['motion_threshold']
        
        # ML classifier override (if available and confident)
        if ml_prediction and ml_prediction.get('proba', 0) > 0.8:
            if ml_prediction['class'] == 'fall':
                is_lying = True
        
        # State transitions
        new_state = self.current_state
        
        if self.current_state == FallState.STANDING:
            if is_lying or is_falling_fast:
                new_state = FallState.FALLING
                
        elif self.current_state == FallState.FALLING:
            if is_lying:
                if time_in_state >= self.fall_duration_threshold:
                    new_state = FallState.FALLEN
            else:
                # False alarm - back to standing
                new_state = FallState.STANDING
                
        elif self.current_state == FallState.FALLEN:
            if is_immobile and time_in_state >= self.immobility_threshold:
                new_state = FallState.ALARM
            elif not is_lying:
                # Person got up
                new_state = FallState.STANDING
                
        elif self.current_state == FallState.ALARM:
            if not is_lying:
                # Person recovered
                new_state = FallState.STANDING
                self.alarm_triggered = False
        
        # Update state
        if new_state != self.current_state:
            self._transition_to(new_state)
        
        # Trigger alarm
        if new_state == FallState.ALARM and not self.alarm_triggered:
            self.alarm_triggered = True
            self.alarm_time = current_time
        
        return self.current_state
    
    def _is_lying_position(self, features: Dict) -> bool:
        """Check if person is in lying position - STRICT VERSION"""
        aspect_ratio = features['aspect_ratio']
        angle = features['angle']
        centroid_y_ratio = features['centroid_y_ratio']
        
        # Lying indicators (STRICTER):
        # 1. Wide aspect ratio (width > height) - MUST HAVE
        is_wide = aspect_ratio > self.aspect_ratio_threshold
        
        # 2. Horizontal angle
        is_horizontal = (
            angle < self.angle_threshold[0] or 
            angle > self.angle_threshold[1]
        )
        
        # 3. Low in frame
        is_low = centroid_y_ratio > self.centroid_y_threshold
        
        # ⚙️ Cần 2/3 indicators (balance giữa accuracy và sensitivity)
        indicators = sum([is_wide, is_horizontal, is_low])
        return indicators >= 2
    
    def _is_falling_fast(self, track: PersonTrack) -> bool:
        """Check if person is falling with high velocity"""
        vy = track.get_centroid_y_speed()
        
        # ⚙️ Giảm từ 8.0 → 6.0 (nhạy hơn nhưng vẫn tránh false alarm)
        fall_speed_threshold = 6.0
        return vy > fall_speed_threshold
    
    def _transition_to(self, new_state: FallState):
        """Transition to new state"""
        self.current_state = new_state
        self.state_start_time = time.time()
        self.state_history.append((new_state, self.state_start_time))
        
        # Keep only recent history
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    def get_state_duration(self) -> float:
        """Get duration in current state"""
        return time.time() - self.state_start_time
    
    def reset(self):
        """Reset to standing state"""
        self._transition_to(FallState.STANDING)
        self.alarm_triggered = False
        self.alarm_time = None


class StateMachineManager:
    """
    Quản lý state machines cho nhiều người
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.state_machines: Dict[int, PersonStateMachine] = {}
    
    def update(
        self,
        track_id: int,
        track: PersonTrack,
        motion_energy: float,
        ml_prediction: Optional[Dict] = None
    ) -> FallState:
        """Update state machine for a person"""
        
        # Create state machine if not exists
        if track_id not in self.state_machines:
            self.state_machines[track_id] = PersonStateMachine(track_id, self.config)
        
        sm = self.state_machines[track_id]
        return sm.update(track, motion_energy, ml_prediction)
    
    def get_state(self, track_id: int) -> Optional[FallState]:
        """Get current state for a person"""
        sm = self.state_machines.get(track_id)
        return sm.current_state if sm else None
    
    def get_state_machine(self, track_id: int) -> Optional[PersonStateMachine]:
        """Get state machine object"""
        return self.state_machines.get(track_id)
    
    def remove_state_machine(self, track_id: int):
        """Remove state machine when track is lost"""
        if track_id in self.state_machines:
            del self.state_machines[track_id]
    
    def get_alarms(self) -> Dict[int, PersonStateMachine]:
        """Get all persons in ALARM state"""
        alarms = {}
        for track_id, sm in self.state_machines.items():
            if sm.current_state == FallState.ALARM:
                alarms[track_id] = sm
        return alarms
