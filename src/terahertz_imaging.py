"""
Terahertz Imaging Module
THz pulse generation, time-domain spectroscopy, 
reflection/transmission imaging, and material parameter extraction.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class THzPulse:
    """THz pulse data."""
    time_ps: List[float]
    amplitude: List[float]
    frequency_THz: Optional[List[float]] = None
    spectrum: Optional[List[complex]] = None


class THzPulseGenerator:
    """
    Generate THz pulses.
    """
    
    def __init__(self, center_freq_THz: float = 1.0,
                 pulse_width_ps: float = 1.0):
        """
        Args:
            center_freq_THz: Center frequency
            pulse_width_ps: Pulse width
        """
        self.fc = center_freq_THz
        self.sigma = pulse_width_ps
    
    def generate_gaussian_pulse(self, time_points: List[float]) -> THzPulse:
        """
        Generate Gaussian pulse.
        
        Args:
            time_points: Time points in ps
        
        Returns:
            THz pulse
        """
        amplitudes = []
        for t in time_points:
            envelope = math.exp(-(t**2) / (2.0 * self.sigma**2))
            carrier = math.cos(2.0 * math.pi * self.fc * t)
            amplitudes.append(envelope * carrier)
        
        return THzPulse(time_points, amplitudes)
    
    def generate_delta_pulse(self, time_points: List[float]) -> THzPulse:
        """
        Generate delta-like pulse.
        
        Args:
            time_points: Time points
        
        Returns:
            Pulse
        """
        amplitudes = []
        for t in time_points:
            if abs(t) < self.sigma / 3.0:
                amplitudes.append(1.0)
            else:
                amplitudes.append(0.0)
        
        return THzPulse(time_points, amplitudes)


class TimeDomainSpectroscopy:
    """
    Time-domain spectroscopy analysis.
    """
    
    def __init__(self):
        pass
    
    def fft(self, pulse: THzPulse) -> THzPulse:
        """
        Compute FFT of pulse.
        
        Args:
            pulse: Input pulse
        
        Returns:
            Pulse with spectrum
        """
        n = len(pulse.amplitude)
        if n == 0:
            return pulse
        
        # Pad to power of 2
        n_fft = 1
        while n_fft < n:
            n_fft *= 2
        
        # Simple DFT
        spectrum = []
        dt = pulse.time_ps[1] - pulse.time_ps[0] if len(pulse.time_ps) > 1 else 1.0
        freqs = [k / (n_fft * dt) for k in range(n_fft // 2)]
        
        for k in range(n_fft // 2):
            real = sum(pulse.amplitude[i] * math.cos(2.0 * math.pi * k * i / n_fft)
                      for i in range(n))
            imag = -sum(pulse.amplitude[i] * math.sin(2.0 * math.pi * k * i / n_fft)
                       for i in range(n))
            spectrum.append(complex(real, imag))
        
        pulse.frequency_THz = freqs
        pulse.spectrum = spectrum
        return pulse
    
    def transfer_function(self, reference: THzPulse,
                         sample: THzPulse) -> List[complex]:
        """
        Compute transfer function.
        
        Args:
            reference: Reference pulse
            sample: Sample pulse
        
        Returns:
            Transfer function
        """
        ref_fft = self.fft(reference)
        sam_fft = self.fft(sample)
        
        if not ref_fft.spectrum or not sam_fft.spectrum:
            return []
        
        tf = []
        for r, s in zip(ref_fft.spectrum, sam_fft.spectrum):
            if abs(r) > 1e-10:
                tf.append(s / r)
            else:
                tf.append(0.0)
        
        return tf


class MaterialParameterExtractor:
    """
    Extract material parameters from THz data.
    """
    
    def __init__(self):
        pass
    
    def refractive_index(self, transfer_function: List[complex],
                        frequencies_THz: List[float],
                        thickness_mm: float) -> List[float]:
        """
        Extract refractive index.
        
        Args:
            transfer_function: Transfer function
            frequencies_THz: Frequencies
            thickness_mm: Thickness
        
        Returns:
            Refractive indices
        """
        n = []
        c_mm_ps = 0.3  # speed of light in mm/ps
        
        for tf, f in zip(transfer_function, frequencies_THz):
            if f <= 0 or thickness_mm <= 0:
                n.append(1.0)
                continue
            
            phase = math.atan2(tf.imag, tf.real)
            delta_phase = phase  # relative phase shift
            
            n_val = 1.0 - delta_phase * c_mm_ps / (2.0 * math.pi * f * thickness_mm)
            n.append(max(1.0, n_val))
        
        return n
    
    def absorption_coefficient(self, transfer_function: List[complex],
                              frequencies_THz: List[float],
                              thickness_mm: float) -> List[float]:
        """
        Extract absorption coefficient.
        
        Args:
            transfer_function: Transfer function
            frequencies_THz: Frequencies
            thickness_mm: Thickness
        
        Returns:
            Absorption coefficients (1/mm)
        """
        alpha = []
        
        for tf, f in zip(transfer_function, frequencies_THz):
            if thickness_mm <= 0:
                alpha.append(0.0)
                continue
            
            magnitude = abs(tf)
            if magnitude > 0:
                a = -2.0 * math.log(magnitude) / thickness_mm
                alpha.append(max(0.0, a))
            else:
                alpha.append(0.0)
        
        return alpha


class THzImageReconstructor:
    """
    Reconstruct THz images.
    """
    
    def __init__(self, width: int = 64, height: int = 64):
        """
        Args:
            width: Image width
            height: Image height
        """
        self.width = width
        self.height = height
    
    def reconstruct_amplitude(self, scans: List[List[float]]) -> List[List[float]]:
        """
        Reconstruct amplitude image.
        
        Args:
            scans: Pixel scan data
        
        Returns:
            Image
        """
        image = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                idx = i * self.width + j
                if idx < len(scans):
                    # Peak amplitude
                    row.append(max(abs(v) for v in scans[idx]) if scans[idx] else 0.0)
                else:
                    row.append(0.0)
            image.append(row)
        
        return image
    
    def reconstruct_phase(self, scans: List[List[float]]) -> List[List[float]]:
        """
        Reconstruct phase image.
        
        Args:
            scans: Pixel scan data
        
        Returns:
            Phase image
        """
        image = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                idx = i * self.width + j
                if idx < len(scans) and scans[idx]:
                    # Phase at peak
                    peak_idx = scans[idx].index(max(scans[idx], key=abs))
                    row.append(math.atan2(0.0, scans[idx][peak_idx]))
                else:
                    row.append(0.0)
            image.append(row)
        
        return image


class TerahertzImaging:
    """
    Unified THz imaging controller.
    """
    
    def __init__(self):
        self.generator = THzPulseGenerator()
        self.tds = TimeDomainSpectroscopy()
        self.extractor = MaterialParameterExtractor()
        self.reconstructor = THzImageReconstructor()
        self.reference: THzPulse = THzPulse([], [])
        self.samples: List[THzPulse] = []
    
    def capture_reference(self, time_ps: List[float]):
        """
        Capture reference.
        
        Args:
            time_ps: Time points
        """
        self.reference = self.generator.generate_gaussian_pulse(time_ps)
    
    def capture_sample(self, time_ps: List[float],
                      amplitude: List[float]):
        """
        Capture sample.
        
        Args:
            time_ps: Time points
            amplitude: Amplitude
        """
        self.samples.append(THzPulse(time_ps, amplitude))
    
    def analyze(self, thickness_mm: float) -> Dict:
        """
        Analyze sample.
        
        Args:
            thickness_mm: Thickness
        
        Returns:
            Results
        """
        if not self.samples:
            return {}
        
        sample = self.samples[-1]
        tf = self.tds.transfer_function(self.reference, sample)
        
        if not tf:
            return {}
        
        ref_fft = self.tds.fft(self.reference)
        freqs = ref_fft.frequency_THz[:len(tf)] if ref_fft.frequency_THz else []
        
        n = self.extractor.refractive_index(tf, freqs, thickness_mm)
        alpha = self.extractor.absorption_coefficient(tf, freqs, thickness_mm)
        
        return {
            "frequencies_THz": freqs[:5] if freqs else [],
            "refractive_index": n[:5] if n else [],
            "absorption_1_per_mm": alpha[:5] if alpha else []
        }
    
    def thz_summary(self) -> Dict:
        """Get summary."""
        return {
            "samples": len(self.samples),
            "center_freq_THz": self.generator.fc
        }
