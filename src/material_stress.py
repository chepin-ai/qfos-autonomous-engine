"""
Material Stress Module
Stress tensor, strain analysis, fatigue, and yield
assessment for autonomous system structural health.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class StressState(Enum):
    """Material stress state."""
    ELASTIC = "elastic"
    PLASTIC = "plastic"
    YIELDED = "yielded"
    FRACTURED = "fractured"


@dataclass
class StressTensor:
    """3D stress tensor components."""
    sigma_x: float = 0.0
    sigma_y: float = 0.0
    sigma_z: float = 0.0
    tau_xy: float = 0.0
    tau_yz: float = 0.0
    tau_zx: float = 0.0
    
    def von_mises(self) -> float:
        """
        Compute von Mises equivalent stress.
        
        Returns:
            von Mises stress (Pa)
        """
        return math.sqrt(
            0.5 * ((self.sigma_x - self.sigma_y)**2 +
                   (self.sigma_y - self.sigma_z)**2 +
                   (self.sigma_z - self.sigma_x)**2) +
            3.0 * (self.tau_xy**2 + self.tau_yz**2 + self.tau_zx**2)
        )
    
    def hydrostatic(self) -> float:
        """
        Compute hydrostatic stress.
        
        Returns:
            Mean stress (Pa)
        """
        return (self.sigma_x + self.sigma_y + self.sigma_z) / 3.0
    
    def deviatoric(self) -> Tuple[float, float, float]:
        """
        Compute deviatoric stress components.
        
        Returns:
            (s_x, s_y, s_z)
        """
        p = self.hydrostatic()
        return (self.sigma_x - p, self.sigma_y - p, self.sigma_z - p)
    
    def principal_stresses(self) -> List[float]:
        """
        Compute principal stresses (simplified 2D approximation).
        
        Returns:
            Sorted principal stresses [max, mid, min]
        """
        # For general 3D we'd solve the characteristic equation
        # Simplified: assume tau_yz = tau_zx = 0
        avg = (self.sigma_x + self.sigma_y) / 2.0
        radius = math.sqrt(((self.sigma_x - self.sigma_y) / 2.0)**2 + self.tau_xy**2)
        
        p1 = avg + radius
        p2 = avg - radius
        p3 = self.sigma_z
        
        return sorted([p1, p2, p3], reverse=True)


class StrainAnalyzer:
    """
    Analyze material strain.
    """
    
    def __init__(self, youngs_modulus_Pa: float = 70e9,
                 poisson_ratio: float = 0.33):
        """
        Args:
            youngs_modulus_Pa: Young's modulus
            poisson_ratio: Poisson's ratio
        """
        self.E = youngs_modulus_Pa
        self.nu = poisson_ratio
    
    def normal_strain(self, stress_Pa: float) -> float:
        """
        Compute normal strain from stress.
        
        Args:
            stress_Pa: Normal stress
        
        Returns:
            Strain (dimensionless)
        """
        return stress_Pa / self.E
    
    def shear_strain(self, shear_stress_Pa: float) -> float:
        """
        Compute shear strain.
        
        Args:
            shear_stress_Pa: Shear stress
        
        Returns:
            Shear strain
        """
        G = self.E / (2.0 * (1.0 + self.nu))
        return shear_stress_Pa / G
    
    def strain_energy_density(self, stress: StressTensor) -> float:
        """
        Compute strain energy density.
        
        Args:
            stress: Stress tensor
        
        Returns:
            Energy density (J/m^3)
        """
        # U = 0.5 * sigma_ij * epsilon_ij
        ex = self.normal_strain(stress.sigma_x)
        ey = self.normal_strain(stress.sigma_y)
        ez = self.normal_strain(stress.sigma_z)
        
        gxy = self.shear_strain(stress.tau_xy)
        
        return 0.5 * (stress.sigma_x * ex + stress.sigma_y * ey +
                     stress.sigma_z * ez + stress.tau_xy * gxy)


class FatigueAnalyzer:
    """
    Analyze material fatigue life.
    """
    
    def __init__(self, endurance_limit_Pa: float = 100e6,
                 fatigue_strength_coeff: float = 1000e6,
                 fatigue_ductility_exponent: float = -0.1):
        """
        Args:
            endurance_limit_Pa: Endurance limit
            fatigue_strength_coeff: Fatigue strength coefficient
            fatigue_ductility_exponent: Fatigue ductility exponent
        """
        self.endurance_limit = endurance_limit_Pa
        self.fatigue_coeff = fatigue_strength_coeff
        self.fatigue_exp = fatigue_ductility_exponent
    
    def cycles_to_failure(self, stress_amplitude_Pa: float) -> float:
        """
        Estimate cycles to failure (Basquin relation).
        
        Args:
            stress_amplitude_Pa: Stress amplitude
        
        Returns:
            Cycles to failure
        """
        if stress_amplitude_Pa <= self.endurance_limit:
            return float('inf')
        
        # Basquin: sigma_a = sigma_f' * (2N)^b
        # N = 0.5 * (sigma_a / sigma_f')^(1/b)
        if self.fatigue_exp >= 0:
            return float('inf')
        
        return 0.5 * (stress_amplitude_Pa / self.fatigue_coeff) ** (1.0 / self.fatigue_exp)
    
    def miner_damage(self, stress_cycles: List[Tuple[float, float]]) -> float:
        """
        Compute Miner's rule cumulative damage.
        
        Args:
            stress_cycles: List of (stress_amplitude_Pa, cycles_applied)
        
        Returns:
            Cumulative damage ratio
        """
        damage = 0.0
        for stress_amp, cycles in stress_cycles:
            n_f = self.cycles_to_failure(stress_amp)
            if n_f != float('inf') and n_f > 0:
                damage += cycles / n_f
        return damage
    
    def remaining_life(self, stress_cycles: List[Tuple[float, float]]) -> float:
        """
        Estimate remaining life fraction.
        
        Args:
            stress_cycles: Applied stress history
        
        Returns:
            Remaining life fraction (1.0 = full life)
        """
        damage = self.miner_damage(stress_cycles)
        return max(0.0, 1.0 - damage)


class YieldAssessor:
    """
    Assess yield conditions.
    """
    
    def __init__(self, yield_strength_Pa: float = 250e6,
                 ultimate_strength_Pa: float = 400e6):
        """
        Args:
            yield_strength_Pa: Yield strength
            ultimate_strength_Pa: Ultimate tensile strength
        """
        self.yield_strength = yield_strength_Pa
        self.ultimate_strength = ultimate_strength_Pa
    
    def assess_von_mises(self, stress: StressTensor) -> StressState:
        """
        Assess state using von Mises criterion.
        
        Args:
            stress: Stress tensor
        
        Returns:
            Stress state
        """
        vm = stress.von_mises()
        
        if vm >= self.ultimate_strength:
            return StressState.FRACTURED
        elif vm >= self.yield_strength:
            return StressState.YIELDED
        elif vm >= self.yield_strength * 0.9:
            return StressState.PLASTIC
        else:
            return StressState.ELASTIC
    
    def safety_factor(self, stress: StressTensor) -> float:
        """
        Compute safety factor.
        
        Args:
            stress: Stress tensor
        
        Returns:
            Safety factor
        """
        vm = stress.von_mises()
        if vm <= 0:
            return float('inf')
        return self.yield_strength / vm
    
    def margin_of_safety(self, stress: StressTensor) -> float:
        """
        Compute margin of safety.
        
        Args:
            stress: Stress tensor
        
        Returns:
            Margin (positive = safe)
        """
        sf = self.safety_factor(stress)
        return sf - 1.0


class MaterialStress:
    """
    Unified material stress controller.
    """
    
    def __init__(self):
        self.strain = StrainAnalyzer()
        self.fatigue = FatigueAnalyzer()
        self.yield_assess = YieldAssessor()
        self.history: List[StressTensor] = []
    
    def record_stress(self, stress: StressTensor):
        """Record stress state."""
        self.history.append(stress)
    
    def current_state(self) -> StressState:
        """Get current stress state."""
        if not self.history:
            return StressState.ELASTIC
        return self.yield_assess.assess_von_mises(self.history[-1])
    
    def cumulative_damage(self) -> float:
        """Compute cumulative fatigue damage."""
        stress_cycles = []
        for i in range(1, len(self.history)):
            amp = abs(self.history[i].von_mises() - self.history[i-1].von_mises()) / 2.0
            if amp > 0:
                stress_cycles.append((amp, 1.0))
        return self.fatigue.miner_damage(stress_cycles)
    
    def structural_health(self) -> Dict:
        """
        Get structural health assessment.
        
        Returns:
            Health summary
        """
        if not self.history:
            return {"state": StressState.ELASTIC.value, "safety_factor": float('inf')}
        
        latest = self.history[-1]
        state = self.yield_assess.assess_von_mises(latest)
        sf = self.yield_assess.safety_factor(latest)
        damage = self.cumulative_damage()
        
        return {
            "state": state.value,
            "von_mises_MPa": latest.von_mises() / 1e6,
            "safety_factor": sf,
            "margin_of_safety": self.yield_assess.margin_of_safety(latest),
            "cumulative_damage": damage,
            "remaining_life": max(0.0, 1.0 - damage),
            "records": len(self.history)
        }
