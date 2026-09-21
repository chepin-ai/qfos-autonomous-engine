"""
SLAM Module
Simultaneous Localization and Mapping
Particle filter SLAM, occupancy grid, landmark detection,
and pose estimation for autonomous robotics.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Pose:
    """Robot pose."""
    x: float
    y: float
    theta: float


@dataclass
class Landmark:
    """Detected landmark."""
    id: int
    x: float
    y: float


class OccupancyGrid:
    """
    2D occupancy grid map.
    """
    
    def __init__(self, width: int = 100, height: int = 100,
                 resolution: float = 0.1):
        """
        Args:
            width: Grid width
            height: Grid height
            resolution: Meters per cell
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        self.grid = [[0.5] * width for _ in range(height)]
    
    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world to grid coordinates.
        
        Args:
            x: World x
            y: World y
        
        Returns:
            (grid_x, grid_y)
        """
        gx = int(x / self.resolution + self.width / 2)
        gy = int(y / self.resolution + self.height / 2)
        gx = max(0, min(self.width - 1, gx))
        gy = max(0, min(self.height - 1, gy))
        return (gx, gy)
    
    def update_cell(self, x: float, y: float,
                   occupied: bool):
        """
        Update cell occupancy.
        
        Args:
            x: World x
            y: World y
            occupied: Whether occupied
        """
        gx, gy = self.world_to_grid(x, y)
        prior = self.grid[gy][gx]
        p_occ = 0.7 if occupied else 0.3
        self.grid[gy][gx] = (p_occ * prior) / (p_occ * prior + (1.0 - p_occ) * (1.0 - prior))
    
    def is_occupied(self, x: float, y: float,
                   threshold: float = 0.6) -> bool:
        """
        Check if cell is occupied.
        
        Args:
            x: World x
            y: World y
            threshold: Occupancy threshold
        
        Returns:
            Whether occupied
        """
        gx, gy = self.world_to_grid(x, y)
        return self.grid[gy][gx] > threshold


class ParticleFilterSLAM:
    """
    Particle filter SLAM.
    """
    
    def __init__(self, num_particles: int = 100):
        """
        Args:
            num_particles: Number of particles
        """
        self.num_particles = num_particles
        self.particles: List[Pose] = []
        self.weights: List[float] = []
        self.landmarks: Dict[int, Landmark] = {}
        self._init_particles()
    
    def _init_particles(self):
        """Initialize particles."""
        for _ in range(self.num_particles):
            self.particles.append(Pose(0.0, 0.0, 0.0))
            self.weights.append(1.0 / self.num_particles)
    
    def predict(self, dx: float, dy: float,
                dtheta: float,
                noise_std: float = 0.1):
        """
        Prediction step with motion model.
        
        Args:
            dx: Forward motion
            dy: Lateral motion
            dtheta: Rotation
            noise_std: Motion noise
        """
        for i, p in enumerate(self.particles):
            nx = p.x + dx + random.gauss(0.0, noise_std)
            ny = p.y + dy + random.gauss(0.0, noise_std)
            nt = p.theta + dtheta + random.gauss(0.0, noise_std)
            self.particles[i] = Pose(nx, ny, nt)
    
    def observe_landmark(self, landmark_id: int,
                        measured_x: float,
                        measured_y: float,
                        measurement_noise: float = 0.5):
        """
        Update from landmark observation.
        
        Args:
            landmark_id: Landmark ID
            measured_x: Measured x
            measured_y: Measured y
            measurement_noise: Measurement noise std
        """
        if landmark_id not in self.landmarks:
            # Initialize landmark from first observation
            self.landmarks[landmark_id] = Landmark(
                landmark_id, measured_x, measured_y
            )
        
        lm = self.landmarks[landmark_id]
        
        for i, p in enumerate(self.particles):
            # Expected measurement from particle pose
            expected_x = lm.x - p.x
            expected_y = lm.y - p.y
            
            # Likelihood
            error_sq = ((measured_x - expected_x) ** 2 +
                       (measured_y - expected_y) ** 2)
            likelihood = math.exp(-error_sq / (2.0 * measurement_noise ** 2))
            self.weights[i] *= likelihood
        
        # Normalize
        total = sum(self.weights)
        if total > 0:
            self.weights = [w / total for w in self.weights]
    
    def resample(self):
        """Resample particles."""
        new_particles = []
        cumsum = []
        s = 0.0
        for w in self.weights:
            s += w
            cumsum.append(s)
        
        for _ in range(self.num_particles):
            u = random.random()
            for i, c in enumerate(cumsum):
                if u <= c:
                    p = self.particles[i]
                    new_particles.append(Pose(p.x, p.y, p.theta))
                    break
        
        self.particles = new_particles
        self.weights = [1.0 / self.num_particles] * self.num_particles
    
    def estimated_pose(self) -> Pose:
        """
        Compute weighted mean pose.
        
        Returns:
            Estimated pose
        """
        x = sum(p.x * w for p, w in zip(self.particles, self.weights))
        y = sum(p.y * w for p, w in zip(self.particles, self.weights))
        
        # Circular mean for theta
        sin_sum = sum(math.sin(p.theta) * w for p, w in zip(self.particles, self.weights))
        cos_sum = sum(math.cos(p.theta) * w for p, w in zip(self.particles, self.weights))
        theta = math.atan2(sin_sum, cos_sum)
        
        return Pose(x, y, theta)


class ScanMatcher:
    """
    Scan matching for SLAM.
    """
    
    def __init__(self):
        pass
    
    def icp_step(self, source: List[Tuple[float, float]],
                target: List[Tuple[float, float]]) -> Tuple[float, float, float]:
        """
        One ICP iteration.
        
        Args:
            source: Source points
            target: Target points
        
        Returns:
            (dx, dy, dtheta)
        """
        if not source or not target:
            return (0.0, 0.0, 0.0)
        
        # Centroids
        cx_s = sum(p[0] for p in source) / len(source)
        cy_s = sum(p[1] for p in source) / len(source)
        cx_t = sum(p[0] for p in target) / len(target)
        cy_t = sum(p[1] for p in target) / len(target)
        
        dx = cx_t - cx_s
        dy = cy_t - cy_s
        
        return (dx, dy, 0.0)


class SLAM:
    """
    Unified SLAM controller.
    """
    
    def __init__(self):
        self.grid = OccupancyGrid()
        self.pf_slam = ParticleFilterSLAM()
        self.scan_matcher = ScanMatcher()
    
    def slam_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["particle_filter", "occupancy_grid", "scan_matching"],
            "particles": self.pf_slam.num_particles,
            "landmarks": len(self.pf_slam.landmarks)
        }
