"""
Leak Detection Module
Pressure decay, helium mass spectrometry, bubble testing,
and acoustic leak detection for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class LeakMethod(Enum):
    """Leak detection methods."""
    PRESSURE_DECAY = "pressure_decay"
    HELIUM_MASS_SPEC = "helium_mass_spec"
    BUBBLE_TEST = "bubble_test"
    ACOUSTIC = "acoustic"


@dataclass
class LeakRate:
    """Leak rate measurement."""
    rate_Pa_m3_s: float
    method: LeakMethod
    location: Optional[Tuple[float, float]] = None


class PressureDecayTester:
    """
    Pressure decay leak testing.
    """
    
    def __init__(self, vessel_volume_m3: float = 0.001):
        """
        Args:
            vessel_volume_m3: Volume in m^3
        """
        self.volume = vessel_volume_m3
    
    def leak_rate(self, initial_pressure_Pa: float,
                 final_pressure_Pa: float,
                 time_s: float,
                 temperature_K: float = 293.15) -> float:
        """
        Compute leak rate from pressure decay.
        
        Args:
            initial_pressure_Pa: Initial pressure
            final_pressure_Pa: Final pressure
            time_s: Time
            temperature_K: Temperature
        
        Returns:
            Leak rate in Pa*m^3/s
        """
        if time_s <= 0 or temperature_K <= 0:
            return 0.0
        
        # Q = V * (P1 - P2) / t
        return self.volume * (initial_pressure_Pa - final_pressure_Pa) / time_s
    
    def decay_constant(self, leak_rate_Pa_m3_s: float,
                      pressure_Pa: float) -> float:
        """
        Compute pressure decay constant tau.
        
        Args:
            leak_rate_Pa_m3_s: Leak rate
            pressure_Pa: Pressure
        
        Returns:
            Time constant in seconds
        """
        if leak_rate_Pa_m3_s <= 0:
            return float('inf')
        return self.volume * pressure_Pa / leak_rate_Pa_m3_s
    
    def time_to_threshold(self, initial_pressure_Pa: float,
                         threshold_pressure_Pa: float,
                         leak_rate_Pa_m3_s: float) -> float:
        """
        Compute time to reach threshold.
        
        Args:
            initial_pressure_Pa: Initial
            threshold_pressure_Pa: Threshold
            leak_rate_Pa_m3_s: Leak rate
        
        Returns:
            Time in seconds
        """
        if leak_rate_Pa_m3_s <= 0:
            return float('inf')
        return self.volume * (initial_pressure_Pa - threshold_pressure_Pa) / leak_rate_Pa_m3_s


class HeliumMassSpectrometer:
    """
    Helium mass spectrometry leak detection.
    """
    
    def __init__(self, sensitivity_Pa_m3_s: float = 1e-10):
        """
        Args:
            sensitivity_Pa_m3_s: Minimum detectable leak
        """
        self.sensitivity = sensitivity_Pa_m3_s
    
    def detect_leak(self, helium_signal: float,
                   background: float = 0.0) -> bool:
        """
        Detect helium leak.
        
        Args:
            helium_signal: Signal
            background: Background
        
        Returns:
            True if leak detected
        """
        snr = (helium_signal - background) / background if background > 0 else helium_signal
        return snr > 3.0
    
    def leak_rate_from_signal(self, signal: float,
                             calibration_factor: float = 1e-9) -> float:
        """
        Convert signal to leak rate.
        
        Args:
            signal: Signal
            calibration_factor: Calibration
        
        Returns:
            Leak rate
        """
        return signal * calibration_factor
    
    def sniff_test(self, helium_concentration_ppm: float,
                  flow_rate_m3_s: float = 1e-4) -> float:
        """
        Sniff test leak rate.
        
        Args:
            helium_concentration_ppm: Concentration
            flow_rate_m3_s: Flow rate
        
        Returns:
            Leak rate
        """
        # Q = C * Q_flow * 1e-6 (ppm to fraction)
        return helium_concentration_ppm * 1e-6 * flow_rate_m3_s


class BubbleTester:
    """
    Bubble immersion leak testing.
    """
    
    def __init__(self):
        self.bubble_size_threshold_mm = 1.0
    
    def bubble_leak_rate(self, bubble_diameter_mm: float,
                        formation_time_s: float = 1.0) -> float:
        """
        Estimate leak rate from bubble size.
        
        Args:
            bubble_diameter_mm: Diameter
            formation_time_s: Formation time
        
        Returns:
            Leak rate Pa*m^3/s
        """
        if formation_time_s <= 0:
            return 0.0
        # Simplified: volume of sphere / time
        r_mm = bubble_diameter_mm / 2.0
        volume_m3 = (4.0 / 3.0) * math.pi * (r_mm * 1e-3) ** 3
        return volume_m3 * 101325.0 / formation_time_s  # Atmospheric pressure
    
    def leak_detected(self, bubble_count: int,
                     time_s: float = 60.0) -> bool:
        """
        Check if leak is detected.
        
        Args:
            bubble_count: Bubbles observed
            time_s: Observation time
        
        Returns:
            True if leak
        """
        if time_s <= 0:
            return False
        rate = bubble_count / time_s
        return rate > 0.1  # More than 0.1 bubbles per second
    
    def bubble_frequency(self, leak_rate_Pa_m3_s: float,
                        pressure_diff_Pa: float = 101325.0) -> float:
        """
        Compute expected bubble frequency.
        
        Args:
            leak_rate_Pa_m3_s: Leak rate
            pressure_diff_Pa: Pressure difference
        
        Returns:
            Bubbles per second
        """
        if pressure_diff_Pa <= 0:
            return 0.0
        # Volume flow = Q / P
        volume_flow = leak_rate_Pa_m3_s / pressure_diff_Pa
        # Assuming 1mm bubbles
        bubble_volume = (4.0 / 3.0) * math.pi * (0.5e-3) ** 3
        return volume_flow / bubble_volume


class AcousticLeakDetector:
    """
    Acoustic leak detection.
    """
    
    def __init__(self, frequency_range_kHz: Tuple[float, float] = (20.0, 100.0)):
        """
        Args:
            frequency_range_kHz: Frequency range
        """
        self.freq_range = frequency_range_kHz
    
    def detect_turbulence(self, sound_level_dB: float,
                         frequency_kHz: float) -> bool:
        """
        Detect turbulent flow from sound.
        
        Args:
            sound_level_dB: Sound level
            frequency_kHz: Frequency
        
        Returns:
            True if turbulent
        """
        if not (self.freq_range[0] <= frequency_kHz <= self.freq_range[1]):
            return False
        return sound_level_dB > 40.0
    
    def leak_intensity(self, sound_pressure_Pa: float) -> float:
        """
        Compute leak intensity.
        
        Args:
            sound_pressure_Pa: Sound pressure
        
        Returns:
            Intensity in W/m^2
        """
        rho_c = 400.0  # Air impedance
        return sound_pressure_Pa ** 2 / rho_c


class LeakDetection:
    """
    Unified leak detection controller.
    """
    
    def __init__(self):
        self.pressure_tester = PressureDecayTester()
        self.helium_detector = HeliumMassSpectrometer()
        self.bubble_tester = BubbleTester()
        self.acoustic_detector = AcousticLeakDetector()
        self.leaks: List[LeakRate] = []
    
    def test_pressure_decay(self, initial_Pa: float,
                           final_Pa: float,
                           time_s: float) -> Dict:
        """
        Run pressure decay test.
        
        Args:
            initial_Pa: Initial
            final_Pa: Final
            time_s: Time
        
        Returns:
            Report
        """
        rate = self.pressure_tester.leak_rate(initial_Pa, final_Pa, time_s)
        leak = LeakRate(rate, LeakMethod.PRESSURE_DECAY)
        self.leaks.append(leak)
        
        return {
            "method": "pressure_decay",
            "leak_rate_Pa_m3_s": rate,
            "acceptable": rate < 1.0
        }
    
    def test_helium(self, signal: float,
                   calibration: float = 1e-9) -> Dict:
        """
        Run helium test.
        
        Args:
            signal: Signal
            calibration: Calibration
        
        Returns:
            Report
        """
        detected = self.helium_detector.detect_leak(signal)
        rate = self.helium_detector.leak_rate_from_signal(signal, calibration)
        leak = LeakRate(rate, LeakMethod.HELIUM_MASS_SPEC)
        self.leaks.append(leak)
        
        return {
            "method": "helium_mass_spec",
            "detected": detected,
            "leak_rate_Pa_m3_s": rate
        }
    
    def test_bubble(self, bubble_count: int,
                   time_s: float = 60.0) -> Dict:
        """
        Run bubble test.
        
        Args:
            bubble_count: Count
            time_s: Time
        
        Returns:
            Report
        """
        detected = self.bubble_tester.leak_detected(bubble_count, time_s)
        
        return {
            "method": "bubble_test",
            "detected": detected,
            "bubble_count": bubble_count
        }
    
    def leak_summary(self) -> Dict:
        """Get leak summary."""
        if not self.leaks:
            return {"status": "no_leaks"}
        
        methods = {}
        for leak in self.leaks:
            m = leak.method.value
            methods[m] = methods.get(m, 0) + 1
        
        return {
            "total_tests": len(self.leaks),
            "max_leak_rate": max(l.rate_Pa_m3_s for l in self.leaks),
            "methods_used": methods
        }
