"""
Eclipse Calculator Module
Compute Earth shadow crossings, umbra/penumbra durations,
and eclipse seasons for Earth-orbiting satellites.
"""

import math
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class EclipseType(Enum):
    """Type of eclipse."""
    UMBRA = "umbra"  # Full shadow
    PENUMBRA = "penumbra"  # Partial shadow
    NONE = "none"


@dataclass
class EclipseEvent:
    """An eclipse event."""
    eclipse_type: EclipseType
    start_time_min: float
    end_time_min: float
    duration_min: float
    max_obscuration: float  # 0.0-1.0, 1.0 = full umbra


class EclipseCalculator:
    """
    Eclipse calculator for Earth-orbiting satellites.
    
    Computes Earth shadow geometry and eclipse durations
    for power and thermal analysis.
    """
    
    SUN_RADIUS_KM = 696340.0
    EARTH_RADIUS_KM = 6378.137
    AU_KM = 149597870.7
    
    def __init__(self, satellite_altitude_km: float,
                 orbital_period_min: float = 0.0,
                 orbit_inclination_deg: float = 0.0):
        """
        Args:
            satellite_altitude_km: Satellite altitude
            orbital_period_min: Orbital period (computed if 0)
            orbit_inclination_deg: Orbit inclination
        """
        self.altitude_km = satellite_altitude_km
        self.inclination_deg = orbit_inclination_deg
        
        if orbital_period_min > 0:
            self.period_min = orbital_period_min
        else:
            mu = 398600.4418
            a = self.EARTH_RADIUS_KM + satellite_altitude_km
            self.period_min = 2.0 * math.pi * math.sqrt(a**3 / mu) / 60.0
        
        # Shadow geometry
        self._compute_shadow_geometry()
    
    def _compute_shadow_geometry(self):
        """Compute shadow cone geometry."""
        rs = self.SUN_RADIUS_KM
        re = self.EARTH_RADIUS_KM
        h = self.altitude_km
        
        # Distance from Earth center to shadow cone apex
        d_apex = re * self.AU_KM / (rs - re)
        
        # Shadow cone half-angle
        self.shadow_cone_angle_rad = math.asin(re / d_apex)
        
        # Distance to penumbra cone apex
        d_penumbra_apex = re * self.AU_KM / (rs + re)
        self.penumbra_cone_angle_rad = math.asin(re / d_penumbra_apex)
        
        # Satellite orbit radius
        r_orbit = re + h
        
        # Maximum Earth angle for umbra (simplified)
        self.max_umbra_angle_rad = math.asin(re / r_orbit)
        
        # Umbra duration fraction of orbit
        # Simplified: chord through shadow cone
        umbra_chord = 2.0 * math.sqrt(max(0.0, re**2 - h**2))
        orbit_circumference = 2.0 * math.pi * r_orbit
        self.umbra_fraction = umbra_chord / orbit_circumference if orbit_circumference > 0 else 0.0
        
        # Clamp
        self.umbra_fraction = min(0.5, max(0.0, self.umbra_fraction))
    
    def is_in_shadow(self, sun_direction: Tuple[float, float, float],
                     satellite_position: Tuple[float, float, float]) -> EclipseType:
        """
        Check if satellite is in Earth's shadow.
        
        Args:
            sun_direction: Unit vector toward Sun
            satellite_position: Satellite position in ECI (km)
        
        Returns:
            EclipseType
        """
        x, y, z = satellite_position
        r = math.sqrt(x**2 + y**2 + z**2)
        
        if r < 1e-6:
            return EclipseType.NONE
        
        # Satellite unit position vector
        sat_unit = (x/r, y/r, z/r)
        
        # Sun direction dot satellite position = cos(angle) * r
        sun_sat_dot = sun_direction[0]*sat_unit[0] + sun_direction[1]*sat_unit[1] + sun_direction[2]*sat_unit[2]
        
        # If satellite is on sun-facing side, not in shadow
        if sun_sat_dot > 0:
            return EclipseType.NONE
        
        # Earth-satellite-sun angle
        angle_from_antisun = math.acos(max(-1.0, min(1.0, -sun_sat_dot)))
        
        # Check against shadow cone
        if angle_from_antisun < self.max_umbra_angle_rad * 0.9:
            return EclipseType.UMBRA
        elif angle_from_antisun < self.max_umbra_angle_rad * 1.2:
            return EclipseType.PENUMBRA
        
        return EclipseType.NONE
    
    def eclipse_duration_min(self) -> float:
        """
        Compute maximum eclipse duration.
        
        Returns:
            Duration in minutes
        """
        return self.umbra_fraction * self.period_min
    
    def eclipse_seasons(self, year_days: float = 365.25) -> List[Dict]:
        """
        Compute eclipse seasons for the year.
        
        Eclipse seasons occur when the Sun is near the orbital plane.
        For inclined orbits, this happens twice per year.
        
        Args:
            year_days: Days in year
        
        Returns:
            List of eclipse season dictionaries
        """
        seasons = []
        
        # Eclipse season duration (approximate)
        # Sun moves ~1 deg/day along ecliptic
        # Season lasts while Sun is within ~12 deg of node
        season_duration_days = 24.0  # ~24 days per season
        
        # Two eclipse seasons per year, separated by ~6 months
        for i in range(2):
            start_day = i * year_days / 2.0 - season_duration_days / 2.0
            seasons.append({
                "season_number": i + 1,
                "start_day": round(start_day, 1),
                "end_day": round(start_day + season_duration_days, 1),
                "duration_days": season_duration_days,
                "max_eclipse_duration_min": round(self.eclipse_duration_min(), 2)
            })
        
        return seasons
    
    def daily_eclipse_profile(self, num_orbits: int = 15) -> List[EclipseEvent]:
        """
        Generate eclipse events for a day.
        
        Args:
            num_orbits: Number of orbits per day
        
        Returns:
            List of EclipseEvent
        """
        events = []
        
        # Simplified: assume one eclipse per orbit when in season
        # Random phase for demonstration
        import random
        random.seed(42)
        
        eclipse_duration = self.eclipse_duration_min()
        
        for orbit in range(num_orbits):
            orbit_start = orbit * self.period_min
            
            # Eclipse occurs at random point in orbit
            eclipse_center = orbit_start + random.uniform(0.1, 0.9) * self.period_min
            
            if eclipse_duration > 0.1:
                events.append(EclipseEvent(
                    eclipse_type=EclipseType.UMBRA,
                    start_time_min=round(eclipse_center - eclipse_duration/2.0, 2),
                    end_time_min=round(eclipse_center + eclipse_duration/2.0, 2),
                    duration_min=round(eclipse_duration, 2),
                    max_obscuration=1.0
                ))
        
        return events
    
    def power_impact(self, solar_array_power_w: float,
                     battery_capacity_wh: float,
                     base_load_w: float) -> Dict:
        """
        Assess power system impact of eclipses.
        
        Args:
            solar_array_power_w: Solar array power in sunlight
            battery_capacity_wh: Battery capacity
            base_load_w: Base load during eclipse
        
        Returns:
            Power impact assessment
        """
        eclipse_duration = self.eclipse_duration_min()
        
        # Energy required during eclipse
        energy_required_wh = base_load_w * (eclipse_duration / 60.0)
        
        # Battery depth of discharge
        dod_percent = (energy_required_wh / battery_capacity_wh) * 100.0
        
        # Recharge time after eclipse
        recharge_power = solar_array_power_w - base_load_w
        if recharge_power > 0:
            recharge_time_min = (energy_required_wh / recharge_power) * 60.0
        else:
            recharge_time_min = float('inf')
        
        # Critical check
        if dod_percent > 80.0:
            status = "CRITICAL"
        elif dod_percent > 50.0:
            status = "WARNING"
        else:
            status = "OK"
        
        return {
            "eclipse_duration_min": round(eclipse_duration, 2),
            "energy_required_wh": round(energy_required_wh, 2),
            "battery_dod_percent": round(dod_percent, 2),
            "recharge_time_min": round(recharge_time_min, 2) if recharge_time_min != float('inf') else -1.0,
            "status": status,
            "sufficient_battery": energy_required_wh < battery_capacity_wh * 0.8
        }
    
    @staticmethod
    def sun_direction_eci(julian_date: float) -> Tuple[float, float, float]:
        """
        Compute Sun direction in ECI frame (simplified).
        
        Args:
            julian_date: Julian date
        
        Returns:
            Unit vector toward Sun
        """
        # Simplified: Sun moves along ecliptic
        # Mean anomaly of Sun
        T = (julian_date - 2451545.0) / 36525.0
        M = math.radians(357.52911 + 35999.05029 * T - 0.0001537 * T**2)
        
        # Ecliptic longitude
        L = math.radians(280.46646 + 36000.76983 * T + 0.0003032 * T**2)
        
        # Obliquity of ecliptic
        epsilon = math.radians(23.439291 - 0.0130042 * T)
        
        # Sun direction in ECI
        x = math.cos(L)
        y = math.sin(L) * math.cos(epsilon)
        z = math.sin(L) * math.sin(epsilon)
        
        # Normalize
        r = math.sqrt(x**2 + y**2 + z**2)
        return (x/r, y/r, z/r)
