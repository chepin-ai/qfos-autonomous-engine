"""
Coverage Analysis Module
Ground target visibility, revisit time, and coverage gap analysis
for Earth-orbiting satellites.
"""

import math
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass


@dataclass
class GroundTarget:
    """Ground target location."""
    name: str
    latitude_deg: float
    longitude_deg: float
    min_elevation_deg: float = 5.0  # Minimum elevation for access


@dataclass
class CoveragePass:
    """A coverage pass over a target."""
    target_name: str
    start_time_min: float
    end_time_min: float
    max_elevation_deg: float
    access_duration_min: float


class CoverageAnalyzer:
    """
    Analyze satellite coverage of ground targets.
    
    Computes access windows, revisit times, and coverage statistics
    for Earth observation and communication missions.
    """
    
    EARTH_RADIUS_KM = 6378.137
    
    def __init__(self, satellite_altitude_km: float,
                 inclination_deg: float = 0.0,
                 orbital_period_min: float = 0.0):
        """
        Args:
            satellite_altitude_km: Satellite altitude
            inclination_deg: Orbit inclination
            orbital_period_min: Orbital period (computed if 0)
        """
        self.altitude_km = satellite_altitude_km
        self.inclination_deg = inclination_deg
        
        if orbital_period_min > 0:
            self.period_min = orbital_period_min
        else:
            # Compute from altitude
            mu = 398600.4418  # km^3/s^2
            a = self.EARTH_RADIUS_KM + satellite_altitude_km
            self.period_min = 2.0 * math.pi * math.sqrt(a**3 / mu) / 60.0
        
        # Compute maximum Earth central angle for access
        self._compute_access_geometry()
    
    def _compute_access_geometry(self):
        """Compute access geometry parameters."""
        re = self.EARTH_RADIUS_KM
        h = self.altitude_km
        
        # Maximum Earth central angle for 0 deg elevation
        rho = math.asin(re / (re + h))
        self.max_earth_angle_rad = rho
        
        # Maximum slant range
        self.max_slant_range_km = math.sqrt((re + h)**2 - re**2)
        
        # Swath half-angle at nadir
        self.swath_half_angle_rad = math.acos(re / (re + h))
    
    def elevation_to_earth_angle(self, elevation_deg: float) -> float:
        """
        Convert minimum elevation to Earth central angle.
        
        Args:
            elevation_deg: Minimum elevation angle
        
        Returns:
            Earth central angle in radians
        """
        re = self.EARTH_RADIUS_KM
        h = self.altitude_km
        eta = math.radians(elevation_deg)
        
        # Law of sines in the observation triangle
        # sin(rho) / cos(eta) = sin(eta + rho) / (1 + h/re)
        
        # Iterative solution for rho
        rho = self.max_earth_angle_rad  # Start with 0-deg elevation
        
        for _ in range(10):
            f = math.sin(rho) * (1.0 + h/re) - math.cos(eta) * math.sin(eta + rho)
            fp = math.cos(rho) * (1.0 + h/re) - math.cos(eta) * math.cos(eta + rho)
            if abs(fp) > 1e-12:
                rho -= f / fp
        
        return rho
    
    def can_access(self, target_lat_deg: float, target_lon_deg: float,
                   satellite_lat_deg: float, satellite_lon_deg: float,
                   min_elevation_deg: float = 5.0) -> bool:
        """
        Check if satellite can access target.
        
        Args:
            target_lat_deg: Target latitude
            target_lon_deg: Target longitude
            satellite_lat_deg: Satellite latitude
            satellite_lon_deg: Satellite longitude
            min_elevation_deg: Minimum elevation
        
        Returns:
            True if access is possible
        """
        # Earth central angle between target and satellite subpoint
        dlat = math.radians(satellite_lat_deg - target_lat_deg)
        dlon = math.radians(satellite_lon_deg - target_lon_deg)
        lat1 = math.radians(target_lat_deg)
        lat2 = math.radians(satellite_lat_deg)
        
        a = (math.sin(dlat/2.0)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2.0)**2)
        
        # Clamp to [0, 1] to avoid numerical issues
        a = min(1.0, max(0.0, a))
        earth_angle = 2.0 * math.asin(math.sqrt(a))
        
        # Maximum allowed Earth angle for this elevation
        max_angle = self.elevation_to_earth_angle(min_elevation_deg)
        
        return earth_angle <= max_angle
    
    def compute_access_windows(self, target: GroundTarget,
                                simulation_duration_min: float = 1440.0,
                                time_step_min: float = 1.0) -> List[CoveragePass]:
        """
        Compute access windows for a target over simulation period.
        
        Assumes circular orbit with ground track propagation.
        
        Args:
            target: Ground target
            simulation_duration_min: Simulation duration
            time_step_min: Time step
        
        Returns:
            List of CoveragePass objects
        """
        passes = []
        
        # Simplified ground track model
        # Assume satellite starts at equator, longitude 0
        # Ground track shifts west by ~22.5 deg per orbit (Earth rotation)
        
        in_access = False
        access_start = 0.0
        max_elevation = 0.0
        
        for t in [i * time_step_min for i in range(int(simulation_duration_min / time_step_min) + 1)]:
            # Approximate satellite position
            orbits = t / self.period_min
            
            # Latitude varies sinusoidally with inclination
            sat_lat = self.inclination_deg * math.sin(2.0 * math.pi * orbits)
            
            # Longitude drifts west due to Earth rotation
            earth_rotation_deg = 360.0 * (t / 1436.07)  # Sidereal day
            sat_lon = (360.0 * orbits * (self.period_min / 1436.07) - earth_rotation_deg) % 360.0
            if sat_lon > 180.0:
                sat_lon -= 360.0
            
            # Check access
            has_access = self.can_access(
                target.latitude_deg, target.longitude_deg,
                sat_lat, sat_lon, target.min_elevation_deg
            )
            
            # Compute elevation (simplified)
            if has_access:
                dlat = math.radians(sat_lat - target.latitude_deg)
                dlon = math.radians(sat_lon - target.longitude_deg)
                lat1 = math.radians(target.latitude_deg)
                lat2 = math.radians(sat_lat)
                a = math.sin(dlat/2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2.0)**2
                a = min(1.0, max(0.0, a))
                earth_angle = 2.0 * math.asin(math.sqrt(a))
                
                # Approximate elevation from earth angle
                elevation = max(0.0, 90.0 - math.degrees(earth_angle) * (self.EARTH_RADIUS_KM + self.altitude_km) / self.altitude_km)
                max_elevation = max(max_elevation, elevation)
            
            if has_access and not in_access:
                access_start = t
                in_access = True
                max_elevation = 0.0
            elif not has_access and in_access:
                passes.append(CoveragePass(
                    target_name=target.name,
                    start_time_min=access_start,
                    end_time_min=t,
                    max_elevation_deg=round(max_elevation, 2),
                    access_duration_min=round(t - access_start, 2)
                ))
                in_access = False
        
        # Close final pass
        if in_access:
            passes.append(CoveragePass(
                target_name=target.name,
                start_time_min=access_start,
                end_time_min=simulation_duration_min,
                max_elevation_deg=round(max_elevation, 2),
                access_duration_min=round(simulation_duration_min - access_start, 2)
            ))
        
        return passes
    
    def revisit_time(self, target: GroundTarget,
                     simulation_duration_min: float = 1440.0) -> Dict:
        """
        Compute revisit statistics for a target.
        
        Args:
            target: Ground target
            simulation_duration_min: Simulation duration
        
        Returns:
            Dictionary with revisit statistics
        """
        passes = self.compute_access_windows(target, simulation_duration_min)
        
        if len(passes) < 2:
            return {
                "num_passes": len(passes),
                "avg_revisit_min": None,
                "max_gap_min": None,
                "min_gap_min": None
            }
        
        gaps = []
        for i in range(1, len(passes)):
            gap = passes[i].start_time_min - passes[i-1].end_time_min
            gaps.append(gap)
        
        return {
            "num_passes": len(passes),
            "avg_revisit_min": round(sum(gaps) / len(gaps), 2),
            "max_gap_min": round(max(gaps), 2),
            "min_gap_min": round(min(gaps), 2),
            "avg_pass_duration_min": round(
                sum(p.access_duration_min for p in passes) / len(passes), 2
            )
        }
    
    def swath_width_km(self, look_angle_deg: float = 0.0) -> float:
        """
        Compute ground swath width.
        
        Args:
            look_angle_deg: Off-nadir look angle
        
        Returns:
            Swath width in km
        """
        re = self.EARTH_RADIUS_KM
        h = self.altitude_km
        
        # Central angle for nadir
        theta = self.swath_half_angle_rad
        
        # Adjust for off-nadir look
        if look_angle_deg != 0.0:
            look = math.radians(look_angle_deg)
            # Simplified adjustment
            theta *= math.cos(look)
        
        # Arc length
        swath = 2.0 * re * theta
        return round(swath, 2)
    
    def coverage_fraction(self, latitude_band_deg: Tuple[float, float] = (-60.0, 60.0),
                          simulation_days: float = 1.0) -> float:
        """
        Estimate coverage fraction for a latitude band.
        
        Args:
            latitude_band_deg: (min_lat, max_lat)
            simulation_days: Simulation duration
        
        Returns:
            Fraction of area covered (0.0-1.0)
        """
        # Simplified: coverage fraction based on orbit inclination and altitude
        band_half_width = (latitude_band_deg[1] - latitude_band_deg[0]) / 2.0
        
        # Maximum latitude reachable
        max_reach = abs(self.inclination_deg) + math.degrees(self.swath_half_angle_rad)
        
        if max_reach >= abs(latitude_band_deg[1]):
            coverage = 1.0
        elif max_reach <= abs(latitude_band_deg[0]):
            coverage = 0.0
        else:
            coverage = (max_reach - abs(latitude_band_deg[0])) / (abs(latitude_band_deg[1]) - abs(latitude_band_deg[0]))
        
        return round(min(1.0, max(0.0, coverage)), 4)
