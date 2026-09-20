"""
Infrared Thermography Module
Thermal NDT with emissivity correction, thermal contrast analysis,
lock-in thermography, and defect detection for autonomous inspection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ThermalMode(Enum):
    """Thermography modes."""
    PULSE = "pulse"
    LOCK_IN = "lock_in"
    STEP_HEATING = "step_heating"


@dataclass
class ThermalPixel:
    """Single thermal pixel reading."""
    x_mm: float
    y_mm: float
    temperature_C: float
    emissivity: float = 0.95
    reflectance: float = 0.05


class EmissivityCorrector:
    """
    Emissivity correction for IR measurements.
    """
    
    def __init__(self):
        self.reflected_temp_C = 25.0
    
    def correct_temperature(self, measured_temp_C: float,
                           emissivity: float,
                           reflected_temp_C: Optional[float] = None) -> float:
        """
        Correct measured temperature for emissivity.
        
        Args:
            measured_temp_C: Apparent temperature
            emissivity: Surface emissivity
            reflected_temp_C: Reflected temperature
        
        Returns:
            True temperature
        """
        t_ref = reflected_temp_C if reflected_temp_C is not None else self.reflected_temp_C
        # Stefan-Boltzmann simplified correction
        # T_true^4 = (T_meas^4 - (1-eps)*T_ref^4) / eps
        t_meas_K = measured_temp_C + 273.15
        t_ref_K = t_ref + 273.15
        
        t_true_K4 = (t_meas_K**4 - (1.0 - emissivity) * t_ref_K**4) / emissivity
        t_true_K = max(0.0, t_true_K4 ** 0.25)
        return t_true_K - 273.15
    
    def estimate_emissivity(self, true_temp_C: float,
                           measured_temp_C: float,
                           reflected_temp_C: float = 25.0) -> float:
        """
        Estimate emissivity from temperatures.
        
        Args:
            true_temp_C: True temperature
            measured_temp_C: Measured
            reflected_temp_C: Reflected
        
        Returns:
            Emissivity
        """
        t_true_K = true_temp_C + 273.15
        t_meas_K = measured_temp_C + 273.15
        t_ref_K = reflected_temp_C + 273.15
        
        num = t_meas_K**4 - t_ref_K**4
        den = t_true_K**4 - t_ref_K**4
        
        if abs(den) < 1e-10:
            return 0.95
        
        eps = num / den
        return max(0.1, min(1.0, eps))


class ThermalContrastAnalyzer:
    """
    Thermal contrast analysis for defect detection.
    """
    
    def __init__(self):
        self.background_temp_C = 25.0
    
    def contrast(self, defect_temp_C: float,
                background_temp_C: Optional[float] = None) -> float:
        """
        Compute thermal contrast.
        
        Args:
            defect_temp_C: Defect temperature
            background_temp_C: Background
        
        Returns:
            Contrast (delta T)
        """
        bg = background_temp_C if background_temp_C is not None else self.background_temp_C
        return defect_temp_C - bg
    
    def contrast_ratio(self, defect_temp_C: float,
                      background_temp_C: Optional[float] = None) -> float:
        """
        Compute contrast ratio.
        
        Args:
            defect_temp_C: Defect
            background_temp_C: Background
        
        Returns:
            Ratio
        """
        bg = background_temp_C if background_temp_C is not None else self.background_temp_C
        if abs(bg) < 1e-10:
            return 0.0
        return (defect_temp_C - bg) / bg
    
    def defect_map(self, thermal_image: List[List[float]],
                  threshold_C: float = 2.0) -> List[List[bool]]:
        """
        Generate defect map from thermal image.
        
        Args:
            thermal_image: Temperature map
            threshold_C: Detection threshold
        
        Returns:
            Boolean defect map
        """
        if not thermal_image:
            return []
        
        # Compute background
        flat = [v for row in thermal_image for v in row]
        bg = sum(flat) / len(flat) if flat else 25.0
        
        return [[abs(v - bg) > threshold_C for v in row] for row in thermal_image]


class LockInThermography:
    """
    Lock-in thermography signal processing.
    """
    
    def __init__(self, modulation_frequency_Hz: float = 0.1):
        """
        Args:
            modulation_frequency_Hz: Modulation frequency
        """
        self.freq = modulation_frequency_Hz
        self.period_s = 1.0 / modulation_frequency_Hz
    
    def demodulate(self, signal: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Demodulate lock-in signal.
        
        Args:
            signal: (time_s, amplitude) pairs
        
        Returns:
            (in_phase, quadrature)
        """
        x_sum = 0.0
        y_sum = 0.0
        
        for t, amp in signal:
            x_sum += amp * math.cos(2.0 * math.pi * self.freq * t)
            y_sum += amp * math.sin(2.0 * math.pi * self.freq * t)
        
        n = len(signal)
        if n == 0:
            return (0.0, 0.0)
        
        return (2.0 * x_sum / n, 2.0 * y_sum / n)
    
    def amplitude(self, in_phase: float, quadrature: float) -> float:
        """
        Compute amplitude from quadrature.
        
        Args:
            in_phase: In-phase component
            quadrature: Quadrature component
        
        Returns:
            Amplitude
        """
        return math.sqrt(in_phase**2 + quadrature**2)
    
    def phase(self, in_phase: float, quadrature: float) -> float:
        """
        Compute phase.
        
        Args:
            in_phase: In-phase
            quadrature: Quadrature
        
        Returns:
            Phase in radians
        """
        return math.atan2(quadrature, in_phase)
    
    def thermal_diffusion_length_mm(self,
                                   thermal_diffusivity_mm2_s: float = 10.0) -> float:
        """
        Compute thermal diffusion length.
        
        Args:
            thermal_diffusivity_mm2_s: Thermal diffusivity
        
        Returns:
            Diffusion length in mm
        """
        return math.sqrt(thermal_diffusivity_mm2_s / (math.pi * self.freq))


