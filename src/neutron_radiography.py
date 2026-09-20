"""
Neutron Radiography Module
Neutron attenuation calculation, image contrast enhancement,
scattering correction, and defect detection for NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MaterialProperties:
    """Material neutron properties."""
    name: str
    macroscopic_cross_section: float  # cm^-1
    density_g_cm3: float


class NeutronAttenuationCalculator:
    """
    Calculate neutron attenuation.
    """
    
    def __init__(self):
        self.materials: Dict[str, MaterialProperties] = {}
    
    def register_material(self, props: MaterialProperties):
        """
        Register material.
        
        Args:
            props: Properties
        """
        self.materials[props.name] = props
    
    def attenuation(self, material: str,
                   thickness_cm: float) -> float:
        """
        Compute attenuation factor.
        
        Args:
            material: Material name
            thickness_cm: Thickness
        
        Returns:
            Attenuation factor (transmission)
        """
        if material not in self.materials:
            return 1.0
        
        sigma = self.materials[material].macroscopic_cross_section
        return math.exp(-sigma * thickness_cm)
    
    def transmitted_flux(self, incident_flux: float,
                        material: str,
                        thickness_cm: float) -> float:
        """
        Compute transmitted neutron flux.
        
        Args:
            incident_flux: Incident flux
            material: Material
            thickness_cm: Thickness
        
        Returns:
            Transmitted flux
        """
        return incident_flux * self.attenuation(material, thickness_cm)


class ContrastEnhancer:
    """
    Enhance neutron radiograph contrast.
    """
    
    def __init__(self):
        pass
    
    def normalize(self, image: List[float]) -> List[float]:
        """
        Normalize image.
        
        Args:
            image: Image data
        
        Returns:
            Normalized image
        """
        if not image:
            return []
        
        min_val = min(image)
        max_val = max(image)
        
        if max_val == min_val:
            return [0.5] * len(image)
        
        return [(v - min_val) / (max_val - min_val) for v in image]
    
    def histogram_equalize(self, image: List[float],
                          bins: int = 256) -> List[float]:
        """
        Histogram equalization.
        
        Args:
            image: Image
            bins: Bins
        
        Returns:
            Equalized image
        """
        if not image:
            return []
        
        # Simple histogram equalization
        hist = [0] * bins
        for v in image:
            idx = min(int(v * bins), bins - 1)
            hist[idx] += 1
        
        # CDF
        cdf = [0] * bins
        cdf[0] = hist[0]
        for i in range(1, bins):
            cdf[i] = cdf[i - 1] + hist[i]
        
        total = len(image)
        equalized = []
        for v in image:
            idx = min(int(v * bins), bins - 1)
            eq = cdf[idx] / total
            equalized.append(eq)
        
        return equalized


class ScatteringCorrector:
    """
    Correct for neutron scattering.
    """
    
    def __init__(self, scatter_fraction: float = 0.1):
        """
        Args:
            scatter_fraction: Scattering fraction
        """
        self.scatter = scatter_fraction
    
    def correct(self, measured_image: List[float],
               direct_image: Optional[List[float]] = None) -> List[float]:
        """
        Correct scattering.
        
        Args:
            measured_image: Measured
            direct_image: Direct component
        
        Returns:
            Corrected image
        """
        if direct_image is None:
            # Assume scattered component is scatter_fraction * measured
            return [v / (1.0 + self.scatter) for v in measured_image]
        
        return [m - self.scatter * d for m, d in zip(measured_image, direct_image)]


class NeutronDefectDetector:
    """
    Detect defects in neutron radiographs.
    """
    
    def __init__(self, threshold: float = 0.2):
        """
        Args:
            threshold: Detection threshold
        """
        self.threshold = threshold
    
    def detect(self, image: List[float],
              width: int, height: int) -> List[Dict]:
        """
        Detect defects.
        
        Args:
            image: Image
            width: Width
            height: Height
        
        Returns:
            Defects
        """
        # Simple threshold-based detection
        defects = []
        mean = sum(image) / len(image) if image else 0.0
        
        visited = set()
        for i, v in enumerate(image):
            if i in visited:
                continue
            
            if abs(v - mean) > self.threshold * mean:
                region = self._flood_fill(image, width, height,
                                         i, mean, visited)
                if region:
                    vals = [image[idx] for idx in region]
                    defects.append({
                        "size": len(region),
                        "contrast": max(abs(v - mean) for v in vals) / mean if mean else 0.0,
                        "center": self._center(region, width)
                    })
        
        return defects
    
    def _flood_fill(self, image: List[float], w: int, h: int,
                   start: int, mean: float, visited: set) -> List[int]:
        """Flood fill."""
        region = []
        stack = [start]
        
        while stack:
            idx = stack.pop()
            if idx in visited or idx < 0 or idx >= len(image):
                continue
            
            if abs(image[idx] - mean) <= self.threshold * mean:
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


class NeutronRadiography:
    """
    Unified neutron radiography controller.
    """
    
    def __init__(self):
        self.attenuation = NeutronAttenuationCalculator()
        self.enhancer = ContrastEnhancer()
        self.scatter = ScatteringCorrector()
        self.detector = NeutronDefectDetector()
        self.image: List[float] = []
    
    def register_material(self, name: str,
                         macroscopic_cs: float,
                         density: float):
        """
        Register material.
        
        Args:
            name: Name
            macroscopic_cs: Cross section
            density: Density
        """
        self.attenuation.register_material(
            MaterialProperties(name, macroscopic_cs, density)
        )
    
    def capture(self, raw_image: List[float]):
        """
        Capture image.
        
        Args:
            raw_image: Raw image
        """
        self.image = raw_image[:]
    
    def process(self) -> List[float]:
        """
        Process image.
        
        Returns:
            Processed image
        """
        # Correct scattering
        corrected = self.scatter.correct(self.image)
        # Enhance contrast
        enhanced = self.enhancer.normalize(corrected)
        return enhanced
    
    def inspect(self, width: int, height: int) -> Dict:
        """
        Inspect for defects.
        
        Args:
            width: Width
            height: Height
        
        Returns:
            Results
        """
        processed = self.process()
        defects = self.detector.detect(processed, width, height)
        
        return {
            "defects": len(defects),
            "regions": defects[:3]
        }
    
    def nr_summary(self) -> Dict:
        """Get summary."""
        return {
            "image_size": len(self.image),
            "materials": len(self.attenuation.materials)
        }
