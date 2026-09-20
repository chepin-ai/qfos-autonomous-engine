"""
Rheology Module
Viscosity measurement, shear stress analysis, elastic modulus,
loss modulus, and creep compliance for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RheologyPoint:
    """Rheology data point."""
    shear_rate_1_s: float
    shear_stress_Pa: float
    time_s: float


class ViscosityCalculator:
    """
    Calculate viscosity from rheological data.
    """
    
    def __init__(self):
        pass
    
    def newtonian_viscosity(self, shear_stress_Pa: float,
                           shear_rate_1_s: float) -> float:
        """
        Compute Newtonian viscosity.
        
        Args:
            shear_stress_Pa: Shear stress
            shear_rate_1_s: Shear rate
        
        Returns:
            Viscosity in Pa.s
        """
        if shear_rate_1_s <= 0:
            return 0.0
        return shear_stress_Pa / shear_rate_1_s
    
    def apparent_viscosity(self, points: List[RheologyPoint]) -> float:
        """
        Compute apparent viscosity.
        
        Args:
            points: Data points
        
        Returns:
            Apparent viscosity in Pa.s
        """
        if not points:
            return 0.0
        
        total_visc = 0.0
        count = 0
        for p in points:
            if p.shear_rate_1_s > 0:
                total_visc += p.shear_stress_Pa / p.shear_rate_1_s
                count += 1
        
        return total_visc / count if count > 0 else 0.0
    
    def power_law_viscosity(self, consistency_K: float,
                           power_index_n: float,
                           shear_rate_1_s: float) -> float:
        """
        Compute power-law viscosity.
        
        Args:
            consistency_K: Consistency index
            power_index_n: Power law index
            shear_rate_1_s: Shear rate
        
        Returns:
            Viscosity in Pa.s
        """
        if shear_rate_1_s <= 0:
            return 0.0
        return consistency_K * (shear_rate_1_s ** (power_index_n - 1.0))


class ShearStressAnalyzer:
    """
    Analyze shear stress behavior.
    """
    
    def __init__(self):
        pass
    
    def yield_stress(self, points: List[RheologyPoint]) -> float:
        """
        Estimate yield stress from data.
        
        Args:
            points: Data points
        
        Returns:
            Yield stress in Pa
        """
        if not points:
            return 0.0
        # Extrapolate to zero shear rate
        stresses = [p.shear_stress_Pa for p in points
                   if p.shear_rate_1_s > 0]
        return min(stresses) if stresses else 0.0
    
    def bingham_model(self, yield_stress_Pa: float,
                     plastic_viscosity_Pa_s: float,
                     shear_rate_1_s: float) -> float:
        """
        Bingham plastic model.
        
        Args:
            yield_stress_Pa: Yield stress
            plastic_viscosity_Pa_s: Plastic viscosity
            shear_rate_1_s: Shear rate
        
        Returns:
            Shear stress in Pa
        """
        return yield_stress_Pa + plastic_viscosity_Pa_s * shear_rate_1_s
    
    def casson_model(self, yield_stress_Pa: float,
                    casson_viscosity_Pa_s: float,
                    shear_rate_1_s: float) -> float:
        """
        Casson model.
        
        Args:
            yield_stress_Pa: Yield stress
            casson_viscosity_Pa_s: Casson viscosity
            shear_rate_1_s: Shear rate
        
        Returns:
            Shear stress in Pa
        """
        return (math.sqrt(yield_stress_Pa) +
                math.sqrt(casson_viscosity_Pa_s * shear_rate_1_s)) ** 2


class ModulusAnalyzer:
    """
    Analyze elastic and loss moduli.
    """
    
    def __init__(self):
        pass
    
    def storage_modulus(self, stress_amplitude_Pa: float,
                       strain_amplitude: float,
                       phase_angle_deg: float) -> float:
        """
        Compute storage modulus G'.
        
        Args:
            stress_amplitude_Pa: Stress amplitude
            strain_amplitude: Strain amplitude
            phase_angle_deg: Phase angle
        
        Returns:
            G' in Pa
        """
        if strain_amplitude <= 0:
            return 0.0
        ratio = stress_amplitude_Pa / strain_amplitude
        return ratio * math.cos(math.radians(phase_angle_deg))
    
    def loss_modulus(self, stress_amplitude_Pa: float,
                    strain_amplitude: float,
                    phase_angle_deg: float) -> float:
        """
        Compute loss modulus G''.
        
        Args:
            stress_amplitude_Pa: Stress amplitude
            strain_amplitude: Strain amplitude
            phase_angle_deg: Phase angle
        
        Returns:
            G'' in Pa
        """
        if strain_amplitude <= 0:
            return 0.0
        ratio = stress_amplitude_Pa / strain_amplitude
        return ratio * math.sin(math.radians(phase_angle_deg))
    
    def tan_delta(self, storage_modulus_Pa: float,
                 loss_modulus_Pa: float) -> float:
        """
        Compute tan(delta).
        
        Args:
            storage_modulus_Pa: G'
            loss_modulus_Pa: G''
        
        Returns:
            tan(delta)
        """
        if abs(storage_modulus_Pa) < 1e-10:
            return float('inf')
        return loss_modulus_Pa / storage_modulus_Pa
    
    def complex_modulus(self, storage_modulus_Pa: float,
                       loss_modulus_Pa: float) -> float:
        """
        Compute complex modulus.
        
        Args:
            storage_modulus_Pa: G'
            loss_modulus_Pa: G''
        
        Returns:
            |G*| in Pa
        """
        return math.sqrt(storage_modulus_Pa**2 + loss_modulus_Pa**2)


class CreepCompliance:
    """
    Creep compliance analysis.
    """
    
    def __init__(self):
        pass
    
    def compliance(self, strain: float,
                  applied_stress_Pa: float) -> float:
        """
        Compute compliance.
        
        Args:
            strain: Strain
            applied_stress_Pa: Applied stress
        
        Returns:
            Compliance in 1/Pa
        """
        if applied_stress_Pa <= 0:
            return 0.0
        return strain / applied_stress_Pa
    
    def maxwell_compliance(self, time_s: float,
                          elastic_modulus_Pa: float,
                          viscosity_Pa_s: float) -> float:
        """
        Maxwell model compliance.
        
        Args:
            time_s: Time
            elastic_modulus_Pa: Elastic modulus
            viscosity_Pa_s: Viscosity
        
        Returns:
            Compliance
        """
        if elastic_modulus_Pa <= 0 or viscosity_Pa_s <= 0:
            return 0.0
        return 1.0 / elastic_modulus_Pa + time_s / viscosity_Pa_s
    
    def kelvin_voigt_compliance(self, time_s: float,
                               elastic_modulus_Pa: float,
                               viscosity_Pa_s: float,
                               applied_stress_Pa: float) -> float:
        """
        Kelvin-Voigt model compliance.
        
        Args:
            time_s: Time
            elastic_modulus_Pa: Elastic modulus
            viscosity_Pa_s: Viscosity
            applied_stress_Pa: Applied stress
        
        Returns:
            Compliance
        """
        if elastic_modulus_Pa <= 0 or viscosity_Pa_s <= 0:
            return 0.0
        tau = viscosity_Pa_s / elastic_modulus_Pa
        return (applied_stress_Pa / elastic_modulus_Pa) * \
               (1.0 - math.exp(-time_s / tau))


class Rheology:
    """
    Unified rheology controller.
    """
    
    def __init__(self):
        self.viscosity = ViscosityCalculator()
        self.shear = ShearStressAnalyzer()
        self.modulus = ModulusAnalyzer()
        self.creep = CreepCompliance()
        self.points: List[RheologyPoint] = []
    
    def add_point(self, point: RheologyPoint):
        """
        Add data point.
        
        Args:
            point: Point
        """
        self.points.append(point)
    
    def analyze(self) -> Dict:
        """
        Analyze rheology data.
        
        Returns:
            Results
        """
        if not self.points:
            return {}
        
        app_visc = self.viscosity.apparent_viscosity(self.points)
        yield_stress = self.shear.yield_stress(self.points)
        
        # Compute moduli from last point
        last = self.points[-1]
        g_prime = self.modulus.storage_modulus(
            last.shear_stress_Pa, 0.1, 45.0)
        g_double = self.modulus.loss_modulus(
            last.shear_stress_Pa, 0.1, 45.0)
        tan_d = self.modulus.tan_delta(g_prime, g_double)
        
        return {
            "apparent_viscosity_Pa_s": app_visc,
            "yield_stress_Pa": yield_stress,
            "storage_modulus_Pa": g_prime,
            "loss_modulus_Pa": g_double,
            "tan_delta": tan_d,
            "points": len(self.points)
        }
    
    def rheo_summary(self) -> Dict:
        """Get summary."""
        return {
            "points": len(self.points),
            "methods": ["viscosity", "shear", "modulus", "creep"]
        }
