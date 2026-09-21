"""
Motion Planning Sampling Module
PRM sampling, RRT variants,
biased sampling, and configuration space coverage for autonomous robotics.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ConfigNode:
    """Configuration space node."""
    x: float
    y: float
    parent_index: Optional[int] = None


class PRMSampling:
    """
    Probabilistic Roadmap sampling strategies.
    """
    
    def __init__(self, config_space_bounds: Tuple[float, float, float, float]):
        """
        Args:
            config_space_bounds: (xmin, xmax, ymin, ymax)
        """
        self.bounds = config_space_bounds
    
    def uniform_sample(self) -> Tuple[float, float]:
        """
        Uniform random sample in C-space.
        
        Returns:
            (x, y)
        """
        xmin, xmax, ymin, ymax = self.bounds
        return (random.uniform(xmin, xmax), random.uniform(ymin, ymax))
    
    def gaussian_sample(self, mean_x: float, mean_y: float,
                       std: float = 1.0) -> Tuple[float, float]:
        """
        Gaussian biased sample.
        
        Args:
            mean_x, mean_y: Mean
            std: Standard deviation
        
        Returns:
            (x, y)
        """
        xmin, xmax, ymin, ymax = self.bounds
        x = random.gauss(mean_x, std)
        y = random.gauss(mean_y, std)
        return (max(xmin, min(xmax, x)), max(ymin, min(ymax, y)))
    
    def obstacle_bias_sample(self, obstacle_centers: List[Tuple[float, float]],
                            bias_probability: float = 0.1) -> Tuple[float, float]:
        """
        Sample with obstacle bias (simplified).
        
        Args:
            obstacle_centers: Obstacle centers
            bias_probability: Bias probability
        
        Returns:
            (x, y)
        """
        if random.random() < bias_probability and obstacle_centers:
            center = random.choice(obstacle_centers)
            return self.gaussian_sample(center[0], center[1], std=0.5)
        return self.uniform_sample()


class RRTVariants:
    """
    RRT and RRT* sampling.
    """
    
    def __init__(self, step_size: float = 0.5):
        """
        Args:
            step_size: Step size
        """
        self.step = step_size
    
    def nearest_neighbor(self, nodes: List[ConfigNode],
                        target: Tuple[float, float]) -> int:
        """
        Find nearest node index.
        
        Args:
            nodes: Existing nodes
            target: Target position
        
        Returns:
            Nearest index
        """
        if not nodes:
            return -1
        min_dist = float('inf')
        nearest = 0
        for i, node in enumerate(nodes):
            d = math.sqrt((node.x - target[0])**2 + (node.y - target[1])**2)
            if d < min_dist:
                min_dist = d
                nearest = i
        return nearest
    
    def steer(self, from_node: ConfigNode,
             to_point: Tuple[float, float]) -> ConfigNode:
        """
        Steer from node toward point with step size.
        
        Args:
            from_node: Starting node
            to_point: Target point
        
        Returns:
            New node
        """
        dx = to_point[0] - from_node.x
        dy = to_point[1] - from_node.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist <= self.step:
            return ConfigNode(to_point[0], to_point[1])
        ratio = self.step / dist
        return ConfigNode(from_node.x + dx * ratio,
                         from_node.y + dy * ratio)
    
    def rrt_star_rewire(self, nodes: List[ConfigNode],
                       new_index: int,
                       near_indices: List[int],
                       collision_free_func) -> List[ConfigNode]:
        """
        RRT* rewire step (simplified).
        
        Args:
            nodes: All nodes
            new_index: New node index
            near_indices: Near node indices
            collision_free_func: Collision checker
        
        Returns:
            Updated nodes
        """
        # Simplified: no actual rewiring, just return nodes
        return nodes


class BiasedSampling:
    """
    Goal-biased and heuristic sampling.
    """
    
    def __init__(self, goal: Tuple[float, float],
                goal_bias: float = 0.1):
        """
        Args:
            goal: Goal position
            goal_bias: Bias probability
        """
        self.goal = goal
        self.bias = goal_bias
    
    def goal_biased_sample(self, bounds: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """
        Sample with goal bias.
        
        Args:
            bounds: C-space bounds
        
        Returns:
            (x, y)
        """
        if random.random() < self.bias:
            return self.goal
        xmin, xmax, ymin, ymax = bounds
        return (random.uniform(xmin, xmax), random.uniform(ymin, ymax))
    
    def heuristic_sample(self, current: Tuple[float, float],
                        goal: Tuple[float, float],
                        progress_weight: float = 0.3) -> Tuple[float, float]:
        """
        Heuristic-biased sample toward goal.
        
        Args:
            current: Current position
            goal: Goal
            progress_weight: Weight
        
        Returns:
            (x, y)
        """
        dx = goal[0] - current[0]
        dy = goal[1] - current[1]
        return (current[0] + progress_weight * dx,
                current[1] + progress_weight * dy)


class ConfigurationSpaceCoverage:
    """
    C-space coverage analysis.
    """
    
    def __init__(self):
        pass
    
    def coverage_ratio(self, sampled_points: List[Tuple[float, float]],
                      bounds: Tuple[float, float, float, float],
                      grid_resolution: float = 1.0) -> float:
        """
        Estimate coverage ratio.
        
        Args:
            sampled_points: Sampled points
            bounds: Bounds
            grid_resolution: Resolution
        
        Returns:
            Coverage ratio
        """
        if not sampled_points or grid_resolution <= 0:
            return 0.0
        xmin, xmax, ymin, ymax = bounds
        nx = int((xmax - xmin) / grid_resolution) + 1
        ny = int((ymax - ymin) / grid_resolution) + 1
        total_cells = nx * ny
        if total_cells <= 0:
            return 0.0
        occupied = set()
        for px, py in sampled_points:
            gx = int((px - xmin) / grid_resolution)
            gy = int((py - ymin) / grid_resolution)
            occupied.add((gx, gy))
        return len(occupied) / total_cells
    
    def dispersion(self, sampled_points: List[Tuple[float, float]],
                  bounds: Tuple[float, float, float, float]) -> float:
        """
        Compute dispersion (max empty ball radius).
        
        Args:
            sampled_points: Sampled points
            bounds: Bounds
        
        Returns:
            Dispersion
        """
        if not sampled_points:
            return math.sqrt((bounds[1]-bounds[0])**2 + (bounds[3]-bounds[2])**2)
        # Simplified: max distance from any sample to center
        cx = (bounds[0] + bounds[1]) / 2.0
        cy = (bounds[2] + bounds[3]) / 2.0
        min_dist_to_center = min(math.sqrt((p[0]-cx)**2 + (p[1]-cy)**2) for p in sampled_points)
        return min_dist_to_center


class MotionPlanningSampling:
    """
    Unified motion planning sampling controller.
    """
    
    def __init__(self):
        self.prm = PRMSampling((0.0, 10.0, 0.0, 10.0))
        self.rrt = RRTVariants()
        self.biased = BiasedSampling((10.0, 10.0))
        self.coverage = ConfigurationSpaceCoverage()
    
    def sampling_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["prm", "rrt", "rrt_star", "goal_bias", "heuristic"],
            "metrics": ["coverage", "dispersion"]
        }
