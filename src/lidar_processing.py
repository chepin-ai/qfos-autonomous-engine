"""
LiDAR Processing Module
Point cloud filtering, clustering, ground segmentation,
obstacle detection, and 3D bounding box estimation for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class Point3D:
    """3D point."""
    x: float
    y: float
    z: float
    
    def distance(self, other: 'Point3D') -> float:
        """Euclidean distance."""
        return math.sqrt((self.x - other.x) ** 2 +
                        (self.y - other.y) ** 2 +
                        (self.z - other.z) ** 2)
    
    def distance_xy(self, other: 'Point3D') -> float:
        """XY plane distance."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class PointCloudFilter:
    """
    Filter point clouds.
    """
    
    def __init__(self):
        pass
    
    def range_filter(self, points: List[Point3D],
                    min_range: float,
                    max_range: float) -> List[Point3D]:
        """
        Filter by range from origin.
        
        Args:
            points: Points
            min_range: Min range
            max_range: Max range
        
        Returns:
            Filtered points
        """
        origin = Point3D(0.0, 0.0, 0.0)
        return [p for p in points
               if min_range <= p.distance(origin) <= max_range]
    
    def height_filter(self, points: List[Point3D],
                     min_z: float,
                     max_z: float) -> List[Point3D]:
        """
        Filter by height.
        
        Args:
            points: Points
            min_z: Min height
            max_z: Max height
        
        Returns:
            Filtered points
        """
        return [p for p in points if min_z <= p.z <= max_z]
    
    def voxel_downsample(self, points: List[Point3D],
                        voxel_size: float = 0.1) -> List[Point3D]:
        """
        Voxel grid downsample.
        
        Args:
            points: Points
            voxel_size: Voxel size
        
        Returns:
            Downsampled points
        """
        voxels: Dict[Tuple[int, int, int], List[Point3D]] = {}
        
        for p in points:
            key = (int(p.x / voxel_size),
                   int(p.y / voxel_size),
                   int(p.z / voxel_size))
            if key not in voxels:
                voxels[key] = []
            voxels[key].append(p)
        
        result = []
        for voxel_points in voxels.values():
            avg_x = sum(p.x for p in voxel_points) / len(voxel_points)
            avg_y = sum(p.y for p in voxel_points) / len(voxel_points)
            avg_z = sum(p.z for p in voxel_points) / len(voxel_points)
            result.append(Point3D(avg_x, avg_y, avg_z))
        
        return result


class DBSCANClustering:
    """
    DBSCAN clustering for point clouds.
    """
    
    def __init__(self, eps: float = 0.5,
                 min_points: int = 3):
        """
        Args:
            eps: Neighborhood radius
            min_points: Min points for core
        """
        self.eps = eps
        self.min_points = min_points
    
    def cluster(self, points: List[Point3D]) -> List[List[Point3D]]:
        """
        Cluster points.
        
        Args:
            points: Points
        
        Returns:
            Clusters
        """
        n = len(points)
        visited = [False] * n
        clusters: List[List[Point3D]] = []
        
        for i in range(n):
            if visited[i]:
                continue
            
            neighbors = self._get_neighbors(points, i)
            if len(neighbors) + 1 < self.min_points:
                visited[i] = True
                continue
            
            cluster = self._expand_cluster(points, visited, i, neighbors)
            if cluster:
                clusters.append(cluster)
        
        return clusters
    
    def _get_neighbors(self, points: List[Point3D],
                      index: int) -> List[int]:
        """Get neighbor indices."""
        target = points[index]
        return [j for j in range(len(points))
               if j != index and points[j].distance(target) < self.eps]
    
    def _expand_cluster(self, points: List[Point3D],
                       visited: List[bool],
                       core_idx: int,
                       neighbors: List[int]) -> List[Point3D]:
        """Expand cluster."""
        cluster = [points[core_idx]]
        visited[core_idx] = True
        
        i = 0
        while i < len(neighbors):
            idx = neighbors[i]
            if not visited[idx]:
                visited[idx] = True
                new_neighbors = self._get_neighbors(points, idx)
                if len(new_neighbors) + 1 >= self.min_points:
                    neighbors.extend(new_neighbors)
                cluster.append(points[idx])
            i += 1
        
        return cluster


class GroundSegmentation:
    """
    Ground plane segmentation.
    """
    
    def __init__(self, height_threshold: float = 0.2):
        """
        Args:
            height_threshold: Height threshold
        """
        self.height_threshold = height_threshold
    
    def segment(self, points: List[Point3D]) -> Tuple[List[Point3D], List[Point3D]]:
        """
        Segment ground and obstacles.
        
        Args:
            points: Points
        
        Returns:
            (ground_points, obstacle_points)
        """
        if not points:
            return ([], [])
        
        # Simple RANSAC-like: fit plane to lowest points
        min_z = min(p.z for p in points)
        ground = [p for p in points if p.z <= min_z + self.height_threshold]
        obstacles = [p for p in points if p.z > min_z + self.height_threshold]
        
        return (ground, obstacles)


class BoundingBoxEstimator:
    """
    Estimate 3D bounding boxes.
    """
    
    def __init__(self):
        pass
    
    def bbox(self, points: List[Point3D]) -> Dict:
        """
        Compute axis-aligned bounding box.
        
        Args:
            points: Points
        
        Returns:
            BBox dict
        """
        if not points:
            return {}
        
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        min_z = min(p.z for p in points)
        max_z = max(p.z for p in points)
        
        return {
            "center": Point3D((min_x + max_x) / 2.0,
                             (min_y + max_y) / 2.0,
                             (min_z + max_z) / 2.0),
            "dimensions": (max_x - min_x, max_y - min_y, max_z - min_z),
            "volume": (max_x - min_x) * (max_y - min_y) * (max_z - min_z)
        }
    
    def centroid(self, points: List[Point3D]) -> Point3D:
        """
        Compute centroid.
        
        Args:
            points: Points
        
        Returns:
            Centroid
        """
        if not points:
            return Point3D(0.0, 0.0, 0.0)
        
        return Point3D(
            sum(p.x for p in points) / len(points),
            sum(p.y for p in points) / len(points),
            sum(p.z for p in points) / len(points)
        )


class LiDARProcessing:
    """
    Unified LiDAR processing controller.
    """
    
    def __init__(self):
        self.filter = PointCloudFilter()
        self.cluster = DBSCANClustering()
        self.ground = GroundSegmentation()
        self.bbox = BoundingBoxEstimator()
    
    def process(self, points: List[Point3D]) -> Dict:
        """
        Full processing pipeline.
        
        Args:
            points: Raw points
        
        Returns:
            Results
        """
        filtered = self.filter.voxel_downsample(points, 0.2)
        ground_pts, obstacle_pts = self.ground.segment(filtered)
        clusters = self.cluster.cluster(obstacle_pts)
        
        bboxes = [self.bbox.bbox(c) for c in clusters if len(c) >= 3]
        
        return {
            "num_points": len(points),
            "num_filtered": len(filtered),
            "num_ground": len(ground_pts),
            "num_obstacles": len(obstacle_pts),
            "num_clusters": len(clusters),
            "num_bboxes": len(bboxes)
        }
    
    def lp_summary(self) -> Dict:
        """Get summary."""
        return {
            "stages": ["filter", "ground_segmentation", "clustering", "bbox"],
            "methods": ["voxel_downsample", "dbscan", "height_threshold"]
        }
