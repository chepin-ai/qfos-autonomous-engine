"""
Digital Radiography Module
DR image acquisition, flat-field correction, bad pixel detection,
DQE estimation, and exposure index calculation for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DRImage:
    """Digital radiography image."""
    width_px: int
    height_px: int
    pixel_size_mm: float
    exposure_mAs: float
    kVp: float
    data: List[List[float]]


class FlatFieldCorrector:
    """
    Flat-field correction for DR images.
    """
    
    def __init__(self):
        self.flat_field: Optional[List[List[float]]] = None
        self.dark_field: Optional[List[List[float]]] = None
    
    def set_flat_field(self, flat: List[List[float]]):
        """
        Set flat field.
        
        Args:
            flat: Flat field image
        """
        self.flat_field = flat
    
    def set_dark_field(self, dark: List[List[float]]):
        """
        Set dark field.
        
        Args:
            dark: Dark field image
        """
        self.dark_field = dark
    
    def correct(self, image: List[List[float]]) -> List[List[float]]:
        """
        Apply flat-field correction.
        
        Args:
            image: Raw image
        
        Returns:
            Corrected image
        """
        if self.flat_field is None or self.dark_field is None:
            return image
        
        corrected = []
        for y in range(len(image)):
            row = []
            for x in range(len(image[y])):
                raw = image[y][x] - self.dark_field[y][x]
                flat = self.flat_field[y][x] - self.dark_field[y][x]
                if flat > 1e-10:
                    row.append(raw / flat)
                else:
                    row.append(0.0)
            corrected.append(row)
        
        return corrected


class BadPixelDetector:
    """
    Detect bad pixels in DR images.
    """
    
    def __init__(self):
        self.threshold_sigma = 5.0
    
    def find_bad_pixels(self, image: List[List[float]]) -> List[Tuple[int, int]]:
        """
        Find bad pixels.
        
        Args:
            image: Image
        
        Returns:
            Bad pixel coordinates
        """
        flat = [v for row in image for v in row]
        if not flat:
            return []
        
        mean = sum(flat) / len(flat)
        std = (sum((v - mean)**2 for v in flat) / len(flat)) ** 0.5
        
        bad = []
        for y in range(len(image)):
            for x in range(len(image[y])):
                if std > 0 and abs(image[y][x] - mean) > self.threshold_sigma * std:
                    bad.append((x, y))
        
        return bad
    
    def interpolate_bad_pixels(self, image: List[List[float]],
                              bad_pixels: List[Tuple[int, int]]) -> List[List[float]]:
        """
        Interpolate bad pixels.
        
        Args:
            image: Image
            bad_pixels: Bad pixels
        
        Returns:
            Corrected image
        """
        corrected = [row[:] for row in image]
        h = len(image)
        w = len(image[0]) if h > 0 else 0
        
        for bx, by in bad_pixels:
            neighbors = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = bx + dx, by + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) != (bx, by):
                        neighbors.append(image[ny][nx])
            
            if neighbors:
                corrected[by][bx] = sum(neighbors) / len(neighbors)
        
        return corrected


class DQEAnalyzer:
    """
    Detective Quantum Efficiency analysis.
    """
    
    def __init__(self):
        pass
    
    def snr(self, signal: List[float], background: List[float]) -> float:
        """
        Compute signal-to-noise ratio.
        
        Args:
            signal: Signal ROI
            background: Background ROI
        
        Returns:
            SNR
        """
        mean_signal = sum(signal) / len(signal) if signal else 0.0
        mean_bg = sum(background) / len(background) if background else 0.0
        
        noise = (sum((v - mean_bg)**2 for v in background) / len(background)) ** 0.5
        if noise <= 0:
            return float('inf')
        
        return (mean_signal - mean_bg) / noise
    
    def dqe(self, snr_out: float, snr_in: float) -> float:
        """
        Compute DQE.
        
        Args:
            snr_out: Output SNR
            snr_in: Input SNR
        
        Returns:
            DQE
        """
        if snr_in <= 0:
            return 0.0
        return (snr_out / snr_in) ** 2
    
    def estimate_from_rois(self, image: List[List[float]],
                          signal_roi: Tuple[int, int, int, int],
                          bg_roi: Tuple[int, int, int, int]) -> Dict:
        """
        Estimate DQE from ROIs.
        
        Args:
            image: Image
            signal_roi: (x, y, w, h)
            bg_roi: (x, y, w, h)
        
        Returns:
            Metrics
        """
        sx, sy, sw, sh = signal_roi
        bx, by, bw, bh = bg_roi
        
        signal = []
        for y in range(sy, min(sy + sh, len(image))):
            for x in range(sx, min(sx + sw, len(image[y]))):
                signal.append(image[y][x])
        
        background = []
        for y in range(by, min(by + bh, len(image))):
            for x in range(bx, min(bx + bw, len(image[y]))):
                background.append(image[y][x])
        
        snr_value = self.snr(signal, background)
        
        # Assume ideal SNR_in = sqrt(N_photons) ~ sqrt(mean_signal)
        mean_signal = sum(signal) / len(signal) if signal else 1.0
        snr_in = math.sqrt(mean_signal)
        
        dqe = self.dqe(snr_value, snr_in)
        
        return {
            "snr": snr_value,
            "snr_in": snr_in,
            "dqe": dqe
        }


class ExposureIndexCalculator:
    """
    Exposure index calculation.
    """
    
    def __init__(self):
        self.target = 100.0
    
    def ei(self, mean_pixel_value: float,
          exposure_mAs: float) -> float:
        """
        Compute exposure index.
        
        Args:
            mean_pixel_value: Mean value
            exposure_mAs: Exposure
        
        Returns:
            EI
        """
        if exposure_mAs <= 0:
            return 0.0
        return mean_pixel_value / exposure_mAs * 100.0
    
    def deviation(self, ei: float) -> float:
        """
        Compute deviation from target.
        
        Args:
            ei: Exposure index
        
        Returns:
            Deviation
        """
        return ei - self.target


class DigitalRadiography:
    """
    Unified digital radiography controller.
    """
    
    def __init__(self):
        self.flat_field = FlatFieldCorrector()
        self.bad_pixel = BadPixelDetector()
        self.dqe = DQEAnalyzer()
        self.exposure = ExposureIndexCalculator()
        self.images: List[DRImage] = []
        self.corrected: List[List[float]] = []
    
    def acquire(self, image_data: List[List[float]],
               pixel_size_mm: float = 0.1,
               exposure_mAs: float = 5.0,
               kVp: float = 200.0):
        """
        Acquire image.
        
        Args:
            image_data: Raw data
            pixel_size_mm: Pixel size
            exposure_mAs: Exposure
            kVp: kVp
        """
        h = len(image_data)
        w = len(image_data[0]) if h > 0 else 0
        img = DRImage(w, h, pixel_size_mm, exposure_mAs, kVp, image_data)
        self.images.append(img)
    
    def process(self) -> List[List[float]]:
        """
        Process latest image.
        
        Returns:
            Corrected image
        """
        if not self.images:
            return []
        
        raw = self.images[-1].data
        corrected = self.flat_field.correct(raw)
        bad = self.bad_pixel.find_bad_pixels(corrected)
        self.corrected = self.bad_pixel.interpolate_bad_pixels(corrected, bad)
        return self.corrected
    
    def analyze_quality(self, signal_roi: Tuple[int, int, int, int],
                       bg_roi: Tuple[int, int, int, int]) -> Dict:
        """
        Analyze image quality.
        
        Args:
            signal_roi: Signal ROI
            bg_roi: Background ROI
        
        Returns:
            Metrics
        """
        if not self.corrected:
            self.process()
        
        dqe_metrics = self.dqe.estimate_from_rois(self.corrected, signal_roi, bg_roi)
        
        flat = [v for row in self.corrected for v in row]
        mean = sum(flat) / len(flat) if flat else 0.0
        
        exposure = self.images[-1].exposure_mAs if self.images else 1.0
        ei = self.exposure.ei(mean, exposure)
        
        return {
            **dqe_metrics,
            "exposure_index": ei,
            "ei_deviation": self.exposure.deviation(ei)
        }
    
    def dr_summary(self) -> Dict:
        """Get summary."""
        return {
            "images": len(self.images),
            "pixel_size_mm": self.images[-1].pixel_size_mm if self.images else 0.0,
            "kVp": self.images[-1].kVp if self.images else 0.0
        }
