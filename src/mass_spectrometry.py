"""
Mass Spectrometry Module
MS spectrum acquisition, peak identification, isotope pattern,
mass calibration, and fragmentation analysis for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MassPeak:
    """Mass peak."""
    mz: float
    intensity: float


class SpectrumAcquisition:
    """
    Acquire mass spectra.
    """
    
    def __init__(self, resolution: float = 10000.0,
                 mass_range: Tuple[float, float] = (10.0, 2000.0)):
        """
        Args:
            resolution: Mass resolution (m/dm)
            mass_range: (min, max) m/z range
        """
        self.resolution = resolution
        self.mass_range = mass_range
    
    def resolve_peak(self, mz: float) -> float:
        """
        Compute peak width at half maximum.
        
        Args:
            mz: m/z value
        
        Returns:
            FWHM
        """
        return mz / self.resolution
    
    def scan(self, peaks: List[MassPeak]) -> List[MassPeak]:
        """
        Filter peaks within mass range.
        
        Args:
            peaks: Input peaks
        
        Returns:
            Filtered peaks
        """
        return [p for p in peaks
                if self.mass_range[0] <= p.mz <= self.mass_range[1]]


class PeakIdentifier:
    """
    Identify peaks from mass spectra.
    """
    
    def __init__(self, tolerance_ppm: float = 10.0):
        """
        Args:
            tolerance_ppm: Mass tolerance in ppm
        """
        self.tolerance_ppm = tolerance_ppm
    
    def match(self, observed_mz: float,
             theoretical_mz: float) -> bool:
        """
        Check if observed matches theoretical within tolerance.
        
        Args:
            observed_mz: Observed m/z
            theoretical_mz: Theoretical m/z
        
        Returns:
            True if match
        """
        delta_ppm = abs(observed_mz - theoretical_mz) / theoretical_mz * 1e6
        return delta_ppm <= self.tolerance_ppm
    
    def identify(self, observed_mz: float,
                library: Dict[str, float]) -> Optional[str]:
        """
        Identify compound from library.
        
        Args:
            observed_mz: Observed m/z
            library: {name: m/z}
        
        Returns:
            Compound name or None
        """
        for name, mz in library.items():
            if self.match(observed_mz, mz):
                return name
        return None


class IsotopePattern:
    """
    Predict isotope patterns.
    """
    
    def __init__(self):
        self.isotope_abundances = {
            "C": [(12.0, 0.9893), (13.00335, 0.0107)],
            "H": [(1.00783, 0.999885), (2.01410, 0.000115)],
            "N": [(14.00307, 0.99632), (15.00011, 0.00368)],
            "O": [(15.99491, 0.99757), (16.99913, 0.00038), (17.99916, 0.00205)]
        }
    
    def monoisotopic_mass(self, formula: Dict[str, int]) -> float:
        """
        Compute monoisotopic mass.
        
        Args:
            formula: {element: count}
        
        Returns:
            Mass in Da
        """
        mass = 0.0
        for element, count in formula.items():
            if element in self.isotope_abundances:
                mass += self.isotope_abundances[element][0][0] * count
        return mass
    
    def isotope_peaks(self, formula: Dict[str, int],
                     max_peaks: int = 4) -> List[Tuple[float, float]]:
        """
        Compute isotope peaks.
        
        Args:
            formula: Molecular formula
            max_peaks: Maximum peaks
        
        Returns:
            List of (m/z, abundance)
        """
        # Simplified: carbon isotope pattern
        c_count = formula.get("C", 0)
        if c_count == 0:
            return [(self.monoisotopic_mass(formula), 1.0)]
        
        peaks = []
        p_13c = 0.0107
        for k in range(min(max_peaks, c_count + 1)):
            import math
            prob = math.comb(c_count, k) * (p_13c ** k) * ((1 - p_13c) ** (c_count - k))
            mass = self.monoisotopic_mass(formula) + k * 1.00335
            peaks.append((mass, prob))
        
        return peaks


class MassCalibrator:
    """
    Calibrate mass spectra.
    """
    
    def __init__(self):
        self.calibrants: List[Tuple[float, float]] = []
    
    def add_calibrant(self, observed_mz: float,
                     known_mz: float):
        """
        Add calibrant.
        
        Args:
            observed_mz: Observed m/z
            known_mz: Known m/z
        """
        self.calibrants.append((observed_mz, known_mz))
    
    def linear_calibration(self) -> Tuple[float, float]:
        """
        Compute linear calibration.
        
        Returns:
            (slope, intercept)
        """
        if len(self.calibrants) < 2:
            return (1.0, 0.0)
        
        n = len(self.calibrants)
        sum_x = sum(c[0] for c in self.calibrants)
        sum_y = sum(c[1] for c in self.calibrants)
        sum_xy = sum(c[0] * c[1] for c in self.calibrants)
        sum_x2 = sum(c[0] ** 2 for c in self.calibrants)
        
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return (1.0, 0.0)
        
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        
        return (slope, intercept)
    
    def apply(self, mz: float) -> float:
        """
        Apply calibration.
        
        Args:
            mz: Raw m/z
        
        Returns:
            Calibrated m/z
        """
        slope, intercept = self.linear_calibration()
        return slope * mz + intercept


class FragmentationAnalyzer:
    """
    Analyze fragmentation patterns (MS/MS).
    """
    
    def __init__(self):
        self.fragment_library: Dict[str, List[float]] = {}
    
    def add_fragment(self, compound: str,
                    fragments: List[float]):
        """
        Add fragment ions.
        
        Args:
            compound: Compound name
            fragments: Fragment m/z values
        """
        self.fragment_library[compound] = fragments
    
    def score_match(self, observed_fragments: List[float],
                   compound: str,
                   tolerance_ppm: float = 20.0) -> float:
        """
        Score fragment match.
        
        Args:
            observed_fragments: Observed m/z
            compound: Compound name
            tolerance_ppm: Tolerance
        
        Returns:
            Match score
        """
        if compound not in self.fragment_library:
            return 0.0
        
        expected = self.fragment_library[compound]
        matches = 0
        
        for obs in observed_fragments:
            for exp in expected:
                delta_ppm = abs(obs - exp) / exp * 1e6
                if delta_ppm <= tolerance_ppm:
                    matches += 1
                    break
        
        return matches / len(expected) if expected else 0.0


class MassSpectrometry:
    """
    Unified mass spectrometry controller.
    """
    
    def __init__(self):
        self.acquisition = SpectrumAcquisition()
        self.identifier = PeakIdentifier()
        self.isotope = IsotopePattern()
        self.calibrator = MassCalibrator()
        self.fragmentation = FragmentationAnalyzer()
        self.spectrum: List[MassPeak] = []
    
    def load_spectrum(self, peaks: List[MassPeak]):
        """
        Load spectrum.
        
        Args:
            peaks: Mass peaks
        """
        self.spectrum = self.acquisition.scan(peaks)
    
    def analyze(self, library: Dict[str, float]) -> Dict:
        """
        Analyze spectrum.
        
        Args:
            library: Compound library
        
        Returns:
            Results
        """
        identified = []
        for peak in self.spectrum:
            compound = self.identifier.identify(peak.mz, library)
            if compound:
                identified.append({
                    "compound": compound,
                    "mz": peak.mz,
                    "intensity": peak.intensity
                })
        
        return {
            "peaks": len(self.spectrum),
            "identified": identified,
            "base_peak": max(self.spectrum, key=lambda p: p.intensity).mz if self.spectrum else None
        }
    
    def ms_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["MS1", "MS/MS"],
            "peaks": len(self.spectrum),
            "resolution": self.acquisition.resolution
        }
