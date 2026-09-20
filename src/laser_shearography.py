"""
Laser Shearography Module
Optical NDT with shearography interferometry, strain measurement,
fringe pattern analysis, and defect detection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ShearDirection(Enum):
    """Shear direction."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    DIAGONAL = "diagonal"


@dataclass
class Shearogram:
    """Shearography fringe pattern."""
    x: float
    y: float
    intensity: float
    phase: float
    shear_dx: float = 0.0
    shear_dy: float = 0.0


class ShearographyOptics:
    """
    Shearography optical system.
    """
    
    def __init__(self, wavelength_nm: float = 532.0,
                 shear_pixels: int = 5):
        """
        Args:
            wavelength_nm: Laser wavelength
            shear_pixels: Shear displacement
        """
        self.wavelength = wavelength_nm * 1e-9  # meters
        self.shear = shear_pixels
    
    def optical_path_difference(self, displacement_m: float,
                                angle_deg: float = 0.0) -> float:
        """
        Compute optical path difference.
        
        Args:
            displacement_m: Out-of-plane displacement
            angle_deg: Illumination angle
        
        Returns:
            OPD in meters
        """
        angle_rad = math.radians(angle_deg)
        # OPD = displacement * (1 + cos(theta))
        return displacement_m * (1.0 + math.cos(angle_rad))
    
    def phase_shift(self, opd_m: float) -> float:
        """
        Compute phase shift from OPD.
        
        Args:
            opd_m: OPD
        
        Returns:
            Phase in radians
        """
        return (2.0 * math.pi * opd_m / self.wavelength) % (2.0 * math.pi)
    
    def fringe_order(self, phase: float) -> int:
        """
        Compute fringe order.
        
        Args:
            phase: Phase
        
        Returns:
            Fringe order
        """
        return int(phase / (2.0 * math.pi))


class FringeAnalyzer:
    """
    Fringe pattern analysis.
    """
    
    def __init__(self):
        self.patterns: List[List[float]] = []
    
    def wrap_phase(self, wrapped: List[List[float]]) -> List[List[float]]:
        """
        Phase unwrapping (simplified).
        
        Args:
            wrapped: Wrapped phase
        
        Returns:
            Unwrapped phase
        """
        if not wrapped:
            return []
        
        h = len(wrapped)
        w = len(wrapped[0]) if h > 0 else 0
        unwrapped = [row[:] for row in wrapped]
        
        for y in range(1, h):
            for x in range(w):
                diff = unwrapped[y][x] - unwrapped[y-1][x]
                if diff > math.pi:
                    unwrapped[y][x] -= 2.0 * math.pi
                elif diff < -math.pi:
                    unwrapped[y][x] += 2.0 * math.pi
        
        return unwrapped
    
    def fringe_contrast(self, pattern: List[List[float]]) -> float:
        """
        Compute fringe contrast.
        
        Args:
            pattern: Intensity pattern
        
        Returns:
            Contrast (0-1)
        """
        if not pattern:
            return 0.0
        
        flat = [val for row in pattern for val in row]
        if not flat:
            return 0.0
        
        max_i = max(flat)
        min_i = min(flat)
        
        if max_i + min_i == 0:
            return 0.0
        
        return (max_i - min_i) / (max_i + min_i)
    
    def defect_indicator(self, pattern: List[List[float]],
                        threshold: float = 0.3) -> List[Tuple[int, int]]:
        """
        Detect defect regions from fringe anomalies.
        
        Args:
            pattern: Fringe pattern
            threshold: Anomaly threshold
        
        Returns:
            Defect coordinates
        """
        defects = []
        h = len(pattern)
        w = len(pattern[0]) if h > 0 else 0
        
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                # Laplacian for anomaly detection
                lap = (pattern[y][x+1] + pattern[y][x-1] +
                       pattern[y+1][x] + pattern[y-1][x] - 4.0 * pattern[y][x])
                if abs(lap) > threshold:
                    defects.append((x, y))
        
        return defects


class StrainMapper:
    """
    Strain computation from shearography data.
    """
    
    def __init__(self, pixel_size_mm: float = 1.0):
        """
        Args:
            pixel_size_mm: Pixel size
        """
        self.pixel_size = pixel_size_mm
    
    def out_of_plane_strain(self, phase_map: List[List[float]],
                           shear_mm: float = 1.0) -> List[List[float]]:
        """
        Compute out-of-plane strain.
        
        Args:
            phase_map: Phase map
            shear_mm: Shear distance
        
        Returns:
            Strain map
        """
        if not phase_map:
            return []
        
        h = len(phase_map)
        w = len(phase_map[0]) if h > 0 else 0
        strain = [[0.0] * w for _ in range(h)]
        
        for y in range(h):
            for x in range(1, w):
                d_phase = phase_map[y][x] - phase_map[y][x-1]
                strain[y][x] = d_phase / (shear_mm * 1e-3)  # per meter
        
        return strain
    
    def max_strain(self, strain_map: List[List[float]]) -> float:
        """
        Find maximum strain.
        
        Args:
            strain_map: Strain map
        
        Returns:
            Max strain
        """
        if not strain_map:
            return 0.0
        flat = [abs(v) for row in strain_map for v in row]
        return max(flat) if flat else 0.0


class LaserShearography:
    """
    Unified laser shearography controller.
    """
    
    def __init__(self):
        self.optics = ShearographyOptics()
        self.fringe = FringeAnalyzer()
        self.strain = StrainMapper()
        self.defects: List[Tuple[int, int]] = []
        self.inspections: List[Dict] = []
    
    def inspect(self, displacement_field_m: List[List[float]],
               illumination_angle_deg: float = 0.0) -> Dict:
        """
        Run shearography inspection.
        
        Args:
            displacement_field_m: Displacement field
            illumination_angle_deg: Angle
        
        Returns:
            Inspection report
        """
        # Compute phase map
        phase_map = []
        for row in displacement_field_m:
            phase_row = []
            for disp in row:
                opd = self.optics.optical_path_difference(disp, illumination_angle_deg)
                phase = self.optics.phase_shift(opd)
                phase_row.append(phase)
            phase_map.append(phase_row)
        
        # Generate fringe pattern
        fringe_pattern = []
        for row in phase_map:
            fringe_row = [0.5 + 0.5 * math.cos(p) for p in row]
            fringe_pattern.append(fringe_row)
        
        # Analyze fringes
        contrast = self.fringe.fringe_contrast(fringe_pattern)
        self.defects = self.fringe.defect_indicator(fringe_pattern, 0.5)
        
        # Compute strain
        strain_map = self.strain.out_of_plane_strain(phase_map)
        max_strain = self.strain.max_strain(strain_map)
        
        report = {
            "contrast": contrast,
            "defects": len(self.defects),
            "max_strain": max_strain,
            "pass": len(self.defects) == 0
        }
        self.inspections.append(report)
        return report
    
    def shearography_summary(self) -> Dict:
        """Get summary."""
        if not self.inspections:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.inspections),
            "pass_count": sum(1 for r in self.inspections if r["pass"]),
            "total_defects": sum(r["defects"] for r in self.inspections)
        }
