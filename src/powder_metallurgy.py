"""
Powder Metallurgy Module
Powder characterization, compaction,
sintering kinetics, density and porosity for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PowderProperties:
    """Powder particle properties."""
    d10_um: float
    d50_um: float
    d90_um: float
    apparent_density_g_cm3: float
    tap_density_g_cm3: float


class PowderCharacterization:
    """
    Powder particle characterization.
    """
    
    def __init__(self):
        pass
    
    def span(self, powder: PowderProperties) -> float:
        """
        Compute powder span (distribution width).
        
        Args:
            powder: Powder properties
        
        Returns:
            Span
        """
        if powder.d50_um <= 0:
            return 0.0
        return (powder.d90_um - powder.d10_um) / powder.d50_um
    
    def hausner_ratio(self, powder: PowderProperties) -> float:
        """
        Compute Hausner ratio (flowability indicator).
        
        Args:
            powder: Powder properties
        
        Returns:
            Hausner ratio
        """
        if powder.apparent_density_g_cm3 <= 0:
            return 0.0
        return powder.tap_density_g_cm3 / powder.apparent_density_g_cm3
    
    def carr_index(self, powder: PowderProperties) -> float:
        """
        Compute Carr index (%).
        
        Args:
            powder: Powder properties
        
        Returns:
            Carr index
        """
        if powder.tap_density_g_cm3 <= 0:
            return 0.0
        return 100.0 * (powder.tap_density_g_cm3 - powder.apparent_density_g_cm3) / powder.tap_density_g_cm3


class PowderCompaction:
    """
    Powder compaction analysis.
    """
    
    def __init__(self):
        pass
    
    def green_density(self, powder_mass_g: float,
                     compact_volume_cm3: float) -> float:
        """
        Compute green density.
        
        Args:
            powder_mass_g: Powder mass
            compact_volume_cm3: Compact volume
        
        Returns:
            Green density (g/cm^3)
        """
        if compact_volume_cm3 <= 0:
            return 0.0
        return powder_mass_g / compact_volume_cm3
    
    def compaction_pressure(self, yield_strength_MPa: float,
                           relative_density: float,
                           friction_coefficient: float = 0.2) -> float:
        """
        Estimate required compaction pressure.
        
        Args:
            yield_strength_MPa: Material yield strength
            relative_density: Relative density
            friction_coefficient: Die wall friction
        
        Returns:
            Pressure (MPa)
        """
        if relative_density >= 1.0 or relative_density <= 0:
            return 0.0
        # Simplified: pressure increases with density
        return yield_strength_MPa * math.log(1.0 / (1.0 - relative_density)) * (1.0 + friction_coefficient)
    
    def relative_density(self, green_density: float,
                        theoretical_density: float) -> float:
        """
        Compute relative density.
        
        Args:
            green_density: Green density
            theoretical_density: Theoretical density
        
        Returns:
            Relative density
        """
        if theoretical_density <= 0:
            return 0.0
        return green_density / theoretical_density


class SinteringKinetics:
    """
    Sintering kinetics and densification.
    """
    
    def __init__(self):
        pass
    
    def arrhenius_rate(self, temperature_K: float,
                      activation_energy_J_mol: float,
                      pre_exponential: float = 1e10) -> float:
        """
        Compute Arrhenius rate constant.
        
        Args:
            temperature_K: Temperature
            activation_energy_J_mol: Activation energy
            pre_exponential: Pre-exponential factor
        
        Returns:
            Rate constant
        """
        R = 8.314
        if temperature_K <= 0:
            return 0.0
        return pre_exponential * math.exp(-activation_energy_J_mol / (R * temperature_K))
    
    def densification(self, initial_density: float,
                     time_s: float,
                     rate_constant: float,
                     final_density: float = 0.98) -> float:
        """
        Compute density after sintering.
        
        Args:
            initial_density: Initial relative density
            time_s: Sintering time
            rate_constant: Rate constant
            final_density: Final density limit
        
        Returns:
            Current density
        """
        if rate_constant <= 0:
            return initial_density
        # Simplified: exponential approach to final density
        return final_density - (final_density - initial_density) * math.exp(-rate_constant * time_s)
    
    def grain_growth(self, initial_grain_size_um: float,
                    time_s: float,
                    growth_rate_um_s: float) -> float:
        """
        Estimate grain size after sintering.
        
        Args:
            initial_grain_size_um: Initial grain size
            time_s: Time
            growth_rate_um_s: Growth rate
        
        Returns:
            Grain size
        """
        # Simplified: parabolic growth
        return math.sqrt(initial_grain_size_um**2 + growth_rate_um_s * time_s)


class PorosityAnalysis:
    """
    Porosity and density analysis.
    """
    
    def __init__(self):
        pass
    
    def porosity(self, density: float,
                theoretical_density: float) -> float:
        """
        Compute porosity fraction.
        
        Args:
            density: Measured density
            theoretical_density: Theoretical density
        
        Returns:
            Porosity
        """
        if theoretical_density <= 0:
            return 0.0
        return 1.0 - density / theoretical_density
    
    def open_porosity(self, apparent_density: float,
                     bulk_density: float) -> float:
        """
        Compute open porosity.
        
        Args:
            apparent_density: Apparent density
            bulk_density: Bulk density
        
        Returns:
            Open porosity
        """
        if bulk_density <= 0:
            return 0.0
        return (bulk_density - apparent_density) / bulk_density


class PowderMetallurgy:
    """
    Unified powder metallurgy controller.
    """
    
    def __init__(self):
        self.characterization = PowderCharacterization()
        self.compaction = PowderCompaction()
        self.sintering = SinteringKinetics()
        self.porosity = PorosityAnalysis()
    
    def metallurgy_summary(self) -> Dict:
        """Get summary."""
        return {
            "processes": ["characterization", "compaction", "sintering"],
            "properties": ["density", "porosity", "grain_size"]
        }
