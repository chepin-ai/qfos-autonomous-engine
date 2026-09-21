"""
Microstructure Characterization Module
Grain size, phase fraction, texture,
and stereology for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GrainData:
    """Individual grain measurements."""
    area_um2: float
    perimeter_um: float
    major_axis_um: float
    minor_axis_um: float


class GrainSizeAnalysis:
    """
    Grain size measurement and analysis.
    """
    
    def __init__(self):
        pass
    
    def equivalent_diameter(self, area_um2: float) -> float:
        """
        Compute equivalent circular diameter.
        
        Args:
            area_um2: Grain area
        
        Returns:
            Diameter (um)
        """
        if area_um2 <= 0:
            return 0.0
        return 2.0 * math.sqrt(area_um2 / math.pi)
    
    def aspect_ratio(self, major_axis_um: float,
                    minor_axis_um: float) -> float:
        """
        Compute grain aspect ratio.
        
        Args:
            major_axis_um: Major axis
            minor_axis_um: Minor axis
        
        Returns:
            Aspect ratio
        """
        if minor_axis_um <= 0:
            return 0.0
        return major_axis_um / minor_axis_um
    
    def astm_grain_size(self, num_grains_per_mm2: float) -> float:
        """
        Compute ASTM grain size number.
        
        Args:
            num_grains_per_mm2: Grain count per mm^2
        
        Returns:
            ASTM G number
        """
        if num_grains_per_mm2 <= 0:
            return 0.0
        return -2.954 + 3.3219 * math.log10(num_grains_per_mm2)
    
    def mean_grain_size(self, grains: List[GrainData]) -> float:
        """
        Compute mean grain diameter.
        
        Args:
            grains: Grain measurements
        
        Returns:
            Mean diameter (um)
        """
        if not grains:
            return 0.0
        diameters = [self.equivalent_diameter(g.area_um2) for g in grains]
        return sum(diameters) / len(diameters)


class PhaseFraction:
    """
    Phase fraction analysis.
    """
    
    def __init__(self):
        pass
    
    def area_fraction(self, phase_area_mm2: float,
                     total_area_mm2: float) -> float:
        """
        Compute area fraction.
        
        Args:
            phase_area_mm2: Phase area
            total_area_mm2: Total area
        
        Returns:
            Fraction
        """
        if total_area_mm2 <= 0:
            return 0.0
        return phase_area_mm2 / total_area_mm2
    
    def volume_fraction_from_area(self, area_fraction: float) -> float:
        """
        Convert area fraction to volume fraction (stereology).
        
        Args:
            area_fraction: Area fraction
        
        Returns:
            Volume fraction
        """
        return area_fraction
    
    def line_fraction(self, intercept_length_mm: float,
                     total_line_length_mm: float) -> float:
        """
        Compute lineal fraction.
        
        Args:
            intercept_length_mm: Phase intercept
            total_line_length_mm: Total line length
        
        Returns:
            Fraction
        """
        if total_line_length_mm <= 0:
            return 0.0
        return intercept_length_mm / total_line_length_mm


class TextureAnalysis:
    """
    Crystallographic texture analysis.
    """
    
    def __init__(self):
        pass
    
    def orientation_density(self, num_grains_with_orientation: int,
                           total_grains: int) -> float:
        """
        Compute orientation density.
        
        Args:
            num_grains_with_orientation: Grains with target orientation
            total_grains: Total grains
        
        Returns:
            Density (multiple of random)
        """
        if total_grains <= 0:
            return 0.0
        random_fraction = 1.0 / total_grains if total_grains > 0 else 0.0
        measured_fraction = num_grains_with_orientation / total_grains
        if random_fraction <= 0:
            return 0.0
        return measured_fraction / random_fraction
    
    def texture_index(self, orientation_distribution: List[float]) -> float:
        """
        Compute texture index (simplified).
        
        Args:
            orientation_distribution: ODF values
        
        Returns:
            Texture index
        """
        if not orientation_distribution:
            return 0.0
        return sum(f**2 for f in orientation_distribution) / len(orientation_distribution)


class Stereology:
    """
    Stereological relationships.
    """
    
    def __init__(self):
        pass
    
    def mean_intercept_length(self, line_length_mm: float,
                             num_intercepts: int) -> float:
        """
        Compute mean linear intercept.
        
        Args:
            line_length_mm: Total line length
            num_intercepts: Number of intercepts
        
        Returns:
            Mean intercept (mm)
        """
        if num_intercepts <= 0:
            return 0.0
        return line_length_mm / num_intercepts
    
    def grain_size_from_intercept(self, mean_intercept_length_um: float) -> float:
        """
        Estimate grain size from mean intercept.
        
        Args:
            mean_intercept_length_um: Mean intercept
        
        Returns:
            Grain size (um)
        """
        return mean_intercept_length_um


class MicrostructureCharacterization:
    """
    Unified microstructure characterization controller.
    """
    
    def __init__(self):
        self.grain = GrainSizeAnalysis()
        self.phase = PhaseFraction()
        self.texture = TextureAnalysis()
        self.stereology = Stereology()
    
    def microstructure_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["grain_size", "phase_fraction", "texture", "stereology"],
            "outputs": ["diameter", "aspect_ratio", "astm_number"]
        }
