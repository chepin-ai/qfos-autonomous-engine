"""
Computer Vision Module
Image filtering, edge detection, feature extraction,
Hough transform, and object detection for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ImagePoint:
    """Image coordinate."""
    x: int
    y: int
    intensity: float


class ImageFilter:
    """
    Image filtering operations.
    """
    
    def __init__(self):
        pass
    
    def gaussian_kernel(self, size: int = 3,
                       sigma: float = 1.0) -> List[List[float]]:
        """
        Generate Gaussian kernel.
        
        Args:
            size: Kernel size
            sigma: Standard deviation
        
        Returns:
            Kernel
        """
        kernel = []
        center = size // 2
        total = 0.0
        
        for i in range(size):
            row = []
            for j in range(size):
                x = i - center
                y = j - center
                val = math.exp(-(x ** 2 + y ** 2) / (2.0 * sigma ** 2))
                row.append(val)
                total += val
            kernel.append(row)
        
        # Normalize
        for i in range(size):
            for j in range(size):
                kernel[i][j] /= total
        
        return kernel
    
    def convolve(self, image: List[List[float]],
                kernel: List[List[float]]) -> List[List[float]]:
        """
        Convolve image with kernel.
        
        Args:
            image: Input image
            kernel: Convolution kernel
        
        Returns:
            Filtered image
        """
        if not image or not kernel:
            return image
        
        h = len(image)
        w = len(image[0])
        k_h = len(kernel)
        k_w = len(kernel[0])
        pad_h = k_h // 2
        pad_w = k_w // 2
        
        result = []
        for i in range(h):
            row = []
            for j in range(w):
                val = 0.0
                for ki in range(k_h):
                    for kj in range(k_w):
                        ii = i + ki - pad_h
                        jj = j + kj - pad_w
                        if 0 <= ii < h and 0 <= jj < w:
                            val += image[ii][jj] * kernel[ki][kj]
                row.append(val)
            result.append(row)
        
        return result
    
    def sobel_kernels(self) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Get Sobel kernels.
        
        Returns:
            (Gx, Gy) kernels
        """
        Gx = [[-1.0, 0.0, 1.0],
              [-2.0, 0.0, 2.0],
              [-1.0, 0.0, 1.0]]
        Gy = [[-1.0, -2.0, -1.0],
              [0.0, 0.0, 0.0],
              [1.0, 2.0, 1.0]]
        return (Gx, Gy)
    
    def sobel_edge(self, image: List[List[float]]) -> List[List[float]]:
        """
        Sobel edge detection.
        
        Args:
            image: Input image
        
        Returns:
            Edge magnitude image
        """
        Gx, Gy = self.sobel_kernels()
        edge_x = self.convolve(image, Gx)
        edge_y = self.convolve(image, Gy)
        
        h = len(image)
        w = len(image[0])
        result = []
        for i in range(h):
            row = []
            for j in range(w):
                mag = math.sqrt(edge_x[i][j] ** 2 + edge_y[i][j] ** 2)
                row.append(min(255.0, mag))
            result.append(row)
        
        return result


class HoughTransform:
    """
    Hough transform for line detection.
    """
    
    def __init__(self, theta_resolution: int = 180,
                 rho_resolution: int = 100):
        """
        Args:
            theta_resolution: Theta bins
            rho_resolution: Rho bins
        """
        self.theta_res = theta_resolution
        self.rho_res = rho_resolution
    
    def detect_lines(self, edge_image: List[List[float]],
                    threshold: float = 50.0) -> List[Tuple[float, float]]:
        """
        Detect lines in edge image.
        
        Args:
            edge_image: Edge image
            threshold: Vote threshold
        
        Returns:
            List of (rho, theta) lines
        """
        h = len(edge_image)
        w = len(edge_image[0])
        diag = math.sqrt(h ** 2 + w ** 2)
        
        # Accumulator
        accumulator: Dict[Tuple[int, int], int] = {}
        
        for y in range(h):
            for x in range(w):
                if edge_image[y][x] > threshold:
                    for t_idx in range(self.theta_res):
                        theta = t_idx * math.pi / self.theta_res
                        rho = x * math.cos(theta) + y * math.sin(theta)
                        r_idx = int((rho + diag) * self.rho_res / (2.0 * diag))
                        key = (r_idx, t_idx)
                        accumulator[key] = accumulator.get(key, 0) + 1
        
        # Find peaks
        max_votes = max(accumulator.values()) if accumulator else 0
        lines = []
        for (r_idx, t_idx), votes in accumulator.items():
            if votes >= max_votes * 0.8:
                theta = t_idx * math.pi / self.theta_res
                rho = r_idx * 2.0 * diag / self.rho_res - diag
                lines.append((rho, theta))
        
        return lines


