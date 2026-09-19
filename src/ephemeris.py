"""
Ephemeris Module
Planetary position computation using simplified analytical series.
Provides J2000 ecliptic positions for major solar system bodies.
"""

import math
from typing import Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class OrbitalElements:
    """Keplerian orbital elements at epoch."""
    a_au: float           # Semi-major axis (AU)
    e: float              # Eccentricity
    i_deg: float          # Inclination (deg)
    L_deg: float          # Mean longitude (deg)
    lon_peri_deg: float   # Longitude of perihelion (deg)
    Omega_deg: float      # Longitude of ascending node (deg)


class PlanetaryEphemeris:
    """
    Simplified planetary ephemeris using Keplerian elements.
    
    Based on JPL Horizons simplified elements with secular rates.
    Valid for approximately 1800-2050.
    """
    
    # J2000.0 Keplerian elements and secular rates
    # Format: [a, e, i, L, lon_peri, Omega] in [AU, deg, deg/century]
    ELEMENTS = {
        "Mercury": OrbitalElements(
            a_au=0.38709927, e=0.20563593, i_deg=7.00497902,
            L_deg=252.25032350, lon_peri_deg=77.45779628, Omega_deg=48.33076593
        ),
        "Venus": OrbitalElements(
            a_au=0.72333566, e=0.00677672, i_deg=3.39467605,
            L_deg=181.97909950, lon_peri_deg=131.60246718, Omega_deg=76.67984255
        ),
        "Earth": OrbitalElements(
            a_au=1.00000261, e=0.01671123, i_deg=-0.00001531,
            L_deg=100.46457166, lon_peri_deg=102.93768193, Omega_deg=0.0
        ),
        "Mars": OrbitalElements(
            a_au=1.52371034, e=0.09339410, i_deg=1.84969142,
            L_deg=-4.55343205, lon_peri_deg=-23.94362959, Omega_deg=49.55953891
        ),
        "Jupiter": OrbitalElements(
            a_au=5.20288700, e=0.04838624, i_deg=1.30439695,
            L_deg=34.39644051, lon_peri_deg=14.72847983, Omega_deg=100.47390909
        ),
        "Saturn": OrbitalElements(
            a_au=9.53667594, e=0.05386179, i_deg=2.48599187,
            L_deg=49.95424423, lon_peri_deg=92.59887831, Omega_deg=113.66242448
        ),
        "Uranus": OrbitalElements(
            a_au=19.18916464, e=0.04725744, i_deg=0.77263783,
            L_deg=313.23810451, lon_peri_deg=170.95427630, Omega_deg=74.01692503
        ),
        "Neptune": OrbitalElements(
            a_au=30.06992276, e=0.00859048, i_deg=1.77004347,
            L_deg=-55.12002969, lon_peri_deg=44.96476227, Omega_deg=131.78422574
        ),
    }
    
    # Secular rates (per Julian century)
    RATES = {
        "Mercury":   [0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081],
        "Venus":     [0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418],
        "Earth":     [0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0],
        "Mars":      [0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343],
        "Jupiter":   [-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106],
        "Saturn":    [-0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794],
        "Uranus":    [-0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589],
        "Neptune":   [0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664],
    }
    
    J2000_EPOCH_JD = 2451545.0
    DAYS_PER_CENTURY = 36525.0
    
    @classmethod
    def compute_elements(cls, body_name: str, julian_date: float) -> OrbitalElements:
        """
        Compute orbital elements at given Julian date.
        
        Args:
            body_name: Planet name
            julian_date: Julian date
        
        Returns:
            OrbitalElements at epoch
        """
        if body_name not in cls.ELEMENTS:
            raise ValueError(f"Unknown body: {body_name}")
        
        base = cls.ELEMENTS[body_name]
        rates = cls.RATES[body_name]
        
        # Time from J2000 in centuries
        T = (julian_date - cls.J2000_EPOCH_JD) / cls.DAYS_PER_CENTURY
        
        return OrbitalElements(
            a_au=base.a_au + rates[0] * T,
            e=base.e + rates[1] * T,
            i_deg=base.i_deg + rates[2] * T,
            L_deg=base.L_deg + rates[3] * T,
            lon_peri_deg=base.lon_peri_deg + rates[4] * T,
            Omega_deg=base.Omega_deg + rates[5] * T
        )
    
    @classmethod
    def position(cls, body_name: str, julian_date: float) -> Tuple[float, float, float]:
        """
        Compute heliocentric position in AU.
        
        Args:
            body_name: Planet name
            julian_date: Julian date
        
        Returns:
            (x, y, z) in AU, J2000 ecliptic
        """
        elements = cls.compute_elements(body_name, julian_date)
        
        # Argument of perihelion
        omega_deg = elements.lon_peri_deg - elements.Omega_deg
        
        # Mean anomaly
        M_deg = elements.L_deg - elements.lon_peri_deg
        M_rad = math.radians(M_deg)
        
        # Solve Kepler's equation
        E_rad = cls._solve_kepler(M_rad, elements.e)
        
        # True anomaly
        nu_rad = 2.0 * math.atan2(
            math.sqrt(1.0 + elements.e) * math.sin(E_rad / 2.0),
            math.sqrt(1.0 - elements.e) * math.cos(E_rad / 2.0)
        )
        
        # Distance
        r = elements.a_au * (1.0 - elements.e * math.cos(E_rad))
        
        # Position in orbital plane
        x_orb = r * math.cos(nu_rad)
        y_orb = r * math.sin(nu_rad)
        
        # Rotate to ecliptic coordinates
        i_rad = math.radians(elements.i_deg)
        Omega_rad = math.radians(elements.Omega_deg)
        omega_rad = math.radians(omega_deg)
        
        # 3D rotation
        cos_O = math.cos(Omega_rad)
        sin_O = math.sin(Omega_rad)
        cos_i = math.cos(i_rad)
        sin_i = math.sin(i_rad)
        cos_w = math.cos(omega_rad)
        sin_w = math.sin(omega_rad)
        
        x = (cos_O * cos_w - sin_O * sin_w * cos_i) * x_orb + \
            (-cos_O * sin_w - sin_O * cos_w * cos_i) * y_orb
        y = (sin_O * cos_w + cos_O * sin_w * cos_i) * x_orb + \
            (-sin_O * sin_w + cos_O * cos_w * cos_i) * y_orb
        z = (sin_w * sin_i) * x_orb + (cos_w * sin_i) * y_orb
        
        return (x, y, z)
    
    @classmethod
    def _solve_kepler(cls, M: float, e: float, tol: float = 1e-10, max_iter: int = 50) -> float:
        """Solve Kepler's equation using Newton-Raphson."""
        E = M if e < 0.8 else math.pi
        for _ in range(max_iter):
            f = E - e * math.sin(E) - M
            fp = 1.0 - e * math.cos(E)
            if abs(fp) < 1e-15:
                break
            delta = f / fp
            E -= delta
            if abs(delta) < tol:
                break
        return E
    
    @classmethod
    def earth_position(cls, julian_date: float) -> Tuple[float, float, float]:
        """Convenience method for Earth position."""
        return cls.position("Earth", julian_date)
    
    @classmethod
    def mars_position(cls, julian_date: float) -> Tuple[float, float, float]:
        """Convenience method for Mars position."""
        return cls.position("Mars", julian_date)
    
    @classmethod
    def get_available_bodies(cls) -> list:
        """Return list of available planetary bodies."""
        return list(cls.ELEMENTS.keys())
    
    @classmethod
    def distance_between(cls, body1: str, body2: str, julian_date: float) -> float:
        """
        Compute distance between two bodies.
        
        Returns:
            Distance in AU
        """
        p1 = cls.position(body1, julian_date)
        p2 = cls.position(body2, julian_date)
        return math.sqrt(sum((p1[i] - p2[i])**2 for i in range(3)))
    
    @classmethod
    def light_time(cls, body1: str, body2: str, julian_date: float) -> float:
        """
        Compute one-way light time between bodies.
        
        Returns:
            Light time in minutes
        """
        dist_au = cls.distance_between(body1, body2, julian_date)
        # Light speed: ~499.0 seconds per AU
        return dist_au * 499.0 / 60.0