class InfraredThermography:
    """
    Unified infrared thermography controller.
    """
    
    def __init__(self):
        self.corrector = EmissivityCorrector()
        self.contrast = ThermalContrastAnalyzer()
        self.lockin = LockInThermography()
        self.thermal_images: List[List[List[float]]] = []
        self.defects: List[Dict] = []
    
    def capture(self, thermal_image_C: List[List[float]],
               emissivity_map: Optional[List[List[float]]] = None):
        """
        Capture thermal image.
        
        Args:
            thermal_image_C: Raw thermal image
            emissivity_map: Emissivity per pixel
        """
        if emissivity_map:
            corrected = []
            for y, row in enumerate(thermal_image_C):
                corrected_row = []
                for x, temp in enumerate(row):
                    eps = emissivity_map[y][x] if y < len(emissivity_map) and x < len(emissivity_map[y]) else 0.95
                    corrected_row.append(self.corrector.correct_temperature(temp, eps))
                corrected.append(corrected_row)
            self.thermal_images.append(corrected)
        else:
            self.thermal_images.append(thermal_image_C)
    
    def detect_defects(self, threshold_C: float = 2.0) -> List[Dict]:
        """
        Detect defects in latest image.
        
        Args:
            threshold_C: Threshold
        
        Returns:
            Defect list
        """
        if not self.thermal_images:
            return []
        
        latest = self.thermal_images[-1]
        defect_map = self.contrast.defect_map(latest, threshold_C)
        
        h = len(defect_map)
        w = len(defect_map[0]) if h > 0 else 0
        
        for y in range(h):
            for x in range(w):
                if defect_map[y][x]:
                    self.defects.append({
                        "x": x,
                        "y": y,
                        "temperature_C": latest[y][x],
                        "contrast_C": self.contrast.contrast(latest[y][x])
                    })
        
        return self.defects
    
    def thermography_summary(self) -> Dict:
        """Get summary."""
        return {
            "images": len(self.thermal_images),
            "defects": len(self.defects),
            "lockin_freq_Hz": self.lockin.freq,
            "diffusion_length_mm": self.lockin.thermal_diffusion_length_mm()
        }
