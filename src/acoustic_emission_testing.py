"""
Acoustic Emission Testing Module
AE event detection, waveform analysis, source location,
and damage severity assessment for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AEEvent:
    """Acoustic emission event."""
    amplitude_dB: float
    energy_aJ: float
    duration_us: float
    rise_time_us: float
    counts: int
    frequency_kHz: float
    timestamp_ms: float


class AEEventDetector:
    """
    Detect AE events from waveforms.
    """
    
    def __init__(self, threshold_dB: float = 40.0):
        """
        Args:
            threshold_dB: Detection threshold
        """
        self.threshold = threshold_dB
    
    def detect(self, waveform: List[float],
              sample_rate_MHz: float,
              gain_dB: float = 0.0) -> List[AEEvent]:
        """
        Detect events.
        
        Args:
            waveform: Raw waveform
            sample_rate_MHz: Sample rate
            gain_dB: Preamp gain
        
        Returns:
            Events
        """
        events = []
        in_event = False
        event_start = 0
        max_amp = 0.0
        count = 0
        energy = 0.0
        
        for i, sample in enumerate(waveform):
            amp_dB = 20.0 * math.log10(abs(sample) + 1e-10) + gain_dB
            
            if amp_dB > self.threshold and not in_event:
                in_event = True
                event_start = i
                max_amp = amp_dB
                count = 1
                energy = sample ** 2
            elif in_event:
                if amp_dB > self.threshold:
                    max_amp = max(max_amp, amp_dB)
                    count += 1
                    energy += sample ** 2
                else:
                    # Event ended
                    duration_us = (i - event_start) / sample_rate_MHz
                    events.append(AEEvent(
                        amplitude_dB=max_amp,
                        energy_aJ=energy * 1e18,
                        duration_us=duration_us,
                        rise_time_us=duration_us / 3.0,
                        counts=count,
                        frequency_kHz=sample_rate_MHz / 2.0,
                        timestamp_ms=event_start / sample_rate_MHz * 1000.0
                    ))
                    in_event = False
        
        if in_event:
            duration_us = (len(waveform) - event_start) / sample_rate_MHz
            events.append(AEEvent(
                amplitude_dB=max_amp,
                energy_aJ=energy * 1e18,
                duration_us=duration_us,
                rise_time_us=duration_us / 3.0,
                counts=count,
                frequency_kHz=sample_rate_MHz / 2.0,
                timestamp_ms=event_start / sample_rate_MHz * 1000.0
            ))
        
        return events


class SourceLocator:
    """
    Locate AE source from sensor array.
    """
    
    def __init__(self, sensors: List[Tuple[float, float, float]]):
        """
        Args:
            sensors: Sensor positions (x, y, z) in mm
        """
        self.sensors = sensors
    
    def locate(self, arrival_times_ms: List[float],
              velocity_mm_us: float) -> Tuple[float, float, float]:
        """
        Locate source.
        
        Args:
            arrival_times_ms: Arrival times
            velocity_mm_us: Wave velocity
        
        Returns:
            Source position
        """
        if len(arrival_times_ms) < 3 or len(self.sensors) < 3:
            return (0.0, 0.0, 0.0)
        
        # Use first arrival as reference
        ref_time = min(arrival_times_ms)
        ref_idx = arrival_times_ms.index(ref_time)
        
        # Simple centroid weighted by inverse time difference
        x, y, z = 0.0, 0.0, 0.0
        total_weight = 0.0
        
        for i, (sx, sy, sz) in enumerate(self.sensors):
            dt = arrival_times_ms[i] - ref_time
            if dt < 0:
                dt = 0.0
            
            weight = 1.0 / (dt + 1.0)
            x += sx * weight
            y += sy * weight
            z += sz * weight
            total_weight += weight
        
        if total_weight > 0:
            return (x / total_weight, y / total_weight, z / total_weight)
        
        return self.sensors[ref_idx]


class SeverityAssessor:
    """
    Assess damage severity from AE data.
    """
    
    def __init__(self):
        pass
    
    def severity_index(self, events: List[AEEvent]) -> float:
        """
        Compute severity index.
        
        Args:
            events: Events
        
        Returns:
            Severity
        """
        if not events:
            return 0.0
        
        total_energy = sum(e.energy_aJ for e in events)
        max_amp = max(e.amplitude_dB for e in events)
        
        return (total_energy / 1e6) * (max_amp / 100.0)
    
    def b_value(self, events: List[AEEvent]) -> float:
        """
        Compute b-value (Gutenberg-Richter).
        
        Args:
            events: Events
        
        Returns:
            b-value
        """
        if len(events) < 2:
            return 0.0
        
        # Count events in amplitude bins
        bins: Dict[int, int] = {}
        for e in events:
            bin_idx = int(e.amplitude_dB / 5.0)
            bins[bin_idx] = bins.get(bin_idx, 0) + 1
        
        if len(bins) < 2:
            return 0.0
        
        # Linear fit of log(count) vs amplitude
        # Simplified: use two points
        sorted_bins = sorted(bins.items())
        if len(sorted_bins) >= 2:
            x1, y1 = sorted_bins[0][0] * 5.0, math.log(sorted_bins[0][1] + 1)
            x2, y2 = sorted_bins[-1][0] * 5.0, math.log(sorted_bins[-1][1] + 1)
            
            if abs(x2 - x1) > 1e-10:
                return abs((y2 - y1) / (x2 - x1))
        
        return 0.0


class AcousticEmissionTesting:
    """
    Unified AE testing controller.
    """
    
    def __init__(self, threshold_dB: float = 40.0):
        self.detector = AEEventDetector(threshold_dB)
        self.locator: Optional[SourceLocator] = None
        self.assessor = SeverityAssessor()
        self.events: List[AEEvent] = []
    
    def set_sensors(self, sensors: List[Tuple[float, float, float]]):
        """
        Set sensors.
        
        Args:
            sensors: Positions
        """
        self.locator = SourceLocator(sensors)
    
    def process(self, waveform: List[float],
               sample_rate_MHz: float,
               gain_dB: float = 0.0):
        """
        Process waveform.
        
        Args:
            waveform: Waveform
            sample_rate_MHz: Rate
            gain_dB: Gain
        """
        self.events = self.detector.detect(waveform, sample_rate_MHz, gain_dB)
    
    def inspect(self) -> Dict:
        """
        Inspect.
        
        Returns:
            Results
        """
        return {
            "events": len(self.events),
            "severity": self.assessor.severity_index(self.events),
            "b_value": self.assessor.b_value(self.events)
        }
    
    def aet_summary(self) -> Dict:
        """Get summary."""
        return {
            "events": len(self.events),
            "threshold_dB": self.detector.threshold
        }