class JulianDate:
    """Julian date conversion utilities."""
    
    @staticmethod
    def from_calendar(year: int, month: int, day: int,
                       hour: float = 0.0) -> float:
        """Convert calendar date to Julian date."""
        if month <= 2:
            year -= 1
            month += 12
        
        A = int(year / 100)
        B = 2 - A + int(A / 4)
        
        JD = (int(365.25 * (year + 4716)) +
              int(30.6001 * (month + 1)) +
              day + hour / 24.0 + B - 1524.5)
        
        return JD
    
    @staticmethod
    def to_calendar(jd: float) -> Tuple[int, int, int, float]:
        """Convert Julian date to calendar date."""
        jd = jd + 0.5
        Z = int(jd)
        F = jd - Z
        
        if Z < 2299161:
            A = Z
        else:
            alpha = int((Z - 1867216.25) / 36524.25)
            A = Z + 1 + alpha - int(alpha / 4)
        
        B = A + 1524
        C = int((B - 122.1) / 365.25)
        D = int(365.25 * C)
        E = int((B - D) / 30.6001)
        
        day = B - D - int(30.6001 * E) + F
        
        if E < 14:
            month = E - 1
        else:
            month = E - 13
        
        if month > 2:
            year = C - 4716
        else:
            year = C - 4715
        
        day_int = int(day)
        hour = (day - day_int) * 24.0
        
        return (year, month, day_int, hour)
