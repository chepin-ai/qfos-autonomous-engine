"""
Shear Wave Ultrasonic Module
Shear wave propagation, mode conversion, angle beam inspection,
weld defect detection, and root/face crack analysis for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ShearWaveProbe:
    """Shear wave probe."""
    angle_deg: float
    frequency_MHz: float
    diameter_mm: float
    shear_velocity_mm_us: float = 3.23


class SnellLawConverter:
    """
    Mode conversion via Snell's law.
    """
    
    def __init__(self, longitudinal_vel_mm_us: float = 5.9,
                 shear_vel_mm_us: float = 3.23):
        """
        Args:
            longitudinal_vel_mm_us: Longitudinal velocity
            shear_vel_mm_us: Shear velocity
        """
        self.v_l = longitudinal_vel_mm_us
        self.v_s = shear_vel_mm_us
    
    def longitudinal_angle(self, shear_angle_deg: float) -> float:
        """
        Compute longitudinal angle from shear angle.
        
        Args:
            shear_angle_deg: Shear angle
        
        Returns:
            Longitudinal angle
        """
        sin_shear = math.sin(math.radians(shear_angle_deg))
        sin_long = sin_shear * self.v_l / self.v_s
        
        if abs(sin_long) > 1.0:
            return 90.0
        return math.degrees(math.asin(sin_long))
    
    def shear_angle(self, longitudinal_angle_deg: float) -> float:
        """
        Compute shear angle from longitudinal angle.
        
        Args:
            longitudinal_angle_deg: Longitudinal angle
        
        Returns:
            Shear angle
        """
        sin_long = math.sin(math.radians(longitudinal_angle_deg))
        sin_shear = sin_long * self.v_s / self.v_l
        
        if abs(sin_shear) > 1.0:
            return 90.0
        return math.degrees(math.asin(sin_shear))
    
    def critical_angle(self) -> float:
        """
        Compute first critical angle.
        
        Returns:
            Critical angle in degrees
        """
        sin_crit = self.v_s / self.v_l
        if sin_crit > 1.0:
            return 90.0
        return math.degrees(math.asin(sin_crit))


class ShearWavePath:
    """
    Shear wave propagation path.
    """
    
    def __init__(self, probe: ShearWaveProbe):
        """
        Args:
            probe: Probe config
        """
        self.probe = probe
    
    def skip_distance(self, thickness_mm: float) -> float:
        """
        Compute skip distance.
        
        Args:
            thickness_mm: Material thickness
        
        Returns:
            Skip distance
        """
        angle_rad = math.radians(self.probe.angle_deg)
        return 2.0 * thickness_mm * math.tan(angle_rad)
    
    def sound_path(self, thickness_mm: float) -> float:
        """
        Compute sound path for one skip.
        
        Args:
            thickness_mm: Thickness
        
        Returns:
            Sound path
        """
        angle_rad = math.radians(self.probe.angle_deg)
        return 2.0 * thickness_mm / math.cos(angle_rad)
    
    def depth_from_path(self, sound_path_mm: float) -> float:
        """
        Compute depth from sound path.
        
        Args:
            sound_path_mm: Sound path
        
        Returns:
            Depth
        """
        angle_rad = math.radians(self.probe.angle_deg)
        return sound_path_mm * math.cos(angle_rad) / 2.0
    
    def surface_distance(self, sound_path_mm: float) -> float:
        """
        Compute surface distance.
        
        Args:
            sound_path_mm: Sound path
        
        Returns:
            Surface distance
        """
        angle_rad = math.radians(self.probe.angle_deg)
        return sound_path_mm * math.sin(angle_rad)


class WeldDefectDetector:
    """
    Weld defect detection with shear waves.
    """
    
    def __init__(self):
        self.defects: List[Dict] = []
    
    def locate_defect(self, probe_position_mm: float,
                     sound_path_mm: float,
                     probe_angle_deg: float,
                     thickness_mm: float) -> Dict:
        """
        Locate defect in weld.
        
        Args:
            probe_position_mm: Probe position
            sound_path_mm: Sound path
            probe_angle_deg: Probe angle
            thickness_mm: Thickness
        
        Returns:
            Defect location
        """
        angle_rad = math.radians(probe_angle_deg)
        
        # Determine skip
        skip_path = 2.0 * thickness_mm / math.cos(angle_rad)
        num_skips = int(sound_path_mm / skip_path) + 1
        
        # Defect position
        horizontal = probe_position_mm + sound_path_mm * math.sin(angle_rad)
        vertical = sound_path_mm * math.cos(angle_rad)
        
        # Account for reflections
        depth = vertical % (2.0 * thickness_mm)
        if depth > thickness_mm:
            depth = 2.0 * thickness_mm - depth
        
        return {
            "x_mm": horizontal,
            "depth_mm": depth,
            "skip": num_skips,
            "sound_path_mm": sound_path_mm
        }
    
    def classify_defect(self, echo_pattern: List[float],
                       threshold: float = 0.5) -> str:
        """
        Classify defect from echo pattern.
        
        Args:
            echo_pattern: Echo amplitudes
            threshold: Threshold
        
        Returns:
            Classification
        """
        if not echo_pattern:
            return "none"
        
        max_amp = max(echo_pattern)
        num_peaks = sum(1 for e in echo_pattern if e > threshold * max_amp)
        
        if num_peaks == 1:
            return "porosity"
        elif num_peaks == 2:
            return "crack"
        elif num_peaks >= 3:
            return "lack_of_fusion"
        else:
            return "none"


class ShearWaveSystem:
    """
    Unified shear wave controller.
    """
    
    def __init__(self, angle_deg: float = 45.0,
                 frequency_MHz: float = 5.0):
        """
        Args:
            angle_deg: Probe angle
            frequency_MHz: Frequency
        """
        self.probe = ShearWaveProbe(angle_deg, frequency_MHz, 10.0)
        self.converter = SnellLawConverter()
        self.path = ShearWavePath(self.probe)
        self.defect_detector = WeldDefectDetector()
        self.measurements: List[Dict] = []
    
    def scan(self, probe_position_mm: float,
            echo_times_us: List[float],
            thickness_mm: float = 10.0):
        """
        Perform scan.
        
        Args:
            probe_position_mm: Position
            echo_times_us: Echo times
            thickness_mm: Thickness
        """
        for t in echo_times_us:
            path_mm = t * self.probe.shear_velocity_mm_us
            location = self.defect_detector.locate_defect(
                probe_position_mm, path_mm, self.probe.angle_deg, thickness_mm
            )
            self.measurements.append(location)
    
    def analyze_defects(self, echo_patterns: List[List[float]]) -> List[str]:
        """
        Analyze defects.
        
        Args:
            echo_patterns: Echo patterns
        
        Returns:
            Classifications
        """
        return [self.defect_detector.classify_defect(p) for p in echo_patterns]
    
    def shear_wave_summary(self) -> Dict:
        """Get summary."""
        return {
            "angle_deg": self.probe.angle_deg,
            "frequency_MHz": self.probe.frequency_MHz,
            "critical_angle_deg": self.converter.critical_angle(),
            "measurements": len(self.measurements),
            "skip_distance_mm": self.path.skip_distance(10.0)
        }
