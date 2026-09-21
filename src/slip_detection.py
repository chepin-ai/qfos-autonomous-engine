"""
Slip Detection Module
Tactile slip detection, incipient slip estimation,
friction limit estimation, and recovery control for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TactileReading:
    """Tactile sensor reading."""
    normal_force_N: float
    shear_force_x_N: float
    shear_force_y_N: float


class TactileSlipDetection:
    """
    Detect slip from tactile sensor arrays.
    """
    
    def __init__(self, threshold_ratio: float = 0.8):
        """
        Args:
            threshold_ratio: Slip threshold ratio
        """
        self.threshold = threshold_ratio
    
    def friction_ratio(self, normal_force_N: float,
                      shear_magnitude_N: float) -> float:
        """
        Compute shear-to-normal ratio.
        
        Args:
            normal_force_N: Normal force
            shear_magnitude_N: Shear magnitude
        
        Returns:
            Friction ratio
        """
        if normal_force_N <= 0:
            return 0.0
        return shear_magnitude_N / normal_force_N
    
    def is_slipping(self, readings: List[TactileReading]) -> bool:
        """
        Detect slip from multiple tactile readings.
        
        Args:
            readings: Tactile readings
        
        Returns:
            True if slipping
        """
        if not readings:
            return False
        ratios = []
        for r in readings:
            shear = math.sqrt(r.shear_force_x_N**2 + r.shear_force_y_N**2)
            ratios.append(self.friction_ratio(r.normal_force_N, shear))
        avg_ratio = sum(ratios) / len(ratios)
        return avg_ratio > self.threshold
    
    def slip_direction(self, readings: List[TactileReading]) -> Tuple[float, float]:
        """
        Estimate slip direction.
        
        Args:
            readings: Tactile readings
        
        Returns:
            Direction vector (x, y)
        """
        if not readings:
            return (0.0, 0.0)
        sx = sum(r.shear_force_x_N for r in readings)
        sy = sum(r.shear_force_y_N for r in readings)
        mag = math.sqrt(sx**2 + sy**2)
        if mag <= 0:
            return (0.0, 0.0)
        return (sx / mag, sy / mag)


class IncipientSlipEstimation:
    """
    Estimate incipient (pre-slip) conditions.
    """
    
    def __init__(self):
        pass
    
    def slip_margin(self, current_friction_ratio: float,
                   static_friction_coefficient: float) -> float:
        """
        Compute safety margin before slip.
        
        Args:
            current_friction_ratio: Current ratio
            static_friction_coefficient: Static friction
        
        Returns:
            Margin (0 = imminent slip)
        """
        if static_friction_coefficient <= 0:
            return 0.0
        return static_friction_coefficient - current_friction_ratio
    
    def time_to_slip(self, current_ratio: float,
                    static_coefficient: float,
                    loading_rate_Ns: float,
                    normal_force_N: float) -> float:
        """
        Estimate time until slip (simplified).
        
        Args:
            current_ratio: Current friction ratio
            static_coefficient: Static friction
            loading_rate_Ns: Shear loading rate
            normal_force_N: Normal force
        
        Returns:
            Time to slip (s)
        """
        if normal_force_N <= 0 or loading_rate_Ns <= 0:
            return float('inf')
        margin_N = (static_coefficient - current_ratio) * normal_force_N
        if margin_N <= 0:
            return 0.0
        return margin_N / loading_rate_Ns


class FrictionLimitEstimation:
    """
    Estimate friction limits from sensor data.
    """
    
    def __init__(self):
        pass
    
    def estimate_static_friction(self, max_observed_ratio: float,
                                safety_factor: float = 1.2) -> float:
        """
        Estimate static friction coefficient.
        
        Args:
            max_observed_ratio: Maximum observed ratio before slip
            safety_factor: Safety factor
        
        Returns:
            Estimated coefficient
        """
        return max_observed_ratio * safety_factor
    
    def estimate_kinetic_friction(self, slip_readings: List[TactileReading]) -> float:
        """
        Estimate kinetic friction coefficient during slip.
        
        Args:
            slip_readings: Readings during slip
        
        Returns:
            Estimated coefficient
        """
        if not slip_readings:
            return 0.0
        ratios = []
        for r in slip_readings:
            shear = math.sqrt(r.shear_force_x_N**2 + r.shear_force_y_N**2)
            if r.normal_force_N > 0:
                ratios.append(shear / r.normal_force_N)
        if not ratios:
            return 0.0
        return sum(ratios) / len(ratios)


class RecoveryControl:
    """
    Recovery control after slip detection.
    """
    
    def __init__(self):
        pass
    
    def grip_adjustment(self, slip_detected: bool,
                       current_grip_force_N: float,
                       target_safety_margin: float = 0.2) -> float:
        """
        Compute adjusted grip force.
        
        Args:
            slip_detected: Whether slip detected
            current_grip_force_N: Current grip
            target_safety_margin: Target margin
        
        Returns:
            Adjusted force (N)
        """
        if slip_detected:
            return current_grip_force_N * (1.0 + target_safety_margin)
        return current_grip_force_N
    
    def contact_reposition(self, slip_direction: Tuple[float, float],
                          step_size_mm: float = 1.0) -> Tuple[float, float]:
        """
        Compute contact repositioning offset.
        
        Args:
            slip_direction: Slip direction
            step_size_mm: Step size
        
        Returns:
            Offset (x, y) mm
        """
        return (-slip_direction[0] * step_size_mm,
                -slip_direction[1] * step_size_mm)


class SlipDetection:
    """
    Unified slip detection controller.
    """
    
    def __init__(self):
        self.tactile = TactileSlipDetection()
        self.incipient = IncipientSlipEstimation()
        self.friction = FrictionLimitEstimation()
        self.recovery = RecoveryControl()
    
    def slip_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["tactile_array", "incipient_estimation", "friction_limit", "recovery"],
            "outputs": ["slip_detected", "direction", "margin"]
        }
