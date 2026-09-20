"""
Vibration Analysis Module
Time domain analysis, frequency domain analysis, modal analysis,
shock response, and vibration severity assessment for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VibrationSample:
    """Vibration sample."""
    timestamp_s: float
    acceleration_ms2: float


class TimeDomainAnalyzer:
    """
    Time domain vibration analysis.
    """
    
    def __init__(self):
        pass
    
    def rms(self, samples: List[float]) -> float:
        """
        Compute RMS.
        
        Args:
            samples: Acceleration values
        
        Returns:
            RMS in m/s2
        """
        if not samples:
            return 0.0
        return math.sqrt(sum(a**2 for a in samples) / len(samples))
    
    def peak(self, samples: List[float]) -> float:
        """
        Compute peak.
        
        Args:
            samples: Values
        
        Returns:
            Peak in m/s2
        """
        if not samples:
            return 0.0
        return max(abs(a) for a in samples)
    
    def crest_factor(self, samples: List[float]) -> float:
        """
        Compute crest factor.
        
        Args:
            samples: Values
        
        Returns:
            Crest factor
        """
        rms_val = self.rms(samples)
        peak_val = self.peak(samples)
        if rms_val <= 0:
            return 0.0
        return peak_val / rms_val
    
    def kurtosis(self, samples: List[float]) -> float:
        """
        Compute kurtosis.
        
        Args:
            samples: Values
        
        Returns:
            Kurtosis
        """
        if len(samples) < 4:
            return 0.0
        
        n = len(samples)
        mean = sum(samples) / n
        variance = sum((a - mean)**2 for a in samples) / n
        
        if variance <= 0:
            return 0.0
        
        fourth_moment = sum((a - mean)**4 for a in samples) / n
        return fourth_moment / (variance ** 2)


class FrequencyDomainAnalyzer:
    """
    Frequency domain vibration analysis.
    """
    
    def __init__(self, sampling_rate_Hz: float = 1000.0):
        """
        Args:
            sampling_rate_Hz: Sampling rate
        """
        self.fs = sampling_rate_Hz
    
    def dft(self, samples: List[float]) -> List[complex]:
        """
        Compute DFT.
        
        Args:
            samples: Time domain samples
        
        Returns:
            Frequency domain
        """
        N = len(samples)
        result = []
        for k in range(N):
            real = 0.0
            imag = 0.0
            for n in range(N):
                angle = -2.0 * math.pi * k * n / N
                real += samples[n] * math.cos(angle)
                imag += samples[n] * math.sin(angle)
            result.append(complex(real, imag))
        return result
    
    def magnitude_spectrum(self, samples: List[float]) -> List[float]:
        """
        Compute magnitude spectrum.
        
        Args:
            samples: Time domain
        
        Returns:
            Magnitudes
        """
        dft_result = self.dft(samples)
        N = len(samples)
        return [abs(dft_result[k]) / N for k in range(N // 2)]
    
    def dominant_frequency(self, samples: List[float]) -> float:
        """
        Find dominant frequency.
        
        Args:
            samples: Time domain
        
        Returns:
            Dominant frequency in Hz
        """
        mags = self.magnitude_spectrum(samples)
        if not mags:
            return 0.0
        
        max_idx = mags.index(max(mags))
        return max_idx * self.fs / len(samples)
    
    def octave_band(self, samples: List[float],
                   center_freq_Hz: float) -> float:
        """
        Compute octave band level.
        
        Args:
            samples: Time domain
            center_freq_Hz: Center frequency
        
        Returns:
        """
        mags = self.magnitude_spectrum(samples)
        N = len(samples)
        freqs = [k * self.fs / N for k in range(N // 2)]
        
        # Find band
        lower = center_freq_Hz / math.sqrt(2)
        upper = center_freq_Hz * math.sqrt(2)
        
        band_energy = 0.0
        for i, f in enumerate(freqs):
            if lower <= f <= upper and i < len(mags):
                band_energy += mags[i] ** 2
        
        return math.sqrt(band_energy)


class ModalAnalyzer:
    """
    Modal analysis.
    """
    
    def __init__(self):
        self.modes: List[Dict] = []
    
    def natural_frequency(self, stiffness_N_m: float,
                         mass_kg: float) -> float:
        """
        Compute natural frequency.
        
        Args:
            stiffness_N_m: Stiffness
            mass_kg: Mass
        
        Returns:
            Natural frequency in Hz
        """
        if mass_kg <= 0:
            return 0.0
        return math.sqrt(stiffness_N_m / mass_kg) / (2.0 * math.pi)
    
    def damping_ratio(self, natural_freq_Hz: float,
                     damped_freq_Hz: float) -> float:
        """
        Compute damping ratio.
        
        Args:
            natural_freq_Hz: Natural frequency
            damped_freq_Hz: Damped frequency
        
        Returns:
            Damping ratio
        """
        if natural_freq_Hz <= 0:
            return 0.0
        ratio = damped_freq_Hz / natural_freq_Hz
        if ratio >= 1.0:
            return 0.0
        return math.sqrt(1.0 - ratio ** 2)
    
    def add_mode(self, freq_Hz: float, damping: float,
                mode_shape: List[float]):
        """
        Add mode.
        
        Args:
            freq_Hz: Frequency
            damping: Damping ratio
            mode_shape: Mode shape
        """
        self.modes.append({
            "frequency_Hz": freq_Hz,
            "damping_ratio": damping,
            "mode_shape": mode_shape
        })


class ShockResponseAnalyzer:
    """
    Shock response analysis.
    """
    
    def __init__(self):
        pass
    
    def shock_spectrum(self, pulse_samples: List[float],
                      natural_freqs_Hz: List[float],
                      sampling_rate_Hz: float = 1000.0) -> List[float]:
        """
        Compute shock response spectrum.
        
        Args:
            pulse_samples: Pulse acceleration
            natural_freqs_Hz: Natural frequencies
            sampling_rate_Hz: Sampling rate
        
        Returns:
            SRS values
        """
        srs = []
        dt = 1.0 / sampling_rate_Hz
        
        for fn in natural_freqs_Hz:
            if fn <= 0:
                srs.append(0.0)
                continue
            
            omega = 2.0 * math.pi * fn
            # Simplified: max response of SDOF
            max_resp = 0.0
            resp = 0.0
            vel = 0.0
            
            for acc in pulse_samples:
                # Newmark-beta (simplified)
                vel += acc * dt
                resp += vel * dt
                # Restoring force
                vel -= omega * omega * resp * dt
                max_resp = max(max_resp, abs(resp))
            
            srs.append(max_resp * omega * omega)
        
        return srs


class VibrationSeverity:
    """
    Vibration severity assessment.
    """
    
    def __init__(self):
        self.iso_thresholds = [
            (0.28, "good"),
            (1.12, "satisfactory"),
            (2.8, "unsatisfactory"),
            (7.1, "unacceptable")
        ]
    
    def assess_iso(self, rms_velocity_mm_s: float) -> str:
        """
        Assess per ISO 10816.
        
        Args:
            rms_velocity_mm_s: RMS velocity
        
        Returns:
            Severity class
        """
        for threshold, level in self.iso_thresholds:
            if rms_velocity_mm_s <= threshold:
                return level
        return "unacceptable"
    
    def velocity_from_acceleration(self, rms_accel_ms2: float,
                                   freq_Hz: float = 60.0) -> float:
        """
        Convert acceleration to velocity.
        
        Args:
            rms_accel_ms2: RMS acceleration
            freq_Hz: Frequency
        
        Returns:
            RMS velocity in mm/s
        """
        if freq_Hz <= 0:
            return 0.0
        omega = 2.0 * math.pi * freq_Hz
        return rms_accel_ms2 / omega * 1000.0


class VibrationAnalysis:
    """
    Unified vibration analysis controller.
    """
    
    def __init__(self, sampling_rate_Hz: float = 1000.0):
        self.time_domain = TimeDomainAnalyzer()
        self.freq_domain = FrequencyDomainAnalyzer(sampling_rate_Hz)
        self.modal = ModalAnalyzer()
        self.shock = ShockResponseAnalyzer()
        self.severity = VibrationSeverity()
        self.samples: List[float] = []
    
    def record(self, samples: List[float]):
        """
        Record samples.
        
        Args:
            samples: Acceleration samples
        """
        self.samples = samples
    
    def analyze(self) -> Dict:
        """
        Analyze vibration.
        
        Returns:
            Results
        """
        if not self.samples:
            return {}
        
        rms = self.time_domain.rms(self.samples)
        peak = self.time_domain.peak(self.samples)
        crest = self.time_domain.crest_factor(self.samples)
        kurt = self.time_domain.kurtosis(self.samples)
        dom_freq = self.freq_domain.dominant_frequency(self.samples)
        
        vel = self.severity.velocity_from_acceleration(rms, dom_freq)
        severity = self.severity.assess_iso(vel)
        
        return {
            "rms_ms2": rms,
            "peak_ms2": peak,
            "crest_factor": crest,
            "kurtosis": kurt,
            "dominant_freq_Hz": dom_freq,
            "velocity_mm_s": vel,
            "severity": severity
        }
    
    def va_summary(self) -> Dict:
        """Get summary."""
        return {
            "samples": len(self.samples),
            "fs_Hz": self.freq_domain.fs
        }
