"""
XRD Analysis Module
Bragg's law, peak detection, pattern matching,
phase identification, and lattice parameter refinement for autonomous materials science.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class XRDPeak:
    """XRD peak."""
    two_theta: float
    intensity: float
    d_spacing: float
    hkl: Optional[Tuple[int, int, int]] = None


class BraggLaw:
    """
    Bragg's law calculations.
    """
    
    def __init__(self, wavelength_A: float = 1.5406):
        """
        Args:
            wavelength_A: X-ray wavelength in Angstroms (Cu K-alpha)
        """
        self.wavelength = wavelength_A
    
    def d_spacing(self, two_theta_deg: float) -> float:
        """
        Compute d-spacing from 2-theta.
        
        Args:
            two_theta_deg: 2-theta angle in degrees
        
        Returns:
            d-spacing in Angstroms
        """
        theta_rad = math.radians(two_theta_deg / 2.0)
        if math.sin(theta_rad) <= 0:
            return float('inf')
        return self.wavelength / (2.0 * math.sin(theta_rad))
    
    def two_theta(self, d_spacing_A: float) -> float:
        """
        Compute 2-theta from d-spacing.
        
        Args:
            d_spacing_A: d-spacing in Angstroms
        
        Returns:
            2-theta in degrees
        """
        if d_spacing_A <= 0:
            return 0.0
        sin_theta = self.wavelength / (2.0 * d_spacing_A)
        sin_theta = min(1.0, max(-1.0, sin_theta))
        theta = math.asin(sin_theta)
        return math.degrees(2.0 * theta)
    
    def lattice_parameter(self, d_spacing_A: float,
                         hkl: Tuple[int, int, int]) -> float:
        """
        Compute cubic lattice parameter from d-spacing.
        
        Args:
            d_spacing_A: d-spacing
            hkl: Miller indices
        
        Returns:
            Lattice parameter in Angstroms
        """
        h, k, l = hkl
        h2k2l2 = h ** 2 + k ** 2 + l ** 2
        if h2k2l2 == 0:
            return 0.0
        return d_spacing_A * math.sqrt(h2k2l2)


class PeakDetector:
    """
    XRD peak detection.
    """
    
    def __init__(self, min_intensity: float = 0.05):
        """
        Args:
            min_intensity: Minimum relative intensity
        """
        self.min_intensity = min_intensity
    
    def find_peaks(self, two_theta: List[float],
                  intensity: List[float]) -> List[XRDPeak]:
        """
        Find peaks in diffraction pattern.
        
        Args:
            two_theta: 2-theta angles
            intensity: Intensities
        
        Returns:
            Detected peaks
        """
        if not two_theta or not intensity:
            return []
        
        max_intensity = max(intensity)
        threshold = self.min_intensity * max_intensity
        peaks = []
        
        for i in range(1, len(intensity) - 1):
            if (intensity[i] > intensity[i - 1] and
                intensity[i] > intensity[i + 1] and
                intensity[i] > threshold):
                bragg = BraggLaw()
                d = bragg.d_spacing(two_theta[i])
                peaks.append(XRDPeak(two_theta[i], intensity[i], d))
        
        return peaks
    
    def gaussian_fit(self, x: List[float],
                    y: List[float],
                    center_guess: float) -> Dict:
        """
        Simple Gaussian peak fit.
        
        Args:
            x: x values
            y: y values
            center_guess: Peak center guess
        
        Returns:
            Fit parameters
        """
        # Find closest point to center
        center_idx = min(range(len(x)), key=lambda i: abs(x[i] - center_guess))
        amplitude = y[center_idx]
        
        # Estimate FWHM
        half_max = amplitude / 2.0
        left = center_idx
        right = center_idx
        
        while left > 0 and y[left] > half_max:
            left -= 1
        while right < len(y) - 1 and y[right] > half_max:
            right += 1
        
        fwhm = x[right] - x[left] if right > left else 0.1
        sigma = fwhm / (2.0 * math.sqrt(2.0 * math.log(2.0)))
        
        return {
            "amplitude": amplitude,
            "center": x[center_idx],
            "sigma": sigma,
            "fwhm": fwhm
        }


class PhaseIdentifier:
    """
    Phase identification from XRD patterns.
    """
    
    def __init__(self):
        self.reference_patterns: Dict[str, List[Tuple[float, float]]] = {}
    
    def add_reference(self, phase_name: str,
                     peaks: List[Tuple[float, float]]):
        """
        Add reference pattern.
        
        Args:
            phase_name: Phase name
            peaks: List of (d-spacing, relative_intensity)
        """
        self.reference_patterns[phase_name] = peaks
    
    def identify(self, observed_peaks: List[XRDPeak],
                tolerance_A: float = 0.05) -> List[Dict]:
        """
        Identify phases from observed peaks.
        
        Args:
            observed_peaks: Observed peaks
            tolerance_A: d-spacing tolerance
        
        Returns:
            Matched phases
        """
        results = []
        
        for phase_name, ref_peaks in self.reference_patterns.items():
            matches = 0
            for obs in observed_peaks:
                for ref_d, ref_int in ref_peaks:
                    if abs(obs.d_spacing - ref_d) < tolerance_A:
                        matches += 1
                        break
            
            if matches > 0:
                score = matches / max(len(ref_peaks), len(observed_peaks))
                results.append({
                    "phase": phase_name,
                    "matches": matches,
                    "score": score
                })
        
        results.sort(key=lambda r: r["score"], reverse=True)
        return results


class XRDAnalysis:
    """
    Unified XRD analysis controller.
    """
    
    def __init__(self):
        self.bragg = BraggLaw()
        self.detector = PeakDetector()
        self.phase_id = PhaseIdentifier()
    
    def xrd_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["bragg_law", "peak_detection", "gaussian_fit", "phase_id"],
            "wavelength_A": self.bragg.wavelength
        }
