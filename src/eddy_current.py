"""
Eddy Current Inspection Module
Eddy current testing, impedance plane analysis, conductivity measurement,
lift-off compensation, and defect detection for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EddyDefectType(Enum):
    """Eddy current detectable defect types."""
    NONE = "none"
    CRACK = "crack"
    CORROSION = "corrosion"
    THINNING = "thinning"
    INCLUSION = "inclusion"


@dataclass
class ImpedancePoint:
    """A point on the impedance plane."""
    resistance: float  # Real part (ohms)
    reactance: float   # Imaginary part (ohms)
    frequency_Hz: float = 1000.0


class ImpedancePlane:
    """
    Analyze impedance plane trajectories.
    """
    
    def __init__(self):
        self.points: List[ImpedancePoint] = []
    
    def add_point(self, point: ImpedancePoint):
        """Add impedance point."""
        self.points.append(point)
    
    def magnitude(self, point: ImpedancePoint) -> float:
        """
        Compute impedance magnitude.
        
        Args:
            point: Impedance point
        
        Returns:
            |Z| in ohms
        """
        return math.sqrt(point.resistance**2 + point.reactance**2)
    
    def phase_angle(self, point: ImpedancePoint) -> float:
        """
        Compute phase angle.
        
        Args:
            point: Impedance point
        
        Returns:
            Phase in radians
        """
        return math.atan2(point.reactance, point.resistance)
    
    def trajectory_length(self) -> float:
        """
        Compute total trajectory length.
        
        Returns:
            Length in impedance plane
        """
        if len(self.points) < 2:
            return 0.0
        
        length = 0.0
        for i in range(len(self.points) - 1):
            dx = self.points[i + 1].resistance - self.points[i].resistance
            dy = self.points[i + 1].reactance - self.points[i].reactance
            length += math.sqrt(dx**2 + dy**2)
        return length
    
    def area_enclosed(self) -> float:
        """
        Compute enclosed area (shoelace formula).
        
        Returns:
            Area
        """
        if len(self.points) < 3:
            return 0.0
        
        area = 0.0
        n = len(self.points)
        for i in range(n):
            j = (i + 1) % n
            area += self.points[i].resistance * self.points[j].reactance
            area -= self.points[j].resistance * self.points[i].reactance
        return abs(area) / 2.0


class ConductivityMeter:
    """
    Measure electrical conductivity from eddy current response.
    """
    
    def __init__(self, probe_diameter_mm: float = 3.0):
        """
        Args:
            probe_diameter_mm: Probe diameter
        """
        self.d = probe_diameter_mm
        self.standard_conductivity: Dict[str, float] = {
            "aluminum": 35.0,  # MS/m
            "copper": 58.0,
            "brass": 15.0,
            "stainless_steel": 1.4,
            "titanium": 0.6
        }
    
    def conductivity_from_impedance(self, Z_reference: ImpedancePoint,
                                   Z_sample: ImpedancePoint,
                                   ref_conductivity_MS_m: float) -> float:
        """
        Estimate conductivity from impedance comparison.
        
        Args:
            Z_reference: Reference impedance
            Z_sample: Sample impedance
            ref_conductivity_MS_m: Reference conductivity
        
        Returns:
            Estimated conductivity
        """
        mag_ref = math.sqrt(Z_reference.resistance**2 + Z_reference.reactance**2)
        mag_samp = math.sqrt(Z_sample.resistance**2 + Z_sample.reactance**2)
        
        if mag_ref <= 0:
            return 0.0
        
        # Conductivity inversely related to impedance magnitude
        ratio = mag_ref / mag_samp
        return ref_conductivity_MS_m * ratio
    
    def classify_material(self, conductivity_MS_m: float) -> str:
        """
        Classify material by conductivity.
        
        Args:
            conductivity_MS_m: Conductivity
        
        Returns:
            Material name
        """
        best_match = "unknown"
        best_diff = float('inf')
        
        for mat, cond in self.standard_conductivity.items():
            diff = abs(cond - conductivity_MS_m)
            if diff < best_diff:
                best_diff = diff
                best_match = mat
        
        return best_match


class LiftOffCompensator:
    """
    Compensate for probe lift-off distance.
    """
    
    def __init__(self):
        self.calibration: Dict[float, ImpedancePoint] = {}
    
    def calibrate(self, lift_off_mm: float, impedance: ImpedancePoint):
        """
        Calibrate at known lift-off.
        
        Args:
            lift_off_mm: Lift-off distance
            impedance: Measured impedance
        """
        self.calibration[lift_off_mm] = impedance
    
    def compensate(self, measured: ImpedancePoint,
                  lift_off_mm: float) -> ImpedancePoint:
        """
        Remove lift-off effect.
        
        Args:
            measured: Measured impedance
            lift_off_mm: Current lift-off
        
        Returns:
            Compensated impedance
        """
        if not self.calibration or lift_off_mm not in self.calibration:
            return measured
        
        cal = self.calibration[lift_off_mm]
        return ImpedancePoint(
            resistance=measured.resistance - cal.resistance + self.calibration[0.0].resistance if 0.0 in self.calibration else measured.resistance,
            reactance=measured.reactance - cal.reactance + self.calibration[0.0].reactance if 0.0 in self.calibration else measured.reactance,
            frequency_Hz=measured.frequency_Hz
        )
    
    def normalized_impedance(self, measured: ImpedancePoint,
                            reference: ImpedancePoint) -> Tuple[float, float]:
        """
        Compute normalized impedance.
        
        Args:
            measured: Measured
            reference: Reference
        
        Returns:
            (normalized_R, normalized_X)
        """
        mag_ref = math.sqrt(reference.resistance**2 + reference.reactance**2)
        if mag_ref <= 0:
            return (0.0, 0.0)
        return (measured.resistance / mag_ref, measured.reactance / mag_ref)


class EddyDefectDetector:
    """
    Detect defects from eddy current signals.
    """
    
    def __init__(self, impedance_threshold_percent: float = 10.0):
        """
        Args:
            impedance_threshold_percent: Detection threshold
        """
        self.threshold = impedance_threshold_percent
    
    def detect(self, trajectory: List[ImpedancePoint],
              reference: ImpedancePoint) -> List[Dict]:
        """
        Detect defects from trajectory.
        
        Args:
            trajectory: Measured trajectory
            reference: Reference impedance
        
        Returns:
            Defect list
        """
        ref_mag = math.sqrt(reference.resistance**2 + reference.reactance**2)
        if ref_mag <= 0:
            return []
        
        defects = []
        for i, point in enumerate(trajectory):
            mag = math.sqrt(point.resistance**2 + point.reactance**2)
            deviation = abs(mag - ref_mag) / ref_mag * 100.0
            
            if deviation > self.threshold:
                defects.append({
                    "index": i,
                    "deviation_percent": deviation,
                    "impedance": mag,
                    "type": EddyDefectType.CRACK.value
                })
        
        return defects
    
    def depth_estimate(self, impedance_change_percent: float,
                      frequency_Hz: float,
                      conductivity_MS_m: float) -> float:
        """
        Estimate defect depth from impedance change.
        
        Args:
            impedance_change_percent: Change
            frequency_Hz: Frequency
            conductivity_MS_m: Conductivity
        
        Returns:
            Depth in mm
        """
        # Skin depth: delta = sqrt(2 / (omega * mu * sigma))
        omega = 2.0 * math.pi * frequency_Hz
        mu = 4.0 * math.pi * 1e-7
        sigma = conductivity_MS_m * 1e6
        
        if omega <= 0 or sigma <= 0:
            return 0.0
        
        skin_depth = math.sqrt(2.0 / (omega * mu * sigma)) * 1000.0  # m to mm
        
        # Depth proportional to impedance change and skin depth
        return skin_depth * impedance_change_percent / 100.0


class EddyCurrent:
    """
    Unified eddy current inspection controller.
    """
    
    def __init__(self):
        self.plane = ImpedancePlane()
        self.conductivity = ConductivityMeter()
        self.lift_off = LiftOffCompensator()
        self.defect = EddyDefectDetector()
        self.inspections: List[Dict] = []
    
    def inspect(self, trajectory: List[ImpedancePoint],
               reference: ImpedancePoint,
               material: str = "aluminum") -> Dict:
        """
        Run eddy current inspection.
        
        Args:
            trajectory: Measured trajectory
            reference: Reference impedance
            material: Material name
        
        Returns:
            Inspection report
        """
        for p in trajectory:
            self.plane.add_point(p)
        
        defects = self.defect.detect(trajectory, reference)
        
        # Estimate conductivity
        est_cond = self.conductivity.conductivity_from_impedance(
            reference, trajectory[0] if trajectory else reference,
            self.conductivity.standard_conductivity.get(material, 35.0)
        )
        
        report = {
            "material": material,
            "trajectory_points": len(trajectory),
            "trajectory_length": self.plane.trajectory_length(),
            "defects_found": len(defects),
            "estimated_conductivity": est_cond,
            "classified_material": self.conductivity.classify_material(est_cond),
            "pass": len(defects) == 0
        }
        self.inspections.append(report)
        return report
    
    def skin_depth(self, frequency_Hz: float,
                  conductivity_MS_m: float) -> float:
        """
        Compute skin depth.
        
        Args:
            frequency_Hz: Frequency
            conductivity_MS_m: Conductivity
        
        Returns:
            Skin depth in mm
        """
        omega = 2.0 * math.pi * frequency_Hz
        mu = 4.0 * math.pi * 1e-7
        sigma = conductivity_MS_m * 1e6
        
        if omega <= 0 or sigma <= 0:
            return 0.0
        
        return math.sqrt(2.0 / (omega * mu * sigma)) * 1000.0
    
    def inspection_summary(self) -> Dict:
        """Get inspection summary."""
        if not self.inspections:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.inspections),
            "pass_count": sum(1 for r in self.inspections if r["pass"]),
            "total_defects": sum(r["defects_found"] for r in self.inspections)
        }
