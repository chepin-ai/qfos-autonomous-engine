"""
Ultrasonic Inspection Module
Time-of-flight measurement, thickness gauging, defect detection,
and attenuation analysis for autonomous non-destructive testing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DefectType(Enum):
    """Types of defects detected by ultrasound."""
    NONE = "none"
    VOID = "void"
    CRACK = "crack"
    INCLUSION = "inclusion"
    DELAMINATION = "delamination"
    CORROSION = "corrosion"


@dataclass
class AScan:
    """A-scan signal from a single transducer position."""
    time_us: float
    amplitude: float
    gate_start_us: float = 0.0
    gate_end_us: float = 100.0


class TimeOfFlight:
    """
    Compute time-of-flight and derive thickness.
    """
    
    def __init__(self, material_velocity_m_s: float = 5900.0):
        """
        Args:
            material_velocity_m_s: Sound velocity in material (steel default)
        """
        self.v = material_velocity_m_s
    
    def thickness(self, tof_us: float) -> float:
        """
        Compute thickness from time-of-flight.
        
        Args:
            tof_us: Time-of-flight in microseconds
        
        Returns:
            Thickness in meters
        """
        # Round-trip time: thickness = v * t / 2
        return self.v * tof_us * 1e-6 / 2.0
    
    def time_of_flight(self, thickness_m: float) -> float:
        """
        Compute time-of-flight from thickness.
        
        Args:
            thickness_m: Thickness in meters
        
        Returns:
            Time-of-flight in microseconds
        """
        return 2.0 * thickness_m / self.v * 1e6
    
    def set_material(self, name: str):
        """
        Set material by name.
        
        Args:
            name: Material name (steel, aluminum, water, air)
        """
        velocities = {
            "steel": 5900.0,
            "aluminum": 6320.0,
            "water": 1480.0,
            "air": 343.0,
            "glass": 5660.0,
            "copper": 4660.0
        }
        self.v = velocities.get(name.lower(), 5900.0)


class DefectDetector:
    """
    Detect defects from A-scan signals.
    """
    
    def __init__(self, amplitude_threshold_percent: float = 50.0):
        """
        Args:
            amplitude_threshold_percent: Threshold as % of backwall amplitude
        """
        self.threshold = amplitude_threshold_percent
    
    def detect(self, scans: List[AScan],
              backwall_amplitude: float = 1.0) -> List[Dict]:
        """
        Detect defects in scans.
        
        Args:
            scans: A-scan signals
            backwall_amplitude: Backwall echo amplitude
        
        Returns:
            Defect list
        """
        threshold = backwall_amplitude * self.threshold / 100.0
        defects = []
        
        for scan in scans:
            if scan.amplitude > threshold and scan.gate_start_us < scan.time_us < scan.gate_end_us:
                defects.append({
                    "time_us": scan.time_us,
                    "amplitude": scan.amplitude,
                    "type": DefectType.VOID.value
                })
        
        return defects
    
    def depth_from_tof(self, tof_us: float,
                      velocity_m_s: float) -> float:
        """
        Compute defect depth from TOF.
        
        Args:
            tof_us: Time-of-flight
            velocity_m_s: Sound velocity
        
        Returns:
            Depth in meters
        """
        return velocity_m_s * tof_us * 1e-6 / 2.0


class AttenuationAnalyzer:
    """
    Analyze signal attenuation.
    """
    
    def __init__(self):
        pass
    
    def attenuation_coefficient(self, amplitude1: float,
                                amplitude2: float,
                                distance_m: float) -> float:
        """
        Compute attenuation coefficient in dB/m.
        
        Args:
            amplitude1: Amplitude at position 1
            amplitude2: Amplitude at position 2
            distance_m: Distance between positions
        
        Returns:
            Attenuation coefficient
        """
        if amplitude1 <= 0 or amplitude2 <= 0 or distance_m <= 0:
            return 0.0
        return 20.0 * math.log10(amplitude1 / amplitude2) / distance_m
    
    def predicted_amplitude(self, initial_amplitude: float,
                           attenuation_db_m: float,
                           distance_m: float) -> float:
        """
        Predict amplitude at distance.
        
        Args:
            initial_amplitude: Initial amplitude
            attenuation_db_m: Attenuation coefficient
            distance_m: Distance
        
        Returns:
            Predicted amplitude
        """
        db_loss = attenuation_db_m * distance_m
        return initial_amplitude * 10**(-db_loss / 20.0)
    
    def grain_size_estimate(self, attenuation_db_m: float,
                           frequency_MHz: float) -> float:
        """
        Estimate average grain size from attenuation.
        
        Args:
            attenuation_db_m: Attenuation
            frequency_MHz: Frequency
        
        Returns:
            Estimated grain size in microns
        """
        # Simplified model: attenuation proportional to f^4 * D^3
        if frequency_MHz <= 0:
            return 0.0
        return (attenuation_db_m / (frequency_MHz**4))**(1.0/3.0)


class ThicknessGauge:
    """
    Measure material thickness via ultrasound.
    """
    
    def __init__(self, velocity_m_s: float = 5900.0):
        """
        Args:
            velocity_m_s: Sound velocity
        """
        self.tof = TimeOfFlight(velocity_m_s)
        self.measurements: List[float] = []
    
    def measure(self, tof_us: float) -> float:
        """
        Measure thickness.
        
        Args:
            tof_us: Time-of-flight
        
        Returns:
            Thickness in mm
        """
        t = self.tof.thickness(tof_us) * 1000.0  # m to mm
        self.measurements.append(t)
        return t
    
    def average_thickness(self) -> float:
        """
        Compute average thickness.
        
        Returns:
            Average in mm
        """
        if not self.measurements:
            return 0.0
        return sum(self.measurements) / len(self.measurements)
    
    def thickness_variation(self) -> float:
        """
        Compute thickness variation (max - min).
        
        Returns:
            Variation in mm
        """
        if not self.measurements:
            return 0.0
        return max(self.measurements) - min(self.measurements)
    
    def within_tolerance(self, nominal_mm: float,
                        tolerance_mm: float = 0.1) -> bool:
        """
        Check if all measurements within tolerance.
        
        Args:
            nominal_mm: Nominal thickness
            tolerance_mm: Allowed tolerance
        
        Returns:
            True if all pass
        """
        if not self.measurements:
            return False
        return all(abs(m - nominal_mm) <= tolerance_mm for m in self.measurements)


class UltrasonicInspection:
    """
    Unified ultrasonic inspection controller.
    """
    
    def __init__(self):
        self.tof = TimeOfFlight()
        self.defect = DefectDetector()
        self.attenuation = AttenuationAnalyzer()
        self.gauge = ThicknessGauge()
        self.inspection_results: List[Dict] = []
    
    def inspect(self, scans: List[AScan],
               material: str = "steel") -> Dict:
        """
        Run ultrasonic inspection.
        
        Args:
            scans: A-scan data
            material: Material name
        
        Returns:
            Inspection report
        """
        self.tof.set_material(material)
        self.gauge.tof.set_material(material)
        
        # Find backwall echo (assume max amplitude in gate)
        gated = [s for s in scans if s.gate_start_us < s.time_us < s.gate_end_us]
        backwall = max((s.amplitude for s in gated), default=1.0)
        
        defects = self.defect.detect(scans, backwall)
        
        # Measure thickness from backwall TOF
        backwall_scan = max(gated, key=lambda s: s.amplitude, default=None)
        thickness_mm = 0.0
        if backwall_scan:
            thickness_mm = self.gauge.measure(backwall_scan.time_us)
        
        report = {
            "material": material,
            "velocity_m_s": self.tof.v,
            "num_scans": len(scans),
            "defects_found": len(defects),
            "thickness_mm": thickness_mm,
            "backwall_amplitude": backwall,
            "pass": len(defects) == 0
        }
        self.inspection_results.append(report)
        return report
    
    def summary(self) -> Dict:
        """Get inspection summary."""
        if not self.inspection_results:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.inspection_results),
            "pass_count": sum(1 for r in self.inspection_results if r["pass"]),
            "total_defects": sum(r["defects_found"] for r in self.inspection_results)
        }
