"""
Contact Detection Module
Force/torque contact sensing, tactile array processing,
proximity detection, and slip estimation for autonomous manipulation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ContactType(Enum):
    """Types of contact."""
    NONE = "none"
    FORCE = "force"
    TACTILE = "tactile"
    PROXIMITY = "proximity"
    SLIP = "slip"


@dataclass
class Wrench:
    """Force and torque vector."""
    fx: float = 0.0
    fy: float = 0.0
    fz: float = 0.0
    tx: float = 0.0
    ty: float = 0.0
    tz: float = 0.0
    
    def magnitude(self) -> float:
        """Compute force magnitude."""
        return math.sqrt(self.fx**2 + self.fy**2 + self.fz**2)
    
    def torque_magnitude(self) -> float:
        """Compute torque magnitude."""
        return math.sqrt(self.tx**2 + self.ty**2 + self.tz**2)


class ForceContactDetector:
    """
    Detect contact from force/torque threshold crossing.
    """
    
    def __init__(self, force_threshold_N: float = 1.0,
                 torque_threshold_Nm: float = 0.1):
        """
        Args:
            force_threshold_N: Force threshold
            torque_threshold_Nm: Torque threshold
        """
        self.f_thresh = force_threshold_N
        self.t_thresh = torque_threshold_Nm
    
    def detect(self, wrench: Wrench) -> bool:
        """
        Detect if contact occurred.
        
        Args:
            wrench: Measured wrench
        
        Returns:
            True if contact
        """
        return (wrench.magnitude() > self.f_thresh or
                wrench.torque_magnitude() > self.t_thresh)
    
    def contact_direction(self, wrench: Wrench) -> Tuple[float, float, float]:
        """
        Estimate contact direction.
        
        Args:
            wrench: Measured wrench
        
        Returns:
            Unit direction vector
        """
        mag = wrench.magnitude()
        if mag < 1e-6:
            return (0.0, 0.0, 0.0)
        return (wrench.fx / mag, wrench.fy / mag, wrench.fz / mag)


class TactileArray:
    """
    Tactile sensor array processor.
    """
    
    def __init__(self, rows: int = 8, cols: int = 8):
        """
        Args:
            rows: Array rows
            cols: Array columns
        """
        self.rows = rows
        self.cols = cols
        self.pressure: List[List[float]] = [[0.0] * cols for _ in range(rows)]
    
    def set_pressure(self, row: int, col: int, value: float):
        """Set pressure at cell."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.pressure[row][col] = value
    
    def total_force(self) -> float:
        """
        Compute total force.
        
        Returns:
            Sum of all pressures
        """
        return sum(sum(row) for row in self.pressure)
    
    def center_of_pressure(self) -> Tuple[float, float]:
        """
        Compute center of pressure.
        
        Returns:
            (row, col) centroid
        """
        total = self.total_force()
        if total < 1e-6:
            return (self.rows / 2.0, self.cols / 2.0)
        
        row_sum = sum(i * sum(self.pressure[i]) for i in range(self.rows))
        col_sum = sum(j * self.pressure[i][j]
                      for i in range(self.rows) for j in range(self.cols))
        
        return (row_sum / total, col_sum / total)
    
    def max_pressure(self) -> float:
        """
        Find maximum pressure.
        
        Returns:
            Max pressure value
        """
        return max(max(row) for row in self.pressure)


class ProximityDetector:
    """
    Proximity sensor processor.
    """
    
    def __init__(self, threshold_mm: float = 5.0):
        """
        Args:
            threshold_mm: Detection threshold
        """
        self.threshold = threshold_mm
    
    def detect(self, distance_mm: float) -> bool:
        """
        Detect proximity.
        
        Args:
            distance_mm: Measured distance
        
        Returns:
            True if object nearby
        """
        return 0.0 < distance_mm < self.threshold
    
    def approach_velocity(self, d1: float, d2: float,
                         dt: float) -> float:
        """
        Compute approach velocity.
        
        Args:
            d1: Distance at t1
            d2: Distance at t2
            dt: Time interval
        
        Returns:
            Approach velocity (positive = approaching)
        """
        if dt <= 0:
            return 0.0
        return (d1 - d2) / dt


class SlipDetector:
    """
    Detect slip from force and motion.
    """
    
    def __init__(self, friction_coefficient: float = 0.5):
        """
        Args:
            friction_coefficient: Static friction coefficient
        """
        self.mu = friction_coefficient
    
    def detect_slip(self, normal_force_N: float,
                   tangential_force_N: float) -> bool:
        """
        Detect slip condition.
        
        Args:
            normal_force_N: Normal force
            tangential_force_N: Tangential force
        
        Returns:
            True if slipping
        """
        if normal_force_N <= 0:
            return False
        max_friction = self.mu * normal_force_N
        return tangential_force_N > max_friction
    
    def safety_margin(self, normal_force_N: float,
                     tangential_force_N: float) -> float:
        """
        Compute safety margin.
        
        Args:
            normal_force_N: Normal force
            tangential_force_N: Tangential force
        
        Returns:
            Margin (1.0 = at limit)
        """
        if normal_force_N <= 0:
            return 0.0
        max_friction = self.mu * normal_force_N
        if max_friction <= 0:
            return 0.0
        return tangential_force_N / max_friction


class ContactDetection:
    """
    Unified contact detection controller.
    """
    
    def __init__(self):
        self.force = ForceContactDetector()
        self.tactile = TactileArray()
        self.proximity = ProximityDetector()
        self.slip = SlipDetector()
        self.contact_history: List[Dict] = []
    
    def update(self, wrench: Wrench,
              proximity_mm: Optional[float] = None) -> Dict:
        """
        Update contact state.
        
        Args:
            wrench: Measured wrench
            proximity_mm: Proximity distance
        
        Returns:
            Contact state
        """
        force_contact = self.force.detect(wrench)
        tactile_contact = self.tactile.total_force() > 0.1
        prox_contact = self.proximity.detect(proximity_mm) if proximity_mm is not None else False
        
        contact_type = ContactType.NONE
        if force_contact:
            contact_type = ContactType.FORCE
        elif tactile_contact:
            contact_type = ContactType.TACTILE
        elif prox_contact:
            contact_type = ContactType.PROXIMITY
        
        state = {
            "contact": force_contact or tactile_contact or prox_contact,
            "type": contact_type.value,
            "force_N": wrench.magnitude(),
            "torque_Nm": wrench.torque_magnitude()
        }
        self.contact_history.append(state)
        return state
    
    def contact_summary(self) -> Dict:
        """Get contact summary."""
        if not self.contact_history:
            return {"status": "no_data"}
        
        contacts = sum(1 for h in self.contact_history if h["contact"])
        return {
            "total_updates": len(self.contact_history),
            "contact_events": contacts,
            "contact_ratio": contacts / len(self.contact_history)
        }
