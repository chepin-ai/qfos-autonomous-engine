"""
Maneuver Design Module
Orbit maneuver planning for impulsive and finite-burn transfers.
Supports Hohmann, bi-elliptic, and plane change maneuvers.
"""

import math
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass


@dataclass
class Maneuver:
    """An orbital maneuver."""
    name: str
    delta_v_ms: float
    direction_rad: float  # In-plane direction
    out_of_plane_rad: float = 0.0
    isp_s: float = 300.0
    thrust_n: float = 450.0
    burn_type: str = "impulsive"  # or "finite"


class HohmannTransfer:
    """
    Hohmann transfer between circular orbits.
    
    Most efficient two-impulse transfer between coplanar circular orbits.
    """
    
    MU_EARTH = 398600.4418  # km^3/s^2
    
    @classmethod
    def design(cls, r1_km: float, r2_km: float) -> Dict:
        """
        Design Hohmann transfer.
        
        Args:
            r1_km: Initial circular orbit radius
            r2_km: Final circular orbit radius
        
        Returns:
            Transfer parameters
        """
        # Velocities
        v1 = math.sqrt(cls.MU_EARTH / r1_km)
        v2 = math.sqrt(cls.MU_EARTH / r2_km)
        
        # Transfer orbit
        a_transfer = (r1_km + r2_km) / 2.0
        v_periapsis = math.sqrt(cls.MU_EARTH * (2.0/r1_km - 1.0/a_transfer))
        v_apoapsis = math.sqrt(cls.MU_EARTH * (2.0/r2_km - 1.0/a_transfer))
        
        # Delta-v
        dv1 = abs(v_periapsis - v1)
        dv2 = abs(v2 - v_apoapsis)
        
        # Transfer time
        tof_s = math.pi * math.sqrt(a_transfer**3 / cls.MU_EARTH)
        
        return {
            "delta_v_total_ms": round((dv1 + dv2) * 1000.0, 3),
            "delta_v1_ms": round(dv1 * 1000.0, 3),
            "delta_v2_ms": round(dv2 * 1000.0, 3),
            "transfer_time_s": round(tof_s, 1),
            "transfer_time_hr": round(tof_s / 3600.0, 2),
            "semi_major_axis_km": round(a_transfer, 1),
            "eccentricity": round((r2_km - r1_km) / (r2_km + r1_km), 5)
        }


class BiEllipticTransfer:
    """
    Bi-elliptic transfer for large orbit changes.
    
    Can be more efficient than Hohmann for very large radius ratios.
    """
    
    MU_EARTH = 398600.4418
    
    @classmethod
    def design(cls, r1_km: float, r2_km: float,
               r_intermediate_km: float) -> Dict:
        """
        Design bi-elliptic transfer.
        
        Args:
            r1_km: Initial orbit radius
            r2_km: Final orbit radius
            r_intermediate_km: Intermediate apoapsis (must be > max(r1, r2))
        
        Returns:
            Transfer parameters
        """
        v1 = math.sqrt(cls.MU_EARTH / r1_km)
        v2 = math.sqrt(cls.MU_EARTH / r2_km)
        
        # First transfer leg
        a1 = (r1_km + r_intermediate_km) / 2.0
        v1a = math.sqrt(cls.MU_EARTH * (2.0/r1_km - 1.0/a1))
        v1b = math.sqrt(cls.MU_EARTH * (2.0/r_intermediate_km - 1.0/a1))
        
        # Second transfer leg
        a2 = (r_intermediate_km + r2_km) / 2.0
        v2a = math.sqrt(cls.MU_EARTH * (2.0/r_intermediate_km - 1.0/a2))
        v2b = math.sqrt(cls.MU_EARTH * (2.0/r2_km - 1.0/a2))
        
        dv1 = abs(v1a - v1)
        dv2 = abs(v2a - v1b)
        dv3 = abs(v2 - v2b)
        
        tof1 = math.pi * math.sqrt(a1**3 / cls.MU_EARTH)
        tof2 = math.pi * math.sqrt(a2**3 / cls.MU_EARTH)
        
        return {
            "delta_v_total_ms": round((dv1 + dv2 + dv3) * 1000.0, 3),
            "delta_v1_ms": round(dv1 * 1000.0, 3),
            "delta_v2_ms": round(dv2 * 1000.0, 3),
            "delta_v3_ms": round(dv3 * 1000.0, 3),
            "transfer_time_s": round(tof1 + tof2, 1),
            "transfer_time_hr": round((tof1 + tof2) / 3600.0, 2)
        }


