"""
Motion Planner Module
RRT, A*, and sampling-based path planning for
autonomous spacecraft navigation and robotics.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable, Set
from dataclasses import dataclass, field


@dataclass
class Node:
    """A node in the planning graph."""
    x: float
    y: float
    z: float = 0.0
    parent: Optional["Node"] = None
    cost: float = 0.0


@dataclass
class Obstacle:
    """A spherical obstacle."""
    x: float
    y: float
    z: float
    radius: float
    
    def contains(self, x: float, y: float, z: float = 0.0) -> bool:
        """Check if point is inside obstacle."""
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z
        return math.sqrt(dx*dx + dy*dy + dz*dz) <= self.radius


class AStarPlanner:
    """
    A* path planner on a grid.
    """
    
    def __init__(self, grid_size: float = 1.0):
        """
        Args:
            grid_size: Grid cell size
        """
        self.grid_size = grid_size
        self.obstacles: List[Obstacle] = []
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add obstacle."""
        self.obstacles.append(obstacle)
    
    def is_collision(self, x: float, y: float, z: float = 0.0) -> bool:
        """Check if position collides with obstacle."""
        for obs in self.obstacles:
            if obs.contains(x, y, z):
                return True
        return False
    
    def heuristic(self, a: Tuple[float, float, float],
                 b: Tuple[float, float, float]) -> float:
        """Euclidean heuristic."""
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)
    
    def get_neighbors(self, pos: Tuple[float, float, float]
                     ) -> List[Tuple[float, float, float]]:
        """Get neighboring grid positions."""
        x, y, z = pos
        neighbors = []
        for dx in [-self.grid_size, 0, self.grid_size]:
            for dy in [-self.grid_size, 0, self.grid_size]:
                for dz in [-self.grid_size, 0, self.grid_size]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if not self.is_collision(nx, ny, nz):
                        neighbors.append((nx, ny, nz))
        return neighbors
    
    def plan(self, start: Tuple[float, float, float],
            goal: Tuple[float, float, float],
            max_iterations: int = 10000) -> Optional[List[Tuple[float, float, float]]]:
        """
        Plan path using A*.
        
        Args:
            start: Start position
            goal: Goal position
            max_iterations: Maximum search iterations
        
        Returns:
            Path or None
        """
        if self.is_collision(*start) or self.is_collision(*goal):
            return None
        
        open_set = {start}
        came_from: Dict[Tuple, Tuple] = {}
        g_score = {start: 0.0}
        f_score = {start: self.heuristic(start, goal)}
        
        iterations = 0
        while open_set and iterations < max_iterations:
            iterations += 1
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if self.heuristic(current, goal) < self.grid_size:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                path[-1] = goal
                return path
            
            open_set.remove(current)
            
            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + self.heuristic(current, neighbor)
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    open_set.add(neighbor)
        
        return None


