"""
Collaborative Manipulation Module
Multi-robot task allocation, coordination,
consensus, and collision avoidance for autonomous collaborative robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RobotState:
    """Robot pose and status."""
    x: float
    y: float
    theta: float
    gripper_open: bool


class TaskAllocation:
    """
    Multi-robot task allocation.
    """
    
    def __init__(self):
        pass
    
    def nearest_robot(self, task_position: Tuple[float, float],
                     robot_states: List[RobotState]) -> int:
        """
        Find nearest robot to task.
        
        Args:
            task_position: Task location
            robot_states: Robot states
        
        Returns:
            Index of nearest robot
        """
        min_dist = float('inf')
        nearest = -1
        for i, rs in enumerate(robot_states):
            dist = math.sqrt((rs.x - task_position[0])**2 + (rs.y - task_position[1])**2)
            if dist < min_dist:
                min_dist = dist
                nearest = i
        return nearest
    
    def greedy_assignment(self, tasks: List[Tuple[float, float]],
                         robot_states: List[RobotState]) -> Dict[int, int]:
        """
        Greedy task-to-robot assignment.
        
        Args:
            tasks: Task positions
            robot_states: Robot states
        
        Returns:
            Robot index -> task index
        """
        assignment = {}
        assigned_tasks = set()
        for i, robot in enumerate(robot_states):
            best_task = -1
            best_dist = float('inf')
            for j, task in enumerate(tasks):
                if j in assigned_tasks:
                    continue
                dist = math.sqrt((robot.x - task[0])**2 + (robot.y - task[1])**2)
                if dist < best_dist:
                    best_dist = dist
                    best_task = j
            if best_task >= 0:
                assignment[i] = best_task
                assigned_tasks.add(best_task)
        return assignment


class CoordinationController:
    """
    Multi-robot motion coordination.
    """
    
    def __init__(self, safety_distance_m: float = 0.5):
        """
        Args:
            safety_distance_m: Minimum separation
        """
        self.d_safe = safety_distance_m
    
    def separation_constraint(self, robot1: RobotState,
                             robot2: RobotState) -> bool:
        """
        Check if robots satisfy separation.
        
        Args:
            robot1: First robot
            robot2: Second robot
        
        Returns:
            True if safe
        """
        dist = math.sqrt((robot1.x - robot2.x)**2 + (robot1.y - robot2.y)**2)
        return dist >= self.d_safe
    
    def velocity_adjustment(self, desired_velocity: float,
                           closest_obstacle_dist_m: float) -> float:
        """
        Adjust velocity based on proximity.
        
        Args:
            desired_velocity: Nominal velocity
            closest_obstacle_dist_m: Distance to obstacle
        
        Returns:
            Adjusted velocity
        """
        if closest_obstacle_dist_m < self.d_safe:
            return 0.0
        elif closest_obstacle_dist_m < 2.0 * self.d_safe:
            return desired_velocity * (closest_obstacle_dist_m - self.d_safe) / self.d_safe
        return desired_velocity


class ConsensusAlgorithm:
    """
    Distributed consensus for multi-robot systems.
    """
    
    def __init__(self, step_size: float = 0.1):
        """
        Args:
            step_size: Consensus step size
        """
        self.eps = step_size
    
    def average_consensus(self, values: List[float],
                         neighbor_indices: List[List[int]]) -> List[float]:
        """
        One step of average consensus.
        
        Args:
            values: Current values
            neighbor_indices: Neighbors for each robot
        
        Returns:
            Updated values
        """
        new_values = []
        for i, val in enumerate(values):
            neighbor_sum = sum(values[j] for j in neighbor_indices[i])
            degree = len(neighbor_indices[i])
            if degree > 0:
                update = val + self.eps * (neighbor_sum / degree - val)
            else:
                update = val
            new_values.append(update)
        return new_values
    
    def consensus_error(self, values: List[float]) -> float:
        """
        Compute deviation from average.
        
        Args:
            values: Current values
        
        Returns:
            Max deviation
        """
        if not values:
            return 0.0
        avg = sum(values) / len(values)
        return max(abs(v - avg) for v in values)


class CollisionAvoidance:
    """
    Reciprocal collision avoidance.
    """
    
    def __init__(self, collision_radius_m: float = 0.3):
        """
        Args:
            collision_radius_m: Collision radius
        """
        self.r = collision_radius_m
    
    def reciprocal_velocity(self, robot_pos: Tuple[float, float],
                           other_pos: Tuple[float, float],
                           preferred_vel: Tuple[float, float],
                           other_vel: Tuple[float, float]) -> Tuple[float, float]:
        """
        Compute reciprocal collision-free velocity.
        
        Args:
            robot_pos: This robot position
            other_pos: Other robot position
            preferred_vel: Preferred velocity
            other_vel: Other robot velocity
        
        Returns:
            Adjusted velocity
        """
        dx = other_pos[0] - robot_pos[0]
        dy = other_pos[1] - robot_pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 2.0 * self.r:
            return preferred_vel
        # Simplified: scale down if too close
        scale = max(0.0, (dist - self.r) / self.r)
        return (preferred_vel[0] * scale, preferred_vel[1] * scale)


class CollaborativeManipulation:
    """
    Unified collaborative manipulation controller.
    """
    
    def __init__(self):
        self.allocation = TaskAllocation()
        self.coordination = CoordinationController()
        self.consensus = ConsensusAlgorithm()
        self.avoidance = CollisionAvoidance()
    
    def collaborative_summary(self) -> Dict:
        """Get summary."""
        return {
            "capabilities": ["task_allocation", "coordination", "consensus", "collision_avoidance"],
            "robots": ["multi"]
        }
