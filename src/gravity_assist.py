"""
Gravity Assist Module
Planetary gravity assist (slingshot) maneuver calculations.
"""

import math
from typing import Tuple
try:
    from .orbital_mechanics import MU_SUN
except ImportError:
    from orbital_mechanics import MU_SUN

# Planet masses (kg)
PLANET_MASSES = {
    "Mercury": 3.301e23,
    "Venus": 4.867e24,
    "Earth": 5.972e24,
    "Mars": 6.417e23,
    "Jupiter": 1.898e27,
    "Saturn": 5.683e26,
    "Uranus": 8.681e25,
    "Neptune": 1.024e26,
}

# Planet radii (m)
PLANET_RADII = {
    "Mercury": 2.439e6,
    "Venus": 6.051e6,
    "Earth": 6.371e6,
    "Mars": 3.389e6,
    "Jupiter": 6.991e7,
    "Saturn": 5.823e7,
    "Uranus": 2.536e7,
    "Neptune": 2.462e7,
}


def gravity_assist_turn_angle(v_inf: float, planet_mass_kg: float, 
                               flyby_radius_m: float) -> float:
    """
    Calculate the turn angle (delta) for a gravity assist.
    
    Args:
        v_inf: Hyperbolic excess velocity (m/s)
        planet_mass_kg: Mass of the planet (kg)
        flyby_radius_m: Flyby distance from planet center (m)
    
    Returns:
        Turn angle in radians
    """
    G = 6.674e-11
    mu = G * planet_mass_kg
    
    # Hyperbolic eccentricity
    e_hyp = 1 + (v_inf**2 * flyby_radius_m) / mu
    
    # Turn angle
    delta = 2 * math.asin(1.0 / e_hyp)
    return delta


def gravity_assist_delta_v(v_inf_in: float, planet_name: str,
                            flyby_altitude_km: float = 500.0) -> Tuple[float, float]:
    """
    Calculate delta-v change from a gravity assist.
    
    Args:
        v_inf_in: Incoming hyperbolic excess velocity (m/s)
        planet_name: Name of the planet
        flyby_altitude_km: Altitude above planet surface (km)
    
    Returns:
        (turn_angle_deg, delta_v_magnitude_m_s)
    """
    mass = PLANET_MASSES.get(planet_name)
    radius = PLANET_RADII.get(planet_name)
    
    if not mass or not radius:
        raise ValueError(f"Unknown planet: {planet_name}")
    
    flyby_radius = radius + flyby_altitude_km * 1000
    
    delta = gravity_assist_turn_angle(v_inf_in, mass, flyby_radius)
    
    # Maximum delta-v is 2*v_inf*sin(delta/2) for perfect alignment
    max_dv = 2 * v_inf_in * math.sin(delta / 2)
    
    return math.degrees(delta), max_dv


def optimal_flyby_planet(v_inf_required: float, available_planets: list) -> dict:
    """
    Find the optimal planet for a gravity assist given required v_inf.
    
    Returns dict with planet recommendations.
    """
    results = []
    for planet in available_planets:
        if planet not in PLANET_MASSES:
            continue
        mass = PLANET_MASSES[planet]
        radius = PLANET_RADII[planet]
        
        # Minimum flyby radius (just above atmosphere)
        min_flyby = radius + 200e3  # 200km minimum
        
        delta, max_dv = gravity_assist_delta_v(v_inf_required, planet, 200.0)
        
        results.append({
            "planet": planet,
            "turn_angle_deg": round(delta, 2),
            "max_delta_v_ms": round(max_dv, 1),
            "score": round(max_dv * delta, 1)
        })
    
    # Sort by score (higher is better)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
