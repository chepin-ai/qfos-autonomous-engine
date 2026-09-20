"""
Thermal Imaging Module
Temperature distribution analysis, hotspot detection,
thermal gradient computation, and emissivity correction
for autonomous non-destructive inspection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TemperatureUnit(Enum):
    """Temperature units."""
    CELSIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "K"


@dataclass
class ThermalPixel:
    """A single thermal image pixel."""
    x: int
    y: int
    temperature_C: float
    emissivity: float = 0.95


class TemperatureConverter:
    """
    Convert between temperature units.
    """
    
    @staticmethod
    def celsius_to_kelvin(c: float) -> float:
        """C to K."""
        return c + 273.15
    
    @staticmethod
    def kelvin_to_celsius(k: float) -> float:
        """K to C."""
        return k - 273.15
    
    @staticmethod
    def celsius_to_fahrenheit(c: float) -> float:
        """C to F."""
        return c * 9.0 / 5.0 + 32.0
    
    @staticmethod
    def fahrenheit_to_celsius(f: float) -> float:
        """F to C."""
        return (f - 32.0) * 5.0 / 9.0


class HotspotDetector:
    """
    Detect thermal hotspots and coldspots.
    """
    
    def __init__(self, threshold_delta_K: float = 10.0):
        """
        Args:
            threshold_delta_K: Temperature difference threshold
        """
        self.threshold = threshold_delta_K
    
    def detect(self, pixels: List[ThermalPixel]) -> List[ThermalPixel]:
        """
        Detect hotspots.
        
        Args:
            pixels: Thermal image pixels
        
        Returns:
            Hotspot pixels
        """
        if not pixels:
            return []
        
        avg_temp = sum(p.temperature_C for p in pixels) / len(pixels)
        return [p for p in pixels if p.temperature_C - avg_temp > self.threshold]
    
    def max_temperature(self, pixels: List[ThermalPixel]) -> float:
        """
        Find maximum temperature.
        
        Args:
            pixels: Pixels
        
        Returns:
            Max temperature
        """
        if not pixels:
            return 0.0
        return max(p.temperature_C for p in pixels)
    
    def min_temperature(self, pixels: List[ThermalPixel]) -> float:
        """
        Find minimum temperature.
        
        Args:
            pixels: Pixels
        
        Returns:
            Min temperature
        """
        if not pixels:
            return 0.0
        return min(p.temperature_C for p in pixels)
    
    def thermal_uniformity(self, pixels: List[ThermalPixel]) -> float:
        """
        Compute thermal uniformity index.
        
        Args:
            pixels: Pixels
        
        Returns:
            Uniformity (0=non-uniform, 1=uniform)
        """
        if len(pixels) < 2:
            return 1.0
        
        temps = [p.temperature_C for p in pixels]
        avg = sum(temps) / len(temps)
        if avg == 0:
            return 1.0
        
        std = math.sqrt(sum((t - avg)**2 for t in temps) / len(temps))
        # Lower std relative to avg = more uniform
        return max(0.0, 1.0 - std / abs(avg))


class ThermalGradient:
    """
    Compute thermal gradients.
    """
    
    def __init__(self):
        pass
    
    def gradient_x(self, pixels: List[ThermalPixel],
                  grid_width: int) -> List[float]:
        """
        Compute horizontal gradient.
        
        Args:
            pixels: Pixels in row-major order
            grid_width: Image width
        
        Returns:
            Gradient values
        """
        grads = []
        for i, p in enumerate(pixels):
            if i % grid_width == grid_width - 1:
                grads.append(0.0)
            elif i + 1 < len(pixels):
                grads.append(pixels[i + 1].temperature_C - p.temperature_C)
            else:
                grads.append(0.0)
        return grads
    
    def gradient_magnitude(self, pixels: List[ThermalPixel],
                          grid_width: int) -> List[float]:
        """
        Compute gradient magnitude.
        
        Args:
            pixels: Pixels
            grid_width: Image width
        
        Returns:
            Gradient magnitudes
        """
        gx = self.gradient_x(pixels, grid_width)
        gy = []
        for i, p in enumerate(pixels):
            below = i + grid_width
            if below < len(pixels):
                gy.append(pixels[below].temperature_C - p.temperature_C)
            else:
                gy.append(0.0)
        
        return [math.sqrt(gx[i]**2 + gy[i]**2) for i in range(len(pixels))]
    
    def max_gradient(self, pixels: List[ThermalPixel],
                    grid_width: int) -> float:
        """
        Find maximum gradient.
        
        Args:
            pixels: Pixels
            grid_width: Image width
        
        Returns:
            Max gradient
        """
        grads = self.gradient_magnitude(pixels, grid_width)
        return max(grads) if grads else 0.0


class EmissivityCorrector:
    """
    Correct temperature for emissivity.
    """
    
    def __init__(self):
        self.ambient_temp_C = 25.0
    
    def correct_temperature(self, measured_temp_C: float,
                           emissivity: float) -> float:
        """
        Correct temperature for emissivity.
        
        Uses simplified correction: T_true^4 = (T_meas^4 - (1-eps)*T_amb^4) / eps
        
        Args:
            measured_temp_C: Measured temperature
            emissivity: Surface emissivity
        
        Returns:
            Corrected temperature
        """
        if emissivity <= 0 or emissivity > 1:
            return measured_temp_C
        
        t_meas_K = measured_temp_C + 273.15
        t_amb_K = self.ambient_temp_C + 273.15
        
        t_true_K4 = (t_meas_K**4 - (1.0 - emissivity) * t_amb_K**4) / emissivity
        if t_true_K4 <= 0:
            return measured_temp_C
        
        return t_true_K4**0.25 - 273.15
    
    def set_ambient(self, temp_C: float):
        """Set ambient temperature."""
        self.ambient_temp_C = temp_C


class ThermalImaging:
    """
    Unified thermal imaging controller.
    """
    
    def __init__(self):
        self.hotspot = HotspotDetector()
        self.gradient = ThermalGradient()
        self.emissivity = EmissivityCorrector()
        self.converter = TemperatureConverter()
        self.pixels: List[ThermalPixel] = []
    
    def load_pixels(self, pixels: List[ThermalPixel]):
        """Load thermal image."""
        self.pixels = pixels
    
    def thermal_report(self, grid_width: int = 0) -> Dict:
        """
        Generate thermal report.
        
        Args:
            grid_width: Image width (0 = no gradient)
        
        Returns:
            Report dict
        """
        if not self.pixels:
            return {"status": "no_data"}
        
        hotspots = self.hotspot.detect(self.pixels)
        
        report = {
            "num_pixels": len(self.pixels),
            "max_temp_C": self.hotspot.max_temperature(self.pixels),
            "min_temp_C": self.hotspot.min_temperature(self.pixels),
            "avg_temp_C": sum(p.temperature_C for p in self.pixels) / len(self.pixels),
            "hotspots": len(hotspots),
            "uniformity": self.hotspot.thermal_uniformity(self.pixels)
        }
        
        if grid_width > 0:
            report["max_gradient"] = self.gradient.max_gradient(self.pixels, grid_width)
        
        return report
    
    def pass_fail(self, max_temp_C: float = 80.0) -> bool:
        """
        Check if within thermal limits.
        
        Args:
            max_temp_C: Maximum allowed temperature
        
        Returns:
            True if passes
        """
        if not self.pixels:
            return False
        return self.hotspot.max_temperature(self.pixels) <= max_temp_C
