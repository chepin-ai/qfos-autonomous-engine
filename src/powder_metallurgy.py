"""
Powder Metallurgy Module
Powder characterization, compaction modeling,
sintering kinetics, and densification for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PowderParticle:
    """Powder particle properties."""
    diameter_um: float
    density_g_cm3: float


class PowderCharacterization:
    """
    Powder particle size and shape characterization.
    """
    
    def __init__(self):
        pass
    
    def sauter_mean_diameter(self, particles: List[PowderParticle]) -> float:
        """
        Compute Sauter mean diameter.
        
        Args:
            particles: Particle list
        
        Returns:
            SMD (um)
        """
        if not particles:
            return 0.0
        num = sum(p.diameter_um ** 3 for p in particles)
        den = sum(p.diameter_um ** 2 for p in particles)
        if den <= 0:
            return 0.0
        return num / den
    
    def packing_density(self, particles: List[PowderParticle],
                       bulk_density_g_cm3: float) -> float:
        """
        Compute packing density (relative density).
        
        Args:
            particles: Particle list
            bulk_density_g_cm3: Bulk density
        
        Returns:
            Packing density
        """
        if not particles:
            return 0.0
        true_density = sum(p.density_g_cm3 for p in particles) / len(particles)
        if true_density <= 0:
            return 0.0
        return bulk_density_g_cm3 / true_density
    
    void_fraction = packing_density
    
    def specific_surface_area(self, particles: List[PowderParticle]) -> float:
        """
        Compute specific surface area (simplified spherical).
        
        Args:
            particles: Particle list
        
        Returns:
            SSA (m2/g)
        """
        if not particles:
            return 0.0
        # For spheres: SSA = 6 / (rho * d)
        total_sa = sum(math.pi * p.diameter_um**2 for p in particles)
        total_mass = sum((math.pi / 6.0) * p.diameter_um**3 * p.density_g_cm3 for p in particles)
        if total_mass <= 0:
            return 0.0
        # Convert to m2/g
        return (total_sa * 1e-12) / (total_mass * 1e-6)


class CompactionModeling:
    """
    Powder compaction modeling.
    """
    
    def __init__(self):
        pass
    
    def relative_density(self, green_density_g_cm3: float,
                        theoretical_density_g_cm3: float = 7.87) -> float:
        """
        Compute relative density.
        
        Args:
            green_density_g_cm3: Green density
            theoretical_density_g_cm3: Theoretical density
        
        Returns:
            Relative density
        """
        if theoretical_density_g_cm3 <= 0:
            return 0.0
        return green_density_g_cm3 / theoretical_density_g_cm3
    
    void_fraction = relative_density
    
    def compaction_pressure(self, yield_strength_MPa: float,
                           relative_density: float,
                           friction_coefficient: float = 0.2) -> float:
        """
        Estimate compaction pressure (simplified).
        
        Args:
            yield_strength_MPa: Material yield strength
            relative_density: Target relative density
            friction_coefficient: Die friction
        
        Returns:
            Pressure (MPa)
        """
        if relative_density >= 1.0 or relative_density <= 0:
            return 0.0
        # Simplified: pressure increases with density
        return yield_strength_MPa * math.log(1.0 / (1.0 - relative_density)) * (1.0 + friction_coefficient)


class SinteringKinetics:
    """
    Sintering kinetics modeling.
    """
    
    def __init__(self):
        pass
    
    def densification_rate(self, time_s: float,
                          activation_energy_J_mol: float = 2e5,
                          temperature_K: float = 1500.0,
                          gas_constant: float = 8.314) -> float:
        """
        Compute densification rate (simplified Arrhenius).
        
        Args:
            time_s: Time
            activation_energy_J_mol: Activation energy
            temperature_K: Temperature
            gas_constant: Gas constant
        
        Returns:
            Densification rate
        """
        if time_s <= 0 or temperature_K <= 0:
            return 0.0
        # Simplified: rate proportional to exp(-E/RT) * t^n
        rate = math.exp(-activation_energy_J_mol / (gas_constant * temperature_K))
        return rate * (time_s ** 0.5)
    
    def neck_growth_ratio(self, time_s: float,
                         diffusion_coefficient_m2_s: float = 1e-12,
                         particle_radius_m: float = 1e-5) -> float:
        """
        Compute neck growth ratio (x/r).
        
        Args:
            time_s: Time
            diffusion_coefficient_m2_s: Diffusivity
            particle_radius_m: Particle radius
        
        Returns:
            Neck growth ratio
        """
        if time_s <= 0 or particle_radius_m <= 0:
            return 0.0
        # Simplified: x/r ~ (Dt/r^2)^0.2
        return (diffusion_coefficient_m2_s * time_s / particle_radius_m**2) ** 0.2


class Densification:
    """
    Densification analysis.
    """
    
    def __init__(self):
        pass
    
    def final_density(self, green_density_g_cm3: float,
                     sintering_shrinkage_pct: float = 15.0) -> float:
        """
        Estimate final density from shrinkage.
        
        Args:
            green_density_g_cm3: Green density
            sintering_shrinkage_pct: Linear shrinkage
        
        Returns:
            Final density
        """
        # Volume change ~ (1 - shrinkage)^3
        vol_factor = (1.0 - sintering_shrinkage_pct / 100.0) ** 3
        if vol_factor <= 0:
            return green_density_g_cm3
        return green_density_g_cm3 / vol_factor
    
    def shrinkage_from_density(self, green_density_g_cm3: float,
                              final_density_g_cm3: float) -> float:
        """
        Compute shrinkage from density change.
        
        Args:
            green_density_g_cm3: Green density
            final_density_g_cm3: Final density
        
        Returns:
            Linear shrinkage (%)
        """
        if final_density_g_cm3 <= 0 or green_density_g_cm3 <= 0:
            return 0.0
        vol_ratio = green_density_g_cm3 / final_density_g_cm3
        linear_shrinkage = 1.0 - vol_ratio ** (1.0 / 3.0)
        return linear_shrinkage * 100.0


class PowderMetallurgy:
    """
    Unified powder metallurgy controller.
    """
    
    def __init__(self):
        self.characterization = PowderCharacterization()
        self.compaction = CompactionModeling()
        self.sintering = SinteringKinetics()
        self.densification = Densification()
    
    def powder_summary(self) -> Dict:
        """Get summary."""
        return {
            "processes": ["characterization", "compaction", "sintering", "densification"],
            "outputs": ["smd", "relative_density", "shrinkage"]
        }
