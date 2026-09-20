"""
Acoustic Holography Module
Near-field acoustic holography, spatial Fourier transform,
back-propagation, and sound field reconstruction for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class HologramPlane:
    """Hologram measurement plane."""
    width_m: float
    height_m: float
    resolution_x: int
    resolution_y: int
    z_m: float
    pressure: List[List[complex]]


class SpatialFourierTransform:
    """
    2D spatial Fourier transform.
    """
    
    def __init__(self):
        pass
    
    def dft_1d(self, signal: List[complex]) -> List[complex]:
        """
        1D DFT.
        
        Args:
            signal: Signal
        
        Returns:
            DFT
        """
        N = len(signal)
        result = []
        for k in range(N):
            s = complex(0, 0)
            for n in range(N):
                angle = -2.0 * math.pi * k * n / N
                s += signal[n] * complex(math.cos(angle), math.sin(angle))
            result.append(s)
        return result
    
    def idft_1d(self, spectrum: List[complex]) -> List[complex]:
        """
        1D IDFT.
        
        Args:
            spectrum: Spectrum
        
        Returns:
            Signal
        """
        N = len(spectrum)
        result = []
        for n in range(N):
            s = complex(0, 0)
            for k in range(N):
                angle = 2.0 * math.pi * k * n / N
                s += spectrum[k] * complex(math.cos(angle), math.sin(angle))
            result.append(s / N)
        return result
    
    def dft_2d(self, matrix: List[List[complex]]) -> List[List[complex]]:
        """
        2D DFT (row then column).
        
        Args:
            matrix: Input
        
        Returns:
            2D DFT
        """
        # Row DFT
        row_dft = [self.dft_1d(row) for row in matrix]
        
        # Column DFT
        h = len(row_dft)
        w = len(row_dft[0]) if h > 0 else 0
        
        result = [[complex(0, 0) for _ in range(w)] for _ in range(h)]
        for x in range(w):
            col = [row_dft[y][x] for y in range(h)]
            col_dft = self.dft_1d(col)
            for y in range(h):
                result[y][x] = col_dft[y]
        
        return result
    
    def idft_2d(self, spectrum: List[List[complex]]) -> List[List[complex]]:
        """
        2D IDFT.
        
        Args:
            spectrum: Spectrum
        
        Returns:
            2D IDFT
        """
        # Column IDFT
        h = len(spectrum)
        w = len(spectrum[0]) if h > 0 else 0
        
        col_idft = []
        for x in range(w):
            col = [spectrum[y][x] for y in range(h)]
            col_idft.append(self.idft_1d(col))
        
        # Row IDFT
        result = []
        for y in range(h):
            row = [col_idft[x][y] for x in range(w)]
            result.append(self.idft_1d(row))
        
        return result


class BackPropagator:
    """
    Back-propagation for NAH.
    """
    
    def __init__(self, freq_Hz: float = 1000.0,
                 c_m_s: float = 343.0):
        """
        Args:
            freq_Hz: Frequency
            c_m_s: Speed of sound
        """
        self.freq = freq_Hz
        self.c = c_m_s
        self.k = 2.0 * math.pi * freq_Hz / c_m_s
    
    def wavenumber_components(self, nx: int, ny: int,
                             dx: float, dy: float) -> Tuple[List[float], List[float]]:
        """
        Compute wavenumber components.
        
        Args:
            nx: X resolution
            ny: Y resolution
            dx: X spacing
            dy: Y spacing
        
        Returns:
            (kx, ky)
        """
        kx = []
        for i in range(nx):
            if i <= nx // 2:
                kx.append(2.0 * math.pi * i / (nx * dx))
            else:
                kx.append(2.0 * math.pi * (i - nx) / (nx * dx))
        
        ky = []
        for j in range(ny):
            if j <= ny // 2:
                ky.append(2.0 * math.pi * j / (ny * dy))
            else:
                ky.append(2.0 * math.pi * (j - ny) / (ny * dy))
        
        return kx, ky
    
    def propagate(self, spectrum: List[List[complex]],
                 z: float, dx: float, dy: float) -> List[List[complex]]:
        """
        Back-propagate spectrum.
        
        Args:
            spectrum: Spatial spectrum
            z: Propagation distance
            dx: X spacing
            dy: Y spacing
        
        Returns:
            Propagated spectrum
        """
        h = len(spectrum)
        w = len(spectrum[0]) if h > 0 else 0
        
        kx, ky = self.wavenumber_components(w, h, dx, dy)
        
        result = [[complex(0, 0) for _ in range(w)] for _ in range(h)]
        for y in range(h):
            for x in range(w):
                kz2 = self.k**2 - kx[x]**2 - ky[y]**2
                if kz2 >= 0:
                    kz = math.sqrt(kz2)
                    phase = kz * z
                    prop = complex(math.cos(phase), math.sin(phase))
                    result[y][x] = spectrum[y][x] * prop
                else:
                    # Evanescent decay
                    alpha = math.sqrt(-kz2)
                    decay = math.exp(-alpha * abs(z))
                    result[y][x] = spectrum[y][x] * decay
        
        return result


class SoundFieldReconstructor:
    """
    Sound field reconstruction from hologram.
    """
    
    def __init__(self, sft: SpatialFourierTransform,
                 propagator: BackPropagator):
        """
        Args:
            sft: Spatial Fourier transform
            propagator: Back-propagator
        """
        self.sft = sft
        self.prop = propagator
    
    def reconstruct(self, plane: HologramPlane,
                   target_z_m: float) -> List[List[complex]]:
        """
        Reconstruct at target z.
        
        Args:
            plane: Hologram plane
            target_z_m: Target z
        
        Returns:
            Reconstructed pressure
        """
        dx = plane.width_m / plane.resolution_x
        dy = plane.height_m / plane.resolution_y
        
        # Forward DFT
        spectrum = self.sft.dft_2d(plane.pressure)
        
        # Back-propagate
        dz = target_z_m - plane.z_m
        propagated = self.prop.propagate(spectrum, dz, dx, dy)
        
        # Inverse DFT
        reconstructed = self.sft.idft_2d(propagated)
        
        return reconstructed
    
    def intensity(self, pressure: List[List[complex]]) -> List[List[float]]:
        """
        Compute acoustic intensity.
        
        Args:
            pressure: Pressure field
        
        Returns:
            Intensity
        """
        return [[abs(p)**2 for p in row] for row in pressure]


class AcousticHolography:
    """
    Unified acoustic holography controller.
    """
    
    def __init__(self, freq_Hz: float = 1000.0):
        """
        Args:
            freq_Hz: Frequency
        """
        self.sft = SpatialFourierTransform()
        self.prop = BackPropagator(freq_Hz)
        self.reconstructor = SoundFieldReconstructor(self.sft, self.prop)
        self.planes: List[HologramPlane] = []
        self.results: List[Dict] = []
    
    def record_hologram(self, pressure: List[List[complex]],
                       width_m: float = 1.0,
                       height_m: float = 1.0,
                       z_m: float = 0.1):
        """
        Record hologram.
        
        Args:
            pressure: Pressure field
            width_m: Width
            height_m: Height
            z_m: Z position
        """
        h = len(pressure)
        w = len(pressure[0]) if h > 0 else 0
        plane = HologramPlane(width_m, height_m, w, h, z_m, pressure)
        self.planes.append(plane)
    
    def reconstruct_at(self, z_m: float) -> List[List[complex]]:
        """
        Reconstruct at z.
        
        Args:
            z_m: Target z
        
        Returns:
            Reconstructed field
        """
        if not self.planes:
            return []
        
        return self.reconstructor.reconstruct(self.planes[-1], z_m)
    
    def holography_summary(self) -> Dict:
        """Get summary."""
        return {
            "planes": len(self.planes),
            "frequency_Hz": self.prop.freq,
            "wavenumber": self.prop.k
        }
