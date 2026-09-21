"""
NMR Spectroscopy Module
Chemical shift, coupling constants, spin systems,
2D NMR, and spectral processing for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class NMRPeak:
    """NMR peak."""
    chemical_shift_ppm: float
    intensity: float
    multiplicity: str = "s"
    j_coupling_hz: float = 0.0


class ChemicalShiftCalculator:
    """
    Calculate chemical shifts.
    """
    
    def __init__(self, reference_ppm: float = 0.0):
        """
        Args:
            reference_ppm: Reference chemical shift
        """
        self.reference = reference_ppm
    
    def frequency(self, chemical_shift_ppm: float,
                 larmor_freq_mhz: float) -> float:
        """
        Convert ppm to frequency.
        
        Args:
            chemical_shift_ppm: Chemical shift
            larmor_freq_mhz: Larmor frequency
        
        Returns:
            Frequency in Hz
        """
        return chemical_shift_ppm * larmor_freq_mhz
    
    def ppm(self, frequency_hz: float,
           larmor_freq_mhz: float) -> float:
        """
        Convert frequency to ppm.
        
        Args:
            frequency_hz: Frequency
            larmor_freq_mhz: Larmor frequency
        
        Returns:
            Chemical shift in ppm
        """
        if larmor_freq_mhz <= 0:
            return 0.0
        return frequency_hz / larmor_freq_mhz


class SpinSystem:
    """
    NMR spin system.
    """
    
    def __init__(self):
        self.spins: List[Dict] = []
    
    def add_spin(self, nucleus: str,
                chemical_shift_ppm: float,
                coupling_hz: float = 0.0):
        """
        Add spin.
        
        Args:
            nucleus: Nucleus type
            chemical_shift_ppm: Chemical shift
            coupling_hz: J-coupling
        """
        self.spins.append({
            "nucleus": nucleus,
            "shift_ppm": chemical_shift_ppm,
            "j_hz": coupling_hz
        })
    
    def first_order_splitting(self, chemical_shift_ppm: float,
                             j_coupling_hz: float,
                             larmor_freq_mhz: float,
                             num_neighbors: int = 1) -> List[float]:
        """
        Compute first-order multiplet.
        
        Args:
            chemical_shift_ppm: Chemical shift
            j_coupling_hz: J-coupling
            larmor_freq_mhz: Larmor frequency
            num_neighbors: Number of equivalent neighbors
        
        Returns:
            Peak positions in ppm
        """
        if num_neighbors == 0:
            return [chemical_shift_ppm]
        
        # N+1 rule: splitting into N+1 lines
        j_ppm = j_coupling_hz / larmor_freq_mhz
        n = num_neighbors
        positions = []
        
        for k in range(n + 1):
            delta = j_ppm * (k - n / 2.0)
            positions.append(chemical_shift_ppm + delta)
        
        return positions
    
    def multiplicity(self, num_neighbors: int) -> str:
        """
        Determine multiplicity.
        
        Args:
            num_neighbors: Number of neighbors
        
        Returns:
            Multiplicity string
        """
        multiplicities = {
            0: "s", 1: "d", 2: "t", 3: "q",
            4: "quintet", 5: "sextet", 6: "septet"
        }
        return multiplicities.get(num_neighbors, "m")


class SpectralProcessor:
    """
    Process NMR spectra.
    """
    
    def __init__(self):
        pass
    
    def baseline_correction(self, spectrum: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Simple baseline correction.
        
        Args:
            spectrum: (ppm, intensity) pairs
        
        Returns:
            Corrected spectrum
        """
        if not spectrum:
            return []
        
        baseline = min(i for _, i in spectrum)
        return [(ppm, intensity - baseline) for ppm, intensity in spectrum]
    
    def integrate(self, spectrum: List[Tuple[float, float]],
                 start_ppm: float,
                 end_ppm: float) -> float:
        """
        Integrate spectral region.
        
        Args:
            spectrum: Spectrum
            start_ppm: Start ppm
            end_ppm: End ppm
        
        Returns:
            Integral
        """
        integral = 0.0
        for i in range(len(spectrum) - 1):
            ppm1, int1 = spectrum[i]
            ppm2, int2 = spectrum[i + 1]
            
            if start_ppm <= ppm1 <= end_ppm and start_ppm <= ppm2 <= end_ppm:
                dx = abs(ppm2 - ppm1)
                integral += (int1 + int2) / 2.0 * dx
        
        return integral
    
    def signal_to_noise(self, spectrum: List[Tuple[float, float]],
                       peak_region: Tuple[float, float]) -> float:
        """
        Compute signal-to-noise ratio.
        
        Args:
            spectrum: Spectrum
            peak_region: Peak region
        
        Returns:
            SNR
        """
        peak_intensities = [i for p, i in spectrum
                           if peak_region[0] <= p <= peak_region[1]]
        noise_intensities = [i for p, i in spectrum
                            if not (peak_region[0] <= p <= peak_region[1])]
        
        if not peak_intensities or not noise_intensities:
            return 0.0
        
        signal = max(peak_intensities)
        noise = sum(abs(i) for i in noise_intensities) / len(noise_intensities)
        
        if noise <= 0:
            return 0.0
        return signal / noise


