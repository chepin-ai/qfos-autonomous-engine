"""
Time-of-Flight Diffraction Module
TOFD ultrasonic NDT with A-scan/D-scan/B-scan processing, defect tip
diffraction analysis, and lateral wave tracking for autonomous inspection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TOFDProbe:
    """TOFD probe pair configuration."""
    separation_mm: float
    frequency_MHz: float
    angle_deg: float
    velocity_mm_us: float = 5.9


class AScanProcessor:
    """
    A-scan signal processing for TOFD.
    """
    
    def __init__(self, sample_rate_MHz: float = 100.0):
        """
        Args:
            sample_rate_MHz: Sample rate
        """
        self.fs = sample_rate_MHz
    
    def envelope(self, signal: List[float]) -> List[float]:
        """
        Compute signal envelope.
        
        Args:
            signal: Input
        
        Returns:
            Envelope
        """
        # Simplified: absolute value
        return [abs(v) for v in signal]
    
    def find_peaks(self, signal: List[float],
                  threshold: float = 0.1) -> List[Tuple[int, float]]:
        """
        Find peaks in signal.
        
        Args:
            signal: Signal
            threshold: Threshold
        
        Returns:
            (index, amplitude) list
        """
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > threshold and signal[i] > signal[i - 1] and signal[i] > signal[i + 1]:
                peaks.append((i, signal[i]))
        return peaks
    
    def time_to_depth(self, time_us: float,
                     velocity_mm_us: float = 5.9) -> float:
        """
        Convert time to depth.
        
        Args:
            time_us: Time
            velocity_mm_us: Velocity
        
        Returns:
            Depth in mm
        """
        return time_us * velocity_mm_us / 2.0


class DiffractionAnalyzer:
    """
    Defect tip diffraction analysis.
    """
    
    def __init__(self, probe: TOFDProbe):
        """
        Args:
            probe: Probe config
        """
        self.probe = probe
    
    def tip_depth(self, time_us: float) -> float:
        """
        Compute defect tip depth.
        
        Args:
            time_us: Diffraction time
        
        Returns:
            Depth in mm
        """
        # Path: probe -> tip -> receiver
        # Path length = sqrt((s/2)^2 + d^2) * 2
        # time = path_length / velocity
        # d = sqrt((time * v / 2)^2 - (s/2)^2)
        half_path = time_us * self.probe.velocity_mm_us / 2.0
        half_sep = self.probe.separation_mm / 2.0
        
        d2 = half_path**2 - half_sep**2
        if d2 < 0:
            return 0.0
        return math.sqrt(d2)
    
    def lateral_wave_time(self) -> float:
        """
        Compute lateral wave arrival time.
        
        Returns:
            Time in us
        """
        return self.probe.separation_mm / self.probe.velocity_mm_us
    
    def backwall_time(self, thickness_mm: float) -> float:
        """
        Compute backwall echo time.
        
        Args:
            thickness_mm: Thickness
        
        Returns:
            Time in us
        """
        # Path: probe -> backwall -> receiver
        half_sep = self.probe.separation_mm / 2.0
        path = 2.0 * math.sqrt(half_sep**2 + thickness_mm**2)
        return path / self.probe.velocity_mm_us
    
    def classify_indication(self, time_us: float,
                           thickness_mm: float) -> str:
        """
        Classify indication.
        
        Args:
            time_us: Arrival time
            thickness_mm: Material thickness
        
        Returns:
            Classification
        """
        lateral = self.lateral_wave_time()
        backwall = self.backwall_time(thickness_mm)
        
        if abs(time_us - lateral) < 0.5:
            return "lateral_wave"
        elif abs(time_us - backwall) < 1.0:
            return "backwall"
        elif time_us > lateral and time_us < backwall:
            return "defect"
        else:
            return "unknown"


class ScanConverter:
    """
    Convert A-scans to D-scan and B-scan images.
    """
    
    def __init__(self):
        self.d_scan: List[List[float]] = []
        self.b_scan: List[List[float]] = []
    
    def build_d_scan(self, a_scans: List[List[float]]) -> List[List[float]]:
        """
        Build D-scan (depth vs position).
        
        Args:
            a_scans: A-scans at each position
        
        Returns:
            D-scan image
        """
        if not a_scans:
            return []
        
        max_len = max(len(s) for s in a_scans)
        d_scan = []
        
        for time_idx in range(max_len):
            row = []
            for scan in a_scans:
                if time_idx < len(scan):
                    row.append(abs(scan[time_idx]))
                else:
                    row.append(0.0)
            d_scan.append(row)
        
        self.d_scan = d_scan
        return d_scan
    
    def build_b_scan(self, a_scans: List[List[float]],
                    probe_positions_mm: List[float]) -> List[List[float]]:
        """
        Build B-scan (position vs time).
        
        Args:
            a_scans: A-scans
            probe_positions_mm: Positions
        
        Returns:
            B-scan image
        """
        if not a_scans:
            return []
        
        # Transpose of D-scan
        b_scan = []
        for scan_idx, scan in enumerate(a_scans):
            row = [abs(v) for v in scan]
            b_scan.append(row)
        
        self.b_scan = b_scan
        return b_scan


class TOFDSystem:
    """
    Unified TOFD controller.
    """
    
    def __init__(self, separation_mm: float = 20.0,
                 frequency_MHz: float = 5.0,
                 angle_deg: float = 60.0):
        """
        Args:
            separation_mm: Probe separation
            frequency_MHz: Frequency
            angle_deg: Angle
        """
        self.probe = TOFDProbe(separation_mm, frequency_MHz, angle_deg)
        self.a_scan = AScanProcessor()
        self.diffraction = DiffractionAnalyzer(self.probe)
        self.scan_converter = ScanConverter()
        self.a_scans: List[List[float]] = []
        self.indications: List[Dict] = []
    
    def record_a_scan(self, signal: List[float]):
        """
        Record A-scan.
        
        Args:
            signal: Signal
        """
        self.a_scans.append(signal)
    
    def analyze(self, thickness_mm: float = 10.0) -> List[Dict]:
        """
        Analyze all A-scans.
        
        Args:
            thickness_mm: Material thickness
        
        Returns:
            Indications
        """
        for pos_idx, signal in enumerate(self.a_scans):
            env = self.a_scan.envelope(signal)
            peaks = self.a_scan.find_peaks(env, 0.2)
            
            for idx, amp in peaks:
                time_us = idx / self.a_scan.fs
                depth = self.diffraction.tip_depth(time_us)
                classification = self.diffraction.classify_indication(time_us, thickness_mm)
                
                self.indications.append({
                    "position": pos_idx,
                    "time_us": time_us,
                    "amplitude": amp,
                    "depth_mm": depth,
                    "type": classification
                })
        
        return self.indications
    
    def generate_d_scan(self) -> List[List[float]]:
        """
        Generate D-scan.
        
        Returns:
            D-scan
        """
        return self.scan_converter.build_d_scan(self.a_scans)
    
    def generate_b_scan(self) -> List[List[float]]:
        """
        Generate B-scan.
        
        Returns:
            B-scan
        """
        return self.scan_converter.build_b_scan(self.a_scans, [])
    
    def tofd_summary(self) -> Dict:
        """Get summary."""
        defects = [i for i in self.indications if i["type"] == "defect"]
        return {
            "scans": len(self.a_scans),
            "indications": len(self.indications),
            "defects": len(defects),
            "probe_separation_mm": self.probe.separation_mm
        }
