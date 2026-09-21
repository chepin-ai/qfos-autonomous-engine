"""
Thermal Barrier Coatings Module
Ceramic topcoat analysis, bond coat oxidation,
temperature gradient, and thermal cycling for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CoatingLayer:
    """Coating layer properties."""
    thickness_mm: float
    thermal_conductivity_W_mK: float
    thermal_expansion_um_mK: float


class ThermalGradient:
    """
    Temperature gradient analysis across coating system.
    """
    
    def __init__(self):
        pass
    
    def temperature_drop(self, heat_flux_MW_m2: float,
                        thickness_m: float,
                        conductivity_W_mK: float) -> float:
        """
        Compute temperature drop across layer.
        
        Args:
            heat_flux_MW_m2: Heat flux
            thickness_m: Layer thickness
            conductivity_W_mK: Thermal conductivity
        
        Returns:
            Temperature drop (K)
        """
        if conductivity_W_mK <= 0:
            return 0.0
        return heat_flux_MW_m2 * 1e6 * thickness_m / conductivity_W_mK
    
    def interface_temperature(self, hot_side_K: float,
                             temperature_drops: List[float]) -> List[float]:
        """
        Compute temperatures at each interface.
        
        Args:
            hot_side_K: Hot side temperature
            temperature_drops: Temperature drops per layer
        
        Returns:
            Interface temperatures
        """
        temps = [hot_side_K]
        current = hot_side_K
        for drop in temperature_drops:
            current -= drop
            temps.append(current)
        return temps


class BondCoatOxidation:
    """
    Bond coat thermally grown oxide (TGO) growth.
    """
    
    def __init__(self):
        pass
    
    def parabolic_growth(self, time_h: float,
                        kp_um2_h: float) -> float:
        """
        Compute TGO thickness (parabolic growth).
        
        Args:
            time_h: Time
            kp_um2_h: Parabolic rate constant
        
        Returns:
            TGO thickness (um)
        """
        return math.sqrt(kp_um2_h * time_h)
    
    def growth_rate_constant(self, temperature_K: float,
                            activation_energy_J_mol: float = 250000.0,
                            pre_exp_um2_h: float = 1e6) -> float:
        """
        Compute temperature-dependent growth rate constant.
        
        Args:
            temperature_K: Temperature
            activation_energy_J_mol: Activation energy
            pre_exp_um2_h: Pre-exponential
        
        Returns:
            kp (um^2/h)
        """
        R = 8.314
        if temperature_K <= 0:
            return 0.0
        return pre_exp_um2_h * math.exp(-activation_energy_J_mol / (R * temperature_K))


class ThermalCycling:
    """
    Thermal cycling fatigue analysis.
    """
    
    def __init__(self):
        pass
    
    def thermal_strain(self, delta_T_K: float,
                      thermal_expansion_um_mK: float) -> float:
        """
        Compute thermal strain.
        
        Args:
            delta_T_K: Temperature change
            thermal_expansion_um_mK: CTE
        
        Returns:
            Strain
        """
        return thermal_expansion_um_mK * 1e-6 * delta_T_K
    
    def stress_from_strain(self, strain: float,
                          youngs_modulus_GPa: float) -> float:
        """
        Compute thermal stress.
        
        Args:
            strain: Strain
            youngs_modulus_GPa: Young's modulus
        
        Returns:
            Stress (MPa)
        """
        return strain * youngs_modulus_GPa * 1e3
    
    def cycles_to_failure(self, stress_range_MPa: float,
                         fatigue_strength_MPa: float = 400.0,
                         fatigue_exponent: float = -0.1) -> float:
        """
        Estimate cycles to failure (Basquin-like).
        
        Args:
            stress_range_MPa: Stress range
            fatigue_strength_MPa: Fatigue strength coefficient
            fatigue_exponent: Fatigue exponent
        
        Returns:
            Cycles
        """
        if stress_range_MPa <= 0:
            return float('inf')
        return (stress_range_MPa / fatigue_strength_MPa) ** (1.0 / fatigue_exponent)


class CoatingDurability:
    """
    Coating system durability assessment.
    """
    
    def __init__(self):
        pass
    
    def thermal_shock_parameter(self, fracture_toughness_MPa_sqrt_m: float,
                               thermal_conductivity_W_mK: float,
                               youngs_modulus_GPa: float,
                               thermal_expansion_um_mK: float) -> float:
        """
        Compute thermal shock resistance parameter.
        
        Args:
            fracture_toughness_MPa_sqrt_m: K_IC
            thermal_conductivity_W_mK: Conductivity
            youngs_modulus_GPa: Young's modulus
            thermal_expansion_um_mK: CTE
        
        Returns:
            Thermal shock parameter
        """
        if thermal_expansion_um_mK <= 0 or youngs_modulus_GPa <= 0:
            return 0.0
        return fracture_toughness_MPa_sqrt_m * thermal_conductivity_W_mK / (youngs_modulus_GPa * thermal_expansion_um_mK)
    
    def spallation_life(self, max_stress_MPa: float,
                       adhesion_strength_MPa: float = 50.0) -> float:
        """
        Estimate spallation life.
        
        Args:
            max_stress_MPa: Maximum stress
            adhesion_strength_MPa: Coating adhesion
        
        Returns:
            Life fraction
        """
        if adhesion_strength_MPa <= 0:
            return 0.0
        return adhesion_strength_MPa / max_stress_MPa


class ThermalBarrierCoatings:
    """
    Unified thermal barrier coating controller.
    """
    
    def __init__(self):
        self.gradient = ThermalGradient()
        self.oxidation = BondCoatOxidation()
        self.cycling = ThermalCycling()
        self.durability = CoatingDurability()
    
    def tbc_summary(self) -> Dict:
        """Get summary."""
        return {
            "layers": ["topcoat", "TGO", "bond_coat", "substrate"],
            "analyses": ["thermal_gradient", "oxidation", "cycling", "durability"]
        }
