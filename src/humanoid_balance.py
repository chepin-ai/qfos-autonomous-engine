"""
Humanoid Balance Module
Zero moment point, capture point,
linear inverted pendulum, and push recovery for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CoMState:
    """Center of mass state."""
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float


class ZeroMomentPoint:
    """
    Zero Moment Point (ZMP) analysis.
    """
    
    def __init__(self, gravity_m_s2: float = 9.81):
        """
        Args:
            gravity_m_s2: Gravitational acceleration
        """
        self.g = gravity_m_s2
    
    def zmp_from_com(self, com: CoMState,
                    z_c: float) -> Tuple[float, float]:
        """
        Compute ZMP from COM state.
        
        Args:
            com: Center of mass state
            z_c: COM height
        
        Returns:
            (px, py) ZMP position
        """
        if z_c <= 0:
            return com.x, com.y
        px = com.x - (z_c / self.g) * com.vx
        py = com.y - (z_c / self.g) * com.vy
        return px, py
    
    def stability_margin(self, zmp_x: float, zmp_y: float,
                        support_polygon: List[Tuple[float, float]]) -> float:
        """
        Compute stability margin from support polygon edges.
        
        Args:
            zmp_x: ZMP x
            zmp_y: ZMP y
            support_polygon: Support polygon vertices
        
        Returns:
            Minimum distance to edge
        """
        if not support_polygon:
            return 0.0
        
        min_dist = float('inf')
        n = len(support_polygon)
        for i in range(n):
            x1, y1 = support_polygon[i]
            x2, y2 = support_polygon[(i + 1) % n]
            # Distance from point to line segment
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0 and dy == 0:
                dist = math.sqrt((zmp_x - x1)**2 + (zmp_y - y1)**2)
            else:
                t = max(0, min(1, ((zmp_x - x1) * dx + (zmp_y - y1) * dy) / (dx**2 + dy**2)))
                closest_x = x1 + t * dx
                closest_y = y1 + t * dy
                dist = math.sqrt((zmp_x - closest_x)**2 + (zmp_y - closest_y)**2)
            min_dist = min(min_dist, dist)
        
        return min_dist


class CapturePoint:
    """
    Capture point for push recovery.
    """
    
    def __init__(self, gravity_m_s2: float = 9.81):
        """
        Args:
            gravity_m_s2: Gravity
        """
        self.g = gravity_m_s2
    
    def capture_point(self, com: CoMState,
                     z_c: float) -> Tuple[float, float]:
        """
        Compute capture point.
        
        Args:
            com: COM state
            z_c: COM height
        
        Returns:
            Capture point (x, y)
        """
        if z_c <= 0:
            return com.x, com.y
        omega = math.sqrt(self.g / z_c)
        cp_x = com.x + com.vx / omega
        cp_y = com.y + com.vy / omega
        return cp_x, cp_y
    
    def is_capturable(self, capture_x: float, capture_y: float,
                     support_polygon: List[Tuple[float, float]]) -> bool:
        """
        Check if capture point is inside support polygon.
        
        Args:
            capture_x: CP x
            capture_y: CP y
            support_polygon: Support polygon
        
        Returns:
            True if inside
        """
        if not support_polygon:
            return False
        
        # Ray casting
        n = len(support_polygon)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = support_polygon[i]
            xj, yj = support_polygon[j]
            if ((yi > capture_y) != (yj > capture_y) and
                capture_x < (xj - xi) * (capture_y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside


class LinearInvertedPendulum:
    """
    Linear Inverted Pendulum Model (LIPM).
    """
    
    def __init__(self, z_c: float = 0.8,
                 gravity_m_s2: float = 9.81):
        """
        Args:
            z_c: COM height
            gravity_m_s2: Gravity
        """
        self.z_c = z_c
        self.g = gravity_m_s2
        self.omega = math.sqrt(self.g / z_c)
    
    def com_trajectory(self, x0: float, vx0: float,
                      time: float) -> Tuple[float, float]:
        """
        Compute COM position and velocity.
        
        Args:
            x0: Initial position
            vx0: Initial velocity
            time: Time
        
        Returns:
            (x, vx)
        """
        x = x0 * math.cosh(self.omega * time) + (vx0 / self.omega) * math.sinh(self.omega * time)
        vx = x0 * self.omega * math.sinh(self.omega * time) + vx0 * math.cosh(self.omega * time)
        return x, vx
    
    def orbital_energy(self, x: float, vx: float) -> float:
        """
        Compute orbital energy.
        
        Args:
            x: Position
            vx: Velocity
        
        Returns:
            Orbital energy
        """
        return 0.5 * vx**2 - 0.5 * (self.omega * x)**2


class PushRecovery:
    """
    Push recovery strategies.
    """
    
    def __init__(self):
        pass
    
    def required_step_length(self, push_force_N: float,
                            push_duration_s: float,
                            mass_kg: float,
                            z_c: float,
                            gravity: float = 9.81) -> float:
        """
        Compute required step length for push recovery.
        
        Args:
            push_force_N: Push force
            push_duration_s: Push duration
            mass_kg: Robot mass
            z_c: COM height
            gravity: Gravity
        
        Returns:
            Required step length
        """
        if mass_kg <= 0 or z_c <= 0:
            return 0.0
        impulse = push_force_N * push_duration_s
        delta_v = impulse / mass_kg
        omega = math.sqrt(gravity / z_c)
        return delta_v / omega
    
    def ankle_strategy_torque(self, zmp_error_m: float,
                             ankle_stiffness_Nm_rad: float = 500.0) -> float:
        """
        Compute ankle torque for small perturbations.
        
        Args:
            zmp_error_m: ZMP error
            ankle_stiffness_Nm_rad: Ankle stiffness
        
        Returns:
            Required torque
        """
        return ankle_stiffness_Nm_rad * zmp_error_m


class HumanoidBalance:
    """
    Unified humanoid balance controller.
    """
    
    def __init__(self):
        self.zmp = ZeroMomentPoint()
        self.capture = CapturePoint()
        self.lipm = LinearInvertedPendulum()
        self.recovery = PushRecovery()
    
    def balance_summary(self) -> Dict:
        """Get summary."""
        return {
            "models": ["ZMP", "capture_point", "LIPM"],
            "strategies": ["ankle", "hip", "stepping"]
        }
