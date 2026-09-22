"""
Aerial Robotics Module
Quadcopter dynamics, trajectory planning,
attitude control, and obstacle avoidance for autonomous aerial systems.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Pose:
    """6-DOF pose."""
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float


class QuadcopterDynamics:
    """
    Simplified quadcopter dynamics.
    """
    
    def __init__(self, mass_kg: float = 1.0,
                 arm_length_m: float = 0.25,
                 thrust_coefficient: float = 1e-5,
                 drag_coefficient: float = 1e-7):
        """
        Args:
            mass_kg: Mass
            arm_length_m: Arm length
            thrust_coefficient: Thrust coeff
            drag_coefficient: Drag coeff
        """
        self.m = mass_kg
        self.L = arm_length_m
        self.k_t = thrust_coefficient
        self.k_d = drag_coefficient
        self.g = 9.81
    
    def thrust(self, angular_velocities: List[float]) -> float:
        """
        Compute total thrust from motor speeds.
        
        Args:
            angular_velocities: Motor speeds (rad/s)
        
        Returns:
            Total thrust (N)
        """
        return sum(self.k_t * w**2 for w in angular_velocities)
    
    def torque(self, angular_velocities: List[float]) -> Tuple[float, float, float]:
        """
        Compute body torques.
        
        Args:
            angular_velocities: Motor speeds
        
        Returns:
            (roll, pitch, yaw) torques
        """
        if len(angular_velocities) < 4:
            return (0.0, 0.0, 0.0)
        w1, w2, w3, w4 = angular_velocities[:4]
        tau_x = self.L * self.k_t * (w4**2 - w2**2)
        tau_y = self.L * self.k_t * (w3**2 - w1**2)
        tau_z = self.k_d * (w1**2 - w2**2 + w3**2 - w4**2)
        return (tau_x, tau_y, tau_z)
    
    def hover_thrust(self) -> float:
        """
        Compute hover thrust.
        
        Returns:
            Hover thrust (N)
        """
        return self.m * self.g


class TrajectoryPlanning:
    """
    Trajectory planning for aerial robots.
    """
    
    def __init__(self):
        pass
    
    def minimum_snap_waypoint(self, start: Tuple[float, float, float],
                             end: Tuple[float, float, float],
                             duration_s: float,
                             t: float) -> Tuple[float, float, float]:
        """
        Compute position along minimum-snap trajectory.
        
        Args:
            start: Start position
            end: End position
            duration_s: Duration
            t: Current time
        
        Returns:
            (x, y, z)
        """
        if duration_s <= 0:
            return end
        s = max(0.0, min(1.0, t / duration_s))
        # Quintic polynomial
        alpha = s**3 * (10.0 - 15.0 * s + 6.0 * s**2)
        x = start[0] + alpha * (end[0] - start[0])
        y = start[1] + alpha * (end[1] - start[1])
        z = start[2] + alpha * (end[2] - start[2])
        return (x, y, z)
    
    def trajectory_length(self, waypoints: List[Tuple[float, float, float]]) -> float:
        """
        Compute total path length.
        
        Args:
            waypoints: Waypoints
        
        Returns:
            Total length
        """
        total = 0.0
        for i in range(len(waypoints) - 1):
            dx = waypoints[i+1][0] - waypoints[i][0]
            dy = waypoints[i+1][1] - waypoints[i][1]
            dz = waypoints[i+1][2] - waypoints[i][2]
            total += math.sqrt(dx**2 + dy**2 + dz**2)
        return total


class AttitudeControl:
    """
    Attitude control for aerial robots.
    """
    
    def __init__(self, kp: float = 1.0, kd: float = 0.1):
        """
        Args:
            kp: Proportional gain
            kd: Derivative gain
        """
        self.kp = kp
        self.kd = kd
    
    def pd_control(self, current: float,
                  target: float,
                  current_rate: float,
                  target_rate: float = 0.0) -> float:
        """
        PD attitude control.
        
        Args:
            current: Current angle
            target: Target angle
            current_rate: Current angular rate
            target_rate: Target rate
        
        Returns:
            Control output
        """
        error = target - current
        rate_error = target_rate - current_rate
        return self.kp * error + self.kd * rate_error
    
    def attitude_error(self, current_roll: float,
                      current_pitch: float,
                      current_yaw: float,
                      target_roll: float,
                      target_pitch: float,
                      target_yaw: float) -> Tuple[float, float, float]:
        """
        Compute attitude error.
        
        Args:
            current: Current angles
            target: Target angles
        
        Returns:
            (roll_error, pitch_error, yaw_error)
        """
        return (target_roll - current_roll,
                target_pitch - current_pitch,
                target_yaw - current_yaw)


class ObstacleAvoidance:
    """
    Obstacle avoidance for aerial robots.
    """
    
    def __init__(self, safety_radius_m: float = 1.0):
        """
        Args:
            safety_radius_m: Safety radius
        """
        self.safety_radius = safety_radius_m
    
    def distance_to_obstacle(self, robot_pos: Tuple[float, float, float],
                            obstacle_pos: Tuple[float, float, float]) -> float:
        """
        Compute distance to obstacle.
        
        Args:
            robot_pos: Robot position
            obstacle_pos: Obstacle position
        
        Returns:
            Distance
        """
        dx = robot_pos[0] - obstacle_pos[0]
        dy = robot_pos[1] - obstacle_pos[1]
        dz = robot_pos[2] - obstacle_pos[2]
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def collision_risk(self, robot_pos: Tuple[float, float, float],
                      obstacle_pos: Tuple[float, float, float],
                      obstacle_radius: float = 0.5) -> bool:
        """
        Check collision risk.
        
        Args:
            robot_pos: Robot position
            obstacle_pos: Obstacle position
            obstacle_radius: Obstacle radius
        
        Returns:
            True if collision risk
        """
        dist = self.distance_to_obstacle(robot_pos, obstacle_pos)
        return dist < (self.safety_radius + obstacle_radius)
    
    def repulsive_force(self, robot_pos: Tuple[float, float, float],
                       obstacle_pos: Tuple[float, float, float],
                       gain: float = 1.0) -> Tuple[float, float, float]:
        """
        Compute repulsive force.
        
        Args:
            robot_pos: Robot position
            obstacle_pos: Obstacle position
            gain: Force gain
        
        Returns:
            (fx, fy, fz)
        """
        dx = robot_pos[0] - obstacle_pos[0]
        dy = robot_pos[1] - obstacle_pos[1]
        dz = robot_pos[2] - obstacle_pos[2]
        dist = math.sqrt(dx**2 + dy**2 + dz**2)
        if dist <= 0:
            return (0.0, 0.0, 0.0)
        force = gain / (dist ** 2)
        return (force * dx / dist, force * dy / dist, force * dz / dist)


class AerialRobotics:
    """
    Unified aerial robotics controller.
    """
    
    def __init__(self):
        self.dynamics = QuadcopterDynamics()
        self.trajectory = TrajectoryPlanning()
        self.attitude = AttitudeControl()
        self.avoidance = ObstacleAvoidance()
    
    def aerial_summary(self) -> Dict:
        """Get summary."""
        return {
            "modules": ["dynamics", "trajectory", "attitude", "avoidance"],
            "outputs": ["thrust", "torque", "waypoints", "control", "collision_check"]
        }
