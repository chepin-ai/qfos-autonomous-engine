"""
X-ray Fluorescence Module
Elemental analysis with XRF peak detection, energy calibration,
matrix correction, and quantitative analysis for autonomous materials
characterization.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class XRFPeak:
    """XRF spectral peak."""
    energy_keV: float
    intensity: float
    fwhm_keV: float
    element: str = ""


class EnergyCalibrator:
    """
    XRF energy calibration.
    """
    
    def __init__(self):
        self.gain = 1.0
        self.offset = 0.0
        self.calibration_points: List[Tuple[float, float]] = []
    
    def add_calibration_point(self, channel: float, energy_keV: float):
        """
        Add calibration point.
        
        Args:
            channel: Channel number
            energy_keV: Known energy
        """
        self.calibration_points.append((channel, energy_keV))
    
    def calibrate(self):
        """
        Fit linear calibration.
        """
        if len(self.calibration_points) < 2:
            return
        
        # Linear regression
        n = len(self.calibration_points)
        sum_x = sum(p[0] for p in self.calibration_points)
        sum_y = sum(p[1] for p in self.calibration_points)
        sum_xy = sum(p[0] * p[1] for p in self.calibration_points)
        sum_x2 = sum(p[0] ** 2 for p in self.calibration_points)
        
        denom = n * sum_x2 - sum_x ** 2
        if abs(denom) > 1e-10:
            self.gain = (n * sum_xy - sum_x * sum_y) / denom
            self.offset = (sum_y - self.gain * sum_x) / n
    
    def channel_to_energy(self, channel: float) -> float:
        """
        Convert channel to energy.
        
        Args:
            channel: Channel
        
        Returns:
            Energy in keV
        """
        return self.gain * channel + self.offset
    
    def energy_to_channel(self, energy_keV: float) -> float:
        """
        Convert energy to channel.
        
        Args:
            energy_keV: Energy
        
        Returns:
            Channel
        """
        if abs(self.gain) < 1e-10:
            return 0.0
        return (energy_keV - self.offset) / self.gain


class PeakDetector:
    """
    XRF peak detection.
    """
    
    def __init__(self):
        self.threshold = 0.1
    
    def smooth(self, spectrum: List[float],
              window: int = 3) -> List[float]:
        """
        Smooth spectrum.
        
        Args:
            spectrum: Spectrum
            window: Window size
        
        Returns:
            Smoothed
        """
        smoothed = []
        half = window // 2
        for i in range(len(spectrum)):
            s = 0.0
            count = 0
            for j in range(i - half, i + half + 1):
                if 0 <= j < len(spectrum):
                    s += spectrum[j]
                    count += 1
            smoothed.append(s / max(count, 1))
        return smoothed
    
    def find_peaks(self, spectrum: List[float],
                  threshold: Optional[float] = None) -> List[Tuple[int, float]]:
        """
        Find peaks.
        
        Args:
            spectrum: Spectrum
            threshold: Threshold
        
        Returns:
            (index, intensity) list
        """
        thresh = threshold if threshold is not None else self.threshold
        smoothed = self.smooth(spectrum)
        peaks = []
        
        for i in range(1, len(smoothed) - 1):
            if smoothed[i] > thresh and smoothed[i] > smoothed[i - 1] and smoothed[i] > smoothed[i + 1]:
                peaks.append((i, smoothed[i]))
        
        return peaks
    
    def estimate_fwhm(self, spectrum: List[float],
                     peak_idx: int) -> float:
        """
        Estimate FWHM.
        
        Args:
            spectrum: Spectrum
            peak_idx: Peak index
        
        Returns:
            FWHM in channels
        """
        peak_val = spectrum[peak_idx]
        half_max = peak_val / 2.0
        
        left = peak_idx
        while left > 0 and spectrum[left] > half_max:
            left -= 1
        
        right = peak_idx
        while right < len(spectrum) - 1 and spectrum[right] > half_max:
            right += 1
        
        return float(right - left)


class ElementIdentifier:
    """
    Identify elements from XRF peaks.
    """
    
    def __init__(self):
        # Characteristic X-ray energies (K-alpha) in keV
        self.element_lines: Dict[str, float] = {
            "Fe": 6.40, "Cu": 8.04, "Zn": 8.64, "Pb": 10.55,
            "Sn": 25.27, "Ag": 22.16, "Au": 66.99, "Cr": 5.41,
            "Ni": 7.48, "Ti": 4.51, "Mn": 5.90, "Co": 6.93
        }
        self.tolerance_keV = 0.2
    
    def identify(self, energy_keV: float) -> Optional[str]:
        """
        Identify element.
        
        Args:
            energy_keV: Peak energy
        
        Returns:
            Element or None
        """
        best_match = None
        best_diff = float('inf')
        
        for element, line_energy in self.element_lines.items():
            diff = abs(energy_keV - line_energy)
            if diff < self.tolerance_keV and diff < best_diff:
                best_diff = diff
                best_match = element
        
        return best_match
    
    def add_element(self, symbol: str, k_alpha_keV: float):
        """
        Add element.
        
        Args:
            symbol: Symbol
            k_alpha_keV: Energy
        """
        self.element_lines[symbol] = k_alpha_keV


class QuantitativeAnalyzer:
    """
    Quantitative XRF analysis.
    """
    
    def __init__(self):
        self.standards: Dict[str, float] = {}
    
    def add_standard(self, element: str, concentration_pct: float):
        """
        Add calibration standard.
        
        Args:
            element: Element
            concentration_pct: Concentration
        """
        self.standards[element] = concentration_pct
    
    def concentration(self, element: str,
                     measured_intensity: float,
                     standard_intensity: float) -> float:
        """
        Estimate concentration.
        
        Args:
            element: Element
            measured_intensity: Sample intensity
            standard_intensity: Standard intensity
        
        Returns:
            Concentration in %
        """
        if standard_intensity <= 0:
            return 0.0
        
        std_conc = self.standards.get(element, 100.0)
        return std_conc * measured_intensity / standard_intensity
    
    def matrix_correction(self, concentration: float,
                         absorption_coeff: float = 1.0,
                         enhancement_coeff: float = 1.0) -> float:
        """
        Apply matrix correction.
        
        Args:
            concentration: Raw concentration
            absorption_coeff: Absorption
            enhancement_coeff: Enhancement
        
        Returns:
            Corrected
        """
        if absorption_coeff <= 0 or enhancement_coeff <= 0:
            return concentration
        return concentration / (absorption_coeff * enhancement_coeff)


class XRayFluorescence:
    """
    Unified XRF controller.
    """
    
    def __init__(self):
        self.calibrator = EnergyCalibrator()
        self.peak_detector = PeakDetector()
        self.element_id = ElementIdentifier()
        self.quantitative = QuantitativeAnalyzer()
        self.spectra: List[List[float]] = []
        self.peaks: List[XRFPeak] = []
    
    def acquire_spectrum(self, spectrum: List[float]):
        """
        Acquire spectrum.
        
        Args:
            spectrum: Raw spectrum
        """
        self.spectra.append(spectrum)
    
    def analyze_peaks(self) -> List[XRFPeak]:
        """
        Analyze peaks.
        
        Returns:
            Peaks
        """
        if not self.spectra:
            return []
        
        latest = self.spectra[-1]
        peak_data = self.peak_detector.find_peaks(latest)
        
        for idx, intensity in peak_data:
            energy = self.calibrator.channel_to_energy(idx)
            fwhm = self.peak_detector.estimate_fwhm(latest, idx)
            element = self.element_id.identify(energy)
            
            self.peaks.append(XRFPeak(
                energy_keV=energy,
                intensity=intensity,
                fwhm_keV=fwhm * self.calibrator.gain,
                element=element or ""
            ))
        
        return self.peaks
    
    def quantitative_analysis(self) -> Dict[str, float]:
        """
        Perform quantitative analysis.
        
        Returns:
            Concentrations
        """
        results = {}
        
        for peak in self.peaks:
            if peak.element:
                # Use peak intensity as proxy
                std_intensity = self.quantitative.standards.get(peak.element, 0.0)
                if std_intensity > 0:
                    conc = self.quantitative.concentration(
                        peak.element, peak.intensity, std_intensity
                    )
                    results[peak.element] = conc
        
        return results
    
    def xrf_summary(self) -> Dict:
        """Get summary."""
        return {
            "spectra": len(self.spectra),
            "peaks": len(self.peaks),
            "elements": list(set(p.element for p in self.peaks if p.element))
        }
