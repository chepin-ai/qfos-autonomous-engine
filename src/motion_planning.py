"""
Motion Planning Module
Trajectory generation, cubic splines, velocity profiling,
jerk limitation, and waypoint interpolation for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Waypoint:
    """Robot waypoint."""
    x: float
    y: float
    theta: float  # Orientation in radians
    velocity: float


class CubicSpline:
    """
    Cubic spline interpolation.
    """
    
    def __init__(self, points: List[Tuple[float, float]]):
        """
        Args:
            points: (x, y) control points
        """
        self.points = points
        self.coeffs: List[Tuple[float, float, float, float]] = []
        self._compute_coeffs()
    
    def _compute_coeffs(self):
        """Compute spline coefficients."""
        n = len(self.points)
        if n < 2:
            return
        
        # Simplified: compute slopes between points
        for i in range(n - 1):
            x0, y0 = self.points[i]
            x1, y1 = self.points[i + 1]
            dx = x1 - x0
            dy = y1 - y0
            
            if dx == 0:
                self.coeffs.append((0.0, 0.0, 0.0, y0))
            else:
                m = dy / dx
                self.coeffs.append((0.0, 0.0, m, y0))
    
    def evaluate(self, x: float) -> float:
        """
        Evaluate spline at x.
        
        Args:
            x: Position
        
        Returns:
            Interpolated value
        """
        if not self.points:
            return 0.0
        
        # Find segment
        for i in range(len(self.points) - 1):
            x0 = self.points[i][0]
            x1 = self.points[i + 1][0]
            if x0 <= x <= x1:
                dx = x - x0
                a, b, c, d = self.coeffs[i]
                return a * dx ** 3 + b * dx ** 2 + c * dx + d
        
        return self.points[-1][1]
    
    def derivative(self, x: float) -> float:
        """
        Compute derivative at x.
        
        Args:
            x: Position
        
        Returns:
            Derivative
        """
        if not self.points:
            return 0.0
        
        for i in range(len(self.points) - 1):
            x0 = self.points[i][0]
            x1 = self.points[i + 1][0]
            if x0 <= x <= x1:
                dx = x - x0
                a, b, c, d = self.coeffs[i]
                return 3.0 * a * dx ** 2 + 2.0 * b * dx + c
        
        return 0.0


class VelocityProfiler:
    """
    Velocity profiling with trapezoidal profile.
    """
    
    def __init__(self, max_velocity: float = 1.0,
                 max_acceleration: float = 1.0):
        """
        Args:
            max_velocity: Max velocity
            max_acceleration: Max acceleration
        """
        self.v_max = max_velocity
        self.a_max = max_acceleration
    
    def profile_time(self, distance: float) -> float:
        """
        Compute time for trapezoidal profile.
        
        Args:
            distance: Distance
        
        Returns:
            Time
        """
        if distance <= 0:
            return 0.0
        
        # Time to accelerate to max velocity
        t_acc = self.v_max / self.a_max
        d_acc = 0.5 * self.a_max * t_acc ** 2
        
        if 2.0 * d_acc >= distance:
            # Triangular profile
            return 2.0 * math.sqrt(distance / self.a_max)
        
        # Trapezoidal profile
        d_const = distance - 2.0 * d_acc
        t_const = d_const / self.v_max
        return 2.0 * t_acc + t_const
    
    def velocity_at_time(self, distance: float,
                        t: float) -> float:
        """
        Compute velocity at time t.
        
        Args:
            distance: Total distance
            t: Time
        
        Returns:
            Velocity
        """
        total_time = self.profile_time(distance)
        if t <= 0:
            return 0.0
        if t >= total_time:
            return 0.0
        
        t_acc = self.v_max / self.a_max
        d_acc = 0.5 * self.a_max * t_acc ** 2
        
        if 2.0 * d_acc >= distance:
            # Triangular
            t_peak = total_time / 2.0
            if t <= t_peak:
                return self.a_max * t
            else:
                return self.a_max * (total_time - t)
        
        # Trapezoidal
        t_const_start = t_acc
        t_const_end = total_time - t_acc
        
        if t <= t_const_start:
            return self.a_max * t
        elif t <= t_const_end:
            return self.v_max
        else:
            return self.a_max * (total_time - t)


class JerkLimitedProfile:
    """
    S-curve (jerk-limited) motion profile.
    """
    
    def __init__(self, max_jerk: float = 1.0,
                 max_acceleration: float = 1.0,
                 max_velocity: float = 1.0):
        """
        Args:
            max_jerk: Max jerk
            max_acceleration: Max acceleration
            max_velocity: Max velocity
        """
        self.j_max = max_jerk
        self.a_max = max_acceleration
        self.v_max = max_velocity
    
    def profile_time(self, distance: float) -> float:
        """
        Compute S-curve profile time.
        
        Args:
            distance: Distance
        
        Returns:
            Time
        """
        # Simplified: use trapezoidal approximation
        vp = VelocityProfiler(self.v_max, self.a_max)
        return vp.profile_time(distance)


class TrajectoryGenerator:
    """
    Generate trajectories from waypoints.
    """
    
    def __init__(self):
        pass
    
    def generate(self, waypoints: List[Waypoint],
                dt: float = 0.1) -> List[Waypoint]:
        """
        Generate interpolated trajectory.
        
        Args:
            waypoints: Waypoints
            dt: Time step
        
        Returns:
            Trajectory
        """
        if len(waypoints) < 2:
            return waypoints
        
        result = []
        for i in range(len(waypoints) - 1):
            wp0 = waypoints[i]
            wp1 = waypoints[i + 1]
            
            # Interpolate
            num_steps = max(2, int(math.hypot(wp1.x - wp0.x, wp1.y - wp0.y) / (dt * wp0.velocity)))
            for j in range(num_steps):
                t = j / num_steps
                x = wp0.x + t * (wp1.x - wp0.x)
                y = wp0.y + t * (wp1.y - wp0.y)
                theta = wp0.theta + t * (wp1.theta - wp0.theta)
                v = wp0.velocity + t * (wp1.velocity - wp0.velocity)
                result.append(Waypoint(x, y, theta, v))
        
        result.append(waypoints[-1])
        return result


class MotionPlanning:
    """
    Unified motion planning controller.
    """
    
    def __init__(self):
        self.velocity_profiler = VelocityProfiler()
        self.jerk_profile = JerkLimitedProfile()
        self.trajectory_generator = TrajectoryGenerator()
    
    def plan_trajectory(self, waypoints: List[Waypoint]) -> List[Waypoint]:
        """
        Plan full trajectory.
        
        Args:
            waypoints: Waypoints
        
        Returns:
            Trajectory
        """
        return self.trajectory_generator.generate(waypoints)
    
    def mp_summary(self) -> Dict:
        """Get summary."""
        return {
            "profiles": ["trapezoidal", "s_curve"],
            "methods": ["cubic_spline", "velocity_profiler", "trajectory_generation"]
        }
