"""
TLE Propagator Module
Parse Two-Line Element sets and propagate orbits using simplified SGP4.
Standard NORAD TLE format support for Earth-orbiting satellites.
"""

import math
import re
from typing import Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class TLEData:
    """Parsed TLE data structure."""
    # Line 0 (optional name)
    name: str = ""
    
    # Line 1
    satellite_number: int = 0
    classification: str = "U"
    international_designator: str = ""
    epoch_year: int = 0
    epoch_day: float = 0.0
    mean_motion_dot: float = 0.0
    mean_motion_ddot: float = 0.0
    bstar: float = 0.0
    element_set_number: int = 0
    
    # Line 2
    inclination_deg: float = 0.0
    raan_deg: float = 0.0
    eccentricity: float = 0.0
    arg_perigee_deg: float = 0.0
    mean_anomaly_deg: float = 0.0
    mean_motion_revs_day: float = 0.0
    rev_number: int = 0


class TLEParser:
    """Parse NORAD Two-Line Element sets."""
    
    @staticmethod
    def parse(tle_lines: list) -> TLEData:
        """
        Parse TLE from 2 or 3 lines.
        
        Args:
            tle_lines: List of strings (2 or 3 lines)
        
        Returns:
            Parsed TLEData
        """
        data = TLEData()
        
        if len(tle_lines) == 3:
            data.name = tle_lines[0].strip()
            line1 = tle_lines[1]
            line2 = tle_lines[2]
        else:
            line1 = tle_lines[0]
            line2 = tle_lines[1]
        
        # Parse Line 1
        data.satellite_number = int(line1[2:7].strip())
        data.classification = line1[7].strip()
        data.international_designator = line1[9:17].strip()
        
        epoch_year_short = int(line1[18:20])
        data.epoch_year = 2000 + epoch_year_short if epoch_year_short < 57 else 1900 + epoch_year_short
        data.epoch_day = float(line1[20:32])
        
        data.mean_motion_dot = float(line1[33:43])
        
        # Exponential notation for ddot
        ddot_str = line1[44:52].strip()
        if ddot_str:
            data.mean_motion_ddot = TLEParser._parse_exponential(ddot_str)
        
        bstar_str = line1[53:61].strip()
        if bstar_str:
            data.bstar = TLEParser._parse_exponential(bstar_str)
        
        data.element_set_number = int(line1[64:68].strip())
        
        # Parse Line 2
        data.inclination_deg = float(line2[8:16])
        data.raan_deg = float(line2[17:25])
        data.eccentricity = float("0." + line2[26:33].strip())
        data.arg_perigee_deg = float(line2[34:42])
        data.mean_anomaly_deg = float(line2[43:51])
        data.mean_motion_revs_day = float(line2[52:63])
        data.rev_number = int(line2[63:68].strip())
        
        return data
    
    @staticmethod
    def _parse_exponential(s: str) -> float:
        """Parse TLE exponential notation like +12345-5."""
        s = s.strip()
        if not s:
            return 0.0
        
        # Sign of mantissa
        sign = 1.0
        if s[0] == '-':
            sign = -1.0
            s = s[1:]
        elif s[0] == '+':
            s = s[1:]
        
        # Find exponent sign
        exp_pos = -1
        for i, c in enumerate(s):
            if c in '+-' and i > 0:
                exp_pos = i
                break
        
        if exp_pos == -1:
            return 0.0
        
        mantissa = float(s[:exp_pos]) / 1e5
        exponent = int(s[exp_pos:])
        
        return sign * mantissa * (10.0 ** exponent)


