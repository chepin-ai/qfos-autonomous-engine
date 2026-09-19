"""
Formation Flying Control Module
Autonomous relative motion control for satellite formations.
Implements leader-follower and cyclic pursuit control laws.
"""

import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

try:
    from .docking import ClohessyWiltshire
except ImportError:
    from docking import ClohessyWiltshire


@dataclass
class FormationSatellite:
    """A satellite in a formation."""
    sat_id: str
    x_m: float = 0.0       # Relative position (radial)
    y_m: float = 0.0       # Relative position (along-track)
    z_m: float = 0.0       # Relative position (cross-track)
    vx_ms: float = 0.0
    vy_ms: float = 0.0
    vz_ms: float = 0.0
    mass_kg: float = 100.0


class LeaderFollowerControl:
    """
    Leader-follower formation flying control.
    
    Follower satellite maintains desired relative position to leader
    using CW dynamics-based control law.
    """
    
    def __init__(self, mean_motion_rad_s: float,
                 control_gains: Tuple[float, float, float] = (0.001, 0.001, 0.001)):
        """
        Args:
            mean_motion_rad_s: Mean motion of reference orbit
            control_gains: (kx, ky, kz) proportional gains
        """
        self.n = mean_motion_rad_s
        self.kx, self.ky, self.kz = control_gains
    
    @classmethod
    def from_altitude_km(cls, altitude_km: float):
        """Create controller from circular orbit altitude."""
        cw = ClohessyWiltshire.from_altitude_km(altitude_km)
        return cls(cw.n)
    
    def compute_control(self, follower: FormationSatellite,
                        desired_relative_m: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Compute control acceleration for follower.
        
        Args:
            follower: Current follower state
            desired_relative_m: Desired (x, y, z) relative position
        
        Returns:
            (ax, ay, az) control acceleration in m/s^2
        """
        n = self.n
        
        # Position error
        ex = follower.x_m - desired_relative_m[0]
        ey = follower.y_m - desired_relative_m[1]
        ez = follower.z_m - desired_relative_m[2]
        
        # PD-like control that cancels CW natural dynamics
        # The CW equations: xdd = 3n^2*x + 2n*yd + u_x
        #                   ydd = -2n*xd + u_y
        #                   zdd = -n^2*z + u_z
        # We choose u to make the system behave like a damped oscillator
        # Using standard LQR-like gains for CW control
        ax = -self.kx * ex - 0.5 * follower.vx_ms
        ay = -self.ky * ey - 0.5 * follower.vy_ms
        az = -self.kz * ez - 0.5 * follower.vz_ms
        
        return ax, ay, az
    
    def simulate_formation_keeping(self, follower: FormationSatellite,
                                    desired_relative_m: Tuple[float, float, float],
                                    duration_s: float = 3600.0,
                                    dt_s: float = 1.0) -> List[FormationSatellite]:
        """
        Simulate formation keeping for given duration.
        
        Returns:
            List of follower states at each timestep
        """
        states = [FormationSatellite(
            sat_id=follower.sat_id,
            x_m=follower.x_m, y_m=follower.y_m, z_m=follower.z_m,
            vx_ms=follower.vx_ms, vy_ms=follower.vy_ms, vz_ms=follower.vz_ms,
            mass_kg=follower.mass_kg
        )]
        
        state = states[0]
        n = self.n
        steps = int(duration_s / dt_s)
        
        for _ in range(steps):
            ax, ay, az = self.compute_control(state, desired_relative_m)
            
            # Simple Euler integration of CW dynamics with control
            # x_dot = vx
            # y_dot = vy
            # z_dot = vz
            # vx_dot = 3*n^2*x + 2*n*vy + ax
            # vy_dot = -2*n*vx + ay
            # vz_dot = -n^2*z + az
            
            dvx = (3 * n**2 * state.x_m + 2 * n * state.vy_ms + ax) * dt_s
            dvy = (-2 * n * state.vx_ms + ay) * dt_s
            dvz = (-n**2 * state.z_m + az) * dt_s
            
            state = FormationSatellite(
                sat_id=state.sat_id,
                x_m=state.x_m + state.vx_ms * dt_s,
                y_m=state.y_m + state.vy_ms * dt_s,
                z_m=state.z_m + state.vz_ms * dt_s,
                vx_ms=state.vx_ms + dvx,
                vy_ms=state.vy_ms + dvy,
                vz_ms=state.vz_ms + dvz,
                mass_kg=state.mass_kg
            )
            states.append(state)
        
        return states
    
    def formation_error(self, follower: FormationSatellite,
                        desired_relative_m: Tuple[float, float, float]) -> Dict:
        """Compute formation keeping error metrics."""
        ex = follower.x_m - desired_relative_m[0]
        ey = follower.y_m - desired_relative_m[1]
        ez = follower.z_m - desired_relative_m[2]
        
        return {
            "error_x_m": round(ex, 3),
            "error_y_m": round(ey, 3),
            "error_z_m": round(ez, 3),
            "error_3d_m": round(math.sqrt(ex**2 + ey**2 + ez**2), 3),
            "error_radial_m": round(abs(ex), 3),
            "error_cross_track_m": round(abs(ez), 3)
        }


class CyclicPursuitControl:
    """
    Cyclic pursuit formation control.
    
    Each satellite pursues the next satellite in a ring topology.
    Produces natural circular or spiral formation patterns.
    """
    
    def __init__(self, pursuit_gain: float = 0.01,
                 angular_rate_rad_s: float = 0.001):
        """
        Args:
            pursuit_gain: Gain for pursuit control
            angular_rate_rad_s: Desired angular rate of formation
        """
        self.k = pursuit_gain
        self.omega_d = angular_rate_rad_s
    
    def compute_pursuit_velocity(self, current_pos: Tuple[float, float],
                                  target_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Compute 2D pursuit velocity.
        
        Args:
            current_pos: (x, y) of pursuer
            target_pos: (x, y) of target
        
        Returns:
            (vx, vy) desired velocity
        """
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 1e-6:
            return (0.0, 0.0)
        
        # Pursuit velocity: toward target with angular bias
        vx = self.k * dx - self.omega_d * dy
        vy = self.k * dy + self.omega_d * dx
        
        return vx, vy
    
    def simulate_cyclic_formation(self, initial_positions: List[Tuple[float, float]],
                                   duration_s: float = 3600.0,
                                   dt_s: float = 1.0) -> List[List[Tuple[float, float]]]:
        """
        Simulate cyclic pursuit formation.
        
        Args:
            initial_positions: List of (x, y) initial positions
            duration_s: Simulation duration
            dt_s: Timestep
        
        Returns:
            Trajectories: list of position lists per satellite
        """
        n = len(initial_positions)
        positions = [list(p) for p in initial_positions]
        trajectories = [[tuple(p)] for p in initial_positions]
        
        steps = int(duration_s / dt_s)
        
        for _ in range(steps):
            new_positions = []
            for i in range(n):
                target_i = (i + 1) % n
                vx, vy = self.compute_pursuit_velocity(
                    (positions[i][0], positions[i][1]),
                    (positions[target_i][0], positions[target_i][1])
                )
                
                new_x = positions[i][0] + vx * dt_s
                new_y = positions[i][1] + vy * dt_s
                new_positions.append([new_x, new_y])
                trajectories[i].append((new_x, new_y))
            
            positions = new_positions
        
        return trajectories
    
    def formation_spread(self, positions: List[Tuple[float, float]]) -> Dict:
        """Compute formation geometry metrics."""
        n = len(positions)
        if n < 2:
            return {"count": n}
        
        # Centroid
        cx = sum(p[0] for p in positions) / n
        cy = sum(p[1] for p in positions) / n
        
        # Spread (mean distance from centroid)
        spread = sum(math.sqrt((p[0]-cx)**2 + (p[1]-cy)**2) for p in positions) / n
        
        # Pairwise distances
        distances = []
        for i in range(n):
            for j in range(i+1, n):
                d = math.sqrt((positions[i][0]-positions[j][0])**2 +
                              (positions[i][1]-positions[j][1])**2)
                distances.append(d)
        
        return {
            "satellite_count": n,
            "centroid": (round(cx, 3), round(cy, 3)),
            "mean_spread_m": round(spread, 3),
            "min_distance_m": round(min(distances), 3) if distances else 0,
            "max_distance_m": round(max(distances), 3) if distances else 0,
            "mean_distance_m": round(sum(distances)/len(distances), 3) if distances else 0
        }


class FormationPlanner:
    """
    Plan formation geometries for specific mission objectives.
    """
    
    @staticmethod
    def along_track_separation(n_satellites: int,
                                 separation_m: float) -> List[Tuple[float, float, float]]:
        """
        Create along-track formation.
        
        Returns:
            List of desired relative positions
        """
        return [(0.0, i * separation_m, 0.0) for i in range(n_satellites)]
    
    @staticmethod
    def cartwheel_formation(n_satellites: int,
                            radius_m: float) -> List[Tuple[float, float, float]]:
        """
        Create cartwheel (circular) formation in cross-track plane.
        
        Returns:
            List of desired relative positions
        """
        positions = []
        for i in range(n_satellites):
            angle = 2 * math.pi * i / n_satellites
            positions.append((0.0, 0.0, radius_m * math.sin(angle)))
        return positions
    
    @staticmethod
    def pendulum_formation(n_satellites: int,
                           baseline_m: float) -> List[Tuple[float, float, float]]:
        """
        Create pendulum (radial oscillation) formation.
        
        Returns:
            List of desired relative positions
        """
        positions = []
        for i in range(n_satellites):
            frac = (i / max(n_satellites - 1, 1)) - 0.5
            positions.append((frac * baseline_m, 0.0, 0.0))
        return positions
    
    @staticmethod
    def inspector_formation(target_distance_m: float = 100.0) -> List[Tuple[float, float, float]]:
        """
        Create inspector (proximity) formation around target.
        
        Returns:
            Positions for inspection viewpoints
        """
        return [
            (target_distance_m, 0.0, 0.0),
            (0.0, target_distance_m, 0.0),
            (-target_distance_m, 0.0, 0.0),
            (0.0, -target_distance_m, 0.0),
        ]
