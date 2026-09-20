"""
Thermal Imaging Module
Infrared thermography, thermal pattern analysis, hot spot detection,
temperature gradient mapping, and emissivity correction for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ThermalPixel:
    """Thermal image pixel."""
    x: int
    y: int
    temp_C: float


class InfraredCamera:
    """
    Infrared camera simulation.
    """
    
    def __init__(self, resolution: Tuple[int, int] = (320, 240),
                 spectral_range_um: Tuple[float, float] = (7.5, 14.0),
                 noise_equivalent_deltaT_mK: float = 50.0):
        """
        Args:
            resolution: Image resolution
            spectral_range_um: Spectral range
            noise_equivalent_deltaT_mK: NETD
        """
        self.resolution = resolution
        self.spectral_range = spectral_range_um
        self.NETD = noise_equivalent_deltaT_mK / 1000.0
    
    def capture(self, ambient_C: float = 20.0,
               hot_spots: Optional[List[Tuple[int, int, float]]] = None
              ) -> List[List[float]]:
        """
        Capture thermal image.
        
        Args:
            ambient_C: Ambient temperature
            hot_spots: List of (x, y, temp_C)
        
        Returns:
            2D temperature array
        """
        import random
        w, h = self.resolution
        image = []
        
        for y in range(h):
            row = []
            for x in range(w):
                temp = ambient_C + random.gauss(0, self.NETD)
                row.append(temp)
            image.append(row)
        
        # Add hot spots
        if hot_spots:
            for (hx, hy, htemp) in hot_spots:
                if 0 <= hx < w and 0 <= hy < h:
                    # Gaussian spread
                    for dy in range(-5, 6):
                        for dx in range(-5, 6):
                            nx, ny = hx + dx, hy + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                dist = math.sqrt(dx**2 + dy**2)
                                factor = math.exp(-dist**2 / 8.0)
                                image[ny][nx] += (htemp - ambient_C) * factor
        
        return image
    
    def min_max_temp(self, image: List[List[float]]) -> Tuple[float, float]:
        """
        Find min/max temperature.
        
        Args:
            image: Thermal image
        
        Returns:
            (min, max)
        """
        all_temps = [t for row in image for t in row]
        return (min(all_temps), max(all_temps))


class HotSpotDetector:
    """
    Detect hot spots in thermal images.
    """
    
    def __init__(self, threshold_delta_K: float = 5.0):
        """
        Args:
            threshold_delta_K: Threshold above ambient
        """
        self.threshold = threshold_delta_K
    
    def detect(self, image: List[List[float]],
              ambient_C: float = 20.0) -> List[Dict]:
        """
        Detect hot spots.
        
        Args:
            image: Thermal image
            ambient_C: Ambient temperature
        
        Returns:
            List of hot spot dicts
        """
        hotspots = []
        h = len(image)
        if h == 0:
            return hotspots
        w = len(image[0])
        
        for y in range(h):
            for x in range(w):
                if image[y][x] - ambient_C >= self.threshold:
                    # Check if local maximum
                    is_max = True
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < w and 0 <= ny < h and
                                image[ny][nx] > image[y][x]):
                                is_max = False
                                break
                        if not is_max:
                            break
                    
                    if is_max:
                        hotspots.append({
                            "x": x, "y": y,
                            "temp_C": image[y][x],
                            "delta_K": image[y][x] - ambient_C
                        })
        
        return hotspots


class TemperatureGradientMapper:
    """
    Map temperature gradients.
    """
    
    def __init__(self):
        pass
    
    def gradient_magnitude(self, image: List[List[float]]) -> List[List[float]]:
        """
        Compute gradient magnitude.
        
        Args:
            image: Thermal image
        
        Returns:
            Gradient magnitude image
        """
        h = len(image)
        if h == 0:
            return []
        w = len(image[0])
        
        grad = []
        for y in range(h):
            row = []
            for x in range(w):
                # Central differences
                dx = (image[y][min(x+1, w-1)] - image[y][max(x-1, 0)]) / 2.0
                dy = (image[min(y+1, h-1)][x] - image[max(y-1, 0)][x]) / 2.0
                row.append(math.sqrt(dx**2 + dy**2))
            grad.append(row)
        
        return grad
    
    def max_gradient(self, image: List[List[float]]) -> float:
        """
        Find maximum gradient.
        
        Args:
            image: Thermal image
        
        Returns:
            Maximum gradient
        """
        grad = self.gradient_magnitude(image)
        all_grads = [g for row in grad for g in row]
        return max(all_grads) if all_grads else 0.0


class EmissivityCorrector:
    """
    Correct for emissivity.
    """
    
    def __init__(self):
        self.stefan_boltzmann = 5.670374e-8  # W/m2/K4
    
    def correct_temperature(self, apparent_temp_C: float,
                           emissivity: float,
                           reflected_temp_C: float = 20.0) -> float:
        """
        Correct temperature for emissivity.
        
        Args:
            apparent_temp_C: Apparent temperature
            emissivity: Emissivity (0-1)
            reflected_temp_C: Reflected temperature
        
        Returns:
            Corrected temperature in C
        """
        if emissivity <= 0 or emissivity > 1.0:
            return apparent_temp_C
        
        Ta = apparent_temp_C + 273.15
        Tr = reflected_temp_C + 273.15
        
        # True radiance = (apparent - (1-e)*reflected) / e
        true_T4 = (Ta**4 - (1.0 - emissivity) * Tr**4) / emissivity
        
        if true_T4 <= 0:
            return apparent_temp_C
        
        return true_T4 ** 0.25 - 273.15
    
    def estimate_emissivity(self, true_temp_C: float,
                           apparent_temp_C: float,
                           reflected_temp_C: float = 20.0) -> float:
        """
        Estimate emissivity.
        
        Args:
            true_temp_C: True temperature
            apparent_temp_C: Apparent temperature
            reflected_temp_C: Reflected temperature
        
        Returns:
            Emissivity
        """
        Tt = true_temp_C + 273.15
        Ta = apparent_temp_C + 273.15
        Tr = reflected_temp_C + 273.15
        
        denom = Tt**4 - Tr**4
        if abs(denom) < 1e-10:
            return 1.0
        
        e = (Ta**4 - Tr**4) / denom
        return max(0.0, min(1.0, e))


class ThermalPatternAnalyzer:
    """
    Analyze thermal patterns.
    """
    
    def __init__(self):
        pass
    
    def thermal_uniformity(self, image: List[List[float]]) -> float:
        """
        Compute thermal uniformity.
        
        Args:
            image: Thermal image
        
        Returns:
            Uniformity index
        """
        all_temps = [t for row in image for t in row]
        if not all_temps:
            return 0.0
        
        mean = sum(all_temps) / len(all_temps)
        variance = sum((t - mean)**2 for t in all_temps) / len(all_temps)
        std = math.sqrt(variance)
        
        # Coefficient of variation
        if mean != 0:
            return std / abs(mean)
        return 0.0
    
    def thermal_histogram(self, image: List[List[float]],
                         bins: int = 10) -> Dict:
        """
        Compute thermal histogram.
        
        Args:
            image: Thermal image
            bins: Number of bins
        
        Returns:
            Histogram dict
        """
        all_temps = [t for row in image for t in row]
        if not all_temps:
            return {}
        
        t_min = min(all_temps)
        t_max = max(all_temps)
        bin_width = (t_max - t_min) / bins if t_max > t_min else 1.0
        
        counts = [0] * bins
        for t in all_temps:
            idx = min(int((t - t_min) / bin_width), bins - 1)
            counts[idx] += 1
        
        return {
            "min_C": t_min,
            "max_C": t_max,
            "bin_width": bin_width,
            "counts": counts
        }


class ThermalImaging:
    """
    Unified thermal imaging controller.
    """
    
    def __init__(self):
        self.camera = InfraredCamera()
        self.detector = HotSpotDetector()
        self.gradient = TemperatureGradientMapper()
        self.emissivity = EmissivityCorrector()
        self.pattern = ThermalPatternAnalyzer()
        self.image: List[List[float]] = []
    
    def inspect(self, ambient_C: float = 20.0,
               hot_spots: Optional[List[Tuple[int, int, float]]] = None):
        """
        Perform thermal inspection.
        
        Args:
            ambient_C: Ambient temperature
            hot_spots: Known hot spots
        """
        self.image = self.camera.capture(ambient_C, hot_spots)
    
    def analyze(self) -> Dict:
        """
        Analyze thermal image.
        
        Returns:
            Results
        """
        if not self.image:
            return {}
        
        t_min, t_max = self.camera.min_max_temp(self.image)
        hotspots = self.detector.detect(self.image, 20.0)
        max_grad = self.gradient.max_gradient(self.image)
        uniformity = self.pattern.thermal_uniformity(self.image)
        hist = self.pattern.thermal_histogram(self.image, 5)
        
        return {
            "min_temp_C": t_min,
            "max_temp_C": t_max,
            "hot_spots": len(hotspots),
            "max_gradient_K_px": max_grad,
            "uniformity": uniformity,
            "histogram": hist
        }
    
    def ti_summary(self) -> Dict:
        """Get summary."""
        return {
            "resolution": self.camera.resolution,
            "image_ready": len(self.image) > 0
        }