class SGP4Propagator:
    """
    Simplified SGP4 orbit propagator.
    
    Provides position/velocity from TLE for Earth-orbiting satellites.
    Uses simplified two-body + J2 model rather than full SGP4 for clarity.
    """
    
    MU_KM3_S2 = 398600.4418
    RE_KM = 6378.137
    J2 = 0.00108263
    
    def __init__(self, tle: TLEData):
        self.tle = tle
        self._init_orbit()
    
    def _init_orbit(self):
        """Initialize orbital parameters."""
        # Mean motion in rad/s
        self.n0 = self.tle.mean_motion_revs_day * 2.0 * math.pi / 86400.0
        
        # Semi-major axis
        self.a0 = (self.MU_KM3_S2 / (self.n0 ** 2)) ** (1.0 / 3.0)
        
        # Eccentricity
        self.e0 = self.tle.eccentricity
        
        # Inclination
        self.i0 = math.radians(self.tle.inclination_deg)
        
        # RAAN
        self.raan0 = math.radians(self.tle.raan_deg)
        
        # Argument of perigee
        self.omega0 = math.radians(self.tle.arg_perigee_deg)
        
        # Mean anomaly at epoch
        self.M0 = math.radians(self.tle.mean_anomaly_deg)
        
        # Epoch as day of year
        self.epoch_doy = self.tle.epoch_day
    
    def _solve_kepler(self, M: float, e: float, tol: float = 1e-10, max_iter: int = 50) -> float:
        """Solve Kepler's equation for eccentric anomaly."""
        E = M if e < 0.8 else math.pi
        for _ in range(max_iter):
            f = E - e * math.sin(E) - M
            fp = 1.0 - e * math.cos(E)
            dE = -f / fp
            E += dE
            if abs(dE) < tol:
                break
        return E
    
    def propagate(self, minutes_since_epoch: float) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Propagate orbit to time since epoch.
        
        Args:
            minutes_since_epoch: Minutes from TLE epoch
        
        Returns:
            (position_km, velocity_km_s)
        """
        dt_s = minutes_since_epoch * 60.0
        
        # J2 perturbation effects on mean motion and RAAN
        cos_i = math.cos(self.i0)
        sin_i = math.sin(self.i0)
        
        # Perturbed mean motion
        n = self.n0 * (1.0 + 1.5 * self.J2 * (self.RE_KM / self.a0) ** 2 * 
                       (1.0 - 1.5 * sin_i ** 2) * (1.0 - self.e0 ** 2) ** (-1.5))
        
        # RAAN drift rate
        draan_dt = -1.5 * self.J2 * (self.RE_KM / self.a0) ** 2 * n * cos_i * (1.0 - self.e0 ** 2) ** (-2.0)
        
        # Argument of perigee drift rate
        domega_dt = 0.75 * self.J2 * (self.RE_KM / self.a0) ** 2 * n * (4.0 - 5.0 * sin_i ** 2) * (1.0 - self.e0 ** 2) ** (-2.0)
        
        # Propagate elements
        M = self.M0 + n * dt_s
        raan = self.raan0 + draan_dt * dt_s
        omega = self.omega0 + domega_dt * dt_s
        
        # Wrap angles
        M = M % (2.0 * math.pi)
        raan = raan % (2.0 * math.pi)
        omega = omega % (2.0 * math.pi)
        
        # Solve Kepler's equation
        E = self._solve_kepler(M, self.e0)
        
        # True anomaly
        sin_E = math.sin(E)
        cos_E = math.cos(E)
        
        sqrt_1me2 = math.sqrt(1.0 - self.e0 ** 2)
        sin_nu = sqrt_1me2 * sin_E / (1.0 - self.e0 * cos_E)
        cos_nu = (cos_E - self.e0) / (1.0 - self.e0 * cos_E)
        nu = math.atan2(sin_nu, cos_nu)
        
        # Distance
        r = self.a0 * (1.0 - self.e0 * cos_E)
        
        # Position in orbital plane
        x_orb = r * cos_nu
        y_orb = r * sin_nu
        
        # Velocity in orbital plane
        p = self.a0 * (1.0 - self.e0 ** 2)
        h = math.sqrt(self.MU_KM3_S2 * p)
        
        vx_orb = -self.MU_KM3_S2 / h * sin_nu
        vy_orb = self.MU_KM3_S2 / h * (self.e0 + cos_nu)
        
        # Rotation to ECI
        cos_raan = math.cos(raan)
        sin_raan = math.sin(raan)
        cos_omega = math.cos(omega)
        sin_omega = math.sin(omega)
        cos_i = math.cos(self.i0)
        sin_i = math.sin(self.i0)
        
        # PQW to ECI rotation
        R11 = cos_raan * cos_omega - sin_raan * sin_omega * cos_i
        R12 = -cos_raan * sin_omega - sin_raan * cos_omega * cos_i
        R21 = sin_raan * cos_omega + cos_raan * sin_omega * cos_i
        R22 = -sin_raan * sin_omega + cos_raan * cos_omega * cos_i
        R31 = sin_omega * sin_i
        R32 = cos_omega * sin_i
        
        position = (
            R11 * x_orb + R12 * y_orb,
            R21 * x_orb + R22 * y_orb,
            R31 * x_orb + R32 * y_orb
        )
        
        velocity = (
            R11 * vx_orb + R12 * vy_orb,
            R21 * vx_orb + R22 * vy_orb,
            R31 * vx_orb + R32 * vy_orb
        )
        
        return position, velocity
    
    def get_orbital_period_min(self) -> float:
        """Get orbital period in minutes."""
        return 2.0 * math.pi / (self.n0 * 60.0)
    
    def get_altitude_km(self) -> float:
        """Get mean altitude."""
        return self.a0 * (1.0 - self.e0) - self.RE_KM


def create_sample_iss_tle() -> list:
    """Create a sample ISS TLE for testing."""
    return [
        "ISS (ZARYA)",
        "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927",
        "2 25544  51.6416 247.4627 0006703 130.5360 229.5775 15.72125391563537"
    ]
