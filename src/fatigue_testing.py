"""
Fatigue Testing Module
S-N curves, Miner's rule, rainflow counting,
mean stress correction, and crack initiation for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CycleCount:
    """Cycle count result."""
    amplitude: float
    mean: float
    count: float


class SNCurve:
    """
    S-N curve (Wohler curve) analysis.
    """
    
    def __init__(self, fatigue_strength_coefficient_MPa: float = 1000.0,
                 fatigue_strength_exponent: float = -0.1,
                 fatigue_ductility_coefficient: float = 1.0,
                 fatigue_ductility_exponent: float = -0.6):
        """
        Args:
            fatigue_strength_coefficient_MPa: sigma_f'
            fatigue_strength_exponent: b
            fatigue_ductility_coefficient: epsilon_f'
            fatigue_ductility_exponent: c
        """
        self.sigma_f = fatigue_strength_coefficient_MPa
        self.b = fatigue_strength_exponent
        self.epsilon_f = fatigue_ductility_coefficient
        self.c = fatigue_ductility_exponent
    
    def cycles_to_failure(self, stress_amplitude_MPa: float) -> float:
        """
        Compute cycles to failure from stress amplitude.
        
        Args:
            stress_amplitude_MPa: Stress amplitude
        
        Returns:
            Cycles to failure
        """
        if stress_amplitude_MPa <= 0:
            return float('inf')
        return (stress_amplitude_MPa / self.sigma_f) ** (1.0 / self.b)
    
    def endurance_limit(self, cycles: float = 1e6) -> float:
        """
        Compute endurance limit.
        
        Args:
            cycles: Reference cycles
        
        Returns:
            Endurance limit in MPa
        """
        return self.sigma_f * (cycles ** self.b)
    
    def strain_life(self, strain_amplitude: float,
                   youngs_modulus_GPa: float = 200.0) -> float:
        """
        Compute strain-life cycles.
        
        Args:
            strain_amplitude: Strain amplitude
            youngs_modulus_GPa: Young's modulus
        
        Returns:
            Cycles to failure
        """
        E = youngs_modulus_GPa * 1e3
        if E <= 0 or strain_amplitude <= 0:
            return float('inf')
        
        # Coffin-Manson: epsilon_a = sigma_f'/E * (2N)^b + epsilon_f' * (2N)^c
        # Simplified: use dominant term
        if strain_amplitude > self.sigma_f / E:
            # Plastic dominated
            N = 0.5 * (strain_amplitude / self.epsilon_f) ** (1.0 / self.c)
        else:
            # Elastic dominated
            N = 0.5 * (strain_amplitude * E / self.sigma_f) ** (1.0 / self.b)
        
        return N


class MinersRule:
    """
    Miner's linear cumulative damage rule.
    """
    
    def __init__(self):
        pass
    
    def damage_ratio(self, cycles_applied: float,
                    cycles_to_failure: float) -> float:
        """
        Compute damage ratio for one level.
        
        Args:
            cycles_applied: Applied cycles
            cycles_to_failure: Cycles to failure
        
        Returns:
            Damage ratio
        """
        if cycles_to_failure <= 0:
            return 0.0
        return cycles_applied / cycles_to_failure
    
    def total_damage(self, cycle_counts: List[CycleCount],
                    sn_curve: SNCurve) -> float:
        """
        Compute total cumulative damage.
        
        Args:
            cycle_counts: Cycle counts
            sn_curve: S-N curve
        
        Returns:
            Total damage
        """
        damage = 0.0
        for cc in cycle_counts:
            Nf = sn_curve.cycles_to_failure(cc.amplitude)
            damage += self.damage_ratio(cc.count, Nf)
        return damage
    
    def remaining_life(self, total_damage: float) -> float:
        """
        Compute remaining life fraction.
        
        Args:
            total_damage: Total damage
        
        Returns:
            Remaining life fraction
        """
        if total_damage >= 1.0:
            return 0.0
        return 1.0 - total_damage


class RainflowCounter:
    """
    Rainflow cycle counting.
    """
    
    def __init__(self):
        pass
    
    def extract_cycles(self, stress_history: List[float]) -> List[CycleCount]:
        """
        Extract cycles from stress history (simplified).
        
        Args:
            stress_history: Stress time history
        
        Returns:
            Cycle counts
        """
        if len(stress_history) < 2:
            return []
        
        cycles = []
        # Simplified: count turning points
        peaks = []
        valleys = []
        
        for i in range(1, len(stress_history) - 1):
            if (stress_history[i] > stress_history[i-1] and
                stress_history[i] > stress_history[i+1]):
                peaks.append(stress_history[i])
            elif (stress_history[i] < stress_history[i-1] and
                  stress_history[i] < stress_history[i+1]):
                valleys.append(stress_history[i])
        
        # Pair peaks and valleys
        for i in range(min(len(peaks), len(valleys))):
            amplitude = abs(peaks[i] - valleys[i]) / 2.0
            mean = (peaks[i] + valleys[i]) / 2.0
            cycles.append(CycleCount(amplitude, mean, 1.0))
        
        return cycles
    
    def range_count(self, stress_history: List[float],
                   bin_size_MPa: float = 10.0) -> Dict[float, int]:
        """
        Count ranges in bins.
        
        Args:
            stress_history: Stress history
            bin_size_MPa: Bin size
        
        Returns:
            Range counts
        """
        cycles = self.extract_cycles(stress_history)
        counts = {}
        for cc in cycles:
            bin_center = round(cc.amplitude / bin_size_MPa) * bin_size_MPa
            counts[bin_center] = counts.get(bin_center, 0) + 1
        return counts


class MeanStressCorrection:
    """
    Mean stress correction methods.
    """
    
    def __init__(self):
        pass
    
    def goodman(self, stress_amplitude_MPa: float,
               mean_stress_MPa: float,
               ultimate_strength_MPa: float) -> float:
        """
        Goodman mean stress correction.
        
        Args:
            stress_amplitude_MPa: Stress amplitude
            mean_stress_MPa: Mean stress
            ultimate_strength_MPa: Ultimate strength
        
        Returns:
            Equivalent fully reversed stress
        """
        if ultimate_strength_MPa <= mean_stress_MPa:
            return float('inf')
        return stress_amplitude_MPa / (1.0 - mean_stress_MPa / ultimate_strength_MPa)
    
    def gerber(self, stress_amplitude_MPa: float,
              mean_stress_MPa: float,
              ultimate_strength_MPa: float) -> float:
        """
        Gerber mean stress correction.
        
        Args:
            stress_amplitude_MPa: Stress amplitude
            mean_stress_MPa: Mean stress
            ultimate_strength_MPa: Ultimate strength
        
        Returns:
            Equivalent fully reversed stress
        """
        if ultimate_strength_MPa == 0:
            return 0.0
        return stress_amplitude_MPa / (1.0 - (mean_stress_MPa / ultimate_strength_MPa) ** 2)
    
    def soderberg(self, stress_amplitude_MPa: float,
                 mean_stress_MPa: float,
                 yield_strength_MPa: float) -> float:
        """
        Soderberg mean stress correction.
        
        Args:
            stress_amplitude_MPa: Stress amplitude
            mean_stress_MPa: Mean stress
            yield_strength_MPa: Yield strength
        
        Returns:
            Equivalent fully reversed stress
        """
        if yield_strength_MPa <= mean_stress_MPa:
            return float('inf')
        return stress_amplitude_MPa / (1.0 - mean_stress_MPa / yield_strength_MPa)


class FatigueTesting:
    """
    Unified fatigue testing controller.
    """
    
    def __init__(self):
        self.sn = SNCurve()
        self.miner = MinersRule()
        self.rainflow = RainflowCounter()
        self.mean_stress = MeanStressCorrection()
    
    def fatigue_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["S-N_curve", "Miners_rule", "rainflow", "mean_stress_correction"],
            "corrections": ["Goodman", "Gerber", "Soderberg"]
        }