class TwoDNMR:
    """
    2D NMR processing.
    """
    
    def __init__(self):
        pass
    
    def correlation_peak(self, f1_ppm: float,
                        f2_ppm: float,
                        intensity: float) -> Dict:
        """
        Create correlation peak.
        
        Args:
            f1_ppm: F1 dimension
            f2_ppm: F2 dimension
            intensity: Intensity
        
        Returns:
            Peak dict
        """
        return {
            "f1_ppm": f1_ppm,
            "f2_ppm": f2_ppm,
            "intensity": intensity
        }
    
    def cross_peak(self, peak_a: NMRPeak,
                  peak_b: NMRPeak) -> bool:
        """
        Check if peaks are correlated.
        
        Args:
            peak_a: Peak A
            peak_b: Peak B
        
        Returns:
            True if correlated
        """
        # Simplified: peaks within coupling distance
        return abs(peak_a.chemical_shift_ppm - peak_b.chemical_shift_ppm) < 0.5


class NMRSpectroscopy:
    """
    Unified NMR spectroscopy controller.
    """
    
    def __init__(self, larmor_freq_mhz: float = 400.0):
        """
        Args:
            larmor_freq_mhz: Larmor frequency
        """
        self.larmor = larmor_freq_mhz
        self.shift_calc = ChemicalShiftCalculator()
        self.spin_system = SpinSystem()
        self.processor = SpectralProcessor()
        self.td_nmr = TwoDNMR()
        self.spectrum: List[NMRPeak] = []
    
    def add_peak(self, peak: NMRPeak):
        """
        Add peak.
        
        Args:
            peak: NMR peak
        """
        self.spectrum.append(peak)
    
    def analyze(self) -> Dict:
        """
        Analyze spectrum.
        
        Returns:
            Results
        """
        peaks_info = []
        for peak in self.spectrum:
            freq_hz = self.shift_calc.frequency(
                peak.chemical_shift_ppm, self.larmor)
            peaks_info.append({
                "ppm": peak.chemical_shift_ppm,
                "hz": freq_hz,
                "multiplicity": peak.multiplicity,
                "j_hz": peak.j_coupling_hz
            })
        
        return {
            "peaks": len(self.spectrum),
            "larmor_mhz": self.larmor,
            "details": peaks_info
        }
    
    def nmr_summary(self) -> Dict:
        """Get summary."""
        return {
            "larmor_mhz": self.larmor,
            "peaks": len(self.spectrum),
            "methods": ["1H NMR", "COSY", "HSQC"]
        }
