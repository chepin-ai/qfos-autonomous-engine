"""
Perception Pipeline Module
Object detection, point cloud processing, and feature
extraction for autonomous spacecraft vision.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Point3D:
    """A 3D point."""
    x: float
    y: float
    z: float
    intensity: float = 0.0


@dataclass
class BoundingBox:
    """A 3D bounding box."""
    x_min: float
    y_min: float
    z_min: float
    x_max: float
    y_max: float
    z_max: float
    label: str = ""
    confidence: float = 0.0
    
    def center(self) -> Tuple[float, float, float]:
        """Get box center."""
        return ((self.x_min + self.x_max) / 2,
                (self.y_min + self.y_max) / 2,
                (self.z_min + self.z_max) / 2)
    
    def volume(self) -> float:
        """Get box volume."""
        return max(0, self.x_max - self.x_min) * max(0, self.y_max - self.y_min) * max(0, self.z_max - self.z_min)
    
    def contains(self, point: Point3D) -> bool:
        """Check if point is inside box."""
        return (self.x_min <= point.x <= self.x_max and
                self.y_min <= point.y <= self.y_max and
                self.z_min <= point.z <= self.z_max)


@dataclass
class DetectedObject:
    """A detected object."""
    bbox: BoundingBox
    label: str
    confidence: float
    features: List[float] = field(default_factory=list)


class PointCloudProcessor:
    """
    Process 3D point clouds.
    """
    
    def __init__(self, voxel_size: float = 0.1):
        """
        Args:
            voxel_size: Voxel grid size for downsampling
        """
        self.voxel_size = voxel_size
    
    def downsample(self, points: List[Point3D]) -> List[Point3D]:
        """
        Voxel grid downsampling.
        
        Args:
            points: Input points
        
        Returns:
            Downsampled points
        """
        voxel_map: Dict[Tuple[int, int, int], List[Point3D]] = {}
        
        for p in points:
            key = (int(p.x / self.voxel_size),
                   int(p.y / self.voxel_size),
                   int(p.z / self.voxel_size))
            if key not in voxel_map:
                voxel_map[key] = []
            voxel_map[key].append(p)
        
        result = []
        for voxel_points in voxel_map.values():
            # Average position
            avg_x = sum(p.x for p in voxel_points) / len(voxel_points)
            avg_y = sum(p.y for p in voxel_points) / len(voxel_points)
            avg_z = sum(p.z for p in voxel_points) / len(voxel_points)
            avg_intensity = sum(p.intensity for p in voxel_points) / len(voxel_points)
            result.append(Point3D(avg_x, avg_y, avg_z, avg_intensity))
        
        return result
    
    def filter_distance(self, points: List[Point3D],
                       max_distance: float,
                       origin: Tuple[float, float, float] = (0, 0, 0)
                       ) -> List[Point3D]:
        """
        Filter points by distance from origin.
        
        Args:
            points: Input points
            max_distance: Maximum distance
            origin: Origin point
        
        Returns:
            Filtered points
        """
        result = []
        for p in points:
            dx = p.x - origin[0]
            dy = p.y - origin[1]
            dz = p.z - origin[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist <= max_distance:
                result.append(p)
        return result
    
    def estimate_normals(self, points: List[Point3D],
                        k: int = 5) -> List[Tuple[float, float, float]]:
        """
        Estimate surface normals using PCA on k-nearest neighbors.
        
        Args:
            points: Input points
            k: Number of neighbors
        
        Returns:
            List of normal vectors
        """
        normals = []
        for i, p in enumerate(points):
            # Find k nearest neighbors
            distances = []
            for j, q in enumerate(points):
                if i == j:
                    continue
                dx = p.x - q.x
                dy = p.y - q.y
                dz = p.z - q.z
                dist = dx*dx + dy*dy + dz*dz
                distances.append((dist, j))
            
            distances.sort()
            neighbors = distances[:k]
            
            if len(neighbors) < 3:
                normals.append((0.0, 0.0, 1.0))
                continue
            
            # Compute centroid
            cx = sum(points[j].x for _, j in neighbors) / len(neighbors)
            cy = sum(points[j].y for _, j in neighbors) / len(neighbors)
            cz = sum(points[j].z for _, j in neighbors) / len(neighbors)
            
            # Simple normal: vector from centroid to point
            nx = p.x - cx
            ny = p.y - cy
            nz = p.z - cz
            norm = math.sqrt(nx*nx + ny*ny + nz*nz)
            if norm > 0:
                normals.append((nx/norm, ny/norm, nz/norm))
            else:
                normals.append((0.0, 0.0, 1.0))
        
        return normals


class ObjectDetector:
    """
    Simple clustering-based object detection.
    """
    
    def __init__(self, cluster_distance: float = 0.5,
                 min_cluster_size: int = 10):
        """
        Args:
            cluster_distance: Distance threshold for clustering
            min_cluster_size: Minimum points per cluster
        """
        self.cluster_distance = cluster_distance
        self.min_cluster_size = min_cluster_size
    
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
        
        visited = set()
        clusters = []
        
        for i, p in enumerate(points):
            if i in visited:
                continue
            
            cluster = []
            queue = [i]
            visited.add(i)
            
            while queue:
                current_idx = queue.pop(0)
                current = points[current_idx]
                cluster.append(current)
                
                for j, q in enumerate(points):
                    if j in visited:
                        continue
                    dx = current.x - q.x
                    dy = current.y - q.y
                    dz = current.z - q.z
                    if math.sqrt(dx*dx + dy*dy + dz*dz) <= self.cluster_distance:
                        visited.add(j)
                        queue.append(j)
            
            if len(cluster) >= self.min_cluster_size:
                clusters.append(cluster)
        
        return clusters
    
    def detect(self, points: List[Point3D]) -> List[DetectedObject]:
        """
        Detect objects from point cloud.
        
        Args:
            points: Input points
        
        Returns:
            Detected objects
        """
        clusters = self.cluster_points(points)
        objects = []
        
        for cluster in clusters:
            xs = [p.x for p in cluster]
            ys = [p.y for p in cluster]
            zs = [p.z for p in cluster]
            
            bbox = BoundingBox(
                x_min=min(xs), y_min=min(ys), z_min=min(zs),
                x_max=max(xs), y_max=max(ys), z_max=max(zs),
                confidence=min(1.0, len(cluster) / 100.0)
            )
            
            # Simple classification by size
            volume = bbox.volume()
            if volume > 10.0:
                label = "large_structure"
            elif volume > 1.0:
                label = "medium_object"
            else:
                label = "small_debris"
            
            # Feature: centroid relative position
            cx, cy, cz = bbox.center()
            features = [cx, cy, cz, volume, len(cluster)]
            
            objects.append(DetectedObject(
                bbox=bbox,
                label=label,
                confidence=bbox.confidence,
                features=features
            ))
        
        return objects


class FeatureExtractor:
    """
    Extract features from point clouds.
    """
    
    def extract_shape_features(self, points: List[Point3D]) -> Dict[str, float]:
        """
        Extract shape features.
        
        Args:
            points: Input points
        
        Returns:
            Feature dict
        """
        if not points:
            return {}
        
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        zs = [p.z for p in points]
        
        # Bounding box dimensions
        x_span = max(xs) - min(xs)
        y_span = max(ys) - min(ys)
        z_span = max(zs) - min(zs)
        
        # Centroid
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        cz = sum(zs) / len(zs)
        
        # Spread
        spread = sum((p.x-cx)**2 + (p.y-cy)**2 + (p.z-cz)**2 for p in points) / len(points)
        
        return {
            "x_span": x_span,
            "y_span": y_span,
            "z_span": z_span,
            "volume": x_span * y_span * z_span,
            "centroid_x": cx,
            "centroid_y": cy,
            "centroid_z": cz,
            "spread": spread,
            "num_points": len(points)
        }
    
    def extract_histogram_features(self, points: List[Point3D],
                                  bins: int = 10) -> List[float]:
        """
        Extract distance histogram features.
        
        Args:
            points: Input points
            bins: Number of histogram bins
        
        Returns:
            Histogram counts
        """
        distances = [math.sqrt(p.x**2 + p.y**2 + p.z**2) for p in points]
        if not distances:
            return [0.0] * bins
        
        max_dist = max(distances)
        if max_dist == 0:
            return [0.0] * bins
        
        histogram = [0.0] * bins
        for d in distances:
            bin_idx = min(int(d / max_dist * bins), bins - 1)
            histogram[bin_idx] += 1
        
        # Normalize
        total = sum(histogram)
        if total > 0:
            histogram = [h / total for h in histogram]
        
        return histogram


class PerceptionPipeline:
    """
    Unified perception pipeline controller.
    """
    
    def __init__(self, voxel_size: float = 0.1):
        """
        Args:
            voxel_size: Voxel size for downsampling
        """
        self.point_processor = PointCloudProcessor(voxel_size)
        self.detector = ObjectDetector()
        self.feature_extractor = FeatureExtractor()
        self.objects: List[DetectedObject] = []
    
    def process_frame(self, points: List[Point3D],
                     max_distance: float = 100.0
                     ) -> List[DetectedObject]:
        """
        Process a frame of point cloud data.
        
        Args:
            points: Raw point cloud
            max_distance: Maximum distance filter
        
        Returns:
            Detected objects
        """
        # Filter by distance
        filtered = self.point_processor.filter_distance(points, max_distance)
        
        # Downsample
        downsampled = self.point_processor.downsample(filtered)
        
        # Detect objects
        self.objects = self.detector.detect(downsampled)
        
        return self.objects
    
    def get_features(self) -> List[Dict[str, float]]:
        """Get features for all detected objects."""
        features = []
        for obj in self.objects:
            # Extract features from bbox corners (approximate)
            pts = [
                Point3D(obj.bbox.x_min, obj.bbox.y_min, obj.bbox.z_min),
                Point3D(obj.bbox.x_max, obj.bbox.y_max, obj.bbox.z_max),
            ]
            feat = self.feature_extractor.extract_shape_features(pts)
            feat["label"] = obj.label
            feat["confidence"] = obj.confidence
            features.append(feat)
        return features
    
    def pipeline_summary(self) -> Dict:
        """Get pipeline summary."""
        return {
            "objects_detected": len(self.objects),
            "object_types": list(set(o.label for o in self.objects))
        }
