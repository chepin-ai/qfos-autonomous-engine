"""
X-Ray Inspection Module
Radiographic imaging, absorption calculation, density estimation,
contrast analysis, and defect detection for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DefectTypeXRay(Enum):
    """X-ray detectable defect types."""
    NONE = "none"
    POROSITY = "porosity"
    CRACK = "crack"
    INCLUSION = "inclusion"
    VOID = "void"
    THINNING = "thinning"


@dataclass
class XRayPixel:
    """A single X-ray image pixel."""
    x: int
    y: int
    intensity: float  # Normalized [0, 1]
    thickness_mm: float = 0.0


class AbsorptionCalculator:
    """
    Compute X-ray absorption using Beer-Lambert law.
    """
    
    def __init__(self):
        # Mass attenuation coefficients (cm^2/g) at typical energy
        self.attenuation: Dict[str, float] = {
            "steel": 0.5,
            "aluminum": 0.15,
            "titanium": 0.3,
            "copper": 1.0,
            "lead": 10.0,
            "water": 0.1,
            "air": 0.001
        }
        # Densities (g/cm^3)
        self.densities: Dict[str, float] = {
            "steel": 7.85,
            "aluminum": 2.70,
            "titanium": 4.51,
            "copper": 8.96,
            "lead": 11.34,
            "water": 1.0,
            "air": 0.0012
        }
    
    def set_material(self, name: str, attenuation: float,
                    density: float):
        """
        Register material properties.
        
        Args:
            name: Material name
            attenuation: Mass attenuation (cm^2/g)
            density: Density (g/cm^3)
        """
        self.attenuation[name] = attenuation
        self.densities[name] = density
    
    def transmission(self, material: str,
                    thickness_mm: float,
                    energy_keV: float = 100.0) -> float:
        """
        Compute X-ray transmission fraction.
        
        Args:
            material: Material name
            thickness_mm: Thickness in mm
            energy_keV: X-ray energy (scaling factor)
        
        Returns:
            Transmission [0, 1]
        """
        mu = self.attenuation.get(material, 0.5)
        rho = self.densities.get(material, 7.85)
        # Scale attenuation with energy (higher energy = less attenuation)
        energy_scale = 100.0 / max(energy_keV, 1.0)
        mu_eff = mu * rho * energy_scale
        # Beer-Lambert: I/I0 = exp(-mu * x)
        x_cm = thickness_mm / 10.0
        return math.exp(-mu_eff * x_cm)
    
    def absorbance(self, material: str,
                  thickness_mm: float,
                  energy_keV: float = 100.0) -> float:
        """
        Compute absorbance (optical density).
        
        Args:
            material: Material name
            thickness_mm: Thickness
            energy_keV: X-ray energy
        
        Returns:
            Absorbance
        """
        T = self.transmission(material, thickness_mm, energy_keV)
        if T <= 0:
            return float('inf')
        return -math.log10(T)


class DensityEstimator:
    """
    Estimate material density from radiographic data.
    """
    
    def __init__(self):
        self.calibration: Dict[float, float] = {}
    
    def calibrate(self, known_density: float,
                 measured_intensity: float):
        """
        Add calibration point.
        
        Args:
            known_density: Known density
            measured_intensity: Measured intensity
        """
        self.calibration[known_density] = measured_intensity
    
    def estimate(self, intensity: float) -> float:
        """
        Estimate density from intensity.
        
        Args:
            intensity: Measured intensity
        
        Returns:
            Estimated density
        """
        if not self.calibration:
            # Default: assume steel-like
            return 7.85 * intensity
        
        # Linear interpolation between calibration points
        points = sorted(self.calibration.items())
        if intensity >= points[0][1]:
            return points[0][0]
        if intensity <= points[-1][1]:
            return points[-1][0]
        
        for i in range(len(points) - 1):
            d1, i1 = points[i]
            d2, i2 = points[i + 1]
            if i2 <= intensity <= i1:
                frac = (intensity - i2) / (i1 - i2)
                return d2 + frac * (d1 - d2)
        
        return points[-1][0]


class ContrastAnalyzer:
    """
    Analyze image contrast for defect visibility.
    """
    
    def __init__(self):
        pass
    
    def contrast(self, I_obj: float, I_bg: float) -> float:
        """
        Compute Michelson contrast.
        
        Args:
            I_obj: Object intensity
            I_bg: Background intensity
        
        Returns:
            Contrast [-1, 1]
        """
        if I_obj + I_bg == 0:
            return 0.0
        return (I_obj - I_bg) / (I_obj + I_bg)
    
    def signal_to_noise(self, signal: float,
                       noise: float) -> float:
        """
        Compute SNR.
        
        Args:
            signal: Signal amplitude
            noise: Noise standard deviation
        
        Returns:
            SNR
        """
        if noise <= 0:
            return float('inf')
        return signal / noise
    
    def contrast_to_noise(self, contrast: float,
                         noise: float) -> float:
        """
        Compute CNR.
        
        Args:
            contrast: Contrast value
            noise: Noise level
        
        Returns:
            CNR
        """
        if noise <= 0:
            return float('inf')
        return contrast / noise
    
    def detectability(self, thickness_difference_mm: float,
                     material: str,
                     energy_keV: float = 100.0) -> float:
        """
        Estimate defect detectability.
        
        Args:
            thickness_difference_mm: Thickness difference
            material: Material
            energy_keV: Energy
        
        Returns:
            Detectability score
        """
        calc = AbsorptionCalculator()
        I_bg = calc.transmission(material, 10.0, energy_keV)
        I_obj = calc.transmission(material, 10.0 + thickness_difference_mm, energy_keV)
        return abs(self.contrast(I_obj, I_bg))


class XRayDefectDetector:
    """
    Detect defects in X-ray images.
    """
    
    def __init__(self, contrast_threshold: float = 0.05):
        """
        Args:
            contrast_threshold: Minimum contrast for detection
        """
        self.threshold = contrast_threshold
    
    def detect(self, pixels: List[XRayPixel]) -> List[Dict]:
        """
        Detect defects from pixel data.
        
        Args:
            pixels: X-ray image pixels
        
        Returns:
            Defect list
        """
        if not pixels:
            return []
        
        avg_intensity = sum(p.intensity for p in pixels) / len(pixels)
        defects = []
        
        for p in pixels:
            contrast = abs(p.intensity - avg_intensity) / max(avg_intensity, 1e-6)
            if contrast > self.threshold:
                defect_type = DefectTypeXRay.VOID
                if p.intensity < avg_intensity:
                    defect_type = DefectTypeXRay.INCLUSION
                
                defects.append({
                    "x": p.x,
                    "y": p.y,
                    "intensity": p.intensity,
                    "contrast": contrast,
                    "type": defect_type.value
                })
        
        return defects
    
    def porosity_fraction(self, pixels: List[XRayPixel]) -> float:
        """
        Estimate porosity fraction.
        
        Args:
            pixels: Image pixels
        
        Returns:
            Porosity fraction [0, 1]
        """
        if not pixels:
            return 0.0
        
        defects = self.detect(pixels)
        return len(defects) / len(pixels)


class XRayInspection:
    """
    Unified X-ray inspection controller.
    """
    
    def __init__(self):
        self.absorption = AbsorptionCalculator()
        self.density = DensityEstimator()
        self.contrast = ContrastAnalyzer()
        self.defect = XRayDefectDetector()
        self.inspection_history: List[Dict] = []
    
    def inspect(self, pixels: List[XRayPixel],
               material: str = "steel") -> Dict:
        """
        Run X-ray inspection.
        
        Args:
            pixels: Image pixels
            material: Material name
        
        Returns:
            Inspection report
        """
        defects = self.defect.detect(pixels)
        porosity = self.defect.porosity_fraction(pixels)
        
        avg_intensity = sum(p.intensity for p in pixels) / len(pixels) if pixels else 0
        est_density = self.density.estimate(avg_intensity)
        
        report = {
            "material": material,
            "num_pixels": len(pixels),
            "avg_intensity": avg_intensity,
            "estimated_density": est_density,
            "defects_found": len(defects),
            "porosity_fraction": porosity,
            "pass": porosity < 0.05 and len(defects) < len(pixels) * 0.01
        }
        self.inspection_history.append(report)
        return report
    
    def thickness_from_transmission(self, transmission: float,
                                   material: str,
                                   energy_keV: float = 100.0) -> float:
        """
        Estimate thickness from transmission.
        
        Args:
            transmission: Measured transmission
            material: Material
            energy_keV: Energy
        
        Returns:
            Estimated thickness in mm
        """
        mu = self.absorption.attenuation.get(material, 0.5)
        rho = self.absorption.densities.get(material, 7.85)
        energy_scale = 100.0 / max(energy_keV, 1.0)
        mu_eff = mu * rho * energy_scale
        
        if transmission <= 0 or mu_eff <= 0:
            return 0.0
        
        return -10.0 * math.log(transmission) / mu_eff
    
    def inspection_summary(self) -> Dict:
        """Get inspection summary."""
        if not self.inspection_history:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.inspection_history),
            "pass_count": sum(1 for r in self.inspection_history if r["pass"]),
            "avg_porosity": sum(r["porosity_fraction"] for r in self.inspection_history) / len(self.inspection_history)
        }
