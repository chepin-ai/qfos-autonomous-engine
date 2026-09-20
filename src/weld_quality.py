"""
Weld Quality Module
Weld inspection, bead geometry, porosity detection, and
crack assessment for autonomous manufacturing quality control.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class WeldDefectType(Enum):
    """Types of weld defects."""
    POROSITY = "porosity"
    CRACK = "crack"
    LACK_OF_FUSION = "lack_of_fusion"
    UNDERCUT = "undercut"
    OVERLAP = "overlap"
    INCOMPLETE_PENETRATION = "incomplete_penetration"


@dataclass
class WeldMeasurement:
    """A weld measurement reading."""
    location_mm: Tuple[float, float]
    bead_width_mm: float
    bead_height_mm: float
    penetration_depth_mm: float
    porosity_count: int = 0
    crack_length_mm: float = 0.0


class BeadGeometryAnalyzer:
    """
    Analyze weld bead geometry.
    """
    
    def __init__(self, nominal_width_mm: float = 5.0,
                 nominal_height_mm: float = 2.0):
        """
        Args:
            nominal_width_mm: Target bead width
            nominal_height_mm: Target bead height
        """
        self.nominal_width = nominal_width_mm
        self.nominal_height = nominal_height_mm
    
    def aspect_ratio(self, width_mm: float, height_mm: float) -> float:
        """
        Compute bead aspect ratio.
        
        Args:
            width_mm: Bead width
            height_mm: Bead height
        
        Returns:
            Width / height ratio
        """
        if height_mm <= 0:
            return 0.0
        return width_mm / height_mm
    
    is_in_spec = None  # Placeholder to avoid lint issues
    
    def width_deviation(self, measured_width_mm: float) -> float:
        """
        Compute width deviation.
        
        Args:
            measured_width_mm: Measured width
        
        Returns:
            Deviation percentage
        """
        return (measured_width_mm - self.nominal_width) / self.nominal_width * 100.0
    
    def reinforcement_factor(self, height_mm: float,
                            base_thickness_mm: float = 5.0) -> float:
        """
        Compute reinforcement factor.
        
        Args:
            height_mm: Bead height
            base_thickness_mm: Base material thickness
        
        Returns:
            Reinforcement factor
        """
        if base_thickness_mm <= 0:
            return 0.0
        return height_mm / base_thickness_mm
    
    def dilution(self, bead_area_mm2: float,
                base_melted_area_mm2: float) -> float:
        """
        Compute weld dilution.
        
        Args:
            bead_area_mm2: Total weld area
            base_melted_area_mm2: Base metal melted area
        
        Returns:
            Dilution percentage
        """
        if bead_area_mm2 <= 0:
            return 0.0
        return base_melted_area_mm2 / bead_area_mm2 * 100.0


class PorosityDetector:
    """
    Detect and quantify porosity.
    """
    
    def __init__(self, max_pores_per_cm2: float = 5.0,
                 max_pore_diameter_mm: float = 1.0):
        """
        Args:
            max_pores_per_cm2: Maximum acceptable pore density
            max_pore_diameter_mm: Maximum acceptable pore size
        """
        self.max_density = max_pores_per_cm2
        self.max_size = max_pore_diameter_mm
    
    def pore_density(self, pore_count: int,
                    area_cm2: float) -> float:
        """
        Compute pore density.
        
        Args:
            pore_count: Number of pores
            area_cm2: Inspection area
        
        Returns:
            Pores per cm^2
        """
        if area_cm2 <= 0:
            return 0.0
        return pore_count / area_cm2
    
    def assess(self, pore_count: int,
              area_cm2: float,
              max_pore_diameter_mm: float = 0.0) -> str:
        """
        Assess porosity level.
        
        Args:
            pore_count: Number of pores
            area_cm2: Area
            max_pore_diameter_mm: Largest pore diameter
        
        Returns:
            Assessment string
        """
        density = self.pore_density(pore_count, area_cm2)
        
        if density > self.max_density or max_pore_diameter_mm > self.max_size:
            return "reject"
        elif density > self.max_density * 0.5:
            return "marginal"
        
        return "acceptable"
    
    void_fraction = None  # Placeholder


class CrackDetector:
    """
    Detect and assess cracks.
    """
    
    def __init__(self, max_crack_length_mm: float = 3.0,
                 critical_depth_mm: float = 1.0):
        """
        Args:
            max_crack_length_mm: Maximum acceptable crack length
            critical_depth_mm: Critical crack depth
        """
        self.max_length = max_crack_length_mm
        self.critical_depth = critical_depth_mm
    
    def assess(self, crack_length_mm: float,
              crack_depth_mm: float = 0.0) -> str:
        """
        Assess crack severity.
        
        Args:
            crack_length_mm: Crack length
            crack_depth_mm: Crack depth
        
        Returns:
            Assessment string
        """
        if crack_length_mm > self.max_length or crack_depth_mm > self.critical_depth:
            return "critical"
        elif crack_length_mm > self.max_length * 0.5:
            return "moderate"
        elif crack_length_mm > 0:
            return "minor"
        return "none"
    
    def total_crack_length(self, cracks: List[float]) -> float:
        """
        Sum total crack length.
        
        Args:
            cracks: List of crack lengths
        
        Returns:
            Total length
        """
        return sum(cracks)


class WeldQuality:
    """
    Unified weld quality controller.
    """
    
    def __init__(self):
        self.geometry = BeadGeometryAnalyzer()
        self.porosity = PorosityDetector()
        self.crack = CrackDetector()
        self.measurements: List[WeldMeasurement] = []
    
    def add_measurement(self, measurement: WeldMeasurement):
        """Add weld measurement."""
        self.measurements.append(measurement)
    
    def quality_report(self) -> Dict:
        """
        Generate weld quality report.
        
        Returns:
            Quality summary
        """
        if not self.measurements:
            return {"status": "no_data"}
        
        widths = [m.bead_width_mm for m in self.measurements]
        heights = [m.bead_height_mm for m in self.measurements]
        pores = sum(m.porosity_count for m in self.measurements)
        cracks = [m.crack_length_mm for m in self.measurements if m.crack_length_mm > 0]
        
        avg_width = sum(widths) / len(widths)
        avg_height = sum(heights) / len(heights)
        total_crack = sum(cracks)
        
        # Assessments
        pore_assess = self.porosity.assess(pores, 10.0)
        crack_assess = self.crack.assess(total_crack)
        
        # Overall grade
        if crack_assess == "critical" or pore_assess == "reject":
            grade = "F"
        elif crack_assess == "moderate" or pore_assess == "marginal":
            grade = "C"
        elif total_crack > 0 or pores > 0:
            grade = "B"
        else:
            grade = "A"
        
        return {
            "total_measurements": len(self.measurements),
            "avg_width_mm": avg_width,
            "avg_height_mm": avg_height,
            "aspect_ratio": self.geometry.aspect_ratio(avg_width, avg_height),
            "total_pores": pores,
            "porosity_assessment": pore_assess,
            "total_crack_mm": total_crack,
            "crack_assessment": crack_assess,
            "grade": grade
        }
    
    def pass_fail(self) -> bool:
        """
        Determine pass/fail.
        
        Returns:
            True if weld passes
        """
        report = self.quality_report()
        return report.get("grade") not in ["F"]
