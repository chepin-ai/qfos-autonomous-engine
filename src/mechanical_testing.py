"""
Mechanical Testing Module
Tensile, compression, fatigue, creep testing,
stress-strain analysis, and S-N curves for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StressStrainPoint:
    """Stress-strain data point."""
    strain: float
    stress_MPa: float


class TensileTest:
    """
    Tensile test analysis.
    """
    
    def __init__(self):
        self.curve: List[StressStrainPoint] = []
    
    def add_point(self, strain: float, stress_MPa: float):
        """
        Add data point.
        
        Args:
            strain: Strain
            stress_MPa: Stress in MPa
        """
        self.curve.append(StressStrainPoint(strain, stress_MPa))
    
    def young_modulus(self) -> float:
        """
        Compute Young's modulus from elastic region.
        
        Returns:
            Young's modulus in GPa
        """
        if len(self.curve) < 2:
            return 0.0
        
        # Linear fit for first few points (elastic region)
        n = min(5, len(self.curve))
        points = self.curve[:n]
        
        sum_x = sum(p.strain for p in points)
        sum_y = sum(p.stress_MPa for p in points)
        sum_xy = sum(p.strain * p.stress_MPa for p in points)
        sum_x2 = sum(p.strain ** 2 for p in points)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        return slope / 1000.0  # Convert to GPa
    
    def yield_strength(self, offset: float = 0.002) -> float:
        """
        Estimate yield strength using 0.2% offset method.
        
        Args:
            offset: Offset strain
        
        Returns:
            Yield strength in MPa
        """
        E = self.young_modulus() * 1000.0  # Back to MPa
        if E <= 0:
            return 0.0
        
        for point in self.curve:
            expected_stress = E * (point.strain - offset)
            if point.stress_MPa < expected_stress:
                return point.stress_MPa
        
        return self.curve[-1].stress_MPa if self.curve else 0.0
    
    def ultimate_tensile_strength(self) -> float:
        """
        Compute ultimate tensile strength.
        
        Returns:
            UTS in MPa
        """
        if not self.curve:
            return 0.0
        return max(p.stress_MPa for p in self.curve)


class FatigueTest:
    """
    Fatigue test analysis.
    """
    
    def __init__(self):
        self.sn_data: List[Tuple[float, int]] = []
    
    def add_point(self, stress_amplitude_MPa: float,
                 cycles_to_failure: int):
        """
        Add S-N data point.
        
        Args:
            stress_amplitude_MPa: Stress amplitude
            cycles_to_failure: Cycles to failure
        """
        self.sn_data.append((stress_amplitude_MPa, cycles_to_failure))
    
    def endurance_limit(self, threshold_cycles: int = 1_000_000) -> float:
        """
        Estimate endurance limit.
        
        Args:
            threshold_cycles: Cycle threshold
        
        Returns:
            Endurance limit in MPa
        """
        below_threshold = [s for s, c in self.sn_data if c >= threshold_cycles]
        if below_threshold:
            return max(below_threshold)
        
        if len(self.sn_data) < 2:
            return 0.0
        
        # Extrapolate from log-log fit
        log_s = [math.log10(s) for s, c in self.sn_data]
        log_n = [math.log10(c) for s, c in self.sn_data]
        
        n = len(log_s)
        sum_x = sum(log_n)
        sum_y = sum(log_s)
        sum_xy = sum(x * y for x, y in zip(log_n, log_s))
        sum_x2 = sum(x ** 2 for x in log_n)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        
        log_threshold = math.log10(threshold_cycles)
        return 10.0 ** (slope * log_threshold + intercept)
    
    def basquin_law(self) -> Tuple[float, float]:
        """
        Fit Basquin's law: sigma_a = sigma_f * (2N)^b.
        
        Returns:
            (sigma_f, b)
        """
        if len(self.sn_data) < 2:
            return (0.0, 0.0)
        
        log_s = [math.log10(s) for s, c in self.sn_data]
        log_n = [math.log10(2 * c) for s, c in self.sn_data]
        
        n = len(log_s)
        sum_x = sum(log_n)
        sum_y = sum(log_s)
        sum_xy = sum(x * y for x, y in zip(log_n, log_s))
        sum_x2 = sum(x ** 2 for x in log_n)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return (0.0, 0.0)
        
        b = (n * sum_xy - sum_x * sum_y) / denom
        log_sigma_f = (sum_y - b * sum_x) / n
        sigma_f = 10.0 ** log_sigma_f
        
        return (sigma_f, b)


class CreepTest:
    """
    Creep test analysis.
    """
    
    def __init__(self):
        self.data: List[Tuple[float, float]] = []  # (time_h, strain)
    
    def add_point(self, time_h: float, strain: float):
        """
        Add creep data point.
        
        Args:
            time_h: Time in hours
            strain: Strain
        """
        self.data.append((time_h, strain))
    
    def creep_rate(self) -> float:
        """
        Compute steady-state creep rate.
        
        Returns:
            Creep rate (strain/hour)
        """
        if len(self.data) < 2:
            return 0.0
        
        # Linear fit to secondary creep region (last half of data)
        start = len(self.data) // 2
        points = self.data[start:]
        
        n = len(points)
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        sum_xy = sum(p[0] * p[1] for p in points)
        sum_x2 = sum(p[0] ** 2 for p in points)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return 0.0
        
        return (n * sum_xy - sum_x * sum_y) / denom
    
    def rupture_time(self, threshold_strain: float = 0.1) -> float:
        """
        Estimate rupture time.
        
        Args:
            threshold_strain: Failure strain
        
        Returns:
            Rupture time in hours
        """
        if not self.data:
            return 0.0
        
        # Extrapolate from last data point using creep rate
        rate = self.creep_rate()
        if rate <= 0:
            return float('inf')
        
        last_time, last_strain = self.data[-1]
        remaining_strain = threshold_strain - last_strain
        
        if remaining_strain <= 0:
            return last_time
        
        return last_time + remaining_strain / rate


class CompressionTest:
    """
    Compression test analysis.
    """
    
    def __init__(self):
        self.curve: List[StressStrainPoint] = []
    
    def add_point(self, strain: float, stress_MPa: float):
        """
        Add data point.
        
        Args:
            strain: Strain
            stress_MPa: Stress in MPa
        """
        self.curve.append(StressStrainPoint(strain, stress_MPa))
    
    def compressive_strength(self) -> float:
        """
        Compute compressive strength.
        
        Returns:
            Compressive strength in MPa
        """
        if not self.curve:
            return 0.0
        return max(p.stress_MPa for p in self.curve)
    
    def compressive_modulus(self) -> float:
        """
        Compute compressive modulus.
        
        Returns:
            Compressive modulus in GPa
        """
        if len(self.curve) < 2:
            return 0.0
        
        n = min(5, len(self.curve))
        points = self.curve[:n]
        
        sum_x = sum(p.strain for p in points)
        sum_y = sum(p.stress_MPa for p in points)
        sum_xy = sum(p.strain * p.stress_MPa for p in points)
        sum_x2 = sum(p.strain ** 2 for p in points)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        return slope / 1000.0


class MechanicalTesting:
    """
    Unified mechanical testing controller.
    """
    
    def __init__(self):
        self.tensile = TensileTest()
        self.compression = CompressionTest()
        self.fatigue = FatigueTest()
        self.creep = CreepTest()
    
    def mt_summary(self) -> Dict:
        """Get summary."""
        return {
            "tests": ["tensile", "compression", "fatigue", "creep"],
            "tensile_points": len(self.tensile.curve),
            "fatigue_points": len(self.fatigue.sn_data),
            "creep_points": len(self.creep.data)
        }
