"""
Eddy Current Array Module
ECA probe modeling, impedance plane analysis, lift-off compensation,
and defect classification for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CoilConfig:
    """EC coil configuration."""
    diameter_mm: float
    turns: int
    frequency_Hz: float
    lift_off_mm: float = 0.0


class ImpedancePlaneAnalyzer:
    """
    Analyze impedance plane trajectories.
    """
    
    def __init__(self):
        pass
    
    def normalize(self, real: float, imag: float,
                 ref_real: float, ref_imag: float) -> Tuple[float, float]:
        """
        Normalize impedance.
        
        Args:
            real: Real part
            imag: Imaginary part
            ref_real: Reference real
            ref_imag: Reference imaginary
        
        Returns:
            Normalized (real, imag)
        """
        if ref_real == 0:
            ref_real = 1e-10
        if ref_imag == 0:
            ref_imag = 1e-10
        
        return (real / ref_real, imag / ref_imag)
    
    def angle(self, real: float, imag: float) -> float:
        """
        Compute impedance angle.
        
        Args:
            real: Real
            imag: Imaginary
        
        Returns:
            Angle in degrees
        """
        return math.degrees(math.atan2(imag, real))
    
    def magnitude(self, real: float, imag: float) -> float:
        """
        Compute magnitude.
        
        Args:
            real: Real
            imag: Imaginary
        
        Returns:
            Magnitude
        """
        return math.sqrt(real**2 + imag**2)
    
    def trajectory(self, readings: List[Tuple[float, float]]) -> Dict:
        """
        Analyze trajectory.
        
        Args:
            readings: (real, imag) readings
        
        Returns:
            Analysis
        """
        if not readings:
            return {}
        
        angles = [self.angle(r, i) for r, i in readings]
        mags = [self.magnitude(r, i) for r, i in readings]
        
        return {
            "start_angle": angles[0],
            "end_angle": angles[-1],
            "angle_span": angles[-1] - angles[0],
            "max_magnitude": max(mags),
            "min_magnitude": min(mags),
            "readings": len(readings)
        }


class LiftOffCompensator:
    """
    Compensate for lift-off effects.
    """
    
    def __init__(self):
        self.lift_off_curve: List[Tuple[float, float]] = []
    
    def calibrate(self, lift_offs: List[float],
                 real_vals: List[float],
                 imag_vals: List[float]):
        """
        Calibrate lift-off curve.
        
        Args:
            lift_offs: Lift-off values
            real_vals: Real impedance
            imag_vals: Imaginary impedance
        """
        self.lift_off_curve = list(zip(lift_offs, real_vals, imag_vals))
    
    def compensate(self, real: float, imag: float,
                  actual_lift_off: float) -> Tuple[float, float]:
        """
        Compensate reading.
        
        Args:
            real: Real impedance
            imag: Imaginary impedance
            actual_lift_off: Actual lift-off
        
        Returns:
            Compensated (real, imag)
        """
        if not self.lift_off_curve:
            return (real, imag)
        
        # Find closest calibration point
        closest = min(self.lift_off_curve, key=lambda x: abs(x[0] - actual_lift_off))
        _, ref_real, ref_imag = closest
        
        # Subtract lift-off effect
        return (real - ref_real, imag - ref_imag)


class DefectClassifier:
    """
    Classify defects from ECA signals.
    """
    
    def __init__(self):
        self.threshold_angle = 30.0
    
    def classify(self, angle_change: float,
                magnitude_change: float) -> str:
        """
        Classify defect.
        
        Args:
            angle_change: Angle change
            magnitude_change: Magnitude change
        
        Returns:
            Classification
        """
        if abs(angle_change) < self.threshold_angle and magnitude_change > 0.1:
            return "lift_off"
        elif angle_change > self.threshold_angle:
            return "crack"
        elif angle_change < -self.threshold_angle:
            return "corrosion"
        elif abs(magnitude_change) < 0.05:
            return "noise"
        else:
            return "unknown"
    
    def classify_trajectory(self, trajectory: List[Tuple[float, float]]) -> str:
        """
        Classify from trajectory.
        
        Args:
            trajectory: (real, imag) points
        
        Returns:
            Classification
        """
        if len(trajectory) < 2:
            return "unknown"
        
        analyzer = ImpedancePlaneAnalyzer()
        start_angle = analyzer.angle(*trajectory[0])
        end_angle = analyzer.angle(*trajectory[-1])
        angle_change = end_angle - start_angle
        
        start_mag = analyzer.magnitude(*trajectory[0])
        end_mag = analyzer.magnitude(*trajectory[-1])
        magnitude_change = (end_mag - start_mag) / max(start_mag, 1e-10)
        
        return self.classify(angle_change, magnitude_change)


class ECAProbeSimulator:
    """
    Simulate ECA probe response.
    """
    
    def __init__(self, coil: CoilConfig):
        """
        Args:
            coil: Coil config
        """
        self.coil = coil
    
    def impedance(self, conductivity: float = 1.0,
                 permeability: float = 1.0) -> Tuple[float, float]:
        """
        Compute coil impedance.
        
        Args:
            conductivity: Material conductivity
            permeability: Material permeability
        
        Returns:
            (real, imag)
        """
        omega = 2.0 * math.pi * self.coil.frequency_Hz
        L = self.coil.turns ** 2 * permeability * math.pi * (self.coil.diameter_mm / 2000.0) ** 2
        R = 1.0 + conductivity * omega * self.coil.lift_off_mm * 1e-3
        
        real = R
        imag = omega * L
        
        return (real, imag)
    
    def scan_response(self, positions: List[float],
                     defect_depth: float = 0.0) -> List[Tuple[float, float]]:
        """
        Simulate scan over defect.
        
        Args:
            positions: Probe positions
            defect_depth: Defect depth
        
        Returns:
            Impedance readings
        """
        readings = []
        base_real, base_imag = self.impedance()
        
        for pos in positions:
            # Defect response: Gaussian perturbation
            perturbation = math.exp(-(pos ** 2) / (2.0 * (defect_depth + 1.0) ** 2))
            
            real = base_real + perturbation * 0.1 * base_real
            imag = base_imag + perturbation * 0.2 * base_imag
            
            readings.append((real, imag))
        
        return readings


class EddyCurrentArray:
    """
    Unified eddy current array controller.
    """
    
    def __init__(self):
        self.coil = CoilConfig(3.0, 50, 100000.0)
        self.simulator = ECAProbeSimulator(self.coil)
        self.analyzer = ImpedancePlaneAnalyzer()
        self.compensator = LiftOffCompensator()
        self.classifier = DefectClassifier()
        self.readings: List[Tuple[float, float]] = []
        self.defects: List[Dict] = []
    
    def scan(self, positions: List[float],
            defect_depth: float = 0.0):
        """
        Perform scan.
        
        Args:
            positions: Positions
            defect_depth: Defect depth
        """
        self.readings = self.simulator.scan_response(positions, defect_depth)
    
    def analyze(self) -> Dict:
        """
        Analyze readings.
        
        Returns:
            Analysis
        """
        traj = self.analyzer.trajectory(self.readings)
        classification = self.classifier.classify_trajectory(self.readings)
        
        return {
            **traj,
            "classification": classification
        }
    
    def eca_summary(self) -> Dict:
        """Get summary."""
        return {
            "coil_diameter_mm": self.coil.diameter_mm,
            "frequency_Hz": self.coil.frequency_Hz,
            "readings": len(self.readings)
        }
