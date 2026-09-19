"""
Guidance Navigation Module
Lambert solver, intercept guidance, and delta-v budgeting
for orbital rendezvous and interplanetary transfer.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class OrbitalState:
    """Orbital state vector."""
    position: Tuple[float, float, float]  # km
    velocity: Tuple[float, float, float]  # km/s
    time: float = 0.0  # seconds from epoch


@dataclass
class TransferSolution:
    """Lambert transfer solution."""
    delta_v1: Tuple[float, float, float]  # km/s
    delta_v2: Tuple[float, float, float]  # km/s
    total_delta_v: float  # km/s
    time_of_flight: float  # seconds
    is_valid: bool = True


@dataclass
class InterceptPlan:
    """Intercept guidance plan."""
    target_id: str
    intercept_time: float
    required_delta_v: float
    phases: List[str] = field(default_factory=list)


class LambertSolver:
    """
    Lambert's problem solver for orbital transfer.
    
    Given two position vectors and time of flight, find
    the velocity vectors at both positions.
    """
    
    def __init__(self, mu: float = 398600.4418):
        """
        Args:
            mu: Standard gravitational parameter (km^3/s^2), Earth default
        """
        self.mu = mu
    
    def _dot(self, a: Tuple[float, float, float],
             b: Tuple[float, float, float]) -> float:
        """Vector dot product."""
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    
    def _cross(self, a: Tuple[float, float, float],
               b: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Vector cross product."""
        return (a[1]*b[2] - a[2]*b[1],
                a[2]*b[0] - a[0]*b[2],
                a[0]*b[1] - a[1]*b[0])
    
    def _norm(self, a: Tuple[float, float, float]) -> float:
        """Vector magnitude."""
        return math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
    
    def _sub(self, a: Tuple[float, float, float],
             b: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Vector subtraction."""
        return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    
    def _add(self, a: Tuple[float, float, float],
             b: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Vector addition."""
        return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
    
    def _scale(self, a: Tuple[float, float, float], s: float) -> Tuple[float, float, float]:
        """Vector scaling."""
        return (a[0]*s, a[1]*s, a[2]*s)
    
    def solve(self, r1: Tuple[float, float, float],
              r2: Tuple[float, float, float],
              tof: float,
              prograde: bool = True) -> Optional[TransferSolution]:
        """
        Solve Lambert's problem.
        
        Args:
            r1: Initial position (km)
            r2: Final position (km)
            tof: Time of flight (seconds)
            prograde: True for prograde transfer
        
        Returns:
            Transfer solution or None
        """
        r1_norm = self._norm(r1)
        r2_norm = self._norm(r2)
        
        if r1_norm == 0 or r2_norm == 0 or tof <= 0:
            return None
        
        # Transfer angle
        cos_dnu = self._dot(r1, r2) / (r1_norm * r2_norm)
        cos_dnu = max(-1.0, min(1.0, cos_dnu))
        
        # Determine transfer direction
        cross_r1r2 = self._cross(r1, r2)
        
        if prograde:
            if cross_r1r2[2] >= 0:
                dnu = math.acos(cos_dnu)
            else:
                dnu = 2 * math.pi - math.acos(cos_dnu)
        else:
            if cross_r1r2[2] >= 0:
                dnu = 2 * math.pi - math.acos(cos_dnu)
            else:
                dnu = math.acos(cos_dnu)
        
        # Chord length
        c = self._norm(self._sub(r2, r1))
        s = (r1_norm + r2_norm + c) / 2
        
        # Minimum energy semi-major axis
        a_min = s / 2
        
        # Initial guess for semi-major axis
        # Use approximate method
        tof_min = (math.sqrt(2) / 3) * (s**1.5 - (s - c)**1.5) / math.sqrt(self.mu)
        
        if tof < tof_min * 0.99:
            return TransferSolution(
                delta_v1=(0, 0, 0), delta_v2=(0, 0, 0),
                total_delta_v=0, time_of_flight=tof, is_valid=False
            )
        
        # Iterative solution using universal variable formulation
        # Simplified: use approximate solution
        a = self._solve_for_a(r1_norm, r2_norm, c, dnu, tof)
        
        if a is None or a <= 0:
            return TransferSolution(
                delta_v1=(0, 0, 0), delta_v2=(0, 0, 0),
                total_delta_v=0, time_of_flight=tof, is_valid=False
            )
        
        # Compute velocity vectors using f and g functions
        f = 1 - r2_norm / a * (1 - math.cos(dnu))
        g = r1_norm * r2_norm * math.sin(dnu) / math.sqrt(self.mu * a)
        
        # f_dot = -sqrt(mu*a) / (r1*r2) * sin(dnu)
        # g_dot = 1 - r1/a * (1 - cos(dnu))
        
        # Velocity at r1
        g_inv = 1.0 / g if g != 0 else 0
        v1 = self._scale(self._sub(r2, self._scale(r1, f)), g_inv)
        
        # Velocity at r2
        g_dot = 1 - r1_norm / a * (1 - math.cos(dnu))
        v2 = self._scale(self._sub(self._scale(r2, g_dot), r1), g_inv)
        
        # Delta-v (assuming initial and final circular orbits)
        # For simplicity, return the departure and arrival velocities
        delta_v1 = v1
        delta_v2 = v2
        
        total = self._norm(delta_v1) + self._norm(delta_v2)
        
        return TransferSolution(
            delta_v1=delta_v1,
            delta_v2=delta_v2,
            total_delta_v=total,
            time_of_flight=tof,
            is_valid=True
        )
    
    def _solve_for_a(self, r1: float, r2: float, c: float,
                     dnu: float, tof: float) -> Optional[float]:
        """Iteratively solve for semi-major axis using bisection."""
        s = (r1 + r2 + c) / 2
        a_min = s / 2 * 1.001
        
        def compute_tof(a_val):
            a_val = max(a_val, a_min)
            ratio_s = min(0.9999, s / (2 * a_val))
            ratio_sc = min(0.9999, (s - c) / (2 * a_val)) if s > c else 0.0
            
            alpha = 2 * math.asin(math.sqrt(ratio_s))
            beta = 2 * math.asin(math.sqrt(ratio_sc))
            
            if dnu > math.pi:
                beta = -beta
            
            return (a_val**1.5 / math.sqrt(self.mu)) * (
                alpha - math.sin(alpha) - (beta - math.sin(beta))
            )
        
        # Bisection search
        a_low = a_min
        a_high = max(a_min * 100, s * 10)
        
        tof_low = compute_tof(a_low)
        tof_high = compute_tof(a_high)
        
        # Check if TOF is in range
        if tof < min(tof_low, tof_high) or tof > max(tof_low, tof_high):
            # Try expanding range
            a_high *= 10
            tof_high = compute_tof(a_high)
            if tof < min(tof_low, tof_high) or tof > max(tof_low, tof_high):
                return None
        
        for _ in range(100):
            a_mid = (a_low + a_high) / 2
            tof_mid = compute_tof(a_mid)
            
            if abs(tof_mid - tof) < 1e-3:
                return a_mid
            
            if (tof_mid - tof) * (tof_low - tof) < 0:
                a_high = a_mid
                tof_high = tof_mid
            else:
                a_low = a_mid
                tof_low = tof_mid
        
        a_final = (a_low + a_high) / 2
        return a_final if abs(compute_tof(a_final) - tof) < tof * 0.5 else None


class InterceptGuidance:
    """
    Proportional navigation intercept guidance.
    """
    
    def __init__(self, nav_constant: float = 3.0):
        """
        Args:
            nav_constant: Navigation constant (typically 3-5)
        """
        self.N = nav_constant
    
    def _sub(self, a: Tuple[float, float, float],
             b: Tuple[float, float, float]) -> Tuple[float, float, float]:
        return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    
    def _norm(self, a: Tuple[float, float, float]) -> float:
        return math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
    
    def _cross(self, a: Tuple[float, float, float],
               b: Tuple[float, float, float]) -> Tuple[float, float, float]:
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    
    def _scale(self, a: Tuple[float, float, float], s: float) -> Tuple[float, float, float]:
        return (a[0]*s, a[1]*s, a[2]*s)
    
    def _dot(self, a: Tuple[float, float, float],
             b: Tuple[float, float, float]) -> float:
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    
    def compute_acceleration(self, missile_pos: Tuple[float, float, float],
                            missile_vel: Tuple[float, float, float],
                            target_pos: Tuple[float, float, float],
                            target_vel: Tuple[float, float, float]
                            ) -> Tuple[float, float, float]:
        """
        Compute required lateral acceleration.
        
        Args:
            missile_pos: Missile position (km)
            missile_vel: Missile velocity (km/s)
            target_pos: Target position (km)
            target_vel: Target velocity (km/s)
        
        Returns:
            Required acceleration (km/s^2)
        """
        # Line of sight vector
        los = self._sub(target_pos, missile_pos)
        los_norm = self._norm(los)
        if los_norm == 0:
            return (0, 0, 0)
        
        los_unit = self._scale(los, 1.0 / los_norm)
        
        # Relative velocity
        v_rel = self._sub(target_vel, missile_vel)
        
        # Line of sight rate (cross product method)
        los_rate = self._cross(los, v_rel)
        los_rate = self._scale(los_rate, 1.0 / (los_norm * los_norm))
        
        # Closing velocity (projection of relative velocity onto LOS)
        v_rel_vec = self._sub(missile_vel, target_vel)
        v_c_mag = self._dot(v_rel_vec, los_unit)
        
        # Lateral acceleration: a = N * v_c * los_rate
        accel = self._scale(los_rate, self.N * abs(v_c_mag) * los_norm)
        
        return accel


class DeltaVBudget:
    """
    Delta-v budget calculator for mission planning.
    """
    
    def __init__(self):
        self.maneuvers: List[Dict] = []
    
    def add_maneuver(self, name: str, delta_v: float,
                    margin: float = 0.1):
        """
        Add maneuver to budget.
        
        Args:
            name: Maneuver name
            delta_v: Required delta-v (km/s)
            margin: Margin fraction (0.1 = 10%)
        """
        self.maneuvers.append({
            "name": name,
            "delta_v": delta_v,
            "margin": margin,
            "total": delta_v * (1 + margin)
        })
    
    def total_budget(self) -> float:
        """Compute total delta-v budget with margins."""
        return sum(m["total"] for m in self.maneuvers)
    
    def total_nominal(self) -> float:
        """Compute nominal delta-v without margins."""
        return sum(m["delta_v"] for m in self.maneuvers)
    
    def budget_breakdown(self) -> Dict:
        """Get detailed budget breakdown."""
        return {
            "maneuvers": self.maneuvers,
            "total_nominal": self.total_nominal(),
            "total_with_margin": self.total_budget(),
            "margin_amount": self.total_budget() - self.total_nominal()
        }
    
    def hohmann_transfer(self, r1: float, r2: float,
                        mu: float = 398600.4418) -> Dict:
        """
        Compute Hohmann transfer delta-v.
        
        Args:
            r1: Initial orbit radius (km)
            r2: Final orbit radius (km)
            mu: Gravitational parameter
        
        Returns:
            Delta-v breakdown
        """
        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)
        
        a_transfer = (r1 + r2) / 2
        v_transfer1 = math.sqrt(mu * (2/r1 - 1/a_transfer))
        v_transfer2 = math.sqrt(mu * (2/r2 - 1/a_transfer))
        
        dv1 = abs(v_transfer1 - v1)
        dv2 = abs(v2 - v_transfer2)
        
        tof = math.pi * math.sqrt(a_transfer**3 / mu)
        
        return {
            "delta_v1": dv1,
            "delta_v2": dv2,
            "total_delta_v": dv1 + dv2,
            "time_of_flight": tof
        }


class GuidanceNavigation:
    """
    Unified guidance and navigation controller.
    """
    
    def __init__(self):
        self.lambert = LambertSolver()
        self.intercept = InterceptGuidance()
        self.budget = DeltaVBudget()
    
    def plan_transfer(self, state1: OrbitalState,
                     state2: OrbitalState,
                     tof: float) -> Optional[TransferSolution]:
        """
        Plan orbital transfer.
        
        Args:
            state1: Initial state
            state2: Final state
            tof: Time of flight
        
        Returns:
            Transfer solution
        """
        return self.lambert.solve(state1.position, state2.position, tof)
    
    def compute_intercept(self, missile: OrbitalState,
                         target: OrbitalState) -> Tuple[float, float, float]:
        """
        Compute intercept acceleration.
        
        Args:
            missile: Missile state
            target: Target state
        
        Returns:
            Required acceleration
        """
        return self.intercept.compute_acceleration(
            missile.position, missile.velocity,
            target.position, target.velocity
        )
    
    def gn_summary(self) -> Dict:
        """Get guidance summary."""
        return {
            "maneuvers_planned": len(self.budget.maneuvers),
            "total_delta_v": self.budget.total_budget()
        }
