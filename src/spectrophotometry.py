"""
Spectrophotometry Module
Absorbance, transmittance, Beer-Lambert law,
calibration curves, and wavelength scanning for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpectrumPoint:
    """Spectrum data point."""
    wavelength_nm: float
    absorbance: float
    transmittance: float


class BeerLambertLaw:
    """
    Beer-Lambert law calculations.
    """
    
    def __init__(self):
        pass
    
    def absorbance(self, epsilon_L_mol_cm: float,
                  concentration_mol_L: float,
                  path_length_cm: float) -> float:
        """
        Compute absorbance.
        
        Args:
            epsilon_L_mol_cm: Molar absorptivity
            concentration_mol_L: Concentration
            path_length_cm: Path length
        
        Returns:
            Absorbance
        """
        return epsilon_L_mol_cm * concentration_mol_L * path_length_cm
    
    def concentration(self, absorbance: float,
                     epsilon_L_mol_cm: float,
                     path_length_cm: float) -> float:
        """
        Compute concentration from absorbance.
        
        Args:
            absorbance: Absorbance
            epsilon_L_mol_cm: Molar absorptivity
            path_length_cm: Path length
        
        Returns:
            Concentration
        """
        if epsilon_L_mol_cm <= 0 or path_length_cm <= 0:
            return 0.0
        return absorbance / (epsilon_L_mol_cm * path_length_cm)
    
    def transmittance(self, absorbance: float) -> float:
        """
        Convert absorbance to transmittance.
        
        Args:
            absorbance: Absorbance
        
        Returns:
            Transmittance
        """
        return 10.0 ** (-absorbance)
    
    def absorbance_from_transmittance(self, transmittance: float) -> float:
        """
        Convert transmittance to absorbance.
        
        Args:
            transmittance: Transmittance
        
        Returns:
            Absorbance
        """
        if transmittance <= 0:
            return float('inf')
        return -math.log10(transmittance)


class CalibrationCurve:
    """
    Calibration curve for concentration determination.
    """
    
    def __init__(self):
        self.standards: List[Tuple[float, float]] = []
    
    def add_standard(self, concentration_mol_L: float,
                    absorbance: float):
        """
        Add calibration standard.
        
        Args:
            concentration_mol_L: Concentration
            absorbance: Absorbance
        """
        self.standards.append((concentration_mol_L, absorbance))
    
    def linear_fit(self) -> Tuple[float, float]:
        """
        Compute linear calibration (slope, intercept).
        
        Returns:
            (slope, intercept)
        """
        if len(self.standards) < 2:
            return (0.0, 0.0)
        
        n = len(self.standards)
        sum_x = sum(s[0] for s in self.standards)
        sum_y = sum(s[1] for s in self.standards)
        sum_xy = sum(s[0] * s[1] for s in self.standards)
        sum_x2 = sum(s[0] ** 2 for s in self.standards)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return (0.0, 0.0)
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        
        return (slope, intercept)
    
    def r_squared(self) -> float:
        """
        Compute R-squared.
        
        Returns:
            R-squared
        """
        if len(self.standards) < 2:
            return 0.0
        
        slope, intercept = self.linear_fit()
        y_mean = sum(s[1] for s in self.standards) / len(self.standards)
        
        ss_tot = sum((s[1] - y_mean) ** 2 for s in self.standards)
        ss_res = sum((s[1] - (slope * s[0] + intercept)) ** 2 for s in self.standards)
        
        if ss_tot == 0:
            return 1.0
        return 1.0 - ss_res / ss_tot
    
    def predict_concentration(self, absorbance: float) -> float:
        """
        Predict concentration from absorbance.
        
        Args:
            absorbance: Absorbance
        
        Returns:
            Concentration
        """
        slope, intercept = self.linear_fit()
        if slope == 0:
            return 0.0
        return (absorbance - intercept) / slope


class WavelengthAnalyzer:
    """
    Analyze wavelength-dependent spectra.
    """
    
    def __init__(self):
        pass
    
    def lambda_max(self, spectrum: List[SpectrumPoint]) -> Optional[float]:
        """
        Find wavelength of maximum absorbance.
        
        Args:
            spectrum: Spectrum
        
        Returns:
            Wavelength or None
        """
        if not spectrum:
            return None
        max_point = max(spectrum, key=lambda p: p.absorbance)
        return max_point.wavelength_nm
    
    def peak_area(self, spectrum: List[SpectrumPoint],
                 start_nm: float,
                 end_nm: float) -> float:
        """
        Integrate peak area.
        
        Args:
            spectrum: Spectrum
            start_nm: Start wavelength
            end_nm: End wavelength
        
        Returns:
            Area
        """
        area = 0.0
        for i in range(len(spectrum) - 1):
            p1 = spectrum[i]
            p2 = spectrum[i + 1]
            if start_nm <= p1.wavelength_nm <= end_nm and start_nm <= p2.wavelength_nm <= end_nm:
                dx = p2.wavelength_nm - p1.wavelength_nm
                area += (p1.absorbance + p2.absorbance) / 2.0 * dx
        return area
    
    def bandwidth(self, spectrum: List[SpectrumPoint],
                 fraction: float = 0.5) -> float:
        """
        Compute bandwidth at specified fraction of peak height.
        
        Args:
            spectrum: Spectrum
            fraction: Fraction of peak height
        
        Returns:
            Bandwidth in nm
        """
        if not spectrum:
            return 0.0
        
        max_abs = max(p.absorbance for p in spectrum)
        threshold = max_abs * fraction
        
        above_threshold = [p.wavelength_nm for p in spectrum
                          if p.absorbance >= threshold]
        
        if not above_threshold:
            return 0.0
        
        return max(above_threshold) - min(above_threshold)


class Spectrophotometry:
    """
    Unified spectrophotometry controller.
    """
    
    def __init__(self):
        self.beer_lambert = BeerLambertLaw()
        self.calibration = CalibrationCurve()
        self.wavelength = WavelengthAnalyzer()
        self.spectrum: List[SpectrumPoint] = []
    
    def load_spectrum(self, spectrum: List[SpectrumPoint]):
        """
        Load spectrum.
        
        Args:
            spectrum: Spectrum data
        """
        self.spectrum = spectrum
    
    def analyze(self) -> Dict:
        """
        Analyze spectrum.
        
        Returns:
            Results
        """
        if not self.spectrum:
            return {}
        
        return {
            "lambda_max_nm": self.wavelength.lambda_max(self.spectrum),
            "peak_area": self.wavelength.peak_area(self.spectrum, 200.0, 800.0),
            "bandwidth_nm": self.wavelength.bandwidth(self.spectrum, 0.5)
        }
    
    def sp_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["beer_lambert", "calibration", "wavelength_analysis"],
            "points": len(self.spectrum),
            "standards": len(self.calibration.standards)
        }
