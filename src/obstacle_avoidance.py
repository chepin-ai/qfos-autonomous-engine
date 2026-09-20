"""
Obstacle Avoidance Module
Potential fields, collision detection, and local planning
for autonomous system navigation.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ObstacleType(Enum):
    """Obstacle classification."""
    STATIC = "static"
    DYNAMIC = "dynamic"
    UNKNOWN = "unknown"


@dataclass
class Obstacle:
    """An obstacle in the environment."""
    obstacle_id: str
    position: Tuple[float, float]  # (x, y)
    radius_m: float
    obstacle_type: ObstacleType = ObstacleType.STATIC
    velocity: Tuple[float, float] = (0.0, 0.0)


class PotentialFieldPlanner:
    """
    Potential field-based obstacle avoidance.
    """
    
    def __init__(self, attractive_gain: float = 1.0,
                 repulsive_gain: float = 100.0,
                 influence_radius_m: float = 5.0):
        """
        Args:
            attractive_gain: Goal attraction strength
            repulsive_gain: Obstacle repulsion strength
            influence_radius_m: Obstacle influence radius
        """
        self.k_att = attractive_gain
        self.k_rep = repulsive_gain
        self.influence_radius = influence_radius_m
    
    def attractive_force(self, position: Tuple[float, float],
                        goal: Tuple[float, float]) -> Tuple[float, float]:
        """
        Compute attractive force toward goal.
        
        Args:
            position: Current position
            goal: Goal position
        
        Returns:
            Force vector (Fx, Fy)
        """
        dx = goal[0] - position[0]
        dy = goal[1] - position[1]
        
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 0.001:
            return (0.0, 0.0)
        
        fx = self.k_att * dx / dist
        fy = self.k_att * dy / dist
        
        return (fx, fy)
    
    def repulsive_force(self, position: Tuple[float, float],
                       obstacle: Obstacle) -> Tuple[float, float]:
        """
        Compute repulsive force from obstacle.
        
        Args:
            position: Current position
            obstacle: Obstacle
        
        Returns:
            Force vector (Fx, Fy)
        """
        dx = position[0] - obstacle.position[0]
        dy = position[1] - obstacle.position[1]
        
        dist = math.sqrt(dx**2 + dy**2)
        min_dist = obstacle.radius_m
        
        if dist <= min_dist:
            # Inside obstacle: very strong repulsion
            if dist < 0.001:
                return (1e6, 1e6)
            scale = self.k_rep * (1.0/min_dist - 1.0/self.influence_radius)
            return (scale * dx / dist, scale * dy / dist)
        
        if dist >= self.influence_radius + min_dist:
            return (0.0, 0.0)
        
        # Potential field repulsion
        effective_dist = dist - min_dist
        if effective_dist < 0.001:
            effective_dist = 0.001
        
        scale = self.k_rep * (1.0/effective_dist - 1.0/self.influence_radius)
        scale /= effective_dist**2
        
        fx = scale * dx / dist
        fy = scale * dy / dist
        
        return (fx, fy)
    
    def total_force(self, position: Tuple[float, float],
                   goal: Tuple[float, float],
                   obstacles: List[Obstacle]) -> Tuple[float, float]:
        """
        Compute total force.
        
        Args:
            position: Current position
            goal: Goal position
            obstacles: Obstacles
        
        Returns:
            Total force
        """
        fx, fy = self.attractive_force(position, goal)
        
        for obs in obstacles:
            rx, ry = self.repulsive_force(position, obs)
            fx += rx
            fy += ry
        
        return (fx, fy)
    
    def plan_step(self, position: Tuple[float, float],
                 goal: Tuple[float, float],
                 obstacles: List[Obstacle],
                 step_size: float = 0.1) -> Tuple[float, float]:
        """
        Plan one step toward goal.
        
        Args:
            position: Current position
            goal: Goal position
            obstacles: Obstacles
            step_size: Step size
        
        Returns:
            Next position
        """
        fx, fy = self.total_force(position, goal, obstacles)
        
        f_mag = math.sqrt(fx**2 + fy**2)
        if f_mag < 0.001:
            return position
        
        dx = step_size * fx / f_mag
        dy = step_size * fy / f_mag
        
        return (position[0] + dx, position[1] + dy)


class CollisionDetector:
    """
    Detect collisions between objects.
    """
    
    def __init__(self, safety_margin_m: float = 0.1):
        """
        Args:
            safety_margin_m: Safety margin
        """
        self.safety_margin = safety_margin_m
    
    def point_to_circle(self, point: Tuple[float, float],
                       center: Tuple[float, float],
                       radius_m: float) -> float:
        """
        Distance from point to circle.
        
        Args:
            point: Point
            center: Circle center
            radius_m: Circle radius
        
        Returns:
            Distance (negative = inside)
        """
        dx = point[0] - center[0]
        dy = point[1] - center[1]
        dist = math.sqrt(dx**2 + dy**2)
        return dist - radius_m
    
    def circle_to_circle(self, c1: Tuple[float, float], r1: float,
                        c2: Tuple[float, float], r2: float) -> float:
        """
        Distance between circles.
        
        Args:
            c1, c2: Centers
            r1, r2: Radii
        
        Returns:
            Separation distance (negative = overlap)
        """
        dx = c1[0] - c2[0]
        dy = c1[1] - c2[1]
        dist = math.sqrt(dx**2 + dy**2)
        return dist - r1 - r2
    
    def check_collision(self, position: Tuple[float, float],
                       radius_m: float,
                       obstacles: List[Obstacle]) -> bool:
        """
        Check for collision.
        
        Args:
            position: Object position
            radius_m: Object radius
            obstacles: Obstacles
        
        Returns:
            True if collision
        """
        for obs in obstacles:
            sep = self.circle_to_circle(position, radius_m,
                                       obs.position, obs.radius_m + self.safety_margin)
            if sep < 0:
                return True
        return False
    
    def nearest_obstacle(self, position: Tuple[float, float],
                        obstacles: List[Obstacle]) -> Optional[Tuple[Obstacle, float]]:
        """
        Find nearest obstacle.
        
        Args:
            position: Current position
            obstacles: Obstacles
        
        Returns:
            (nearest obstacle, distance) or None
        """
        if not obstacles:
            return None
        
        nearest = None
        min_dist = float('inf')
        
        for obs in obstacles:
            dx = position[0] - obs.position[0]
            dy = position[1] - obs.position[1]
            dist = math.sqrt(dx**2 + dy**2) - obs.radius_m
            
            if dist < min_dist:
                min_dist = dist
                nearest = obs
        
        if nearest:
            return (nearest, min_dist)
        return None


class LocalPlanner:
    """
    Local trajectory planner.
    """
    
    def __init__(self, max_speed_ms: float = 1.0,
                 max_accel_ms2: float = 1.0):
        """
        Args:
            max_speed_ms: Maximum speed
            max_accel_ms2: Maximum acceleration
        """
        self.max_speed = max_speed_ms
        self.max_accel = max_accel_ms2
    
    def plan_velocity(self, position: Tuple[float, float],
                     goal: Tuple[float, float],
                     current_speed: float = 0.0,
                     dt_s: float = 0.1) -> Tuple[float, float]:
        """
        Plan velocity toward goal.
        
        Args:
            position: Current position
            goal: Goal position
            current_speed: Current speed
            dt_s: Time step
        
        Returns:
            Velocity command (vx, vy)
        """
        dx = goal[0] - position[0]
        dy = goal[1] - position[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist < 0.01:
            return (0.0, 0.0)
        
        # Speed profile: slow down near goal
        target_speed = min(self.max_speed, dist / dt_s)
        
        # Direction
        vx = target_speed * dx / dist
        vy = target_speed * dy / dist
        
        return (vx, vy)
    
    def plan_trajectory(self, start: Tuple[float, float],
                       goal: Tuple[float, float],
                       steps: int = 10) -> List[Tuple[float, float]]:
        """
        Plan straight-line trajectory.
        
        Args:
            start: Start position
            goal: Goal position
            steps: Number of steps
        
        Returns:
            Waypoints
        """
        waypoints = [start]
        
        for i in range(1, steps + 1):
            t = i / steps
            x = start[0] + t * (goal[0] - start[0])
            y = start[1] + t * (goal[1] - start[1])
            waypoints.append((x, y))
        
        return waypoints


class ObstacleAvoidance:
    """
    Unified obstacle avoidance controller.
    """
    
    def __init__(self):
        self.potential = PotentialFieldPlanner()
        self.collision = CollisionDetector()
        self.planner = LocalPlanner()
        self.obstacles: List[Obstacle] = []
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add obstacle."""
        self.obstacles.append(obstacle)
    
    def remove_obstacle(self, obstacle_id: str):
        """Remove obstacle."""
        self.obstacles = [o for o in self.obstacles if o.obstacle_id != obstacle_id]
    
    def navigate(self, position: Tuple[float, float],
                goal: Tuple[float, float],
                own_radius_m: float = 0.5,
                dt_s: float = 0.1) -> Tuple[float, float]:
        """
        Navigate toward goal avoiding obstacles.
        
        Args:
            position: Current position
            goal: Goal position
            own_radius_m: Robot radius
            dt_s: Time step
        
        Returns:
            Next position
        """
        # Check collision
        if self.collision.check_collision(position, own_radius_m, self.obstacles):
            # Use potential field to escape
            return self.potential.plan_step(position, goal, self.obstacles, 0.2)
        
        # Plan using potential field
        next_pos = self.potential.plan_step(position, goal, self.obstacles, 0.3)
        
        # Check if new position is collision-free
        if not self.collision.check_collision(next_pos, own_radius_m, self.obstacles):
            return next_pos
        
        # Fallback: plan slower
        return self.potential.plan_step(position, goal, self.obstacles, 0.1)
    
    def avoidance_summary(self) -> Dict:
        """Get avoidance summary."""
        return {
            "obstacles": len(self.obstacles),
            "static": sum(1 for o in self.obstacles if o.obstacle_type == ObstacleType.STATIC),
            "dynamic": sum(1 for o in self.obstacles if o.obstacle_type == ObstacleType.DYNAMIC)
        }
