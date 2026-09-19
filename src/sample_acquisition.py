"""
Sample Acquisition Module
Drilling control, sample handling, and processing
for autonomous surface science missions.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DrillState(Enum):
    """Drill operational state."""
    IDLE = "idle"
    EXTENDING = "extending"
    DRILLING = "drilling"
    RETRACTING = "retracting"
    SAMPLE_COLLECTED = "sample_collected"
    ERROR = "error"


class SampleQuality(Enum):
    """Acquired sample quality."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CONTAMINATED = "contaminated"


@dataclass
class Sample:
    """A collected sample."""
    sample_id: str
    depth_m: float
    mass_g: float
    volume_ml: float
    quality: SampleQuality
    composition: Dict[str, float] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.composition is None:
            self.composition = {}


class DrillController:
    """
    Control drilling operations.
    """
    
    def __init__(self, max_depth_m: float = 2.0,
                 drill_rate_m_per_min: float = 0.1,
                 max_rpm: float = 300.0):
        """
        Args:
            max_depth_m: Maximum drill depth
            drill_rate_m_per_min: Nominal drill rate
            max_rpm: Maximum drill RPM
        """
        self.max_depth = max_depth_m
        self.drill_rate = drill_rate_m_per_min / 60.0  # m/s
        self.max_rpm = max_rpm
        self.state = DrillState.IDLE
        self.current_depth = 0.0
        self.applied_force_N = 0.0
        self.rpm = 0.0
    
    def start_drilling(self, target_depth_m: float) -> bool:
        """
        Start drilling to target depth.
        
        Args:
            target_depth_m: Target depth
        
        Returns:
            True if started
        """
        if self.state != DrillState.IDLE:
            return False
        if target_depth_m > self.max_depth:
            return False
        self.state = DrillState.DRILLING
        self.rpm = self.max_rpm * 0.8
        self.applied_force_N = 50.0
        return True
    
    def update_drilling(self, dt: float) -> bool:
        """
        Update drilling progress.
        
        Args:
            dt: Time step (seconds)
        
        Returns:
            True if still drilling
        """
        if self.state != DrillState.DRILLING:
            return False
        
        # Advance drill
        advance = self.drill_rate * dt
        self.current_depth += advance
        
        if self.current_depth >= self.max_depth:
            self.current_depth = self.max_depth
            self.state = DrillState.SAMPLE_COLLECTED
            return False
        
        return True
    
    def retract(self):
        """Retract drill."""
        self.state = DrillState.RETRACTING
        self.rpm = 0.0
        self.applied_force_N = 0.0
        self.current_depth = 0.0
    
    def emergency_stop(self):
        """Emergency stop."""
        self.state = DrillState.ERROR
        self.rpm = 0.0
        self.applied_force_N = 0.0
    
    def get_progress(self) -> float:
        """Get drilling progress (0-1)."""
        if self.max_depth <= 0:
            return 0.0
        return min(1.0, self.current_depth / self.max_depth)


class SampleHandler:
    """
    Handle collected samples.
    """
    
    def __init__(self, max_samples: int = 10):
        """
        Args:
            max_samples: Maximum number of stored samples
        """
        self.max_samples = max_samples
        self.samples: List[Sample] = []
        self.sample_counter = 0
    
    def collect_sample(self, depth_m: float,
                      mass_g: float = 10.0,
                      volume_ml: float = 5.0,
                      timestamp: float = 0.0) -> Sample:
        """
        Collect and store a sample.
        
        Args:
            depth_m: Sample depth
            mass_g: Sample mass
            volume_ml: Sample volume
            timestamp: Collection time
        
        Returns:
            Collected sample
        """
        self.sample_counter += 1
        
        # Assess quality based on depth
        if depth_m < 0.1:
            quality = SampleQuality.POOR
        elif depth_m < 0.5:
            quality = SampleQuality.FAIR
        elif depth_m < 1.0:
            quality = SampleQuality.GOOD
        else:
            quality = SampleQuality.EXCELLENT
        
        sample = Sample(
            sample_id=f"S{self.sample_counter:03d}",
            depth_m=depth_m,
            mass_g=mass_g,
            volume_ml=volume_ml,
            quality=quality,
            timestamp=timestamp
        )
        
        self.samples.append(sample)
        if len(self.samples) > self.max_samples:
            self.samples.pop(0)
        
        return sample
    
    def analyze_composition(self, sample_id: str,
                           composition: Dict[str, float]) -> bool:
        """
        Add compositional analysis to sample.
        
        Args:
            sample_id: Sample ID
            composition: Element/molecule fractions
        
        Returns:
            True if applied
        """
        for sample in self.samples:
            if sample.sample_id == sample_id:
                sample.composition = composition.copy()
                return True
        return False
    
    def get_samples_by_quality(self, min_quality: SampleQuality
                              ) -> List[Sample]:
        """Get samples above quality threshold."""
        quality_order = [SampleQuality.POOR, SampleQuality.FAIR,
                        SampleQuality.GOOD, SampleQuality.EXCELLENT]
        min_idx = quality_order.index(min_quality)
        return [s for s in self.samples
                if quality_order.index(s.quality) >= min_idx]
    
    def total_mass(self) -> float:
        """Get total sample mass."""
        return sum(s.mass_g for s in self.samples)
    
    def remaining_capacity(self) -> int:
        """Get remaining sample capacity."""
        return self.max_samples - len(self.samples)


