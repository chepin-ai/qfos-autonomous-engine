"""
Acoustic Resonance Module
Resonance frequency analysis, modal parameter extraction, damping
estimation, and defect detection via spectral shifts for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ResonanceMode:
    """Vibration mode."""
    frequency_Hz: float
    amplitude: float
    damping_ratio: float
    phase_rad: float


class SpectrumAnalyzer:
    """
    FFT-based spectrum analysis.
    """
    
    def __init__(self, sample_rate_Hz: float = 10000.0):
        """
        Args:
            sample_rate_Hz: Sample rate
        """
        self.fs = sample_rate_Hz
    
    def dft(self, signal: List[float]) -> List[complex]:
        """
        Discrete Fourier transform.
        
        Args:
            signal: Input
        
        Returns:
            Spectrum
        """
        N = len(signal)
        spectrum = []
        for k in range(N):
            real = 0.0
            imag = 0.0
            for n in range(N):
                angle = -2.0 * math.pi * k * n / N
                real += signal[n] * math.cos(angle)
                imag += signal[n] * math.sin(angle)
            spectrum.append(complex(real, imag))
        return spectrum
    
    def magnitude_spectrum(self, signal: List[float]) -> List[float]:
        """
        Compute magnitude spectrum.
        
        Args:
            signal: Signal
        
        Returns:
            Magnitudes
        """
        spectrum = self.dft(signal)
        return [abs(z) / len(signal) for z in spectrum]
    
    def frequency_bins(self, N: int) -> List[float]:
        """
        Frequency bins.
        
        Args:
            N: Samples
        
        Returns:
            Frequencies
        """
        return [k * self.fs / N for k in range(N // 2 + 1)]


class ModalExtractor:
    """
    Extract modal parameters from spectrum.
    """
    
    def __init__(self):
        self.modes: List[ResonanceMode] = []
    
    def find_peaks(self, magnitudes: List[float],
                  frequencies: List[float],
                  threshold: float = 0.1) -> List[Tuple[int, float]]:
        """
        Find spectral peaks.
        
        Args:
            magnitudes: Magnitudes
            frequencies: Frequencies
            threshold: Threshold
        
        Returns:
            (index, freq) list
        """
        peaks = []
        for i in range(1, len(magnitudes) - 1):
            if magnitudes[i] > threshold and magnitudes[i] > magnitudes[i - 1] and magnitudes[i] > magnitudes[i + 1]:
                peaks.append((i, frequencies[i]))
        return peaks
    
    def estimate_damping(self, signal: List[float],
                        mode_freq_Hz: float,
                        sample_rate_Hz: float = 10000.0) -> float:
        """
        Estimate damping ratio from decay.
        
        Args:
            signal: Decay signal
            mode_freq_Hz: Mode frequency
            sample_rate_Hz: Sample rate
        
        Returns:
            Damping ratio
        """
        # Find peaks in decay
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1]:
                peaks.append((i, signal[i]))
        
        if len(peaks) < 2:
            return 0.01
        
        # Log decrement method
        period_samples = int(sample_rate_Hz / mode_freq_Hz)
        if period_samples < 1:
            period_samples = 1
        
        ratios = []
        for i in range(1, min(len(peaks), 10)):
            if peaks[i][1] > 0 and peaks[i - 1][1] > 0:
                delta = math.log(peaks[i - 1][1] / peaks[i][1])
                ratios.append(delta)
        
        if not ratios:
            return 0.01
        
        avg_delta = sum(ratios) / len(ratios)
        return avg_delta / (2.0 * math.pi)
    
    def q_factor(self, frequency_Hz: float,
                damping_ratio: float) -> float:
        """
        Compute Q factor.
        
        Args:
            frequency_Hz: Frequency
            damping_ratio: Damping
        
        Returns:
            Q
        """
        if damping_ratio <= 0:
            return float('inf')
        return 1.0 / (2.0 * damping_ratio)
    
    def extract_modes(self, signal: List[float],
                     sample_rate_Hz: float = 10000.0) -> List[ResonanceMode]:
        """
        Extract all modes.
        
        Args:
            signal: Signal
            sample_rate_Hz: Sample rate
        
        Returns:
            Modes
        """
        sa = SpectrumAnalyzer(sample_rate_Hz)
        mags = sa.magnitude_spectrum(signal)
        freqs = sa.frequency_bins(len(signal))
        
        peaks = self.find_peaks(mags[:len(freqs)], freqs)
        
        modes = []
        for idx, freq in peaks[:5]:
            damping = self.estimate_damping(signal, freq, sample_rate_Hz)
            q = self.q_factor(freq, damping)
            modes.append(ResonanceMode(
                frequency_Hz=freq,
                amplitude=mags[idx],
                damping_ratio=damping,
                phase_rad=0.0
            ))
        
        self.modes = modes
        return modes


class ResonanceDefectDetector:
    """
    Detect defects via resonance shifts.
    """
    
    def __init__(self):
        self.baseline_modes: List[ResonanceMode] = []
        self.defects: List[Dict] = []
    
    def set_baseline(self, modes: List[ResonanceMode]):
        """
        Set baseline modes.
        
        Args:
            modes: Baseline
        """
        self.baseline_modes = modes
    
    def detect_shift(self, current_modes: List[ResonanceMode],
                    threshold_Hz: float = 10.0) -> List[Dict]:
        """
        Detect frequency shifts.
        
        Args:
            current_modes: Current
            threshold_Hz: Threshold
        
        Returns:
            Shifts
        """
        shifts = []
        for i, current in enumerate(current_modes):
            if i < len(self.baseline_modes):
                baseline = self.baseline_modes[i]
                delta_f = abs(current.frequency_Hz - baseline.frequency_Hz)
                delta_a = abs(current.amplitude - baseline.amplitude)
                
                if delta_f > threshold_Hz:
                    shifts.append({
                        "mode": i,
                        "delta_freq_Hz": delta_f,
                        "delta_amp": delta_a,
                        "severity": "high" if delta_f > 3 * threshold_Hz else "medium"
                    })
        
        self.defects = shifts
        return shifts


class AcousticResonance:
    """
    Unified acoustic resonance controller.
    """
    
    def __init__(self, sample_rate_Hz: float = 10000.0):
        """
        Args:
            sample_rate_Hz: Sample rate
        """
        self.fs = sample_rate_Hz
        self.spectrum = SpectrumAnalyzer(sample_rate_Hz)
        self.modal = ModalExtractor()
        self.defect_detector = ResonanceDefectDetector()
        self.measurements: List[List[float]] = []
        self.modes_history: List[List[ResonanceMode]] = []
    
    def measure(self, signal: List[float]):
        """
        Record measurement.
        
        Args:
            signal: Signal
        """
        self.measurements.append(signal)
    
    def analyze(self) -> List[ResonanceMode]:
        """
        Analyze latest measurement.
        
        Returns:
            Modes
        """
        if not self.measurements:
            return []
        
        modes = self.modal.extract_modes(self.measurements[-1], self.fs)
        self.modes_history.append(modes)
        return modes
    
    def detect(self, threshold_Hz: float = 10.0) -> List[Dict]:
        """
        Detect defects.
        
        Args:
            threshold_Hz: Threshold
        
        Returns:
            Defects
        """
        if len(self.modes_history) < 2:
            return []
        
        self.defect_detector.set_baseline(self.modes_history[0])
        return self.defect_detector.detect_shift(self.modes_history[-1], threshold_Hz)
    
    def resonance_summary(self) -> Dict:
        """Get summary."""
        latest_modes = self.modes_history[-1] if self.modes_history else []
        return {
            "measurements": len(self.measurements),
            "modes": len(latest_modes),
            "defects": len(self.defect_detector.defects),
            "sample_rate_Hz": self.fs
        }
