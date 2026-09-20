"""
Infrared Thermography Module
Thermal image capture, emissivity correction, hotspot detection,
and temperature trend analysis for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ThermalPixel:
    """Thermal pixel data."""
    x: int
    y: int
    temperature_C: float
    emissivity: float


class EmissivityCorrector:
    """
    Correct temperature for emissivity.
    """
    
    def __init__(self, ambient_temp_C: float = 25.0):
        """
        Args:
            ambient_temp_C: Ambient temperature
        """
        self.T_ambient = ambient_temp_C
    
    def correct(self, measured_temp_C: float,
               emissivity: float,
               reflected_temp_C: Optional[float] = None) -> float:
        """
        Correct temperature.
        
        Args:
            measured_temp_C: Measured
            emissivity: Emissivity (0-1)
            reflected_temp_C: Reflected temp
        
        Returns:
            Corrected temperature
        """
        if emissivity <= 0 or emissivity > 1.0:
            return measured_temp_C
        
        T_ref = reflected_temp_C if reflected_temp_C is not None else self.T_ambient
        
        # Stefan-Boltzmann correction approximation
        T_meas_K = measured_temp_C + 273.15
        T_ref_K = T_ref + 273.15
        
        # True radiance = (measured - (1-eps)*reflected) / eps
        T_true_K = ((T_meas_K**4 - (1.0 - emissivity) * T_ref_K**4) / emissivity) ** 0.25
        
        return T_true_K - 273.15
    
    def correct_image(self, pixels: List[ThermalPixel]) -> List[ThermalPixel]:
        """
        Correct entire image.
        
        Args:
            pixels: Pixels
        
        Returns:
            Corrected pixels
        """
        corrected = []
        for p in pixels:
            t = self.correct(p.temperature_C, p.emissivity)
            corrected.append(ThermalPixel(p.x, p.y, t, p.emissivity))
        return corrected


class HotspotDetector:
    """
    Detect thermal hotspots.
    """
    
    def __init__(self, threshold_delta_C: float = 10.0):
        """
        Args:
            threshold_delta_C: Threshold above average
        """
        self.threshold = threshold_delta_C
    
    def detect(self, temperatures_C: List[float],
              width: int, height: int) -> List[Dict]:
        """
        Detect hotspots.
        
        Args:
            temperatures_C: Temperature array
            width: Image width
            height: Image height
        
        Returns:
            Hotspot regions
        """
        if not temperatures_C:
            return []
        
        avg_temp = sum(temperatures_C) / len(temperatures_C)
        hotspots = []
        visited = set()
        
        for i, t in enumerate(temperatures_C):
            if i in visited:
                continue
            
            if t - avg_temp > self.threshold:
                # Find connected region
                region = self._flood_fill(temperatures_C, width, height,
                                         i, avg_temp, visited)
                if region:
                    temps = [temperatures_C[idx] for idx in region]
                    hotspots.append({
                        "size": len(region),
                        "max_temp_C": max(temps),
                        "avg_temp_C": sum(temps) / len(temps),
                        "center": self._center(region, width)
                    })
        
        return hotspots
    
    def _flood_fill(self, temps: List[float], w: int, h: int,
                   start: int, avg: float, visited: set) -> List[int]:
        """Flood fill connected hotspot."""
        region = []
        stack = [start]
        
        while stack:
            idx = stack.pop()
            if idx in visited or idx < 0 or idx >= len(temps):
                continue
            
            if temps[idx] - avg <= self.threshold:
                continue
            
            visited.add(idx)
            region.append(idx)
            
            # Add neighbors
            x = idx % w
            y = idx // w
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    stack.append(ny * w + nx)
        
        return region
    
    def _center(self, region: List[int], width: int) -> Tuple[int, int]:
        """Compute region center."""
        xs = [idx % width for idx in region]
        ys = [idx // width for idx in region]
        return (int(sum(xs) / len(xs)), int(sum(ys) / len(ys)))


class TemperatureTrendAnalyzer:
    """
    Analyze temperature trends over time.
    """
    
    def __init__(self):
        self.history: List[Dict] = []
    
    def add_measurement(self, timestamp: float,
                       temperatures_C: List[float]):
        """
        Add measurement.
        
        Args:
            timestamp: Time
            temperatures_C: Temperatures
        """
        if temperatures_C:
            self.history.append({
                "time": timestamp,
                "max": max(temperatures_C),
                "min": min(temperatures_C),
                "mean": sum(temperatures_C) / len(temperatures_C)
            })
    
    def trend_slope(self) -> float:
        """
        Compute mean temperature trend slope.
        
        Returns:
            Slope (C per time unit)
        """
        if len(self.history) < 2:
            return 0.0
        
        n = len(self.history)
        sum_t = sum(h["time"] for h in self.history)
        sum_m = sum(h["mean"] for h in self.history)
        sum_tt = sum(h["time"]**2 for h in self.history)
        sum_tm = sum(h["time"] * h["mean"] for h in self.history)
        
        denom = n * sum_tt - sum_t**2
        if denom == 0:
            return 0.0
        
        return (n * sum_tm - sum_t * sum_m) / denom
    
    def is_overheating(self, threshold_slope: float = 0.5) -> bool:
        """
        Check if overheating.
        
        Args:
            threshold_slope: Threshold
        
        Returns:
            True if overheating
        """
        return self.trend_slope() > threshold_slope


class InfraredThermography:
    """
    Unified IR thermography controller.
    """
    
    def __init__(self, ambient_temp_C: float = 25.0):
        self.corrector = EmissivityCorrector(ambient_temp_C)
        self.detector = HotspotDetector()
        self.trend = TemperatureTrendAnalyzer()
        self.pixels: List[ThermalPixel] = []
    
    def capture(self, temperatures_C: List[float],
               emissivities: List[float],
               width: int, height: int):
        """
        Capture thermal image.
        
        Args:
            temperatures_C: Raw temps
            emissivities: Emissivities
            width: Width
            height: Height
        """
        self.pixels = []
        for i, (t, e) in enumerate(zip(temperatures_C, emissivities)):
            x = i % width
            y = i // width
            self.pixels.append(ThermalPixel(x, y, t, e))
    
    def inspect(self) -> Dict:
        """
        Inspect for defects.
        
        Returns:
            Results
        """
        corrected = self.corrector.correct_image(self.pixels)
        temps = [p.temperature_C for p in corrected]
        
        w = max(p.x for p in corrected) + 1 if corrected else 1
        h = max(p.y for p in corrected) + 1 if corrected else 1
        
        hotspots = self.detector.detect(temps, w, h)
        
        return {
            "hotspots": len(hotspots),
            "max_temp_C": max(temps) if temps else 0.0,
            "avg_temp_C": sum(temps) / len(temps) if temps else 0.0,
            "regions": hotspots[:3]
        }
    
    def add_timepoint(self, timestamp: float):
        """
        Add timepoint for trend analysis.
        
        Args:
            timestamp: Time
        """
        temps = [p.temperature_C for p in self.pixels]
        self.trend.add_measurement(timestamp, temps)
    
    def ir_summary(self) -> Dict:
        """Get summary."""
        return {
            "pixels": len(self.pixels),
            "hotspots": 0,
            "trend_slope": self.trend.trend_slope()
        }
