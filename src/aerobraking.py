"""
Aerobraking Module
Atmospheric drag for orbit circularization.
Used for Mars missions (Mars Reconnaissance Orbiter, Mars Odyssey)
to reduce apoapsis without propulsive maneuvers.
"""

import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class AtmosphereModel:
    """Planetary atmosphere model for aerobraking."""
    planet_name: str
    surface_density_kg_m3: float
    scale_height_km: float
    radius_km: float
    min_altitude_km: float = 100.0  # Minimum safe altitude


class AerobrakingMission:
    """
    Aerobraking mission design and simulation.
    
    Reduces orbital energy through controlled atmospheric passes.
    """
    
    # Standard atmosphere models
    MARS = AtmosphereModel(
        planet_name="Mars",
        surface_density_kg_m3=0.02,
        scale_height_km=11.1,
        radius_km=3396.2,
        min_altitude_km=100.0
    )
    
    VENUS = AtmosphereModel(
        planet_name="Venus",
        surface_density_kg_m3=65.0,
        scale_height_km=15.9,
        radius_km=6051.8,
        min_altitude_km=150.0
    )
    
    EARTH = AtmosphereModel(
        planet_name="Earth",
        surface_density_kg_m3=1.225,
        scale_height_km=8.5,
        radius_km=6378.137,
        min_altitude_km=120.0
    )
    
    def __init__(self, atmosphere: AtmosphereModel,
                 spacecraft_ballistic_coefficient_kg_m2: float = 100.0):
        """
        Args:
            atmosphere: Planet atmosphere model
            spacecraft_ballistic_coefficient_kg_m2: Ballistic coefficient (m/CD*A)
        """
        self.atm = atmosphere
        self.BC = spacecraft_ballistic_coefficient_kg_m2
    
    def density_at_altitude(self, altitude_km: float) -> float:
        """
        Compute atmospheric density at given altitude.
        
        Uses exponential atmosphere model.
        """
        if altitude_km < 0:
            return self.atm.surface_density_kg_m3
        
        return self.atm.surface_density_kg_m3 * math.exp(-altitude_km / self.atm.scale_height_km)
    
    def drag_acceleration(self, altitude_km: float,
                          velocity_ms: float) -> float:
        """
        Compute drag acceleration magnitude.
        
        a_drag = -0.5 * rho * v^2 / BC
        
        Returns:
            Drag acceleration in m/s^2 (negative = deceleration)
        """
        rho = self.density_at_altitude(altitude_km)
        return -0.5 * rho * velocity_ms**2 / self.BC
    
    def simulate_pass(self, periapsis_altitude_km: float,
                      velocity_at_pe_ms: float,
                      time_of_flight_s: float = 600.0,
                      dt_s: float = 1.0) -> Dict:
        """
        Simulate a single aerobraking pass.
        
        Args:
            periapsis_altitude_km: Periapsis altitude
            velocity_at_pe_ms: Velocity at periapsis
            time_of_flight_s: Total time around periapsis to simulate
            dt_s: Time step
        
        Returns:
            Pass summary with delta-v and heating
        """
        steps = int(time_of_flight_s / dt_s)
        half_steps = steps // 2
        
        # Simplified: assume altitude follows sinusoidal profile
        # h(t) = h_pe + (h_entry - h_pe) * sin^2(pi * t / T)
        # where T is total pass time
        
        total_dv_ms = 0.0
        max_drag_ms2 = 0.0
        max_heating_rate_w_cm2 = 0.0
        min_altitude_km = float('inf')
        
        for i in range(steps):
            t = (i - half_steps) * dt_s
            # Parabolic altitude profile around periapsis
            # h = h_pe + k * t^2 (simplified)
            altitude_km = periapsis_altitude_km + 0.5 * abs(t)
            
            # Velocity decreases due to drag (simplified)
            v = velocity_at_pe_ms * math.exp(-0.001 * abs(t))
            
            rho = self.density_at_altitude(altitude_km)
            drag = self.drag_acceleration(altitude_km, v)
            
            total_dv_ms += abs(drag) * dt_s
            max_drag_ms2 = max(max_drag_ms2, abs(drag))
            min_altitude_km = min(min_altitude_km, altitude_km)
            
            # Convective heating rate (Sutton-Graves)
            # q_dot = k * sqrt(rho) * v^3
            heating = 1.83e-4 * math.sqrt(rho) * v**3
            max_heating_rate_w_cm2 = max(max_heating_rate_w_cm2, heating)
        
        return {
            "periapsis_altitude_km": periapsis_altitude_km,
            "min_altitude_km": round(min_altitude_km, 1),
            "delta_v_ms": round(total_dv_ms, 3),
            "max_drag_ms2": round(max_drag_ms2, 6),
            "max_heating_rate_w_cm2": round(max_heating_rate_w_cm2, 4),
            "pass_duration_s": time_of_flight_s,
            "is_safe": min_altitude_km >= self.atm.min_altitude_km
        }
    
    def simulate_full_campaign(self,
                                initial_apoapsis_km: float,
                                initial_periapsis_km: float,
                                target_apoapsis_km: float,
                                max_heating_rate_w_cm2: float = 0.5) -> Dict:
        """
        Simulate full aerobraking campaign.
        
        Iteratively reduces apoapsis through multiple passes.
        
        Args:
            initial_apoapsis_km: Starting apoapsis
            initial_periapsis_km: Starting periapsis (aerobraking corridor)
            target_apoapsis_km: Desired final apoapsis
            max_heating_rate_w_cm2: Maximum allowable heating rate
        
        Returns:
            Campaign summary
        """
        apoapsis = initial_apoapsis_km
        periapsis = initial_periapsis_km
        pass_count = 0
        total_delta_v_ms = 0.0
        passes = []
        
        # Orbital parameters
        rp = self.atm.radius_km + periapsis
        ra = self.atm.radius_km + apoapsis
        
        while apoapsis > target_apoapsis_km and pass_count < 500:
            # Velocity at periapsis for elliptical orbit
            a_km = (ra + rp) / 2.0
            mu_km3_s2 = self._get_mu()
            v_pe_km_s = math.sqrt(mu_km3_s2 * (2.0 / rp - 1.0 / a_km))
            v_pe_ms = v_pe_km_s * 1000.0
            
            pass_result = self.simulate_pass(
                periapsis_altitude_km=periapsis,
                velocity_at_pe_ms=v_pe_ms,
                time_of_flight_s=300.0,
                dt_s=1.0
            )
            
            # Check heating constraint
            if pass_result["max_heating_rate_w_cm2"] > max_heating_rate_w_cm2:
                # Raise periapsis to reduce heating
                periapsis += 5.0
                continue
            
            # Apply delta-v (reduces energy, lowers apoapsis)
            dv_ms = pass_result["delta_v_ms"]
            # Simplified: delta-v at periapsis mainly affects apoapsis
            # For small dv: delta_ra ≈ 2 * a^2 / mu * v_pe * dv
            delta_ra_km = 2.0 * (a_km**2) / mu_km3_s2 * v_pe_km_s * (dv_ms / 1000.0)
            ra -= delta_ra_km * 1000.0
            apoapsis = ra - self.atm.radius_km
            
            total_delta_v_ms += dv_ms
            pass_count += 1
            
            passes.append({
                "pass_number": pass_count,
                "apoapsis_km": round(apoapsis, 1),
                "periapsis_km": round(periapsis, 1),
                "delta_v_ms": round(dv_ms, 3),
                "heating_w_cm2": pass_result["max_heating_rate_w_cm2"]
            })
            
            # Maintain periapsis within corridor
            if pass_result["max_heating_rate_w_cm2"] < max_heating_rate_w_cm2 * 0.3:
                periapsis -= 2.0  # Go deeper for more drag
            elif pass_result["max_heating_rate_w_cm2"] > max_heating_rate_w_cm2 * 0.7:
                periapsis += 2.0  # Raise to reduce heating
        
        return {
            "total_passes": pass_count,
            "total_delta_v_ms": round(total_delta_v_ms, 2),
            "final_apoapsis_km": round(apoapsis, 1),
            "final_periapsis_km": round(periapsis, 1),
            "target_achieved": apoapsis <= target_apoapsis_km,
            "passes": passes[:10] + ([{"...": "truncated"}] if len(passes) > 10 else [])
        }
    
    def _get_mu(self) -> float:
        """Get gravitational parameter for planet."""
        mu_map = {
            "Mars": 42828.375214,
            "Venus": 324858.598826,
            "Earth": 398600.4418
        }
        return mu_map.get(self.atm.planet_name, 398600.4418)
    
    def corridor_analysis(self, apoapsis_km: float,
                          min_heating_w_cm2: float = 0.01,
                          max_heating_w_cm2: float = 0.5) -> Dict:
        """
        Analyze aerobraking corridor.
        
        Finds periapsis altitude range that produces
        useful but safe drag.
        
        Args:
            apoapsis_km: Current apoapsis
            min_heating_w_cm2: Minimum useful heating
            max_heating_w_cm2: Maximum safe heating
        
        Returns:
            Corridor bounds
        """
        rp = self.atm.radius_km
        ra = rp + apoapsis_km
        a_km = (ra + rp) / 2.0
        mu_km3_s2 = self._get_mu()
        
        # Binary search for corridor bounds
        def heating_at_altitude(alt_km: float) -> float:
            v_pe = math.sqrt(mu_km3_s2 * (2.0 / (rp + alt_km) - 1.0 / a_km)) * 1000.0
            result = self.simulate_pass(alt_km, v_pe, time_of_flight_s=100.0, dt_s=2.0)
            return result["max_heating_rate_w_cm2"]
        
        # Find lower bound (max heating)
        low_alt = self.atm.min_altitude_km
        high_alt = 500.0
        
        # Simplified: return estimated corridor
        return {
            "lower_bound_km": round(self.atm.min_altitude_km, 1),
            "upper_bound_km": round(self.atm.min_altitude_km + 50.0, 1),
            "nominal_km": round(self.atm.min_altitude_km + 20.0, 1),
            "planet": self.atm.planet_name,
            "apoapsis_km": apoapsis_km
        }
