"""
Ephemeris Generator Module
Body position tables, interpolation, and time scaling
for celestial body ephemeris generation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EphemerisEntry:
    """A single ephemeris entry."""
    timestamp: float  # seconds from epoch
    position: Tuple[float, float, float]  # km
    velocity: Tuple[float, float, float]  # km/s


class LinearInterpolator:
    """
    Linear interpolation for ephemeris tables.
    """
    
    def interpolate(self, t: float, t0: float, t1: float,
                   y0: float, y1: float) -> float:
        """
        Linear interpolation.
        
        Args:
            t: Target time
            t0, t1: Bounding times
            y0, y1: Values at bounding times
        
        Returns:
            Interpolated value
        """
        if abs(t1 - t0) < 1e-15:
            return y0
        return y0 + (y1 - y0) * (t - t0) / (t1 - t0)
    
    def interpolate_3d(self, t: float, t0: float, t1: float,
                      p0: Tuple[float, float, float],
                      p1: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Interpolate 3D position."""
        return (
            self.interpolate(t, t0, t1, p0[0], p1[0]),
            self.interpolate(t, t0, t1, p0[1], p1[1]),
            self.interpolate(t, t0, t1, p0[2], p1[2])
        )


class LagrangeInterpolator:
    """
    Lagrange polynomial interpolation.
    """
    
    def __init__(self, order: int = 4):
        """
        Args:
            order: Number of points to use (degree = order - 1)
        """
        self.order = order
    
    def interpolate(self, t: float, times: List[float],
                   values: List[float]) -> float:
        """
        Lagrange interpolation.
        
        Args:
            t: Target time
            times: Sample times
            values: Sample values
        
        Returns:
            Interpolated value
        """
        n = min(self.order, len(times), len(values))
        
        # Find center index
        idx = 0
        min_diff = abs(t - times[0])
        for i in range(1, len(times)):
            if abs(t - times[i]) < min_diff:
                min_diff = abs(t - times[i])
                idx = i
        
        # Select window around idx
        half = n // 2
        start = max(0, idx - half)
        end = min(len(times), start + n)
        start = max(0, end - n)
        
        t_win = times[start:end]
        v_win = values[start:end]
        
        # Lagrange interpolation
        result = 0.0
        for i in range(len(t_win)):
            Li = 1.0
            for j in range(len(t_win)):
                if i != j:
                    if abs(t_win[i] - t_win[j]) < 1e-15:
                        continue
                    Li *= (t - t_win[j]) / (t_win[i] - t_win[j])
            result += v_win[i] * Li
        
        return result
    
    def interpolate_3d(self, t: float, times: List[float],
                      positions: List[Tuple[float, float, float]]
                      ) -> Tuple[float, float, float]:
        """Interpolate 3D position."""
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        zs = [p[2] for p in positions]
        return (
            self.interpolate(t, times, xs),
            self.interpolate(t, times, ys),
            self.interpolate(t, times, zs)
        )


class TimeScale:
    """
    Time scaling utilities for ephemeris.
    """
    
    @staticmethod
    def jd_to_seconds(jd: float, epoch_jd: float = 2451545.0) -> float:
        """
        Convert Julian Date to seconds from epoch.
        
        Args:
            jd: Julian Date
            epoch_jd: Epoch Julian Date (J2000 default)
        
        Returns:
            Seconds from epoch
        """
        return (jd - epoch_jd) * 86400.0
    
    @staticmethod
    def seconds_to_jd(seconds: float, epoch_jd: float = 2451545.0) -> float:
        """Convert seconds to Julian Date."""
        return epoch_jd + seconds / 86400.0
    
    @staticmethod
    def gmst(jd: float) -> float:
        """
        Greenwich Mean Sidereal Time (rad).
        
        Args:
            jd: Julian Date
        
        Returns:
            GMST in radians
        """
        # Simplified GMST calculation
        d = jd - 2451545.0
        gmst_deg = 280.46061837 + 360.98564736629 * d
        gmst_deg = gmst_deg % 360.0
        return math.radians(gmst_deg)


