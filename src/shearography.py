"""
Shearography Module
Shear image generation, phase difference calculation,
speckle pattern analysis, and defect-induced deformation detection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpecklePattern:
    """Speckle pattern data."""
    intensity: List[float]
    width: int
    height: int


class ShearImageGenerator:
    """
    Generate sheared images.
    """
    
    def __init__(self, shear_pixels: int = 2):
        """
        Args:
            shear_pixels: Shear displacement
        """
        self.shear = shear_pixels
    
    def shear_image(self, image: List[float],
                   width: int, height: int,
                   direction: str = "x") -> List[float]:
        """
        Shear image.
        
        Args:
            image: Image data
            width: Width
            height: Height
            direction: Shear direction
        
        Returns:
            Sheared image
        """
        sheared = [0.0] * len(image)
        
        for y in range(height):
            for x in range(width):
                idx = y * width + x
                
                if direction == "x":
                    sx = min(x + self.shear, width - 1)
                    sidx = y * width + sx
                else:
                    sy = min(y + self.shear, height - 1)
                    sidx = sy * width + x
                
                sheared[idx] = image[sidx]
        
        return sheared
    
    def generate_speckle(self, width: int, height: int,
                        contrast: float = 0.5) -> SpecklePattern:
        """
        Generate synthetic speckle pattern.
        
        Args:
            width: Width
            height: Height
            contrast: Contrast
        
        Returns:
            Speckle pattern
        """
        import random
        intensity = [0.5 + contrast * (random.random() - 0.5)
                    for _ in range(width * height)]
        return SpecklePattern(intensity, width, height)


class PhaseDifferenceCalculator:
    """
    Calculate phase differences.
    """
    
    def __init__(self):
        pass
    
    def phase_difference(self, reference: List[float],
                        deformed: List[float]) -> List[float]:
        """
        Compute phase difference.
        
        Args:
            reference: Reference image
            deformed: Deformed image
        
        Returns:
            Phase differences
        """
        diff = []
        for r, d in zip(reference, deformed):
            # Simplified phase difference
            phase = math.atan2(d - r, r + 1e-10)
            diff.append(phase)
        return diff
    
    def wrap_phase(self, phase: float) -> float:
        """
        Wrap phase to [-pi, pi].
        
        Args:
            phase: Phase
        
        Returns:
            Wrapped phase
        """
        while phase > math.pi:
            phase -= 2.0 * math.pi
        while phase < -math.pi:
            phase += 2.0 * math.pi
        return phase
    
    def unwrap_phase(self, wrapped: List[float]) -> List[float]:
        """
        Unwrap phase.
        
        Args:
            wrapped: Wrapped phases
        
        Returns:
            Unwrapped phases
        """
        if not wrapped:
            return []
        
        unwrapped = [wrapped[0]]
        for i in range(1, len(wrapped)):
            diff = wrapped[i] - wrapped[i - 1]
            while diff > math.pi:
                diff -= 2.0 * math.pi
            while diff < -math.pi:
                diff += 2.0 * math.pi
            unwrapped.append(unwrapped[-1] + diff)
        
        return unwrapped


class SpecklePatternAnalyzer:
    """
    Analyze speckle patterns.
    """
    
    def __init__(self):
        pass
    
    def contrast(self, pattern: SpecklePattern) -> float:
        """
        Compute speckle contrast.
        
        Args:
            pattern: Pattern
        
        Returns:
            Contrast
        """
        if not pattern.intensity:
            return 0.0
        
        mean = sum(pattern.intensity) / len(pattern.intensity)
        variance = sum((i - mean)**2 for i in pattern.intensity) / len(pattern.intensity)
        
        if mean == 0:
            return 0.0
        
        return math.sqrt(variance) / mean
    
    def correlation(self, pattern1: SpecklePattern,
                   pattern2: SpecklePattern) -> float:
        """
        Compute correlation between patterns.
        
        Args:
            pattern1: Pattern 1
            pattern2: Pattern 2
        
        Returns:
            Correlation
        """
        if len(pattern1.intensity) != len(pattern2.intensity):
            return 0.0
        
        n = len(pattern1.intensity)
        mean1 = sum(pattern1.intensity) / n
        mean2 = sum(pattern2.intensity) / n
        
        cov = sum((a - mean1) * (b - mean2)
                 for a, b in zip(pattern1.intensity, pattern2.intensity)) / n
        
        var1 = sum((a - mean1)**2 for a in pattern1.intensity) / n
        var2 = sum((b - mean2)**2 for b in pattern2.intensity) / n
        
        if var1 == 0 or var2 == 0:
            return 1.0 if var1 == var2 else 0.0
        
        return cov / math.sqrt(var1 * var2)


class DeformationDefectDetector:
    """
    Detect defects from deformation.
    """
    
    def __init__(self, threshold_rad: float = 0.5):
        """
        Args:
            threshold_rad: Phase threshold
        """
        self.threshold = threshold_rad
    
    def detect_defects(self, phase_diff: List[float],
                      width: int, height: int) -> List[Dict]:
        """
        Detect defects from phase difference.
        
        Args:
            phase_diff: Phase differences
            width: Width
            height: Height
        
        Returns:
            Defects
        """
        defects = []
        visited = set()
        
        for i, p in enumerate(phase_diff):
            if i in visited or abs(p) < self.threshold:
                continue
            
            region = self._find_region(phase_diff, width, height,
                                      i, visited)
            if region:
                phases = [phase_diff[idx] for idx in region]
                defects.append({
                    "size": len(region),
                    "max_phase": max(abs(p) for p in phases),
                    "center": self._center(region, width)
                })
        
        return defects
    
    def _find_region(self, phase_diff: List[float], w: int, h: int,
                    start: int, visited: set) -> List[int]:
        """Find connected region."""
        region = []
        stack = [start]
        
        while stack:
            idx = stack.pop()
            if idx in visited or idx < 0 or idx >= len(phase_diff):
                continue
            
            if abs(phase_diff[idx]) < self.threshold:
                continue
            
            visited.add(idx)
            region.append(idx)
            
            x = idx % w
            y = idx // w
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    stack.append(ny * w + nx)
        
        return region
    
    def _center(self, region: List[int], width: int) -> Tuple[int, int]:
        """Compute center."""
        xs = [idx % width for idx in region]
        ys = [idx // width for idx in region]
        return (int(sum(xs) / len(xs)), int(sum(ys) / len(ys)))


class Shearography:
    """
    Unified shearography controller.
    """
    
    def __init__(self, shear_pixels: int = 2):
        self.generator = ShearImageGenerator(shear_pixels)
        self.phase_calc = PhaseDifferenceCalculator()
        self.analyzer = SpecklePatternAnalyzer()
        self.defect_detector = DeformationDefectDetector()
        self.reference: List[float] = []
        self.deformed: List[float] = []
    
    def capture_reference(self, image: List[float],
                         width: int, height: int):
        """
        Capture reference.
        
        Args:
            image: Image
            width: Width
            height: Height
        """
        self.reference = self.generator.shear_image(image, width, height)
    
    def capture_deformed(self, image: List[float],
                        width: int, height: int):
        """
        Capture deformed.
        
        Args:
            image: Image
            width: Width
            height: Height
        """
        self.deformed = self.generator.shear_image(image, width, height)
    
    def inspect(self, width: int, height: int) -> Dict:
        """
        Inspect.
        
        Args:
            width: Width
            height: Height
        
        Returns:
            Results
        """
        if not self.reference or not self.deformed:
            return {"defects": 0, "regions": []}
        
        phase_diff = self.phase_calc.phase_difference(self.reference,
                                                       self.deformed)
        defects = self.defect_detector.detect_defects(phase_diff, width, height)
        
        return {
            "defects": len(defects),
            "regions": defects[:3]
        }
    
    def shearography_summary(self) -> Dict:
        """Get summary."""
        return {
            "reference_size": len(self.reference),
            "deformed_size": len(self.deformed),
            "shear": self.generator.shear
        }
