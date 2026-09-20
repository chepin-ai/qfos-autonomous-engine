"""
Penetrant Inspection Module
Dye penetrant testing, indication detection, sensitivity analysis,
and developer response evaluation for autonomous surface NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class IndicationType(Enum):
    """Types of penetrant indications."""
    NONE = "none"
    CRACK = "crack"
    POROSITY = "porosity"
    LAP = "lap"
    SEAM = "seam"
    INCLUSION = "inclusion"


class SensitivityLevel(Enum):
    """Penetrant sensitivity levels."""
    VERY_LOW = 0.5
    LOW = 1.0
    MEDIUM = 2.0
    HIGH = 3.0
    VERY_HIGH = 4.0


@dataclass
class Indication:
    """A detected penetrant indication."""
    x: float
    y: float
    length_mm: float
    width_mm: float
    intensity: float  # 0-1
    indication_type: IndicationType = IndicationType.NONE


class DyePenetrant:
    """
    Dye penetrant properties and application.
    """
    
    def __init__(self, sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM):
        """
        Args:
            sensitivity: Penetrant sensitivity
        """
        self.sensitivity = sensitivity
        self.viscosity_cps = 2.0 + sensitivity.value * 0.5
        self.dwell_time_min = 5.0 + sensitivity.value * 2.0
    
    def penetration_depth(self, crack_width_um: float) -> float:
        """
        Estimate penetration depth.
        
        Args:
            crack_width_um: Crack opening width in microns
        
        Returns:
            Depth in mm
        """
        # Deeper penetration for narrower cracks with higher sensitivity
        if crack_width_um <= 0:
            return 0.0
        base_depth = 10.0 / crack_width_um  # mm
        return base_depth * self.sensitivity.value
    
    def visibility_score(self, indication_intensity: float) -> float:
        """
        Compute visibility score.
        
        Args:
            indication_intensity: Raw intensity
        
        Returns:
            Visibility [0, 1]
        """
        return min(1.0, indication_intensity * self.sensitivity.value)


class Developer:
    """
    Developer application and response analyzer.
    """
    
    def __init__(self, thickness_um: float = 50.0):
        """
        Args:
            thickness_um: Developer layer thickness
        """
        self.thickness = thickness_um
        self.blotting_time_min = 10.0
    
    def extract_indication(self, raw_response: float,
                          background: float) -> float:
        """
        Extract indication from background.
        
        Args:
            raw_response: Raw signal
            background: Background level
        
        Returns:
            Extracted indication intensity
        """
        return max(0.0, raw_response - background)
    
    def spreading_factor(self, viscosity_cps: float) -> float:
        """
        Compute dye spreading factor.
        
        Args:
            viscosity_cps: Penetrant viscosity
        
        Returns:
            Spreading factor
        """
        if viscosity_cps <= 0:
            return 1.0
        return 1.0 + 50.0 / (viscosity_cps * self.thickness)


class IndicationDetector:
    """
    Detect and classify penetrant indications.
    """
    
    def __init__(self, intensity_threshold: float = 0.1):
        """
        Args:
            intensity_threshold: Detection threshold
        """
        self.threshold = intensity_threshold
    
    def detect(self, image_intensities: List[float],
              positions: List[Tuple[float, float]]) -> List[Indication]:
        """
        Detect indications from image data.
        
        Args:
            image_intensities: Pixel intensities
            positions: Pixel positions
        
        Returns:
            Detected indications
        """
        indications = []
        i = 0
        while i < len(image_intensities):
            if image_intensities[i] > self.threshold:
                # Find indication extent
                start = i
                max_intensity = image_intensities[i]
                while i < len(image_intensities) and image_intensities[i] > self.threshold:
                    max_intensity = max(max_intensity, image_intensities[i])
                    i += 1
                end = i
                
                # Compute centroid
                xs = [positions[j][0] for j in range(start, end)]
                ys = [positions[j][1] for j in range(start, end)]
                cx = sum(xs) / len(xs) if xs else 0
                cy = sum(ys) / len(ys) if ys else 0
                
                length = max(xs) - min(xs) if xs else 0
                width = max(ys) - min(ys) if ys else 0
                
                # Classify by shape
                ind_type = IndicationType.POROSITY
                if length > 3 * width and length > 5.0:
                    ind_type = IndicationType.CRACK
                elif width > 3 * length:
                    ind_type = IndicationType.LAP
                
                indications.append(Indication(
                    x=cx, y=cy, length_mm=length, width_mm=width,
                    intensity=max_intensity, indication_type=ind_type
                ))
            else:
                i += 1
        
        return indications
    
    def rejectable(self, indication: Indication,
                  spec_length_mm: float = 3.0) -> bool:
        """
        Check if indication is rejectable per spec.
        
        Args:
            indication: Indication
            spec_length_mm: Maximum allowed length
        
        Returns:
            True if rejectable
        """
        return indication.length_mm > spec_length_mm
    
    def linear_indications(self, indications: List[Indication]) -> List[Indication]:
        """
        Filter linear indications.
        
        Args:
            indications: All indications
        
        Returns:
            Linear indications
        """
        return [ind for ind in indications
                if ind.indication_type in (IndicationType.CRACK, IndicationType.LAP, IndicationType.SEAM)]
    
    def rounded_indications(self, indications: List[Indication]) -> List[Indication]:
        """
        Filter rounded indications.
        
        Args:
            indications: All indications
        
        Returns:
            Rounded indications
        """
        return [ind for ind in indications
                if ind.indication_type in (IndicationType.POROSITY, IndicationType.INCLUSION)]


class SensitivityAnalyzer:
    """
    Analyze inspection sensitivity.
    """
    
    def __init__(self):
        self.calibration_data: List[Tuple[float, float]] = []
    
    def calibrate(self, known_defect_size_um: float,
                 detected_intensity: float):
        """
        Add calibration point.
        
        Args:
            known_defect_size_um: Known size
            detected_intensity: Measured intensity
        """
        self.calibration_data.append((known_defect_size_um, detected_intensity))
    
    def minimum_detectable_size(self) -> float:
        """
        Estimate minimum detectable defect size.
        
        Returns:
            Size in microns
        """
        if not self.calibration_data:
            return 10.0
        
        # Find smallest detected size
        detected = [size for size, intensity in self.calibration_data if intensity > 0.1]
        return min(detected) if detected else 10.0
    
    def detection_probability(self, defect_size_um: float) -> float:
        """
        Estimate detection probability.
        
        Args:
            defect_size_um: Defect size
        
        Returns:
            Probability [0, 1]
        """
        if not self.calibration_data:
            return 0.5
        
        # Logistic fit approximation
        mds = self.minimum_detectable_size()
        if mds <= 0:
            return 0.5
        return 1.0 / (1.0 + math.exp(-(defect_size_um - mds) / mds))


class PenetrantInspection:
    """
    Unified penetrant inspection controller.
    """
    
    def __init__(self):
        self.penetrant = DyePenetrant()
        self.developer = Developer()
        self.detector = IndicationDetector()
        self.sensitivity = SensitivityAnalyzer()
        self.inspections: List[Dict] = []
    
    def inspect(self, image_intensities: List[float],
               positions: List[Tuple[float, float]],
               spec_length_mm: float = 3.0) -> Dict:
        """
        Run penetrant inspection.
        
        Args:
            image_intensities: Image intensities
            positions: Positions
            spec_length_mm: Specification limit
        
        Returns:
            Inspection report
        """
        indications = self.detector.detect(image_intensities, positions)
        rejectable = [ind for ind in indications if self.detector.rejectable(ind, spec_length_mm)]
        linear = self.detector.linear_indications(indications)
        rounded = self.detector.rounded_indications(indications)
        
        report = {
            "indications": len(indications),
            "rejectable": len(rejectable),
            "linear": len(linear),
            "rounded": len(rounded),
            "sensitivity": self.penetrant.sensitivity.name,
            "pass": len(rejectable) == 0
        }
        self.inspections.append(report)
        return report
    
    def set_sensitivity(self, level: SensitivityLevel):
        """
        Set inspection sensitivity.
        
        Args:
            level: Sensitivity level
        """
        self.penetrant = DyePenetrant(level)
    
    def inspection_summary(self) -> Dict:
        """Get inspection summary."""
        if not self.inspections:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.inspections),
            "pass_count": sum(1 for r in self.inspections if r["pass"]),
            "total_indications": sum(r["indications"] for r in self.inspections),
            "total_rejectable": sum(r["rejectable"] for r in self.inspections)
        }
