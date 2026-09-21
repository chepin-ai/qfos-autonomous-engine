"""
Acoustic Emission Module
AE signal analysis, source location, Kaiser effect,
hit detection, and amplitude analysis for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AEHit:
    """Acoustic emission hit."""
    time_us: float
    amplitude_dB: float
    duration_us: float
    rise_time_us: float
    energy: float
    counts: int


class HitDetector:
    """
    AE hit detection from raw signals.
    """
    
    def __init__(self, threshold_dB: float = 40.0,
                 dead_time_us: float = 100.0):
        """
        Args:
            threshold_dB: Detection threshold
            dead_time_us: Dead time
        """
        self.threshold = threshold_dB
        self.dead_time = dead_time_us
    
    def detect_hits(self, times_us: List[float],
                   amplitudes_dB: List[float]) -> List[AEHit]:
        """
        Detect hits from signal.
        
        Args:
            times_us: Time samples
            amplitudes_dB: Amplitude samples
        
        Returns:
            Detected hits
        """
        hits = []
        in_hit = False
        hit_start = 0
        hit_peak = 0.0
        hit_peak_time = 0.0
        hit_counts = 0
        hit_energy = 0.0
        last_hit_end = -self.dead_time
        
        for i, (t, amp) in enumerate(zip(times_us, amplitudes_dB)):
            if amp > self.threshold:
                if not in_hit and t - last_hit_end > self.dead_time:
                    in_hit = True
                    hit_start = t
                    hit_peak = amp
                    hit_peak_time = t
                    hit_counts = 1
                    hit_energy = 10.0 ** (amp / 20.0)
                elif in_hit:
                    hit_counts += 1
                    hit_energy += 10.0 ** (amp / 20.0)
                    if amp > hit_peak:
                        hit_peak = amp
                        hit_peak_time = t
            else:
                if in_hit:
                    in_hit = False
                    duration = t - hit_start
                    rise_time = hit_peak_time - hit_start
                    hits.append(AEHit(hit_start, hit_peak, duration,
                                    rise_time, hit_energy, hit_counts))
                    last_hit_end = t
        
        return hits
    
    def count_rate(self, hits: List[AEHit],
                  time_window_s: float = 1.0) -> float:
        """
        Compute hit count rate.
        
        Args:
            hits: Detected hits
            time_window_s: Time window
        
        Returns:
            Hits per second
        """
        if not hits or time_window_s <= 0:
            return 0.0
        return len(hits) / time_window_s


class SourceLocator:
    """
    AE source location from multiple sensors.
    """
    
    def __init__(self, velocity_m_s: float = 5000.0):
        """
        Args:
            velocity_m_s: Wave velocity in material
        """
        self.velocity = velocity_m_s
    
    def time_difference_location(self,
                                 sensor_positions: List[Tuple[float, float]],
                                 arrival_times_us: List[float]) -> Optional[Tuple[float, float]]:
        """
        Locate source from time differences.
        
        Args:
            sensor_positions: Sensor (x, y) positions
            arrival_times_us: Arrival times
        
        Returns:
            Source position or None
        """
        if len(sensor_positions) < 3 or len(arrival_times_us) < 3:
            return None
        
        # Simplified: use first sensor as reference
        ref_pos = sensor_positions[0]
        ref_time = arrival_times_us[0]
        
        # Estimate source from weighted average
        x_sum = 0.0
        y_sum = 0.0
        weight_sum = 0.0
        
        for i in range(1, min(len(sensor_positions), len(arrival_times_us))):
            dt = (arrival_times_us[i] - ref_time) * 1e-6
            distance = self.velocity * abs(dt)
            
            dx = sensor_positions[i][0] - ref_pos[0]
            dy = sensor_positions[i][1] - ref_pos[1]
            
            weight = 1.0 / (distance + 1e-6)
            x_sum += sensor_positions[i][0] * weight
            y_sum += sensor_positions[i][1] * weight
            weight_sum += weight
        
        if weight_sum > 0:
            return (x_sum / weight_sum, y_sum / weight_sum)
        return None
    
    def delta_t_source(self, sensor1_pos: Tuple[float, float],
                      sensor2_pos: Tuple[float, float],
                      delta_t_us: float) -> List[Tuple[float, float]]:
        """
        Compute hyperbola of possible source locations.
        
        Args:
            sensor1_pos: First sensor
            sensor2_pos: Second sensor
            delta_t_us: Time difference
        
        Returns:
            Sample points on hyperbola
        """
        dt = delta_t_us * 1e-6
        distance_diff = self.velocity * dt
        
        mid_x = (sensor1_pos[0] + sensor2_pos[0]) / 2.0
        mid_y = (sensor1_pos[1] + sensor2_pos[1]) / 2.0
        
        # Simplified: return midpoint
        return [(mid_x, mid_y)]


class KaiserEffect:
    """
    Kaiser effect (felicity ratio) analysis.
    """
    
    def __init__(self):
        pass
    
    def felicity_ratio(self, previous_load_MPa: float,
                      current_emission_load_MPa: float) -> float:
        """
        Compute felicity ratio.
        
        Args:
            previous_load_MPa: Previous maximum load
            current_emission_load_MPa: Current emission load
        
        Returns:
            Felicity ratio
        """
        if previous_load_MPa <= 0:
            return 0.0
        return current_emission_load_MPa / previous_load_MPa
    
    def is_kaiser_violation(self, felicity_ratio: float,
                           threshold: float = 0.95) -> bool:
        """
        Check for Kaiser effect violation.
        
        Args:
            felicity_ratio: Felicity ratio
            threshold: Threshold
        
        Returns:
            Whether violated
        """
        return felicity_ratio < threshold


class AmplitudeAnalyzer:
    """
    AE amplitude analysis.
    """
    
    def __init__(self):
        pass
    
    def b_value(self, amplitudes_dB: List[float],
               bin_width_dB: float = 1.0) -> float:
        """
        Compute b-value from amplitude distribution.
        
        Args:
            amplitudes_dB: Amplitudes
            bin_width_dB: Bin width
        
        Returns:
            b-value
        """
        if not amplitudes_dB:
            return 0.0
        
        # Simplified: slope of log(N) vs amplitude
        min_amp = min(amplitudes_dB)
        max_amp = max(amplitudes_dB)
        num_bins = max(1, int((max_amp - min_amp) / bin_width_dB))
        
        bins = [0] * num_bins
        for amp in amplitudes_dB:
            idx = min(int((amp - min_amp) / bin_width_dB), num_bins - 1)
            bins[idx] += 1
        
        # Simple slope estimation
        valid_bins = [(i, math.log10(c + 1)) for i, c in enumerate(bins) if c > 0]
        if len(valid_bins) < 2:
            return 0.0
        
        n = len(valid_bins)
        sum_x = sum(v[0] for v in valid_bins)
        sum_y = sum(v[1] for v in valid_bins)
        sum_xy = sum(v[0] * v[1] for v in valid_bins)
        sum_x2 = sum(v[0] ** 2 for v in valid_bins)
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return -slope
    
    def average_signal_level(self, amplitudes_dB: List[float]) -> float:
        """
        Compute average signal level.
        
        Args:
            amplitudes_dB: Amplitudes
        
        Returns:
            Average in dB
        """
        if not amplitudes_dB:
            return 0.0
        return sum(amplitudes_dB) / len(amplitudes_dB)


class AcousticEmission:
    """
    Unified acoustic emission controller.
    """
    
    def __init__(self):
        self.detector = HitDetector()
        self.locator = SourceLocator()
        self.kaiser = KaiserEffect()
        self.amplitude = AmplitudeAnalyzer()
    
    def ae_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["hit_detection", "source_location", "kaiser_effect", "amplitude_analysis"],
            "velocity_m_s": self.locator.velocity
        }
