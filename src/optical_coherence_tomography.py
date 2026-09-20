"""
Optical Coherence Tomography Module
A-scan processing, B-scan reconstruction, depth profiling,
and layer segmentation for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AScan:
    """A-scan data."""
    depth_mm: List[float]
    intensity: List[float]
    lateral_position_mm: float


class AScanProcessor:
    """
    Process A-scan signals.
    """
    
    def __init__(self):
        pass
    
    def envelope(self, signal: List[float]) -> List[float]:
        """
        Compute signal envelope.
        
        Args:
            signal: Input signal
        
        Returns:
            Envelope
        """
        if not signal:
            return []
        
        # Hilbert transform approximation
        env = []
        for i in range(len(signal)):
            # Local maxima approximation
            window = 3
            start = max(0, i - window)
            end = min(len(signal), i + window + 1)
            local_max = max(abs(signal[j]) for j in range(start, end))
            env.append(local_max)
        
        return env
    
    def peak_positions(self, envelope: List[float],
                      depth_mm: List[float],
                      threshold: float = 0.3) -> List[Tuple[float, float]]:
        """
        Find peak positions.
        
        Args:
            envelope: Envelope
            depth_mm: Depth positions
            threshold: Threshold
        
        Returns:
            (depth, intensity) peaks
        """
        if not envelope:
            return []
        
        max_env = max(envelope)
        peaks = []
        
        for i in range(1, len(envelope) - 1):
            if envelope[i] > threshold * max_env:
                if envelope[i] > envelope[i - 1] and envelope[i] > envelope[i + 1]:
                    peaks.append((depth_mm[i], envelope[i]))
        
        return peaks


class BScanReconstructor:
    """
    Reconstruct B-scan from A-scans.
    """
    
    def __init__(self):
        self.ascans: List[AScan] = []
    
    def add_ascan(self, ascan: AScan):
        """
        Add A-scan.
        
        Args:
            ascan: A-scan
        """
        self.ascans.append(ascan)
    
    def reconstruct(self) -> List[List[float]]:
        """
        Reconstruct B-scan image.
        
        Returns:
            2D image (lateral x depth)
        """
        if not self.ascans:
            return []
        
        # Create image matrix
        num_depth = len(self.ascans[0].intensity)
        image = []
        
        for ascan in self.ascans:
            row = ascan.intensity[:]
            # Pad if needed
            while len(row) < num_depth:
                row.append(0.0)
            image.append(row[:num_depth])
        
        return image
    
    def lateral_positions(self) -> List[float]:
        """
        Get lateral positions.
        
        Returns:
            Positions
        """
        return [a.lateral_position_mm for a in self.ascans]


class DepthProfiler:
    """
    Profile depth characteristics.
    """
    
    def __init__(self):
        pass
    
    def attenuation_coefficient(self, intensities: List[float],
                               depths_mm: List[float]) -> float:
        """
        Compute attenuation coefficient.
        
        Args:
            intensities: Intensities
            depths_mm: Depths
        
        Returns:
            Attenuation coefficient (1/mm)
        """
        if len(intensities) < 2 or len(depths_mm) < 2:
            return 0.0
        
        # Fit exponential decay
        log_intensities = [math.log(max(i, 1e-10)) for i in intensities]
        
        # Linear regression
        n = len(log_intensities)
        sum_x = sum(depths_mm)
        sum_y = sum(log_intensities)
        sum_xy = sum(d * l for d, l in zip(depths_mm, log_intensities))
        sum_xx = sum(d**2 for d in depths_mm)
        
        denom = n * sum_xx - sum_x**2
        if denom == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        return -slope
    
    def penetration_depth(self, intensities: List[float],
                         depths_mm: List[float],
                         threshold: float = 0.1) -> float:
        """
        Find penetration depth.
        
        Args:
            intensities: Intensities
            depths_mm: Depths
            threshold: Threshold fraction
        
        Returns:
            Penetration depth
        """
        if not intensities:
            return 0.0
        
        max_int = max(intensities)
        thresh = threshold * max_int
        
        for i, intensity in enumerate(intensities):
            if intensity < thresh and i > 0:
                return depths_mm[i]
        
        return depths_mm[-1] if depths_mm else 0.0


class LayerSegmenter:
    """
    Segment layers in OCT data.
    """
    
    def __init__(self):
        pass
    
    def segment(self, bscan: List[List[float]],
               depth_mm: List[float]) -> List[Dict]:
        """
        Segment layers.
        
        Args:
            bscan: B-scan image
            depth_mm: Depth positions
        
        Returns:
            Layer boundaries
        """
        if not bscan or not bscan[0]:
            return []
        
        # Find layer boundaries from intensity transitions
        num_depth = len(bscan[0])
        avg_profile = [sum(bscan[i][j] for i in range(len(bscan))) / len(bscan)
                      for j in range(num_depth)]
        
        # Find peaks in derivative
        layers = []
        for j in range(1, num_depth - 1):
            derivative = avg_profile[j + 1] - avg_profile[j - 1]
            if abs(derivative) > 0.1 * max(abs(v) for v in avg_profile):
                layers.append({
                    "depth_mm": depth_mm[j] if j < len(depth_mm) else j,
                    "intensity": avg_profile[j],
                    "type": "boundary" if derivative > 0 else "interface"
                })
        
        return layers[:5]


class OpticalCoherenceTomography:
    """
    Unified OCT controller.
    """
    
    def __init__(self):
        self.processor = AScanProcessor()
        self.reconstructor = BScanReconstructor()
        self.profiler = DepthProfiler()
        self.segmenter = LayerSegmenter()
    
    def capture_ascan(self, depth_mm: List[float],
                     intensity: List[float],
                     lateral_mm: float = 0.0):
        """
        Capture A-scan.
        
        Args:
            depth_mm: Depths
            intensity: Intensities
            lateral_mm: Lateral position
        """
        ascan = AScan(depth_mm, intensity, lateral_mm)
        self.reconstructor.add_ascan(ascan)
    
    def inspect(self) -> Dict:
        """
        Inspect structure.
        
        Returns:
            Results
        """
        bscan = self.reconstructor.reconstruct()
        
        if not bscan or not bscan[0]:
            return {"layers": 0, "penetration_mm": 0.0}
        
        # Get depth axis from first A-scan
        depth_mm = self.reconstructor.ascans[0].depth_mm if self.reconstructor.ascans else []
        
        layers = self.segmenter.segment(bscan, depth_mm)
        
        # Compute average profile for penetration depth
        avg_profile = [sum(bscan[i][j] for i in range(len(bscan))) / len(bscan)
                      for j in range(len(bscan[0]))]
        
        penetration = self.profiler.penetration_depth(avg_profile, depth_mm)
        
        return {
            "layers": len(layers),
            "penetration_mm": penetration,
            "ascans": len(self.reconstructor.ascans)
        }
    
    def oct_summary(self) -> Dict:
        """Get summary."""
        return {
            "ascans": len(self.reconstructor.ascans),
            "lateral_range_mm": (min(self.reconstructor.lateral_positions()) if self.reconstructor.ascans else 0.0,
                                 max(self.reconstructor.lateral_positions()) if self.reconstructor.ascans else 0.0)
        }
