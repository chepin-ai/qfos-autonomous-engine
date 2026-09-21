"""
Tribology Module
Friction analysis, wear measurement, lubrication regimes,
Stribeck curve, and bearing life prediction for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FrictionMeasurement:
    """Friction measurement."""
    normal_force_N: float
    tangential_force_N: float
    velocity_ms: float
    temperature_c: float = 25.0


class FrictionAnalyzer:
    """
    Analyze friction coefficients.
    """
    
    def __init__(self):
        self.measurements: List[FrictionMeasurement] = []
    
    def coefficient(self, measurement: FrictionMeasurement) -> float:
        """
        Compute friction coefficient.
        
        Args:
            measurement: Measurement
        
        Returns:
            mu
        """
        if measurement.normal_force_N <= 0:
            return 0.0
        return measurement.tangential_force_N / measurement.normal_force_N
    
    def add_measurement(self, measurement: FrictionMeasurement):
        """
        Add measurement.
        
        Args:
            measurement: Measurement
        """
        self.measurements.append(measurement)
    
    def average_coefficient(self) -> float:
        """
        Compute average friction coefficient.
        
        Returns:
            Average mu
        """
        if not self.measurements:
            return 0.0
        coeffs = [self.coefficient(m) for m in self.measurements]
        return sum(coeffs) / len(coeffs)
    
    def stribeck_number(self, viscosity_pa_s: float,
                       velocity_ms: float,
                       load_pa: float) -> float:
        """
        Compute Stribeck number.
        
        Args:
            viscosity_pa_s: Dynamic viscosity
            velocity_ms: Velocity
            load_pa: Load pressure
        
        Returns:
            Stribeck number
        """
        if load_pa <= 0:
            return 0.0
        return (viscosity_pa_s * velocity_ms) / load_pa


class WearAnalyzer:
    """
    Analyze wear rates.
    """
    
    def __init__(self):
        self.wear_volume_mm3 = 0.0
        self.sliding_distance_m = 0.0
    
    def archard_wear_rate(self, wear_volume_mm3: float,
                         load_N: float,
                         sliding_distance_m: float) -> float:
        """
        Compute Archard wear coefficient.
        
        Args:
            wear_volume_mm3: Wear volume
            load_N: Normal load
            sliding_distance_m: Sliding distance
        
        Returns:
            Wear coefficient K
        """
        if load_N <= 0 or sliding_distance_m <= 0:
            return 0.0
        return wear_volume_mm3 / (load_N * sliding_distance_m)
    
    def wear_rate_per_distance(self, wear_volume_mm3: float,
                              sliding_distance_m: float) -> float:
        """
        Compute wear rate per distance.
        
        Args:
            wear_volume_mm3: Wear volume
            sliding_distance_m: Sliding distance
        
        Returns:
            Wear rate mm3/m
        """
        if sliding_distance_m <= 0:
            return 0.0
        return wear_volume_mm3 / sliding_distance_m
    
    def specific_wear_rate(self, wear_volume_mm3: float,
                          load_N: float,
                          sliding_distance_m: float) -> float:
        """
        Compute specific wear rate.
        
        Args:
            wear_volume_mm3: Wear volume
            load_N: Normal load
            sliding_distance_m: Sliding distance
        
        Returns:
            Specific wear rate mm3/Nm
        """
        if load_N <= 0 or sliding_distance_m <= 0:
            return 0.0
        return wear_volume_mm3 / (load_N * sliding_distance_m)


class LubricationRegime:
    """
    Determine lubrication regime.
    """
    
    def __init__(self):
        pass
    
    def regime(self, film_thickness_um: float,
              roughness_ra_um: float) -> str:
        """
        Determine lubrication regime.
        
        Args:
            film_thickness_um: Film thickness
            roughness_ra_um: Surface roughness
        
        Returns:
            Regime name
        """
        if roughness_ra_um <= 0:
            return "unknown"
        
        ratio = film_thickness_um / roughness_ra_um
        
        if ratio < 1.0:
            return "boundary"
        elif ratio < 3.0:
            return "mixed"
        elif ratio < 10.0:
            return "elastohydrodynamic"
        else:
            return "hydrodynamic"
    
    def lambda_ratio(self, film_thickness_um: float,
                    roughness1_ra_um: float,
                    roughness2_ra_um: float) -> float:
        """
        Compute lambda ratio.
        
        Args:
            film_thickness_um: Film thickness
            roughness1_ra_um: Roughness of surface 1
            roughness2_ra_um: Roughness of surface 2
        
        Returns:
            Lambda ratio
        """
        rms = math.sqrt(roughness1_ra_um ** 2 + roughness2_ra_um ** 2)
        if rms <= 0:
            return 0.0
        return film_thickness_um / rms


class BearingLifePredictor:
    """
    Predict bearing life.
    """
    
    def __init__(self):
        pass
    
    def l10_life(self, basic_rating_life: float,
                dynamic_load_N: float,
                equivalent_load_N: float) -> float:
        """
        Compute L10 bearing life.
        
        Args:
            basic_rating_life: C (basic dynamic load rating)
            dynamic_load_N: C
            equivalent_load_N: P (equivalent dynamic load)
        
        Returns:
            L10 life in millions of revolutions
        """
        if equivalent_load_N <= 0 or dynamic_load_N <= 0:
            return 0.0
        return (dynamic_load_N / equivalent_load_N) ** 3.0
    
    def adjusted_life(self, l10_life: float,
                     reliability_factor: float = 1.0,
                     material_factor: float = 1.0,
                     lubrication_factor: float = 1.0) -> float:
        """
        Compute adjusted bearing life.
        
        Args:
            l10_life: L10 life
            reliability_factor: a1
            material_factor: a2
            lubrication_factor: a3
        
        Returns:
            Adjusted life
        """
        return l10_life * reliability_factor * material_factor * lubrication_factor


class Tribology:
    """
    Unified tribology controller.
    """
    
    def __init__(self):
        self.friction = FrictionAnalyzer()
        self.wear = WearAnalyzer()
        self.lubrication = LubricationRegime()
        self.bearing = BearingLifePredictor()
        self.measurements: List[FrictionMeasurement] = []
    
    def test_friction(self, measurement: FrictionMeasurement) -> Dict:
        """
        Test friction.
        
        Args:
            measurement: Measurement
        
        Returns:
            Results
        """
        mu = self.friction.coefficient(measurement)
        self.measurements.append(measurement)
        
        return {
            "mu": mu,
            "normal_force_N": measurement.normal_force_N,
            "velocity_ms": measurement.velocity_ms
        }
    
    def tribo_summary(self) -> Dict:
        """Get summary."""
        return {
            "measurements": len(self.measurements),
            "methods": ["friction", "wear", "lubrication", "bearing_life"]
        }
