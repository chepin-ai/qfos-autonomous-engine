"""
Rheology Module
Viscosity, shear stress, creep compliance,
stress relaxation, and viscoelastic models for autonomous materials science.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ShearPoint:
    """Shear rheology data point."""
    shear_rate_s: float
    shear_stress_Pa: float
    viscosity_Pa_s: float


class NewtonianFluid:
    """
    Newtonian fluid model.
    """
    
    def __init__(self, viscosity_Pa_s: float = 1.0):
        """
        Args:
            viscosity_Pa_s: Dynamic viscosity
        """
        self.viscosity = viscosity_Pa_s
    
    def shear_stress(self, shear_rate_s: float) -> float:
        """
        Compute shear stress.
        
        Args:
            shear_rate_s: Shear rate
        
        Returns:
            Shear stress in Pa
        """
        return self.viscosity * shear_rate_s
    
    def reynolds_number(self, density_kg_m3: float,
                       velocity_m_s: float,
                       characteristic_length_m: float) -> float:
        """
        Compute Reynolds number.
        
        Args:
            density_kg_m3: Density
            velocity_m_s: Velocity
            characteristic_length_m: Characteristic length
        
        Returns:
            Reynolds number
        """
        if self.viscosity <= 0:
            return 0.0
        return (density_kg_m3 * velocity_m_s * characteristic_length_m) / self.viscosity


class PowerLawFluid:
    """
    Power-law (Ostwald-de Waele) fluid model.
    """
    
    def __init__(self, consistency_index_Pa_s_n: float = 1.0,
                 flow_index: float = 1.0):
        """
        Args:
            consistency_index_Pa_s_n: Consistency index K
            flow_index: Flow behavior index n
        """
        self.K = consistency_index_Pa_s_n
        self.n = flow_index
    
    def shear_stress(self, shear_rate_s: float) -> float:
        """
        Compute shear stress.
        
        Args:
            shear_rate_s: Shear rate
        
        Returns:
            Shear stress in Pa
        """
        return self.K * (abs(shear_rate_s) ** self.n)
    
    def apparent_viscosity(self, shear_rate_s: float) -> float:
        """
        Compute apparent viscosity.
        
        Args:
            shear_rate_s: Shear rate
        
        Returns:
            Apparent viscosity in Pa.s
        """
        if shear_rate_s == 0:
            return float('inf') if self.n < 1 else self.K
        return self.K * (abs(shear_rate_s) ** (self.n - 1.0))


class MaxwellModel:
    """
    Maxwell viscoelastic model.
    """
    
    def __init__(self, elastic_modulus_Pa: float = 1e6,
                 viscosity_Pa_s: float = 1e3):
        """
        Args:
            elastic_modulus_Pa: Elastic modulus
            viscosity_Pa_s: Viscosity
        """
        self.E = elastic_modulus_Pa
        self.eta = viscosity_Pa_s
    
    def relaxation_time(self) -> float:
        """
        Compute relaxation time.
        
        Returns:
            Relaxation time in s
        """
        if self.E <= 0:
            return 0.0
        return self.eta / self.E
    
    def stress_relaxation(self, initial_stress_Pa: float,
                         time_s: float) -> float:
        """
        Compute stress at time t after step strain.
        
        Args:
            initial_stress_Pa: Initial stress
            time_s: Time
        
        Returns:
            Stress in Pa
        """
        tau = self.relaxation_time()
        if tau <= 0:
            return initial_stress_Pa
        return initial_stress_Pa * math.exp(-time_s / tau)
    
    def creep_compliance(self, time_s: float) -> float:
        """
        Compute creep compliance J(t).
        
        Args:
            time_s: Time
        
        Returns:
            Compliance in 1/Pa
        """
        if self.E <= 0:
            return 0.0
        tau = self.relaxation_time()
        return 1.0 / self.E + time_s / self.eta if self.eta > 0 else 1.0 / self.E


class KelvinVoigtModel:
    """
    Kelvin-Voigt viscoelastic model.
    """
    
    def __init__(self, elastic_modulus_Pa: float = 1e6,
                 viscosity_Pa_s: float = 1e3):
        """
        Args:
            elastic_modulus_Pa: Elastic modulus
            viscosity_Pa_s: Viscosity
        """
        self.E = elastic_modulus_Pa
        self.eta = viscosity_Pa_s
    
    def retardation_time(self) -> float:
        """
        Compute retardation time.
        
        Returns:
            Retardation time in s
        """
        if self.E <= 0:
            return 0.0
        return self.eta / self.E
    
    def creep_strain(self, applied_stress_Pa: float,
                    time_s: float) -> float:
        """
        Compute creep strain.
        
        Args:
            applied_stress_Pa: Applied stress
            time_s: Time
        
        Returns:
            Strain
        """
        if self.E <= 0:
            return 0.0
        tau = self.retardation_time()
        return (applied_stress_Pa / self.E) * (1.0 - math.exp(-time_s / tau))


class Rheology:
    """
    Unified rheology controller.
    """
    
    def __init__(self):
        self.newtonian = NewtonianFluid()
        self.power_law = PowerLawFluid()
        self.maxwell = MaxwellModel()
        self.kelvin_voigt = KelvinVoigtModel()
    
    def rheology_summary(self) -> Dict:
        """Get summary."""
        return {
            "models": ["newtonian", "power_law", "maxwell", "kelvin_voigt"],
            "properties": ["viscosity", "shear_stress", "creep", "relaxation"]
        }
