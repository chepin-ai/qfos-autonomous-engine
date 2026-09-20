"""
X-ray Computed Tomography Module
Projection acquisition, filtered back-projection, cone-beam
reconstruction, and artifact reduction for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CTProjection:
    """CT projection data."""
    angle_deg: float
    detector_values: List[float]
    source_distance_mm: float
    detector_distance_mm: float


class ProjectionAcquirer:
    """
    Acquire CT projections.
    """
    
    def __init__(self, num_angles: int = 180,
                 num_detectors: int = 256):
        """
        Args:
            num_angles: Number of angles
            num_detectors: Detector count
        """
        self.num_angles = num_angles
        self.num_detectors = num_detectors
        self.angles: List[float] = []
    
    def generate_angles(self) -> List[float]:
        """
        Generate evenly spaced angles.
        
        Returns:
            Angles in degrees
        """
        self.angles = [i * 180.0 / self.num_angles
                      for i in range(self.num_angles)]
        return self.angles
    
    def simulate_projection(self, angle_deg: float,
                           phantom: List[List[float]],
                           phantom_size: int) -> List[float]:
        """
        Simulate projection at angle.
        
        Args:
            angle_deg: Angle
            phantom: Phantom image
            phantom_size: Size
        
        Returns:
            Detector values
        """
        import math
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        projection = []
        for d in range(self.num_detectors):
            # Detector position
            t = (d - self.num_detectors / 2.0) / self.num_detectors
            
            # Line integral through phantom
            value = 0.0
            for i in range(phantom_size):
                for j in range(phantom_size):
                    x = (j - phantom_size / 2.0) / phantom_size
                    y = (i - phantom_size / 2.0) / phantom_size
                    
                    # Rotate coordinates
                    xr = x * cos_a + y * sin_a
                    yr = -x * sin_a + y * cos_a
                    
                    if abs(yr - t) < 1.0 / phantom_size:
                        value += phantom[i][j]
            
            projection.append(value)
        
        return projection


class FilteredBackProjection:
    """
    Filtered back-projection reconstruction.
    """
    
    def __init__(self, image_size: int = 256):
        """
        Args:
            image_size: Reconstruction size
        """
        self.image_size = image_size
    
    def ramp_filter(self, projection: List[float]) -> List[float]:
        """
        Apply ramp filter.
        
        Args:
            projection: Projection
        
        Returns:
            Filtered projection
        """
        import math
        n = len(projection)
        
        # Simple ramp filter in frequency domain approximation
        filtered = []
        for i in range(n):
            # Approximate derivative
            if i == 0:
                d = projection[i + 1] - projection[i]
            elif i == n - 1:
                d = projection[i] - projection[i - 1]
            else:
                d = (projection[i + 1] - projection[i - 1]) / 2.0
            
            filtered.append(d)
        
        return filtered
    
    def back_project(self, projections: List[CTProjection]) -> List[List[float]]:
        """
        Back-project.
        
        Args:
            projections: Projections
        
        Returns:
            Reconstructed image
        """
        import math
        
        image = [[0.0 for _ in range(self.image_size)]
                for _ in range(self.image_size)]
        
        center = self.image_size / 2.0
        
        for proj in projections:
            rad = math.radians(proj.angle_deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            
            for i in range(self.image_size):
                for j in range(self.image_size):
                    x = j - center
                    y = i - center
                    
                    # Project onto detector
                    t = x * cos_a + y * sin_a
                    d_idx = int(t + len(proj.detector_values) / 2.0)
                    
                    if 0 <= d_idx < len(proj.detector_values):
                        image[i][j] += proj.detector_values[d_idx]
        
        # Normalize
        if projections:
            for i in range(self.image_size):
                for j in range(self.image_size):
                    image[i][j] /= len(projections)
        
        return image
    
    def reconstruct(self, projections: List[CTProjection]) -> List[List[float]]:
        """
        Full FBP reconstruction.
        
        Args:
            projections: Projections
        
        Returns:
            Reconstructed image
        """
        # Filter projections
        filtered = []
        for proj in projections:
            f = self.ramp_filter(proj.detector_values)
            filtered.append(CTProjection(
                proj.angle_deg, f,
                proj.source_distance_mm,
                proj.detector_distance_mm
            ))
        
        return self.back_project(filtered)


class ArtifactReducer:
    """
    Reduce CT artifacts.
    """
    
    def __init__(self):
        pass
    
    def ring_artifact_reduction(self, image: List[List[float]],
                                threshold: float = 0.1) -> List[List[float]]:
        """
        Reduce ring artifacts.
        
        Args:
            image: Image
            threshold: Threshold
        
        Returns:
            Corrected image
        """
        if not image or not image[0]:
            return image
        
        size = len(image)
        center = size / 2.0
        corrected = [row[:] for row in image]
        
        # Detect rings
        for i in range(size):
            for j in range(size):
                r = math.sqrt((i - center)**2 + (j - center)**2)
                ring_idx = int(r)
                
                # Simple correction: smooth radial profile
                if ring_idx > 0 and ring_idx < size // 2:
                    neighbors = []
                    for di in range(-1, 2):
                        for dj in range(-1, 2):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < size and 0 <= nj < size:
                                neighbors.append(image[ni][nj])
                    
                    if neighbors:
                        corrected[i][j] = sum(neighbors) / len(neighbors)
        
        return corrected
    
    def beam_hardening_correction(self, image: List[List[float]],
                                  coefficient: float = 0.001) -> List[List[float]]:
        """
        Correct beam hardening.
        
        Args:
            image: Image
            coefficient: Correction coefficient
        
        Returns:
            Corrected image
        """
        return [[max(0.0, v - coefficient * v**2) for v in row] for row in image]


class XRayComputedTomography:
    """
    Unified CT controller.
    """
    
    def __init__(self, image_size: int = 256):
        self.acquirer = ProjectionAcquirer()
        self.fbp = FilteredBackProjection(image_size)
        self.reducer = ArtifactReducer()
        self.projections: List[CTProjection] = []
        self.reconstructed: List[List[float]] = []
    
    def scan(self, phantom: List[List[float]],
            num_angles: int = 180):
        """
        Scan phantom.
        
        Args:
            phantom: Phantom
            num_angles: Number of angles
        """
        self.acquirer.num_angles = num_angles
        angles = self.acquirer.generate_angles()
        phantom_size = len(phantom)
        
        self.projections = []
        for angle in angles:
            det = self.acquirer.simulate_projection(angle, phantom, phantom_size)
            self.projections.append(CTProjection(angle, det, 500.0, 250.0))
    
    def reconstruct(self) -> List[List[float]]:
        """
        Reconstruct image.
        
        Returns:
            Reconstructed image
        """
        self.reconstructed = self.fbp.reconstruct(self.projections)
        self.reconstructed = self.reducer.ring_artifact_reduction(self.reconstructed)
        self.reconstructed = self.reducer.beam_hardening_correction(self.reconstructed)
        return self.reconstructed
    
    def inspect(self) -> Dict:
        """
        Inspect.
        
        Returns:
            Results
        """
        if not self.reconstructed:
            return {"mean": 0.0, "max": 0.0, "projections": len(self.projections)}
        
        flat = [v for row in self.reconstructed for v in row]
        return {
            "mean": sum(flat) / len(flat),
            "max": max(flat),
            "projections": len(self.projections)
        }
    
    def ct_summary(self) -> Dict:
        """Get summary."""
        return {
            "projections": len(self.projections),
            "image_size": self.fbp.image_size
        }
