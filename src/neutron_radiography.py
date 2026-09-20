"""
Neutron Radiography Module
Thermal/fast neutron imaging, attenuation analysis, contrast computation,
and defect detection for autonomous NDT of dense materials.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class NeutronType(Enum):
    """Neutron energy classification."""
    THERMAL = "thermal"
    FAST = "fast"
    COLD = "cold"


@dataclass
class NeutronImage:
    """Neutron radiography image."""
    pixel_size_mm: float
    exposure_s: float
    neutron_flux_n_cm2_s: float
    data: List[List[float]]


class AttenuationCalculator:
    """
    Neutron attenuation calculations.
    """
    
    def __init__(self):
        # Macroscopic cross sections (cm^-1) for common materials
        self.cross_sections: Dict[str, float] = {
            "water": 3.45,
            "aluminum": 0.10,
            "steel": 1.19,
            "concrete": 0.15,
            "polyethylene": 3.38,
            "boron": 100.0
        }
    
    def attenuation(self, material: str, thickness_cm: float) -> float:
        """
        Compute neutron attenuation.
        
        Args:
            material: Material name
            thickness_cm: Thickness
        
        Returns:
            Transmission fraction
        """
        sigma = self.cross_sections.get(material.lower(), 0.5)
        return math.exp(-sigma * thickness_cm)
    
    def thickness_from_attenuation(self, material: str,
                                  transmission: float) -> float:
        """
        Estimate thickness from attenuation.
        
        Args:
            material: Material
            transmission: Transmission
        
        Returns:
            Thickness in cm
        """
        sigma = self.cross_sections.get(material.lower(), 0.5)
        if sigma <= 0 or transmission <= 0:
            return 0.0
        return -math.log(transmission) / sigma
    
    def add_material(self, name: str, cross_section_cm: float):
        """
        Add material cross section.
        
        Args:
            name: Material name
            cross_section_cm: Macroscopic cross section
        """
        self.cross_sections[name.lower()] = cross_section_cm


class NeutronContrastAnalyzer:
    """
    Contrast analysis for neutron images.
    """
    
    def __init__(self):
        self.reference_flux = 1000.0
    
    def contrast(self, object_flux: float,
                background_flux: Optional[float] = None) -> float:
        """
        Compute image contrast.
        
        Args:
            object_flux: Object flux
            background_flux: Background
        
        Returns:
            Contrast
        """
        bg = background_flux if background_flux is not None else self.reference_flux
        if bg <= 0:
            return 0.0
        return (bg - object_flux) / bg
    
    def signal_to_noise(self, signal: float, noise: float) -> float:
        """
        Compute SNR.
        
        Args:
            signal: Signal
            noise: Noise
        
        Returns:
            SNR
        """
        if noise <= 0:
            return float('inf')
        return signal / noise
    
    def defect_map(self, image: NeutronImage,
                  threshold: float = 0.1) -> List[List[bool]]:
        """
        Detect defects from neutron image.
        
        Args:
            image: Neutron image
            threshold: Threshold
        
        Returns:
            Defect map
        """
        if not image.data:
            return []
        
        # Compute background
        flat = [v for row in image.data for v in row]
        bg = sum(flat) / len(flat) if flat else 1.0
        
        return [[abs((bg - v) / bg) > threshold for v in row] for row in image.data]


class NeutronScatterCorrector:
    """
    Neutron scatter correction.
    """
    
    def __init__(self):
        self.scatter_fraction = 0.15
    
    def correct(self, image: NeutronImage) -> NeutronImage:
        """
        Apply scatter correction.
        
        Args:
            image: Raw image
        
        Returns:
            Corrected image
        """
        corrected = []
        for row in image.data:
            corrected_row = [v * (1.0 - self.scatter_fraction) for v in row]
            corrected.append(corrected_row)
        
        return NeutronImage(
            pixel_size_mm=image.pixel_size_mm,
            exposure_s=image.exposure_s,
            neutron_flux_n_cm2_s=image.neutron_flux_n_cm2_s,
            data=corrected
        )
    
    def dark_current_subtract(self, image: NeutronImage,
                             dark_image: NeutronImage) -> NeutronImage:
        """
        Subtract dark current.
        
        Args:
            image: Image
            dark_image: Dark field
        
        Returns:
            Corrected image
        """
        corrected = []
        for i, row in enumerate(image.data):
            dark_row = dark_image.data[i] if i < len(dark_image.data) else [0.0] * len(row)
            corrected_row = [max(0.0, v - d) for v, d in zip(row, dark_row)]
            corrected.append(corrected_row)
        
        return NeutronImage(
            pixel_size_mm=image.pixel_size_mm,
            exposure_s=image.exposure_s,
            neutron_flux_n_cm2_s=image.neutron_flux_n_cm2_s,
            data=corrected
        )


class NeutronRadiography:
    """
    Unified neutron radiography controller.
    """
    
    def __init__(self):
        self.attenuation = AttenuationCalculator()
        self.contrast = NeutronContrastAnalyzer()
        self.scatter = NeutronScatterCorrector()
        self.images: List[NeutronImage] = []
        self.defects: List[Dict] = []
    
    def capture(self, image_data: List[List[float]],
               pixel_size_mm: float = 0.1,
               exposure_s: float = 60.0,
               flux: float = 1e6):
        """
        Capture neutron image.
        
        Args:
            image_data: Raw data
            pixel_size_mm: Pixel size
            exposure_s: Exposure
            flux: Neutron flux
        """
        img = NeutronImage(pixel_size_mm, exposure_s, flux, image_data)
        self.images.append(img)
    
    def detect_defects(self, threshold: float = 0.1) -> List[Dict]:
        """
        Detect defects.
        
        Args:
            threshold: Threshold
        
        Returns:
            Defect list
        """
        if not self.images:
            return []
        
        latest = self.images[-1]
        corrected = self.scatter.correct(latest)
        defect_map = self.contrast.defect_map(corrected, threshold)
        
        h = len(defect_map)
        w = len(defect_map[0]) if h > 0 else 0
        
        for y in range(h):
            for x in range(w):
                if defect_map[y][x]:
                    self.defects.append({
                        "x": x,
                        "y": y,
                        "flux": corrected.data[y][x],
                        "contrast": self.contrast.contrast(corrected.data[y][x])
                    })
        
        return self.defects
    
    def estimate_thickness(self, material: str,
                          region: Tuple[int, int, int, int]) -> float:
        """
        Estimate thickness in region.
        
        Args:
            material: Material
            region: (x, y, w, h)
        
        Returns:
            Average thickness in cm
        """
        if not self.images:
            return 0.0
        
        latest = self.images[-1]
        x0, y0, w, h = region
        
        transmissions = []
        for y in range(y0, min(y0 + h, len(latest.data))):
            for x in range(x0, min(x0 + w, len(latest.data[y]))):
                # Normalize by reference
                t = latest.data[y][x] / max(latest.neutron_flux_n_cm2_s, 1.0)
                transmissions.append(t)
        
        avg_t = sum(transmissions) / len(transmissions) if transmissions else 1.0
        return self.attenuation.thickness_from_attenuation(material, avg_t)
    
    def radiography_summary(self) -> Dict:
        """Get summary."""
        return {
            "images": len(self.images),
            "defects": len(self.defects),
            "materials": list(self.attenuation.cross_sections.keys())
        }
