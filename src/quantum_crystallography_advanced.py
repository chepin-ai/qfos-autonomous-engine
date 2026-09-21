"""
Quantum Crystallography Advanced Module
Quantum diffraction, structure factor,
phase retrieval, and electron density mapping for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MillerIndices:
    """Miller indices."""
    h: int
    k: int
    l: int


class QuantumDiffraction:
    """
    Quantum diffraction pattern analysis.
    """
    
    def __init__(self, wavelength_A: float = 1.54):
        """
        Args:
            wavelength_A: X-ray wavelength
        """
        self.wavelength = wavelength_A
    
    def bragg_angle(self, d_spacing_A: float) -> float:
        """
        Compute Bragg angle (2theta) from d-spacing.
        
        Args:
            d_spacing_A: d-spacing
        
        Returns:
            2theta (degrees)
        """
        if d_spacing_A <= 0:
            return 0.0
        ratio = self.wavelength / (2.0 * d_spacing_A)
        if ratio > 1.0:
            ratio = 1.0
        theta = math.asin(ratio)
        return 2.0 * math.degrees(theta)
    
    def d_spacing(self, miller: MillerIndices,
                 a_A: float, b_A: float = None, c_A: float = None,
                 alpha_deg: float = 90.0, beta_deg: float = 90.0,
                 gamma_deg: float = 90.0) -> float:
        """
        Compute d-spacing for given Miller indices (cubic system).
        
        Args:
            miller: Miller indices
            a_A: Lattice parameter
            b_A, c_A: Lattice parameters
            alpha_deg, beta_deg, gamma_deg: Angles
        
        Returns:
            d-spacing (A)
        """
        if a_A <= 0:
            return 0.0
        # Cubic simplification
        h2k2l2 = miller.h**2 + miller.k**2 + miller.l**2
        return a_A / math.sqrt(h2k2l2) if h2k2l2 > 0 else float('inf')


class StructureFactor:
    """
    Structure factor calculation.
    """
    
    def __init__(self):
        pass
    
    def atomic_scattering_factor(self, sin_theta_over_lambda: float,
                                 atomic_number: int = 26) -> float:
        """
        Compute atomic scattering factor (simplified).
        
        Args:
            sin_theta_over_lambda: sin(theta)/lambda
            atomic_number: Atomic number
        
        Returns:
            Scattering factor
        """
        # Simplified: f = Z * exp(-B * s^2)
        b_factor = 1.0
        return atomic_number * math.exp(-b_factor * sin_theta_over_lambda**2)
    
    def structure_factor_amplitude(self, atoms: List[Tuple[float, float, float, float]],
                                   miller: MillerIndices) -> float:
        """
        Compute structure factor amplitude (simplified).
        
        Args:
            atoms: List of (x, y, z, Z) fractional coordinates
            miller: Miller indices
        
        Returns:
            |F(hkl)|
        """
        real = 0.0
        imag = 0.0
        for atom in atoms:
            x, y, z, z_eff = atom
            phase = 2.0 * math.pi * (miller.h * x + miller.k * y + miller.l * z)
            real += z_eff * math.cos(phase)
            imag += z_eff * math.sin(phase)
        return math.sqrt(real**2 + imag**2)


class PhaseRetrieval:
    """
    Phase retrieval algorithms.
    """
    
    def __init__(self):
        pass
    
    def error_reduction(self, measured_amplitudes: List[float],
                       current_phases: List[float],
                       support_mask: List[bool]) -> Tuple[List[float], List[float]]:
        """
        One iteration of error reduction algorithm.
        
        Args:
            measured_amplitudes: Measured |F|
            current_phases: Current phases
            support_mask: Support constraint
        
        Returns:
            Updated amplitudes and phases
        """
        new_amps = []
        new_phases = []
        for i, (amp, phase) in enumerate(zip(measured_amplitudes, current_phases)):
            if support_mask[i] if i < len(support_mask) else True:
                new_amps.append(amp)
                new_phases.append(phase)
            else:
                new_amps.append(0.0)
                new_phases.append(0.0)
        return new_amps, new_phases
    
    def phase_error(self, true_phases: List[float],
                   estimated_phases: List[float]) -> float:
        """
        Compute RMS phase error.
        
        Args:
            true_phases: True phases
            estimated_phases: Estimated phases
        
        Returns:
            RMS error (degrees)
        """
        if not true_phases or len(true_phases) != len(estimated_phases):
            return 0.0
        diffs = []
        for tp, ep in zip(true_phases, estimated_phases):
            diff = abs(tp - ep)
            while diff > 180.0:
                diff -= 360.0
            diffs.append(diff**2)
        return math.sqrt(sum(diffs) / len(diffs))


class ElectronDensityMap:
    """
    Electron density mapping.
    """
    
    def __init__(self):
        pass
    
    def electron_density(self, structure_factors: List[complex],
                        miller_indices: List[MillerIndices],
                        x_frac: float, y_frac: float, z_frac: float) -> float:
        """
        Compute electron density at position (Fourier synthesis).
        
        Args:
            structure_factors: F(hkl) values
            miller_indices: Corresponding indices
            x_frac, y_frac, z_frac: Fractional coordinates
        
        Returns:
            Electron density
        """
        rho = 0.0
        for f, hkl in zip(structure_factors, miller_indices):
            phase = 2.0 * math.pi * (hkl.h * x_frac + hkl.k * y_frac + hkl.l * z_frac)
            rho += (f.real * math.cos(phase) - f.imag * math.sin(phase))
        return rho / len(structure_factors) if structure_factors else 0.0
    
    def peak_height(self, electron_density_values: List[float]) -> float:
        """
        Find maximum electron density.
        
        Args:
            electron_density_values: Density values
        
        Returns:
            Peak height
        """
        if not electron_density_values:
            return 0.0
        return max(electron_density_values)


class QuantumCrystallographyAdvanced:
    """
    Unified quantum crystallography controller.
    """
    
    def __init__(self):
        self.diffraction = QuantumDiffraction()
        self.structure = StructureFactor()
        self.phase = PhaseRetrieval()
        self.density = ElectronDensityMap()
    
    def crystallography_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["diffraction", "structure_factor", "phase_retrieval", "density_map"],
            "applications": ["structure_determination", "phase_problem"]
        }
