"""
Radio Science Module
Spacecraft radio measurements for planetary science.
Supports gravity field determination via Doppler tracking and
atmospheric occultation experiments.
"""

import math
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass


@dataclass
class DopplerMeasurement:
    """A two-way Doppler measurement."""
    timestamp_s: float
    range_rate_ms: float        # Measured range rate (m/s)
    sigma_ms: float = 0.001     # Measurement uncertainty (m/s)
    band: str = "X"             # Tracking band (S, X, Ka)


@dataclass
class OccultationGeometry:
    """Geometry for radio occultation experiment."""
    planet_radius_km: float
    atmosphere_scale_height_km: float
    ring_system: bool = False


class GravityFieldEstimator:
    """
    Estimate gravity field parameters from Doppler tracking data.
    
    Computes spherical harmonic coefficients from range-rate residuals.
    """
    
    SPEED_OF_LIGHT = 299792458.0  # m/s
    
    def __init__(self, central_body_mu_km3_s2: float = 398600.4418):
        """
        Args:
            central_body_mu_km3_s2: GM of central body (km^3/s^2)
        """
        self.mu = central_body_mu_km3_s2
    
    @classmethod
    def for_planet(cls, planet: str) -> "GravityFieldEstimator":
        """Create estimator for named planet."""
        mu_map = {
            "Earth": 398600.4418,
            "Mars": 42828.375214,
            "Venus": 324858.598826,
            "Moon": 4902.800117,
            "Jupiter": 126712767.8578,
            "Saturn": 37940626.0611,
            "Mercury": 22032.080486418,
        }
        return cls(mu_map.get(planet, 398600.4418))
    
    def compute_range_rate(self, sc_position_km: Tuple[float, float, float],
                           sc_velocity_km_s: Tuple[float, float, float],
                           gs_position_km: Tuple[float, float, float]) -> float:
        """
        Compute expected two-way Doppler range rate.
        
        Args:
            sc_position_km: Spacecraft position
            sc_velocity_km_s: Spacecraft velocity
            gs_position_km: Ground station position
        
        Returns:
            Range rate in m/s
        """
        # Vector from SC to GS
        dx = gs_position_km[0] - sc_position_km[0]
        dy = gs_position_km[1] - sc_position_km[1]
        dz = gs_position_km[2] - sc_position_km[2]
        
        range_km = math.sqrt(dx**2 + dy**2 + dz**2)
        if range_km < 1e-12:
            return 0.0
        
        # Line of sight unit vector
        ux = dx / range_km
        uy = dy / range_km
        uz = dz / range_km
        
        # Range rate = velocity dot LOS
        # Two-way: multiply by 2
        range_rate_km_s = 2.0 * (sc_velocity_km_s[0] * ux +
                                  sc_velocity_km_s[1] * uy +
                                  sc_velocity_km_s[2] * uz)
        
        return range_rate_km_s * 1000.0  # Convert to m/s
    
    def gravity_anomaly_acceleration(self, sc_position_km: Tuple[float, float, float],
                                      j2: float = 0.00108263,
                                      equatorial_radius_km: float = 6378.137) -> Tuple[float, float, float]:
        """
        Compute J2 perturbation acceleration.
        
        Args:
            sc_position_km: Position
            j2: J2 coefficient
            equatorial_radius_km: Equatorial radius
        
        Returns:
            (ax, ay, az) in m/s^2
        """
        r = math.sqrt(sc_position_km[0]**2 + sc_position_km[1]**2 + sc_position_km[2]**2)
        if r < 1e-12:
            return (0.0, 0.0, 0.0)
        
        mu = self.mu * 1e9  # Convert to m^3/s^2
        r_m = r * 1000.0
        re_m = equatorial_radius_km * 1000.0
        
        factor = -1.5 * j2 * mu * (re_m**2) / (r_m**5)
        
        ax = factor * sc_position_km[0] * (1 - 5 * (sc_position_km[2]/r)**2)
        ay = factor * sc_position_km[1] * (1 - 5 * (sc_position_km[2]/r)**2)
        az = factor * sc_position_km[2] * (3 - 5 * (sc_position_km[2]/r)**2)
        
        return ax, ay, az
    
    def estimate_j2_from_residuals(self, measurements: List[DopplerMeasurement],
                                    sc_positions_km: List[Tuple[float, float, float]],
                                    sc_velocities_km_s: List[Tuple[float, float, float]],
                                    gs_position_km: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Dict:
        """
        Simple J2 estimation from Doppler residuals.
        
        Returns estimated J2 and fit quality.
        """
        residuals = []
        
        for i, meas in enumerate(measurements):
            expected = self.compute_range_rate(
                sc_positions_km[i], sc_velocities_km_s[i], gs_position_km
            )
            residual = meas.range_rate_ms - expected
            residuals.append(residual)
        
        if not residuals:
            return {"j2_estimate": None, "rms_residual_ms": None}
        
        rms = math.sqrt(sum(r**2 for r in residuals) / len(residuals))
        
        # Very simple J2 estimate from residual sign pattern
        # In practice would use least squares or filter
        mean_residual = sum(residuals) / len(residuals)
        
        return {
            "j2_estimate": round(0.00108263 + mean_residual * 1e-8, 8),
            "rms_residual_ms": round(rms, 6),
            "measurement_count": len(measurements),
            "mean_residual_ms": round(mean_residual, 6)
        }


class OccultationAnalyzer:
    """
    Analyze radio occultation data for atmospheric profiles.
    
    Derives temperature/pressure profiles from signal intensity
    and phase during planetary occultation.
    """
    
    SPEED_OF_LIGHT_KM_S = 299792.458
    
    def __init__(self, geometry: OccultationGeometry):
        self.geometry = geometry
    
    def compute_refraction_angle(self, impact_parameter_km: float,
                                  atmosphere_density_kg_m3: float) -> float:
        """
        Compute refraction angle from atmospheric density.
        
        Uses Abelian inversion approximation.
        
        Args:
            impact_parameter_km: Distance from planet center at closest approach
            atmosphere_density_kg_m3: Atmospheric density at impact parameter
        
        Returns:
            Refraction angle in radians
        """
        rp = self.geometry.planet_radius_km
        H = self.geometry.atmosphere_scale_height_km
        
        if impact_parameter_km <= rp:
            return 0.0
        
        # Simplified: exponential atmosphere refraction
        # alpha ~ density * scale_height / impact_parameter
        height_km = impact_parameter_km - rp
        density_factor = math.exp(-height_km / H) if H > 0 else 1.0
        
        # Simplified formula (order of magnitude)
        alpha_rad = 1e-6 * atmosphere_density_kg_m3 * H / impact_parameter_km
        
        return alpha_rad
    
    def compute_signal_attenuation(self, impact_parameter_km: float,
                                    opacity_db_km: float = 0.1) -> float:
        """
        Compute signal attenuation during occultation.
        
        Args:
            impact_parameter_km: Impact parameter
            opacity_db_km: Atmospheric opacity per km
        
        Returns:
            Signal attenuation in dB
        """
        rp = self.geometry.planet_radius_km
        H = self.geometry.atmosphere_scale_height_km
        
        if impact_parameter_km <= rp:
            # Below surface - total loss
            return 100.0
        
        height_km = impact_parameter_km - rp
        
        # Simplified: attenuation proportional to path length through atmosphere
        # Path length ~ sqrt(2 * pi * H * height) for grazing ray
        if height_km > 0 and H > 0:
            path_length_km = math.sqrt(2 * math.pi * H * height_km)
            attenuation_db = opacity_db_km * path_length_km
        else:
            attenuation_db = 0.0
        
        return min(attenuation_db, 100.0)
    
    def generate_occultation_profile(self,
                                      impact_parameters_km: List[float],
                                      base_density_kg_m3: float = 1.0) -> Dict:
        """
        Generate synthetic occultation profile.
        
        Args:
            impact_parameters_km: List of impact parameters to sample
            base_density_kg_m3: Surface atmospheric density
        
        Returns:
            Profile with refraction, attenuation, and temperature
        """
        profile = {
            "impact_parameters_km": impact_parameters_km,
            "refraction_angles_rad": [],
            "attenuation_db": [],
            "temperature_k": []
        }
        
        rp = self.geometry.planet_radius_km
        H = self.geometry.atmosphere_scale_height_km
        
        for ip in impact_parameters_km:
            if ip <= rp:
                profile["refraction_angles_rad"].append(0.0)
                profile["attenuation_db"].append(100.0)
                profile["temperature_k"].append(0.0)
                continue
            
            height_km = ip - rp
            density = base_density_kg_m3 * math.exp(-height_km / H) if H > 0 else base_density_kg_m3
            
            alpha = self.compute_refraction_angle(ip, density)
            atten = self.compute_signal_attenuation(ip)
            
            # Simplified temperature profile (exponential)
            temp = 300.0 * math.exp(-height_km / (5 * H)) if H > 0 else 300.0
            
            profile["refraction_angles_rad"].append(round(alpha, 10))
            profile["attenuation_db"].append(round(atten, 2))
            profile["temperature_k"].append(round(temp, 1))
        
        return profile
    
    def find_occultation_events(self, sc_trajectory_km: List[Tuple[float, float, float]],
                                 planet_position_km: Tuple[float, float, float],
                                 sun_position_km: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> List[Dict]:
        """
        Find radio occultation entry/exit events from trajectory.
        
        Args:
            sc_trajectory_km: List of spacecraft positions
            planet_position_km: Planet center position
            sun_position_km: Sun position (for illumination check)
        
        Returns:
            List of occultation events with entry/exit times
        """
        events = []
        rp = self.geometry.planet_radius_km
        
        in_occultation = False
        entry_idx = None
        
        for i, sc_pos in enumerate(sc_trajectory_km):
            dx = sc_pos[0] - planet_position_km[0]
            dy = sc_pos[1] - planet_position_km[1]
            dz = sc_pos[2] - planet_position_km[2]
            
            distance_km = math.sqrt(dx**2 + dy**2 + dz**2)
            
            # Check if spacecraft is behind planet from sun
            # Simplified: just check distance
            is_occulted = distance_km < rp * 1.5  # Include atmosphere
            
            if is_occulted and not in_occultation:
                entry_idx = i
                in_occultation = True
            elif not is_occulted and in_occultation:
                events.append({
                    "entry_index": entry_idx,
                    "exit_index": i,
                    "min_altitude_km": round(min(
                        math.sqrt((p[0]-planet_position_km[0])**2 +
                                  (p[1]-planet_position_km[1])**2 +
                                  (p[2]-planet_position_km[2])**2)
                        for p in sc_trajectory_km[entry_idx:i+1]
                    ) - rp, 1)
                })
                in_occultation = False
        
        return events


class RadioScienceSummary:
    """Summary report for radio science observations."""
    
    @staticmethod
    def generate_report(gravity_estimator: GravityFieldEstimator,
                        occultation_analyzer: Optional[OccultationAnalyzer] = None,
                        doppler_measurements: Optional[List[DopplerMeasurement]] = None) -> Dict:
        """Generate radio science summary report."""
        report = {
            "central_body_mu_km3_s2": gravity_estimator.mu,
            "gravity_field_status": "active",
            "doppler_measurements": len(doppler_measurements) if doppler_measurements else 0,
            "occultation_experiments": 0
        }
        
        if occultation_analyzer:
            report["occultation_experiments"] = 1
            report["planet_radius_km"] = occultation_analyzer.geometry.planet_radius_km
            report["scale_height_km"] = occultation_analyzer.geometry.atmosphere_scale_height_km
        
        return report
