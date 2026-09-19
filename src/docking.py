"""
Autonomous Docking Module
Rendezvous and docking maneuver planning for spacecraft proximity operations.
"""

import math
from typing import Tuple, Optional, Dict
from dataclasses import dataclass

try:
    from .orbital_mechanics import MU_SUN, AU
except ImportError:
    from orbital_mechanics import MU_SUN, AU


# Earth gravitational parameter
MU_EARTH = 3.986004418e14  # m^3/s^2
EARTH_RADIUS_M = 6.371e6


@dataclass
class DockingState:
    """Relative state during proximity operations."""
    range_m: float          # Distance to target
    range_rate_ms: float    # Closing velocity
    relative_position_m: Tuple[float, float, float]
    relative_velocity_ms: Tuple[float, float, float]
    phase: str              # 'far', 'mid', 'close', 'contact'


class ClohessyWiltshire:
    """
    Clohessy-Wiltshire equations for relative orbital motion.
    
    Linearized relative dynamics near a circular reference orbit.
    """
    
    def __init__(self, mean_motion_rad_s: float):
        """
        Args:
            mean_motion_rad_s: Mean motion of reference orbit (rad/s)
        """
        self.n = mean_motion_rad_s
    
    @classmethod
    def from_altitude_km(cls, altitude_km: float) -> 'ClohessyWiltshire':
        """Create CW model from circular orbit altitude."""
        r = EARTH_RADIUS_M + altitude_km * 1000.0
        n = math.sqrt(MU_EARTH / r**3)
        return cls(n)
    
    def propagate(self, x0: float, y0: float, z0: float,
                  vx0: float, vy0: float, vz0: float,
                  dt_s: float) -> Tuple[float, float, float, float, float, float]:
        """
        Propagate relative state using CW equations.
        
        Args:
            x0, y0, z0: Initial relative position (radial, along-track, cross-track) in m
            vx0, vy0, vz0: Initial relative velocity in m/s
            dt_s: Time of flight in seconds
        
        Returns:
            (x, y, z, vx, vy, vz) at time dt_s
        """
        n = self.n
        nt = n * dt_s
        snt = math.sin(nt)
        cnt = math.cos(nt)
        
        # Radial (x) and along-track (y) are coupled
        x = (vx0 / n) * snt - (3*x0 + 2*vy0/n) * cnt + (4*x0 + 2*vy0/n)
        y = (6*x0 + 4*vy0/n) * snt + (2*vx0/n) * cnt - 6*n*x0*dt_s + (y0 - 2*vx0/n)
        z = z0 * cnt + (vz0 / n) * snt
        
        vx = vx0 * cnt + (3*n*x0 + 2*vy0) * snt
        vy = (6*n*x0 + 4*vy0) * cnt - 2*vx0 * snt - 3*n*x0
        vz = -z0 * n * snt + vz0 * cnt
        
        return x, y, z, vx, vy, vz
    
    def required_velocity(self, x0: float, y0: float, z0: float,
                          xf: float, yf: float, zf: float,
                          dt_s: float) -> Tuple[float, float, float]:
        """
        Calculate required initial velocity for desired final position.
        
        Two-impulse rendezvous: compute delta-v at t=0 and t=dt.
        
        Returns:
            (vx0, vy0, vz0) required initial relative velocity
        """
        n = self.n
        nt = n * dt_s
        snt = math.sin(nt)
        cnt = math.cos(nt)
        
        # Matrix elements for solving
        a11 = snt / n
        a12 = -(3*x0 + 2*vy0/n)  # Will be solved iteratively
        
        # For simplicity, use the standard two-impulse solution
        # Reference: Vallado, Fundamentals of Astrodynamics and Applications
        
        c = 4 * (1 - cnt) / (3 * nt * snt - 8 * (1 - cnt))
        
        vx0 = n * (c * (xf * nt - x0 * snt) + xf - x0 * cnt) / snt
        vy0 = n * (c * (x0 * (1 - cnt) - xf * (1 - cnt)) + xf * snt - 2 * x0 * snt + 3 * x0 * nt) / (3 * nt * snt - 8 * (1 - cnt))
        
        # Simplified: direct approach for radial transfer
        if abs(snt) > 0.001:
            vx0 = n * ((xf - x0*(4-3*cnt)) * snt - xf * snt) / (snt**2)
            # Use approximate solution
            vx0 = n * (xf * snt - x0 * (4*snt - 3*nt*cnt)) / (snt**2)
        else:
            vx0 = (xf - x0) / dt_s
        
        vy0 = -2 * n * x0  # Natural drift compensation
        vz0 = 0.0
        
        if abs(snt) > 0.001:
            vz0 = n * (zf - z0 * cnt) / snt
        else:
            vz0 = (zf - z0) / dt_s
        
        # Refine using simplified approach for far-field
        dx = xf - x0
        dy = yf - y0
        dz = zf - z0
        
        vx0 = dx / dt_s - 2 * n * dy
        vy0 = dy / dt_s + 2 * n * dx
        vz0 = dz / dt_s
        
        return vx0, vy0, vz0


