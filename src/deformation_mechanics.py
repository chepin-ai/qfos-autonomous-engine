"""
Deformation Mechanics Module
Elastic, plastic, creep,
and work hardening for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StressState:
    """Stress tensor components."""
    sigma_xx: float
    sigma_yy: float
    sigma_zz: float
    sigma_xy: float = 0.0
    sigma_yz: float = 0.0
    sigma_zx: float = 0.0


class ElasticDeformation:
    """
    Elastic deformation analysis.
    """
    
    def __init__(self, youngs_modulus_GPa: float = 200.0,
                 poisson_ratio: float = 0.3):
        """
        Args:
            youngs_modulus_GPa: Young's modulus
            poisson_ratio: Poisson's ratio
        """
        self.E = youngs_modulus_GPa
        self.nu = poisson_ratio
    
    def axial_strain(self, stress_MPa: float) -> float:
        """
        Compute axial strain from stress.
        
        Args:
            stress_MPa: Applied stress
        
        Returns:
            Strain
        """
        if self.E <= 0:
            return 0.0
        return stress_MPa / self.E
    
    def lateral_strain(self, axial_strain: float) -> float:
        """
        Compute lateral strain (Poisson effect).
        
        Args:
            axial_strain: Axial strain
        
        Returns:
            Lateral strain
        """
        return -self.nu * axial_strain
    
    def shear_modulus(self) -> float:
        """
        Compute shear modulus.
        
        Returns:
            G (GPa)
        """
        if self.nu == -1:
            return 0.0
        return self.E / (2.0 * (1.0 + self.nu))
    
    def bulk_modulus(self) -> float:
        """
        Compute bulk modulus.
        
        Returns:
            K (GPa)
        """
        if self.nu == 0.5:
            return float('inf')
        return self.E / (3.0 * (1.0 - 2.0 * self.nu))


class PlasticDeformation:
    """
    Plastic deformation and yield criteria.
    """
    
    def __init__(self, yield_strength_MPa: float = 250.0):
        """
        Args:
            yield_strength_MPa: Yield strength
        """
        self.sigma_y = yield_strength_MPa
    
    def von_mises_stress(self, stress: StressState) -> float:
        """
        Compute von Mises equivalent stress.
        
        Args:
            stress: Stress state
        
        Returns:
            von Mises stress (MPa)
        """
        s1 = stress.sigma_xx
        s2 = stress.sigma_yy
        s3 = stress.sigma_zz
        return math.sqrt(0.5 * ((s1-s2)**2 + (s2-s3)**2 + (s3-s1)**2) +
                        3.0 * (stress.sigma_xy**2 + stress.sigma_yz**2 + stress.sigma_zx**2))
    
    def is_yielding(self, stress: StressState) -> bool:
        """
        Check if von Mises stress exceeds yield.
        
        Args:
            stress: Stress state
        
        Returns:
            True if yielding
        """
        return self.von_mises_stress(stress) > self.sigma_y
    
    def safety_factor(self, stress: StressState) -> float:
        """
        Compute safety factor.
        
        Args:
            stress: Stress state
        
        Returns:
            Safety factor
        """
        vm = self.von_mises_stress(stress)
        if vm <= 0:
            return float('inf')
        return self.sigma_y / vm


class CreepDeformation:
    """
    Creep deformation modeling.
    """
    
    def __init__(self):
        pass
    
    def steady_state_creep_rate(self, stress_MPa: float,
                               activation_energy_J_mol: float = 2.5e5,
                               temperature_K: float = 800.0,
                               gas_constant: float = 8.314,
                               creep_exponent: float = 5.0,
                               pre_exponential: float = 1e-10) -> float:
        """
        Compute steady-state creep rate (power-law).
        
        Args:
            stress_MPa: Applied stress
            activation_energy_J_mol: Activation energy
            temperature_K: Temperature
            gas_constant: Gas constant
            creep_exponent: Stress exponent
            pre_exponential: Pre-exponential factor
        
        Returns:
            Creep rate (1/s)
        """
        if temperature_K <= 0:
            return 0.0
        return pre_exponential * (stress_MPa ** creep_exponent) * math.exp(-activation_energy_J_mol / (gas_constant * temperature_K))
    
    def creep_strain(self, creep_rate_s: float, time_s: float) -> float:
        """
        Compute creep strain.
        
        Args:
            creep_rate_s: Creep rate
            time_s: Time
        
        Returns:
            Creep strain
        """
        return creep_rate_s * time_s


class WorkHardening:
    """
    Work hardening modeling.
    """
    
    def __init__(self, strength_coefficient_MPa: float = 500.0,
                 hardening_exponent: float = 0.2):
        """
        Args:
            strength_coefficient_MPa: K
            hardening_exponent: n
        """
        self.K = strength_coefficient_MPa
        self.n = hardening_exponent
    
    def flow_stress(self, plastic_strain: float) -> float:
        """
        Compute flow stress (power-law hardening).
        
        Args:
            plastic_strain: Plastic strain
        
        Returns:
            Flow stress (MPa)
        """
        if plastic_strain <= 0:
            return 0.0
        return self.K * (plastic_strain ** self.n)
    
    def tangent_modulus(self, plastic_strain: float) -> float:
        """
        Compute tangent modulus.
        
        Args:
            plastic_strain: Plastic strain
        
        Returns:
            Tangent modulus (MPa)
        """
        if plastic_strain <= 0:
            return 0.0
        return self.K * self.n * (plastic_strain ** (self.n - 1.0))


class DeformationMechanics:
    """
    Unified deformation mechanics controller.
    """
    
    def __init__(self):
        self.elastic = ElasticDeformation()
        self.plastic = PlasticDeformation()
        self.creep = CreepDeformation()
        self.hardening = WorkHardening()
    
    def deformation_summary(self) -> Dict:
        """Get summary."""
        return {
            "regimes": ["elastic", "plastic", "creep"],
            "models": ["von_mises", "power_law_hardening", "power_law_creep"]
        }
