"""
Trajectory Generator Module
Spline interpolation, velocity profiling, and time-optimal
planning for autonomous robotic motion control.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ProfileType(Enum):
    """Types of velocity profiles."""
    TRAPEZOIDAL = "trapezoidal"
    S_CURVE = "s_curve"
    CUBIC = "cubic"
    QUINTIC = "quintic"


@dataclass
class Waypoint:
    """A trajectory waypoint."""
    position: float
    velocity: float = 0.0
    acceleration: float = 0.0
    time: float = 0.0


class CubicSpline:
    """
    Cubic spline interpolation.
    """
    
    def __init__(self, waypoints: List[Waypoint]):
        """
        Args:
            waypoints: List of waypoints
        """
        self.waypoints = sorted(waypoints, key=lambda w: w.position)
        self.coefficients: List[Tuple[float, float, float, float]] = []
        self._compute()
    
    def _compute(self):
        """Compute cubic spline coefficients."""
        n = len(self.waypoints)
        if n < 2:
            return
        
        # Natural cubic spline: second derivatives at endpoints = 0
        h = [0.0] * (n - 1)
        for i in range(n - 1):
            h[i] = self.waypoints[i + 1].position - self.waypoints[i].position
            if h[i] == 0:
                h[i] = 1e-6
        
        # Tridiagonal system for second derivatives
        a = [0.0] * n
        b = [1.0] + [2.0 * (h[i - 1] + h[i]) for i in range(1, n - 1)] + [1.0]
        c = [0.0] + h[1:] + [0.0]
        d = [0.0]
        
        for i in range(1, n - 1):
            d_i = 3.0 * ((self.waypoints[i + 1].velocity - self.waypoints[i].velocity) / h[i] -
                        (self.waypoints[i].velocity - self.waypoints[i - 1].velocity) / h[i - 1])
            d.append(d_i)
        d.append(0.0)
        
        # Thomas algorithm
        m = [0.0] * n
        cp = [0.0] * n
        dp = [0.0] * n
        
        cp[0] = c[0] / b[0] if b[0] != 0 else 0
        dp[0] = d[0] / b[0] if b[0] != 0 else 0
        
        for i in range(1, n):
            denom = b[i] - a[i] * cp[i - 1]
            cp[i] = c[i] / denom if denom != 0 else 0
            dp[i] = (d[i] - a[i] * dp[i - 1]) / denom if denom != 0 else 0
        
        m[-1] = dp[-1]
        for i in range(n - 2, -1, -1):
            m[i] = dp[i] - cp[i] * m[i + 1]
        
        # Compute coefficients a, b, c, d for each segment
        # S_i(x) = a + b(x-x_i) + c(x-x_i)^2 + d(x-x_i)^3
        for i in range(n - 1):
            p0 = self.waypoints[i].position
            p1 = self.waypoints[i + 1].position
            v0 = self.waypoints[i].velocity
            v1 = self.waypoints[i + 1].velocity
            hi = h[i]
            
            a_coef = v0
            b_coef = (v1 - v0) / hi - hi * (2.0 * m[i] + m[i + 1]) / 6.0
            c_coef = 0.5 * m[i]
            d_coef = (m[i + 1] - m[i]) / (6.0 * hi)
            
            self.coefficients.append((a_coef, b_coef, c_coef, d_coef))
    
    def evaluate(self, x: float) -> float:
        """
        Evaluate spline at position.
        
        Args:
            x: Position
        
        Returns:
            Interpolated value
        """
        if not self.waypoints:
            return 0.0
        
        # Find segment
        idx = 0
        for i in range(len(self.waypoints) - 1):
            if x >= self.waypoints[i].position and x <= self.waypoints[i + 1].position:
                idx = i
                break
        
        if idx >= len(self.coefficients):
            return self.waypoints[-1].velocity
        
        a, b, c, d = self.coefficients[idx]
        dx = x - self.waypoints[idx].position
        return a + b * dx + c * dx**2 + d * dx**3
    
    def derivative(self, x: float) -> float:
        """
        Evaluate derivative.
        
        Args:
            x: Position
        
        Returns:
            Derivative
        """
        if not self.waypoints:
            return 0.0
        
        idx = 0
        for i in range(len(self.waypoints) - 1):
            if x >= self.waypoints[i].position and x <= self.waypoints[i + 1].position:
                idx = i
                break
        
        if idx >= len(self.coefficients):
            return 0.0
        
        a, b, c, d = self.coefficients[idx]
        dx = x - self.waypoints[idx].position
        return b + 2.0 * c * dx + 3.0 * d * dx**2


class VelocityProfile:
    """
    Trapezoidal and S-curve velocity profiling.
    """
    
    def __init__(self, vmax: float = 1.0, amax: float = 2.0,
                 jmax: float = 4.0):
        """
        Args:
            vmax: Maximum velocity
            amax: Maximum acceleration
            jmax: Maximum jerk
        """
        self.vmax = vmax
        self.amax = amax
        self.jmax = jmax
    
    def trapezoidal_time(self, distance: float) -> float:
        """
        Compute trapezoidal profile duration.
        
        Args:
            distance: Travel distance
        
        Returns:
            Total time
        """
        if distance <= 0:
            return 0.0
        
        # Acceleration and deceleration time
        t_acc = self.vmax / self.amax
        d_acc = 0.5 * self.amax * t_acc**2
        
        if 2.0 * d_acc >= distance:
            # Triangular profile
            return 2.0 * math.sqrt(distance / self.amax)
        
        # Trapezoidal profile
        d_const = distance - 2.0 * d_acc
        t_const = d_const / self.vmax
        return 2.0 * t_acc + t_const
    
    def trapezoidal_velocity(self, t: float, distance: float) -> float:
        """
        Get velocity at time.
        
        Args:
            t: Time
            distance: Total distance
        
        Returns:
            Velocity
        """
        if distance <= 0:
            return 0.0
        
        t_total = self.trapezoidal_time(distance)
        if t <= 0:
            return 0.0
        if t >= t_total:
            return 0.0
        
        t_acc = self.vmax / self.amax
        d_acc = 0.5 * self.amax * t_acc**2
        
        if 2.0 * d_acc >= distance:
            # Triangular
            t_peak = t_total / 2.0
            if t <= t_peak:
                return self.amax * t
            return self.amax * (t_total - t)
        
        # Trapezoidal
        t_const_start = t_acc
        t_const_end = t_total - t_acc
        
        if t <= t_const_start:
            return self.amax * t
        elif t <= t_const_end:
            return self.vmax
        else:
            return self.amax * (t_total - t)
    
    def s_curve_time(self, distance: float) -> float:
        """
        Compute S-curve profile duration.
        
        Args:
            distance: Travel distance
        
        Returns:
            Total time
        """
        # Simplified: use trapezoidal with jerk limit approximation
        t_jerk = self.amax / self.jmax
        d_jerk = self.jmax * t_jerk**3 / 6.0
        
        t_trap = self.trapezoidal_time(distance)
        return t_trap + 4.0 * t_jerk


class TimeOptimalPlanner:
    """
    Time-optimal path planning.
    """
    
    def __init__(self, vmax: float = 1.0, amax: float = 2.0):
        """
        Args:
            vmax: Maximum velocity
            amax: Maximum acceleration
        """
        self.vmax = vmax
        self.amax = amax
    
    def plan(self, waypoints: List[Waypoint]) -> List[float]:
        """
        Plan time-optimal trajectory.
        
        Args:
            waypoints: Path waypoints
        
        Returns:
            List of segment durations
        """
        if len(waypoints) < 2:
            return []
        
        durations = []
        for i in range(len(waypoints) - 1):
            dist = abs(waypoints[i + 1].position - waypoints[i].position)
            t = self._segment_time(dist)
            durations.append(t)
        
        return durations
    
    def _segment_time(self, distance: float) -> float:
        """Compute single segment time."""
        if distance <= 0:
            return 0.0
        
        t_acc = self.vmax / self.amax
        d_acc = 0.5 * self.amax * t_acc**2
        
        if 2.0 * d_acc >= distance:
            return 2.0 * math.sqrt(distance / self.amax)
        
        d_const = distance - 2.0 * d_acc
        t_const = d_const / self.vmax
        return 2.0 * t_acc + t_const
    
    def total_time(self, durations: List[float]) -> float:
        """
        Sum total trajectory time.
        
        Args:
            durations: Segment durations
        
        Returns:
            Total time
        """
        return sum(durations)


class TrajectoryGenerator:
    """
    Unified trajectory generation controller.
    """
    
    def __init__(self):
        self.spline: Optional[CubicSpline] = None
        self.profile = VelocityProfile()
        self.planner = TimeOptimalPlanner()
        self.waypoints: List[Waypoint] = []
    
    def set_waypoints(self, waypoints: List[Waypoint]):
        """Set path waypoints."""
        self.waypoints = waypoints
        self.spline = CubicSpline(waypoints)
    
    def generate(self, dt: float = 0.01) -> List[Dict]:
        """
        Generate trajectory points.
        
        Args:
            dt: Time step
        
        Returns:
            List of trajectory states
        """
        if not self.waypoints:
            return []
        
        durations = self.planner.plan(self.waypoints)
        total_t = sum(durations)
        
        trajectory = []
        t = 0.0
        while t <= total_t:
            # Approximate position as fraction of total
            fraction = t / total_t if total_t > 0 else 0.0
            pos_range = self.waypoints[-1].position - self.waypoints[0].position
            pos = self.waypoints[0].position + fraction * pos_range
            
            vel = self.profile.trapezoidal_velocity(t, abs(pos_range))
            
            trajectory.append({
                "time": t,
                "position": pos,
                "velocity": vel
            })
            t += dt
        
        return trajectory
    
    def trajectory_summary(self) -> Dict:
        """Get trajectory summary."""
        if not self.waypoints:
            return {"status": "no_waypoints"}
        
        durations = self.planner.plan(self.waypoints)
        total = sum(durations)
        dist = abs(self.waypoints[-1].position - self.waypoints[0].position)
        
        return {
            "waypoints": len(self.waypoints),
            "total_distance": dist,
            "total_time": total,
            "avg_velocity": dist / total if total > 0 else 0.0
        }
