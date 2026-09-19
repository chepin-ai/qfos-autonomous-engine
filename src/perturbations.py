"""
Orbit Perturbations Module
High-fidelity perturbation accelerations for orbital propagation.
Models J2/J3 geopotential, atmospheric drag, third-body gravity,
and solar radiation pressure.
"""

import math
from typing import Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class EarthGravityModel:
    """Earth gravity model parameters."""
    mu_km3_s2: float = 398600.4418
    re_km: float = 6378.137
    j2: float = 0.00108263
    j3: float = -0.00000254
    j4: float = -0.00000161


@dataclass
class AtmosphereParams:
    """Atmospheric drag parameters."""
    density_kg_m3: float = 1.0e-12  # At altitude
    scale_height_km: float = 50.0
    cd: float = 2.2
    area_m2: float = 1.0
    mass_kg: float = 100.0


class PerturbationModel:
    """
    Compute perturbation accelerations for orbital propagation.
    
    Provides physically accurate perturbation models for
    high-fidelity orbit determination and prediction.
    """
    
    # Astronomical constants
    AU_KM = 149597870.7
    MU_SUN_KM3_S2 = 1.32712440018e11
    MU_MOON_KM3_S2 = 4902.800117
    SPEED_OF_LIGHT_KM_S = 299792.458
    
    # Solar radiation pressure at 1 AU
    SRP_PA = 4.56e-6  # N/m^2
    
    def __init__(self, gravity: Optional[EarthGravityModel] = None):
        self.gravity = gravity or EarthGravityModel()
    
    def j2_acceleration(self, position_km: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Compute J2 perturbation acceleration.
        
        Accounts for Earth's oblateness.
        
        Args:
            position_km: Position in Earth-centered inertial frame (km)
        
        Returns:
            (ax, ay, az) in m/s^2
        """
        x, y, z = position_km
        r = math.sqrt(x**2 + y**2 + z**2)
        if r < 1e-6:
            return (0.0, 0.0, 0.0)
        
        mu = self.gravity.mu_km3_s2 * 1e9  # m^3/s^2
        re = self.gravity.re_km * 1000.0   # m
        j2 = self.gravity.j2
        
        factor = -1.5 * j2 * mu * (re**2) / (r**5)
        
        # J2 acceleration components
        ax = factor * x * (1.0 - 5.0 * (z/r)**2)
        ay = factor * y * (1.0 - 5.0 * (z/r)**2)
        az = factor * z * (3.0 - 5.0 * (z/r)**2)
        
        return ax, ay, az
    
    def j3_acceleration(self, position_km: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Compute J3 perturbation acceleration.
        
        Pear-shaped Earth effect.
        """
        x, y, z = position_km
        r = math.sqrt(x**2 + y**2 + z**2)
        if r < 1e-6:
            return (0.0, 0.0, 0.0)
        
        mu = self.gravity.mu_km3_s2 * 1e9
        re = self.gravity.re_km * 1000.0
        j3 = self.gravity.j3
        
        sin_phi = z / r  # sin of geocentric latitude
        
        factor = -0.5 * j3 * mu * (re**3) / (r**6)
        
        ax = factor * x * (3.0 * sin_phi - 7.0 * sin_phi**3) * 5.0
        ay = factor * y * (3.0 * sin_phi - 7.0 * sin_phi**3) * 5.0
        az = factor * z * (6.0 * sin_phi - 7.0 * sin_phi**3 - 3.0 / sin_phi if abs(sin_phi) > 1e-6 else 0.0)
        
        # Simplified J3 (dominant zonal harmonic after J2)
        factor_z = -2.5 * j3 * mu * (re**3) / (r**7)
        az = factor_z * z * (3.0 * r**2 - 7.0 * z**2)
        ax = factor_z * x * (3.0 * r**2 - 7.0 * z**2)
        ay = factor_z * y * (3.0 * r**2 - 7.0 * z**2)
        
        return ax, ay, az
    
    def atmospheric_drag(self, position_km: Tuple[float, float, float],
                         velocity_km_s: Tuple[float, float, float],
                         params: AtmosphereParams) -> Tuple[float, float, float]:
        """
        Compute atmospheric drag acceleration.
        
        a_drag = -0.5 * (Cd * A / m) * rho * v * v_vec
        
        Args:
            position_km: Position
            velocity_km_s: Velocity
            params: Atmospheric parameters
        
        Returns:
            (ax, ay, az) in m/s^2
        """
        vx, vy, vz = velocity_km_s
        v = math.sqrt(vx**2 + vy**2 + vz**2)
        
        if v < 1e-6:
            return (0.0, 0.0, 0.0)
        
        # Ballistic coefficient
        bc = params.cd * params.area_m2 / params.mass_kg
        
        # Drag acceleration (opposite to velocity)
        drag_mag = -0.5 * bc * params.density_kg_m3 * v * 1000.0  # v in m/s
        
        ax = drag_mag * (vx / v)
        ay = drag_mag * (vy / v)
        az = drag_mag * (vz / v)
        
        return ax, ay, az
    
    def third_body_acceleration(self, position_km: Tuple[float, float, float],
                                 third_body_pos_km: Tuple[float, float, float],
                                 mu_third_km3_s2: float) -> Tuple[float, float, float]:
        """
        Compute third-body perturbation acceleration.
        
        a_3body = mu_3 * (r_3body_sc / |r_3body_sc|^3 - r_3body / |r_3body|^3)
        
        Args:
            position_km: Spacecraft position
            third_body_pos_km: Third body position
            mu_third_km3_s2: Third body gravitational parameter
        
        Returns:
            (ax, ay, az) in m/s^2
        """
        # Vector from 3rd body to spacecraft
        dx = position_km[0] - third_body_pos_km[0]
        dy = position_km[1] - third_body_pos_km[1]
        dz = position_km[2] - third_body_pos_km[2]
        
        r_sc = math.sqrt(dx**2 + dy**2 + dz**2)
        r_3 = math.sqrt(sum(p**2 for p in third_body_pos_km))
        
        if r_sc < 1e-6 or r_3 < 1e-6:
            return (0.0, 0.0, 0.0)
        
        mu = mu_third_km3_s2 * 1e9  # Convert to m^3/s^2
        
        factor1 = mu / (r_sc**3)
        factor2 = mu / (r_3**3)
        
        ax = factor1 * dx - factor2 * third_body_pos_km[0]
        ay = factor1 * dy - factor2 * third_body_pos_km[1]
        az = factor1 * dz - factor2 * third_body_pos_km[2]
        
        return ax, ay, az
    
    def solar_radiation_pressure(self, position_km: Tuple[float, float, float],
                                  sun_position_km: Tuple[float, float, float],
                                  spacecraft_area_m2: float = 1.0,
                                  reflectivity: float = 1.3,
                                  mass_kg: float = 100.0) -> Tuple[float, float, float]:
        """
        Compute solar radiation pressure acceleration.
        
        Args:
            position_km: Spacecraft position
            sun_position_km: Sun position
            spacecraft_area_m2: Cross-sectional area
            reflectivity: Reflectivity coefficient (1.0=absorbing, 2.0=reflecting)
            mass_kg: Spacecraft mass
        
        Returns:
            (ax, ay, az) in m/s^2
        """
        # Vector from Sun to spacecraft
        dx = position_km[0] - sun_position_km[0]
        dy = position_km[1] - sun_position_km[1]
        dz = position_km[2] - sun_position_km[2]
        
        r = math.sqrt(dx**2 + dy**2 + dz**2)
        if r < 1e-6:
            return (0.0, 0.0, 0.0)
        
        # Distance in AU
        r_au = r / self.AU_KM
        
        # SRP acceleration (away from Sun)
        flux = self.SRP_PA / (r_au**2)
        accel_mag = reflectivity * flux * spacecraft_area_m2 / mass_kg
        
        ax = accel_mag * (-dx / r)
        ay = accel_mag * (-dy / r)
        az = accel_mag * (-dz / r)
        
        return ax, ay, az
    
    def total_perturbations(self, position_km: Tuple[float, float, float],
                            velocity_km_s: Tuple[float, float, float],
                            sun_position_km: Optional[Tuple[float, float, float]] = None,
                            moon_position_km: Optional[Tuple[float, float, float]] = None,
                            atmosphere: Optional[AtmosphereParams] = None,
                            include_j2: bool = True,
                            include_j3: bool = False,
                            include_drag: bool = False,
                            include_sun: bool = False,
                            include_moon: bool = False,
                            include_srp: bool = False) -> Dict:
        """
        Compute total perturbation acceleration.
        
        Returns dictionary with individual and total accelerations.
        """
        total = [0.0, 0.0, 0.0]
        components = {}
        
        if include_j2:
            a = self.j2_acceleration(position_km)
            components["j2"] = a
            for i in range(3): total[i] += a[i]
        
        if include_j3:
            a = self.j3_acceleration(position_km)
            components["j3"] = a
            for i in range(3): total[i] += a[i]
        
        if include_drag and atmosphere:
            a = self.atmospheric_drag(position_km, velocity_km_s, atmosphere)
            components["drag"] = a
            for i in range(3): total[i] += a[i]
        
        if include_sun and sun_position_km:
            a = self.third_body_acceleration(position_km, sun_position_km, self.MU_SUN_KM3_S2)
            components["sun"] = a
            for i in range(3): total[i] += a[i]
        
        if include_moon and moon_position_km:
            a = self.third_body_acceleration(position_km, moon_position_km, self.MU_MOON_KM3_S2)
            components["moon"] = a
            for i in range(3): total[i] += a[i]
        
        if include_srp and sun_position_km:
            a = self.solar_radiation_pressure(position_km, sun_position_km)
            components["srp"] = a
            for i in range(3): total[i] += a[i]
        
        total_mag = math.sqrt(sum(t**2 for t in total))
        
        return {
            "total": tuple(total),
            "total_magnitude_ms2": round(total_mag, 10),
            "components": components
        }
    
    @staticmethod
    def density_harris_priester(altitude_km: float) -> float:
        """
        Simplified atmospheric density model.
        
        Exponential approximation for LEO.
        """
        if altitude_km < 200:
            return 3.0e-10
        elif altitude_km < 400:
            return 1.0e-12
        elif altitude_km < 600:
            return 1.0e-14
        elif altitude_km < 800:
            return 1.0e-15
        else:
            return 1.0e-17
