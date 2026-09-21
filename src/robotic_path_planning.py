"""
Robotic Path Planning Module
A* search, RRT, obstacle avoidance, trajectory smoothing,
and path optimization for autonomous robotics.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class Point2D:
    """2D point."""
    x: float
    y: float
    
    def distance(self, other: 'Point2D') -> float:
        """Euclidean distance."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class AStarPlanner:
    """
    A* path planning.
    """
    
    def __init__(self, grid_size: float = 1.0):
        """
        Args:
            grid_size: Grid cell size
        """
        self.grid_size = grid_size
        self.obstacles: Set[Tuple[int, int]] = set()
    
    def add_obstacle(self, x: float, y: float):
        """
        Add obstacle.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        gx = int(x / self.grid_size)
        gy = int(y / self.grid_size)
        self.obstacles.add((gx, gy))
    
    def heuristic(self, a: Tuple[int, int],
                 b: Tuple[int, int]) -> float:
        """
        Compute heuristic.
        
        Args:
            a: Point A
            b: Point B
        
        Returns:
            Heuristic distance
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    
    def neighbors(self, node: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get neighbors.
        
        Args:
            node: Current node
        
        Returns:
            Neighbors
        """
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]
        result = []
        for dx, dy in deltas:
            n = (node[0] + dx, node[1] + dy)
            if n not in self.obstacles:
                result.append(n)
        return result
    
    def plan(self, start: Point2D, goal: Point2D) -> List[Point2D]:
        """
        Plan path using A*.
        
        Args:
            start: Start point
            goal: Goal point
        
        Returns:
            Path
        """
        s = (int(start.x / self.grid_size), int(start.y / self.grid_size))
        g = (int(goal.x / self.grid_size), int(goal.y / self.grid_size))
        
        open_set = {s}
        came_from = {}
        g_score = {s: 0.0}
        f_score = {s: self.heuristic(s, g)}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == g:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return [Point2D(p[0] * self.grid_size, p[1] * self.grid_size) for p in path]
            
            open_set.remove(current)
            
            for neighbor in self.neighbors(current):
                tentative = g_score[current] + self.heuristic(current, neighbor)
                
                if tentative < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f_score[neighbor] = tentative + self.heuristic(neighbor, g)
                    open_set.add(neighbor)
        
        return []


class RRTPlanner:
    """
    Rapidly-exploring Random Tree planner.
    """
    
    def __init__(self, max_iterations: int = 1000,
                 step_size: float = 1.0):
        """
        Args:
            max_iterations: Max iterations
            step_size: Step size
        """
        self.max_iter = max_iterations
        self.step_size = step_size
        self.nodes: List[Point2D] = []
        self.parents: Dict[int, int] = {}
        self.obstacles: List[Tuple[Point2D, float]] = []
    
    def add_obstacle(self, center: Point2D, radius: float):
        """
        Add circular obstacle.
        
        Args:
            center: Center
            radius: Radius
        """
        self.obstacles.append((center, radius))
    
    def collision(self, point: Point2D) -> bool:
        """
        Check collision.
        
        Args:
            point: Point
        
        Returns:
            True if collision
        """
        for center, radius in self.obstacles:
            if point.distance(center) < radius:
                return True
        return False
    
    def nearest(self, point: Point2D) -> int:
        """
        Find nearest node.
        
        Args:
            point: Point
        
        Returns:
            Index of nearest node
        """
        return min(range(len(self.nodes)), key=lambda i: self.nodes[i].distance(point))
    
    def steer(self, from_point: Point2D, to_point: Point2D) -> Point2D:
        """
        Steer from one point toward another.
        
        Args:
            from_point: From
            to_point: To
        
        Returns:
            New point
        """
        dist = from_point.distance(to_point)
        if dist < self.step_size:
            return to_point
        
        ratio = self.step_size / dist
        return Point2D(
            from_point.x + (to_point.x - from_point.x) * ratio,
            from_point.y + (to_point.y - from_point.y) * ratio
        )
    
    def plan(self, start: Point2D, goal: Point2D) -> List[Point2D]:
        """
        Plan path using RRT.
        
        Args:
            start: Start
            goal: Goal
        
        Returns:
            Path
        """
        self.nodes = [start]
        self.parents = {0: -1}
        
        for _ in range(self.max_iter):
            random_point = Point2D(
                random.uniform(min(start.x, goal.x) - 5, max(start.x, goal.x) + 5),
                random.uniform(min(start.y, goal.y) - 5, max(start.y, goal.y) + 5)
            )
            
            nearest_idx = self.nearest(random_point)
            nearest_point = self.nodes[nearest_idx]
            new_point = self.steer(nearest_point, random_point)
            
            if not self.collision(new_point):
                new_idx = len(self.nodes)
                self.nodes.append(new_point)
                self.parents[new_idx] = nearest_idx
                
                if new_point.distance(goal) < self.step_size:
                    path = [goal]
                    current = new_idx
                    while current >= 0:
                        path.append(self.nodes[current])
                        current = self.parents.get(current, -1)
                    path.reverse()
                    return path
        
        return []


class PathSmoother:
    """
    Smooth trajectories.
    """
    
    def __init__(self):
        pass
    
    def path_length(self, path: List[Point2D]) -> float:
        """
        Compute path length.
        
        Args:
            path: Path
        
        Returns:
            Length
        """
        length = 0.0
        for i in range(len(path) - 1):
            length += path[i].distance(path[i + 1])
        return length
    
    def smooth(self, path: List[Point2D],
              iterations: int = 5) -> List[Point2D]:
        """
        Smooth path using moving average.
        
        Args:
            path: Path
            iterations: Iterations
        
        Returns:
            Smoothed path
        """
        if len(path) < 3:
            return path
        
        current = path[:]
        for _ in range(iterations):
            new_path = [current[0]]
            for i in range(1, len(current) - 1):
                new_x = (current[i - 1].x + current[i].x + current[i + 1].x) / 3.0
                new_y = (current[i - 1].y + current[i].y + current[i + 1].y) / 3.0
                new_path.append(Point2D(new_x, new_y))
            new_path.append(current[-1])
            current = new_path
        
        return current


class RoboticPathPlanning:
    """
    Unified path planning controller.
    """
    
    def __init__(self):
        self.astar = AStarPlanner()
        self.rrt = RRTPlanner()
        self.smoother = PathSmoother()
    
    def plan(self, start: Point2D, goal: Point2D,
            method: str = "astar") -> List[Point2D]:
        """
        Plan path.
        
        Args:
            start: Start
            goal: Goal
            method: Method
        
        Returns:
            Path
        """
        if method == "astar":
            return self.astar.plan(start, goal)
        elif method == "rrt":
            return self.rrt.plan(start, goal)
        return []
    
    def rpp_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["astar", "rrt"],
            "obstacles_astar": len(self.astar.obstacles),
            "obstacles_rrt": len(self.rrt.obstacles)
        }
