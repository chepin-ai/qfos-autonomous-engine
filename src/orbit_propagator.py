"""
Orbit Propagator Module
Keplerian elements, SGP4-style propagation, and state
vector integration for orbital mechanics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class KeplerianElements:
    """Classical orbital elements."""
    semi_major_axis: float  # km
    eccentricity: float
    inclination: float  # rad
    raan: float  # rad, right ascension of ascending node
    arg_perigee: float  # rad, argument of perigee
    true_anomaly: float  # rad
    
    def period(self, mu: float = 398600.4418) -> float:
        """Orbital period (seconds)."""
        return 2 * math.pi * math.sqrt(self.semi_major_axis**3 / mu)
    
    def mean_motion(self, mu: float = 398600.4418) -> float:
        """Mean motion (rad/s)."""
        return math.sqrt(mu / self.semi_major_axis**3)


@dataclass
class StateVector:
    """Cartesian state vector."""
    position: Tuple[float, float, float]  # km
    velocity: Tuple[float, float, float]  # km/s
    timestamp: float = 0.0  # seconds from epoch


class KeplerPropagator:
    """
    Propagate orbits using Keplerian elements.
    """
    
    def __init__(self, mu: float = 398600.4418):
        """
        Args:
            mu: Standard gravitational parameter (km^3/s^2)
        """
        self.mu = mu
    
    def _solve_kepler(self, M: float, e: float, tol: float = 1e-10) -> float:
        """
        Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E.
        
        Args:
            M: Mean anomaly (rad)
            e: Eccentricity
            tol: Tolerance
        
        Returns:
            Eccentric anomaly (rad)
        """
        E = M if e < 0.8 else math.pi
        for _ in range(50):
            f = E - e * math.sin(E) - M
            df = 1 - e * math.cos(E)
            if abs(df) < 1e-15:
                break
            dE = -f / df
            E = E + dE
            if abs(dE) < tol:
                break
        return E
    
    def _true_to_eccentric(self, nu: float, e: float) -> float:
        """Convert true anomaly to eccentric anomaly."""
        cos_E = (e + math.cos(nu)) / (1 + e * math.cos(nu))
        cos_E = max(-1.0, min(1.0, cos_E))
        E = math.acos(cos_E)
        if math.sin(nu) < 0:
            E = 2 * math.pi - E
        return E
    
    def _eccentric_to_true(self, E: float, e: float) -> float:
        """Convert eccentric anomaly to true anomaly."""
        cos_nu = (math.cos(E) - e) / (1 - e * math.cos(E))
        cos_nu = max(-1.0, min(1.0, cos_nu))
        nu = math.acos(cos_nu)
        if math.sin(E) < 0:
            nu = 2 * math.pi - nu
        return nu
    
    def propagate(self, elements: KeplerianElements,
                 dt: float) -> KeplerianElements:
        """
        Propagate orbit by time delta.
        
        Args:
            elements: Initial elements
            dt: Time delta (seconds)
        
        Returns:
            Propagated elements
        """
        n = elements.mean_motion(self.mu)
        
        # Current eccentric anomaly
        E0 = self._true_to_eccentric(elements.true_anomaly, elements.eccentricity)
        
        # Mean anomaly at epoch
        M0 = E0 - elements.eccentricity * math.sin(E0)
        
        # Propagate mean anomaly
        M = M0 + n * dt
        M = M % (2 * math.pi)
        
        # Solve for new eccentric anomaly
        E = self._solve_kepler(M, elements.eccentricity)
        
        # Convert back to true anomaly
        nu = self._eccentric_to_true(E, elements.eccentricity)
        
        return KeplerianElements(
            semi_major_axis=elements.semi_major_axis,
            eccentricity=elements.eccentricity,
            inclination=elements.inclination,
            raan=elements.raan,
            arg_perigee=elements.arg_perigee,
            true_anomaly=nu
        )
    
    def elements_to_state(self, elements: KeplerianElements) -> StateVector:
        """
        Convert Keplerian elements to Cartesian state vector.
        
        Args:
            elements: Orbital elements
        
        Returns:
            State vector
        """
        a = elements.semi_major_axis
        e = elements.eccentricity
        i = elements.inclination
        Omega = elements.raan
        omega = elements.arg_perigee
        nu = elements.true_anomaly
        
        # Distance from focus
        r = a * (1 - e**2) / (1 + e * math.cos(nu))
        
        # Position in orbital plane
        x_orb = r * math.cos(nu)
        y_orb = r * math.sin(nu)
        
        # Velocity in orbital plane (vis-viva)
        h = math.sqrt(self.mu * a * (1 - e**2))
        vx_orb = -self.mu / h * math.sin(nu)
        vy_orb = self.mu / h * (e + math.cos(nu))
        
        # Rotation matrix from orbital to inertial frame
        cos_O = math.cos(Omega)
        sin_O = math.sin(Omega)
        cos_w = math.cos(omega)
        sin_w = math.sin(omega)
        cos_i = math.cos(i)
        sin_i = math.sin(i)
        
        # Position
        x = (cos_O * cos_w - sin_O * sin_w * cos_i) * x_orb + \
            (-cos_O * sin_w - sin_O * cos_w * cos_i) * y_orb
        y = (sin_O * cos_w + cos_O * sin_w * cos_i) * x_orb + \
            (-sin_O * sin_w + cos_O * cos_w * cos_i) * y_orb
        z = (sin_w * sin_i) * x_orb + (cos_w * sin_i) * y_orb
        
        # Velocity
        vx = (cos_O * cos_w - sin_O * sin_w * cos_i) * vx_orb + \
             (-cos_O * sin_w - sin_O * cos_w * cos_i) * vy_orb
        vy = (sin_O * cos_w + cos_O * sin_w * cos_i) * vx_orb + \
             (-sin_O * sin_w + cos_O * cos_w * cos_i) * vy_orb
        vz = (sin_w * sin_i) * vx_orb + (cos_w * sin_i) * vy_orb
        
        return StateVector(position=(x, y, z), velocity=(vx, vy, vz))
    
    def state_to_elements(self, state: StateVector,
                         mu: Optional[float] = None) -> KeplerianElements:
        """
        Convert Cartesian state vector to Keplerian elements.
        
        Args:
            state: State vector
            mu: Gravitational parameter
        
        Returns:
            Keplerian elements
        """
        mu = mu or self.mu
        r_vec = state.position
        v_vec = state.velocity
        
        r = math.sqrt(sum(c**2 for c in r_vec))
        v = math.sqrt(sum(c**2 for c in v_vec))
        
        # Specific angular momentum
        h_vec = (
            r_vec[1] * v_vec[2] - r_vec[2] * v_vec[1],
            r_vec[2] * v_vec[0] - r_vec[0] * v_vec[2],
            r_vec[0] * v_vec[1] - r_vec[1] * v_vec[0]
        )
        h = math.sqrt(sum(c**2 for c in h_vec))
        
        # Node vector
        n_vec = (-h_vec[1], h_vec[0], 0.0)
        n = math.sqrt(n_vec[0]**2 + n_vec[1]**2)
        
        # Eccentricity vector
        e_vec = (
            (v**2 - mu/r) * r_vec[0] / mu - (r_vec[0]*v_vec[0] + r_vec[1]*v_vec[1] + r_vec[2]*v_vec[2]) * v_vec[0] / mu,
            (v**2 - mu/r) * r_vec[1] / mu - (r_vec[0]*v_vec[0] + r_vec[1]*v_vec[1] + r_vec[2]*v_vec[2]) * v_vec[1] / mu,
            (v**2 - mu/r) * r_vec[2] / mu - (r_vec[0]*v_vec[0] + r_vec[1]*v_vec[1] + r_vec[2]*v_vec[2]) * v_vec[2] / mu,
        )
        e = math.sqrt(sum(c**2 for c in e_vec))
        e = min(e, 0.9999)  # Clamp to avoid parabolic
        
        # Specific energy
        energy = v**2 / 2 - mu / r
        
        # Semi-major axis
        if abs(e - 1.0) < 1e-10:
            a = h**2 / (2 * mu)  # Parabolic approximation
        else:
            a = -mu / (2 * energy)
        
        # Inclination
        i = math.acos(max(-1.0, min(1.0, h_vec[2] / h)))
        
        # RAAN
        if n < 1e-10:
            Omega = 0.0
        else:
            Omega = math.acos(max(-1.0, min(1.0, n_vec[0] / n)))
            if n_vec[1] < 0:
                Omega = 2 * math.pi - Omega
        
        # Argument of perigee
        if n < 1e-10:
            omega = 0.0
        elif e < 1e-10:
            omega = 0.0
        else:
            omega = math.acos(max(-1.0, min(1.0, (n_vec[0]*e_vec[0] + n_vec[1]*e_vec[1]) / (n * e))))
            if e_vec[2] < 0:
                omega = 2 * math.pi - omega
        
        # True anomaly
        if e < 1e-10:
            nu = 0.0
        else:
            nu = math.acos(max(-1.0, min(1.0, (e_vec[0]*r_vec[0] + e_vec[1]*r_vec[1] + e_vec[2]*r_vec[2]) / (e * r))))
            if (r_vec[0]*v_vec[0] + r_vec[1]*v_vec[1] + r_vec[2]*v_vec[2]) < 0:
                nu = 2 * math.pi - nu
        
        return KeplerianElements(
            semi_major_axis=a,
            eccentricity=e,
            inclination=i,
            raan=Omega,
            arg_perigee=omega,
            true_anomaly=nu
        )


class SGP4Propagator:
    """
    Simplified SGP4-style propagator for near-Earth orbits.
    
    Simplified implementation for demonstration.
    """
    
    def __init__(self, mu: float = 398600.4418,
                 j2: float = 1.08263e-3,
                 re: float = 6378.137):
        """
        Args:
            mu: Gravitational parameter
            j2: Earth's oblateness coefficient
            re: Earth equatorial radius (km)
        """
        self.mu = mu
        self.j2 = j2
        self.re = re
    
    def propagate_with_j2(self, elements: KeplerianElements,
                          dt: float) -> KeplerianElements:
        """
        Propagate orbit with J2 perturbation.
        
        Args:
            elements: Initial elements
            dt: Time delta (seconds)
        
        Returns:
            Propagated elements
        """
        a = elements.semi_major_axis
        e = elements.eccentricity
        i = elements.inclination
        
        n = math.sqrt(self.mu / a**3)
        
        # J2 perturbation rates
        p = a * (1 - e**2)
        raan_dot = -1.5 * n * self.j2 * (self.re / p)**2 * math.cos(i)
        omega_dot = 0.75 * n * self.j2 * (self.re / p)**2 * (4 - 5 * math.sin(i)**2)
        
        # Propagate
        prop = KeplerPropagator(self.mu).propagate(elements, dt)
        
        # Apply J2 secular perturbations
        return KeplerianElements(
            semi_major_axis=prop.semi_major_axis,
            eccentricity=prop.eccentricity,
            inclination=prop.inclination,
            raan=prop.raan + raan_dot * dt,
            arg_perigee=prop.arg_perigee + omega_dot * dt,
            true_anomaly=prop.true_anomaly
        )


class OrbitPropagator:
    """
    Unified orbit propagation controller.
    """
    
    def __init__(self):
        self.kepler = KeplerPropagator()
        self.sgp4 = SGP4Propagator()
    
    def propagate(self, elements: KeplerianElements,
                 dt: float, use_j2: bool = False) -> KeplerianElements:
        """
        Propagate orbit.
        
        Args:
            elements: Initial elements
            dt: Time delta (seconds)
            use_j2: Whether to include J2 perturbation
        
        Returns:
            Propagated elements
        """
        if use_j2:
            return self.sgp4.propagate_with_j2(elements, dt)
        return self.kepler.propagate(elements, dt)
    
    def to_state(self, elements: KeplerianElements) -> StateVector:
        """Convert elements to state vector."""
        return self.kepler.elements_to_state(elements)
    
    def from_state(self, state: StateVector) -> KeplerianElements:
        """Convert state vector to elements."""
        return self.kepler.state_to_elements(state)
    
    def generate_ephemeris(self, elements: KeplerianElements,
                          start: float, end: float,
                          step: float) -> List[StateVector]:
        """
        Generate ephemeris table.
        
        Args:
            elements: Initial elements
            start: Start time (seconds)
            end: End time (seconds)
            step: Time step (seconds)
        
        Returns:
            List of state vectors
        """
        states = []
        t = start
        while t <= end:
            prop = self.propagate(elements, t)
            state = self.to_state(prop)
            state.timestamp = t
            states.append(state)
            t += step
        return states
    
    def propagator_summary(self) -> Dict:
        """Get propagator summary."""
        return {
            "propagator_type": "Kepler + SGP4(J2)",
            "mu": self.kepler.mu,
            "j2": self.sgp4.j2
        }
