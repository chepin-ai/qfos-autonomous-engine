"""
Leak Testing Module
Pressure decay, helium mass spectrometry, bubble leak testing,
and leak rate quantification for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LeakReading:
    """Leak measurement reading."""
    timestamp_s: float
    pressure_Pa: float
    leak_rate_Pa_m3_s: float
    temperature_C: float


class PressureDecayAnalyzer:
    """
    Analyze pressure decay for leak detection.
    """
    
    def __init__(self, volume_m3: float = 0.001):
        """
        Args:
            volume_m3: Test volume
        """
        self.volume = volume_m3
    
    def leak_rate(self, pressure_drop_Pa: float,
                 time_s: float) -> float:
        """
        Compute leak rate.
        
        Args:
            pressure_drop_Pa: Pressure drop
            time_s: Time
        
        Returns:
            Leak rate in Pa m3 / s
        """
        if time_s <= 0:
            return 0.0
        return pressure_drop_Pa * self.volume / time_s
    
    def pressure_at_time(self, initial_pressure_Pa: float,
                        leak_rate_Pa_m3_s: float,
                        time_s: float) -> float:
        """
        Compute pressure at time.
        
        Args:
            initial_pressure_Pa: Initial pressure
            leak_rate_Pa_m3_s: Leak rate
            time_s: Time
        
        Returns:
            Pressure
        """
        if self.volume <= 0:
            return initial_pressure_Pa
        return initial_pressure_Pa - leak_rate_Pa_m3_s * time_s / self.volume


class HeliumMassSpectrometry:
    """
    Helium leak detection.
    """
    
    def __init__(self, sensitivity_Pa_m3_s: float = 1e-10):
        """
        Args:
            sensitivity_Pa_m3_s: Detector sensitivity
        """
        self.sensitivity = sensitivity_Pa_m3_s
    
    def detect(self, helium_signal: float,
              background: float = 0.0) -> bool:
        """
        Detect helium leak.
        
        Args:
            helium_signal: Signal
            background: Background
        
        Returns:
            True if leak detected
        """
        return (helium_signal - background) > self.sensitivity * 10.0
    
    def leak_rate(self, signal: float,
                 calibration_factor: float = 1.0) -> float:
        """
        Quantify leak rate.
        
        Args:
            signal: Signal
            calibration_factor: Calibration
        
        Returns:
            Leak rate
        """
        return signal * calibration_factor


class BubbleLeakTester:
    """
    Bubble leak testing.
    """
    
    def __init__(self, min_bubble_size_mm: float = 1.0):
        """
        Args:
            min_bubble_size_mm: Minimum bubble size
        """
        self.min_size = min_bubble_size_mm
    
    def leak_rate_from_bubbles(self, bubbles_per_minute: float,
                               bubble_volume_mm3: float) -> float:
        """
        Estimate leak rate from bubbles.
        
        Args:
            bubbles_per_minute: Rate
            bubble_volume_mm3: Volume per bubble
        
        Returns:
            Leak rate in Pa m3 / s
        """
        # Convert to standard conditions
        # 1 atm = 101325 Pa
        bubbles_per_s = bubbles_per_minute / 60.0
        volume_m3 = bubble_volume_mm3 * 1e-9
        return bubbles_per_s * volume_m3 * 101325.0
    
    def detect(self, bubbles: List[Dict]) -> bool:
        """
        Detect leaks from bubbles.
        
        Args:
            bubbles: Bubble list
        
        Returns:
            True if leak
        """
        return len(bubbles) > 0


class LeakQuantifier:
    """
    Quantify and classify leaks.
    """
    
    def __init__(self):
        pass
    
    def classify(self, leak_rate_Pa_m3_s: float) -> str:
        """
        Classify leak.
        
        Args:
            leak_rate_Pa_m3_s: Rate
        
        Returns:
            Classification
        """
        if leak_rate_Pa_m3_s < 1e-9:
            return "negligible"
        elif leak_rate_Pa_m3_s < 1e-6:
            return "minor"
        elif leak_rate_Pa_m3_s < 1e-3:
            return "moderate"
        else:
            return "severe"
    
    def total_leak(self, readings: List[LeakReading]) -> float:
        """
        Compute total leak.
        
        Args:
            readings: Readings
        
        Returns:
            Total leak rate
        """
        if not readings:
            return 0.0
        return sum(r.leak_rate_Pa_m3_s for r in readings) / len(readings)


class LeakTesting:
    """
    Unified leak testing controller.
    """
    
    def __init__(self, volume_m3: float = 0.001):
        self.decay = PressureDecayAnalyzer(volume_m3)
        self.helium = HeliumMassSpectrometry()
        self.bubble = BubbleLeakTester()
        self.quantifier = LeakQuantifier()
        self.readings: List[LeakReading] = []
    
    def add_reading(self, reading: LeakReading):
        """
        Add reading.
        
        Args:
            reading: Reading
        """
        self.readings.append(reading)
    
    def inspect(self) -> Dict:
        """
        Inspect.
        
        Returns:
            Results
        """
        if not self.readings:
            return {}
        
        total = self.quantifier.total_leak(self.readings)
        cls = self.quantifier.classify(total)
        
        return {
            "readings": len(self.readings),
            "avg_leak_rate": total,
            "classification": cls,
            "max_leak": max(r.leak_rate_Pa_m3_s for r in self.readings)
        }
    
    def lt_summary(self) -> Dict:
        """Get summary."""
        return {
            "readings": len(self.readings),
            "volume_m3": self.decay.volume
        }
