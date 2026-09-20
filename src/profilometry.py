"""
Profilometry Module
Surface profile measurement, roughness analysis, waviness analysis,
form error evaluation, and surface texture parameters for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ProfilePoint:
    """Profile measurement point."""
    x_mm: float
    z_um: float


class ProfileAcquisition:
    """
    Acquire surface profile data.
    """
    
    def __init__(self, sampling_interval_um: float = 5.0):
        """
        Args:
            sampling_interval_um: Sampling interval
        """
        self.interval = sampling_interval_um
    
    def generate_profile(self, length_mm: float,
                        roughness_um: float = 1.0) -> List[ProfilePoint]:
        """
        Generate synthetic profile.
        
        Args:
            length_mm: Profile length
            roughness_um: Roughness amplitude
        
        Returns:
            Profile points
        """
        import random
        num_points = int(length_mm * 1000.0 / self.interval)
        profile = []
        
        for i in range(num_points):
            x = i * self.interval / 1000.0
            # Synthetic rough surface with form error
            z = (roughness_um * random.uniform(-1.0, 1.0) +
                 0.1 * math.sin(2.0 * math.pi * x / 10.0))
            profile.append(ProfilePoint(x, z))
        
        return profile
    
    def resample(self, profile: List[ProfilePoint],
                new_interval_um: float) -> List[ProfilePoint]:
        """
        Resample profile.
        
        Args:
            profile: Input profile
            new_interval_um: New interval
        
        Returns:
            Resampled profile
        """
        if not profile:
            return []
        
        resampled = []
        x_max = profile[-1].x_mm
        x = 0.0
        
        while x <= x_max:
            # Find closest point
            closest = min(profile, key=lambda p: abs(p.x_mm - x))
            resampled.append(ProfilePoint(x, closest.z_um))
            x += new_interval_um / 1000.0
        
        return resampled


class RoughnessAnalyzer:
    """
    Analyze surface roughness.
    """
    
    def __init__(self, cutoff_mm: float = 0.8):
        """
        Args:
            cutoff_mm: Evaluation length
        """
        self.cutoff = cutoff_mm
    
    def ra(self, profile: List[ProfilePoint]) -> float:
        """
        Compute Ra (arithmetic mean roughness).
        
        Args:
            profile: Profile
        
        Returns:
            Ra in um
        """
        if not profile:
            return 0.0
        
        mean_z = sum(p.z_um for p in profile) / len(profile)
        return sum(abs(p.z_um - mean_z) for p in profile) / len(profile)
    
    def rq(self, profile: List[ProfilePoint]) -> float:
        """
        Compute Rq (root mean square roughness).
        
        Args:
            profile: Profile
        
        Returns:
            Rq in um
        """
        if not profile:
            return 0.0
        
        mean_z = sum(p.z_um for p in profile) / len(profile)
        return math.sqrt(sum((p.z_um - mean_z) ** 2 for p in profile) / len(profile))
    
    def rz(self, profile: List[ProfilePoint], num_cutoffs: int = 5) -> float:
        """
        Compute Rz (mean peak-to-valley).
        
        Args:
            profile: Profile
            num_cutoffs: Cutoffs
        
        Returns:
            Rz in um
        """
        if not profile:
            return 0.0
        
        # Simplified: overall peak-to-valley
        z_values = [p.z_um for p in profile]
        return max(z_values) - min(z_values)
    
    def rt(self, profile: List[ProfilePoint]) -> float:
        """
        Compute Rt (total peak-to-valley).
        
        Args:
            profile: Profile
        
        Returns:
            Rt in um
        """
        return self.rz(profile)


class WavinessAnalyzer:
    """
    Analyze surface waviness.
    """
    
    def __init__(self, waviness_cutoff_mm: float = 0.8):
        """
        Args:
            waviness_cutoff_mm: Waviness cutoff
        """
        self.cutoff = waviness_cutoff_mm
    
    def wa(self, profile: List[ProfilePoint]) -> float:
        """
        Compute Wa (waviness average).
        
        Args:
            profile: Profile
        
        Returns:
            Wa in um
        """
        if not profile:
            return 0.0
        
        # Simplified moving average
        smoothed = self._smooth(profile, 11)
        mean_z = sum(p.z_um for p in smoothed) / len(smoothed)
        return sum(abs(p.z_um - mean_z) for p in smoothed) / len(smoothed)
    
    def _smooth(self, profile: List[ProfilePoint],
               window: int) -> List[ProfilePoint]:
        """
        Smooth profile.
        
        Args:
            profile: Profile
            window: Window size
        
        Returns:
            Smoothed profile
        """
        smoothed = []
        half = window // 2
        
        for i in range(len(profile)):
            start = max(0, i - half)
            end = min(len(profile), i + half + 1)
            avg_z = sum(profile[j].z_um for j in range(start, end)) / (end - start)
            smoothed.append(ProfilePoint(profile[i].x_mm, avg_z))
        
        return smoothed


class FormErrorEvaluator:
    """
    Evaluate form errors.
    """
    
    def __init__(self):
        pass
    
    def least_squares_line(self, profile: List[ProfilePoint]) -> Tuple[float, float]:
        """
        Fit least squares line.
        
        Args:
            profile: Profile
        
        Returns:
            (slope, intercept)
        """
        if len(profile) < 2:
            return (0.0, 0.0)
        
        n = len(profile)
        sum_x = sum(p.x_mm for p in profile)
        sum_z = sum(p.z_um for p in profile)
        sum_xz = sum(p.x_mm * p.z_um for p in profile)
        sum_x2 = sum(p.x_mm ** 2 for p in profile)
        
        denom = n * sum_x2 - sum_x ** 2
        if abs(denom) < 1e-10:
            return (0.0, sum_z / n)
        
        slope = (n * sum_xz - sum_x * sum_z) / denom
        intercept = (sum_z - slope * sum_x) / n
        
        return (slope, intercept)
    
    def flatness(self, profile: List[ProfilePoint]) -> float:
        """
        Compute flatness error.
        
        Args:
            profile: Profile
        
        Returns:
            Flatness in um
        """
        if not profile:
            return 0.0
        
        slope, intercept = self.least_squares_line(profile)
        
        residuals = []
        for p in profile:
            fitted = slope * p.x_mm + intercept
            residuals.append(p.z_um - fitted)
        
        return max(residuals) - min(residuals)


class Profilometry:
    """
    Unified profilometry controller.
    """
    
    def __init__(self):
        self.acquisition = ProfileAcquisition()
        self.roughness = RoughnessAnalyzer()
        self.waviness = WavinessAnalyzer()
        self.form = FormErrorEvaluator()
        self.profile: List[ProfilePoint] = []
    
    def measure(self, length_mm: float, roughness_um: float = 1.0):
        """
        Measure surface.
        
        Args:
            length_mm: Length
            roughness_um: Roughness
        """
        self.profile = self.acquisition.generate_profile(length_mm, roughness_um)
    
    def analyze(self) -> Dict:
        """
        Analyze surface.
        
        Returns:
            Results
        """
        return {
            "Ra_um": self.roughness.ra(self.profile),
            "Rq_um": self.roughness.rq(self.profile),
            "Rz_um": self.roughness.rz(self.profile),
            "Rt_um": self.roughness.rt(self.profile),
            "Wa_um": self.waviness.wa(self.profile),
            "flatness_um": self.form.flatness(self.profile)
        }
    
    def prof_summary(self) -> Dict:
        """Get summary."""
        return {
            "points": len(self.profile),
            "length_mm": self.profile[-1].x_mm if self.profile else 0.0
        }