class SampleProcessor:
    """
    Process samples for analysis.
    """
    
    def __init__(self):
        self.processed_count = 0
    
    def grind(self, sample: Sample, target_size_um: float = 50.0
             ) -> Sample:
        """
        Grind sample to target size.
        
        Args:
            sample: Input sample
            target_size_um: Target particle size
        
        Returns:
            Processed sample
        """
        processed = Sample(
            sample_id=f"{sample.sample_id}_G",
            depth_m=sample.depth_m,
            mass_g=sample.mass_g * 0.98,  # 2% loss
            volume_ml=sample.volume_ml * 0.95,
            quality=sample.quality,
            composition=sample.composition.copy() if sample.composition else {},
            timestamp=sample.timestamp
        )
        processed.composition["grind_size_um"] = target_size_um
        self.processed_count += 1
        return processed
    
    def sieve(self, sample: Sample, mesh_size_um: float = 100.0
             ) -> Tuple[Sample, Sample]:
        """
        Sieve sample into coarse and fine fractions.
        
        Args:
            sample: Input sample
            mesh_size_um: Mesh size
        
        Returns:
            (coarse, fine) samples
        """
        coarse = Sample(
            sample_id=f"{sample.sample_id}_C",
            depth_m=sample.depth_m,
            mass_g=sample.mass_g * 0.3,
            volume_ml=sample.volume_ml * 0.35,
            quality=sample.quality,
            composition=sample.composition.copy() if sample.composition else {},
            timestamp=sample.timestamp
        )
        fine = Sample(
            sample_id=f"{sample.sample_id}_F",
            depth_m=sample.depth_m,
            mass_g=sample.mass_g * 0.7,
            volume_ml=sample.volume_ml * 0.65,
            quality=sample.quality,
            composition=sample.composition.copy() if sample.composition else {},
            timestamp=sample.timestamp
        )
        self.processed_count += 2
        return coarse, fine


class SampleAcquisition:
    """
    Unified sample acquisition controller.
    """
    
    def __init__(self):
        self.drill = DrillController()
        self.handler = SampleHandler()
        self.processor = SampleProcessor()
    
    def drill_and_collect(self, target_depth_m: float,
                         timestamp: float = 0.0) -> Optional[Sample]:
        """
        Execute full drill and collect sequence.
        
        Args:
            target_depth_m: Target depth
            timestamp: Timestamp
        
        Returns:
            Collected sample or None
        """
        if not self.drill.start_drilling(target_depth_m):
            return None
        
        # Simulate drilling
        while self.drill.update_drilling(1.0):
            pass
        
        if self.drill.state != DrillState.SAMPLE_COLLECTED:
            return None
        
        sample = self.handler.collect_sample(
            self.drill.current_depth,
            timestamp=timestamp
        )
        
        self.drill.retract()
        return sample
    
    def process_sample(self, sample_id: str,
                      operation: str = "grind") -> Optional[Sample]:
        """
        Process a stored sample.
        
        Args:
            sample_id: Sample ID
            operation: "grind" or "sieve"
        
        Returns:
            Processed sample or None
        """
        sample = next((s for s in self.handler.samples if s.sample_id == sample_id), None)
        if not sample:
            return None
        
        if operation == "grind":
            return self.processor.grind(sample)
        elif operation == "sieve":
            return self.processor.sieve(sample)[1]  # Return fine fraction
        return None
    
    def acquisition_summary(self) -> Dict:
        """Get acquisition summary."""
        return {
            "drill_state": self.drill.state.value,
            "drill_progress": self.drill.get_progress(),
            "samples_stored": len(self.handler.samples),
            "total_mass_g": self.handler.total_mass(),
            "remaining_capacity": self.handler.remaining_capacity(),
            "processed_count": self.processor.processed_count
        }