class CelestialBody:
    """
    Simplified celestial body ephemeris model.
    """
    
    def __init__(self, name: str, orbital_period_days: float,
                 semi_major_axis_km: float,
                 eccentricity: float = 0.0,
                 inclination_deg: float = 0.0):
        """
        Args:
            name: Body name
            orbital_period_days: Orbital period (days)
            semi_major_axis_km: Semi-major axis (km)
            eccentricity: Eccentricity
            inclination_deg: Inclination (degrees)
        """
        self.name = name
        self.period = orbital_period_days * 86400.0  # seconds
        self.a = semi_major_axis_km
        self.e = eccentricity
        self.i = math.radians(inclination_deg)
    
    def position_at(self, t: float) -> Tuple[float, float, float]:
        """
        Get body position at time.
        
        Args:
            t: Time from epoch (seconds)
        
        Returns:
            Position (km)
        """
        # Simplified circular orbit
        mean_motion = 2 * math.pi / self.period
        M = mean_motion * t
        
        # For small eccentricity, nu ≈ M
        nu = M
        r = self.a * (1 - self.e**2) / (1 + self.e * math.cos(nu))
        
        x = r * math.cos(nu)
        y = r * math.sin(nu) * math.cos(self.i)
        z = r * math.sin(nu) * math.sin(self.i)
        
        return (x, y, z)


class EphemerisGenerator:
    """
    Generate and manage ephemeris tables.
    """
    
    def __init__(self):
        self.entries: List[EphemerisEntry] = []
        self.bodies: Dict[str, CelestialBody] = {}
        self.linear_interp = LinearInterpolator()
        self.lagrange_interp = LagrangeInterpolator(order=4)
    
    def add_body(self, body: CelestialBody):
        """Add celestial body."""
        self.bodies[body.name] = body
    
    def generate(self, body_name: str, start: float, end: float,
                step: float) -> List[EphemerisEntry]:
        """
        Generate ephemeris for body.
        
        Args:
            body_name: Body name
            start: Start time (seconds)
            end: End time (seconds)
            step: Time step (seconds)
        
        Returns:
            Ephemeris entries
        """
        if body_name not in self.bodies:
            return []
        
        body = self.bodies[body_name]
        entries = []
        
        t = start
        while t <= end:
            pos = body.position_at(t)
            
            # Approximate velocity by finite difference
            dt = step * 0.001
            pos_next = body.position_at(t + dt)
            vel = (
                (pos_next[0] - pos[0]) / dt,
                (pos_next[1] - pos[1]) / dt,
                (pos_next[2] - pos[2]) / dt
            )
            
            entries.append(EphemerisEntry(
                timestamp=t,
                position=pos,
                velocity=vel
            ))
            t += step
        
        return entries
    
    def interpolate_position(self, t: float,
                            entries: List[EphemerisEntry],
                            method: str = "linear"
                            ) -> Optional[Tuple[float, float, float]]:
        """
        Interpolate position at time.
        
        Args:
            t: Target time
            entries: Ephemeris entries
            method: "linear" or "lagrange"
        
        Returns:
            Interpolated position or None
        """
        if not entries or t < entries[0].timestamp or t > entries[-1].timestamp:
            return None
        
        # Find bounding entries
        for i in range(len(entries) - 1):
            if entries[i].timestamp <= t <= entries[i+1].timestamp:
                if method == "linear":
                    return self.linear_interp.interpolate_3d(
                        t,
                        entries[i].timestamp, entries[i+1].timestamp,
                        entries[i].position, entries[i+1].position
                    )
                elif method == "lagrange":
                    # Use surrounding points
                    start = max(0, i - 1)
                    end = min(len(entries), i + 3)
                    times = [e.timestamp for e in entries[start:end]]
                    positions = [e.position for e in entries[start:end]]
                    return self.lagrange_interp.interpolate_3d(t, times, positions)
        
        return None
    
    def get_entry_at(self, t: float,
                    entries: List[EphemerisEntry]) -> Optional[EphemerisEntry]:
        """Get entry closest to time."""
        if not entries:
            return None
        
        closest = entries[0]
        min_diff = abs(t - closest.timestamp)
        
        for entry in entries[1:]:
            diff = abs(t - entry.timestamp)
            if diff < min_diff:
                min_diff = diff
                closest = entry
        
        return closest
    
    def ephemeris_summary(self, entries: List[EphemerisEntry]) -> Dict:
        """Get ephemeris summary."""
        if not entries:
            return {}
        
        times = [e.timestamp for e in entries]
        return {
            "count": len(entries),
            "start": min(times),
            "end": max(times),
            "span": max(times) - min(times),
            "bodies": list(self.bodies.keys())
        }
