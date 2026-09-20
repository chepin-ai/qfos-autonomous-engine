"""
Visual Inspection Module
Automated visual NDT with defect detection, edge extraction,
blob analysis, pattern matching, and lighting compensation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DefectType(Enum):
    """Types of visual defects."""
    CRACK = "crack"
    SCRATCH = "scratch"
    DENT = "dent"
    DISCOLORATION = "discoloration"
    CONTAMINATION = "contamination"
    MISSING = "missing"


@dataclass
class VisualDefect:
    """Detected visual defect."""
    x: float
    y: float
    width: float
    height: float
    defect_type: DefectType
    severity: float  # 0-1
    confidence: float


class EdgeDetector:
    """
    Edge detection for visual inspection.
    """
    
    def __init__(self, threshold: float = 30.0):
        """
        Args:
            threshold: Edge threshold
        """
        self.threshold = threshold
    
    def gradient(self, image: List[List[float]],
                x: int, y: int) -> Tuple[float, float]:
        """
        Compute gradient at pixel.
        
        Args:
            image: 2D image
            x: X position
            y: Y position
        
        Returns:
            (dx, dy)
        """
        h = len(image)
        w = len(image[0]) if h > 0 else 0
        
        if w == 0 or h == 0:
            return (0.0, 0.0)
        
        dx = image[y][min(w - 1, x + 1)] - image[y][max(0, x - 1)]
        dy = image[min(h - 1, y + 1)][x] - image[max(0, y - 1)][x]
        return (dx, dy)
    
    def magnitude(self, dx: float, dy: float) -> float:
        """
        Compute gradient magnitude.
        
        Args:
            dx: X gradient
            dy: Y gradient
        
        Returns:
            Magnitude
        """
        return math.sqrt(dx**2 + dy**2)
    
    def detect_edges(self, image: List[List[float]]) -> List[List[float]]:
        """
        Detect edges in image.
        
        Args:
            image: 2D image
        
        Returns:
            Edge magnitude map
        """
        h = len(image)
        w = len(image[0]) if h > 0 else 0
        edges = [[0.0] * w for _ in range(h)]
        
        for y in range(h):
            for x in range(w):
                dx, dy = self.gradient(image, x, y)
                mag = self.magnitude(dx, dy)
                edges[y][x] = mag if mag > self.threshold else 0.0
        
        return edges
    
    def edge_count(self, edges: List[List[float]]) -> int:
        """
        Count edge pixels.
        
        Args:
            edges: Edge map
        
        Returns:
            Count
        """
        return sum(1 for row in edges for val in row if val > 0)


class BlobAnalyzer:
    """
    Blob detection and analysis.
    """
    
    def __init__(self, threshold: float = 50.0):
        """
        Args:
            threshold: Detection threshold
        """
        self.threshold = threshold
    
    def detect_blobs(self, image: List[List[float]]) -> List[Dict]:
        """
        Detect blobs using connected component labeling.
        
        Args:
            image: 2D image
        
        Returns:
            Blob list
        """
        h = len(image)
        w = len(image[0]) if h > 0 else 0
        visited = [[False] * w for _ in range(h)]
        blobs = []
        
        for y in range(h):
            for x in range(w):
                if image[y][x] > self.threshold and not visited[y][x]:
                    # Flood fill
                    pixels = []
                    stack = [(x, y)]
                    while stack:
                        cx, cy = stack.pop()
                        if cx < 0 or cx >= w or cy < 0 or cy >= h:
                            continue
                        if visited[cy][cx] or image[cy][cx] <= self.threshold:
                            continue
                        visited[cy][cx] = True
                        pixels.append((cx, cy))
                        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
                    
                    if pixels:
                        xs = [p[0] for p in pixels]
                        ys = [p[1] for p in pixels]
                        blobs.append({
                            "x": sum(xs) / len(xs),
                            "y": sum(ys) / len(ys),
                            "width": max(xs) - min(xs) + 1,
                            "height": max(ys) - min(ys) + 1,
                            "area": len(pixels),
                            "mean_intensity": sum(image[p[1]][p[0]] for p in pixels) / len(pixels)
                        })
        
        return blobs
    
    def blob_circularity(self, blob: Dict) -> float:
        """
        Compute blob circularity.
        
        Args:
            blob: Blob dict
        
        Returns:
            Circularity (1.0 = perfect circle)
        """
        area = blob.get("area", 1)
        if area <= 0:
            return 0.0
        # Perimeter approximation
        perimeter = 2.0 * (blob.get("width", 1) + blob.get("height", 1))
        return 4.0 * math.pi * area / (perimeter ** 2)


class PatternMatcher:
    """
    Pattern matching for visual inspection.
    """
    
    def __init__(self):
        self.templates: List[Dict] = []
    
    def add_template(self, name: str, pattern: List[List[float]]):
        """
        Add template pattern.
        
        Args:
            name: Template name
            pattern: 2D pattern
        """
        self.templates.append({"name": name, "pattern": pattern})
    
    def normalized_cross_correlation(self,
                                     image: List[List[float]],
                                     template: List[List[float]],
                                     x: int, y: int) -> float:
        """
        Compute NCC at position.
        
        Args:
            image: Image
            template: Template
            x: X position
            y: Y position
        
        Returns:
            NCC (-1 to 1)
        """
        th = len(template)
        tw = len(template[0]) if th > 0 else 0
        ih = len(image)
        iw = len(image[0]) if ih > 0 else 0
        
        if th == 0 or tw == 0:
            return 0.0
        
        # Extract region
        region = []
        for dy in range(th):
            row = []
            for dx in range(tw):
                py = y + dy
                px = x + dx
                if 0 <= py < ih and 0 <= px < iw:
                    row.append(image[py][px])
                else:
                    row.append(0.0)
            region.append(row)
        
        # Compute NCC
        mean_t = sum(sum(row) for row in template) / (th * tw)
        mean_r = sum(sum(row) for row in region) / (th * tw)
        
        num = 0.0
        den_t = 0.0
        den_r = 0.0
        
        for dy in range(th):
            for dx in range(tw):
                t_val = template[dy][dx] - mean_t
                r_val = region[dy][dx] - mean_r
                num += t_val * r_val
                den_t += t_val ** 2
                den_r += r_val ** 2
        
        if den_t <= 0 or den_r <= 0:
            return 0.0
        
        return num / math.sqrt(den_t * den_r)
    
    def match(self, image: List[List[float]],
             threshold: float = 0.8) -> List[Dict]:
        """
        Match all templates.
        
        Args:
            image: Image
            threshold: Match threshold
        
        Returns:
            Matches
        """
        matches = []
        ih = len(image)
        iw = len(image[0]) if ih > 0 else 0
        
        for template in self.templates:
            pat = template["pattern"]
            th = len(pat)
            tw = len(pat[0]) if th > 0 else 0
            
            for y in range(ih - th + 1):
                for x in range(iw - tw + 1):
                    ncc = self.normalized_cross_correlation(image, pat, x, y)
                    if ncc >= threshold:
                        matches.append({
                            "name": template["name"],
                            "x": x,
                            "y": y,
                            "score": ncc
                        })
        
        return matches


class LightingCompensator:
    """
    Lighting compensation for visual inspection.
    """
    
    def __init__(self):
        self.target_mean = 128.0
    
    def histogram_equalization(self, image: List[List[float]]) -> List[List[float]]:
        """
        Simple histogram equalization.
        
        Args:
            image: Image
        
        Returns:
            Equalized image
        """
        if not image:
            return []
        
        h = len(image)
        w = len(image[0]) if h > 0 else 0
        
        # Compute histogram
        hist = [0] * 256
        for row in image:
            for val in row:
                idx = int(max(0, min(255, val)))
                hist[idx] += 1
        
        # CDF
        cdf = []
        cumsum = 0
        for count in hist:
            cumsum += count
            cdf.append(cumsum)
        
        total = cdf[-1] if cdf else 1
        if total == 0:
            total = 1
        
        # Map
        equalized = []
        for row in image:
            new_row = []
            for val in row:
                idx = int(max(0, min(255, val)))
                new_val = 255.0 * cdf[idx] / total
                new_row.append(new_val)
            equalized.append(new_row)
        
        return equalized
    
    def mean_intensity(self, image: List[List[float]]) -> float:
        """
        Compute mean intensity.
        
        Args:
            image: Image
        
        Returns:
            Mean
        """
        if not image:
            return 0.0
        total = sum(sum(row) for row in image)
        count = sum(len(row) for row in image)
        return total / count if count > 0 else 0.0


class VisualInspection:
    """
    Unified visual inspection controller.
    """
    
    def __init__(self):
        self.edge_detector = EdgeDetector()
        self.blob_analyzer = BlobAnalyzer()
        self.pattern_matcher = PatternMatcher()
        self.lighting = LightingCompensator()
        self.defects: List[VisualDefect] = []
        self.inspections: List[Dict] = []
    
    def inspect(self, image: List[List[float]]) -> Dict:
        """
        Run visual inspection.
        
        Args:
            image: 2D image
        
        Returns:
            Inspection report
        """
        # Compensate lighting
        comp = self.lighting.histogram_equalization(image)
        
        # Detect edges
        edges = self.edge_detector.detect_edges(comp)
        edge_count = self.edge_detector.edge_count(edges)
        
        # Detect blobs
        blobs = self.blob_analyzer.detect_blobs(comp)
        
        # Pattern matching
        matches = self.pattern_matcher.match(comp)
        
        # Detect defects from blobs
        defects = []
        for blob in blobs:
            if blob["area"] > 10:
                defects.append(VisualDefect(
                    x=blob["x"],
                    y=blob["y"],
                    width=blob["width"],
                    height=blob["height"],
                    defect_type=DefectType.CONTAMINATION,
                    severity=min(1.0, blob["area"] / 100.0),
                    confidence=0.7
                ))
        
        self.defects.extend(defects)
        
        report = {
            "edge_pixels": edge_count,
            "blobs": len(blobs),
            "patterns": len(matches),
            "defects": len(defects),
            "pass": len(defects) == 0
        }
        self.inspections.append(report)
        return report
    
    def add_pattern(self, name: str, pattern: List[List[float]]):
        """
        Add reference pattern.
        
        Args:
            name: Pattern name
            pattern: 2D pattern
        """
        self.pattern_matcher.add_template(name, pattern)
    
    def inspection_summary(self) -> Dict:
        """Get inspection summary."""
        if not self.inspections:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.inspections),
            "pass_count": sum(1 for r in self.inspections if r["pass"]),
            "total_defects": sum(r["defects"] for r in self.inspections)
        }
