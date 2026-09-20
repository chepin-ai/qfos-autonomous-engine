"""
Liquid Penetrant Testing Module
Penetrant application, dwell time control, developer application,
indication detection, and defect characterization for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PenetrantIndication:
    """Penetrant indication."""
    x_mm: float
    y_mm: float
    area_mm2: float
    intensity: float
    shape: str


class PenetrantApplicator:
    """
    Apply penetrant.
    """
    
    def __init__(self, penetrant_type: str = "visible",
                 viscosity_cSt: float = 5.0):
        """
        Args:
            penetrant_type: Type
            viscosity_cSt: Viscosity
        """
        self.type = penetrant_type
        self.viscosity = viscosity_cSt
    
    def dwell_time(self, material_thickness_mm: float,
                   temperature_C: float = 20.0) -> float:
        """
        Compute recommended dwell time.
        
        Args:
            material_thickness_mm: Thickness
            temperature_C: Temperature
        
        Returns:
            Dwell time in minutes
        """
        # Base time
        base = 10.0
        
        # Thickness factor
        if material_thickness_mm > 25.0:
            base += 10.0
        elif material_thickness_mm > 12.0:
            base += 5.0
        
        # Temperature factor
        if temperature_C < 10.0:
            base *= 1.5
        elif temperature_C > 50.0:
            base *= 0.8
        
        return base
    
    def coverage(self, surface_area_mm2: float,
                application_rate_ml_per_mm2: float = 0.001) -> float:
        """
        Compute penetrant volume.
        
        Args:
            surface_area_mm2: Area
            application_rate_ml_per_mm2: Rate
        
        Returns:
            Volume in mL
        """
        return surface_area_mm2 * application_rate_ml_per_mm2


class DeveloperApplicator:
    """
    Apply developer.
    """
    
    def __init__(self, developer_type: str = "dry"):
        """
        Args:
            developer_type: Type
        """
        self.type = developer_type
    
    def development_time(self, penetrant_type: str) -> float:
        """
        Compute development time.
        
        Args:
            penetrant_type: Penetrant type
        
        Returns:
            Time in minutes
        """
        if penetrant_type == "fluorescent":
            return 10.0
        return 7.0
    
    def thickness(self, application_rate_g_per_mm2: float = 0.0005,
                 surface_area_mm2: float = 10000.0) -> float:
        """
        Compute developer thickness.
        
        Args:
            application_rate_g_per_mm2: Rate
            surface_area_mm2: Area
        
        Returns:
            Thickness in mm
        """
        density_g_per_mm3 = 0.0015
        mass = application_rate_g_per_mm2 * surface_area_mm2
        return mass / (surface_area_mm2 * density_g_per_mm3)


class PenetrantIndicationDetector:
    """
    Detect penetrant indications.
    """
    
    def __init__(self, min_area_mm2: float = 0.5,
                 min_intensity: float = 0.1):
        """
        Args:
            min_area_mm2: Minimum area
            min_intensity: Minimum intensity
        """
        self.min_area = min_area_mm2
        self.min_intensity = min_intensity
    
    def detect(self, image: List[List[float]],
              pixel_size_mm: float) -> List[PenetrantIndication]:
        """
        Detect indications.
        
        Args:
            image: Intensity image
            pixel_size_mm: Pixel size
        
        Returns:
            Indications
        """
        indications = []
        visited = set()
        
        for i in range(len(image)):
            for j in range(len(image[0])):
                if image[i][j] > self.min_intensity and (i, j) not in visited:
                    # Flood fill
                    cluster = []
                    stack = [(i, j)]
                    while stack:
                        x, y = stack.pop()
                        if (x, y) in visited:
                            continue
                        if x < 0 or x >= len(image) or y < 0 or y >= len(image[0]):
                            continue
                        if image[x][y] <= self.min_intensity:
                            continue
                        visited.add((x, y))
                        cluster.append((x, y))
                        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
                    
                    if cluster:
                        area = len(cluster) * pixel_size_mm ** 2
                        if area >= self.min_area:
                            cx = sum(p[1] for p in cluster) / len(cluster) * pixel_size_mm
                            cy = sum(p[0] for p in cluster) / len(cluster) * pixel_size_mm
                            max_intensity = max(image[p[0]][p[1]] for p in cluster)
                            indications.append(PenetrantIndication(
                                x_mm=cx, y_mm=cy, area_mm2=area,
                                intensity=max_intensity,
                                shape="linear" if len(cluster) > 3 else "point"
                            ))
        
        return indications
    
    def classify_defect(self, indication: PenetrantIndication) -> str:
        """
        Classify defect.
        
        Args:
            indication: Indication
        
        Returns:
            Classification
        """
        if indication.area_mm2 < 1.0:
            return "minor"
        elif indication.area_mm2 < 5.0:
            return "moderate"
        else:
            return "severe"


class LiquidPenetrantTesting:
    """
    Unified liquid penetrant testing controller.
    """
    
    def __init__(self):
        self.penetrant = PenetrantApplicator()
        self.developer = DeveloperApplicator()
        self.detector = PenetrantIndicationDetector()
        self.indications: List[PenetrantIndication] = []
    
    def inspect(self, image: List[List[float]],
               pixel_size_mm: float,
               material_thickness_mm: float) -> Dict:
        """
        Inspect surface.
        
        Args:
            image: Image
            pixel_size_mm: Pixel size
            material_thickness_mm: Thickness
        
        Returns:
            Results
        """
        self.indications = self.detector.detect(image, pixel_size_mm)
        
        dwell = self.penetrant.dwell_time(material_thickness_mm)
        dev_time = self.developer.development_time(self.penetrant.type)
        
        classifications = {}
        for ind in self.indications:
            c = self.detector.classify_defect(ind)
            classifications[c] = classifications.get(c, 0) + 1
        
        return {
            "indications": len(self.indications),
            "dwell_time_min": dwell,
            "development_time_min": dev_time,
            "classifications": classifications
        }
    
    def lpt_summary(self) -> Dict:
        """Get summary."""
        return {
            "indications": len(self.indications),
            "penetrant_type": self.penetrant.type
        }
