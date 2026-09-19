"""
Orbit Lifetime Module
Estimate orbital lifetime from atmospheric drag decay.
Predicts reentry time for low Earth orbits.
"""

import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AtmosphericModel:
    """Simplified atmospheric density model."""
    base_density_kg_m3: float = 1.0e-12
    scale_height_km: float = 50.0
    
    def density_at(self, altitude_km: float) -> float:
        """Get density at altitude."""
        if altitude_km < 100.0:
            return 5.0e-7
        elif altitude_km < 200.0:
            return 3.0e-10
        elif altitude_km < 400.0:
            return 1.0e-12
        elif altitude_km < 600.0:
            return 1.0e-14
        elif altitude_km < 800.0:
            return 1.0e-15
        else:
            return 1.0e-17


class OrbitLifetimeEstimator:
    """
    Estimate orbital lifetime from atmospheric drag.
    
    Uses simplified ballistic coefficient model for
    decay prediction.
    """
    
    EARTH_RADIUS_KM = 6378.137
    MU_KM3_S2 = 398600.4418
    
    def __init__(self, atmosphere: Optional[AtmosphericModel] = None):
        self.atmosphere = atmosphere or AtmosphericModel()
    
    def ballistic_coefficient_kg_m2(self, mass_kg: float,
                                     drag_coefficient: float = 2.2,
                                     area_m2: float = 1.0) -> float:
        """
        Compute ballistic coefficient B = m / (Cd * A).
        
        Args:
            mass_kg: Spacecraft mass
            drag_coefficient: Drag coefficient
            area_m2: Cross-sectional area
        
        Returns:
            Ballistic coefficient in kg/m^2
        """
        return mass_kg / (drag_coefficient * area_m2)
    
    def decay_rate_km_day(self, altitude_km: float,
                          ballistic_coefficient_kg_m2: float) -> float:
        """
        Compute orbital decay rate.
        
        da/dt = -2 * pi * Cd * A / m * rho * a^2
        
        Args:
            altitude_km: Current altitude
            ballistic_coefficient_kg_m2: Ballistic coefficient
        
        Returns:
            Decay rate in km/day
        """
        re = self.EARTH_RADIUS_KM
        a = re + altitude_km
        
        # Density
        rho = self.atmosphere.density_at(altitude_km)
        
        # Orbital velocity
        v = math.sqrt(self.MU_KM3_S2 / a)  # km/s
        
        # Decay rate: da/dt = -rho * v * (Cd*A/m) * a
        # In consistent units: rho [kg/m^3], v [m/s], a [m]
        v_ms = v * 1000.0
        a_m = a * 1000.0
        
        # 1/B = Cd*A/m
        decay_rate_m_s = -rho * v_ms * a_m / ballistic_coefficient_kg_m2
        
        # Convert to km/day
        decay_rate_km_day = decay_rate_m_s * 86400.0 / 1000.0
        
        return abs(decay_rate_km_day)
    
    def estimate_lifetime(self, initial_altitude_km: float,
                          mass_kg: float,
                          drag_coefficient: float = 2.2,
                          area_m2: float = 1.0,
                          min_altitude_km: float = 100.0) -> Dict:
        """
        Estimate orbital lifetime.
        
        Numerically integrates decay from initial to minimum altitude.
        
        Args:
            initial_altitude_km: Initial altitude
            mass_kg: Spacecraft mass
            drag_coefficient: Drag coefficient
            area_m2: Cross-sectional area
            min_altitude_km: Minimum survivable altitude
        
        Returns:
            Lifetime estimate dictionary
        """
        bc = self.ballistic_coefficient_kg_m2(mass_kg, drag_coefficient, area_m2)
        
        altitude = initial_altitude_km
        total_days = 0.0
        time_step_days = 1.0
        
        # History for reporting
        history = [(0.0, altitude)]
        
        while altitude > min_altitude_km:
            decay_rate = self.decay_rate_km_day(altitude, bc)
            
            if decay_rate < 1.0e-12:
                # Effectively no decay
                total_days = float('inf')
                break
            
            # Adaptive time step
            if decay_rate > 1.0:
                time_step_days = 0.1
            elif decay_rate > 0.1:
                time_step_days = 1.0
            else:
                time_step_days = 10.0
            
            altitude -= decay_rate * time_step_days
            total_days += time_step_days
            
            if len(history) < 10 or int(total_days) % 100 == 0:
                history.append((total_days, altitude))
            
            # Safety limit
            if total_days > 100000:
                total_days = float('inf')
                break
        
        # Convert to years
        years = total_days / 365.25 if total_days != float('inf') else float('inf')
        
        return {
            "initial_altitude_km": initial_altitude_km,
            "min_altitude_km": min_altitude_km,
            "ballistic_coefficient_kg_m2": round(bc, 3),
            "lifetime_days": round(total_days, 1) if total_days != float('inf') else -1.0,
            "lifetime_years": round(years, 2) if years != float('inf') else -1.0,
            "decay_rate_initial_km_day": round(
                self.decay_rate_km_day(initial_altitude_km, bc), 6
            ),
            "is_stable": total_days == float('inf'),
            "history": history
        }
    
    def reentry_prediction(self, initial_altitude_km: float,
                           mass_kg: float,
                           drag_coefficient: float = 2.2,
                           area_m2: float = 1.0) -> Dict:
        """
        Predict reentry parameters.
        
        Args:
            initial_altitude_km: Initial altitude
            mass_kg: Mass
            drag_coefficient: Cd
            area_m2: Area
        
        Returns:
            Reentry prediction dictionary
        """
        result = self.estimate_lifetime(
            initial_altitude_km, mass_kg, drag_coefficient, area_m2,
            min_altitude_km=80.0
        )
        
        # Reentry velocity estimate
        re = self.EARTH_RADIUS_KM
        v_circular = math.sqrt(self.MU_KM3_S2 / (re + 80.0))
        
        result["reentry_velocity_km_s"] = round(v_circular, 3)
        result["reentry_altitude_km"] = 80.0
        
        return result
    
    def compare_configurations(self, altitude_km: float,
                                configurations: list) -> list:
        """
        Compare lifetime for multiple spacecraft configurations.
        
        Args:
            altitude_km: Altitude
            configurations: List of dicts with mass_kg, Cd, area_m2, name
        
        Returns:
            List of results sorted by lifetime
        """
        results = []
        for config in configurations:
            result = self.estimate_lifetime(
                altitude_km,
                config.get("mass_kg", 1000.0),
                config.get("drag_coefficient", 2.2),
                config.get("area_m2", 1.0)
            )
            result["name"] = config.get("name", "Unnamed")
            results.append(result)
        
        # Sort by lifetime
        results.sort(key=lambda x: x["lifetime_years"] if x["lifetime_years"] >= 0 else float('inf'))
        
        return results
