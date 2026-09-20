"""
Chromatography Module
Gas chromatography, liquid chromatography, peak detection,
retention time analysis, and compound identification for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ChromatogramPoint:
    """Chromatogram data point."""
    time_min: float
    signal: float


class PeakDetector:
    """
    Detect peaks in chromatograms.
    """
    
    def __init__(self, threshold: float = 0.1,
                 min_width_points: int = 3):
        """
        Args:
            threshold: Detection threshold
            min_width_points: Minimum peak width
        """
        self.threshold = threshold
        self.min_width = min_width_points
    
    def detect_peaks(self, chromatogram: List[ChromatogramPoint]) -> List[Dict]:
        """
        Detect peaks.
        
        Args:
            chromatogram: Data points
        
        Returns:
            List of peak dicts
        """
        peaks = []
        in_peak = False
        peak_start = 0
        
        for i in range(len(chromatogram)):
            if chromatogram[i].signal > self.threshold:
                if not in_peak:
                    in_peak = True
                    peak_start = i
            else:
                if in_peak:
                    in_peak = False
                    peak_end = i
                    if peak_end - peak_start >= self.min_width:
                        peak_data = chromatogram[peak_start:peak_end]
                        max_point = max(peak_data, key=lambda p: p.signal)
                        peaks.append({
                            "start_idx": peak_start,
                            "end_idx": peak_end - 1,
                            "retention_time_min": max_point.time_min,
                            "height": max_point.signal,
                            "area": sum(p.signal for p in peak_data)
                        })
        
        # Handle peak at end
        if in_peak:
            peak_end = len(chromatogram)
            if peak_end - peak_start >= self.min_width:
                peak_data = chromatogram[peak_start:peak_end]
                max_point = max(peak_data, key=lambda p: p.signal)
                peaks.append({
                    "start_idx": peak_start,
                    "end_idx": peak_end - 1,
                    "retention_time_min": max_point.time_min,
                    "height": max_point.signal,
                    "area": sum(p.signal for p in peak_data)
                })
        
        return peaks


class RetentionTimeAnalyzer:
    """
    Analyze retention times.
    """
    
    def __init__(self):
        self.reference_peaks: Dict[str, float] = {}
    
    def add_reference(self, compound: str,
                     retention_time_min: float):
        """
        Add reference peak.
        
        Args:
            compound: Compound name
            retention_time_min: Retention time
        """
        self.reference_peaks[compound] = retention_time_min
    
    def identify(self, retention_time_min: float,
                tolerance_min: float = 0.5) -> Optional[str]:
        """
        Identify compound by retention time.
        
        Args:
            retention_time_min: Measured RT
            tolerance_min: Tolerance
        
        Returns:
            Compound name or None
        """
        for compound, ref_rt in self.reference_peaks.items():
            if abs(ref_rt - retention_time_min) <= tolerance_min:
                return compound
        return None
    
    def resolution(self, rt1_min: float, rt2_min: float,
                  w1_min: float, w2_min: float) -> float:
        """
        Compute resolution between two peaks.
        
        Args:
            rt1_min: RT of peak 1
            rt2_min: RT of peak 2
            w1_min: Width of peak 1
            w2_min: Width of peak 2
        
        Returns:
            Resolution
        """
        avg_width = (w1_min + w2_min) / 2.0
        if avg_width <= 0:
            return 0.0
        return abs(rt2_min - rt1_min) / avg_width


class GasChromatography:
    """
    Gas chromatography analysis.
    """
    
    def __init__(self, column_length_m: float = 30.0,
                 carrier_gas: str = "helium"):
        """
        Args:
            column_length_m: Column length
            carrier_gas: Carrier gas
        """
        self.column_length = column_length_m
        self.carrier_gas = carrier_gas
    
    def retention_factor(self, retention_time_min: float,
                        dead_time_min: float) -> float:
        """
        Compute retention factor.
        
        Args:
            retention_time_min: Retention time
            dead_time_min: Dead time
        
        Returns:
            k
        """
        if dead_time_min <= 0:
            return 0.0
        return (retention_time_min - dead_time_min) / dead_time_min
    
    def selectivity_factor(self, rt1_min: float,
                          rt2_min: float,
                          dead_time_min: float) -> float:
        """
        Compute selectivity factor.
        
        Args:
            rt1_min: RT of compound 1
            rt2_min: RT of compound 2
            dead_time_min: Dead time
        
        Returns:
            Alpha
        """
        k1 = self.retention_factor(rt1_min, dead_time_min)
        k2 = self.retention_factor(rt2_min, dead_time_min)
        if k1 <= 0:
            return 0.0
        return k2 / k1
    
    def theoretical_plates(self, retention_time_min: float,
                          peak_width_min: float) -> float:
        """
        Compute theoretical plates.
        
        Args:
            retention_time_min: RT
            peak_width_min: Peak width
        
        Returns:
            N
        """
        if peak_width_min <= 0:
            return 0.0
        return 16.0 * (retention_time_min / peak_width_min) ** 2
    
    def plate_height(self, retention_time_min: float,
                    peak_width_min: float) -> float:
        """
        Compute plate height.
        
        Args:
            retention_time_min: RT
            peak_width_min: Peak width
        
        Returns:
            H in mm
        """
        N = self.theoretical_plates(retention_time_min, peak_width_min)
        if N <= 0:
            return 0.0
        return self.column_length * 1000.0 / N


class LiquidChromatography:
    """
    Liquid chromatography analysis.
    """
    
    def __init__(self, flow_rate_ml_min: float = 1.0):
        """
        Args:
            flow_rate_ml_min: Flow rate
        """
        self.flow_rate = flow_rate_ml_min
    
    def void_volume(self, column_volume_ml: float) -> float:
        """
        Compute void volume.
        
        Args:
            column_volume_ml: Column volume
        
        Returns:
            Void volume in ml
        """
        return column_volume_ml * 0.6  # Typical porosity
    
    def dead_time(self, column_volume_ml: float) -> float:
        """
        Compute dead time.
        
        Args:
            column_volume_ml: Column volume
        
        Returns:
            Dead time in min
        """
        if self.flow_rate <= 0:
            return 0.0
        return self.void_volume(column_volume_ml) / self.flow_rate


class Chromatography:
    """
    Unified chromatography controller.
    """
    
    def __init__(self):
        self.peak_detector = PeakDetector()
        self.rt_analyzer = RetentionTimeAnalyzer()
        self.gc = GasChromatography()
        self.lc = LiquidChromatography()
        self.chromatogram: List[ChromatogramPoint] = []
    
    def load_data(self, chromatogram: List[ChromatogramPoint]):
        """
        Load chromatogram.
        
        Args:
            chromatogram: Data
        """
        self.chromatogram = chromatogram
    
    def analyze(self) -> Dict:
        """
        Analyze chromatogram.
        
        Returns:
            Results
        """
        if not self.chromatogram:
            return {}
        
        peaks = self.peak_detector.detect_peaks(self.chromatogram)
        
        identified = []
        for peak in peaks:
            compound = self.rt_analyzer.identify(peak["retention_time_min"])
            identified.append({
                "compound": compound,
                "retention_time_min": peak["retention_time_min"],
                "height": peak["height"],
                "area": peak["area"]
            })
        
        return {
            "peaks": len(peaks),
            "identified": identified,
            "total_area": sum(p["area"] for p in peaks)
        }
    
    def chrom_summary(self) -> Dict:
        """Get summary."""
        return {
            "points": len(self.chromatogram),
            "methods": ["GC", "LC"],
            "references": len(self.rt_analyzer.reference_peaks)
        }
