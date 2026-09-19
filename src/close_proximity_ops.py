"""
Close Proximity Operations Module
Rendezvous final approach, station-keeping, flyaround,
and docking corridor management.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ProximityPhase(Enum):
    """Phases of close-proximity operations."""
    APPROACH = "approach"
    STATION_KEEPING = "station_keeping"
    FLYAROUND = "flyaround"
    FINAL_APPROACH = "final_approach"
    DOCKING = "docking"
    RETREAT = "retreat"


@dataclass
class Waypoint:
    """A waypoint in relative coordinates."""
    x_m: float  # Along-track (positive = in front of target)
    y_m: float  # Cross-track
    z_m: float  # Radial
    velocity_ms: float = 0.0
    hold_time_s: float = 0.0


class CloseProximityOps:
    """
    Close proximity operations planner and monitor.
    
    Manages rendezvous waypoints, approach corridors,
    and safety boundaries.
    """
    
    def __init__(self, target_size_m: float = 10.0,
                 docking_port_pos_m: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """
        Args:
            target_size_m: Characteristic target size
            docking_port_pos_m: Docking port position in target frame
        """
        self.target_size_m = target_size_m
        self.docking_port = docking_port_pos_m
        self.current_phase = ProximityPhase.APPROACH
        self.waypoints: List[Waypoint] = []
        self.current_waypoint_idx = 0
    
    def set_waypoints(self, waypoints: List[Waypoint]):
        """Set the approach waypoints."""
        self.waypoints = waypoints
        self.current_waypoint_idx = 0
    
    def standard_approach_waypoints(self, initial_range_m: float = 10000.0) -> List[Waypoint]:
        """
        Generate standard rendezvous waypoints.
        
        Args:
            initial_range_m: Starting range
        
        Returns:
            List of waypoints
        """
        return [
            Waypoint(x_m=initial_range_m, y_m=0.0, z_m=0.0, velocity_ms=-2.0),
            Waypoint(x_m=5000.0, y_m=0.0, z_m=0.0, velocity_ms=-1.0, hold_time_s=300.0),
            Waypoint(x_m=1000.0, y_m=0.0, z_m=0.0, velocity_ms=-0.5, hold_time_s=600.0),
            Waypoint(x_m=300.0, y_m=0.0, z_m=0.0, velocity_ms=-0.1, hold_time_s=300.0),
            Waypoint(x_m=50.0, y_m=0.0, z_m=0.0, velocity_ms=-0.05),
            Waypoint(x_m=10.0, y_m=0.0, z_m=0.0, velocity_ms=-0.01),
            Waypoint(x_m=0.0, y_m=0.0, z_m=0.0, velocity_ms=0.0)
        ]
    
    def flyaround_waypoints(self, radius_m: float = 200.0,
                            num_points: int = 8) -> List[Waypoint]:
        """
        Generate flyaround waypoints.
        
        Args:
            radius_m: Flyaround radius
            num_points: Number of waypoints
        
        Returns:
            Circular waypoints
        """
        waypoints = []
        for i in range(num_points + 1):
            angle = 2.0 * math.pi * i / num_points
            x = radius_m * math.cos(angle)
            y = radius_m * math.sin(angle)
            waypoints.append(Waypoint(x_m=x, y_m=y, z_m=0.0, velocity_ms=0.5))
        return waypoints
    
    def distance_to_waypoint(self, current_pos_m: Tuple[float, float, float]) -> float:
        """
        Distance to current waypoint.
        
        Args:
            current_pos_m: Current position
        
        Returns:
            Distance in meters
        """
        if not self.waypoints or self.current_waypoint_idx >= len(self.waypoints):
            return 0.0
        
        wp = self.waypoints[self.current_waypoint_idx]
        dx = current_pos_m[0] - wp.x_m
        dy = current_pos_m[1] - wp.y_m
        dz = current_pos_m[2] - wp.z_m
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def advance_waypoint(self, tolerance_m: float = 10.0) -> bool:
        """
        Advance to next waypoint if within tolerance.
        
        Args:
            tolerance_m: Waypoint tolerance
        
        Returns:
            True if advanced
        """
        if self.current_waypoint_idx < len(self.waypoints) - 1:
            self.current_waypoint_idx += 1
            return True
        return False
    
    def approach_corridor_check(self, position_m: Tuple[float, float, float],
                                 max_lateral_m: float = 50.0) -> Dict:
        """
        Check if position is within approach corridor.
        
        Args:
            position_m: Current position
            max_lateral_m: Maximum lateral deviation
        
        Returns:
            Corridor check result
        """
        x, y, z = position_m
        lateral = math.sqrt(y**2 + z**2)
        
        in_corridor = lateral <= max_lateral_m and x >= -50.0
        
        # Tighten corridor as range decreases
        if x < 1000.0:
            max_lateral_m = max(5.0, max_lateral_m * x / 1000.0)
            in_corridor = lateral <= max_lateral_m
        
        return {
            "in_corridor": in_corridor,
            "lateral_deviation_m": round(lateral, 2),
            "max_allowed_lateral_m": round(max_lateral_m, 2),
            "range_m": round(x, 2)
        }
    
    def station_keeping_dv(self, current_pos_m: Tuple[float, float, float],
                           current_vel_ms: Tuple[float, float, float],
                           hold_position_m: Tuple[float, float, float],
                           kp: float = 0.01,
                           kd: float = 0.1) -> Tuple[float, float, float]:
        """
        Compute station-keeping delta-V.
        
        PD control to maintain position.
        
        Args:
            current_pos_m: Current position
            current_vel_ms: Current velocity
            hold_position_m: Desired hold position
            kp: Position gain
            kd: Velocity gain
        
        Returns:
            Required delta-V per axis
        """
        dx = current_pos_m[0] - hold_position_m[0]
        dy = current_pos_m[1] - hold_position_m[1]
        dz = current_pos_m[2] - hold_position_m[2]
        
        dvx = -(kp * dx + kd * current_vel_ms[0])
        dvy = -(kp * dy + kd * current_vel_ms[1])
        dvz = -(kp * dz + kd * current_vel_ms[2])
        
        return (dvx, dvy, dvz)
    
    def docking_alignment_score(self, chaser_attitude_deg: Tuple[float, float, float],
                                 relative_pos_m: Tuple[float, float, float]) -> float:
        """
        Compute docking alignment score.
        
        Args:
            chaser_attitude_deg: Chaser attitude (roll, pitch, yaw)
            relative_pos_m: Relative position
        
        Returns:
            Score 0.0-1.0 (1.0 = perfect)
        """
        # Ideal: chaser -x axis points directly at target docking port
        # Simplified: just check if along-track alignment is good
        range_m = math.sqrt(relative_pos_m[0]**2 + relative_pos_m[1]**2 + relative_pos_m[2]**2)
        
        if range_m < 1.0:
            return 1.0
        
        # Alignment with x-axis
        cos_align = -relative_pos_m[0] / range_m  # Negative because approaching from +x
        cos_align = max(-1.0, min(1.0, cos_align))
        
        # Convert to score
        angle_deg = math.degrees(math.acos(cos_align))
        score = max(0.0, 1.0 - angle_deg / 10.0)
        
        return round(score, 3)
    
    def abort_manoeuvre(self, current_pos_m: Tuple[float, float, float],
                        current_vel_ms: Tuple[float, float, float],
                        abort_distance_m: float = 5000.0) -> Dict:
        """
        Compute abort manoeuvre.
        
        Args:
            current_pos_m: Current position
            current_vel_ms: Current velocity
            abort_distance_m: Target abort distance
        
        Returns:
            Abort plan
        """
        # Simple: burn retrograde to stop, then burn away
        vel_mag = math.sqrt(current_vel_ms[0]**2 + current_vel_ms[1]**2 + current_vel_ms[2]**2)
        
        if vel_mag > 0.0:
            # Delta-V to stop
            dv_stop = vel_mag
            
            # Delta-V to retreat
            retreat_direction = (
                current_pos_m[0] / abort_distance_m,
                current_pos_m[1] / abort_distance_m,
                current_pos_m[2] / abort_distance_m
            )
            dv_retreat = 2.0  # m/s retreat velocity
            
            total_dv = dv_stop + dv_retreat
        else:
            total_dv = 2.0
        
        return {
            "abort_distance_m": abort_distance_m,
            "delta_v_required_ms": round(total_dv, 3),
            "retreat_direction": retreat_direction if vel_mag > 0 else (1.0, 0.0, 0.0),
            "estimated_time_s": round(abort_distance_m / 2.0, 1)
        }
    
    def mission_timeline(self, current_pos_m: Tuple[float, float, float],
                         current_vel_ms: Tuple[float, float, float]) -> Dict:
        """
        Estimate mission timeline.
        
        Args:
            current_pos_m: Current position
            current_vel_ms: Current velocity
        
        Returns:
            Timeline estimate
        """
        range_m = math.sqrt(current_pos_m[0]**2 + current_pos_m[1]**2 + current_pos_m[2]**2)
        vel_mag = math.sqrt(current_vel_ms[0]**2 + current_vel_ms[1]**2 + current_vel_ms[2]**2)
        
        # Estimate time to each waypoint
        remaining_waypoints = self.waypoints[self.current_waypoint_idx:]
        
        total_time_s = 0.0
        if vel_mag > 0.1:
            total_time_s = range_m / vel_mag
        
        # Add hold times
        for wp in remaining_waypoints:
            total_time_s += wp.hold_time_s
        
        return {
            "current_phase": self.current_phase.value,
            "current_waypoint": self.current_waypoint_idx,
            "total_waypoints": len(self.waypoints),
            "range_to_target_m": round(range_m, 2),
            "estimated_remaining_time_min": round(total_time_s / 60.0, 2)
        }
