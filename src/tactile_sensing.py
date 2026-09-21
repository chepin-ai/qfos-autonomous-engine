"""
Tactile Sensing Module
Tactile array processing, slip detection from texture,
force distribution estimation, and material identification for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TactileReading:
    """Single tactile sensor reading."""
    x: int
    y: int
    pressure: float
    shear_x: float
    shear_y: float


class TactileArrayProcessing:
    """
    Process tactile sensor arrays.
    """
    
    def __init__(self, width: int = 16, height: int = 16):
        """
        Args:
            width, height: Array dimensions
        """
        self.width = width
        self.height = height
    
    def total_force(self, readings: List[TactileReading]) -> float:
        """
        Compute total normal force.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Total force
        """
        return sum(r.pressure for r in readings)
    
    def center_of_pressure(self, readings: List[TactileReading]) -> Tuple[float, float]:
        """
        Compute center of pressure.
        
        Args:
            readings: Sensor readings
        
        Returns:
            (x, y) center
        """
        total = self.total_force(readings)
        if total <= 0:
            return (0.0, 0.0)
        x = sum(r.x * r.pressure for r in readings) / total
        y = sum(r.y * r.pressure for r in readings) / total
        return (x, y)
    
    def pressure_map(self, readings: List[TactileReading]) -> List[List[float]]:
        """
        Build pressure map.
        
        Args:
            readings: Sensor readings
        
        Returns:
            2D pressure array
        """
        pmap = [[0.0] * self.width for _ in range(self.height)]
        for r in readings:
            if 0 <= r.x < self.width and 0 <= r.y < self.height:
                pmap[r.y][r.x] = r.pressure
        return pmap


class SlipDetectionFromTexture:
    """
    Detect slip from tactile texture patterns.
    """
    
    def __init__(self):
        pass
    
    def texture_variation(self, readings: List[TactileReading]) -> float:
        """
        Compute texture variation as slip indicator.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Variation measure
        """
        if len(readings) < 2:
            return 0.0
        mean_p = sum(r.pressure for r in readings) / len(readings)
        var = sum((r.pressure - mean_p) ** 2 for r in readings) / len(readings)
        return math.sqrt(var)
    
    def shear_magnitude(self, readings: List[TactileReading]) -> float:
        """
        Compute total shear magnitude.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Shear magnitude
        """
        return math.sqrt(sum(r.shear_x**2 + r.shear_y**2 for r in readings))
    
    def is_slipping(self, readings: List[TactileReading],
                   threshold: float = 5.0) -> bool:
        """
        Detect slip from readings.
        
        Args:
            readings: Sensor readings
            threshold: Slip threshold
        
        Returns:
            True if slipping
        """
        shear = self.shear_magnitude(readings)
        return shear > threshold


class ForceDistributionEstimation:
    """
    Estimate force distribution from tactile data.
    """
    
    def __init__(self):
        pass
    
    def contact_area(self, readings: List[TactileReading],
                    threshold: float = 0.1) -> int:
        """
        Count sensors in contact.
        
        Args:
            readings: Sensor readings
            threshold: Contact threshold
        
        Returns:
            Number of active sensors
        """
        return sum(1 for r in readings if r.pressure > threshold)
    
    def average_pressure(self, readings: List[TactileReading]) -> float:
        """
        Compute average pressure.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Average pressure
        """
        if not readings:
            return 0.0
        return sum(r.pressure for r in readings) / len(readings)
    
    def pressure_gradient(self, readings: List[TactileReading]) -> Tuple[float, float]:
        """
        Compute pressure gradient.
        
        Args:
            readings: Sensor readings
        
        Returns:
            (dx, dy) gradient
        """
        if len(readings) < 2:
            return (0.0, 0.0)
        max_p = max(r.pressure for r in readings)
        min_p = min(r.pressure for r in readings)
        max_r = max(readings, key=lambda r: r.pressure)
        min_r = min(readings, key=lambda r: r.pressure)
        dx = max_r.x - min_r.x
        dy = max_r.y - min_r.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist <= 0:
            return (0.0, 0.0)
        return ((max_p - min_p) * dx / dist, (max_p - min_p) * dy / dist)


class MaterialIdentification:
    """
    Identify material from tactile properties.
    """
    
    def __init__(self):
        self.materials = {
            "metal": {"hardness": 0.9, "roughness": 0.1},
            "plastic": {"hardness": 0.5, "roughness": 0.3},
            "rubber": {"hardness": 0.3, "roughness": 0.7},
            "wood": {"hardness": 0.6, "roughness": 0.5},
        }
    
    def identify(self, hardness: float, roughness: float) -> str:
        """
        Identify material from properties.
        
        Args:
            hardness: Hardness estimate (0-1)
            roughness: Roughness estimate (0-1)
        
        Returns:
            Material name
        """
        best_match = "unknown"
        min_dist = float('inf')
        for name, props in self.materials.items():
            dist = math.sqrt((hardness - props["hardness"])**2 +
                           (roughness - props["roughness"])**2)
            if dist < min_dist:
                min_dist = dist
                best_match = name
        return best_match


class TactileSensing:
    """
    Unified tactile sensing controller.
    """
    
    def __init__(self):
        self.array = TactileArrayProcessing()
        self.slip = SlipDetectionFromTexture()
        self.force = ForceDistributionEstimation()
        self.material = MaterialIdentification()
    
    def tactile_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["array_processing", "slip_detection", "force_distribution", "material_id"],
            "outputs": ["total_force", "center_of_pressure", "slip_status", "material"]
        }
