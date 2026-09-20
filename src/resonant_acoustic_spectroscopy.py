"""
Resonant Acoustic Spectroscopy Module
Resonance frequency scanning, quality factor estimation,
modal density analysis, and defect-induced shift detection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ResonancePeak:
    """Detected resonance peak."""
    frequency_Hz: float
    amplitude: float
    bandwidth_Hz: float


class ResonanceScanner:
    """
    Scan for resonance frequencies.
    """
    
    def __init__(self, min_freq_Hz: float = 100.0,
                 max_freq_Hz: float = 10000.0):
        """
        Args:
            min_freq_Hz: Min frequency
            max_freq_Hz: Max frequency
        """
        self.min_f = min_freq_Hz
        self.max_f = max_freq_Hz
    
    def find_peaks(self, frequencies: List[float],
                  amplitudes: List[float],
                  threshold: float = 0.3) -> List[ResonancePeak]:
        """
        Find resonance peaks.
        
        Args:
            frequencies: Frequency array
            amplitudes: Amplitude array
            threshold: Detection threshold
        
        Returns:
            Peaks
        """
        if not amplitudes:
            return []
        
        max_amp = max(amplitudes)
        peaks = []
        
        for i in range(1, len(amplitudes) - 1):
            if amplitudes[i] > threshold * max_amp:
                if amplitudes[i] > amplitudes[i - 1] and amplitudes[i] > amplitudes[i + 1]:
                    # Estimate bandwidth
                    bw = self._estimate_bandwidth(frequencies, amplitudes, i)
                    peaks.append(ResonancePeak(frequencies[i], amplitudes[i], bw))
        
        return peaks
    
    def _estimate_bandwidth(self, frequencies: List[float],
                           amplitudes: List[float],
                           peak_idx: int) -> float:
        """
        Estimate 3dB bandwidth.
        
        Args:
            frequencies: Frequencies
            amplitudes: Amplitudes
            peak_idx: Peak index
        
        Returns:
            Bandwidth
        """
        peak_amp = amplitudes[peak_idx]
        half_power = peak_amp / math.sqrt(2)
        
        # Find lower bound
        lower = peak_idx
        for i in range(peak_idx, -1, -1):
            if amplitudes[i] < half_power:
                lower = i
                break
        
        # Find upper bound
        upper = peak_idx
        for i in range(peak_idx, len(amplitudes)):
            if amplitudes[i] < half_power:
                upper = i
                break
        
        return frequencies[upper] - frequencies[lower] if upper > lower else 0.0


class QualityFactorEstimator:
    """
    Estimate quality factors.
    """
    
    def __init__(self):
        pass
    
    def q_factor(self, peak: ResonancePeak) -> float:
        """
        Compute Q factor.
        
        Args:
            peak: Resonance peak
        
        Returns:
            Q factor
        """
        if peak.bandwidth_Hz <= 0:
            return float('inf')
        return peak.frequency_Hz / peak.bandwidth_Hz
    
    def q_factors(self, peaks: List[ResonancePeak]) -> List[float]:
        """
        Compute Q factors for all peaks.
        
        Args:
            peaks: Peaks
        
        Returns:
            Q factors
        """
        return [self.q_factor(p) for p in peaks]
    
    def average_q(self, peaks: List[ResonancePeak]) -> float:
        """
        Compute average Q.
        
        Args:
            peaks: Peaks
        
        Returns:
            Average Q
        """
        qs = self.q_factors(peaks)
        return sum(qs) / len(qs) if qs else 0.0


class ModalDensityAnalyzer:
    """
    Analyze modal density.
    """
    
    def __init__(self):
        pass
    
    def modal_density(self, frequencies: List[float],
                     freq_range_Hz: float = 1000.0) -> float:
        """
        Compute modal density.
        
        Args:
            frequencies: Resonance frequencies
            freq_range_Hz: Frequency range
        
        Returns:
            Modal density (modes/Hz)
        """
        if not frequencies or freq_range_Hz <= 0:
            return 0.0
        return len(frequencies) / freq_range_Hz
    
    def spacing_uniformity(self, frequencies: List[float]) -> float:
        """
        Compute spacing uniformity.
        
        Args:
            frequencies: Frequencies
        
        Returns:
            Coefficient of variation
        """
        if len(frequencies) < 2:
            return 0.0
        
        spacings = [frequencies[i+1] - frequencies[i]
                   for i in range(len(frequencies) - 1)]
        
        mean = sum(spacings) / len(spacings)
        if mean <= 0:
            return 0.0
        
        variance = sum((s - mean)**2 for s in spacings) / len(spacings)
        std = math.sqrt(variance)
        
        return std / mean


class DefectShiftDetector:
    """
    Detect defect-induced frequency shifts.
    """
    
    def __init__(self):
        self.baseline: List[float] = []
    
    def set_baseline(self, frequencies: List[float]):
        """
        Set baseline frequencies.
        
        Args:
            frequencies: Baseline
        """
        self.baseline = sorted(frequencies)
    
    def detect_shifts(self, measured_frequencies: List[float],
                     threshold_Hz: float = 10.0) -> List[Dict]:
        """
        Detect frequency shifts.
        
        Args:
            measured_frequencies: Measured
            threshold_Hz: Threshold
        
        Returns:
            Shifts
        """
        measured = sorted(measured_frequencies)
        shifts = []
        
        for i, (base, meas) in enumerate(zip(self.baseline, measured)):
            shift = meas - base
            if abs(shift) > threshold_Hz:
                shifts.append({
                    "mode": i,
                    "baseline_Hz": base,
                    "measured_Hz": meas,
                    "shift_Hz": shift
                })
        
        return shifts
    
    def correlation_with_defect_size(self, shifts_Hz: List[float],
                                    defect_size_mm: float) -> float:
        """
        Correlate shift with defect size.
        
        Args:
            shifts_Hz: Shifts
            defect_size_mm: Defect size
        
        Returns:
            Correlation
        """
        if not shifts_Hz or defect_size_mm <= 0:
            return 0.0
        
        total_shift = sum(abs(s) for s in shifts_Hz)
        return total_shift / defect_size_mm


class ResonantAcousticSpectroscopy:
    """
    Unified RAS controller.
    """
    
    def __init__(self):
        self.scanner = ResonanceScanner()
        self.q_estimator = QualityFactorEstimator()
        self.modal = ModalDensityAnalyzer()
        self.shift_detector = DefectShiftDetector()
        self.peaks: List[ResonancePeak] = []
    
    def analyze_spectrum(self, frequencies: List[float],
                        amplitudes: List[float]) -> Dict:
        """
        Analyze spectrum.
        
        Args:
            frequencies: Frequencies
            amplitudes: Amplitudes
        
        Returns:
            Analysis
        """
        self.peaks = self.scanner.find_peaks(frequencies, amplitudes)
        qs = self.q_estimator.q_factors(self.peaks)
        
        return {
            "num_peaks": len(self.peaks),
            "peak_frequencies": [p.frequency_Hz for p in self.peaks],
            "q_factors": qs,
            "average_q": self.q_estimator.average_q(self.peaks)
        }
    
    def detect_defects(self, baseline_frequencies: List[float],
                      measured_frequencies: List[float],
                      threshold_Hz: float = 10.0) -> List[Dict]:
        """
        Detect defects from shifts.
        
        Args:
            baseline_frequencies: Baseline
            measured_frequencies: Measured
            threshold_Hz: Threshold
        
        Returns:
            Shifts
        """
        self.shift_detector.set_baseline(baseline_frequencies)
        return self.shift_detector.detect_shifts(measured_frequencies, threshold_Hz)
    
    def ras_summary(self) -> Dict:
        """Get summary."""
        return {
            "peaks": len(self.peaks),
            "frequency_range_Hz": (self.scanner.min_f, self.scanner.max_f)
        }