class PlaneChangeManeuver:
    """
    Orbital plane change maneuvers.
    
    Simple plane change is most efficient at apoapsis.
    Combined plane change + circularization can be more efficient.
    """
    
    @staticmethod
    def simple_plane_change(velocity_ms: float,
                            delta_inclination_deg: float) -> float:
        """
        Delta-v for simple plane change.
        
        dv = 2 * v * sin(di/2)
        
        Args:
            velocity_ms: Orbital velocity
            delta_inclination_deg: Inclination change
        
        Returns:
            Delta-v in m/s
        """
        di_rad = math.radians(delta_inclination_deg)
        return 2.0 * velocity_ms * math.sin(di_rad / 2.0)
    
    @staticmethod
    def combined_plane_change(v1_ms: float, v2_ms: float,
                              delta_inclination_deg: float) -> float:
        """
        Delta-v for combined plane change and speed change.
        
        Uses law of cosines.
        
        Args:
            v1_ms: Initial velocity
            v2_ms: Final velocity
            delta_inclination_deg: Inclination change
        
        Returns:
            Delta-v in m/s
        """
        di_rad = math.radians(delta_inclination_deg)
        return math.sqrt(v1_ms**2 + v2_ms**2 - 
                        2.0 * v1_ms * v2_ms * math.cos(di_rad))


class FiniteBurnManeuver:
    """
    Finite-burn maneuver design.
    
    Models continuous thrust maneuvers with gravity losses.
    """
    
    @staticmethod
    def compute_burn_duration(delta_v_ms: float,
                              initial_mass_kg: float,
                              isp_s: float = 300.0,
                              thrust_n: float = 450.0) -> Dict:
        """
        Compute finite burn parameters.
        
        Args:
            delta_v_ms: Required delta-v
            initial_mass_kg: Spacecraft mass before burn
            isp_s: Specific impulse
            thrust_n: Thrust
        
        Returns:
            Burn parameters
        """
        g0 = 9.80665
        
        # Mass ratio
        mr = math.exp(delta_v_ms / (isp_s * g0))
        final_mass = initial_mass_kg / mr
        propellant_mass = initial_mass_kg - final_mass
        
        # Burn duration
        mass_flow = thrust_n / (isp_s * g0)
        burn_duration = propellant_mass / mass_flow
        
        # Average acceleration
        avg_accel = thrust_n / ((initial_mass_kg + final_mass) / 2.0)
        
        return {
            "burn_duration_s": round(burn_duration, 2),
            "burn_duration_min": round(burn_duration / 60.0, 3),
            "propellant_mass_kg": round(propellant_mass, 4),
            "final_mass_kg": round(final_mass, 4),
            "mass_ratio": round(mr, 5),
            "average_acceleration_ms2": round(avg_accel, 4)
        }
    
    @staticmethod
    def gravity_loss(delta_v_ideal_ms: float,
                     burn_duration_s: float,
                     gravity_ms2: float = 9.8) -> float:
        """
        Estimate gravity loss during vertical burn.
        
        Args:
            delta_v_ideal_ms: Ideal delta-v
            burn_duration_s: Burn duration
            gravity_ms2: Gravitational acceleration
        
        Returns:
            Gravity loss in m/s
        """
        # Simplified: gravity loss ~ g * t_burn * (1 - efficiency)
        # For horizontal burns, gravity loss is much smaller
        return gravity_ms2 * burn_duration_s * 0.1  # 10% effective for typical burns


class ManeuverSequence:
    """
    Sequence of maneuvers for complex orbit changes.
    """
    
    def __init__(self):
        self.maneuvers: List[Maneuver] = []
    
    def add_maneuver(self, maneuver: Maneuver):
        """Add maneuver to sequence."""
        self.maneuvers.append(maneuver)
    
    def total_delta_v(self) -> float:
        """Total delta-v of sequence."""
        return sum(m.delta_v_ms for m in self.maneuvers)
    
    def total_propellant(self, initial_mass_kg: float,
                         isp_s: float = 300.0) -> float:
        """Total propellant required."""
        mass = initial_mass_kg
        for m in self.maneuvers:
            g0 = 9.80665
            mr = math.exp(m.delta_v_ms / (isp_s * g0))
            prop = mass * (1.0 - 1.0/mr)
            mass -= prop
        return initial_mass_kg - mass
    
    def get_summary(self) -> Dict:
        """Get sequence summary."""
        return {
            "maneuver_count": len(self.maneuvers),
            "total_delta_v_ms": round(self.total_delta_v(), 3),
            "maneuvers": [
                {
                    "name": m.name,
                    "delta_v_ms": round(m.delta_v_ms, 3),
                    "burn_type": m.burn_type
                }
                for m in self.maneuvers
            ]
        }
