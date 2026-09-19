"""
Space Debris Analysis Module
Collision probability assessment and debris flux modeling.
Implements NASA-standard collision probability methods.
"""

import math
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass


@dataclass
class DebrisObject:
    """Space debris object parameters."""
    object_id: str
    position_km: Tuple[float, float, float]
    velocity_km_s: Tuple[float, float, float]
    radar_cross_section_m2: float  # RCS in m^2
    diameter_m: float = 0.0  # Estimated diameter


@dataclass
class CollisionParameters:
    """Collision geometry parameters."""
    relative_velocity_km_s: float
    miss_distance_km: float
    combined_radius_m: float
    conjunction_plane_angle_deg: float


class DebrisFluxModel:
    """
    NASA Orbital Debris Engineering Model (simplified).
    
    Estimates debris flux at given orbital altitude.
    """
    
    # Reference flux at 800km (objects > 1cm per m^2 per year)
    REFERENCE_FLUX_800KM = 1.0e-4
    
    def __init__(self):
        self.earth_radius_km = 6378.0
    
    def flux_at_altitude(self, altitude_km: float,
                         particle_size_m: float = 0.01) -> float:
        """
        Estimate debris flux at altitude.
        
        Args:
            altitude_km: Altitude above Earth's surface
            particle_size_m: Minimum particle size of concern
        
        Returns:
            Flux in impacts per m^2 per year
        """
        # Altitude profile: peak around 800-1000 km
        r = altitude_km / 1000.0
        
        # Gaussian-like distribution centered at 800km
        altitude_factor = math.exp(-((altitude_km - 800.0) ** 2) / (2.0 * 400.0 ** 2))
        
        # Size factor: smaller particles more numerous
        # NASA power law: N ~ d^-2.6
        size_factor = (0.01 / max(particle_size_m, 1.0e-4)) ** 2.6
        
        flux = self.REFERENCE_FLUX_800KM * altitude_factor * size_factor
        
        return round(flux, 10)
    
    def flux_directional(self, altitude_km: float,
                         inclination_deg: float,
                         particle_size_m: float = 0.01) -> Dict:
        """
        Directional debris flux components.
        
        Returns flux from different directions.
        """
        total_flux = self.flux_at_altitude(altitude_km, particle_size_m)
        
        # Directional distribution
        # LEO debris flux is predominantly from prograde orbits
        prograde_fraction = 0.7
        retrograde_fraction = 0.2
        zenith_fraction = 0.1
        
        if inclination_deg > 90.0:
            prograde_fraction, retrograde_fraction = retrograde_fraction, prograde_fraction
        
        return {
            "total_flux_per_m2_yr": total_flux,
            "prograde_fraction": prograde_fraction,
            "retrograde_fraction": retrograde_fraction,
            "zenith_fraction": zenith_fraction,
            "prograde_flux": round(total_flux * prograde_fraction, 10),
            "retrograde_flux": round(total_flux * retrograde_fraction, 10)
        }


