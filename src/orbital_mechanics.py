"""
Orbital Mechanics Module
Core orbital calculations using real NASA/JPL SBDB data.
"""

import math
from typing import Dict, List, Tuple, Optional

# Physical constants
MU_SUN = 1.32712440018e20  # m^3/s^2
AU = 1.495978707e11  # meters
EARTH_VELOCITY = 29780  # m/s


class OrbitalBody:
    """Represents a celestial body with orbital elements."""
    
    def __init__(self, name: str, spkid: str, a_au: float, e: float, 
                 i_deg: float, omega_deg: float = 0.0, 
                 Omega_deg: float = 0.0, epoch: str = None):
        self.name = name
        self.spkid = spkid
        self.a = a_au * AU  # semi-major axis in meters
        self.e = e
        self.i = math.radians(i_deg)
        self.omega = math.radians(omega_deg)
        self.Omega = math.radians(Omega_deg)
        self.epoch = epoch
    
    @property
    def semi_major_axis_au(self) -> float:
        return self.a / AU
    
    @property
    def inclination_deg(self) -> float:
        return math.degrees(self.i)
    
    @property
    def period_years(self) -> float:
        """Orbital period using Kepler's 3rd law."""
        return math.sqrt((self.a / AU) ** 3)
    
    @property
    def perihelion_m(self) -> float:
        return self.a * (1 - self.e)
    
    @property
    def aphelion_m(self) -> float:
        return self.a * (1 + self.e)
    
    def orbital_velocity_at(self, r_m: float) -> float:
        """Vis-viva equation: velocity at distance r from central body."""
        return math.sqrt(MU_SUN * (2 / r_m - 1 / self.a))
    
    def velocity_at_perihelion(self) -> float:
        return self.orbital_velocity_at(self.perihelion_m)
    
    def velocity_at_aphelion(self) -> float:
        return self.orbital_velocity_at(self.aphelion_m)
    
    def solve_kepler(self, M: float, tol: float = 1e-10) -> float:
        """Newton-Raphson solution to Kepler's equation: M = E - e*sin(E)."""
        E = M if self.e < 0.8 else math.pi
        for _ in range(50):
            f = E - self.e * math.sin(E) - M
            fp = 1 - self.e * math.cos(E)
            dE = -f / fp
            E += dE
            if abs(dE) < tol:
                break
        return E
    
    def position_at_time(self, t_days: float) -> Tuple[float, float, float]:
        """Propagate orbit to t_days after epoch. Returns (x,y,z) in AU."""
        n = math.sqrt(MU_SUN / self.a ** 3)  # mean motion rad/s
        M = n * t_days * 86400
        M = M % (2 * math.pi)
        
        E = self.solve_kepler(M)
        
        # True anomaly
        nu = 2 * math.atan2(
            math.sqrt(1 + self.e) * math.sin(E / 2),
            math.sqrt(1 - self.e) * math.cos(E / 2)
        )
        r = self.a * (1 - self.e * math.cos(E))
        
        # Orbital plane coordinates
        x_orb = r * math.cos(nu)
        y_orb = r * math.sin(nu)
        
        # Rotation to inertial frame
        cosO, sinO = math.cos(self.Omega), math.sin(self.Omega)
        cosw, sinw = math.cos(self.omega), math.sin(self.omega)
        cosi, sini = math.cos(self.i), math.sin(self.i)
        
        x = (cosO * cosw - sinO * sinw * cosi) * x_orb + (-cosO * sinw - sinO * cosw * cosi) * y_orb
        y = (sinO * cosw + cosO * sinw * cosi) * x_orb + (-sinO * sinw + cosO * cosw * cosi) * y_orb
        z = (sinw * sini) * x_orb + (cosw * sini) * y_orb
        
        return x / AU, y / AU, z / AU


def hohmann_transfer_delta_v(a1_au: float, a2_au: float) -> float:
    """Total delta-v for Hohmann transfer between circular orbits (km/s)."""
    r1 = a1_au * AU
    r2 = a2_au * AU
    a_t = (r1 + r2) / 2.0
    
    v1 = math.sqrt(MU_SUN / r1)
    v2 = math.sqrt(MU_SUN / r2)
    vt1 = math.sqrt(MU_SUN * (2.0 / r1 - 1.0 / a_t))
    vt2 = math.sqrt(MU_SUN * (2.0 / r2 - 1.0 / a_t))
    
    dv1 = abs(vt1 - v1)
    dv2 = abs(v2 - vt2)
    return (dv1 + dv2) / 1000.0


def estimate_moid(body1: OrbitalBody, body2: OrbitalBody) -> float:
    """Estimate Minimum Orbit Intersection Distance in AU."""
    q1 = body1.semi_major_axis_au * (1 - body1.e)
    Q1 = body1.semi_major_axis_au * (1 + body1.e)
    q2 = body2.semi_major_axis_au * (1 - body2.e)
    Q2 = body2.semi_major_axis_au * (1 + body2.e)
    
    # If orbits don't intersect
    if Q1 < q2 or Q2 < q1:
        return max(abs(q1 - Q2), abs(q2 - Q1))
    
    # Estimate based on inclination difference
    di = abs(body1.inclination_deg - body2.inclination_deg)
    return max(0.001, min(body1.semi_major_axis_au, body2.semi_major_axis_au) * 
               math.sin(math.radians(di)))
