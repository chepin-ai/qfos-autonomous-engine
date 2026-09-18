"""
Orbit Determination Module
Initial orbit determination from angular observations using Gaussian method.
"""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

try:
    from .orbital_mechanics import OrbitalBody, MU_SUN, AU
except ImportError:
    from orbital_mechanics import OrbitalBody, MU_SUN, AU


@dataclass
class Observation:
    """A ground-based angular observation (RA, Dec)."""
    timestamp: float  # Julian Date or days from epoch
    ra_deg: float     # Right ascension in degrees
    dec_deg: float    # Declination in degrees
    observer_pos_au: Tuple[float, float, float]  # Observer heliocentric position


class GaussOrbitDetermination:
    """
    Initial orbit determination using Gaussian method.
    Determines orbit from 3 observations.
    
    Reference: Bate, Mueller, White - Fundamentals of Astrodynamics
    """
    
    def __init__(self, mu: float = MU_SUN):
        self.mu = mu
    
    def _direction_cosines(self, ra_deg: float, dec_deg: float) -> Tuple[float, float, float]:
        """Convert RA/Dec to unit direction vector."""
        ra = math.radians(ra_deg)
        dec = math.radians(dec_deg)
        
        x = math.cos(dec) * math.cos(ra)
        y = math.cos(dec) * math.sin(ra)
        z = math.sin(dec)
        
        return x, y, z
    
    def determine_orbit(self, obs1: Observation, obs2: Observation, 
                        obs3: Observation) -> Optional[dict]:
        """
        Determine orbit from 3 observations using Gaussian method.
        
        Returns dict with orbital elements or None if indeterminate.
        """
        if len({obs1.timestamp, obs2.timestamp, obs3.timestamp}) < 3:
            return None
        
        # Time intervals (assuming small, in days -> seconds)
        tau1 = (obs1.timestamp - obs2.timestamp) * 86400.0  # t1 - t2
        tau3 = (obs3.timestamp - obs2.timestamp) * 86400.0  # t3 - t2
        tau = tau3 - tau1
        
        # Direction vectors
        L1 = self._direction_cosines(obs1.ra_deg, obs1.dec_deg)
        L2 = self._direction_cosines(obs2.ra_deg, obs2.dec_deg)
        L3 = self._direction_cosines(obs3.ra_deg, obs3.dec_deg)
        
        # Observer positions
        R1 = obs1.observer_pos_au
        R2 = obs2.observer_pos_au
        R3 = obs3.observer_pos_au
        
        # Cross products for Gaussian method
        p1 = self._cross(L2, L3)
        p2 = self._cross(L1, L3)
        p3 = self._cross(L1, L2)
        
        D0 = self._dot(L1, p1)
        
        if abs(D0) < 1e-15:
            return None  # Coplanar or indeterminate
        
        D = [
            [self._dot(R1, p1), self._dot(R1, p2), self._dot(R1, p3)],
            [self._dot(R2, p1), self._dot(R2, p2), self._dot(R2, p3)],
            [self._dot(R3, p1), self._dot(R3, p2), self._dot(R3, p3)],
        ]
        
        # First approximation (f and g series truncated)
        A = 1.0 / D0 * (-D[0][0] + D[1][0] * (tau3 / tau) - D[2][0] * (tau3 / tau1))
        B = 1.0 / (6.0 * D0) * (D[0][0] * (tau3**2 - tau**2) + D[1][0] * (tau**2 - tau1**2) + D[2][0] * (tau1**2 - tau3**2))
        
        E = self._dot(R2, L2)
        R2_sq = self._dot(R2, R2)
        
        # Solve for r2 (scalar distance to object at t2)
        # r2^8 - (A^2 + 2*A*E + R2_sq)*r2^6 - 2*mu*B*(A + E)*r2^3 - mu^2 * B^2 = 0
        # Simplified: iterate
        
        a = -(A**2 + 2*A*E + R2_sq)
        b = -2 * self.mu * B * (A + E)
        c = -(self.mu * B)**2
        
        # Initial guess
        r2 = math.sqrt(R2_sq) + 0.5  # Slightly beyond observer
        
        # Newton-Raphson iteration
        for _ in range(50):
            r2_sq = r2**2
            r2_cu = r2**3
            f = r2**8 + a * r2**6 + b * r2_cu + c
            fp = 8 * r2**7 + 6 * a * r2**5 + 3 * b * r2_sq
            
            if abs(fp) < 1e-15:
                break
            
            r2_new = r2 - f / fp
            if abs(r2_new - r2) < 1e-10:
                r2 = r2_new
                break
            r2 = r2_new
        
        if r2 <= 0 or r2 > 100 * AU:
            return None
        
        # Calculate slant ranges
        rho1 = 1.0 / D0 * ((6.0 * (D[2][0] * tau1 / tau3 + D[1][0] * tau / tau3) * r2**3 + self.mu * D[2][0] * (tau**2 - tau1**2) * tau1 / tau3) / (6.0 * r2**3 + self.mu * (tau**2 - tau3**2)) - D[0][0])
        rho2 = A + self.mu * B / r2**3
        rho3 = 1.0 / D0 * ((6.0 * (D[0][0] * tau3 / tau1 - D[1][0] * tau / tau1) * r2**3 + self.mu * D[0][0] * (tau**2 - tau3**2) * tau3 / tau1) / (6.0 * r2**3 + self.mu * (tau**2 - tau1**2)) - D[2][0])
        
        # Position vectors
        r1_vec = (R1[0] + rho1 * L1[0], R1[1] + rho1 * L1[1], R1[2] + rho1 * L1[2])
        r2_vec = (R2[0] + rho2 * L2[0], R2[1] + rho2 * L2[1], R2[2] + rho2 * L2[2])
        r3_vec = (R3[0] + rho3 * L3[0], R3[1] + rho3 * L3[1], R3[2] + rho3 * L3[2])
        
        # Estimate velocity at t2 using Gibbs/Herrick formula
        c1 = tau3 / tau * (1.0 + self.mu / (6.0 * r2**3) * (tau**2 - tau3**2))
        c3 = -tau1 / tau * (1.0 + self.mu / (6.0 * r2**3) * (tau**2 - tau1**2))
        
        v2_vec = (
            (c1 * r1_vec[0] + c3 * r3_vec[0] - r2_vec[0]) / tau,
            (c1 * r1_vec[1] + c3 * r3_vec[1] - r2_vec[1]) / tau,
            (c1 * r1_vec[2] + c3 * r3_vec[2] - r2_vec[2]) / tau,
        )
        
        # Convert to orbital elements (simplified)
        r2_mag = math.sqrt(self._dot(r2_vec, r2_vec))
        v2_mag = math.sqrt(self._dot(v2_vec, v2_vec))
        
        # Specific angular momentum
        h_vec = self._cross(r2_vec, v2_vec)
        h_mag = math.sqrt(self._dot(h_vec, h_vec))
        
        # Semi-major axis from vis-viva
        a = 1.0 / (2.0 / r2_mag - v2_mag**2 / self.mu)
        
        # Eccentricity
        e_vec = (
            (v2_mag**2 / self.mu - 1.0 / r2_mag) * r2_vec[0] - (self._dot(r2_vec, v2_vec) / self.mu) * v2_vec[0],
            (v2_mag**2 / self.mu - 1.0 / r2_mag) * r2_vec[1] - (self._dot(r2_vec, v2_vec) / self.mu) * v2_vec[1],
            (v2_mag**2 / self.mu - 1.0 / r2_mag) * r2_vec[2] - (self._dot(r2_vec, v2_vec) / self.mu) * v2_vec[2],
        )
        e = math.sqrt(self._dot(e_vec, e_vec))
        
        # Inclination
        i = math.acos(h_vec[2] / h_mag)
        
        return {
            "semi_major_axis_m": a,
            "semi_major_axis_au": a / AU,
            "eccentricity": e,
            "inclination_deg": math.degrees(i),
            "position_m": r2_vec,
            "velocity_ms": v2_vec,
            "method": "gaussian",
            "iterations": 50
        }
    
    @staticmethod
    def _dot(a: Tuple, b: Tuple) -> float:
        return sum(x * y for x, y in zip(a, b))
    
    @staticmethod
    def _cross(a: Tuple, b: Tuple) -> Tuple:
        return (
            a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]
        )
