"""
Coating Inspection Module
Coating thickness, adhesion, defect detection, and gloss
measurement for autonomous material quality assurance.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CoatingDefectType(Enum):
    """Types of coating defects."""
    PINHOLE = "pinhole"
    CRACK = "crack"
    BLISTER = "blister"
    ORANGE_PEEL = "orange_peel"
    SAG_RUN = "sag_run"
    CONTAMINATION = "contamination"


@dataclass
class CoatingMeasurement:
    """A coating measurement reading."""
    location: Tuple[float, float]
    thickness_um: float
    gloss_GU: float
    adhesion_MPa: float
    defect_detected: bool = False
    defect_type: Optional[CoatingDefectType] = None


class ThicknessGauge:
    """
    Coating thickness measurement and analysis.
    """
    
    def __init__(self, nominal_thickness_um: float = 100.0,
                 tolerance_percent: float = 10.0):
        """
        Args:
            nominal_thickness_um: Target thickness
            tolerance_percent: Allowed variation
        """
        self.nominal = nominal_thickness_um
        self.tolerance = tolerance_percent / 100.0
    
    def is_in_spec(self, thickness_um: float) -> bool:
        """
        Check if thickness is within specification.
        
        Args:
            thickness_um: Measured thickness
        
        Returns:
            True if in spec
        """
        lower = self.nominal * (1.0 - self.tolerance)
        upper = self.nominal * (1.0 + self.tolerance)
        return lower <= thickness_um <= upper
    
    def deviation(self, thickness_um: float) -> float:
        """
        Compute deviation from nominal.
        
        Args:
            thickness_um: Measured thickness
        
        Returns:
            Deviation percentage
        """
        return (thickness_um - self.nominal) / self.nominal * 100.0
    
    def uniformity(self, measurements: List[float]) -> float:
        """
        Compute thickness uniformity.
        
        Args:
            measurements: Thickness readings
        
        Returns:
            Coefficient of variation (%)
        """
        if not measurements or len(measurements) < 2:
            return 0.0
        
        mean = sum(measurements) / len(measurements)
        if mean == 0:
            return 0.0
        
        variance = sum((x - mean)**2 for x in measurements) / len(measurements)
        std = math.sqrt(variance)
        
        return (std / mean) * 100.0
    
    def coverage_estimate(self, measurements: List[float],
                         area_m2: float) -> float:
        """
        Estimate coating coverage quality.
        
        Args:
            measurements: Thickness readings
            area_m2: Total area
        
        Returns:
            Coverage score (0-1)
        """
        if not measurements:
            return 0.0
        
        in_spec = sum(1 for m in measurements if self.is_in_spec(m))
        return in_spec / len(measurements)


class AdhesionTester:
    """
    Coating adhesion assessment.
    """
    
    def __init__(self, min_adhesion_MPa: float = 5.0):
        """
        Args:
            min_adhesion_MPa: Minimum acceptable adhesion
        """
        self.min_adhesion = min_adhesion_MPa
    
    def assess(self, adhesion_MPa: float) -> str:
        """
        Assess adhesion strength.
        
        Args:
            adhesion_MPa: Measured adhesion
        
        Returns:
            Assessment string
        """
        if adhesion_MPa >= self.min_adhesion * 1.5:
            return "excellent"
        elif adhesion_MPa >= self.min_adhesion:
            return "acceptable"
        elif adhesion_MPa >= self.min_adhesion * 0.5:
            return "marginal"
        return "poor"
    
    def pull_off_strength(self, force_N: float,
                         dolly_diameter_mm: float = 20.0) -> float:
        """
        Compute pull-off adhesion strength.
        
        Args:
            force_N: Pull-off force
            dolly_diameter_mm: Dolly diameter
        
        Returns:
            Adhesion strength (MPa)
        """
        area_mm2 = math.pi * (dolly_diameter_mm / 2.0)**2
        area_m2 = area_mm2 * 1e-6
        
        if area_m2 <= 0:
            return 0.0
        
        return force_N / area_m2 / 1e6  # MPa


class DefectDetector:
    """
    Detect coating defects.
    """
    
    def __init__(self, gloss_threshold_deviation: float = 20.0,
                 thickness_threshold_deviation: float = 30.0):
        """
        Args:
            gloss_threshold_deviation: Gloss deviation threshold
            thickness_threshold_deviation: Thickness deviation threshold
        """
        self.gloss_thresh = gloss_threshold_deviation
        self.thickness_thresh = thickness_threshold_deviation
    
    def detect(self, measurement: CoatingMeasurement,
              nominal_gloss: float = 80.0) -> Tuple[bool, Optional[CoatingDefectType]]:
        """
        Detect defect from measurement.
        
        Args:
            measurement: Coating measurement
            nominal_gloss: Expected gloss
        
        Returns:
            (defect_detected, defect_type)
        """
        # Gloss deviation
        gloss_dev = abs(measurement.gloss_GU - nominal_gloss)
        
        if gloss_dev > self.gloss_thresh:
            if measurement.gloss_GU < nominal_gloss * 0.5:
                return (True, CoatingDefectType.PINHOLE)
            elif measurement.gloss_GU > nominal_gloss * 1.3:
                return (True, CoatingDefectType.SAG_RUN)
            return (True, CoatingDefectType.ORANGE_PEEL)
        
        # Thickness deviation
        if measurement.thickness_um < 10.0:
            return (True, CoatingDefectType.PINHOLE)
        
        if measurement.adhesion_MPa < 1.0:
            return (True, CoatingDefectType.BLISTER)
        
        return (False, None)
    
    def defect_density(self, defects: List[CoatingMeasurement],
                      area_m2: float) -> float:
        """
        Compute defect density.
        
        Args:
            defects: Defect measurements
            area_m2: Total area
        
        Returns:
            Defects per m^2
        """
        if area_m2 <= 0:
            return 0.0
        return len(defects) / area_m2


class GlossMeter:
    """
    Gloss measurement analyzer.
    """
    
    def __init__(self, angle_degrees: float = 60.0):
        """
        Args:
            angle_degrees: Measurement angle
        """
        self.angle = angle_degrees
    
    def classify_gloss(self, gloss_GU: float) -> str:
        """
        Classify gloss level.
        
        Args:
            gloss_GU: Gloss reading
        
        Returns:
            Gloss classification
        """
        if gloss_GU >= 70:
            return "high_gloss"
        elif gloss_GU >= 30:
            return "semi_gloss"
        elif gloss_GU >= 10:
            return "satin"
        return "matte"
    
    def haze_index(self, gloss_20: float, gloss_60: float) -> float:
        """
        Compute haze index.
        
        Args:
            gloss_20: 20-degree gloss
            gloss_60: 60-degree gloss
        
        Returns:
            Haze index
        """
        if gloss_60 <= 0:
            return 0.0
        return 100.0 * gloss_20 / gloss_60


class CoatingInspection:
    """
    Unified coating inspection system.
    """
    
    def __init__(self):
        self.thickness = ThicknessGauge()
        self.adhesion = AdhesionTester()
        self.defects = DefectDetector()
        self.gloss = GlossMeter()
        self.measurements: List[CoatingMeasurement] = []
    
    def measure(self, measurement: CoatingMeasurement):
        """Add measurement."""
        self.measurements.append(measurement)
    
    def inspection_report(self) -> Dict:
        """
        Generate inspection report.
        
        Returns:
            Report summary
        """
        if not self.measurements:
            return {"status": "no_data"}
        
        thicknesses = [m.thickness_um for m in self.measurements]
        glosses = [m.gloss_GU for m in self.measurements]
        adhesions = [m.adhesion_MPa for m in self.measurements]
        
        # Detect defects
        defect_count = 0
        defect_types: Dict[str, int] = {}
        for m in self.measurements:
            detected, dtype = self.defects.detect(m)
            if detected and dtype:
                defect_count += 1
                defect_types[dtype.value] = defect_types.get(dtype.value, 0) + 1
        
        return {
            "total_measurements": len(self.measurements),
            "avg_thickness_um": sum(thicknesses) / len(thicknesses),
            "thickness_uniformity_percent": self.thickness.uniformity(thicknesses),
            "avg_gloss_GU": sum(glosses) / len(glosses),
            "avg_adhesion_MPa": sum(adhesions) / len(adhesions),
            "defect_count": defect_count,
            "defect_types": defect_types,
            "pass_rate": (len(self.measurements) - defect_count) / len(self.measurements)
        }
    
    def quality_grade(self) -> str:
        """
        Compute overall quality grade.
        
        Returns:
            Grade (A/B/C/F)
        """
        report = self.inspection_report()
        if report.get("status") == "no_data":
            return "N/A"
        
        pass_rate = report.get("pass_rate", 0.0)
        uniformity = report.get("thickness_uniformity_percent", 100.0)
        
        if pass_rate >= 0.98 and uniformity < 5.0:
            return "A"
        elif pass_rate >= 0.95 and uniformity < 10.0:
            return "B"
        elif pass_rate >= 0.90:
            return "C"
        return "F"
