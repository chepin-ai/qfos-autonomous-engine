"""
Phased Array Ultrasonic Testing Module
PAUT beam steering, focal law computation, sectorial scanning,
and total focusing method (TFM) for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AScan:
    """Single A-scan signal."""
    element_id: int
    time_us: float
    amplitude: float
    depth_mm: float = 0.0


class PAElement:
    """
    Single phased array element.
    """
    
    def __init__(self, element_id: int, position_mm: float,
                 pitch_mm: float = 1.0, frequency_MHz: float = 5.0):
        """
        Args:
            element_id: Element ID
            position_mm: X position
            pitch_mm: Pitch
            frequency_MHz: Frequency
        """
        self.element_id = element_id
        self.position = position_mm
        self.pitch = pitch_mm
        self.frequency = frequency_MHz
        self.wavelength_mm = 1.5 / frequency_MHz  # In steel
    
    def delay_for_angle(self, angle_deg: float,
                       velocity_mm_us: float = 5.9) -> float:
        """
        Compute transmit delay for beam angle.
        
        Args:
            angle_deg: Beam angle
            velocity_mm_us: Material velocity
        
        Returns:
            Delay in microseconds
        """
        angle_rad = math.radians(angle_deg)
        # Delay proportional to position * sin(angle)
        delay = self.position * math.sin(angle_rad) / velocity_mm_us
        return delay
    
    def focal_delay(self, focal_depth_mm: float,
                   velocity_mm_us: float = 5.9) -> float:
        """
        Compute focal delay.
        
        Args:
            focal_depth_mm: Focal depth
            velocity_mm_us: Velocity
        
        Returns:
            Delay
        """
        # Distance to focal point
        dist = math.sqrt(self.position**2 + focal_depth_mm**2)
        return dist / velocity_mm_us


class PAProbe:
    """
    Phased array probe controller.
    """
    
    def __init__(self, num_elements: int = 16,
                 pitch_mm: float = 1.0,
                 frequency_MHz: float = 5.0):
        """
        Args:
            num_elements: Elements
            pitch_mm: Pitch
            frequency_MHz: Frequency
        """
        self.num_elements = num_elements
        self.pitch = pitch_mm
        self.frequency = frequency_MHz
        self.elements: List[PAElement] = []
        self._build()
    
    def _build(self):
        """Initialize elements."""
        for i in range(self.num_elements):
            pos = (i - self.num_elements / 2.0 + 0.5) * self.pitch
            self.elements.append(PAElement(i, pos, self.pitch, self.frequency))
    
    def focal_law(self, angle_deg: float = 0.0,
                 focal_depth_mm: Optional[float] = None,
                 aperture_elements: Optional[int] = None) -> List[float]:
        """
        Compute focal law delays.
        
        Args:
            angle_deg: Beam angle
            focal_depth_mm: Focal depth
            aperture_elements: Active aperture
        
        Returns:
            Delays per element
        """
        aperture = aperture_elements or self.num_elements
        delays = []
        
        for elem in self.elements:
            d = elem.delay_for_angle(angle_deg)
            if focal_depth_mm is not None:
                d += elem.focal_delay(focal_depth_mm)
            delays.append(d)
        
        # Normalize to first element = 0
        min_d = min(delays[:aperture]) if delays else 0.0
        return [d - min_d for d in delays]
    
    def beam_spread(self, angle_deg: float,
                   wavelength_mm: Optional[float] = None) -> float:
        """
        Compute beam spread angle.
        
        Args:
            angle_deg: Beam angle
            wavelength_mm: Wavelength
        
        Returns:
            Spread in degrees
        """
        wl = wavelength_mm or self.elements[0].wavelength_mm if self.elements else 1.0
        aperture = self.num_elements * self.pitch
        # sin(theta) ~ lambda / aperture
        spread_rad = math.asin(min(1.0, wl / max(aperture, 0.001)))
        return math.degrees(spread_rad)


class SectorialScan:
    """
    Sectorial (S-scan) imaging.
    """
    
    def __init__(self, probe: PAProbe):
        """
        Args:
            probe: PA probe
        """
        self.probe = probe
        self.angles: List[float] = []
        self.ascans: Dict[float, List[AScan]] = {}
    
    def set_angles(self, start_deg: float, end_deg: float,
                  step_deg: float = 1.0):
        """
        Set scan angles.
        
        Args:
            start_deg: Start angle
            end_deg: End angle
            step_deg: Step
        """
        n = int((end_deg - start_deg) / step_deg) + 1
        self.angles = [start_deg + i * step_deg for i in range(n)]
    
    def simulate_ascan(self, angle_deg: float,
                      reflectors: List[Tuple[float, float, float]],
                      velocity_mm_us: float = 5.9) -> List[AScan]:
        """
        Simulate A-scan for angle.
        
        Args:
            angle_deg: Beam angle
            reflectors: (depth_mm, amplitude, x_offset)
            velocity_mm_us: Velocity
        
        Returns:
            A-scans
        """
        scans = []
        angle_rad = math.radians(angle_deg)
        
        for depth, amp, x_off in reflectors:
            # Time of flight
            path = depth / math.cos(angle_rad)
            tof = 2.0 * path / velocity_mm_us
            
            scans.append(AScan(
                element_id=0,
                time_us=tof,
                amplitude=amp,
                depth_mm=depth
            ))
        
        self.ascans[angle_deg] = scans
        return scans
    
    def bscan_image(self) -> List[List[float]]:
        """
        Generate B-scan image.
        
        Returns:
            2D amplitude map
        """
        if not self.ascans:
            return []
        
        # Simple: depth vs angle
        max_depth = 100.0
        depth_res = 1.0
        num_depth = int(max_depth / depth_res)
        num_angles = len(self.angles)
        
        image = [[0.0] * num_depth for _ in range(num_angles)]
        
        for i, angle in enumerate(self.angles):
            if angle in self.ascans:
                for scan in self.ascans[angle]:
                    d_idx = int(scan.depth_mm / depth_res)
                    if 0 <= d_idx < num_depth:
                        image[i][d_idx] = scan.amplitude
        
        return image


class TotalFocusingMethod:
    """
    Total Focusing Method (TFM) imaging.
    """
    
    def __init__(self, probe: PAProbe):
        """
        Args:
            probe: PA probe
        """
        self.probe = probe
        self.fmc_data: Dict[Tuple[int, int], List[AScan]] = {}
    
    def add_fmc_channel(self, tx: int, rx: int,
                       ascans: List[AScan]):
        """
        Add FMC channel data.
        
        Args:
            tx: Transmit element
            rx: Receive element
            ascans: A-scans
        """
        self.fmc_data[(tx, rx)] = ascans
    
    def tfm_image(self, grid_x_mm: List[float],
                 grid_y_mm: List[float],
                 velocity_mm_us: float = 5.9) -> List[List[float]]:
        """
        Generate TFM image.
        
        Args:
            grid_x_mm: X grid
            grid_y_mm: Y grid
            velocity_mm_us: Velocity
        
        Returns:
            TFM amplitude image
        """
        ny = len(grid_y_mm)
        nx = len(grid_x_mm)
        image = [[0.0] * nx for _ in range(ny)]
        
        for yi, y in enumerate(grid_y_mm):
            for xi, x in enumerate(grid_x_mm):
                total = 0.0
                count = 0
                
                for (tx, rx), ascans in self.fmc_data.items():
                    if tx >= len(self.probe.elements) or rx >= len(self.probe.elements):
                        continue
                    
                    tx_pos = self.probe.elements[tx].position
                    rx_pos = self.probe.elements[rx].position
                    
                    # Path length: tx -> point -> rx
                    dist_tx = math.sqrt((x - tx_pos)**2 + y**2)
                    dist_rx = math.sqrt((x - rx_pos)**2 + y**2)
                    total_dist = dist_tx + dist_rx
                    tof = total_dist / velocity_mm_us
                    
                    # Find matching A-scan
                    for scan in ascans:
                        if abs(scan.time_us - tof) < 0.1:
                            total += scan.amplitude
                            count += 1
                
                image[yi][xi] = total / max(count, 1)
        
        return image


class PhasedArrayUltrasonic:
    """
    Unified phased array ultrasonic controller.
    """
    
    def __init__(self, num_elements: int = 16):
        """
        Args:
            num_elements: Elements
        """
        self.probe = PAProbe(num_elements)
        self.sectorial = SectorialScan(self.probe)
        self.tfm = TotalFocusingMethod(self.probe)
        self.inspections: List[Dict] = []
    
    def sector_scan(self, start_deg: float, end_deg: float,
                   reflectors: List[Tuple[float, float, float]]):
        """
        Run sectorial scan.
        
        Args:
            start_deg: Start angle
            end_deg: End angle
            reflectors: Reflector list
        """
        self.sectorial.set_angles(start_deg, end_deg)
        for angle in self.sectorial.angles:
            self.sectorial.simulate_ascan(angle, reflectors)
    
    def tfm_scan(self, fmc_channels: Dict[Tuple[int, int], List[AScan]]):
        """
        Run TFM scan.
        
        Args:
            fmc_channels: FMC data
        """
        for (tx, rx), ascans in fmc_channels.items():
            self.tfm.add_fmc_channel(tx, rx, ascans)
    
    def paut_summary(self) -> Dict:
        """Get PAUT summary."""
        return {
            "elements": self.probe.num_elements,
            "pitch_mm": self.probe.pitch,
            "frequency_MHz": self.probe.frequency,
            "sector_angles": len(self.sectorial.angles),
            "fmc_channels": len(self.tfm.fmc_data)
        }
