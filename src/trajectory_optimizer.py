"""
Trajectory Optimizer Module
Minimum snap trajectory generation and time-optimal
trajectory optimization for spacecraft and robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Waypoint:
    """A waypoint in 3D space with time."""
    x: float
    y: float
    z: float
    t: float = 0.0  # Time at waypoint
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0


@dataclass
class PolynomialSegment:
    """A polynomial trajectory segment."""
    coeffs_x: List[float] = field(default_factory=list)
    coeffs_y: List[float] = field(default_factory=list)
    coeffs_z: List[float] = field(default_factory=list)
    t_start: float = 0.0
    t_end: float = 0.0
    
    def evaluate(self, t: float) -> Tuple[float, float, float]:
        """
        Evaluate position at time t.
        
        Args:
            t: Time
        
        Returns:
            (x, y, z)
        """
        dt = t - self.t_start
        x = sum(c * dt ** i for i, c in enumerate(self.coeffs_x))
        y = sum(c * dt ** i for i, c in enumerate(self.coeffs_y))
        z = sum(c * dt ** i for i, c in enumerate(self.coeffs_z))
        return (x, y, z)
    
    def evaluate_velocity(self, t: float) -> Tuple[float, float, float]:
        """Evaluate velocity at time t."""
        dt = t - self.t_start
        vx = sum(c * i * dt ** (i - 1) for i, c in enumerate(self.coeffs_x) if i > 0)
        vy = sum(c * i * dt ** (i - 1) for i, c in enumerate(self.coeffs_y) if i > 0)
        vz = sum(c * i * dt ** (i - 1) for i, c in enumerate(self.coeffs_z) if i > 0)
        return (vx, vy, vz)
    
    def evaluate_acceleration(self, t: float) -> Tuple[float, float, float]:
        """Evaluate acceleration at time t."""
        dt = t - self.t_start
        ax = sum(c * i * (i - 1) * dt ** (i - 2) for i, c in enumerate(self.coeffs_x) if i > 1)
        ay = sum(c * i * (i - 1) * dt ** (i - 2) for i, c in enumerate(self.coeffs_y) if i > 1)
        az = sum(c * i * (i - 1) * dt ** (i - 2) for i, c in enumerate(self.coeffs_z) if i > 1)
        return (ax, ay, az)


class MinimumSnapOptimizer:
    """
    Minimum snap trajectory optimizer.
    
    Generates smooth polynomial trajectories through waypoints.
    """
    
    def __init__(self, order: int = 7):
        """
        Args:
            order: Polynomial order (default 7 for min snap)
        """
        self.order = order
        self.segments: List[PolynomialSegment] = []
    
    def solve_segment(self, p0: float, p1: float,
                     v0: float, v1: float,
                     a0: float, a1: float,
                     t: float) -> List[float]:
        """
        Solve 1D polynomial segment with position, velocity, acceleration constraints.
        
        Args:
            p0, p1: Start/end position
            v0, v1: Start/end velocity
            a0, a1: Start/end acceleration
            t: Segment duration
        
        Returns:
            Polynomial coefficients [c0, c1, c2, c3, c4, c5]
        """
        if t <= 0:
            return [p0, 0, 0, 0, 0, 0]
        
        # Quintic polynomial: p(t) = c0 + c1*t + c2*t^2 + c3*t^3 + c4*t^4 + c5*t^5
        # Constraints at t=0: p=p0, v=v0, a=a0
        # Constraints at t=T: p=p1, v=v1, a=a1
        
        T = t
        T2 = T * T
        T3 = T2 * T
        T4 = T3 * T
        T5 = T4 * T
        
        c0 = p0
        c1 = v0
        c2 = a0 / 2.0
        
        # Solve for c3, c4, c5 from end constraints
        # p(T) = c0 + c1*T + c2*T^2 + c3*T^3 + c4*T^4 + c5*T^5 = p1
        # v(T) = c1 + 2*c2*T + 3*c3*T^2 + 4*c4*T^3 + 5*c5*T^4 = v1
        # a(T) = 2*c2 + 6*c3*T + 12*c4*T^2 + 20*c5*T^3 = a1
        
        # Matrix form for c3, c4, c5
        # T3*c3 + T4*c4 + T5*c5 = p1 - c0 - c1*T - c2*T^2
        # 3*T2*c3 + 4*T3*c4 + 5*T4*c5 = v1 - c1 - 2*c2*T
        # 6*T*c3 + 12*T2*c4 + 20*T3*c5 = a1 - 2*c2
        
        rhs_p = p1 - c0 - c1 * T - c2 * T2
        rhs_v = v1 - c1 - 2 * c2 * T
        rhs_a = a1 - 2 * c2
        
        # Simple Gaussian elimination for 3x3
        A = [
            [T3, T4, T5],
            [3*T2, 4*T3, 5*T4],
            [6*T, 12*T2, 20*T3]
        ]
        b = [rhs_p, rhs_v, rhs_a]
        
        # Forward elimination
        for i in range(3):
            pivot = A[i][i]
            if abs(pivot) < 1e-10:
                pivot = 1e-10
            for j in range(i, 3):
                A[i][j] /= pivot
            b[i] /= pivot
            
            for k in range(i + 1, 3):
                factor = A[k][i]
                for j in range(i, 3):
                    A[k][j] -= factor * A[i][j]
                b[k] -= factor * b[i]
        
        # Back substitution
        c = [0.0, 0.0, 0.0]
        for i in range(2, -1, -1):
            c[i] = b[i]
            for j in range(i + 1, 3):
                c[i] -= A[i][j] * c[j]
        
        return [c0, c1, c2, c[0], c[1], c[2]]
    
    def optimize(self, waypoints: List[Waypoint]) -> List[PolynomialSegment]:
        """
        Optimize trajectory through waypoints.
        
        Args:
            waypoints: List of waypoints
        
        Returns:
            List of polynomial segments
        """
        if len(waypoints) < 2:
            return []
        
        self.segments = []
        
        for i in range(len(waypoints) - 1):
            wp0 = waypoints[i]
            wp1 = waypoints[i + 1]
            dt = wp1.t - wp0.t
            
            if dt <= 0:
                dt = 1.0
            
            coeffs_x = self.solve_segment(wp0.x, wp1.x, wp0.vx, wp1.vx, 0, 0, dt)
            coeffs_y = self.solve_segment(wp0.y, wp1.y, wp0.vy, wp1.vy, 0, 0, dt)
            coeffs_z = self.solve_segment(wp0.z, wp1.z, wp0.vz, wp1.vz, 0, 0, dt)
            
            segment = PolynomialSegment(
                coeffs_x=coeffs_x,
                coeffs_y=coeffs_y,
                coeffs_z=coeffs_z,
                t_start=wp0.t,
                t_end=wp1.t
            )
            self.segments.append(segment)
        
        return self.segments
    
    def evaluate(self, t: float) -> Optional[Tuple[float, float, float]]:
        """
        Evaluate trajectory at time t.
        
        Args:
            t: Time
        
        Returns:
            Position or None
        """
        for seg in self.segments:
            if seg.t_start <= t <= seg.t_end:
                return seg.evaluate(t)
        return None


class TimeOptimalPath:
    """
    Time-optimal path parameterization.
    """
    
    def __init__(self, max_velocity: float = 1.0,
                 max_acceleration: float = 1.0):
        """
        Args:
            max_velocity: Maximum velocity
            max_acceleration: Maximum acceleration
        """
        self.max_velocity = max_velocity
        self.max_acceleration = max_acceleration
    
    def compute_trapezoidal_profile(self, distance: float
                                    ) -> Tuple[float, float, float]:
        """
        Compute trapezoidal velocity profile.
        
        Args:
            distance: Total distance
        
        Returns:
            (acceleration_time, coast_time, deceleration_time)
        """
        if distance <= 0:
            return (0.0, 0.0, 0.0)
        
        # Time to accelerate to max velocity
        t_accel = self.max_velocity / self.max_acceleration
        d_accel = 0.5 * self.max_acceleration * t_accel ** 2
        
        if 2 * d_accel >= distance:
            # Triangular profile (never reaches max velocity)
            t_accel = math.sqrt(distance / self.max_acceleration)
            return (t_accel, 0.0, t_accel)
        
        # Trapezoidal profile
        d_coast = distance - 2 * d_accel
        t_coast = d_coast / self.max_velocity
        
        return (t_accel, t_coast, t_accel)
    
    def parameterize_path(self, path: List[Tuple[float, float, float]]
                         ) -> List[Waypoint]:
        """
        Parameterize path with time-optimal timing.
        
        Args:
            path: Path points
        
        Returns:
            Waypoints with timing
        """
        if len(path) < 2:
            return []
        
        waypoints = []
        total_time = 0.0
        
        waypoints.append(Waypoint(x=path[0][0], y=path[0][1], z=path[0][2], t=0.0))
        
        for i in range(len(path) - 1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            dz = path[i+1][2] - path[i][2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            t_accel, t_coast, t_decel = self.compute_trapezoidal_profile(dist)
            segment_time = t_accel + t_coast + t_decel
            
            total_time += segment_time
            
            waypoints.append(Waypoint(
                x=path[i+1][0],
                y=path[i+1][1],
                z=path[i+1][2],
                t=total_time
            ))
        
        return waypoints


class TrajectoryOptimizer:
    """
    Unified trajectory optimization controller.
    """
    
    def __init__(self):
        self.min_snap = MinimumSnapOptimizer()
        self.time_opt = TimeOptimalPath()
    
    def optimize_waypoints(self, waypoints: List[Waypoint]
                          ) -> List[PolynomialSegment]:
        """
        Optimize waypoints for minimum snap.
        
        Args:
            waypoints: Waypoints
        
        Returns:
            Polynomial segments
        """
        return self.min_snap.optimize(waypoints)
    
    def optimize_path(self, path: List[Tuple[float, float, float]],
                     max_velocity: float = 1.0,
                     max_acceleration: float = 1.0
                     ) -> List[Waypoint]:
        """
        Time-optimal path parameterization.
        
        Args:
            path: Path points
            max_velocity: Max velocity
            max_acceleration: Max acceleration
        
        Returns:
            Timed waypoints
        """
        self.time_opt.max_velocity = max_velocity
        self.time_opt.max_acceleration = max_acceleration
        return self.time_opt.parameterize_path(path)
    
    def get_trajectory_duration(self, segments: List[PolynomialSegment]) -> float:
        """Get total trajectory duration."""
        if not segments:
            return 0.0
        return segments[-1].t_end - segments[0].t_start
    
    def check_velocity_constraints(self, segments: List[PolynomialSegment],
                                  max_v: float,
                                  num_samples: int = 100) -> bool:
        """
        Check if trajectory satisfies velocity constraints.
        
        Args:
            segments: Trajectory segments
            max_v: Maximum velocity
            num_samples: Number of sample points
        
        Returns:
            True if constraints satisfied
        """
        for seg in segments:
            dt = seg.t_end - seg.t_start
            for i in range(num_samples):
                t = seg.t_start + i / num_samples * dt
                vx, vy, vz = seg.evaluate_velocity(t)
                v = math.sqrt(vx*vx + vy*vy + vz*vz)
                if v > max_v * 1.01:  # 1% tolerance
                    return False
        return True
    
    def optimizer_summary(self) -> Dict:
        """Get optimizer summary."""
        return {
            "segments": len(self.min_snap.segments),
            "duration": self.get_trajectory_duration(self.min_snap.segments),
            "max_velocity": self.time_opt.max_velocity,
            "max_acceleration": self.time_opt.max_acceleration
        }