class DockingPlanner:
    """
    Plan autonomous docking maneuvers.
    
    Supports V-bar (along-track) and R-bar (radial) approaches.
    """
    
    # Approach phases
    PHASES = {
        'far': {'range_m': 10000, 'max_rate_ms': 5.0},
        'mid': {'range_m': 1000, 'max_rate_ms': 2.0},
        'close': {'range_m': 100, 'max_rate_ms': 0.5},
        'final': {'range_m': 10, 'max_rate_ms': 0.1},
        'contact': {'range_m': 0, 'max_rate_ms': 0.02},
    }
    
    def __init__(self, approach_type: str = 'v_bar'):
        """
        Args:
            approach_type: 'v_bar' (along-track) or 'r_bar' (radial)
        """
        self.approach_type = approach_type
    
    def plan_approach(self, initial_range_m: float,
                      target_altitude_km: float = 400.0) -> Dict:
        """
        Plan multi-phase docking approach.
        
        Returns:
            Dict with phase-by-phase plan
        """
        cw = ClohessyWiltshire.from_altitude_km(target_altitude_km)
        n = cw.n
        
        plan = []
        current_range = initial_range_m
        
        for phase_name, phase_params in self.PHASES.items():
            if current_range <= phase_params['range_m']:
                continue
            
            target_range = phase_params['range_m']
            max_rate = phase_params['max_rate_ms']
            
            # Calculate required delta-v for this phase
            if self.approach_type == 'v_bar':
                # Along-track approach
                dy = current_range - target_range
                dt = dy / max_rate
                
                # Natural drift during approach
                drift_x = -2 * n * dy  # Cross-coupling from along-track motion
                
                phase = {
                    'phase': phase_name,
                    'initial_range_m': round(current_range, 1),
                    'target_range_m': target_range,
                    'duration_s': round(dt, 1),
                    'max_rate_ms': max_rate,
                    'delta_v_ms': round(abs(max_rate), 3),
                    'approach': 'v_bar'
                }
            else:
                # Radial approach
                dx = current_range - target_range
                dt = dx / max_rate
                
                phase = {
                    'phase': phase_name,
                    'initial_range_m': round(current_range, 1),
                    'target_range_m': target_range,
                    'duration_s': round(dt, 1),
                    'max_rate_ms': max_rate,
                    'delta_v_ms': round(abs(max_rate), 3),
                    'approach': 'r_bar'
                }
            
            plan.append(phase)
            current_range = target_range
            
            if phase_name == 'contact':
                break
        
        total_dv = sum(p['delta_v_ms'] for p in plan)
        total_time = sum(p['duration_s'] for p in plan)
        
        return {
            'phases': plan,
            'total_delta_v_ms': round(total_dv, 3),
            'total_time_s': round(total_time, 1),
            'approach_type': self.approach_type,
            'target_altitude_km': target_altitude_km
        }
    
    def approach_state(self, range_m: float) -> str:
        """Determine approach phase from current range."""
        for phase_name, params in self.PHASES.items():
            if range_m > params['range_m']:
                return phase_name
        return 'contact'
    
    def compute_approach_velocity(self, range_m: float,
                                   target_altitude_km: float = 400.0) -> float:
        """
        Compute desired approach velocity at given range.
        
        Uses linear transition between phase limits.
        """
        phase = self.approach_state(range_m)
        phase_params = self.PHASES.get(phase, self.PHASES['far'])
        return phase_params['max_rate_ms']


class CooperativeDocking:
    """
    Model cooperative docking where both spacecraft maneuver.
    """
    
    def __init__(self, chaser_mass_kg: float = 1000.0,
                 target_mass_kg: float = 5000.0):
        self.chaser_mass = chaser_mass_kg
        self.target_mass = target_mass_kg
    
    def optimal_mass_ratio(self) -> float:
        """
        Calculate optimal mass ratio for fuel-efficient cooperative docking.
        
        Heuristic: lighter spacecraft should do more maneuvering.
        """
        total_mass = self.chaser_mass + self.target_mass
        return self.chaser_mass / total_mass
    
    def allocate_delta_v(self, total_dv_ms: float) -> Tuple[float, float]:
        """
        Allocate delta-v between chaser and target.
        
        Returns:
            (chaser_dv_ms, target_dv_ms)
        """
        ratio = self.optimal_mass_ratio()
        # Chaser does more (inverse mass ratio)
        chaser_dv = total_dv_ms * (1.0 + ratio) / 2.0
        target_dv = total_dv_ms - chaser_dv
        return chaser_dv, target_dv
