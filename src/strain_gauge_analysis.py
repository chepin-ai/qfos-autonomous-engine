"""
Strain Gauge Analysis Module
Bridge circuit analysis, strain calculation, stress conversion,
load cell calibration, and fatigue monitoring for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StrainReading:
    """Strain gauge reading."""
    gauge_id: str
    microstrain: float
    temperature_C: float
    timestamp_ms: float


class BridgeCircuit:
    """
    Wheatstone bridge circuit analysis.
    """
    
    def __init__(self, excitation_V: float = 5.0,
                 gauge_resistance_Ohm: float = 350.0,
                 gauge_factor: float = 2.0):
        """
        Args:
            excitation_V: Excitation voltage
            gauge_resistance_Ohm: Gauge resistance
            gauge_factor: Gauge factor
        """
        self.Vex = excitation_V
        self.Rg = gauge_resistance_Ohm
        self.GF = gauge_factor
    
    def quarter_bridge_output(self, delta_R_Ohm: float) -> float:
        """
        Compute quarter bridge output.
        
        Args:
            delta_R_Ohm: Resistance change
        
        Returns:
            Output voltage
        """
        if self.Rg <= 0:
            return 0.0
        return self.Vex * delta_R_Ohm / (4.0 * self.Rg)
    
    def half_bridge_output(self, delta_R1_Ohm: float,
                          delta_R2_Ohm: float) -> float:
        """
        Compute half bridge output.
        
        Args:
            delta_R1_Ohm: R1 change
            delta_R2_Ohm: R2 change
        
        Returns:
            Output voltage
        """
        if self.Rg <= 0:
            return 0.0
        return self.Vex * (delta_R1_Ohm - delta_R2_Ohm) / (4.0 * self.Rg)
    
    def full_bridge_output(self, delta_Rs: List[float]) -> float:
        """
        Compute full bridge output.
        
        Args:
            delta_Rs: [dR1, dR2, dR3, dR4]
        
        Returns:
            Output voltage
        """
        if len(delta_Rs) < 4 or self.Rg <= 0:
            return 0.0
        return (self.Vex / (4.0 * self.Rg)) * (
            delta_Rs[0] - delta_Rs[1] + delta_Rs[2] - delta_Rs[3]
        )
    
    def strain_from_output(self, output_V: float,
                          bridge_type: str = "quarter") -> float:
        """
        Convert output to strain.
        
        Args:
            output_V: Output voltage
            bridge_type: Bridge type
        
        Returns:
            Microstrain
        """
        if self.Vex <= 0 or self.GF <= 0:
            return 0.0
        
        if bridge_type == "quarter":
            return output_V / (self.Vex * self.GF / 4.0) * 1e6
        elif bridge_type == "half":
            return output_V / (self.Vex * self.GF / 2.0) * 1e6
        elif bridge_type == "full":
            return output_V / (self.Vex * self.GF) * 1e6
        return 0.0


class StressConverter:
    """
    Convert strain to stress.
    """
    
    def __init__(self, youngs_modulus_GPa: float = 200.0,
                 poisson_ratio: float = 0.3):
        """
        Args:
            youngs_modulus_GPa: E
            poisson_ratio: nu
        """
        self.E = youngs_modulus_GPa * 1e9
        self.nu = poisson_ratio
    
    def uniaxial_stress(self, microstrain: float) -> float:
        """
        Uniaxial stress.
        
        Args:
            microstrain: Strain
        
        Returns:
            Stress in MPa
        """
        strain = microstrain * 1e-6
        return self.E * strain / 1e6
    
    def biaxial_stress(self, strain_x: float, strain_y: float) -> Tuple[float, float]:
        """
        Biaxial stress.
        
        Args:
            strain_x: x strain (microstrain)
            strain_y: y strain (microstrain)
        
        Returns:
            (sigma_x, sigma_y) in MPa
        """
        ex = strain_x * 1e-6
        ey = strain_y * 1e-6
        
        denom = 1.0 - self.nu ** 2
        if abs(denom) < 1e-10:
            return (0.0, 0.0)
        
        sx = self.E * (ex + self.nu * ey) / denom / 1e6
        sy = self.E * (ey + self.nu * ex) / denom / 1e6
        
        return (sx, sy)


class LoadCellCalibrator:
    """
    Load cell calibration.
    """
    
    def __init__(self):
        self.calibration_points: List[Tuple[float, float]] = []
    
    def add_point(self, known_load_N: float, output_mV_V: float):
        """
        Add calibration point.
        
        Args:
            known_load_N: Known load
            output_mV_V: Output
        """
        self.calibration_points.append((known_load_N, output_mV_V))
    
    def sensitivity_mV_V_per_N(self) -> float:
        """
        Compute sensitivity.
        
        Returns:
            Sensitivity
        """
        if len(self.calibration_points) < 2:
            return 0.0
        
        # Linear fit
        n = len(self.calibration_points)
        sum_x = sum(p[0] for p in self.calibration_points)
        sum_y = sum(p[1] for p in self.calibration_points)
        sum_xy = sum(p[0] * p[1] for p in self.calibration_points)
        sum_x2 = sum(p[0] ** 2 for p in self.calibration_points)
        
        denom = n * sum_x2 - sum_x ** 2
        if abs(denom) < 1e-10:
            return 0.0
        
        return (n * sum_xy - sum_x * sum_y) / denom
    
    def load_from_output(self, output_mV_V: float) -> float:
        """
        Convert output to load.
        
        Args:
            output_mV_V: Output
        
        Returns:
            Load in N
        """
        sens = self.sensitivity_mV_V_per_N()
        if sens <= 0:
            return 0.0
        return output_mV_V / sens


class FatigueMonitor:
    """
    Monitor fatigue from strain history.
    """
    
    def __init__(self):
        self.cycles: List[Tuple[float, float]] = []  # (strain_range, count)
    
    def rainflow_count(self, strain_history: List[float]) -> List[Tuple[float, float]]:
        """
        Rainflow counting.
        
        Args:
            strain_history: Strain history (microstrain)
        
        Returns:
            Cycles
        """
        if len(strain_history) < 2:
            return []
        
        # Simplified: count half-cycles between peaks
        peaks = []
        for i in range(1, len(strain_history) - 1):
            if (strain_history[i] > strain_history[i-1] and
                strain_history[i] > strain_history[i+1]):
                peaks.append(strain_history[i])
            elif (strain_history[i] < strain_history[i-1] and
                  strain_history[i] < strain_history[i+1]):
                peaks.append(strain_history[i])
        
        cycles = []
        for i in range(len(peaks) - 1):
            range_val = abs(peaks[i+1] - peaks[i])
            cycles.append((range_val, 0.5))
        
        self.cycles = cycles
        return cycles
    
    def miners_rule(self, fatigue_strength_MPa: float,
                   fatigue_exponent: float = -0.1) -> float:
        """
        Miner's rule damage.
        
        Args:
            fatigue_strength_MPa: Fatigue strength
            fatigue_exponent: Exponent
        
        Returns:
            Damage ratio
        """
        damage = 0.0
        for range_val, count in self.cycles:
            # S-N curve
            stress_range = range_val * 1e-6 * 200e9 / 1e6  # Simplified
            if stress_range <= 0:
                continue
            N = fatigue_strength_MPa / stress_range ** (1.0 / fatigue_exponent)
            if N > 0:
                damage += count / N
        
        return damage


class StrainGaugeAnalysis:
    """
    Unified strain gauge analysis controller.
    """
    
    def __init__(self):
        self.bridge = BridgeCircuit()
        self.stress = StressConverter()
        self.calibrator = LoadCellCalibrator()
        self.fatigue = FatigueMonitor()
        self.readings: List[StrainReading] = []
    
    def add_reading(self, reading: StrainReading):
        """
        Add reading.
        
        Args:
            reading: Reading
        """
        self.readings.append(reading)
    
    def analyze(self) -> Dict:
        """
        Analyze readings.
        
        Returns:
            Results
        """
        if not self.readings:
            return {}
        
        strains = [r.microstrain for r in self.readings]
        stresses = [self.stress.uniaxial_stress(s) for s in strains]
        
        # Fatigue analysis
        cycles = self.fatigue.rainflow_count(strains)
        damage = self.fatigue.miners_rule(200.0)
        
        return {
            "readings": len(self.readings),
            "max_strain": max(strains),
            "max_stress_MPa": max(stresses),
            "cycles": len(cycles),
            "fatigue_damage": damage
        }
    
    def sga_summary(self) -> Dict:
        """Get summary."""
        return {
            "readings": len(self.readings),
            "gauge_factor": self.bridge.GF
        }
