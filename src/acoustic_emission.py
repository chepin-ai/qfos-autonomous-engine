"""
Acoustic Emission Module
AE sensor array, hit detection, event clustering,
and source localization for autonomous structural health monitoring.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class AEEventType(Enum):
    """Types of acoustic emission events."""
    CRACK_GROWTH = "crack_growth"
    FIBER_BREAKAGE = "fiber_breakage"
    DELAMINATION = "delamination"
    FRICTION = "friction"
    PLASTIC_DEFORMATION = "plastic_deformation"


@dataclass
class AEHit:
    """Single acoustic emission hit."""
    sensor_id: int
    amplitude_dB: float
    energy: float
    duration_us: float
    rise_time_us: float
    counts: int
    timestamp: float = 0.0


class AESensor:
    """
    Single acoustic emission sensor.
    """
    
    def __init__(self, sensor_id: int, position: Tuple[float, float],
                 threshold_dB: float = 40.0):
        """
        Args:
            sensor_id: Sensor ID
            position: (x, y) position
            threshold_dB: Detection threshold
        """
        self.sensor_id = sensor_id
        self.position = position
        self.threshold = threshold_dB
        self.hits: List[AEHit] = []
    
    def detect(self, signal_amplitude: float,
              energy: float = 0.0,
              duration_us: float = 0.0,
              rise_time_us: float = 0.0,
              counts: int = 0,
              timestamp: float = 0.0) -> Optional[AEHit]:
        """
        Detect hit from signal.
        
        Args:
            signal_amplitude: Signal amplitude
            energy: Energy
            duration_us: Duration
            rise_time_us: Rise time
            counts: Counts
            timestamp: Timestamp
        
        Returns:
            Hit or None
        """
        if signal_amplitude < self.threshold:
            return None
        
        hit = AEHit(
            sensor_id=self.sensor_id,
            amplitude_dB=signal_amplitude,
            energy=energy,
            duration_us=duration_us,
            rise_time_us=rise_time_us,
            counts=counts,
            timestamp=timestamp
        )
        self.hits.append(hit)
        return hit
    
    def hit_rate(self, time_window_s: float = 60.0) -> float:
        """
        Compute hit rate.
        
        Args:
            time_window_s: Time window
        
        Returns:
            Hits per second
        """
        if time_window_s <= 0:
            return 0.0
        recent = [h for h in self.hits if h.timestamp >= (self.hits[-1].timestamp if self.hits else 0) - time_window_s]
        return len(recent) / time_window_s


class AEEventDetector:
    """
    Detect and cluster AE events from multiple sensors.
    """
    
    def __init__(self, time_window_ms: float = 5.0):
        """
        Args:
            time_window_ms: Time window for event clustering
        """
        self.time_window = time_window_ms
        self.events: List[Dict] = []
    
    def cluster_hits(self, hits: List[AEHit]) -> List[List[AEHit]]:
        """
        Cluster hits into events.
        
        Args:
            hits: All hits
        
        Returns:
            Event clusters
        """
        if not hits:
            return []
        
        sorted_hits = sorted(hits, key=lambda h: h.timestamp)
        clusters = []
        current = [sorted_hits[0]]
        
        for hit in sorted_hits[1:]:
            if hit.timestamp - current[-1].timestamp <= self.time_window:
                current.append(hit)
            else:
                clusters.append(current)
                current = [hit]
        
        if current:
            clusters.append(current)
        
        return clusters
    
    def event_energy(self, cluster: List[AEHit]) -> float:
        """
        Compute total event energy.
        
        Args:
            cluster: Event cluster
        
        Returns:
            Total energy
        """
        return sum(h.energy for h in cluster)
    
    def event_amplitude(self, cluster: List[AEHit]) -> float:
        """
        Compute max event amplitude.
        
        Args:
            cluster: Event cluster
        
        Returns:
            Max amplitude dB
        """
        return max(h.amplitude_dB for h in cluster) if cluster else 0.0
    
    def event_duration(self, cluster: List[AEHit]) -> float:
        """
        Compute event duration.
        
        Args:
            cluster: Event cluster
        
        Returns:
            Duration
        """
        if len(cluster) < 2:
            return 0.0
        return cluster[-1].timestamp - cluster[0].timestamp
    
    def classify_event(self, cluster: List[AEHit]) -> AEEventType:
        """
        Classify event type from cluster features.
        
        Args:
            cluster: Event cluster
        
        Returns:
            Event type
        """
        if not cluster:
            return AEEventType.FRICTION
        
        avg_rise = sum(h.rise_time_us for h in cluster) / len(cluster)
        avg_dur = sum(h.duration_us for h in cluster) / len(cluster)
        max_amp = self.event_amplitude(cluster)
        
        if max_amp > 80 and avg_rise < 10:
            return AEEventType.CRACK_GROWTH
        elif avg_dur > 1000:
            return AEEventType.PLASTIC_DEFORMATION
        elif avg_rise < 50 and max_amp > 60:
            return AEEventType.DELAMINATION
        elif max_amp > 70:
            return AEEventType.FIBER_BREAKAGE
        return AEEventType.FRICTION


class AESourceLocator:
    """
    Locate AE source from sensor arrival times.
    """
    
    def __init__(self, wave_velocity_mm_us: float = 5.0):
        """
        Args:
            wave_velocity_mm_us: Wave velocity mm/us
        """
        self.velocity = wave_velocity_mm_us
    
    def time_difference_of_arrival(self,
                                    sensor_positions: List[Tuple[float, float]],
                                    arrival_times: List[float]) -> Tuple[float, float]:
        """
        Locate source using TDOA.
        
        Args:
            sensor_positions: Sensor positions
            arrival_times: Arrival times
        
        Returns:
            Estimated (x, y)
        """
        if len(sensor_positions) < 3 or len(arrival_times) < 3:
            return (0.0, 0.0)
        
        # Use first sensor as reference
        ref_pos = sensor_positions[0]
        ref_time = arrival_times[0]
        
        # Weighted average based on time difference
        weights = []
        for i in range(1, len(sensor_positions)):
            dt = abs(arrival_times[i] - ref_time)
            if dt > 0:
                dist = self.velocity * dt
                weights.append(1.0 / dist)
            else:
                weights.append(0.0)
        
        if sum(weights) == 0:
            return ref_pos
        
        x = sum(sensor_positions[i][0] * weights[i-1] for i in range(1, len(sensor_positions))) / sum(weights)
        y = sum(sensor_positions[i][1] * weights[i-1] for i in range(1, len(sensor_positions))) / sum(weights)
        
        return (x, y)
    
    def distance_to_source(self, sensor_pos: Tuple[float, float],
                          source_pos: Tuple[float, float]) -> float:
        """
        Compute distance.
        
        Args:
            sensor_pos: Sensor position
            source_pos: Source position
        
        Returns:
            Distance
        """
        return math.sqrt((sensor_pos[0] - source_pos[0])**2 +
                        (sensor_pos[1] - source_pos[1])**2)
    
    def expected_arrival(self, sensor_pos: Tuple[float, float],
                        source_pos: Tuple[float, float],
                        emission_time: float = 0.0) -> float:
        """
        Compute expected arrival time.
        
        Args:
            sensor_pos: Sensor position
            source_pos: Source position
            emission_time: Emission time
        
        Returns:
            Arrival time
        """
        dist = self.distance_to_source(sensor_pos, source_pos)
        return emission_time + dist / self.velocity


class AcousticEmission:
    """
    Unified acoustic emission monitoring controller.
    """
    
    def __init__(self):
        self.sensors: List[AESensor] = []
        self.detector = AEEventDetector()
        self.locator = AESourceLocator()
        self.events: List[Dict] = []
    
    def add_sensor(self, position: Tuple[float, float],
                  threshold_dB: float = 40.0) -> int:
        """
        Add sensor.
        
        Args:
            position: Position
            threshold_dB: Threshold
        
        Returns:
            Sensor ID
        """
        sensor_id = len(self.sensors)
        sensor = AESensor(sensor_id, position, threshold_dB)
        self.sensors.append(sensor)
        return sensor_id
    
    def monitor(self, signals: List[Dict]):
        """
        Process signals from all sensors.
        
        Args:
            signals: List of signal dicts per sensor
        """
        all_hits = []
        for i, sig in enumerate(signals):
            if i < len(self.sensors):
                hit = self.sensors[i].detect(
                    signal_amplitude=sig.get("amplitude", 0.0),
                    energy=sig.get("energy", 0.0),
                    duration_us=sig.get("duration", 0.0),
                    rise_time_us=sig.get("rise_time", 0.0),
                    counts=sig.get("counts", 0),
                    timestamp=sig.get("timestamp", 0.0)
                )
                if hit:
                    all_hits.append(hit)
        
        # Cluster into events
        clusters = self.detector.cluster_hits(all_hits)
        for cluster in clusters:
            event_type = self.detector.classify_event(cluster)
            event = {
                "hits": len(cluster),
                "energy": self.detector.event_energy(cluster),
                "amplitude_dB": self.detector.event_amplitude(cluster),
                "duration_ms": self.detector.event_duration(cluster),
                "type": event_type.value
            }
            self.events.append(event)
    
    def locate_source(self, arrival_times: List[float]) -> Tuple[float, float]:
        """
        Locate source.
        
        Args:
            arrival_times: Arrival times per sensor
        
        Returns:
            Source position
        """
        positions = [s.position for s in self.sensors]
        return self.locator.time_difference_of_arrival(positions, arrival_times)
    
    def emission_summary(self) -> Dict:
        """Get emission summary."""
        if not self.events:
            return {"status": "no_events"}
        
        type_counts = {}
        for e in self.events:
            t = e["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            "total_events": len(self.events),
            "total_hits": sum(e["hits"] for e in self.events),
            "max_amplitude_dB": max(e["amplitude_dB"] for e in self.events),
            "event_types": type_counts
        }
