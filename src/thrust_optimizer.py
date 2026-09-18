"""
Thrust Optimizer Module
Impulsive and low-thrust trajectory optimization.
"""

import math
from typing import List, Tuple, Dict
from dataclasses import dataclass

try:
    from .orbital_mechanics import MU_SUN, AU
except ImportError:
    from orbital_mechanics import MU_SUN, AU


@dataclass
class ThrustManeuver:
    """A single impulsive thrust maneuver."""
    time_days: float
    delta_v_ms: Tuple[float, float, float]  # Inertial frame components
    delta_v_magnitude_ms: float
    isp_seconds: float = 300.0  # Specific impulse
    propellant_kg: float = 0.0


class ImpulsiveThrustOptimizer:
    """
    Optimize sequences of impulsive burns for orbital transfers.
    Uses bi-elliptic and plane change approximations.
    """
    
    def __init__(self, spacecraft_mass_kg: float = 1000.0, isp_seconds: float = 300.0):
        self.m0 = spacecraft_mass_kg
        self.isp = isp_seconds
        self.g0 = 9.80665  # Standard gravity (m/s^2)
    
    def _propellant_mass(self, dv_ms: float, m_initial_kg: float) -> float:
        """Calculate propellant mass for a given delta-v using Tsiolkovsky."""
        if dv_ms <= 0:
            return 0.0
        ve = self.isp * self.g0
        m_final = m_initial_kg * math.exp(-dv_ms / ve)
        return m_initial_kg - m_final
    
    def optimize_plane_change(self, v_ms: float, delta_i_deg: float,
                              optimize: bool = True) -> Dict:
        """
        Optimize plane change maneuver.
        
        If optimize=True, use combined burn (partial at apogee).
        If optimize=False, use pure plane change.
        
        Returns dict with strategy and delta-v breakdown.
        """
        delta_i = math.radians(delta_i_deg)
        
        if not optimize or delta_i_deg < 5.0:
            # Simple plane change at current velocity
            dv = 2 * v_ms * math.sin(delta_i / 2)
            return {
                "strategy": "simple_plane_change",
                "total_dv_ms": dv,
                "plane_change_dv_ms": dv,
                "propellant_kg": self._propellant_mass(dv, self.m0)
            }
        
        # Bi-elliptic approximation for large plane changes
        # Raise to high apogee, do plane change there, lower
        # Simplified: assume circular orbit, use 2-burn approximation
        
        r1 = 1.0 * AU  # Assume 1 AU
        r2 = 5.0 * AU  # High intermediate orbit
        
        v1 = math.sqrt(MU_SUN / r1)
        
        # Burn 1: raise to high orbit
        a_t1 = (r1 + r2) / 2.0
        vt1 = math.sqrt(MU_SUN * (2.0 / r1 - 1.0 / a_t1))
        dv1 = abs(vt1 - v1)
        
        # Burn 2: plane change at high apogee (lower velocity)
        v_ap = math.sqrt(MU_SUN * (2.0 / r2 - 1.0 / a_t1))
        dv2 = 2 * v_ap * math.sin(delta_i / 2)
        
        # Burn 3: lower back
        a_t2 = (r1 + r2) / 2.0
        vt2 = math.sqrt(MU_SUN * (2.0 / r1 - 1.0 / a_t2))
        dv3 = abs(v1 - vt2)
        
        total = dv1 + dv2 + dv3
        simple = 2 * v1 * math.sin(delta_i / 2)
        
        # Choose cheaper option
        if total < simple:
            return {
                "strategy": "bi_elliptic_plane_change",
                "total_dv_ms": total,
                "raise_dv_ms": dv1,
                "plane_change_dv_ms": dv2,
                "lower_dv_ms": dv3,
                "propellant_kg": self._propellant_mass(total, self.m0),
                "savings_vs_simple_ms": simple - total
            }
        else:
            return {
                "strategy": "simple_plane_change",
                "total_dv_ms": simple,
                "plane_change_dv_ms": simple,
                "propellant_kg": self._propellant_mass(simple, self.m0)
            }
    
    def optimize_transfer_sequence(self, burns: List[Tuple[float, float]]) -> List[ThrustManeuver]:
        """
        Optimize a sequence of burns accounting for mass change.
        
        Args:
            burns: List of (time_days, delta_v_magnitude_ms)
        
        Returns:
            List of ThrustManeuver with calculated propellant masses.
        """
        maneuvers = []
        m_current = self.m0
        
        for time_days, dv_mag in burns:
            mp = self._propellant_mass(dv_mag, m_current)
            
            maneuver = ThrustManeuver(
                time_days=time_days,
                delta_v_ms=(dv_mag, 0.0, 0.0),  # Simplified: all in x-direction
                delta_v_magnitude_ms=dv_mag,
                isp_seconds=self.isp,
                propellant_kg=mp
            )
            maneuvers.append(maneuver)
            m_current -= mp
        
        return maneuvers
    
    def low_thrust_spiral_time(self, r1_au: float, r2_au: float,
                               thrust_n: float, mass_kg: float) -> float:
        """
        Estimate spiral transfer time for low-thrust electric propulsion.
        
        Uses Edelbaum approximation for continuous thrust.
        
        Args:
            r1_au: Initial orbit radius (AU)
            r2_au: Final orbit radius (AU)
            thrust_n: Thrust in Newtons
            mass_kg: Spacecraft mass (kg)
        
        Returns:
            Transfer time in days
        """
        r1 = r1_au * AU
        r2 = r2_au * AU
        
        # Characteristic acceleration
        a0 = thrust_n / mass_kg
        
        # Circular orbit velocity
        v1 = math.sqrt(MU_SUN / r1)
        v2 = math.sqrt(MU_SUN / r2)
        
        # Edelbaum approximation for coplanar spiral
        # Time = (v2 - v1) / a0 (for small accelerations)
        delta_v = abs(v2 - v1)
        time_seconds = delta_v / a0
        
        return time_seconds / 86400.0


class LowThrustOptimizer:
    """
    Direct optimization of low-thrust trajectories using shape-based methods.
    """
    
    def __init__(self, mu: float = MU_SUN):
        self.mu = mu
    
    def exponential_sinusoid_trajectory(self, r1_au: float, r2_au: float,
                                        revolutions: int = 1,
                                        kappa: float = 0.5) -> Dict:
        """
        Generate exponential sinusoid trajectory (Petropoulos method).
        
        Returns trajectory parameters and thrust profile.
        """
        r1 = r1_au * AU
        r2 = r2_au * AU
        
        # Logarithmic spiral parameter
        theta_total = 2 * math.pi * revolutions + math.log(r2 / r1) / math.tan(math.radians(30))
        
        # Angular rate (constant for logarithmic spiral)
        # Simplified: assume constant tangential thrust
        
        # Acceleration profile
        a_tan = self.mu / r1**2  # Initial gravitational acceleration
        
        return {
            "trajectory_type": "exponential_sinusoid",
            "revolutions": revolutions,
            "total_angle_deg": math.degrees(theta_total),
            "initial_acceleration_ms2": a_tan,
            "notes": "Shape-based approximation; full optimization requires numerical integration"
        }
