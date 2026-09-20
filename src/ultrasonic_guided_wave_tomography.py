"""
Ultrasonic Guided Wave Tomography Module
Ray tracing, travel time inversion, damage mapping, and
tomographic reconstruction for autonomous structural health monitoring.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Transducer:
    """Transducer position."""
    x_mm: float
    y_mm: float
    id: int


class RayTracer:
    """
    Trace rays between transducers.
    """
    
    def __init__(self, velocity_mm_us: float = 5.9):
        """
        Args:
            velocity_mm_us: Wave velocity
        """
        self.v = velocity_mm_us
    
    def distance(self, t1: Transducer, t2: Transducer) -> float:
        """
        Compute distance between transducers.
        
        Args:
            t1: Transducer 1
            t2: Transducer 2
        
        Returns:
            Distance
        """
        dx = t1.x_mm - t2.x_mm
        dy = t1.y_mm - t2.y_mm
        return math.sqrt(dx**2 + dy**2)
    
    def travel_time(self, t1: Transducer, t2: Transducer) -> float:
        """
        Compute travel time.
        
        Args:
            t1: Transducer 1
            t2: Transducer 2
        
        Returns:
            Travel time in microseconds
        """
        return self.distance(t1, t2) / self.v
    
    def ray_path(self, t1: Transducer, t2: Transducer,
                num_points: int = 10) -> List[Tuple[float, float]]:
        """
        Compute ray path points.
        
        Args:
            t1: Start
            t2: End
            num_points: Points
        
        Returns:
            Path points
        """
        path = []
        for i in range(num_points):
            frac = i / (num_points - 1) if num_points > 1 else 0
            x = t1.x_mm + frac * (t2.x_mm - t1.x_mm)
            y = t1.y_mm + frac * (t2.y_mm - t1.y_mm)
            path.append((x, y))
        return path


class TravelTimeInverter:
    """
    Invert travel times to slowness map.
    """
    
    def __init__(self, grid_size_mm: float = 10.0,
                 grid_x: int = 20, grid_y: int = 20):
        """
        Args:
            grid_size_mm: Grid size
            grid_x: X divisions
            grid_y: Y divisions
        """
        self.grid_size = grid_size_mm
        self.nx = grid_x
        self.ny = grid_y
        self.slowness: List[List[float]] = [[1.0 / 5.9 for _ in range(grid_x)]
                                            for _ in range(grid_y)]
    
    def grid_index(self, x_mm: float, y_mm: float) -> Optional[Tuple[int, int]]:
        """
        Get grid index.
        
        Args:
            x_mm: X position
            y_mm: Y position
        
        Returns:
            Grid index
        """
        ix = int(x_mm / self.grid_size)
        iy = int(y_mm / self.grid_size)
        
        if 0 <= ix < self.nx and 0 <= iy < self.ny:
            return (ix, iy)
        return None
    
    def update_slowness(self, measurements: List[Tuple[Transducer, Transducer, float]]):
        """
        Update slowness map from measurements.
        
        Args:
            measurements: (t1, t2, measured_time)
        """
        tracer = RayTracer()
        
        for t1, t2, measured in measurements:
            expected = tracer.travel_time(t1, t2)
            if expected <= 0:
                continue
            
            ratio = measured / expected
            path = tracer.ray_path(t1, t2, 20)
            
            for x, y in path:
                idx = self.grid_index(x, y)
                if idx:
                    ix, iy = idx
                    # Update slowness
                    self.slowness[iy][ix] *= ratio


class DamageMapper:
    """
    Map damage from tomography results.
    """
    
    def __init__(self, inverter: TravelTimeInverter):
        """
        Args:
            inverter: Inverter
        """
        self.inverter = inverter
    
    def find_damage(self, baseline_slowness: float = 1.0 / 5.9,
                   threshold: float = 1.2) -> List[Dict]:
        """
        Find damage regions.
        
        Args:
            baseline_slowness: Baseline
            threshold: Threshold
        
        Returns:
            Damage regions
        """
        damage = []
        for iy in range(self.inverter.ny):
            for ix in range(self.inverter.nx):
                s = self.inverter.slowness[iy][ix]
                if s > baseline_slowness * threshold:
                    damage.append({
                        "x_mm": ix * self.inverter.grid_size,
                        "y_mm": iy * self.inverter.grid_size,
                        "slowness": s,
                        "severity": (s / baseline_slowness - 1.0) * 100.0
                    })
        return damage
    
    def damage_percentage(self, baseline_slowness: float = 1.0 / 5.9,
                         threshold: float = 1.2) -> float:
        """
        Compute damage area percentage.
        
        Args:
            baseline_slowness: Baseline
            threshold: Threshold
        
        Returns:
            Percentage
        """
        total = self.inverter.nx * self.inverter.ny
        damaged = sum(1 for iy in range(self.inverter.ny)
                     for ix in range(self.inverter.nx)
                     if self.inverter.slowness[iy][ix] > baseline_slowness * threshold)
        return damaged / total * 100.0 if total > 0 else 0.0


class UltrasonicGuidedWaveTomography:
    """
    Unified UGWT controller.
    """
    
    def __init__(self):
        self.tracer = RayTracer()
        self.inverter = TravelTimeInverter()
        self.mapper = DamageMapper(self.inverter)
        self.transducers: List[Transducer] = []
        self.measurements: List[Tuple[Transducer, Transducer, float]] = []
    
    def place_transducers(self, positions: List[Tuple[float, float]]):
        """
        Place transducers.
        
        Args:
            positions: (x, y) positions
        """
        self.transducers = []
        for i, (x, y) in enumerate(positions):
            self.transducers.append(Transducer(x, y, i))
    
    def measure(self, pairs: List[Tuple[int, int]],
               times_us: List[float]):
        """
        Add measurements.
        
        Args:
            pairs: Transducer pairs
            times_us: Measured times
        """
        self.measurements = []
        for (i, j), t in zip(pairs, times_us):
            if i < len(self.transducers) and j < len(self.transducers):
                self.measurements.append((self.transducers[i],
                                         self.transducers[j], t))
        
        self.inverter.update_slowness(self.measurements)
    
    def inspect(self) -> Dict:
        """
        Inspect structure.
        
        Returns:
            Results
        """
        damage = self.mapper.find_damage()
        pct = self.mapper.damage_percentage()
        
        return {
            "damage_regions": len(damage),
            "damage_percentage": pct,
            "regions": damage[:5]
        }
    
    def ugwt_summary(self) -> Dict:
        """Get summary."""
        return {
            "transducers": len(self.transducers),
            "measurements": len(self.measurements),
            "grid": f"{self.inverter.nx}x{self.inverter.ny}"
        }
