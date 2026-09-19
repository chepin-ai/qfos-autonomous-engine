"""
Docking Mechanism Module
Capture, latching, sealing, and undocking control
for autonomous spacecraft docking operations.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DockingState(Enum):
    """Docking operational state."""
    IDLE = "idle"
    APPROACHING = "approaching"
    CAPTURING = "capturing"
    LATCHING = "latching"
    SEALING = "sealing"
    DOCKED = "docked"
    UNLATCHING = "unlatching"
    UNDOCKING = "undocking"
    ERROR = "error"


class CaptureStatus(Enum):
    """Capture mechanism status."""
    OPEN = "open"
    PARTIAL = "partial"
    CAPTURED = "captured"
    MISALIGNED = "misaligned"


@dataclass
class AlignmentData:
    """Relative alignment between vehicles."""
    lateral_error_m: float = 0.0
    angular_error_deg: float = 0.0
    closing_velocity_ms: float = 0.0
    range_m: float = 1000.0


class CaptureRing:
    """
    Soft capture ring control.
    """
    
    def __init__(self, capture_range_m: float = 0.5,
                 max_misalignment_deg: float = 5.0):
        """
        Args:
            capture_range_m: Maximum capture range
            max_misalignment_deg: Max angular misalignment
        """
        self.capture_range = capture_range_m
        self.max_misalignment = max_misalignment_deg
        self.status = CaptureStatus.OPEN
    
    def assess_capture(self, alignment: AlignmentData) -> CaptureStatus:
        """
        Assess if capture is possible.
        
        Args:
            alignment: Current alignment
        
        Returns:
            Capture status
        """
        if alignment.range_m > self.capture_range:
            return CaptureStatus.OPEN
        
        if abs(alignment.angular_error_deg) > self.max_misalignment:
            return CaptureStatus.MISALIGNED
        
        if abs(alignment.lateral_error_m) < 0.05 and \
           abs(alignment.angular_error_deg) < 1.0:
            return CaptureStatus.CAPTURED
        
        return CaptureStatus.PARTIAL
    
    def dampen(self, closing_velocity_ms: float) -> float:
        """
        Compute dampening force.
        
        Args:
            closing_velocity_ms: Closing velocity
        
        Returns:
            Dampening force (N)
        """
        # Simple velocity-dependent dampening
        return -500.0 * closing_velocity_ms


class LatchController:
    """
    Hard dock latching control.
    """
    
    def __init__(self, num_latches: int = 12):
        """
        Args:
            num_latches: Number of latches
        """
        self.num_latches = num_latches
        self.latch_states: List[bool] = [False] * num_latches
        self.latch_forces_N: List[float] = [0.0] * num_latches
    
    def engage_latch(self, latch_id: int, force_N: float = 1000.0) -> bool:
        """
        Engage a latch.
        
        Args:
            latch_id: Latch index
            force_N: Engagement force
        
        Returns:
            True if engaged
        """
        if 0 <= latch_id < self.num_latches:
            self.latch_states[latch_id] = True
            self.latch_forces_N[latch_id] = force_N
            return True
        return False
    
    def release_latch(self, latch_id: int) -> bool:
        """Release a latch."""
        if 0 <= latch_id < self.num_latches:
            self.latch_states[latch_id] = False
            self.latch_forces_N[latch_id] = 0.0
            return True
        return False
    
    def all_engaged(self) -> bool:
        """Check if all latches are engaged."""
        return all(self.latch_states)
    
    def engagement_fraction(self) -> float:
        """Get fraction of engaged latches."""
        if self.num_latches == 0:
            return 0.0
        return sum(self.latch_states) / self.num_latches
    
    def total_force(self) -> float:
        """Get total latching force."""
        return sum(self.latch_forces_N)


class SealSystem:
    """
    Docking seal system.
    """
    
    def __init__(self, seal_diameter_m: float = 1.2):
        """
        Args:
            seal_diameter_m: Seal diameter
        """
        self.diameter = seal_diameter_m
        self.seal_engaged = False
        self.pressure_test_passed = False
        self.leak_rate = 0.0  # mbar*L/s
    
    def engage_seal(self):
        """Engage docking seal."""
        self.seal_engaged = True
    
    def release_seal(self):
        """Release docking seal."""
        self.seal_engaged = False
        self.pressure_test_passed = False
    
    def pressure_check(self, target_pressure_mbar: float = 1013.0,
                      tolerance_mbar: float = 10.0) -> bool:
        """
        Check seal integrity.
        
        Args:
            target_pressure_mbar: Target pressure
            tolerance_mbar: Pressure tolerance
        
        Returns:
            True if seal is good
        """
        if not self.seal_engaged:
            return False
        
        # Simulate pressure test
        self.leak_rate = 0.01  # small leak
        self.pressure_test_passed = self.leak_rate < 0.1
        return self.pressure_test_passed
    
    def seal_circumference(self) -> float:
        """Get seal circumference."""
        return math.pi * self.diameter


class DockingController:
    """
    Unified docking controller.
    """
    
    def __init__(self):
        self.capture = CaptureRing()
        self.latch = LatchController()
        self.seal = SealSystem()
        self.state = DockingState.IDLE
        self.alignment = AlignmentData()
    
    def update_alignment(self, lateral_m: float, angular_deg: float,
                        velocity_ms: float, range_m: float):
        """Update relative alignment."""
        self.alignment = AlignmentData(lateral_m, angular_deg, velocity_ms, range_m)
    
    def perform_docking(self) -> DockingState:
        """
        Execute docking sequence.
        
        Returns:
            Current state
        """
        # State machine
        if self.state == DockingState.IDLE:
            self.state = DockingState.APPROACHING
        
        elif self.state == DockingState.APPROACHING:
            cap_status = self.capture.assess_capture(self.alignment)
            if cap_status == CaptureStatus.CAPTURED:
                self.state = DockingState.CAPTURING
            elif cap_status == CaptureStatus.MISALIGNED:
                self.state = DockingState.ERROR
        
        elif self.state == DockingState.CAPTURING:
            # Engage latches
            for i in range(self.latch.num_latches):
                self.latch.engage_latch(i)
            if self.latch.all_engaged():
                self.state = DockingState.LATCHING
        
        elif self.state == DockingState.LATCHING:
            self.seal.engage_seal()
            if self.seal.pressure_check():
                self.state = DockingState.SEALING
        
        elif self.state == DockingState.SEALING:
            self.state = DockingState.DOCKED
        
        return self.state
    
    def undock(self) -> DockingState:
        """
        Execute undocking sequence.
        
        Returns:
            Current state
        """
        if self.state == DockingState.DOCKED:
            self.state = DockingState.UNLATCHING
        
        elif self.state == DockingState.UNLATCHING:
            for i in range(self.latch.num_latches):
                self.latch.release_latch(i)
            if not any(self.latch.latch_states):
                self.seal.release_seal()
                self.state = DockingState.UNDOCKING
        
        elif self.state == DockingState.UNDOCKING:
            self.state = DockingState.IDLE
        
        return self.state
    
    def docking_summary(self) -> Dict:
        """Get docking summary."""
        return {
            "state": self.state.value,
            "capture_status": self.capture.status.value,
            "latch_engagement": self.latch.engagement_fraction(),
            "seal_engaged": self.seal.seal_engaged,
            "seal_test": self.seal.pressure_test_passed,
            "alignment_range_m": self.alignment.range_m,
            "alignment_lateral_m": self.alignment.lateral_error_m
        }
