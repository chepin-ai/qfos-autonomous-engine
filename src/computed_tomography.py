"""
Computed Tomography Module
CT reconstruction with parallel-beam geometry, filtered backprojection,
Radon transform, and artifact correction for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CTProjection:
    """Single CT projection."""
    angle_deg: float
    detector_position_mm: float
    intensity: float


class RadonTransform:
    """
    Radon transform for CT.
    """
    
    def __init__(self, image_size: int = 64):
        """
        Args:
            image_size: Image dimensions
        """
        self.size = image_size
    
    def line_integral(self, image: List[List[float]],
                     angle_deg: float,
                     distance_mm: float) -> float:
        """
        Compute line integral through image.
        
        Args:
            image: 2D image
            angle_deg: Projection angle
            distance_mm: Distance from center
        
        Returns:
            Line integral
        """
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        center = self.size / 2.0
        integral = 0.0
        count = 0
        
        # Sample along line perpendicular to angle
        for t in range(-self.size, self.size + 1):
            # Point on line
            x = distance_mm * cos_a - t * sin_a + center
            y = distance_mm * sin_a + t * cos_a + center
            
            ix = int(round(x))
            iy = int(round(y))
            
            if 0 <= ix < self.size and 0 <= iy < self.size:
                integral += image[iy][ix]
                count += 1
        
        return integral / max(count, 1)
    
    def project(self, image: List[List[float]],
               angles: List[float],
               num_detectors: int = 64) -> Dict[float, List[float]]:
        """
        Compute projections at multiple angles.
        
        Args:
            image: Image
            angles: Projection angles
            num_detectors: Detectors per angle
        
        Returns:
            Projections
        """
        projections = {}
        max_dist = self.size / 2.0
        
        for angle in angles:
            proj = []
            for d in range(num_detectors):
                dist = (d - num_detectors / 2.0) * max_dist / (num_detectors / 2.0)
                val = self.line_integral(image, angle, dist)
                proj.append(val)
            projections[angle] = proj
        
        return projections


class FilteredBackprojection:
    """
    Filtered backprojection CT reconstruction.
    """
    
    def __init__(self, image_size: int = 64):
        """
        Args:
            image_size: Reconstruction size
        """
        self.size = image_size
    
    def ram_lak_filter(self, num_points: int) -> List[float]:
        """
        Generate Ram-Lak filter.
        
        Args:
            num_points: Number of points
        
        Returns:
            Filter kernel
        """
        kernel = []
        for i in range(num_points):
            n = i - num_points // 2
            if n == 0:
                kernel.append(1.0)
            elif n % 2 == 0:
                kernel.append(0.0)
            else:
                kernel.append(-4.0 / (math.pi ** 2 * n ** 2))
        return kernel
    
    def convolve(self, signal: List[float],
                kernel: List[float]) -> List[float]:
        """
        Convolve signal with kernel.
        
        Args:
            signal: Signal
            kernel: Kernel
        
        Returns:
            Convolved signal
        """
        n = len(signal)
        m = len(kernel)
        result = []
        
        for i in range(n):
            val = 0.0
            for j in range(m):
                idx = i + j - m // 2
                if 0 <= idx < n:
                    val += signal[idx] * kernel[j]
            result.append(val)
        
        return result
    
    def backproject(self, projections: Dict[float, List[float]]) -> List[List[float]]:
        """
        Backproject filtered projections.
        
        Args:
            projections: Filtered projections
        
        Returns:
            Reconstructed image
        """
        image = [[0.0] * self.size for _ in range(self.size)]
        center = self.size / 2.0
        num_angles = len(projections)
        
        for angle, proj in projections.items():
            angle_rad = math.radians(angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            num_det = len(proj)
            
            for y in range(self.size):
                for x in range(self.size):
                    # Distance from center for this pixel
                    dx = x - center
                    dy = y - center
                    dist = dx * cos_a + dy * sin_a
                    
                    # Interpolate projection value
                    det_idx = (dist / center + 1.0) * num_det / 2.0
                    idx0 = int(det_idx)
                    idx1 = idx0 + 1
                    frac = det_idx - idx0
                    
                    val = 0.0
                    if 0 <= idx0 < num_det:
                        val += proj[idx0] * (1.0 - frac)
                    if 0 <= idx1 < num_det:
                        val += proj[idx1] * frac
                    
                    image[y][x] += val / num_angles
        
        return image
    
    def reconstruct(self, projections: Dict[float, List[float]]) -> List[List[float]]:
        """
        Full FBP reconstruction.
        
        Args:
            projections: Raw projections
        
        Returns:
            Reconstructed image
        """
        # Filter each projection
        num_points = len(next(iter(projections.values())))
        kernel = self.ram_lak_filter(num_points)
        
        filtered = {}
        for angle, proj in projections.items():
            filtered[angle] = self.convolve(proj, kernel)
        
        return self.backproject(filtered)


class CTArtifactCorrector:
    """
    CT artifact correction.
    """
    
    def beam_hardening_correction(self, projection: List[float],
                                 material_thickness_mm: float = 10.0) -> List[float]:
        """
        Correct beam hardening.
        
        Args:
            projection: Projection
            material_thickness_mm: Thickness
        
        Returns:
            Corrected projection
        """
        # Simplified polynomial correction
        return [p + 0.001 * p**3 for p in projection]
    
    def ring_artifact_reduction(self, sinogram: List[List[float]]) -> List[List[float]]:
        """
        Reduce ring artifacts.
        
        Args:
            sinogram: Sinogram
        
        Returns:
            Corrected sinogram
        """
        if not sinogram:
            return []
        
        # Median filter along angle axis
        corrected = []
        for row in sinogram:
            filtered_row = []
            for i in range(len(row)):
                neighbors = [row[max(0, i-1):min(len(row), i+2)]]
                flat = [v for sub in neighbors for v in sub]
                filtered_row.append(sorted(flat)[len(flat)//2])
            corrected.append(filtered_row)
        
        return corrected


class ComputedTomography:
    """
    Unified computed tomography controller.
    """
    
    def __init__(self, image_size: int = 64):
        """
        Args:
            image_size: Image size
        """
        self.radon = RadonTransform(image_size)
        self.fbp = FilteredBackprojection(image_size)
        self.corrector = CTArtifactCorrector()
        self.projections: Dict[float, List[float]] = {}
        self.reconstruction: Optional[List[List[float]]] = None
    
    def scan(self, image: List[List[float]],
            angles: List[float] = None,
            num_detectors: int = 64):
        """
        Simulate CT scan.
        
        Args:
            image: Object
            angles: Projection angles
            num_detectors: Detectors
        """
        if angles is None:
            angles = [i * 180.0 / 64 for i in range(64)]
        
        self.projections = self.radon.project(image, angles, num_detectors)
    
    def reconstruct_fbp(self) -> List[List[float]]:
        """
        Reconstruct with FBP.
        
        Returns:
            Reconstructed image
        """
        self.reconstruction = self.fbp.reconstruct(self.projections)
        return self.reconstruction
    
    def apply_corrections(self):
        """Apply artifact corrections."""
        corrected = {}
        for angle, proj in self.projections.items():
            corrected[angle] = self.corrector.beam_hardening_correction(proj)
        self.projections = corrected
    
    def ct_summary(self) -> Dict:
        """Get CT summary."""
        return {
            "image_size": self.radon.size,
            "projections": len(self.projections),
            "reconstructed": self.reconstruction is not None
        }
