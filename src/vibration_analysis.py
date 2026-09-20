"""
Vibration Analysis Module
FFT spectrum analysis, RMS/peak detection, bearing fault diagnosis,
crest factor, kurtosis, and envelope analysis for autonomous condition monitoring.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class BearingFaultType(Enum):
    """Types of bearing faults."""
    OUTER_RACE = "outer_race"
    INNER_RACE = "inner_race"
    BALL = "ball"
    CAGE = "cage"


class VibrationAnalyzer:
    """
    Core vibration signal analysis.
    """
    
    def __init__(self, sampling_rate_Hz: float = 10000.0):
        """
        Args:
            sampling_rate_Hz: Sampling rate
        """
        self.fs = sampling_rate_Hz
    
    def rms(self, signal: List[float]) -> float:
        """
        Compute RMS.
        
        Args:
            signal: Time series
        
        Returns:
            RMS value
        """
        if not signal:
            return 0.0
        return math.sqrt(sum(x**2 for x in signal) / len(signal))
    
    def peak(self, signal: List[float]) -> float:
        """
        Compute peak amplitude.
        
        Args:
            signal: Time series
        
        Returns:
            Peak
        """
        if not signal:
            return 0.0
        return max(abs(x) for x in signal)
    
    def peak_to_peak(self, signal: List[float]) -> float:
        """
        Compute peak-to-peak.
        
        Args:
            signal: Time series
        
        Returns:
            P-P
        """
        if not signal:
            return 0.0
        return max(signal) - min(signal)
    
    def crest_factor(self, signal: List[float]) -> float:
        """
        Compute crest factor = peak / RMS.
        
        Args:
            signal: Time series
        
        Returns:
            Crest factor
        """
        rms_val = self.rms(signal)
        if rms_val <= 0:
            return 0.0
        return self.peak(signal) / rms_val
    
    def kurtosis(self, signal: List[float]) -> float:
        """
        Compute kurtosis (normalized).
        
        Args:
            signal: Time series
        
        Returns:
            Kurtosis
        """
        if not signal:
            return 0.0
        n = len(signal)
        mean = sum(signal) / n
        variance = sum((x - mean)**2 for x in signal) / n
        if variance <= 0:
            return 0.0
        return sum((x - mean)**4 for x in signal) / (n * variance**2) - 3.0
    
    def dft(self, signal: List[float]) -> List[complex]:
        """
        Discrete Fourier Transform.
        
        Args:
            signal: Time series
        
        Returns:
            Complex spectrum
        """
        N = len(signal)
        spectrum = []
        for k in range(N):
            real = sum(signal[n] * math.cos(2.0 * math.pi * k * n / N) for n in range(N))
            imag = -sum(signal[n] * math.sin(2.0 * math.pi * k * n / N) for n in range(N))
            spectrum.append(complex(real, imag))
        return spectrum
    
    def magnitude_spectrum(self, signal: List[float]) -> List[float]:
        """
        Compute magnitude spectrum.
        
        Args:
            signal: Time series
        
        Returns:
            Magnitudes
        """
        spectrum = self.dft(signal)
        return [abs(c) / len(signal) for c in spectrum[:len(spectrum)//2]]
    
    def dominant_frequency(self, signal: List[float]) -> Tuple[float, float]:
        """
        Find dominant frequency.
        
        Args:
            signal: Time series
        
        Returns:
            (frequency_Hz, magnitude)
        """
        mags = self.magnitude_spectrum(signal)
        if not mags:
            return (0.0, 0.0)
        
        max_idx = max(range(len(mags)), key=lambda i: mags[i])
        freq_resolution = self.fs / len(signal)
        return (max_idx * freq_resolution, mags[max_idx])


class BearingDiagnoser:
    """
    Bearing fault diagnosis.
    """
    
    def __init__(self, shaft_speed_rpm: float = 1800.0,
                 num_balls: int = 8,
                 ball_diameter_mm: float = 10.0,
                 pitch_diameter_mm: float = 50.0,
                 contact_angle_deg: float = 0.0):
        """
        Args:
            shaft_speed_rpm: Shaft speed
            num_balls: Number of balls
            ball_diameter_mm: Ball diameter
            pitch_diameter_mm: Pitch diameter
            contact_angle_deg: Contact angle
        """
        self.speed_hz = shaft_speed_rpm / 60.0
        self.Nb = num_balls
        self.Bd = ball_diameter_mm
        self.Pd = pitch_diameter_mm
        self.beta = math.radians(contact_angle_deg)
    
    def bpf_outer(self) -> float:
        """
        Ball pass frequency outer race.
        
        Returns:
            Frequency in Hz
        """
        return self.Nb * self.speed_hz / 2.0 * (1.0 - self.Bd / self.Pd * math.cos(self.beta))
    
    def bpf_inner(self) -> float:
        """
        Ball pass frequency inner race.
        
        Returns:
            Frequency in Hz
        """
        return self.Nb * self.speed_hz / 2.0 * (1.0 + self.Bd / self.Pd * math.cos(self.beta))
    
    def bsf(self) -> float:
        """
        Ball spin frequency.
        
        Returns:
            Frequency in Hz
        """
        return self.Pd / self.Bd * self.speed_hz / 2.0 * (1.0 - (self.Bd / self.Pd * math.cos(self.beta))**2)
    
    def ftf(self) -> float:
        """
        Fundamental train frequency (cage).
        
        Returns:
            Frequency in Hz
        """
        return self.speed_hz / 2.0 * (1.0 - self.Bd / self.Pd * math.cos(self.beta))
    
    def detect_fault(self, spectrum: List[float],
                    freq_resolution_Hz: float,
                    threshold_multiplier: float = 3.0) -> Dict[str, bool]:
        """
        Detect bearing faults from spectrum.
        
        Args:
            spectrum: Magnitude spectrum
            freq_resolution_Hz: Frequency resolution
            threshold_multiplier: Detection threshold
        
        Returns:
            Fault detection results
        """
        if not spectrum:
            return {t.value: False for t in BearingFaultType}
        
        baseline = sum(spectrum) / len(spectrum)
        threshold = baseline * threshold_multiplier
        
        freqs = {
            BearingFaultType.OUTER_RACE: self.bpf_outer(),
            BearingFaultType.INNER_RACE: self.bpf_inner(),
            BearingFaultType.BALL: self.bsf(),
            BearingFaultType.CAGE: self.ftf()
        }
        
        results = {}
        for fault_type, freq in freqs.items():
            idx = int(round(freq / freq_resolution_Hz))
            if 0 <= idx < len(spectrum):
                results[fault_type.value] = spectrum[idx] > threshold
            else:
                results[fault_type.value] = False
        
        return results


class EnvelopeAnalyzer:
    """
    Envelope analysis for bearing diagnostics.
    """
    
    def __init__(self, sampling_rate_Hz: float = 10000.0):
        """
        Args:
            sampling_rate_Hz: Sampling rate
        """
        self.fs = sampling_rate_Hz
    
    def hilbert_envelope(self, signal: List[float]) -> List[float]:
        """
        Compute envelope using Hilbert transform approximation.
        
        Args:
            signal: Time series
        
        Returns:
            Envelope
        """
        if not signal:
            return []
        
        # Simplified: square and smooth
        squared = [x**2 for x in signal]
        envelope = []
        window = 5
        for i in range(len(squared)):
            start = max(0, i - window//2)
            end = min(len(squared), i + window//2 + 1)
            envelope.append(math.sqrt(sum(squared[start:end]) / (end - start)))
        return envelope
    
    def envelope_spectrum(self, signal: List[float]) -> List[float]:
        """
        Compute envelope spectrum.
        
        Args:
            signal: Time series
        
        Returns:
            Envelope spectrum magnitudes
        """
        env = self.hilbert_envelope(signal)
        analyzer = VibrationAnalyzer(self.fs)
        return analyzer.magnitude_spectrum(env)


class VibrationAnalysis:
    """
    Unified vibration analysis controller.
    """
    
    def __init__(self, sampling_rate_Hz: float = 10000.0):
        """
        Args:
            sampling_rate_Hz: Sampling rate
        """
        self.analyzer = VibrationAnalyzer(sampling_rate_Hz)
        self.bearing = BearingDiagnoser()
        self.envelope = EnvelopeAnalyzer(sampling_rate_Hz)
        self.history: List[Dict] = []
    
    def analyze(self, signal: List[float]) -> Dict:
        """
        Full vibration analysis.
        
        Args:
            signal: Time series
        
        Returns:
            Analysis report
        """
        rms_val = self.analyzer.rms(signal)
        peak_val = self.analyzer.peak(signal)
        crest = self.analyzer.crest_factor(signal)
        kurt = self.analyzer.kurtosis(signal)
        
        dom_freq, dom_mag = self.analyzer.dominant_frequency(signal)
        spectrum = self.analyzer.magnitude_spectrum(signal)
        
        freq_res = self.analyzer.fs / len(signal) if signal else 1.0
        faults = self.bearing.detect_fault(spectrum, freq_res)
        
        report = {
            "rms": rms_val,
            "peak": peak_val,
            "crest_factor": crest,
            "kurtosis": kurt,
            "dominant_frequency_Hz": dom_freq,
            "dominant_magnitude": dom_mag,
            "bearing_faults": faults,
            "alert": crest > 6.0 or kurt > 3.0
        }
        self.history.append(report)
        return report
    
    def trend_analysis(self, parameter: str = "rms") -> List[float]:
        """
        Extract parameter trend.
        
        Args:
            parameter: Parameter name
        
        Returns:
            Trend values
        """
        return [h.get(parameter, 0.0) for h in self.history]
    
    def analysis_summary(self) -> Dict:
        """Get analysis summary."""
        if not self.history:
            return {"status": "no_data"}
        
        alerts = sum(1 for h in self.history if h.get("alert", False))
        return {
            "analyses": len(self.history),
            "alerts": alerts,
            "avg_rms": sum(h["rms"] for h in self.history) / len(self.history)
        }