class RRTPlanner:
    """
    Rapidly-exploring Random Tree planner.
    """
    
    def __init__(self, step_size: float = 1.0,
                 max_iterations: int = 10000,
                 goal_bias: float = 0.1,
                 seed: Optional[int] = None):
        """
        Args:
            step_size: Extension step size
            max_iterations: Maximum iterations
            goal_bias: Probability of sampling goal
            seed: Random seed
        """
        self.step_size = step_size
        self.max_iterations = max_iterations
        self.goal_bias = goal_bias
        self.rng = random.Random(seed)
        self.obstacles: List[Obstacle] = []
        self.nodes: List[Node] = []
        self.bounds: Tuple[float, float, float, float, float, float] = (-10, 10, -10, 10, -10, 10)
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add obstacle."""
        self.obstacles.append(obstacle)
    
    def set_bounds(self, x_min: float, x_max: float,
                  y_min: float, y_max: float,
                  z_min: float = -10, z_max: float = 10):
        """Set sampling bounds."""
        self.bounds = (x_min, x_max, y_min, y_max, z_min, z_max)
    
    def is_collision(self, x: float, y: float, z: float = 0.0) -> bool:
        """Check collision."""
        for obs in self.obstacles:
            if obs.contains(x, y, z):
                return True
        return False
    
    def distance(self, a: Node, b: Node) -> float:
        """Distance between nodes."""
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (a.z-b.z)**2)
    
    def nearest(self, x: float, y: float, z: float) -> Node:
        """Find nearest node."""
        target = Node(x, y, z)
        return min(self.nodes, key=lambda n: self.distance(n, target))
    
    def steer(self, from_node: Node, to_x: float, to_y: float, to_z: float) -> Node:
        """Steer from node toward target."""
        dx = to_x - from_node.x
        dy = to_y - from_node.y
        dz = to_z - from_node.z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist < self.step_size:
            return Node(to_x, to_y, to_z, parent=from_node)
        
        ratio = self.step_size / dist
        return Node(
            from_node.x + dx * ratio,
            from_node.y + dy * ratio,
            from_node.z + dz * ratio,
            parent=from_node
        )
    
    def is_collision_free(self, from_node: Node, to_node: Node) -> bool:
        """Check if path between nodes is collision-free."""
        # Simple check: sample points along line
        steps = max(1, int(self.distance(from_node, to_node) / (self.step_size * 0.5)))
        for i in range(steps + 1):
            t = i / steps
            x = from_node.x + t * (to_node.x - from_node.x)
            y = from_node.y + t * (to_node.y - from_node.y)
            z = from_node.z + t * (to_node.z - from_node.z)
            if self.is_collision(x, y, z):
                return False
        return True
    
    def sample(self, goal: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Sample random point with goal bias."""
        if self.rng.random() < self.goal_bias:
            return goal
        
        x = self.rng.uniform(self.bounds[0], self.bounds[1])
        y = self.rng.uniform(self.bounds[2], self.bounds[3])
        z = self.rng.uniform(self.bounds[4], self.bounds[5])
        return (x, y, z)
    
    def plan(self, start: Tuple[float, float, float],
            goal: Tuple[float, float, float],
            goal_tolerance: float = 0.5
            ) -> Optional[List[Tuple[float, float, float]]]:
        """
        Plan path using RRT.
        
        Args:
            start: Start position
            goal: Goal position
            goal_tolerance: Distance to goal to consider reached
        
        Returns:
            Path or None
        """
        self.nodes = []
        start_node = Node(*start)
        self.nodes.append(start_node)
        
        for _ in range(self.max_iterations):
            # Sample
            sample_point = self.sample(goal)
            
            # Find nearest
            nearest_node = self.nearest(*sample_point)
            
            # Steer
            new_node = self.steer(nearest_node, *sample_point)
            
            # Check collision
            if self.is_collision(new_node.x, new_node.y, new_node.z):
                continue
            
            if not self.is_collision_free(nearest_node, new_node):
                continue
            
            # Add node
            new_node.parent = nearest_node
            new_node.cost = nearest_node.cost + self.distance(nearest_node, new_node)
            self.nodes.append(new_node)
            
            # Check if reached goal
            if self.distance(new_node, Node(*goal)) < goal_tolerance:
                # Reconstruct path
                path = []
                current = new_node
                while current is not None:
                    path.append((current.x, current.y, current.z))
                    current = current.parent
                path.reverse()
                path[-1] = goal
                return path
        
        return None


class MotionPlanner:
    """
    Unified motion planning controller.
    """
    
    def __init__(self):
        self.astar = AStarPlanner()
        self.rrt = RRTPlanner()
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add obstacle to all planners."""
        self.astar.add_obstacle(obstacle)
        self.rrt.add_obstacle(obstacle)
    
    def plan_astar(self, start: Tuple[float, float, float],
                  goal: Tuple[float, float, float]) -> Optional[List[Tuple[float, float, float]]]:
        """
        Plan with A*.
        
        Args:
            start: Start position
            goal: Goal position
        
        Returns:
            Path or None
        """
        return self.astar.plan(start, goal)
    
    def plan_rrt(self, start: Tuple[float, float, float],
                goal: Tuple[float, float, float],
                bounds: Optional[Tuple[float, float, float, float, float, float]] = None
                ) -> Optional[List[Tuple[float, float, float]]]:
        """
        Plan with RRT.
        
        Args:
            start: Start position
            goal: Goal position
            bounds: Sampling bounds
        
        Returns:
            Path or None
        """
        if bounds:
            self.rrt.set_bounds(*bounds)
        return self.rrt.plan(start, goal)
    
    def path_length(self, path: List[Tuple[float, float, float]]) -> float:
        """Compute path length."""
        length = 0.0
        for i in range(len(path) - 1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            dz = path[i+1][2] - path[i][2]
            length += math.sqrt(dx*dx + dy*dy + dz*dz)
        return length
    
    def planner_summary(self) -> Dict:
        """Get planner summary."""
        return {
            "astar_obstacles": len(self.astar.obstacles),
            "rrt_obstacles": len(self.rrt.obstacles),
            "rrt_nodes": len(self.rrt.nodes)
        }
