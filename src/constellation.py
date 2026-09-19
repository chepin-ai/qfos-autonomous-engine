"""
Constellation Maintenance Module
Orbit maintenance, phasing, and collision avoidance for satellite constellations.
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

try:
    from .orbital_mechanics import OrbitalBody, MU_SUN, AU, EARTH_MU_KM3_S2
except ImportError:
    from orbital_mechanics import OrbitalBody, MU_SUN, AU


# Earth parameters
MU_EARTH_KM3_S2 = 398600.4418  # km^3/s^2
EARTH_RADIUS_KM = 6378.137
J2 = 1.08263e-3  # Earth oblateness coefficient


@dataclass
class Satellite:
    """A satellite in a constellation."""
    sat_id: str
    semi_major_axis_km: float
    eccentricity: float
    inclination_deg: float
    raan_deg: float
    arg_perigee_deg: float
    mean_anomaly_deg: float
    mass_kg: float = 100.0
    fuel_remaining_kg: float = 10.0
    operational: bool = True
    
    @property
    def orbital_period_min(self) -> float:
        """Orbital period in minutes."""
        a_m = self.semi_major_axis_km * 1000.0
        period_s = 2 * math.pi * math.sqrt(a_m**3 / (MU_EARTH_KM3_S2 * 1e9))
        return period_s / 60.0
    
    @property
    def mean_motion_rad_s(self) -> float:
        """Mean motion in rad/s."""
        a_m = self.semi_major_axis_km * 1000.0
        return math.sqrt(MU_EARTH_KM3_S2 * 1e9 / a_m**3)


class ConstellationPlanner:
    """
    Plan and maintain satellite constellations.
    
    Supports Walker delta and star constellation patterns.
    """
    
    def __init__(self):
        self.satellites: Dict[str, Satellite] = {}
    
    def add_satellite(self, sat: Satellite):
        """Add a satellite to the constellation."""
        self.satellites[sat.sat_id] = sat
    
    @staticmethod
    def design_walker_delta(num_planes: int,
                            sats_per_plane: int,
                            altitude_km: float,
                            inclination_deg: float) -> List[Satellite]:
        """
        Design a Walker delta constellation.
        
        Args:
            num_planes: Number of orbital planes
            sats_per_plane: Satellites per plane
            altitude_km: Orbital altitude
            inclination_deg: Orbital inclination
        
        Returns:
            List of satellites
        """
        satellites = []
        total_sats = num_planes * sats_per_plane
        
        a = EARTH_RADIUS_KM + altitude_km
        
        for plane in range(num_planes):
            raan = plane * (360.0 / num_planes)
            
            for sat in range(sats_per_plane):
                ma = sat * (360.0 / sats_per_plane) + plane * (360.0 / total_sats)
                
                sat_obj = Satellite(
                    sat_id=f"S{plane:02d}{sat:02d}",
                    semi_major_axis_km=a,
                    eccentricity=0.0,
                    inclination_deg=inclination_deg,
                    raan_deg=raan,
                    arg_perigee_deg=0.0,
                    mean_anomaly_deg=ma % 360.0
                )
                satellites.append(sat_obj)
        
        return satellites
    
    @staticmethod
    def design_star_constellation(num_planes: int,
                                   altitude_km: float,
                                   inclination_deg: float) -> List[Satellite]:
        """
        Design a star (Walker star) constellation with retrograde planes.
        
        Returns:
            List of satellites
        """
        sats = ConstellationPlanner.design_walker_delta(
            num_planes, 1, altitude_km, inclination_deg
        )
        # Alternate plane directions for star pattern
        for i, sat in enumerate(sats):
            if i % 2 == 1:
                sat.inclination_deg = -sat.inclination_deg
        return sats
    
    def get_constellation_summary(self) -> Dict:
        """Get summary of constellation configuration."""
        if not self.satellites:
            return {"total_satellites": 0}
        
        periods = [s.orbital_period_min for s in self.satellites.values()]
        altitudes = [s.semi_major_axis_km - EARTH_RADIUS_KM for s in self.satellites.values()]
        
        # Group by plane (approximate by RAAN)
        planes: Dict[int, List[str]] = {}
        for sat in self.satellites.values():
            plane = int(round(sat.raan_deg / 30.0)) * 30
            planes.setdefault(plane, []).append(sat.sat_id)
        
        operational = sum(1 for s in self.satellites.values() if s.operational)
        total_fuel = sum(s.fuel_remaining_kg for s in self.satellites.values())
        
        return {
            "total_satellites": len(self.satellites),
            "operational": operational,
            "planes": len(planes),
            "sats_per_plane": len(self.satellites) // max(len(planes), 1),
            "avg_altitude_km": round(sum(altitudes) / len(altitudes), 1),
            "orbital_period_min": round(sum(periods) / len(periods), 1),
            "total_fuel_kg": round(total_fuel, 2)
        }
    
    def check_spacing(self, plane_raan_deg: float) -> List[Dict]:
        """
        Check mean anomaly spacing of satellites in a plane.
        
        Returns:
            List of spacing anomalies
        """
        plane_sats = [s for s in self.satellites.values()
                      if abs(s.raan_deg - plane_raan_deg) < 5.0]
        
        if len(plane_sats) < 2:
            return []
        
        # Sort by mean anomaly
        plane_sats.sort(key=lambda s: s.mean_anomaly_deg)
        
        anomalies = []
        expected_spacing = 360.0 / len(plane_sats)
        
        for i in range(len(plane_sats)):
            j = (i + 1) % len(plane_sats)
            actual = (plane_sats[j].mean_anomaly_deg - plane_sats[i].mean_anomaly_deg) % 360.0
            error = actual - expected_spacing
            
            if abs(error) > expected_spacing * 0.1:  # >10% deviation
                anomalies.append({
                    "between": (plane_sats[i].sat_id, plane_sats[j].sat_id),
                    "expected_deg": round(expected_spacing, 2),
                    "actual_deg": round(actual, 2),
                    "error_deg": round(error, 2)
                })
        
        return anomalies


class OrbitMaintenance:
    """
    Station-keeping and orbit maintenance for constellation satellites.
    
    Handles drag compensation and phasing corrections.
    """
    
    # Atmospheric density model (simplified)
    RHO_0 = 1.225  # kg/m^3 at sea level
    H_SCALE = 8500.0  # Scale height in m
    
    def __init__(self, satellite: Satellite, drag_coefficient: float = 2.2,
                 area_m2: float = 1.0):
        self.sat = satellite
        self.Cd = drag_coefficient
        self.A = area_m2
    
    def atmospheric_density(self, altitude_km: float) -> float:
        """Exponential atmosphere model."""
        h_m = altitude_km * 1000.0
        return self.RHO_0 * math.exp(-h_m / self.H_SCALE)
    
    def drag_acceleration(self, altitude_km: float, velocity_ms: float) -> float:
        """Calculate drag acceleration magnitude."""
        rho = self.atmospheric_density(altitude_km)
        return 0.5 * rho * velocity_ms**2 * self.Cd * self.A / self.sat.mass_kg
    
    def semi_major_axis_decay_rate(self) -> float:
        """
        Rate of semi-major axis decay due to drag (m/s).
        
        Returns:
            Decay rate in m/s
        """
        a_km = self.sat.semi_major_axis_km
        altitude_km = a_km - EARTH_RADIUS_KM
        
        # Orbital velocity
        v_ms = math.sqrt(MU_EARTH_KM3_S2 * 1e9 / (a_km * 1000.0))
        
        # Drag acceleration
        a_drag = self.drag_acceleration(altitude_km, v_ms)
        
        # Semi-major axis decay (simplified)
        da_dt = -2 * a_drag * (a_km * 1000.0) / v_ms
        
        return da_dt  # m/s
    
    def required_station_keeping_dv(self, days: float = 30.0) -> float:
        """
        Calculate delta-v required for station-keeping over given period.
        
        Args:
            days: Time period in days
        
        Returns:
            Required delta-v in m/s
        """
        da_dt = self.semi_major_axis_decay_rate()  # m/s
        
        # Convert to km/day
        da_dt_km_day = da_dt * 86400.0 / 1000.0
        total_decay_km = abs(da_dt_km_day) * days
        
        # Delta-v to compensate (Hohmann-like boost)
        a_km = self.sat.semi_major_axis_km
        v_ms = math.sqrt(MU_EARTH_KM3_S2 * 1e9 / (a_km * 1000.0))
        
        # Small correction: dv ≈ v * da / (2a)
        dv = v_ms * total_decay_km / (2 * a_km)
        
        return dv
    
    def phasing_maneuver(self, desired_phase_deg: float,
                         current_phase_deg: float) -> Dict:
        """
        Plan a phasing maneuver to achieve desired orbital phase.
        
        Uses drift orbit method: temporarily change semi-major axis
        to drift relative to constellation.
        
        Args:
            desired_phase_deg: Target mean anomaly phase
            current_phase_deg: Current mean anomaly phase
        
        Returns:
            Maneuver plan
        """
        phase_error = (desired_phase_deg - current_phase_deg) % 360.0
        if phase_error > 180.0:
            phase_error -= 360.0
        
        n = self.sat.mean_motion_rad_s  # rad/s
        T = 2 * math.pi / n  # Period in s
        
        # To drift by phase_error degrees in time t:
        # Use drift orbit with different period T_drift
        # phase_error_rad = (n - n_drift) * t
        # Choose t = N orbits for efficiency
        
        # Simple approach: drift for one orbit period
        t_drift = T
        n_drift = n - math.radians(phase_error) / t_drift
        
        # Required semi-major axis change
        a_current = self.sat.semi_major_axis_km * 1000.0  # m
        a_drift = (MU_EARTH_KM3_S2 * 1e9 / n_drift**2)**(1/3)
        
        # Delta-v for orbit change (circular approximation)
        v_current = math.sqrt(MU_EARTH_KM3_S2 * 1e9 / a_current)
        v_drift = math.sqrt(MU_EARTH_KM3_S2 * 1e9 / a_drift)
        
        dv = abs(v_drift - v_current)
        
        return {
            "phase_error_deg": round(phase_error, 2),
            "drift_time_min": round(t_drift / 60.0, 1),
            "delta_v_ms": round(dv, 3),
            "semi_major_axis_change_m": round(a_drift - a_current, 1),
            "orbits_to_drift": 1
        }


class ConstellationCollisionAvoidance:
    """
    Intra-constellation collision avoidance.
    
    Checks for close approaches between constellation satellites.
    """
    
    def __init__(self, min_separation_km: float = 10.0):
        self.min_separation = min_separation_km
    
    def check_pair(self, sat1: Satellite, sat2: Satellite,
                   time_hours: float = 24.0) -> Optional[Dict]:
        """
        Check for close approach between two satellites.
        
        Simplified check assuming circular orbits and same plane.
        
        Returns:
            Close approach info or None
        """
        # Different planes - minimal risk
        if abs(sat1.raan_deg - sat2.raan_deg) > 10.0:
            return None
        
        # Same plane - check phase difference
        phase_diff = abs(sat1.mean_anomaly_deg - sat2.mean_anomaly_deg) % 360.0
        if phase_diff > 180.0:
            phase_diff = 360.0 - phase_diff
        
        # Arc distance
        r = sat1.semi_major_axis_km
        arc_distance = math.radians(phase_diff) * r
        
        if arc_distance < self.min_separation:
            return {
                "satellites": (sat1.sat_id, sat2.sat_id),
                "separation_km": round(arc_distance, 2),
                "phase_diff_deg": round(phase_diff, 2),
                "risk_level": "HIGH" if arc_distance < 1.0 else "MODERATE"
            }
        
        return None
    
    def scan_constellation(self, constellation: ConstellationPlanner,
                           time_hours: float = 24.0) -> List[Dict]:
        """Scan entire constellation for close approaches."""
        risks = []
        sats = list(constellation.satellites.values())
        
        for i in range(len(sats)):
            for j in range(i + 1, len(sats)):
                result = self.check_pair(sats[i], sats[j], time_hours)
                if result:
                    risks.append(result)
        
        return risks