class FeatureExtractor:
    """
    Feature extraction from images.
    """
    
    def __init__(self):
        pass
    
    def gradient_histogram(self, edge_image: List[List[float]],
                          num_bins: int = 8) -> List[float]:
        """
        Compute gradient orientation histogram.
        
        Args:
            edge_image: Edge magnitude image
            num_bins: Number of orientation bins
        
        Returns:
            Histogram
        """
        if not edge_image:
            return [0.0] * num_bins
        
        h = len(edge_image)
        w = len(edge_image[0])
        histogram = [0.0] * num_bins
        total = 0.0
        
        # Simple horizontal/vertical gradient approximation
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                dx = edge_image[y][x + 1] - edge_image[y][x - 1]
                dy = edge_image[y + 1][x] - edge_image[y - 1][x]
                mag = math.sqrt(dx ** 2 + dy ** 2)
                
                if mag > 0:
                    angle = math.atan2(dy, dx)
                    if angle < 0:
                        angle += math.pi
                    bin_idx = int(angle / math.pi * num_bins) % num_bins
                    histogram[bin_idx] += mag
                    total += mag
        
        if total > 0:
            histogram = [v / total for v in histogram]
        
        return histogram
    
    def corners_from_edges(self, edge_image: List[List[float]],
                          threshold: float = 100.0) -> List[Tuple[int, int]]:
        """
        Detect corners from edge intersections.
        
        Args:
            edge_image: Edge image
            threshold: Edge threshold
        
        Returns:
            Corner coordinates
        """
        corners = []
        h = len(edge_image)
        w = len(edge_image[0])
        
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if edge_image[y][x] > threshold:
                    # Count strong neighbors
                    neighbors = sum(1 for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                                   if edge_image[y + dy][x + dx] > threshold)
                    if 3 <= neighbors <= 5:
                        corners.append((x, y))
        
        return corners


class ObjectDetector:
    """
    Simple object detection.
    """
    
    def __init__(self):
        pass
    
    def bounding_boxes(self, binary_image: List[List[float]],
                      threshold: float = 128.0) -> List[Dict]:
        """
        Find bounding boxes in binary image.
        
        Args:
            binary_image: Binary image
            threshold: Threshold
        
        Returns:
            Bounding boxes
        """
        h = len(binary_image)
        w = len(binary_image[0])
        visited = [[False] * w for _ in range(h)]
        boxes = []
        
        for y in range(h):
            for x in range(w):
                if binary_image[y][x] > threshold and not visited[y][x]:
                    # BFS to find connected component
                    min_x, max_x = x, x
                    min_y, max_y = y, y
                    stack = [(x, y)]
                    visited[y][x] = True
                    
                    while stack:
                        cx, cy = stack.pop()
                        min_x = min(min_x, cx)
                        max_x = max(max_x, cx)
                        min_y = min(min_y, cy)
                        max_y = max(max_y, cy)
                        
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if binary_image[ny][nx] > threshold and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    stack.append((nx, ny))
                    
                    boxes.append({
                        "x": min_x,
                        "y": min_y,
                        "width": max_x - min_x + 1,
                        "height": max_y - min_y + 1,
                        "center": ((min_x + max_x) // 2, (min_y + max_y) // 2)
                    })
        
        return boxes


class ComputerVision:
    """
    Unified computer vision controller.
    """
    
    def __init__(self):
        self.filter = ImageFilter()
        self.hough = HoughTransform()
        self.features = FeatureExtractor()
        self.detector = ObjectDetector()
    
    def cv_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["gaussian_filter", "sobel_edge", "hough_lines",
                       "gradient_histogram", "corner_detection", "bounding_boxes"],
            "pipelines": ["edge_detection", "feature_extraction", "object_detection"]
        }
