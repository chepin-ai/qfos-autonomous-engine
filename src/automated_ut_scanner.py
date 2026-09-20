"""
Automated UT Scanner Module
Robotic ultrasonic scanning path planning, encoder tracking,
coverage mapping, and defect reporting for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ScanPattern(Enum):
    """Scan pattern types."""
    RASTER = "raster"
    SPIRAL = "spiral"
    SECTOR = "sector"
    MANUAL = "manual"


@dataclass
class ScanPoint:
    """Single scan position."""
    x_mm: float
    y_mm: float
    z_mm: float = 0.0
    encoder_x: float = 0.0
    encoder_y: float = 0.0


class UTProbe:
    """
    Ultrasonic probe model.
    """
    
    def __init__(self, probe_id: int,
                 diameter_mm: float = 10.0,
                 frequency_MHz: float = 5.0):
        """
        Args:
            probe_id: Probe ID
            diameter_mm: Element diameter
            frequency_MHz: Frequency
        """
        self.probe_id = probe_id
        self.diameter = diameter_mm
        self.frequency = frequency_MHz
        self.wavelength_mm = 1.5 / frequency_MHz  # In steel
    
    def beam_spread_deg(self) -> float:
        """
        Compute beam spread.
        
        Returns:
            Spread in degrees
        """
        # sin(theta) ~ 1.22 * lambda / D
        spread_rad = math.asin(min(1.0, 1.22 * self.wavelength_mm / self.diameter))
        return math.degrees(spread_rad)
    
    def near_field_mm(self) -> float:
        """
        Compute near field length.
        
        Returns:
            Near field length
        """
        return self.diameter ** 2 / (4.0 * self.wavelength_mm)


class ScanPathPlanner:
    """
    Scan path planning for automated UT.
    """
    
    def __init__(self, scan_area_mm: Tuple[float, float] = (500.0, 500.0),
                 step_mm: float = 5.0):
        """
        Args:
            scan_area_mm: (width, height)
            step_mm: Index step
        """
        self.area = scan_area_mm
        self.step = step_mm
        self.pattern = ScanPattern.RASTER
    
    def raster_path(self) -> List[ScanPoint]:
        """
        Generate raster scan path.
        
        Returns:
            Path points
        """
        points = []
        width, height = self.area
        nx = int(width / self.step) + 1
        ny = int(height / self.step) + 1
        
        for yi in range(ny):
            y = yi * self.step
            # Alternate direction for efficiency
            x_range = range(nx) if yi % 2 == 0 else range(nx - 1, -1, -1)
            for xi in x_range:
                x = xi * self.step
                points.append(ScanPoint(x, y))
        
        return points
    
    def spiral_path(self, center_mm: Tuple[float, float] = (250.0, 250.0),
                   max_radius_mm: float = 250.0) -> List[ScanPoint]:
        """
        Generate spiral scan path.
        
        Args:
            center_mm: Center
            max_radius_mm: Max radius
        
        Returns:
            Path points
        """
        points = []
        cx, cy = center_mm
        radius = 0.0
        angle = 0.0
        
        while radius <= max_radius_mm:
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append(ScanPoint(x, y))
            
            # Increment
            d_angle = self.step / max(radius, self.step)
            angle += d_angle
            radius += self.step * d_angle / (2.0 * math.pi)
        
        return points
    
    def coverage_percent(self, probe_diameter_mm: float = 10.0) -> float:
        """
        Compute scan coverage.
        
        Args:
            probe_diameter_mm: Probe diameter
        
        Returns:
            Coverage percentage
        """
        width, height = self.area
        area_total = width * height
        
        # Effective coverage per point (circular area)
        area_per_point = math.pi * (probe_diameter_mm / 2.0) ** 2
        num_points = (width / self.step + 1) * (height / self.step + 1)
        
        coverage = area_per_point * num_points / area_total
        return min(100.0, coverage * 100.0)


class EncoderTracker:
    """
    Encoder position tracking.
    """
    
    def __init__(self, counts_per_mm: float = 100.0):
        """
        Args:
            counts_per_mm: Encoder resolution
        """
        self.cpm = counts_per_mm
        self.x_counts = 0
        self.y_counts = 0
    
    def update(self, x_counts: int, y_counts: int):
        """
        Update encoder counts.
        
        Args:
            x_counts: X counts
            y_counts: Y counts
        """
        self.x_counts = x_counts
        self.y_counts = y_counts
    
    def position_mm(self) -> Tuple[float, float]:
        """
        Get position in mm.
        
        Returns:
            (x_mm, y_mm)
        """
        return (self.x_counts / self.cpm, self.y_counts / self.cpm)
    
    def reset(self):
        """Reset encoders."""
        self.x_counts = 0
        self.y_counts = 0


class DefectReporter:
    """
    Defect reporting from scan data.
    """
    
    def __init__(self):
        self.defects: List[Dict] = []
    
    def add_defect(self, x_mm: float, y_mm: float,
                   amplitude_dB: float,
                   depth_mm: float = 0.0):
        """
        Add defect finding.
        
        Args:
            x_mm: X position
            y_mm: Y position
            amplitude_dB: Signal amplitude
            depth_mm: Depth
        """
        severity = self._severity_from_amplitude(amplitude_dB)
        self.defects.append({
            "x_mm": x_mm,
            "y_mm": y_mm,
            "amplitude_dB": amplitude_dB,
            "depth_mm": depth_mm,
            "severity": severity
        })
    
    def _severity_from_amplitude(self, amplitude_dB: float) -> str:
        """
        Classify severity.
        
        Args:
            amplitude_dB: Amplitude
        
        Returns:
            Severity level
        """
        if amplitude_dB >= 20.0:
            return "critical"
        elif amplitude_dB >= 10.0:
            return "major"
        elif amplitude_dB >= 5.0:
            return "minor"
        return "indication"
    
    def defect_count(self) -> int:
        """
        Get defect count.
        
        Returns:
            Count
        """
        return len(self.defects)
    
    def critical_count(self) -> int:
        """
        Get critical defect count.
        
        Returns:
            Count
        """
        return sum(1 for d in self.defects if d["severity"] == "critical")


class AutomatedUTScanner:
    """
    Unified automated UT scanner controller.
    """
    
    def __init__(self, scan_area_mm: Tuple[float, float] = (500.0, 500.0)):
        """
        Args:
            scan_area_mm: Scan area
        """
        self.planner = ScanPathPlanner(scan_area_mm)
        self.encoder = EncoderTracker()
        self.reporter = DefectReporter()
        self.probe = UTProbe(0)
        self.path: List[ScanPoint] = []
        self.scan_data: List[Dict] = []
    
    def plan_raster(self, step_mm: float = 5.0):
        """
        Plan raster scan.
        
        Args:
            step_mm: Step size
        """
        self.planner.step = step_mm
        self.path = self.planner.raster_path()
    
    def plan_spiral(self, center_mm: Tuple[float, float] = (250.0, 250.0)):
        """
        Plan spiral scan.
        
        Args:
            center_mm: Center
        """
        self.path = self.planner.spiral_path(center_mm)
    
    def record_point(self, x_counts: int, y_counts: int,
                    amplitude_dB: float, depth_mm: float = 0.0):
        """
        Record scan point.
        
        Args:
            x_counts: X encoder
            y_counts: Y encoder
            amplitude_dB: Amplitude
            depth_mm: Depth
        """
        self.encoder.update(x_counts, y_counts)
        x_mm, y_mm = self.encoder.position_mm()
        
        if amplitude_dB >= 5.0:
            self.reporter.add_defect(x_mm, y_mm, amplitude_dB, depth_mm)
        
        self.scan_data.append({
            "x_mm": x_mm,
            "y_mm": y_mm,
            "amplitude_dB": amplitude_dB
        })
    
    def scanner_summary(self) -> Dict:
        """Get scanner summary."""
        return {
            "path_points": len(self.path),
            "scan_points": len(self.scan_data),
            "defects": self.reporter.defect_count(),
            "critical": self.reporter.critical_count(),
            "coverage": self.planner.coverage_percent(self.probe.diameter)
        }
