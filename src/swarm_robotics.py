"""
Swarm Robotics Module
Boid flocking, consensus algorithms,
task allocation, and formation control for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RobotState:
    """Robot state in 2D."""
    x: float
    y: float
    vx: float
    vy: float


class BoidFlocking:
    """
    Reynolds boid flocking behavior.
    """
    
    def __init__(self, separation_weight: float = 1.5,
                 alignment_weight: float = 1.0,
                 cohesion_weight: float = 1.0,
                 neighbor_radius: float = 5.0):
        """
        Args:
            separation_weight: Separation coefficient
            alignment_weight: Alignment coefficient
            cohesion_weight: Cohesion coefficient
            neighbor_radius: Perception radius
        """
        self.w_sep = separation_weight
        self.w_ali = alignment_weight
        self.w_coh = cohesion_weight
        self.radius = neighbor_radius
    
    def separation(self, robot: RobotState,
                  neighbors: List[RobotState]) -> Tuple[float, float]:
        """
        Compute separation force.
        
        Args:
            robot: Current robot
            neighbors: Neighboring robots
        
        Returns:
            (fx, fy) force
        """
        fx, fy = 0.0, 0.0
        count = 0
        for n in neighbors:
            dx = robot.x - n.x
            dy = robot.y - n.y
            dist = math.sqrt(dx**2 + dy**2)
            if 0 < dist < self.radius:
                fx += dx / dist
                fy += dy / dist
                count += 1
        if count > 0:
            fx = fx / count * self.w_sep
            fy = fy / count * self.w_sep
        return (fx, fy)
    
    def alignment(self, robot: RobotState,
                 neighbors: List[RobotState]) -> Tuple[float, float]:
        """
        Compute alignment force.
        
        Args:
            robot: Current robot
            neighbors: Neighboring robots
        
        Returns:
            (fx, fy) force
        """
        fx, fy = 0.0, 0.0
        count = 0
        for n in neighbors:
            dx = n.x - robot.x
            dy = n.y - robot.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < self.radius:
                fx += n.vx - robot.vx
                fy += n.vy - robot.vy
                count += 1
        if count > 0:
            fx = fx / count * self.w_ali
            fy = fy / count * self.w_ali
        return (fx, fy)
    
    def cohesion(self, robot: RobotState,
                neighbors: List[RobotState]) -> Tuple[float, float]:
        """
        Compute cohesion force.
        
        Args:
            robot: Current robot
            neighbors: Neighboring robots
        
        Returns:
            (fx, fy) force
        """
        cx, cy = 0.0, 0.0
        count = 0
        for n in neighbors:
            dx = n.x - robot.x
            dy = n.y - robot.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < self.radius:
                cx += n.x
                cy += n.y
                count += 1
        if count > 0:
            cx /= count
            cy /= count
            return ((cx - robot.x) * self.w_coh / count,
                    (cy - robot.y) * self.w_coh / count)
        return (0.0, 0.0)
    
    def flocking_velocity(self, robot: RobotState,
                         neighbors: List[RobotState],
                         max_speed: float = 2.0) -> Tuple[float, float]:
        """
        Compute flocking velocity.
        
        Args:
            robot: Current robot
            neighbors: Neighbors
            max_speed: Speed limit
        
        Returns:
            (vx, vy)
        """
        sep = self.separation(robot, neighbors)
        ali = self.alignment(robot, neighbors)
        coh = self.cohesion(robot, neighbors)
        vx = robot.vx + sep[0] + ali[0] + coh[0]
        vy = robot.vy + sep[1] + ali[1] + coh[1]
        speed = math.sqrt(vx**2 + vy**2)
        if speed > max_speed and speed > 0:
            vx = vx / speed * max_speed
            vy = vy / speed * max_speed
        return (vx, vy)


class ConsensusAlgorithms:
    """
    Distributed consensus algorithms.
    """
    
    def __init__(self):
        pass
    
    def average_consensus(self, values: List[float],
                         adjacency: List[List[int]],
                         iterations: int = 10) -> List[float]:
        """
        Run average consensus.
        
        Args:
            values: Initial values
            adjacency: Network adjacency
            iterations: Iterations
        
        Returns:
            Final values
        """
        if not values:
            return []
        current = list(values)
        n = len(current)
        for _ in range(iterations):
            new_values = []
            for i in range(n):
                neighbor_sum = sum(current[j] for j in range(n) if adjacency[i][j] == 1)
                degree = sum(adjacency[i])
                if degree > 0:
                    new_values.append((current[i] + neighbor_sum) / (degree + 1))
                else:
                    new_values.append(current[i])
            current = new_values
        return current
    
    def consensus_value(self, values: List[float]) -> float:
        """
        Compute theoretical consensus value.
        
        Args:
            values: Values
        
        Returns:
            Average
        """
        if not values:
            return 0.0
        return sum(values) / len(values)


class TaskAllocation:
    """
    Multi-robot task allocation.
    """
    
    def __init__(self):
        pass
    
    def greedy_allocation(self, robots: List[RobotState],
                         tasks: List[Tuple[float, float]]) -> Dict[int, int]:
        """
        Greedy nearest-task allocation.
        
        Args:
            robots: Robot states
            tasks: Task positions
        
        Returns:
            Robot -> task mapping
        """
        allocation = {}
        assigned_tasks = set()
        for i, robot in enumerate(robots):
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
                allocation[i] = best_task
                assigned_tasks.add(best_task)
        return allocation
    
    def total_travel_distance(self, robots: List[RobotState],
                             allocation: Dict[int, int],
                             tasks: List[Tuple[float, float]]) -> float:
        """
        Compute total travel distance.
        
        Args:
            robots: Robot states
            allocation: Allocation
            tasks: Task positions
        
        Returns:
            Total distance
        """
        total = 0.0
        for robot_idx, task_idx in allocation.items():
            robot = robots[robot_idx]
            task = tasks[task_idx]
            total += math.sqrt((robot.x - task[0])**2 + (robot.y - task[1])**2)
        return total


class FormationControl:
    """
    Formation control for robot swarms.
    """
    
    def __init__(self):
        pass
    
    def desired_position(self, center: Tuple[float, float],
                        formation_angle: float,
                        radius: float,
                        robot_index: int,
                        total_robots: int) -> Tuple[float, float]:
        """
        Compute desired position in circular formation.
        
        Args:
            center: Formation center
            formation_angle: Starting angle
            radius: Formation radius
            robot_index: Robot index
            total_robots: Total robots
        
        Returns:
            (x, y) desired position
        """
        if total_robots <= 0:
            return center
        angle = formation_angle + 2.0 * math.pi * robot_index / total_robots
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        return (x, y)
    
    def formation_error(self, robot: RobotState,
                       desired: Tuple[float, float]) -> float:
        """
        Compute distance to desired position.
        
        Args:
            robot: Robot state
            desired: Desired position
        
        Returns:
            Error distance
        """
        return math.sqrt((robot.x - desired[0])**2 + (robot.y - desired[1])**2)


class SwarmRobotics:
    """
    Unified swarm robotics controller.
    """
    
    def __init__(self):
        self.flocking = BoidFlocking()
        self.consensus = ConsensusAlgorithms()
        self.task = TaskAllocation()
        self.formation = FormationControl()
    
    def swarm_summary(self) -> Dict:
        """Get summary."""
        return {
            "behaviors": ["flocking", "consensus", "task_allocation", "formation"],
            "outputs": ["velocity", "consensus_value", "allocation", "formation_error"]
        }
