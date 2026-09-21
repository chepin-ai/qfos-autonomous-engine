"""
Solidification Modeling Module
Nucleation, growth kinetics,
Scheil equation, and microsegregation for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AlloyComposition:
    """Alloy composition data."""
    element: str
    concentration_wt: float


class NucleationModeling:
    """
    Homogeneous and heterogeneous nucleation modeling.
    """
    
    def __init__(self):
        pass
    
    def homogeneous_nucleation_rate(self, undercooling_K: float,
                                   interfacial_energy_J_m2: float = 0.2,
                                   melting_temperature_K: float = 1800.0,
                                   latent_heat_J_m3: float = 2e9) -> float:
        """
        Compute homogeneous nucleation rate.
        
        Args:
            undercooling_K: Undercooling
            interfacial_energy_J_m2: Surface energy
            melting_temperature_K: Melting point
            latent_heat_J_m3: Latent heat
        
        Returns:
            Nucleation rate (1/m^3/s)
        """
        if undercooling_K <= 0:
            return 0.0
        # Simplified: I = I0 * exp(-A / dT^2)
        A = (16.0 * math.pi * interfacial_energy_J_m2**3 * melting_temperature_K**2) / (3.0 * latent_heat_J_m3**2)
        return 1e30 * math.exp(-A / undercooling_K**2)
    
    def critical_radius(self, undercooling_K: float,
                       interfacial_energy_J_m2: float = 0.2,
                       latent_heat_J_m3: float = 2e9) -> float:
        """
        Compute critical nucleus radius.
        
        Args:
            undercooling_K: Undercooling
            interfacial_energy_J_m2: Surface energy
            latent_heat_J_m3: Latent heat
        
        Returns:
            Radius (m)
        """
        if undercooling_K <= 0:
            return float('inf')
        return (2.0 * interfacial_energy_J_m2) / latent_heat_J_m3 / undercooling_K


class GrowthKinetics:
    """
    Crystal growth kinetics.
    """
    
    def __init__(self):
        pass
    
    def dendrite_tip_velocity(self, undercooling_K: float,
                             diffusion_coefficient_m2_s: float = 1e-9,
                             capillary_length_m: float = 1e-9) -> float:
        """
        Compute dendrite tip velocity (LGK model simplified).
        
        Args:
            undercooling_K: Undercooling
            diffusion_coefficient_m2_s: Diffusivity
            capillary_length_m: Capillary length
        
        Returns:
            Velocity (m/s)
        """
        if undercooling_K <= 0 or capillary_length_m <= 0:
            return 0.0
        # Simplified: v proportional to D * dT / (capillary_length * undercooling)
        return diffusion_coefficient_m2_s * undercooling_K / (capillary_length_m * 10.0)
    
    def secondary_dendrite_arm_spacing(self, local_solidification_time_s: float,
                                      diffusion_coefficient_m2_s: float = 1e-13) -> float:
        """
        Compute secondary dendrite arm spacing.
        
        Args:
            local_solidification_time_s: Local solidification time
            diffusion_coefficient_m2_s: Diffusivity
        
        Returns:
            SDAS (m)
        """
        if local_solidification_time_s <= 0:
            return 0.0
        return 5.0 * (diffusion_coefficient_m2_s * local_solidification_time_s) ** 0.33


class ScheilEquation:
    """
    Scheil-Gulliver equation for microsegregation.
    """
    
    def __init__(self):
        pass
    
    def solid_composition(self, initial_composition: float,
                         partition_coefficient: float,
                         fraction_solid: float) -> float:
        """
        Compute solid composition using Scheil equation.
        
        Args:
            initial_composition: C0
            partition_coefficient: k
            fraction_solid: fs
        
        Returns:
            Solid composition
        """
        if fraction_solid < 0 or fraction_solid >= 1.0:
            return initial_composition
        if partition_coefficient <= 0:
            return initial_composition
        return initial_composition * partition_coefficient * (1.0 - fraction_solid) ** (partition_coefficient - 1.0)
    
    def liquid_composition(self, initial_composition: float,
                          partition_coefficient: float,
                          fraction_solid: float) -> float:
        """
        Compute liquid composition.
        
        Args:
            initial_composition: C0
            partition_coefficient: k
            fraction_solid: fs
        
        Returns:
            Liquid composition
        """
        if fraction_solid < 0 or fraction_solid >= 1.0:
            return initial_composition
        return initial_composition * (1.0 - fraction_solid) ** (partition_coefficient - 1.0)
    
    def final_eutectic_fraction(self, initial_composition: float,
                               partition_coefficient: float,
                               eutectic_composition: float) -> float:
        """
        Compute fraction solidified at eutectic.
        
        Args:
            initial_composition: C0
            partition_coefficient: k
            eutectic_composition: Ce
        
        Returns:
            Fraction solid
        """
        if eutectic_composition <= 0 or initial_composition <= 0 or partition_coefficient >= 1.0:
            return 0.0
        ratio = eutectic_composition / initial_composition
        return 1.0 - ratio ** (1.0 / (partition_coefficient - 1.0))


class Microsegregation:
    """
    Microsegregation analysis.
    """
    
    def __init__(self):
        pass
    
    def lever_rule_composition(self, initial_composition: float,
                              partition_coefficient: float,
                              fraction_solid: float) -> float:
        """
        Compute solid composition using lever rule.
        
        Args:
            initial_composition: C0
            partition_coefficient: k
            fraction_solid: fs
        
        Returns:
            Solid composition
        """
        if fraction_solid < 0 or fraction_solid > 1.0:
            return initial_composition
        denom = 1.0 - fraction_solid + partition_coefficient * fraction_solid
        if denom <= 0:
            return initial_composition
        return initial_composition / denom
    
    def segregation_ratio(self, max_composition: float,
                         min_composition: float) -> float:
        """
        Compute segregation ratio.
        
        Args:
            max_composition: Maximum composition
            min_composition: Minimum composition
        
        Returns:
            Segregation ratio
        """
        if min_composition <= 0:
            return 0.0
        return max_composition / min_composition


class SolidificationModeling:
    """
    Unified solidification modeling controller.
    """
    
    def __init__(self):
        self.nucleation = NucleationModeling()
        self.growth = GrowthKinetics()
        self.scheil = ScheilEquation()
        self.microsegregation = Microsegregation()
    
    def solidification_summary(self) -> Dict:
        """Get summary."""
        return {
            "models": ["nucleation", "growth", "scheil", "microsegregation"],
            "outputs": ["nucleation_rate", "growth_velocity", "composition_profile"]
        }
