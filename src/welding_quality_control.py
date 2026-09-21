"""
Welding Quality Control Module
Weld bead geometry, penetration depth,
heat affected zone, defect detection, and mechanical properties for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WeldBead:
    """Weld bead geometry."""
    width_mm: float
    height_mm: float
    penetration_mm: float
    reinforcement_mm: float


class WeldBeadGeometry:
    """
    Weld bead geometry analysis.
    """
    
    def __init__(self):
        pass
    
    def aspect_ratio(self, bead: WeldBead) -> float:
        """
        Compute weld bead aspect ratio.
        
        Args:
            bead: Weld bead
        
        Returns:
            Aspect ratio (width/height)
        """
        if bead.height_mm <= 0:
            return 0.0
        return bead.width_mm / bead.height_mm
    
    def dilution(self, bead: WeldBead,
                groove_area_mm2: float) -> float:
        """
        Compute weld dilution.
        
        Args:
            bead: Weld bead
            groove_area_mm2: Groove cross-section area
        
        Returns:
            Dilution fraction
        """
        bead_area = bead.width_mm * bead.penetration_mm
        total = bead_area + groove_area_mm2
        if total <= 0:
            return 0.0
        return groove_area_mm2 / total
    
    def throat_thickness(self, bead: WeldBead,
                        joint_angle_deg: float = 45.0) -> float:
        """
        Compute theoretical throat thickness for fillet weld.
        
        Args:
            bead: Weld bead
            joint_angle_deg: Joint angle
        
        Returns:
            Throat thickness
        """
        return bead.height_mm * math.sin(math.radians(joint_angle_deg))


class HeatAffectedZone:
    """
    Heat Affected Zone (HAZ) analysis.
    """
    
    def __init__(self, thermal_diffusivity_mm2_s: float = 8.0):
        """
        Args:
            thermal_diffusivity_mm2_s: Thermal diffusivity
        """
        self.alpha = thermal_diffusivity_mm2_s
    
    def haz_width(self, heat_input_J_mm: float,
                 preheat_temp_C: float,
                 melting_temp_C: float = 1500.0) -> float:
        """
        Estimate HAZ width.
        
        Args:
            heat_input_J_mm: Heat input per unit length
            preheat_temp_C: Preheat temperature
            melting_temp_C: Melting temperature
        
        Returns:
            HAZ width (mm)
        """
        delta_T = melting_temp_C - preheat_temp_C
        if delta_T <= 0:
            return 0.0
        # Simplified: HAZ width proportional to sqrt(heat_input / delta_T)
        return math.sqrt(self.alpha * heat_input_J_mm / (delta_T * 4.0))
    
    def cooling_time_t8_5(self, heat_input_J_mm: float,
                         thickness_mm: float,
                         preheat_temp_C: float = 20.0) -> float:
        """
        Compute cooling time from 800C to 500C.
        
        Args:
            heat_input_J_mm: Heat input
            thickness_mm: Plate thickness
            preheat_temp_C: Preheat temperature
        
        Returns:
            t8/5 cooling time (s)
        """
        if thickness_mm <= 0:
            return 0.0
        # Simplified formula
        return heat_input_J_mm / (2.0 * math.pi * self.alpha * thickness_mm) * 1000.0


class WeldDefectDetection:
    """
    Weld defect detection metrics.
    """
    
    def __init__(self):
        pass
    
    def porosity_fraction(self, pore_area_mm2: float,
                         total_area_mm2: float) -> float:
        """
        Compute porosity fraction.
        
        Args:
            pore_area_mm2: Total pore area
            total_area_mm2: Total weld area
        
        Returns:
            Porosity fraction
        """
        if total_area_mm2 <= 0:
            return 0.0
        return pore_area_mm2 / total_area_mm2
    
    def crack_acceptance(self, crack_length_mm: float,
                        plate_thickness_mm: float,
                        standard: str = "ISO") -> bool:
        """
        Check crack acceptance criteria.
        
        Args:
            crack_length_mm: Crack length
            plate_thickness_mm: Plate thickness
            standard: Standard name
        
        Returns:
            True if acceptable
        """
        if standard == "ISO":
            return crack_length_mm <= 0.1 * plate_thickness_mm
        return crack_length_mm <= 1.0
    
    def undercut_depth_acceptance(self, undercut_mm: float,
                                 thickness_mm: float) -> bool:
        """
        Check undercut acceptance.
        
        Args:
            undercut_mm: Undercut depth
            thickness_mm: Plate thickness
        
        Returns:
            True if acceptable
        """
        limit = 0.05 * thickness_mm
        return undercut_mm <= limit


class WeldMechanicalProperties:
    """
    Weld mechanical properties estimation.
    """
    
    def __init__(self):
        pass
    
    def hardness_haz(self, base_hardness_HV: float,
                    carbon_equivalent: float,
                    cooling_time_s: float) -> float:
        """
        Estimate HAZ hardness.
        
        Args:
            base_hardness_HV: Base metal hardness
            carbon_equivalent: CE
            cooling_time_s: t8/5
        
        Returns:
            HAZ hardness (HV)
        """
        if cooling_time_s <= 0:
            return base_hardness_HV
        # Simplified: hardness increases with CE and decreases with cooling time
        return base_hardness_HV * (1.0 + carbon_equivalent * 10.0 / cooling_time_s)
    
    def tensile_strength_estimate(self, base_uts_MPa: float,
                                 dilution: float) -> float:
        """
        Estimate weld metal tensile strength.
        
        Args:
            base_uts_MPa: Base metal UTS
            dilution: Dilution fraction
        
        Returns:
            Estimated UTS
        """
        # Simplified: weld metal ~90% of base for typical dilution
        return base_uts_MPa * (1.0 - 0.1 * dilution)


class WeldingQualityControl:
    """
    Unified welding quality control controller.
    """
    
    def __init__(self):
        self.bead = WeldBeadGeometry()
        self.haz = HeatAffectedZone()
        self.defects = WeldDefectDetection()
        self.mechanical = WeldMechanicalProperties()
    
    def welding_summary(self) -> Dict:
        """Get summary."""
        return {
            "metrics": ["bead_geometry", "HAZ", "defects", "mechanical"],
            "standards": ["ISO", "AWS", "ASME"]
        }
