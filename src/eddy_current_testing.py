"""
Eddy Current Testing Module
Impedance analysis, flaw detection, conductivity measurement,
lift-off compensation, and frequency response for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ImpedancePoint:
    """Impedance measurement point."""
    frequency_Hz: float
    resistance_Ohm: float
    reactance_Ohm: float


class ImpedanceAnalyzer:
    """
    Eddy current impedance analysis.
    """
    
    def __init__(self, coil_inductance_H: float = 1e-3,
                 coil_resistance_Ohm: float = 10.0):
        """
        Args:
            coil_inductance_H: Coil inductance
            coil_resistance_Ohm: Coil resistance
        """
        self.L = coil_inductance_H
        self.R_coil = coil_resistance_Ohm
    
    def impedance(self, frequency_Hz: float,
                 sample_resistance_Ohm: float = 0.0,
                 sample_reactance_Ohm: float = 0.0) -> Tuple[float, float]:
        """
        Compute total impedance.
        
        Args:
            frequency_Hz: Frequency
            sample_resistance_Ohm: Sample resistance
            sample_reactance_Ohm: Sample reactance
        
        Returns:
            (R, X) impedance
        """
        omega = 2.0 * math.pi * frequency_Hz
        X_L = omega * self.L
        
        R_total = self.R_coil + sample_resistance_Ohm
        X_total = X_L + sample_reactance_Ohm
        
        return (R_total, X_total)
    
    def magnitude(self, R: float, X: float) -> float:
        """
        Compute impedance magnitude.
        
        Args:
            R: Resistance
            X: Reactance
        
        Returns:
            Magnitude
        """
        return math.sqrt(R ** 2 + X ** 2)
    
    def phase_angle(self, R: float, X: float) -> float:
        """
        Compute phase angle.
        
        Args:
            R: Resistance
            X: Reactance
        
        Returns:
            Phase angle in degrees
        """
        if R == 0:
            return 90.0 if X > 0 else -90.0
        return math.degrees(math.atan2(X, R))
    
    def skin_depth(self, conductivity_S_m: float,
                  frequency_Hz: float,
                  permeability_H_m: float = 4.0e-7 * math.pi) -> float:
        """
        Compute electromagnetic skin depth.
        
        Args:
            conductivity_S_m: Electrical conductivity
            frequency_Hz: Frequency
            permeability_H_m: Magnetic permeability
        
        Returns:
            Skin depth in meters
        """
        if conductivity_S_m <= 0 or frequency_Hz <= 0:
            return float('inf')
        return math.sqrt(1.0 / (math.pi * frequency_Hz * conductivity_S_m * permeability_H_m))


class FlawDetector:
    """
    Eddy current flaw detection.
    """
    
    def __init__(self, threshold_percent: float = 10.0):
        """
        Args:
            threshold_percent: Detection threshold
        """
        self.threshold = threshold_percent
    
    def detect_from_impedance(self,
                              baseline: List[ImpedancePoint],
                              measured: List[ImpedancePoint]) -> List[Dict]:
        """
        Detect flaws from impedance comparison.
        
        Args:
            baseline: Baseline measurements
            measured: Measured values
        
        Returns:
            Detected flaws
        """
        flaws = []
        for base, meas in zip(baseline, measured):
            base_mag = math.sqrt(base.resistance_Ohm ** 2 + base.reactance_Ohm ** 2)
            meas_mag = math.sqrt(meas.resistance_Ohm ** 2 + meas.reactance_Ohm ** 2)
            
            if base_mag > 0:
                change_percent = abs(meas_mag - base_mag) / base_mag * 100.0
                if change_percent > self.threshold:
                    flaws.append({
                        "frequency_Hz": base.frequency_Hz,
                        "change_percent": change_percent,
                        "severity": "high" if change_percent > 50.0 else "medium"
                    })
        
        return flaws
    
    def crack_depth_estimate(self, impedance_change_percent: float,
                            skin_depth_m: float) -> float:
        """
        Estimate crack depth from impedance change.
        
        Args:
            impedance_change_percent: Impedance change
            skin_depth_m: Skin depth
        
        Returns:
            Estimated depth in meters
        """
        # Simplified: depth proportional to impedance change
        return skin_depth_m * impedance_change_percent / 100.0


class ConductivityMeter:
    """
    Electrical conductivity measurement.
    """
    
    def __init__(self):
        pass
    
    def conductivity_from_impedance(self, R_sample_Ohm: float,
                                   thickness_m: float,
                                   area_m2: float) -> float:
        """
        Compute conductivity from sample resistance.
        
        Args:
            R_sample_Ohm: Sample resistance
            thickness_m: Sample thickness
            area_m2: Sample area
        
        Returns:
            Conductivity in S/m
        """
        if R_sample_Ohm <= 0 or thickness_m <= 0:
            return 0.0
        return thickness_m / (R_sample_Ohm * area_m2)
    
    def iacs_conductivity(self, conductivity_S_m: float) -> float:
        """
        Convert to %IACS (International Annealed Copper Standard).
        
        Args:
            conductivity_S_m: Conductivity
        
        Returns:
            %IACS
        """
        copper_conductivity = 5.8e7
        return conductivity_S_m / copper_conductivity * 100.0


class LiftOffCompensator:
    """
    Lift-off compensation for eddy current testing.
    """
    
    def __init__(self):
        pass
    
    def compensated_impedance(self, measured_R: float,
                             measured_X: float,
                             lift_off_m: float,
                             reference_lift_off_m: float = 0.001) -> Tuple[float, float]:
        """
        Compensate for lift-off effect.
        
        Args:
            measured_R: Measured resistance
            measured_X: Measured reactance
            lift_off_m: Actual lift-off
            reference_lift_off_m: Reference lift-off
        
        Returns:
            Compensated (R, X)
        """
        # Simplified: linear compensation
        ratio = reference_lift_off_m / lift_off_m if lift_off_m > 0 else 1.0
        return (measured_R * ratio, measured_X * ratio)


class EddyCurrentTesting:
    """
    Unified eddy current testing controller.
    """
    
    def __init__(self):
        self.impedance = ImpedanceAnalyzer()
        self.flaw = FlawDetector()
        self.conductivity = ConductivityMeter()
        self.lift_off = LiftOffCompensator()
    
    def ect_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["impedance_analysis", "flaw_detection", "conductivity", "lift_off"],
            "coil_L_H": self.impedance.L,
            "coil_R_Ohm": self.impedance.R_coil
        }
