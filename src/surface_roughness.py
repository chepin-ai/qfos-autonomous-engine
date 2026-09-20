"""
Surface Roughness Module
Surface texture measurement: Ra, Rz, Rq, texture direction,
and flatness assessment for autonomous quality inspection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RoughnessStandard(Enum):
    """Surface roughness standards."""
    ISO = "iso"
    ASME = "asme"
    JIS = "jis"


@dataclass
class ProfilePoint:
    """A single surface profile point."""
    x_mm: float
    z_um: float  # Height in micrometers


class ProfileFilter:
    """
    Filter surface profile (Gaussian long-wavelength removal).
    """
    
    def __init__(self, cutoff_um: float = 800.0):
        """
        Args:
            cutoff_um: Filter cutoff wavelength
        """
        self.cutoff = cutoff_um
    
    def remove_form(self, points: List[ProfilePoint]) -> List[ProfilePoint]:
        """
        Remove form error (linear trend).
        
        Args:
            points: Raw profile
        
        Returns:
            Detrended profile
        """
        if len(points) < 2:
            return points
        
        n = len(points)
        x_avg = sum(p.x_mm for p in points) / n
        z_avg = sum(p.z_um for p in points) / n
        
        # Linear regression
        num = sum((p.x_mm - x_avg) * (p.z_um - z_avg) for p in points)
        den = sum((p.x_mm - x_avg)**2 for p in points)
        slope = num / den if den != 0 else 0.0
        intercept = z_avg - slope * x_avg
        
        return [ProfilePoint(p.x_mm, p.z_um - (slope * p.x_mm + intercept))
                for p in points]
    
    def roughness_profile(self, points: List[ProfilePoint]) -> List[ProfilePoint]:
        """
        Extract roughness profile (remove waviness).
        
        Args:
            points: Filtered profile
        
        Returns:
            Roughness profile
        """
        # Simplified: subtract moving average as waviness
        window = max(3, len(points) // 10)
        result = []
        
        for i in range(len(points)):
            start = max(0, i - window // 2)
            end = min(len(points), i + window // 2 + 1)
            avg = sum(points[j].z_um for j in range(start, end)) / (end - start)
            result.append(ProfilePoint(points[i].x_mm, points[i].z_um - avg))
        
        return result


class RoughnessParameters:
    """
    Compute ISO surface roughness parameters.
    """
    
    def __init__(self, profile: List[ProfilePoint]):
        """
        Args:
            profile: Roughness profile
        """
        self.profile = profile
        self.heights = [p.z_um for p in profile]
        self.n = len(self.heights)
    
    def ra(self) -> float:
        """
        Arithmetic mean roughness Ra.
        
        Returns:
            Ra in micrometers
        """
        if self.n == 0:
            return 0.0
        return sum(abs(h) for h in self.heights) / self.n
    
    def rq(self) -> float:
        """
        Root mean square roughness Rq.
        
        Returns:
            Rq in micrometers
        """
        if self.n == 0:
            return 0.0
        return math.sqrt(sum(h**2 for h in self.heights) / self.n)
    
    def rz(self) -> float:
        """
        Maximum height roughness Rz (ISO: average of 5 sampling lengths).
        
        Returns:
            Rz in micrometers
        """
        if self.n == 0:
            return 0.0
        
        # Divide into 5 segments
        seg_len = max(1, self.n // 5) if self.n >= 5 else self.n
        rz_values = []
        
        for i in range(5):
            start = i * seg_len
            end = min((i + 1) * seg_len, self.n)
            segment = self.heights[start:end]
            if segment:
                rz_values.append(max(segment) - min(segment))
        
        return sum(rz_values) / len(rz_values) if rz_values else 0.0
    
    def rmax(self) -> float:
        """
        Maximum peak-to-valley height.
        
        Returns:
            Rmax in micrometers
        """
        if self.n == 0:
            return 0.0
        return max(self.heights) - min(self.heights)
    
    def skewness(self) -> float:
        """
        Skewness Rsk (asymmetry of profile).
        
        Returns:
            Skewness
        """
        if self.n == 0:
            return 0.0
        rq = self.rq()
        if rq == 0:
            return 0.0
        return sum((h / rq)**3 for h in self.heights) / self.n
    
    def kurtosis(self) -> float:
        """
        Kurtosis Rku (peak sharpness).
        
        Returns:
            Kurtosis
        """
        if self.n == 0:
            return 0.0
        rq = self.rq()
        if rq == 0:
            return 0.0
        return sum((h / rq)**4 for h in self.heights) / self.n


class TextureDirection:
    """
    Analyze surface texture direction.
    """
    
    def __init__(self):
        pass
    
    def dominant_direction(self, points_2d: List[Tuple[float, float]]) -> float:
        """
        Compute dominant texture direction.
        
        Args:
            points_2d: List of (x, z) points
        
        Returns:
            Direction angle in degrees
        """
        if len(points_2d) < 2:
            return 0.0
        
        # PCA-like: compute covariance
        n = len(points_2d)
        x_avg = sum(p[0] for p in points_2d) / n
        z_avg = sum(p[1] for p in points_2d) / n
        
        cxx = sum((p[0] - x_avg)**2 for p in points_2d) / n
        czz = sum((p[1] - z_avg)**2 for p in points_2d) / n
        cxz = sum((p[0] - x_avg) * (p[1] - z_avg) for p in points_2d) / n
        
        # Dominant direction from covariance
        if cxx + czz == 0:
            return 0.0
        
        angle = 0.5 * math.atan2(2.0 * cxz, cxx - czz)
        return math.degrees(angle)
    
    def isotropic_index(self, points_2d: List[Tuple[float, float]]) -> float:
        """
        Compute isotropy index (0=anisotropic, 1=isotropic).
        
        Args:
            points_2d: 2D profile points
        
        Returns:
            Isotropy index
        """
        if len(points_2d) < 2:
            return 1.0
        
        n = len(points_2d)
        x_avg = sum(p[0] for p in points_2d) / n
        z_avg = sum(p[1] for p in points_2d) / n
        
        cxx = sum((p[0] - x_avg)**2 for p in points_2d) / n
        czz = sum((p[1] - z_avg)**2 for p in points_2d) / n
        
        if cxx + czz == 0:
            return 1.0
        
        return min(cxx, czz) / max(cxx, czz)


class FlatnessChecker:
    """
    Check surface flatness.
    """
    
    def __init__(self, tolerance_um: float = 10.0):
        """
        Args:
            tolerance_um: Flatness tolerance
        """
        self.tolerance = tolerance_um
    
    def flatness_error(self, points: List[ProfilePoint]) -> float:
        """
        Compute flatness error (max deviation from least-squares plane).
        
        Args:
            points: 3D points (using x_mm, z_um)
        
        Returns:
            Flatness error in micrometers
        """
        if len(points) < 3:
            return 0.0
        
        heights = [p.z_um for p in points]
        return max(heights) - min(heights)
    
    def check_flatness(self, points: List[ProfilePoint]) -> bool:
        """
        Check if within tolerance.
        
        Args:
            points: Profile points
        
        Returns:
            True if flat
        """
        return self.flatness_error(points) <= self.tolerance


class SurfaceRoughness:
    """
    Unified surface roughness controller.
    """
    
    def __init__(self):
        self.filter = ProfileFilter()
        self.texture = TextureDirection()
        self.flatness = FlatnessChecker()
        self.parameters: Optional[RoughnessParameters] = None
    
    def measure(self, raw_profile: List[ProfilePoint]):
        """
        Process and measure profile.
        
        Args:
            raw_profile: Raw measured profile
        """
        filtered = self.filter.remove_form(raw_profile)
        roughness = self.filter.roughness_profile(filtered)
        self.parameters = RoughnessParameters(roughness)
    
    def roughness_report(self) -> Dict:
        """
        Generate roughness report.
        
        Returns:
            Report dict
        """
        if self.parameters is None:
            return {"status": "no_data"}
        
        return {
            "ra_um": self.parameters.ra(),
            "rq_um": self.parameters.rq(),
            "rz_um": self.parameters.rz(),
            "rmax_um": self.parameters.rmax(),
            "skewness": self.parameters.skewness(),
            "kurtosis": self.parameters.kurtosis()
        }
    
    def pass_fail(self, ra_limit_um: float = 3.2,
                  rz_limit_um: float = 20.0) -> bool:
        """
        Determine pass/fail.
        
        Args:
            ra_limit_um: Ra limit
            rz_limit_um: Rz limit
        
        Returns:
            True if passes
        """
        if self.parameters is None:
            return False
        
        return (self.parameters.ra() <= ra_limit_um and
                self.parameters.rz() <= rz_limit_um)
