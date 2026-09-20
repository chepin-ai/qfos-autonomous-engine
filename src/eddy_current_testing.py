"""
Eddy Current Testing Module
Electromagnetic induction, impedance analysis, crack detection,
and material property evaluation for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CoilMeasurement:
    """Eddy current coil measurement."""
    frequency_Hz: float
    impedance_real_Ohm: float
    impedance_imag_Ohm: float
    lift_off_mm: float


class ImpedanceAnalyzer:
    """
    Analyze eddy current impedance.
    """
    
    def __init__(self):
        pass
    
    def impedance_magnitude(self, measurement: CoilMeasurement) -> float:
        """
        Compute magnitude.
        
        Args:
            measurement: Measurement
        
        Returns:
            Magnitude
        """
        return math.sqrt(measurement.impedance_real_Ohm**2 +
                        measurement.impedance_imag_Ohm**2)
    
    def phase_angle(self, measurement: CoilMeasurement) -> float:
        """
        Compute phase angle.
        
        Args:
            measurement: Measurement
        
        Returns:
            Phase in radians
        """
        return math.atan2(measurement.impedance_imag_Ohm,
                         measurement.impedance_real_Ohm)
    
    def reactance(self, measurement: CoilMeasurement) -> float:
        """
        Get reactance.
        
        Args:
            measurement: Measurement
        
        Returns:
            Reactance
        """
        return measurement.impedance_imag_Ohm
    
    def skin_depth(self, conductivity_S_m: float,
                  permeability_H_m: float,
                  frequency_Hz: float) -> float:
        """
        Compute skin depth.
        
        Args:
            conductivity_S_m: Conductivity
            permeability_H_m: Permeability
            frequency_Hz: Frequency
        
        Returns:
            Skin depth in meters
        """
        if frequency_Hz <= 0 or conductivity_S_m <= 0:
            return float('inf')
        return math.sqrt(1.0 / (math.pi * frequency_Hz *
                                conductivity_S_m * permeability_H_m))


class CrackDetector:
    """
    Detect cracks from impedance changes.
    """
    
    def __init__(self, threshold_percent: float = 5.0):
        """
        Args:
            threshold_percent: Detection threshold
        """
        self.threshold = threshold_percent
    
    def detect(self, reference: CoilMeasurement,
              scan: CoilMeasurement) -> bool:
        """
        Detect crack presence.
        
        Args:
            reference: Reference measurement
            scan: Scan measurement
        
        Returns:
            True if crack detected
        """
        ref_mag = math.sqrt(reference.impedance_real_Ohm**2 +
                           reference.impedance_imag_Ohm**2)
        scan_mag = math.sqrt(scan.impedance_real_Ohm**2 +
                            scan.impedance_imag_Ohm**2)
        
        if ref_mag <= 0:
            return False
        
        change = abs(scan_mag - ref_mag) / ref_mag * 100.0
        return change > self.threshold
    
    def crack_depth_estimate(self, impedance_change_percent: float,
                            skin_depth_mm: float) -> float:
        """
        Estimate crack depth.
        
        Args:
            impedance_change_percent: Change
            skin_depth_mm: Skin depth
        
        Returns:
            Depth in mm
        """
        # Simplified model
        return impedance_change_percent / 100.0 * skin_depth_mm


class LiftOffCompensator:
    """
    Compensate for lift-off effects.
    """
    
    def __init__(self):
        pass
    
    def compensate(self, measurement: CoilMeasurement,
                  target_lift_off_mm: float) -> CoilMeasurement:
        """
        Compensate lift-off.
        
        Args:
            measurement: Measurement
            target_lift_off_mm: Target lift-off
        
        Returns:
            Compensated measurement
        """
        delta = measurement.lift_off_mm - target_lift_off_mm
        
        # Simplified: assume impedance changes linearly with lift-off
        compensation_factor = 1.0 - 0.05 * delta
        
        return CoilMeasurement(
            measurement.frequency_Hz,
            measurement.impedance_real_Ohm * compensation_factor,
            measurement.impedance_imag_Ohm * compensation_factor,
            target_lift_off_mm
        )


class MaterialPropertyEvaluator:
    """
    Evaluate material properties from eddy current data.
    """
    
    def __init__(self):
        pass
    
    def conductivity(self, impedance_real: float,
                    coil_radius_mm: float,
                    frequency_Hz: float) -> float:
        """
        Estimate conductivity.
        
        Args:
            impedance_real: Real impedance
            coil_radius_mm: Coil radius
            frequency_Hz: Frequency
        
        Returns:
            Conductivity in S/m
        """
        if coil_radius_mm <= 0 or frequency_Hz <= 0:
            return 0.0
        
        # Simplified model
        area = math.pi * (coil_radius_mm / 1000.0) ** 2
        return impedance_real / (2.0 * math.pi * frequency_Hz * area)
    
    def permeability(self, impedance_imag: float,
                    coil_inductance_H: float) -> float:
        """
        Estimate permeability.
        
        Args:
            impedance_imag: Imaginary impedance
            coil_inductance_H: Coil inductance
        
        Returns:
            Relative permeability
        """
        if coil_inductance_H <= 0:
            return 1.0
        
        mu0 = 4.0 * math.pi * 1e-7
        return impedance_imag / (2.0 * math.pi * coil_inductance_H) / mu0


class EddyCurrentTesting:
    """
    Unified eddy current testing controller.
    """
    
    def __init__(self):
        self.analyzer = ImpedanceAnalyzer()
        self.detector = CrackDetector()
        self.compensator = LiftOffCompensator()
        self.evaluator = MaterialPropertyEvaluator()
        self.measurements: List[CoilMeasurement] = []
        self.reference: Optional[CoilMeasurement] = None
    
    def set_reference(self, measurement: CoilMeasurement):
        """
        Set reference.
        
        Args:
            measurement: Reference
        """
        self.reference = measurement
    
    def scan(self, measurement: CoilMeasurement):
        """
        Add scan.
        
        Args:
            measurement: Measurement
        """
        self.measurements.append(measurement)
    
    def inspect(self) -> Dict:
        """
        Inspect.
        
        Returns:
            Results
        """
        if not self.measurements or not self.reference:
            return {}
        
        cracks = 0
        for m in self.measurements:
            if self.detector.detect(self.reference, m):
                cracks += 1
        
        return {
            "scans": len(self.measurements),
            "crack_indications": cracks,
            "skin_depth_mm": self.analyzer.skin_depth(
                1e6, 4.0 * math.pi * 1e-7, self.reference.frequency_Hz
            ) * 1000.0 if self.reference else 0.0
        }
    
    def ect_summary(self) -> Dict:
        """Get summary."""
        return {
            "measurements": len(self.measurements),
            "reference_set": self.reference is not None
        }
