"""
Particle Size Analysis Module
Sieve analysis, laser diffraction, dynamic light scattering,
particle distribution, and surface area estimation for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Particle:
    """Individual particle."""
    diameter_um: float
    volume_um3: float


class SieveAnalysis:
    """
    Sieve analysis for particle size distribution.
    """
    
    def __init__(self):
        self.standard_sieves_um = [
            4000, 2000, 1000, 500, 250, 125, 63, 32, 16, 8
        ]
    
    def analyze(self, particles: List[Particle]) -> Dict[float, float]:
        """
        Analyze particle distribution by sieves.
        
        Args:
            particles: Particles
        
        Returns:
            Fraction retained on each sieve
        """
        if not particles:
            return {}
        
        total_mass = sum(p.volume_um3 for p in particles)
        if total_mass <= 0:
            return {}
        
        results = {}
        for i, sieve_size in enumerate(self.standard_sieves_um):
            if i == 0:
                # First sieve: everything larger
                retained = [p for p in particles
                           if p.diameter_um >= sieve_size]
            else:
                prev_size = self.standard_sieves_um[i - 1]
                retained = [p for p in particles
                           if prev_size > p.diameter_um >= sieve_size]
            
            mass = sum(p.volume_um3 for p in retained)
            results[sieve_size] = mass / total_mass
        
        # Pan fraction
        last = self.standard_sieves_um[-1]
        pan = [p for p in particles if p.diameter_um < last]
        pan_mass = sum(p.volume_um3 for p in pan)
        results[0] = pan_mass / total_mass
        
        return results
    
    def d50(self, particles: List[Particle]) -> float:
        """
        Compute median particle size.
        
        Args:
            particles: Particles
        
        Returns:
            D50 in um
        """
        if not particles:
            return 0.0
        
        diameters = sorted([p.diameter_um for p in particles])
        n = len(diameters)
        
        if n % 2 == 1:
            return diameters[n // 2]
        else:
            return (diameters[n // 2 - 1] + diameters[n // 2]) / 2.0


class LaserDiffraction:
    """
    Laser diffraction particle sizing.
    """
    
    def __init__(self, wavelength_nm: float = 633.0):
        """
        Args:
            wavelength_nm: Laser wavelength
        """
        self.wavelength = wavelength_nm
    
    def diffraction_angle(self, particle_diameter_um: float) -> float:
        """
        Compute diffraction angle.
        
        Args:
            particle_diameter_um: Particle diameter
        
        Returns:
            Angle in radians
        """
        if particle_diameter_um <= 0:
            return 0.0
        # Simplified: sin(theta) ~ lambda / d
        return self.wavelength / (particle_diameter_um * 1000.0)
    
    def size_from_angle(self, angle_rad: float) -> float:
        """
        Compute size from diffraction angle.
        
        Args:
            angle_rad: Diffraction angle
        
        Returns:
            Diameter in um
        """
        if angle_rad <= 0:
            return 0.0
        return self.wavelength / (angle_rad * 1000.0)


class DynamicLightScattering:
    """
    Dynamic light scattering analysis.
    """
    
    def __init__(self, temperature_K: float = 298.15,
                 viscosity_mPa_s: float = 0.89):
        """
        Args:
            temperature_K: Temperature
            viscosity_mPa_s: Viscosity
        """
        self.T = temperature_K
        self.eta = viscosity_mPa_s * 1e-3  # Pa.s
        self.k_B = 1.380649e-23  # J/K
    
    def hydrodynamic_diameter(self, diffusion_coefficient_m2_s: float) -> float:
        """
        Compute hydrodynamic diameter.
        
        Args:
            diffusion_coefficient_m2_s: Diffusion coefficient
        
        Returns:
            Diameter in nm
        """
        if diffusion_coefficient_m2_s <= 0:
            return 0.0
        # Stokes-Einstein: d = kT / (3 * pi * eta * D)
        d_m = self.k_B * self.T / (3.0 * math.pi * self.eta *
                                    diffusion_coefficient_m2_s)
        return d_m * 1e9  # nm
    
    def diffusion_coefficient(self, diameter_nm: float) -> float:
        """
        Compute diffusion coefficient.
        
        Args:
            diameter_nm: Diameter
        
        Returns:
            D in m2/s
        """
        if diameter_nm <= 0:
            return 0.0
        d_m = diameter_nm * 1e-9
        return self.k_B * self.T / (3.0 * math.pi * self.eta * d_m)


class ParticleDistribution:
    """
    Particle size distribution analysis.
    """
    
    def __init__(self):
        pass
    
    def mean_diameter(self, particles: List[Particle]) -> float:
        """
        Compute mean diameter.
        
        Args:
            particles: Particles
        
        Returns:
            Mean in um
        """
        if not particles:
            return 0.0
        return sum(p.diameter_um for p in particles) / len(particles)
    
    def std_deviation(self, particles: List[Particle]) -> float:
        """
        Compute standard deviation.
        
        Args:
            particles: Particles
        
        Returns:
            Std dev in um
        """
        if len(particles) < 2:
            return 0.0
        mean = self.mean_diameter(particles)
        variance = sum((p.diameter_um - mean)**2
                      for p in particles) / len(particles)
        return math.sqrt(variance)
    
    def span(self, particles: List[Particle]) -> float:
        """
        Compute distribution span.
        
        Args:
            particles: Particles
        
        Returns:
            Span
        """
        if not particles:
            return 0.0
        diameters = sorted([p.diameter_um for p in particles])
        n = len(diameters)
        d10 = diameters[n // 10] if n >= 10 else diameters[0]
        d90 = diameters[9 * n // 10] if n >= 10 else diameters[-1]
        d50 = diameters[n // 2]
        
        if d50 <= 0:
            return 0.0
        return (d90 - d10) / d50
    
    def specific_surface_area(self, particles: List[Particle],
                             density_g_cm3: float = 2.65) -> float:
        """
        Estimate specific surface area.
        
        Args:
            particles: Particles
            density_g_cm3: Density
        
        Returns:
            SSA in m2/g
        """
        if not particles:
            return 0.0
        
        # For spherical particles: SSA = 6 / (rho * d)
        mean_d_um = self.mean_diameter(particles)
        if mean_d_um <= 0:
            return 0.0
        
        # Convert um to m
        d_m = mean_d_um * 1e-6
        rho_kg_m3 = density_g_cm3 * 1000.0
        
        return 6.0 / (rho_kg_m3 * d_m) / 1000.0  # m2/g


class ParticleSizeAnalysis:
    """
    Unified particle size analysis controller.
    """
    
    def __init__(self):
        self.sieve = SieveAnalysis()
        self.laser = LaserDiffraction()
        self.dls = DynamicLightScattering()
        self.distribution = ParticleDistribution()
        self.particles: List[Particle] = []
    
    def load_particles(self, particles: List[Particle]):
        """
        Load particles.
        
        Args:
            particles: Particles
        """
        self.particles = particles
    
    def full_analysis(self) -> Dict:
        """
        Perform full analysis.
        
        Returns:
            Results
        """
        if not self.particles:
            return {}
        
        sieve_results = self.sieve.analyze(self.particles)
        d50 = self.sieve.d50(self.particles)
        mean = self.distribution.mean_diameter(self.particles)
        std = self.distribution.std_deviation(self.particles)
        span = self.distribution.span(self.particles)
        ssa = self.distribution.specific_surface_area(self.particles)
        
        return {
            "count": len(self.particles),
            "d50_um": d50,
            "mean_um": mean,
            "std_um": std,
            "span": span,
            "ssa_m2_g": ssa,
            "sieve_fractions": len(sieve_results)
        }
    
    def psa_summary(self) -> Dict:
        """Get summary."""
        return {
            "particles": len(self.particles),
            "methods": ["sieve", "laser", "dls"]
        }
