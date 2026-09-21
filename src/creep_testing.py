"""
Creep Testing Module
Creep strain, stress rupture, Larson-Miller parameter,
steady-state rate, and tertiary creep analysis for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CreepDataPoint:
    """Creep data point."""
    time_h: float
    strain: float
    stress_MPa: float
    temperature_C: float


class SteadyStateCreep:
    """
    Steady-state creep rate analysis.
    """
    
    def __init__(self, A: float = 1.0e-10,
                 n: float = 5.0,
                 Q_kJ_mol: float = 200.0):
        """
        Args:
            A: Material constant
            n: Stress exponent
            Q_kJ_mol: Activation energy
        """
        self.A = A
        self.n = n
        self.Q = Q_kJ_mol * 1e3
        self.R = 8.314
    
    def creep_rate(self, stress_MPa: float,
                  temperature_K: float) -> float:
        """
        Compute steady-state creep rate.
        
        Args:
            stress_MPa: Applied stress
            temperature_K: Temperature
        
        Returns:
            Creep rate in 1/h
        """
        if temperature_K <= 0:
            return 0.0
        return self.A * (stress_MPa ** self.n) * math.exp(-self.Q / (self.R * temperature_K))
    
    def activation_energy(self, creep_rates: List[float],
                         temperatures_K: List[float]) -> float:
        """
        Estimate activation energy from data.
        
        Args:
            creep_rates: Creep rates
            temperatures_K: Temperatures
        
        Returns:
            Activation energy in kJ/mol
        """
        if len(creep_rates) < 2:
            return 0.0
        
        # Use Arrhenius plot: ln(creep_rate) vs 1/T
        log_rates = [math.log(r) for r in creep_rates if r > 0]
        inv_T = [1.0 / T for T in temperatures_K if T > 0]
        
        if len(log_rates) < 2:
            return 0.0
        
        n = len(log_rates)
        sum_x = sum(inv_T)
        sum_y = sum(log_rates)
        sum_xy = sum(x * y for x, y in zip(inv_T, log_rates))
        sum_x2 = sum(x ** 2 for x in inv_T)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        return -slope * self.R / 1e3


class LarsonMillerParameter:
    """
    Larson-Miller parameter for creep life prediction.
    """
    
    def __init__(self, constant_C: float = 20.0):
        """
        Args:
            constant_C: Larson-Miller constant
        """
        self.C = constant_C
    
    def parameter(self, temperature_K: float,
                 rupture_time_h: float) -> float:
        """
        Compute Larson-Miller parameter.
        
        Args:
            temperature_K: Temperature
            rupture_time_h: Rupture time
        
        Returns:
            LMP value
        """
        if rupture_time_h <= 0 or temperature_K <= 0:
            return 0.0
        return temperature_K * (math.log10(rupture_time_h) + self.C) * 1e-3
    
    def rupture_time(self, LMP: float,
                    temperature_K: float) -> float:
        """
        Predict rupture time from LMP.
        
        Args:
            LMP: Larson-Miller parameter
            temperature_K: Temperature
        
        Returns:
            Rupture time in hours
        """
        if temperature_K <= 0:
            return 0.0
        return 10.0 ** (LMP * 1e3 / temperature_K - self.C)


class StressRupture:
    """
    Stress rupture analysis.
    """
    
    def __init__(self):
        pass
    
    def monkman_grant(self, steady_state_creep_rate: float,
                     rupture_strain: float) -> float:
        """
        Compute Monkman-Grant product.
        
        Args:
            steady_state_creep_rate: Creep rate
            rupture_strain: Rupture strain
        
        Returns:
            Monkman-Grant product
        """
        if steady_state_creep_rate <= 0:
            return 0.0
        return rupture_strain / steady_state_creep_rate
    
    def rupture_life_stress(self, stress_MPa: float,
                           A: float = 1.0e6,
                           B: float = -5.0) -> float:
        """
        Estimate rupture life from stress.
        
        Args:
            stress_MPa: Stress
            A: Constant
            B: Exponent
        
        Returns:
            Rupture life in hours
        """
        if stress_MPa <= 0:
            return 0.0
        return A * (stress_MPa ** B)


class TertiaryCreep:
    """
    Tertiary creep and damage analysis.
    """
    
    def __init__(self):
        pass
    
    def damage_parameter(self, current_area_mm2: float,
                        initial_area_mm2: float) -> float:
        """
        Compute creep damage parameter.
        
        Args:
            current_area_mm2: Current cross-section
            initial_area_mm2: Initial cross-section
        
        Returns:
            Damage parameter
        """
        if initial_area_mm2 <= 0:
            return 0.0
        return 1.0 - current_area_mm2 / initial_area_mm2
    
    def void_growth_rate(self, stress_MPa: float,
                    void_radius_mm: float,
                    diffusion_coefficient: float = 1.0e-12) -> float:
        """
        Compute void growth rate.
        
        Args:
            stress_MPa: Stress
            void_radius_mm: Void radius
            diffusion_coefficient: Diffusion coefficient
        
        Returns:
            Growth rate
        """
        if void_radius_mm <= 0:
            return 0.0
        return diffusion_coefficient * stress_MPa / void_radius_mm


class CreepTesting:
    """
    Unified creep testing controller.
    """
    
    def __init__(self):
        self.steady_state = SteadyStateCreep()
        self.larson_miller = LarsonMillerParameter()
        self.rupture = StressRupture()
        self.tertiary = TertiaryCreep()
    
    def creep_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["steady_state", "Larson-Miller", "stress_rupture", "tertiary"],
            "applications": ["turbines", "pressure_vessels", "pipelines"]
        }
