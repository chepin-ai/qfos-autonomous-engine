"""
Bipedal Locomotion Module
Zero moment point, capture point,
walking pattern generation, and balance control for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FootStep:
    """Footstep placement."""
    x: float
    y: float
    theta: float
    support_leg: str  # 'left' or 'right'


class ZeroMomentPoint:
    """
    Zero Moment Point (ZMP) computation.
    """
    
    def __init__(self, gravity: float = 9.81):
        """
        Args:
            gravity: Gravity acceleration
        """
        self.g = gravity
    
    def zmp_from_forces(self, cop_x: float, cop_y: float,
                       horizontal_force_x: float,
                       horizontal_force_y: float,
                       vertical_force: float,
                       com_height_m: float = 1.0) -> Tuple[float, float]:
        """
        Compute ZMP from forces (simplified).
        
        Args:
            cop_x, cop_y: Center of pressure
            horizontal_force_x, horizontal_force_y: Horizontal forces
            vertical_force: Vertical force
            com_height_m: COM height
        
        Returns:
            (zmp_x, zmp_y)
        """
        if vertical_force <= 0:
            return (cop_x, cop_y)
        # Simplified: ZMP = COP - (h/Fz) * (Fx, Fy)
        zmp_x = cop_x - (com_height_m / vertical_force) * horizontal_force_x
        zmp_y = cop_y - (com_height_m / vertical_force) * horizontal_force_y
        return (zmp_x, zmp_y)
    
    def zmp_stability_margin(self, zmp_x: float, zmp_y: float,
                            support_polygon: List[Tuple[float, float]]) -> float:
        """
        Compute stability margin (distance to nearest edge).
        
        Args:
            zmp_x, zmp_y: ZMP position
            support_polygon: Support polygon vertices
        
        Returns:
            Margin (positive = stable)
        """
        if len(support_polygon) < 3:
            return 0.0
        # Simplified: distance to centroid
        cx = sum(p[0] for p in support_polygon) / len(support_polygon)
        cy = sum(p[1] for p in support_polygon) / len(support_polygon)
        dist = math.sqrt((zmp_x - cx)**2 + (zmp_y - cy)**2)
        # Approximate polygon radius
        radius = max(math.sqrt((p[0] - cx)**2 + (p[1] - cy)**2) for p in support_polygon)
        return radius - dist


class CapturePoint:
    """
    Capture point (Viability theory).
    """
    
    def __init__(self, gravity: float = 9.81):
        """
        Args:
            gravity: Gravity
        """
        self.g = gravity
    
    def capture_point(self, com_x: float, com_vx: float,
                     com_height_m: float = 1.0) -> float:
        """
        Compute capture point for 1D motion.
        
        Args:
            com_x: COM position
            com_vx: COM velocity
            com_height_m: COM height
        
        Returns:
            Capture point position
        """
        omega = math.sqrt(self.g / com_height_m)
        return com_x + com_vx / omega
    
    def is_capturable(self, capture_point: float,
                     foot_position: float,
                     max_step_length: float = 0.5) -> bool:
        """
        Check if capture point is reachable.
        
        Args:
            capture_point: Capture point
            foot_position: Current foot position
            max_step_length: Maximum step
        
        Returns:
            True if capturable
        """
        return abs(capture_point - foot_position) <= max_step_length


class WalkingPatternGeneration:
    """
    Generate bipedal walking patterns.
    """
    
    def __init__(self, step_length_m: float = 0.3,
                 step_height_m: float = 0.05,
                 step_time_s: float = 0.8):
        """
        Args:
            step_length_m: Step length
            step_height_m: Foot lift height
            step_time_s: Step duration
        """
        self.step_length = step_length_m
        self.step_height = step_height_m
        self.step_time = step_time_s
    
    def com_trajectory(self, time_s: float,
                      amplitude_m: float = 0.05) -> Tuple[float, float]:
        """
        Compute COM trajectory (lateral oscillation).
        
        Args:
            time_s: Time
            amplitude_m: Oscillation amplitude
        
        Returns:
            (com_x, com_y)
        """
        # Simplified: sinusoidal lateral oscillation
        com_y = amplitude_m * math.sin(2.0 * math.pi * time_s / self.step_time)
        com_x = self.step_length * time_s / self.step_time
        return (com_x, com_y)
    
    def swing_foot_trajectory(self, time_s: float,
                             start_x: float,
                             end_x: float) -> Tuple[float, float]:
        """
        Compute swing foot trajectory.
        
        Args:
            time_s: Time in step
            start_x: Start position
            end_x: End position
        
        Returns:
            (foot_x, foot_z)
        """
        if time_s < 0 or time_s > self.step_time:
            return (end_x, 0.0)
        t_norm = time_s / self.step_time
        # Parabolic trajectory
        foot_x = start_x + (end_x - start_x) * t_norm
        foot_z = 4.0 * self.step_height * t_norm * (1.0 - t_norm)
        return (foot_x, foot_z)


class BalanceControl:
    """
    Balance control for bipedal robots.
    """
    
    def __init__(self, kp: float = 50.0, kd: float = 10.0):
        """
        Args:
            kp: Proportional gain
            kd: Derivative gain
        """
        self.kp = kp
        self.kd = kd
    
    def ankle_strategy(self, com_error_x: float,
                      com_velocity_x: float) -> float:
        """
        Compute ankle torque for balance.
        
        Args:
            com_error_x: COM error
            com_velocity_x: COM velocity
        
        Returns:
            Ankle torque
        """
        return self.kp * com_error_x + self.kd * com_velocity_x
    
    def hip_strategy(self, com_error_x: float,
                    com_acceleration_x: float) -> float:
        """
        Compute hip torque for balance.
        
        Args:
            com_error_x: COM error
            com_acceleration_x: COM acceleration
        
        Returns:
            Hip torque
        """
        return self.kp * com_error_x + self.kd * com_acceleration_x


class BipedalLocomotion:
    """
    Unified bipedal locomotion controller.
    """
    
    def __init__(self):
        self.zmp = ZeroMomentPoint()
        self.capture = CapturePoint()
        self.walking = WalkingPatternGeneration()
        self.balance = BalanceControl()
    
    def locomotion_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["zmp", "capture_point", "walking_pattern", "balance"],
            "outputs": ["stability_margin", "capture_point", "foot_trajectory"]
        }
