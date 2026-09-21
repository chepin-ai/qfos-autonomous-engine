"""
Fracture Mechanics Module
Stress intensity factor, J-integral, CTOD,
Paris law, and crack growth analysis for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CrackGrowth:
    """Crack growth result."""
    cycles: int
    crack_length_mm: float
    da_dn: float


class StressIntensityFactor:
    """
    Stress intensity factor (SIF) calculator.
    """
    
    def __init__(self):
        pass
    
    def mode_I_infinite_plate(self, stress_MPa: float,
                             crack_length_mm: float) -> float:
        """
        Compute Mode I SIF for center crack in infinite plate.
        
        Args:
            stress_MPa: Applied stress
            crack_length_mm: Half crack length
        
        Returns:
            K_I in MPa*sqrt(m)
        """
        a = crack_length_mm * 1e-3
        return stress_MPa * math.sqrt(math.pi * a)
    
    def mode_I_finite_width(self, stress_MPa: float,
                           crack_length_mm: float,
                           width_mm: float) -> float:
        """
        Compute Mode I SIF for center crack in finite width plate.
        
        Args:
            stress_MPa: Applied stress
            crack_length_mm: Half crack length
            width_mm: Plate width
        
        Returns:
            K_I in MPa*sqrt(m)
        """
        a = crack_length_mm * 1e-3
        W = width_mm * 1e-3
        if W <= 0:
            return 0.0
        ratio = a / W
        # Tada-Paris-Irwin correction
        Y = math.sqrt(math.pi * ratio) * (1.0 - 0.5 * ratio + 0.326 * ratio ** 2)
        return stress_MPa * math.sqrt(W) * Y
    
    def mode_I_edge_crack(self, stress_MPa: float,
                         crack_length_mm: float) -> float:
        """
        Compute Mode I SIF for edge crack.
        
        Args:
            stress_MPa: Applied stress
            crack_length_mm: Crack length
        
        Returns:
            K_I in MPa*sqrt(m)
        """
        a = crack_length_mm * 1e-3
        return 1.12 * stress_MPa * math.sqrt(math.pi * a)
    
    def critical_stress(self, fracture_toughness_MPa_sqrt_m: float,
                       crack_length_mm: float) -> float:
        """
        Compute critical stress for crack propagation.
        
        Args:
            fracture_toughness_MPa_sqrt_m: K_IC
            crack_length_mm: Half crack length
        
        Returns:
            Critical stress in MPa
        """
        a = crack_length_mm * 1e-3
        if a <= 0:
            return float('inf')
        return fracture_toughness_MPa_sqrt_m / math.sqrt(math.pi * a)


class ParisLaw:
    """
    Paris law fatigue crack growth.
    """
    
    def __init__(self, C: float = 1.0e-12, m: float = 3.0):
        """
        Args:
            C: Paris law constant
            m: Paris law exponent
        """
        self.C = C
        self.m = m
    
    def crack_growth_rate(self, delta_K: float) -> float:
        """
        Compute crack growth rate per cycle.
        
        Args:
            delta_K: Stress intensity range
        
        Returns:
            da/dN in mm/cycle
        """
        return self.C * (delta_K ** self.m) * 1e3
    
    def cycles_to_failure(self, initial_crack_mm: float,
                         final_crack_mm: float,
                         delta_stress_MPa: float,
                         geometry_factor: float = 1.0) -> int:
        """
        Estimate cycles to failure.
        
        Args:
            initial_crack_mm: Initial crack length
            final_crack_mm: Final crack length
            delta_stress_MPa: Stress range
            geometry_factor: Geometry correction
        
        Returns:
            Estimated cycles
        """
        if initial_crack_mm <= 0 or final_crack_mm <= initial_crack_mm:
            return 0
        
        # Integral form for center crack
        a0 = initial_crack_mm * 1e-3
        af = final_crack_mm * 1e-3
        
        # Simplified: N = 2 / (C * (delta_sigma * Y * sqrt(pi))^m * (m-2)) * (1/a0^((m-2)/2) - 1/af^((m-2)/2))
        if self.m == 2:
            return 0
        
        term = self.C * (delta_stress_MPa * geometry_factor * math.sqrt(math.pi)) ** self.m
        if term == 0:
            return 0
        
        exp = (self.m - 2) / 2.0
        N = (2.0 / (term * exp)) * (a0 ** (-exp) - af ** (-exp))
        return max(0, int(N))
    
    def simulate_growth(self, initial_crack_mm: float,
                       max_cycles: int,
                       delta_stress_MPa: float,
                       geometry_factor: float = 1.0) -> List[CrackGrowth]:
        """
        Simulate crack growth over cycles.
        
        Args:
            initial_crack_mm: Initial crack length
            max_cycles: Maximum cycles
            delta_stress_MPa: Stress range
            geometry_factor: Geometry correction
        
        Returns:
            Crack growth history
        """
        history = []
        a = initial_crack_mm
        
        for cycle in range(0, max_cycles + 1, max(1, max_cycles // 20)):
            if a <= 0:
                break
            delta_K = delta_stress_MPa * geometry_factor * math.sqrt(math.pi * a * 1e-3)
            dadn = self.crack_growth_rate(delta_K)
            history.append(CrackGrowth(cycle, a, dadn))
            a += dadn * (max_cycles // 20)
        
        return history


class JIntegral:
    """
    J-integral for elastic-plastic fracture.
    """
    
    def __init__(self):
        pass
    
    def elastic_component(self, K_I: float,
                         youngs_modulus_GPa: float,
                         poisson_ratio: float = 0.3) -> float:
        """
        Compute elastic component of J-integral.
        
        Args:
            K_I: Stress intensity factor
            youngs_modulus_GPa: Young's modulus
            poisson_ratio: Poisson's ratio
        
        Returns:
            J_elastic in kJ/m^2
        """
        E = youngs_modulus_GPa * 1e3
        if E <= 0:
            return 0.0
        return (K_I ** 2 * (1.0 - poisson_ratio ** 2)) / E
    
    def plastic_component(self, yield_stress_MPa: float,
                         crack_opening_displacement_mm: float) -> float:
        """
        Compute plastic component of J-integral.
        
        Args:
            yield_stress_MPa: Yield stress
            crack_opening_displacement_mm: CTOD
        
        Returns:
            J_plastic in kJ/m^2
        """
        delta = crack_opening_displacement_mm * 1e-3
        return yield_stress_MPa * delta * 1e-3
    
    def total_J(self, K_I: float,
               youngs_modulus_GPa: float,
               yield_stress_MPa: float,
               crack_opening_displacement_mm: float,
               poisson_ratio: float = 0.3) -> float:
        """
        Compute total J-integral.
        
        Args:
            K_I: SIF
            youngs_modulus_GPa: Young's modulus
            yield_stress_MPa: Yield stress
            crack_opening_displacement_mm: CTOD
            poisson_ratio: Poisson's ratio
        
        Returns:
            J_total in kJ/m^2
        """
        J_e = self.elastic_component(K_I, youngs_modulus_GPa, poisson_ratio)
        J_p = self.plastic_component(yield_stress_MPa, crack_opening_displacement_mm)
        return J_e + J_p


class CTODCalculator:
    """
    Crack Tip Opening Displacement (CTOD) calculator.
    """
    
    def __init__(self):
        pass
    
    def from_K(self, K_I: float,
              yield_stress_MPa: float,
              youngs_modulus_GPa: float) -> float:
        """
        Compute CTOD from K_I.
        
        Args:
            K_I: Stress intensity factor
            yield_stress_MPa: Yield stress
            youngs_modulus_GPa: Young's modulus
        
        Returns:
            CTOD in mm
        """
        E = youngs_modulus_GPa * 1e3
        if yield_stress_MPa <= 0 or E <= 0:
            return 0.0
        return (K_I ** 2) / (yield_stress_MPa * E) * 1e3
    
    def from_J(self, J_kJ_m2: float,
              yield_stress_MPa: float,
              constraint_factor: float = 2.0) -> float:
        """
        Compute CTOD from J-integral.
        
        Args:
            J_kJ_m2: J-integral
            yield_stress_MPa: Yield stress
            constraint_factor: Constraint factor
        
        Returns:
            CTOD in mm
        """
        if yield_stress_MPa <= 0:
            return 0.0
        return J_kJ_m2 / (constraint_factor * yield_stress_MPa) * 1e3


class FractureMechanics:
    """
    Unified fracture mechanics controller.
    """
    
    def __init__(self):
        self.sif = StressIntensityFactor()
        self.paris = ParisLaw()
        self.j_integral = JIntegral()
        self.ctod = CTODCalculator()
    
    def fracture_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["SIF", "Paris_law", "J_integral", "CTOD"],
            "modes": ["Mode_I", "Mode_II", "Mode_III"]
        }
