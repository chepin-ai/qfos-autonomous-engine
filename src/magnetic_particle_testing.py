"""
Magnetic Particle Testing Module
Magnetization, particle application, indication detection,
and defect characterization for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Indication:
    """Magnetic particle indication."""
    x_mm: float
    y_mm: float
    length_mm: float
    width_mm: float
    intensity: float
    orientation_deg: float


class Magnetizer:
    """
    Apply magnetic field.
    """
    
    def __init__(self, field_strength_A_m: float = 2000.0):
        """
        Args:
            field_strength_A_m: Field strength
        """
        self.field = field_strength_A_m
    
    def longitudinal_magnetization(self, material_permeability: float,
                                   cross_section_mm2: float) -> float:
        """
        Compute longitudinal magnetization.
        
        Args:
            material_permeability: Relative permeability
            cross_section_mm2: Cross-section
        
        Returns:
            Magnetizing current (A)
        """
        # Simplified: ampere-turns
        if cross_section_mm2 <= 0:
            return 0.0
        return self.field * cross_section_mm2 * 1e-6 / (4.0 * math.pi * 1e-7 * material_permeability)
    
    def circular_magnetization(self, diameter_mm: float,
                              material_permeability: float) -> float:
        """
        Compute circular magnetization current.
        
        Args:
            diameter_mm: Diameter
            material_permeability: Permeability
        
        Returns:
            Current (A)
        """
        if diameter_mm <= 0 or material_permeability <= 0:
            return 0.0
        return self.field * math.pi * diameter_mm * 1e-3 / (4.0 * math.pi * 1e-7 * material_permeability)


class ParticleApplicator:
    """
    Apply magnetic particles.
    """
    
    def __init__(self, particle_size_um: float = 5.0):
        """
        Args:
            particle_size_um: Particle size
        """
        self.size = particle_size_um
    
    def concentration(self, particle_mass_g: float,
                     carrier_volume_L: float) -> float:
        """
        Compute concentration.
        
        Args:
            particle_mass_g: Mass
            carrier_volume_L: Volume
        
        Returns:
            Concentration (g/L)
        """
        if carrier_volume_L <= 0:
            return 0.0
        return particle_mass_g / carrier_volume_L


class IndicationDetector:
    """
    Detect indications from particle patterns.
    """
    
    def __init__(self, min_length_mm: float = 1.0,
                 min_intensity: float = 0.1):
        """
        Args:
            min_length_mm: Minimum length
            min_intensity: Minimum intensity
        """
        self.min_length = min_length_mm
        self.min_intensity = min_intensity
    
    def detect(self, image: List[List[float]],
              pixel_size_mm: float) -> List[Indication]:
        """
        Detect indications.
        
        Args:
            image: Intensity image
            pixel_size_mm: Pixel size
        
        Returns:
            Indications
        """
        indications = []
        
        for i in range(len(image)):
            for j in range(len(image[0])):
                if image[i][j] > self.min_intensity:
                    # Simplified: single-pixel indication
                    indications.append(Indication(
                        x_mm=j * pixel_size_mm,
                        y_mm=i * pixel_size_mm,
                        length_mm=pixel_size_mm,
                        width_mm=pixel_size_mm,
                        intensity=image[i][j],
                        orientation_deg=0.0
                    ))
        
        return indications
    
    def classify(self, indication: Indication) -> str:
        """
        Classify indication.
        
        Args:
            indication: Indication
        
        Returns:
            Classification
        """
        if indication.length_mm < 3.0:
            return "relevant"
        elif indication.length_mm < 10.0:
            return "significant"
        else:
            return "critical"


class DefectCharacterizer:
    """
    Characterize defects from indications.
    """
    
    def __init__(self):
        pass
    
    def depth_estimate(self, indication_length_mm: float,
                      material_thickness_mm: float) -> float:
        """
        Estimate defect depth.
        
        Args:
            indication_length_mm: Indication length
            material_thickness_mm: Thickness
        
        Returns:
            Depth estimate
        """
        # Simplified: assume surface-breaking
        return min(indication_length_mm / 5.0, material_thickness_mm)
    
    def orientation_analysis(self, indications: List[Indication]) -> Dict:
        """
        Analyze orientations.
        
        Args:
            indications: Indications
        
        Returns:
            Analysis
        """
        if not indications:
            return {"dominant": 0.0, "spread": 0.0}
        
        orientations = [ind.orientation_deg for ind in indications]
        avg = sum(orientations) / len(orientations)
        
        # Circular standard deviation
        sin_sum = sum(math.sin(math.radians(o)) for o in orientations)
        cos_sum = sum(math.cos(math.radians(o)) for o in orientations)
        r = math.sqrt(sin_sum**2 + cos_sum**2) / len(orientations)
        spread = math.degrees(math.sqrt(-2.0 * math.log(max(r, 1e-10))))
        
        return {"dominant": avg, "spread": spread}


class MagneticParticleTesting:
    """
    Unified magnetic particle testing controller.
    """
    
    def __init__(self):
        self.magnetizer = Magnetizer()
        self.applicator = ParticleApplicator()
        self.detector = IndicationDetector()
        self.characterizer = DefectCharacterizer()
        self.indications: List[Indication] = []
    
    def inspect_surface(self, image: List[List[float]],
                       pixel_size_mm: float) -> Dict:
        """
        Inspect surface.
        
        Args:
            image: Image
            pixel_size_mm: Pixel size
        
        Returns:
            Results
        """
        self.indications = self.detector.detect(image, pixel_size_mm)
        
        classifications = {}
        for ind in self.indications:
            c = self.detector.classify(ind)
            classifications[c] = classifications.get(c, 0) + 1
        
        orient = self.characterizer.orientation_analysis(self.indications)
        
        return {
            "indications": len(self.indications),
            "classifications": classifications,
            "orientation": orient
        }
    
    def mpt_summary(self) -> Dict:
        """Get summary."""
        return {
            "indications": len(self.indications),
            "field_strength": self.magnetizer.field
        }