class CollisionProbability:
    """
    Collision probability calculation methods.
    
    Implements the Patera method and simplified Poisson model.
    """
    
    def __init__(self, spacecraft_radius_m: float = 5.0):
        """
        Args:
            spacecraft_radius_m: Spacecraft hard body radius
        """
        self.spacecraft_radius_m = spacecraft_radius_m
    
    def compute_relative_geometry(self, 
                                   pos1_km: Tuple[float, float, float],
                                   vel1_km_s: Tuple[float, float, float],
                                   pos2_km: Tuple[float, float, float],
                                   vel2_km_s: Tuple[float, float, float]) -> CollisionParameters:
        """
        Compute collision geometry from two object states.
        
        Args:
            pos1_km, vel1_km_s: Primary object state
            pos2_km, vel2_km_s: Secondary object state
        
        Returns:
            CollisionParameters
        """
        # Relative position
        dx = pos2_km[0] - pos1_km[0]
        dy = pos2_km[1] - pos1_km[1]
        dz = pos2_km[2] - pos1_km[2]
        
        # Relative velocity
        dvx = vel2_km_s[0] - vel1_km_s[0]
        dvy = vel2_km_s[1] - vel1_km_s[1]
        dvz = vel2_km_s[2] - vel1_km_s[2]
        
        relative_velocity = math.sqrt(dvx**2 + dvy**2 + dvz**2)
        
        # Miss distance (current distance, assuming linear motion)
        miss_distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Combined hard body radius (simplified)
        combined_radius = self.spacecraft_radius_m / 1000.0  # Convert to km
        
        # Conjunction plane angle (simplified)
        if relative_velocity > 1e-6 and miss_distance > 1e-9:
            cos_angle = abs(dx*dvx + dy*dvy + dz*dvz) / (miss_distance * relative_velocity)
            cos_angle = min(1.0, max(0.0, cos_angle))
            angle = math.degrees(math.acos(cos_angle))
        else:
            angle = 90.0
        
        return CollisionParameters(
            relative_velocity_km_s=round(relative_velocity, 4),
            miss_distance_km=round(miss_distance, 4),
            combined_radius_m=combined_radius * 1000.0,
            conjunction_plane_angle_deg=round(angle, 2)
        )
    
    def patera_probability(self, miss_distance_km: float,
                           position_uncertainty_km: float,
                           object_radius_m: float = 1.0) -> float:
        """
        Compute collision probability using Patera method (simplified).
        
        Uses 2D Gaussian probability integrated over circular area.
        
        Args:
            miss_distance_km: Closest approach distance
            position_uncertainty_km: 1-sigma position uncertainty
            object_radius_m: Object radius
        
        Returns:
            Collision probability (0.0 - 1.0)
        """
        if position_uncertainty_km < 1e-12:
            return 0.0
        
        # Combined radius in km
        r_combined_km = (self.spacecraft_radius_m + object_radius_m) / 1000.0
        
        # Simplified Patera: probability = exp(-d^2/(2*sigma^2)) * (pi*r^2)/(2*pi*sigma^2)
        d = miss_distance_km
        sigma = position_uncertainty_km
        
        # Maximum probability (at b=0)
        p_max = (r_combined_km ** 2) / (2.0 * sigma ** 2)
        
        # Distance attenuation
        p = p_max * math.exp(-(d ** 2) / (2.0 * sigma ** 2))
        
        # Clamp to valid probability
        return min(p, 1.0)
    
    def poisson_collision_rate(self, flux_per_m2_yr: float,
                                cross_sectional_area_m2: float) -> float:
        """
        Compute annual collision probability from flux.
        
        P = 1 - exp(-flux * area)
        
        Args:
            flux_per_m2_yr: Debris flux
            cross_sectional_area_m2: Spacecraft cross-sectional area
        
        Returns:
            Annual collision probability
        """
        expected_impacts = flux_per_m2_yr * cross_sectional_area_m2
        p_collision = 1.0 - math.exp(-expected_impacts)
        return round(p_collision, 10)
    
    def assess_conjunction(self, primary_pos_km: Tuple[float, float, float],
                           primary_vel_km_s: Tuple[float, float, float],
                           secondary: DebrisObject,
                           position_uncertainty_km: float = 0.1) -> Dict:
        """
        Full conjunction assessment.
        
        Args:
            primary_pos_km: Primary object position
            primary_vel_km_s: Primary object velocity
            secondary: Secondary object (debris)
            position_uncertainty_km: Position uncertainty
        
        Returns:
            Assessment dictionary
        """
        geometry = self.compute_relative_geometry(
            primary_pos_km, primary_vel_km_s,
            secondary.position_km, secondary.velocity_km_s
        )
        
        # Collision probability
        p_collision = self.patera_probability(
            geometry.miss_distance_km,
            position_uncertainty_km,
            secondary.diameter_m / 2.0 if secondary.diameter_m > 0 else 0.1
        )
        
        # Risk classification (NASA standard)
        if p_collision > 1.0e-4:
            risk = "HIGH"
            action = "Maneuver required"
        elif p_collision > 1.0e-6:
            risk = "MODERATE"
            action = "Monitor closely"
        elif p_collision > 1.0e-7:
            risk = "LOW"
            action = "Routine monitoring"
        else:
            risk = "NEGLIGIBLE"
            action = "No action"
        
        return {
            "secondary_id": secondary.object_id,
            "miss_distance_km": geometry.miss_distance_km,
            "relative_velocity_km_s": geometry.relative_velocity_km_s,
            "collision_probability": p_collision,
            "risk_level": risk,
            "recommended_action": action,
            "position_uncertainty_km": position_uncertainty_km,
            "combined_radius_m": round(geometry.combined_radius_m, 3)
        }
    
    def screen_catalog(self, primary_pos_km: Tuple[float, float, float],
                       primary_vel_km_s: Tuple[float, float, float],
                       debris_catalog: List[DebrisObject],
                       threshold_p: float = 1.0e-6) -> List[Dict]:
        """
        Screen debris catalog for threatening objects.
        
        Args:
            primary_pos_km: Primary position
            primary_vel_km_s: Primary velocity
            debris_catalog: List of debris objects
            threshold_p: Probability threshold for reporting
        
        Returns:
            List of threatening conjunctions
        """
        threats = []
        
        for debris in debris_catalog:
            assessment = self.assess_conjunction(
                primary_pos_km, primary_vel_km_s, debris
            )
            
            if assessment["collision_probability"] >= threshold_p:
                threats.append(assessment)
        
        # Sort by probability
        threats.sort(key=lambda x: x["collision_probability"], reverse=True)
        
        return threats
