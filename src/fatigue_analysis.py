"""
Fatigue Analysis Module
S-N curves, Miner's rule,
crack growth rate (Paris law), and rainflow counting for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StressCycle:
    """Fatigue stress cycle."""
    min_stress: float
    max_stress: float
    count: int = 1


class SNCurve:
    """
    S-N curve (Wohler curve) analysis.
    """
    
    def __init__(self, fatigue_strength_coefficient_MPa: float = 1000.0,
                 fatigue_exponent: float = -0.1):
        """
        Args:
            fatigue_strength_coefficient_MPa: Fatigue strength coefficient
            fatigue_exponent: Fatigue strength exponent
        """
        self.sigma_f = fatigue_strength_coefficient_MPa
        self.b = fatigue_exponent
    
    def cycles_to_failure(self, stress_amplitude_MPa: float) -> float:
        """
        Compute cycles to failure at given stress amplitude.
        
        Args:
            stress_amplitude_MPa: Stress amplitude
        
        Returns:
            Cycles to failure
        """
        if stress_amplitude_MPa <= 0:
            return float('inf')
        return (stress_amplitude_MPa / self.sigma_f) ** (1.0 / self.b)
    
    def fatigue_limit(self, endurance_cycles: float = 1e6) -> float:
        """
        Compute fatigue limit.
        
        Args:
            endurance_cycles: Endurance cycle count
        
        Returns:
            Fatigue limit stress (MPa)
        """
        return self.sigma_f * (endurance_cycles ** self.b)
    
    def fatigue_strength(self, num_cycles: float) -> float:
        """
        Compute allowable stress for given cycles.
        
        Args:
            num_cycles: Target cycle count
        
        Returns:
            Allowable stress (MPa)
        """
        if num_cycles <= 0:
            return self.sigma_f
        return self.sigma_f * (num_cycles ** self.b)


class MinersRule:
    """
    Palmgren-Miner cumulative damage rule.
    """
    
    def __init__(self):
        pass
    
    def damage_per_cycle(self, stress_amplitude_MPa: float,
                        sn_curve: SNCurve) -> float:
        """
        Compute damage per cycle.
        
        Args:
            stress_amplitude_MPa: Stress amplitude
            sn_curve: S-N curve
        
        Returns:
            Damage per cycle
        """
        n_f = sn_curve.cycles_to_failure(stress_amplitude_MPa)
        if n_f <= 0 or n_f == float('inf'):
            return 0.0
        return 1.0 / n_f
    
    def cumulative_damage(self, cycles: List[StressCycle],
                         sn_curve: SNCurve) -> float:
        """
        Compute total cumulative damage.
        
        Args:
            cycles: Stress cycles
            sn_curve: S-N curve
        
        Returns:
            Total damage (1.0 = failure)
        """
        total = 0.0
        for cycle in cycles:
            amplitude = (cycle.max_stress - cycle.min_stress) / 2.0
            dpc = self.damage_per_cycle(amplitude, sn_curve)
            total += dpc * cycle.count
        return total
    
    def remaining_life(self, current_damage: float) -> float:
        """
        Compute remaining life fraction.
        
        Args:
            current_damage: Current damage
        
        Returns:
            Remaining life fraction
        """
        return max(0.0, 1.0 - current_damage)


class ParisLaw:
    """
    Fatigue crack growth (Paris law).
    """
    
    def __init__(self, C: float = 1e-12, m: float = 3.0):
        """
        Args:
            C: Paris constant
            m: Paris exponent
        """
        self.C = C
        self.m = m
    
    def crack_growth_rate(self, delta_K_MPa_sqrt_m: float) -> float:
        """
        Compute crack growth rate per cycle.
        
        Args:
            delta_K_MPa_sqrt_m: Stress intensity range
        
        Returns:
            da/dN (m/cycle)
        """
        if delta_K_MPa_sqrt_m <= 0:
            return 0.0
        return self.C * (delta_K_MPa_sqrt_m ** self.m)
    
    def cycles_to_critical(self, initial_crack_m: float,
                          critical_crack_m: float,
                          delta_K_MPa_sqrt_m: float) -> float:
        """
        Compute cycles from initial to critical crack size.
        
        Args:
            initial_crack_m: Initial crack size
            critical_crack_m: Critical crack size
            delta_K_MPa_sqrt_m: Stress intensity range
        
        Returns:
            Cycles
        """
        if initial_crack_m >= critical_crack_m or delta_K_MPa_sqrt_m <= 0:
            return 0.0
        dadn = self.crack_growth_rate(delta_K_MPa_sqrt_m)
        if dadn <= 0:
            return float('inf')
        return (critical_crack_m - initial_crack_m) / dadn


class RainflowCounting:
    """
    Rainflow cycle counting algorithm (simplified).
    """
    
    def __init__(self):
        pass
    
    def extract_cycles(self, stress_history: List[float]) -> List[StressCycle]:
        """
        Extract cycles from stress history (simplified peak-valley).
        
        Args:
            stress_history: Stress values over time
        
        Returns:
            Extracted cycles
        """
        if len(stress_history) < 2:
            return []
        cycles = []
        # Simplified: pair consecutive peaks and valleys
        for i in range(0, len(stress_history) - 1, 2):
            s_min = min(stress_history[i], stress_history[i + 1])
            s_max = max(stress_history[i], stress_history[i + 1])
            cycles.append(StressCycle(s_min, s_max, 1))
        return cycles
    
    def stress_range_histogram(self, cycles: List[StressCycle],
                              num_bins: int = 10) -> List[int]:
        """
        Build stress range histogram.
        
        Args:
            cycles: Extracted cycles
            num_bins: Number of bins
        
        Returns:
            Bin counts
        """
        if not cycles:
            return [0] * num_bins
        ranges = [c.max_stress - c.min_stress for c in cycles]
        max_range = max(ranges)
        if max_range <= 0:
            return [0] * num_bins
        bins = [0] * num_bins
        for cycle in cycles:
            r = cycle.max_stress - cycle.min_stress
            idx = min(int(r / max_range * num_bins), num_bins - 1)
            bins[idx] += cycle.count
        return bins


class FatigueAnalysis:
    """
    Unified fatigue analysis controller.
    """
    
    def __init__(self):
        self.sn = SNCurve()
        self.miner = MinersRule()
        self.paris = ParisLaw()
        self.rainflow = RainflowCounting()
    
    def fatigue_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["sn_curve", "miners_rule", "paris_law", "rainflow"],
            "outputs": ["cycles_to_failure", "cumulative_damage", "crack_growth"]
        }
