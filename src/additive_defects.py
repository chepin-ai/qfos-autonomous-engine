"""
Additive Manufacturing Defects Module
Porosity detection, crack detection,
layer misalignment, and geometric deviation for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DefectRegion:
    """Defect region properties."""
    x_mm: float
    y_mm: float
    z_mm: float
    size_mm: float
    severity: str


class PorosityDetection:
    """
    Detect porosity in additively manufactured parts.
    """
    
    def __init__(self):
        pass
    
    def porosity_fraction(self, void_volume_mm3: float,
                         total_volume_mm3: float) -> float:
        """
        Compute porosity fraction.
        
        Args:
            void_volume_mm3: Void volume
            total_volume_mm3: Total volume
        
        Returns:
            Porosity fraction
        """
        if total_volume_mm3 <= 0:
            return 0.0
        return void_volume_mm3 / total_volume_mm3
    
    def pore_equivalent_diameter(self, pore_volume_mm3: float) -> float:
        """
        Compute equivalent spherical diameter.
        
        Args:
            pore_volume_mm3: Pore volume
        
        Returns:
            Diameter (mm)
        """
        if pore_volume_mm3 <= 0:
            return 0.0
        return 2.0 * (3.0 * pore_volume_mm3 / (4.0 * math.pi)) ** (1.0 / 3.0)
    
    def critical_porosity_threshold(self, material_yield_MPa: float = 200.0) -> float:
        """
        Compute critical porosity threshold.
        
        Args:
            material_yield_MPa: Material yield strength
        
        Returns:
            Critical porosity fraction
        """
        # Simplified: higher strength allows lower porosity
        return max(0.0, 0.05 - 0.0001 * material_yield_MPa)


class CrackDetection:
    """
    Detect cracks in additively manufactured parts.
    """
    
    def __init__(self):
        pass
    
    def crack_severity(self, crack_length_mm: float,
                      crack_width_mm: float) -> str:
        """
        Classify crack severity.
        
        Args:
            crack_length_mm: Crack length
            crack_width_mm: Crack width
        
        Returns:
            Severity level
        """
        area = crack_length_mm * crack_width_mm
        if area < 0.1:
            return "minor"
        elif area < 1.0:
            return "moderate"
        else:
            return "critical"
    
    def stress_intensity_factor(self, stress_MPa: float,
                               crack_length_mm: float,
                               geometry_factor: float = 1.12) -> float:
        """
        Compute stress intensity factor K_I.
        
        Args:
            stress_MPa: Applied stress
            crack_length_mm: Crack length
            geometry_factor: Geometry correction
        
        Returns:
            K_I (MPa sqrt(m))
        """
        a_m = crack_length_mm * 1e-3
        return geometry_factor * stress_MPa * math.sqrt(math.pi * a_m)


class LayerMisalignment:
    """
    Layer misalignment analysis.
    """
    
    def __init__(self):
        pass
    
    def misalignment_vector(self, target_position: Tuple[float, float],
                           actual_position: Tuple[float, float]) -> Tuple[float, float]:
        """
        Compute misalignment vector.
        
        Args:
            target_position: Target
            actual_position: Actual
        
        Returns:
            Misalignment (mm)
        """
        return (actual_position[0] - target_position[0],
                actual_position[1] - target_position[1])
    
    def cumulative_misalignment(self, layer_offsets: List[Tuple[float, float]]) -> float:
        """
        Compute cumulative misalignment.
        
        Args:
            layer_offsets: Per-layer offsets
        
        Returns:
            Cumulative offset (mm)
        """
        if not layer_offsets:
            return 0.0
        total_x = sum(o[0] for o in layer_offsets)
        total_y = sum(o[1] for o in layer_offsets)
        return math.sqrt(total_x**2 + total_y**2)


class GeometricDeviation:
    """
    Geometric deviation from design.
    """
    
    def __init__(self):
        pass
    
    def dimensional_deviation(self, measured_mm: float,
                             nominal_mm: float) -> float:
        """
        Compute dimensional deviation.
        
        Args:
            measured_mm: Measured dimension
            nominal_mm: Nominal dimension
        
        Returns:
            Deviation (mm)
        """
        return measured_mm - nominal_mm
    
    def surface_roughness_deviation(self, measured_Ra_um: float,
                                   target_Ra_um: float) -> float:
        """
        Compute surface roughness deviation.
        
        Args:
            measured_Ra_um: Measured Ra
            target_Ra_um: Target Ra
        
        Returns:
            Deviation (um)
        """
        return measured_Ra_um - target_Ra_um
    
    def is_within_tolerance(self, deviation_mm: float,
                           tolerance_mm: float = 0.1) -> bool:
        """
        Check if within tolerance.
        
        Args:
            deviation_mm: Deviation
            tolerance_mm: Tolerance
        
        Returns:
            True if within tolerance
        """
        return abs(deviation_mm) <= tolerance_mm


class AdditiveDefects:
    """
    Unified additive manufacturing defects controller.
    """
    
    def __init__(self):
        self.porosity = PorosityDetection()
        self.crack = CrackDetection()
        self.misalignment = LayerMisalignment()
        self.geometric = GeometricDeviation()
    
    def defects_summary(self) -> Dict:
        """Get summary."""
        return {
            "defect_types": ["porosity", "crack", "misalignment", "geometric"],
            "detection": ["volumetric", "surface", "dimensional"]
        }
