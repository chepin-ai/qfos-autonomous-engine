"""
Phased Array Ultrasonic Testing Module
Beam steering, focal law generation, sector scanning, and dynamic
depth focusing for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ProbeElement:
    """PA probe element."""
    position_mm: float
    pitch_mm: float
    frequency_MHz: float
    diameter_mm: float


class DelayLawGenerator:
    """
    Generate delay laws for beam steering and focusing.
    """
    
    def __init__(self, velocity_mm_us: float = 5.9):
        """
        Args:
            velocity_mm_us: Velocity
        """
        self.v = velocity_mm_us
    
    def steering_delays(self, elements: List[ProbeElement],
                       angle_deg: float) -> List[float]:
        """
        Compute steering delays.
        
        Args:
            elements: Elements
            angle_deg: Steering angle
        
        Returns:
            Delays in microseconds
        """
        angle_rad = math.radians(angle_deg)
        delays = []
        
        for i, el in enumerate(elements):
            # Time delay for element i
            delay = el.position_mm * math.sin(angle_rad) / self.v
            delays.append(delay)
        
        # Normalize to minimum = 0
        min_delay = min(delays)
        return [d - min_delay for d in delays]
    
    def focusing_delays(self, elements: List[ProbeElement],
                       focal_depth_mm: float) -> List[float]:
        """
        Compute focusing delays.
        
        Args:
            elements: Elements
            focal_depth_mm: Focal depth
        
        Returns:
            Delays
        """
        delays = []
        
        for el in elements:
            # Distance from element to focal point
            dist = math.sqrt(el.position_mm**2 + focal_depth_mm**2)
            delay = dist / self.v
            delays.append(delay)
        
        # Normalize
        min_delay = min(delays)
        return [d - min_delay for d in delays]
    
    def combined_delays(self, elements: List[ProbeElement],
                       angle_deg: float,
                       focal_depth_mm: float) -> List[float]:
        """
        Combined steering and focusing delays.
        
        Args:
            elements: Elements
            angle_deg: Angle
            focal_depth_mm: Depth
        
        Returns:
            Delays
        """
        steer = self.steering_delays(elements, angle_deg)
        focus = self.focusing_delays(elements, focal_depth_mm)
        combined = [s + f for s, f in zip(steer, focus)]
        
        min_delay = min(combined)
        return [d - min_delay for d in combined]


class BeamSteerer:
    """
    Beam steering controller.
    """
    
    def __init__(self, num_elements: int = 16,
                 pitch_mm: float = 1.0):
        """
        Args:
            num_elements: Elements
            pitch_mm: Pitch
        """
        self.elements = []
        for i in range(num_elements):
            pos = (i - (num_elements - 1) / 2.0) * pitch_mm
            self.elements.append(ProbeElement(pos, pitch_mm, 5.0, 0.5))
        
        self.delay_gen = DelayLawGenerator()
        self.active_aperture = num_elements
        self.start_idx = 0
    
    def set_aperture(self, start: int, count: int):
        """
        Set active aperture.
        
        Args:
            start: Start index
            count: Element count
        """
        self.active_aperture = min(count, len(self.elements) - start)
        self.start_idx = start
    
    def steer(self, angle_deg: float) -> List[float]:
        """
        Get steering delays.
        
        Args:
            angle_deg: Angle
        
        Returns:
            Delays
        """
        active = self.elements[self.start_idx:self.start_idx + self.active_aperture]
        return self.delay_gen.steering_delays(active, angle_deg)


class SectorScanner:
    """
    Sector scan (S-scan) generator.
    """
    
    def __init__(self, beam_steerer: BeamSteerer,
                 min_angle_deg: float = -45.0,
                 max_angle_deg: float = 45.0,
                 angle_step_deg: float = 1.0):
        """
        Args:
            beam_steerer: Beam steerer
            min_angle_deg: Min angle
            max_angle_deg: Max angle
            angle_step_deg: Step
        """
        self.steerer = beam_steerer
        self.min_angle = min_angle_deg
        self.max_angle = max_angle_deg
        self.step = angle_step_deg
        self.angles: List[float] = []
        self.delays: List[List[float]] = []
    
    def generate_scan(self):
        """Generate scan angles and delays."""
        self.angles = []
        self.delays = []
        
        angle = self.min_angle
        while angle <= self.max_angle:
            self.angles.append(angle)
            self.delays.append(self.steerer.steer(angle))
            angle += self.step
    
    def num_beams(self) -> int:
        """Get beam count."""
        return len(self.angles)


class DynamicDepthFocuser:
    """
    Dynamic depth focusing.
    """
    
    def __init__(self, delay_gen: DelayLawGenerator,
                 elements: List[ProbeElement]):
        """
        Args:
            delay_gen: Delay generator
            elements: Elements
        """
        self.delay_gen = delay_gen
        self.elements = elements
    
    def focus_at_depth(self, depth_mm: float) -> List[float]:
        """
        Focus at depth.
        
        Args:
            depth_mm: Depth
        
        Returns:
            Delays
        """
        return self.delay_gen.focusing_delays(self.elements, depth_mm)
    
    def depth_scan(self, min_depth: float, max_depth: float,
                  step: float) -> Dict[float, List[float]]:
        """
        Scan depth range.
        
        Args:
            min_depth: Min depth
            max_depth: Max depth
            step: Step
        
        Returns:
            Depth to delays mapping
        """
        result = {}
        depth = min_depth
        while depth <= max_depth:
            result[depth] = self.focus_at_depth(depth)
            depth += step
        return result


class PhasedArrayUT:
    """
    Unified phased array UT controller.
    """
    
    def __init__(self):
        self.beam = BeamSteerer()
        self.sector = SectorScanner(self.beam)
        self.ddf = DynamicDepthFocuser(
            DelayLawGenerator(), self.beam.elements
        )
        self.scan_results: List[Dict] = []
    
    def perform_sector_scan(self):
        """Perform sector scan."""
        self.sector.generate_scan()
        result = {
            "beams": self.sector.num_beams(),
            "angles": self.sector.angles[:5]
        }
        self.scan_results.append(result)
        return result
    
    def focus_depths(self, min_d: float, max_d: float,
                    step: float) -> Dict:
        """
        Focus at depths.
        
        Args:
            min_d: Min depth
            max_d: Max depth
            step: Step
        
        Returns:
            Depth focus map
        """
        return self.ddf.depth_scan(min_d, max_d, step)
    
    def pa_summary(self) -> Dict:
        """Get summary."""
        return {
            "elements": len(self.beam.elements),
            "aperture": self.beam.active_aperture,
            "beams": self.sector.num_beams(),
            "scans": len(self.scan_results)
        }
