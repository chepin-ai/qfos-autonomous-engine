"""
Positron Emission Tomography Module
Coincidence detection, sinogram formation, tomographic
reconstruction, and tracer uptake analysis for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PETEvent:
    """PET coincidence event."""
    x1_mm: float
    y1_mm: float
    x2_mm: float
    y2_mm: float
    time_ns: float
    energy_keV: float


class CoincidenceDetector:
    """
    Detect coincident gamma rays.
    """
    
    def __init__(self, time_window_ns: float = 5.0,
                 energy_window_keV: Tuple[float, float] = (350.0, 650.0)):
        """
        Args:
            time_window_ns: Coincidence window
            energy_window_keV: Energy window
        """
        self.time_window = time_window_ns
        self.energy_min = energy_window_keV[0]
        self.energy_max = energy_window_keV[1]
        self.events: List[PETEvent] = []
    
    def detect(self, singles: List[Dict]) -> List[PETEvent]:
        """
        Detect coincidences from singles.
        
        Args:
            singles: Single events
        
        Returns:
            Coincidence events
        """
        events = []
        
        for i in range(len(singles)):
            for j in range(i + 1, len(singles)):
                s1 = singles[i]
                s2 = singles[j]
                
                # Time coincidence
                if abs(s1["time_ns"] - s2["time_ns"]) > self.time_window:
                    continue
                
                # Energy check
                e1 = s1.get("energy_keV", 511.0)
                e2 = s2.get("energy_keV", 511.0)
                if not (self.energy_min <= e1 <= self.energy_max):
                    continue
                if not (self.energy_min <= e2 <= self.energy_max):
                    continue
                
                events.append(PETEvent(
                    s1["x_mm"], s1["y_mm"],
                    s2["x_mm"], s2["y_mm"],
                    (s1["time_ns"] + s2["time_ns"]) / 2.0,
                    (e1 + e2) / 2.0
                ))
        
        self.events = events
        return events
    
    def count_rate(self, acquisition_time_s: float) -> float:
        """
        Compute count rate.
        
        Args:
            acquisition_time_s: Time
        
        Returns:
            Counts per second
        """
        if acquisition_time_s <= 0:
            return 0.0
        return len(self.events) / acquisition_time_s


class SinogramFormer:
    """
    Form sinogram from PET events.
    """
    
    def __init__(self, num_angles: int = 180,
                 num_r_bins: int = 128,
                 fov_mm: float = 200.0):
        """
        Args:
            num_angles: Angular bins
            num_r_bins: Radial bins
            fov_mm: Field of view
        """
        self.num_angles = num_angles
        self.num_r = num_r_bins
        self.fov = fov_mm
        self.sinogram: List[List[float]] = [
            [0.0 for _ in range(num_r_bins)] for _ in range(num_angles)
        ]
    
    def line_of_response(self, event: PETEvent) -> Tuple[float, float]:
        """
        Compute LOR parameters.
        
        Args:
            event: Event
        
        Returns:
            (angle_rad, distance_mm)
        """
        dx = event.x2_mm - event.x1_mm
        dy = event.y2_mm - event.y1_mm
        
        angle = math.atan2(dy, dx)
        
        # Distance from origin
        mid_x = (event.x1_mm + event.x2_mm) / 2.0
        mid_y = (event.y1_mm + event.y2_mm) / 2.0
        
        perp_angle = angle + math.pi / 2.0
        distance = abs(mid_x * math.cos(perp_angle) + mid_y * math.sin(perp_angle))
        
        return angle, distance
    
    def add_event(self, event: PETEvent):
        """
        Add event to sinogram.
        
        Args:
            event: Event
        """
        angle, distance = self.line_of_response(event)
        
        angle_idx = int((angle + math.pi) / (2.0 * math.pi) * self.num_angles)
        angle_idx = max(0, min(angle_idx, self.num_angles - 1))
        
        r_idx = int((distance + self.fov / 2.0) / self.fov * self.num_r)
        r_idx = max(0, min(r_idx, self.num_r - 1))
        
        self.sinogram[angle_idx][r_idx] += 1.0
    
    def form(self, events: List[PETEvent]) -> List[List[float]]:
        """
        Form sinogram from events.
        
        Args:
            events: Events
        
        Returns:
            Sinogram
        """
        self.sinogram = [[0.0 for _ in range(self.num_r)]
                        for _ in range(self.num_angles)]
        
        for event in events:
            self.add_event(event)
        
        return self.sinogram


class PETReconstructor:
    """
    Reconstruct PET image.
    """
    
    def __init__(self, image_size: int = 128):
        """
        Args:
            image_size: Image size
        """
        self.image_size = image_size
    
    def simple_back_project(self, sinogram: List[List[float]],
                           num_angles: int,
                           fov_mm: float) -> List[List[float]]:
        """
        Simple back-projection.
        
        Args:
            sinogram: Sinogram
            num_angles: Angles
            fov_mm: FOV
        
        Returns:
            Image
        """
        image = [[0.0 for _ in range(self.image_size)]
                for _ in range(self.image_size)]
        
        center = self.image_size / 2.0
        scale = self.image_size / fov_mm
        
        for angle_idx in range(num_angles):
            angle = angle_idx * math.pi / num_angles
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            for i in range(self.image_size):
                for j in range(self.image_size):
                    x = (j - center) / scale
                    y = (i - center) / scale
                    
                    r = x * cos_a + y * sin_a
                    r_idx = int((r + fov_mm / 2.0) / fov_mm * len(sinogram[0]))
                    
                    if 0 <= r_idx < len(sinogram[0]):
                        image[i][j] += sinogram[angle_idx][r_idx]
        
        # Normalize
        if num_angles > 0:
            for i in range(self.image_size):
                for j in range(self.image_size):
                    image[i][j] /= num_angles
        
        return image


class TracerUptakeAnalyzer:
    """
    Analyze tracer uptake.
    """
    
    def __init__(self):
        pass
    
    def roi_uptake(self, image: List[List[float]],
                  roi_mask: List[List[bool]]) -> float:
        """
        Compute ROI uptake.
        
        Args:
            image: Image
            roi_mask: ROI mask
        
        Returns:
            Mean uptake
        """
        total = 0.0
        count = 0
        
        for i in range(len(image)):
            for j in range(len(image[0])):
                if roi_mask[i][j]:
                    total += image[i][j]
                    count += 1
        
        return total / count if count > 0 else 0.0
    
    def suv(self, activity_kBq: float,
           dose_mCi: float,
           weight_kg: float) -> float:
        """
        Compute standardized uptake value.
        
        Args:
            activity_kBq: Activity
            dose_mCi: Dose
            weight_kg: Weight
        
        Returns:
            SUV
        """
        if dose_mCi <= 0 or weight_kg <= 0:
            return 0.0
        
        # SUV = activity / (dose / weight)
        return activity_kBq / (dose_mCi * 37.0 / weight_kg)


class PositronEmissionTomography:
    """
    Unified PET controller.
    """
    
    def __init__(self, image_size: int = 128):
        self.detector = CoincidenceDetector()
        self.sinogram = SinogramFormer()
        self.reconstructor = PETReconstructor(image_size)
        self.uptake = TracerUptakeAnalyzer()
        self.events: List[PETEvent] = []
        self.image: List[List[float]] = []
    
    def acquire(self, singles: List[Dict]):
        """
        Acquire data.
        
        Args:
            singles: Single events
        """
        self.events = self.detector.detect(singles)
    
    def reconstruct(self) -> List[List[float]]:
        """
        Reconstruct image.
        
        Returns:
            Image
        """
        sino = self.sinogram.form(self.events)
        self.image = self.reconstructor.simple_back_project(
            sino, self.sinogram.num_angles, self.sinogram.fov
        )
        return self.image
    
    def inspect(self) -> Dict:
        """
        Inspect.
        
        Returns:
            Results
        """
        if not self.image:
            return {"events": 0, "max_uptake": 0.0}
        
        flat = [v for row in self.image for v in row]
        return {
            "events": len(self.events),
            "max_uptake": max(flat) if flat else 0.0,
            "mean_uptake": sum(flat) / len(flat) if flat else 0.0
        }
    
    def pet_summary(self) -> Dict:
        """Get summary."""
        return {
            "events": len(self.events),
            "image_size": self.reconstructor.image_size
        }
