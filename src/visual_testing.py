"""
Visual Testing Module
Direct visual inspection, image enhancement, defect detection,
and dimensional measurement for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VisualDefect:
    """Visual defect."""
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float
    area_mm2: float
    type: str
    severity: str


class ImageEnhancer:
    """
    Enhance images for visual inspection.
    """
    
    def __init__(self):
        pass
    
    def contrast_stretch(self, image: List[List[float]],
                        low_percentile: float = 2.0,
                        high_percentile: float = 98.0) -> List[List[float]]:
        """
        Contrast stretch.
        
        Args:
            image: Image
            low_percentile: Low percentile
            high_percentile: High percentile
        
        Returns:
            Enhanced image
        """
        flat = [v for row in image for v in row]
        flat_sorted = sorted(flat)
        
        low_idx = int(len(flat_sorted) * low_percentile / 100.0)
        high_idx = int(len(flat_sorted) * high_percentile / 100.0)
        
        low = flat_sorted[max(0, low_idx)]
        high = flat_sorted[min(len(flat_sorted) - 1, high_idx)]
        
        if high <= low:
            return image
        
        enhanced = []
        for row in image:
            new_row = []
            for v in row:
                stretched = (v - low) / (high - low)
                new_row.append(max(0.0, min(1.0, stretched)))
            enhanced.append(new_row)
        
        return enhanced
    
    def edge_enhance(self, image: List[List[float]]) -> List[List[float]]:
        """
        Edge enhancement.
        
        Args:
            image: Image
        
        Returns:
            Enhanced image
        """
        enhanced = []
        for i in range(len(image)):
            row = []
            for j in range(len(image[0])):
                # Simple Laplacian
                laplacian = -4.0 * image[i][j]
                if i > 0:
                    laplacian += image[i-1][j]
                if i < len(image) - 1:
                    laplacian += image[i+1][j]
                if j > 0:
                    laplacian += image[i][j-1]
                if j < len(image[0]) - 1:
                    laplacian += image[i][j+1]
                
                row.append(image[i][j] - laplacian)
            enhanced.append(row)
        
        return enhanced


class VisualDefectDetector:
    """
    Detect visual defects.
    """
    
    def __init__(self, min_area_mm2: float = 0.5,
                 contrast_threshold: float = 0.2):
        """
        Args:
            min_area_mm2: Minimum area
            contrast_threshold: Contrast threshold
        """
        self.min_area = min_area_mm2
        self.threshold = contrast_threshold
    
    def detect(self, image: List[List[float]],
              pixel_size_mm: float) -> List[VisualDefect]:
        """
        Detect defects.
        
        Args:
            image: Image
            pixel_size_mm: Pixel size
        
        Returns:
            Defects
        """
        defects = []
        visited = set()
        
        # Compute local contrast
        mean_val = sum(sum(row) for row in image) / (len(image) * len(image[0]))
        
        for i in range(len(image)):
            for j in range(len(image[0])):
                if abs(image[i][j] - mean_val) > self.threshold and (i, j) not in visited:
                    # Flood fill
                    cluster = []
                    stack = [(i, j)]
                    while stack:
                        x, y = stack.pop()
                        if (x, y) in visited:
                            continue
                        if x < 0 or x >= len(image) or y < 0 or y >= len(image[0]):
                            continue
                        if abs(image[x][y] - mean_val) <= self.threshold:
                            continue
                        visited.add((x, y))
                        cluster.append((x, y))
                        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
                    
                    if cluster:
                        area = len(cluster) * pixel_size_mm ** 2
                        if area >= self.min_area:
                            xs = [p[1] for p in cluster]
                            ys = [p[0] for p in cluster]
                            cx = sum(xs) / len(xs) * pixel_size_mm
                            cy = sum(ys) / len(ys) * pixel_size_mm
                            w = (max(xs) - min(xs) + 1) * pixel_size_mm
                            h = (max(ys) - min(ys) + 1) * pixel_size_mm
                            
                            defects.append(VisualDefect(
                                x_mm=cx, y_mm=cy, width_mm=w, height_mm=h,
                                area_mm2=area, type="anomaly",
                                severity="minor" if area < 2.0 else "major"
                            ))
        
        return defects


class DimensionalMeasurer:
    """
    Measure dimensions visually.
    """
    
    def __init__(self):
        pass
    
    def measure_length(self, points: List[Tuple[float, float]]) -> float:
        """
        Measure length.
        
        Args:
            points: Points in mm
        
        Returns:
            Length
        """
        length = 0.0
        for i in range(len(points) - 1):
            dx = points[i+1][0] - points[i][0]
            dy = points[i+1][1] - points[i][1]
            length += math.sqrt(dx**2 + dy**2)
        return length
    
    def measure_angle(self, p1: Tuple[float, float],
                     p2: Tuple[float, float],
                     p3: Tuple[float, float]) -> float:
        """
        Measure angle.
        
        Args:
            p1, p2, p3: Points
        
        Returns:
            Angle in degrees
        """
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if mag1 <= 0 or mag2 <= 0:
            return 0.0
        
        cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        return math.degrees(math.acos(cos_angle))


class VisualTesting:
    """
    Unified visual testing controller.
    """
    
    def __init__(self):
        self.enhancer = ImageEnhancer()
        self.detector = VisualDefectDetector()
        self.measurer = DimensionalMeasurer()
        self.defects: List[VisualDefect] = []
    
    def inspect(self, image: List[List[float]],
               pixel_size_mm: float) -> Dict:
        """
        Inspect.
        
        Args:
            image: Image
            pixel_size_mm: Pixel size
        
        Returns:
            Results
        """
        enhanced = self.enhancer.contrast_stretch(image)
        self.defects = self.detector.detect(enhanced, pixel_size_mm)
        
        severities = {}
        for d in self.defects:
            severities[d.severity] = severities.get(d.severity, 0) + 1
        
        return {
            "defects": len(self.defects),
            "severities": severities,
            "total_area_mm2": sum(d.area_mm2 for d in self.defects)
        }
    
    def vt_summary(self) -> Dict:
        """Get summary."""
        return {
            "defects": len(self.defects)
        }
