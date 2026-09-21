"""
Tactile Sensing Module
Pressure distribution, slip detection,
texture classification, and grasp force estimation for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TactileReading:
    """Tactile sensor reading."""
    x: float
    y: float
    pressure_kPa: float
    shear_x: float
    shear_y: float


class PressureDistribution:
    """
    Pressure distribution analysis.
    """
    
    def __init__(self, resolution: int = 10):
        """
        Args:
            resolution: Grid resolution
        """
        self.res = resolution
    
    def total_force(self, readings: List[TactileReading]) -> float:
        """
        Compute total normal force.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Total force in N (simplified: pressure * area)
        """
        if not readings:
            return 0.0
        return sum(r.pressure_kPa for r in readings)
    
    def center_of_pressure(self, readings: List[TactileReading]) -> Tuple[float, float]:
        """
        Compute center of pressure.
        
        Args:
            readings: Sensor readings
        
        Returns:
            (cop_x, cop_y)
        """
        if not readings:
            return 0.0, 0.0
        
        total_p = sum(r.pressure_kPa for r in readings)
        if total_p == 0:
            return 0.0, 0.0
        
        cop_x = sum(r.x * r.pressure_kPa for r in readings) / total_p
        cop_y = sum(r.y * r.pressure_kPa for r in readings) / total_p
        return cop_x, cop_y
    
    def pressure_map(self, readings: List[TactileReading]) -> List[List[float]]:
        """
        Create pressure map grid.
        
        Args:
            readings: Sensor readings
        
        Returns:
            2D pressure grid
        """
        grid = [[0.0 for _ in range(self.res)] for _ in range(self.res)]
        
        for r in readings:
            ix = min(int(r.x * self.res), self.res - 1)
            iy = min(int(r.y * self.res), self.res - 1)
            grid[iy][ix] += r.pressure_kPa
        
        return grid


class SlipDetector:
    """
    Slip detection from tactile data.
    """
    
    def __init__(self, threshold: float = 0.5):
        """
        Args:
            threshold: Slip detection threshold
        """
        self.threshold = threshold
    
    def shear_magnitude(self, reading: TactileReading) -> float:
        """
        Compute shear magnitude.
        
        Args:
            reading: Tactile reading
        
        Returns:
            Shear magnitude
        """
        return math.sqrt(reading.shear_x ** 2 + reading.shear_y ** 2)
    
    def is_slipping(self, reading: TactileReading) -> bool:
        """
        Detect slip.
        
        Args:
            reading: Tactile reading
        
        Returns:
            Whether slipping
        """
        return self.shear_magnitude(reading) > self.threshold
    
    def slip_ratio(self, readings: List[TactileReading]) -> float:
        """
        Compute ratio of slipping sensors.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Slip ratio
        """
        if not readings:
            return 0.0
        slipping = sum(1 for r in readings if self.is_slipping(r))
        return slipping / len(readings)


class TextureClassifier:
    """
    Texture classification from tactile data.
    """
    
    def __init__(self):
        pass
    
    def roughness_index(self, readings: List[TactileReading]) -> float:
        """
        Compute roughness index from pressure variance.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Roughness index
        """
        if not readings:
            return 0.0
        
        pressures = [r.pressure_kPa for r in readings]
        mean_p = sum(pressures) / len(pressures)
        variance = sum((p - mean_p) ** 2 for p in pressures) / len(pressures)
        
        return math.sqrt(variance)
    
    def classify_texture(self, readings: List[TactileReading]) -> str:
        """
        Classify surface texture.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Texture class
        """
        roughness = self.roughness_index(readings)
        if roughness < 0.5:
            return "smooth"
        elif roughness < 2.0:
            return "moderate"
        else:
            return "rough"


class GraspForceEstimator:
    """
    Grasp force estimation from tactile data.
    """
    
    def __init__(self, friction_coefficient: float = 0.5):
        """
        Args:
            friction_coefficient: Friction coefficient
        """
        self.mu = friction_coefficient
    
    def required_normal_force(self, object_weight_N: float,
                             num_contact_points: int = 2) -> float:
        """
        Compute required normal force to prevent slip.
        
        Args:
            object_weight_N: Object weight
            num_contact_points: Number of contacts
        
        Returns:
            Required normal force per contact
        """
        if num_contact_points <= 0 or self.mu <= 0:
            return 0.0
        return object_weight_N / (self.mu * num_contact_points)
    
    def safety_margin(self, actual_force_N: float,
                     required_force_N: float) -> float:
        """
        Compute safety margin.
        
        Args:
            actual_force_N: Actual force
            required_force_N: Required force
        
        Returns:
            Safety margin ratio
        """
        if required_force_N <= 0:
            return 0.0
        return actual_force_N / required_force_N


class TactileSensing:
    """
    Unified tactile sensing controller.
    """
    
    def __init__(self):
        self.pressure = PressureDistribution()
        self.slip = SlipDetector()
        self.texture = TextureClassifier()
        self.grasp = GraspForceEstimator()
    
    def tactile_summary(self) -> Dict:
        """Get summary."""
        return {
            "capabilities": ["pressure", "slip", "texture", "grasp_force"],
            "applications": ["grasping", "manipulation", "exploration"]
        }
