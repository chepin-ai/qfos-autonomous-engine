"""
LiDAR Processor Module
Point cloud filtering, ground segmentation, and obstacle
detection for autonomous navigation.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class PointClass(Enum):
    """Point classification."""
    UNKNOWN = "unknown"
    GROUND = "ground"
    OBSTACLE = "obstacle"
    VEGETATION = "vegetation"
    STRUCTURE = "structure"


@dataclass
class Point3D:
    """3D point in space."""
    x: float
    y: float
    z: float
    intensity: float = 0.0
    classification: PointClass = PointClass.UNKNOWN


class PointCloudFilter:
    """
    Filter noise and outliers from point clouds.
    """
    
    def __init__(self, range_min_m: float = 0.5,
                 range_max_m: float = 100.0,
                 intensity_min: float = 0.0):
        """
        Args:
            range_min_m: Minimum range
            range_max_m: Maximum range
            intensity_min: Minimum intensity
        """
        self.range_min = range_min_m
        self.range_max = range_max_m
        self.intensity_min = intensity_min
    
    def _distance(self, point: Point3D) -> float:
        """Compute point distance from origin."""
        return math.sqrt(point.x**2 + point.y**2 + point.z**2)
    
    def range_filter(self, points: List[Point3D]) -> List[Point3D]:
        """
        Filter by range.
        
        Args:
            points: Input points
        
        Returns:
            Filtered points
        """
        return [p for p in points
                if self.range_min <= self._distance(p) <= self.range_max]
    
    def intensity_filter(self, points: List[Point3D]) -> List[Point3D]:
        """Filter by intensity."""
        return [p for p in points if p.intensity >= self.intensity_min]
    
    def statistical_outlier_removal(self, points: List[Point3D],
                                    k_neighbors: int = 10,
                                    std_dev_threshold: float = 1.0
                                    ) -> List[Point3D]:
        """
        Remove statistical outliers.
        
        Args:
            points: Input points
            k_neighbors: Number of neighbors
            std_dev_threshold: Standard deviation threshold
        
        Returns:
            Filtered points
        """
        if len(points) < k_neighbors + 1:
            return points
        
        filtered = []
        for i, p in enumerate(points):
            # Find k nearest neighbors
            distances = []
            for j, q in enumerate(points):
                if i == j:
                    continue
                d = math.sqrt((p.x-q.x)**2 + (p.y-q.y)**2 + (p.z-q.z)**2)
                distances.append(d)
            
            distances.sort()
            k_dist = distances[:k_neighbors]
            
            mean_d = sum(k_dist) / len(k_dist)
            std_d = math.sqrt(sum((d - mean_d)**2 for d in k_dist) / len(k_dist))
            
            if std_d > 0:
                # Compute point's mean distance to neighbors
                point_mean = sum(k_dist) / len(k_dist)
                z_score = abs(point_mean - mean_d) / std_d
                if z_score <= std_dev_threshold:
                    filtered.append(p)
            else:
                filtered.append(p)
        
        return filtered
    
    def filter_all(self, points: List[Point3D]) -> List[Point3D]:
        """Apply all filters."""
        points = self.range_filter(points)
        points = self.intensity_filter(points)
        points = self.statistical_outlier_removal(points)
        return points


class GroundSegmentation:
    """
    Segment ground plane from point cloud.
    """
    
    def __init__(self, ground_threshold_m: float = 0.1,
                 max_ground_slope_deg: float = 30.0):
        """
        Args:
            ground_threshold_m: Ground plane threshold
            max_ground_slope_deg: Maximum ground slope
        """
        self.ground_threshold = ground_threshold_m
        self.max_slope_rad = math.radians(max_ground_slope_deg)
    
    def find_ground_plane(self, points: List[Point3D],
                         grid_size_m: float = 1.0) -> List[Point3D]:
        """
        Find ground points using grid-based minimum.
        
        Args:
            points: Input points
            grid_size_m: Grid cell size
        
        Returns:
            Ground points
        """
        if not points:
            return []
        
        # Bin points into grid cells
        grid: Dict[Tuple[int, int], List[Point3D]] = {}
        for p in points:
            gx = int(p.x / grid_size_m)
            gy = int(p.y / grid_size_m)
            key = (gx, gy)
            if key not in grid:
                grid[key] = []
            grid[key].append(p)
        
        # Ground is lowest point in each cell
        ground = []
        for cell_points in grid.values():
            lowest = min(cell_points, key=lambda p: p.z)
            ground.append(lowest)
        
        return ground
    
    def segment(self, points: List[Point3D]) -> Tuple[List[Point3D], List[Point3D]]:
        """
        Segment ground and non-ground.
        
        Args:
            points: Input points
        
        Returns:
            (ground_points, non_ground_points)
        """
        ground = self.find_ground_plane(points)
        
        # Build set of ground points (by approximate coordinates)
        ground_keys = set()
        for p in ground:
            key = (round(p.x, 3), round(p.y, 3), round(p.z, 3))
            ground_keys.add(key)
        
        non_ground = []
        for p in points:
            key = (round(p.x, 3), round(p.y, 3), round(p.z, 3))
            if key not in ground_keys:
                non_ground.append(p)
        
        return ground, non_ground


class ObstacleDetector:
    """
    Detect obstacles from non-ground points.
    """
    
    def __init__(self, min_obstacle_height_m: float = 0.3,
                 clustering_distance_m: float = 1.0):
        """
        Args:
            min_obstacle_height_m: Minimum obstacle height
            clustering_distance_m: Clustering distance
        """
        self.min_height = min_obstacle_height_m
        self.cluster_dist = clustering_distance_m
    
    def cluster_points(self, points: List[Point3D]) -> List[List[Point3D]]:
        """
        Cluster points using simple distance threshold.
        
        Args:
            points: Input points
        
        Returns:
            List of clusters
        """
        if not points:
            return []
        
        clusters: List[List[Point3D]] = []
        used: Set[int] = set()
        
        for i, p in enumerate(points):
            if i in used:
                continue
            
            cluster = [p]
            used.add(i)
            
            # Find all points within threshold
            for j, q in enumerate(points):
                if j in used or j == i:
                    continue
                d = math.sqrt((p.x-q.x)**2 + (p.y-q.y)**2 + (p.z-q.z)**2)
                if d <= self.cluster_dist:
                    cluster.append(q)
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def detect_obstacles(self, points: List[Point3D],
                        ground_points: List[Point3D] = None
                        ) -> List[Dict]:
        """
        Detect obstacles from points.
        
        Args:
            points: Non-ground points
            ground_points: Ground reference
        
        Returns:
            List of obstacle descriptors
        """
        clusters = self.cluster_points(points)
        
        obstacles = []
        for cluster in clusters:
            if len(cluster) < 3:
                continue
            
            # Compute bounding box
            xs = [p.x for p in cluster]
            ys = [p.y for p in cluster]
            zs = [p.z for p in cluster]
            
            height = max(zs) - min(zs)
            if height < self.min_height:
                continue
            
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            cz = sum(zs) / len(zs)
            
            width = max(xs) - min(xs)
            depth = max(ys) - min(ys)
            
            obstacles.append({
                "center": (cx, cy, cz),
                "height_m": height,
                "width_m": width,
                "depth_m": depth,
                "points": len(cluster),
                "volume_m3": width * depth * height
            })
        
        return obstacles


class LiDARProcessor:
    """
    Unified LiDAR processing pipeline.
    """
    
    def __init__(self):
        self.filter = PointCloudFilter()
        self.ground_seg = GroundSegmentation()
        self.obstacle_det = ObstacleDetector()
        self.processed_frames = 0
    
    def process(self, points: List[Point3D]) -> Dict:
        """
        Process point cloud through pipeline.
        
        Args:
            points: Raw point cloud
        
        Returns:
            Processing results
        """
        # Filter
        filtered = self.filter.filter_all(points)
        
        # Segment ground
        ground, non_ground = self.ground_seg.segment(filtered)
        
        # Detect obstacles
        obstacles = self.obstacle_det.detect_obstacles(non_ground, ground)
        
        self.processed_frames += 1
        
        return {
            "raw_points": len(points),
            "filtered_points": len(filtered),
            "ground_points": len(ground),
            "non_ground_points": len(non_ground),
            "obstacles": obstacles,
            "obstacle_count": len(obstacles)
        }
    
    def set_filter_params(self, range_min: float, range_max: float,
                         intensity_min: float = 0.0):
        """Set filter parameters."""
        self.filter = PointCloudFilter(range_min, range_max, intensity_min)
    
    def processing_summary(self) -> Dict:
        """Get processing summary."""
        return {
            "processed_frames": self.processed_frames,
            "filter_range": (self.filter.range_min, self.filter.range_max)
        }
