"""
Quantum Interferometry Module
Mach-Zehnder, Michelson, Sagnac interferometers,
phase sensitivity, and quantum-enhanced measurement for autonomous quantum sensing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class InterferencePattern:
    """Interference pattern result."""
    intensity: float
    visibility: float
    phase_shift: float


class MachZehnderInterferometer:
    """
    Mach-Zehnder interferometer.
    """
    
    def __init__(self):
        pass
    
    def output_intensity(self, input_intensity: float,
                        phase_difference: float) -> Tuple[float, float]:
        """
        Compute output intensities.
        
        Args:
            input_intensity: Input intensity
            phase_difference: Phase difference
        
        Returns:
            (intensity_port1, intensity_port2)
        """
        I0 = input_intensity
        phi = phase_difference
        I1 = 0.5 * I0 * (1.0 + math.cos(phi))
        I2 = 0.5 * I0 * (1.0 - math.cos(phi))
        return I1, I2
    
    def phase_from_intensities(self, I1: float,
                              I2: float) -> float:
        """
        Estimate phase from output intensities.
        
        Args:
            I1: Port 1 intensity
            I2: Port 2 intensity
        
        Returns:
            Phase difference
        """
        if I1 + I2 == 0:
            return 0.0
        return math.acos(max(-1.0, min(1.0, (I1 - I2) / (I1 + I2))))
    
    def visibility(self, I_max: float,
                  I_min: float) -> float:
        """
        Compute fringe visibility.
        
        Args:
            I_max: Maximum intensity
            I_min: Minimum intensity
        
        Returns:
            Visibility
        """
        if I_max + I_min == 0:
            return 0.0
        return (I_max - I_min) / (I_max + I_min)


class MichelsonInterferometer:
    """
    Michelson interferometer.
    """
    
    def __init__(self, wavelength_nm: float = 633.0):
        """
        Args:
            wavelength_nm: Laser wavelength
        """
        self.wavelength = wavelength_nm * 1e-9
    
    def path_difference(self, mirror_displacement_m: float) -> float:
        """
        Compute optical path difference.
        
        Args:
            mirror_displacement_m: Mirror displacement
        
        Returns:
            Path difference
        """
        return 2.0 * mirror_displacement_m
    
    def fringe_count(self, displacement_m: float) -> float:
        """
        Compute number of fringes for displacement.
        
        Args:
            displacement_m: Displacement
        
        Returns:
            Fringe count
        """
        if self.wavelength == 0:
            return 0.0
        return self.path_difference(displacement_m) / self.wavelength
    
    def displacement_from_fringes(self, fringe_count: float) -> float:
        """
        Compute displacement from fringe count.
        
        Args:
            fringe_count: Number of fringes
        
        Returns:
            Displacement
        """
        return fringe_count * self.wavelength / 2.0


class SagnacInterferometer:
    """
    Sagnac interferometer for rotation sensing.
    """
    
    def __init__(self, area_m2: float = 1.0,
                 wavelength_nm: float = 633.0):
        """
        Args:
            area_m2: Enclosed area
            wavelength_nm: Wavelength
        """
        self.A = area_m2
        self.wavelength = wavelength_nm * 1e-9
        self.c = 299792458.0
    
    def sagnac_phase(self, angular_velocity_rad_s: float) -> float:
        """
        Compute Sagnac phase shift.
        
        Args:
            angular_velocity_rad_s: Angular velocity
        
        Returns:
            Phase shift
        """
        if self.wavelength == 0:
            return 0.0
        return (8.0 * math.pi * self.A * angular_velocity_rad_s) / (self.wavelength * self.c)
    
    def angular_velocity_from_phase(self, phase: float) -> float:
        """
        Compute angular velocity from phase.
        
        Args:
            phase: Phase shift
        
        Returns:
            Angular velocity
        """
        if self.A == 0:
            return 0.0
        return phase * self.wavelength * self.c / (8.0 * math.pi * self.A)


class QuantumEnhancedSensitivity:
    """
    Quantum-enhanced interferometric sensitivity.
    """
    
    def __init__(self):
        pass
    
    def shot_noise_limit(self, N_photons: float) -> float:
        """
        Compute shot noise limit.
        
        Args:
            N_photons: Number of photons
        
        Returns:
            Phase uncertainty
        """
        if N_photons <= 0:
            return float('inf')
        return 1.0 / math.sqrt(N_photons)
    
    def squeezed_state_sensitivity(self, N_photons: float,
                                  squeezing_dB: float = 10.0) -> float:
        """
        Compute squeezed state sensitivity.
        
        Args:
            N_photons: Number of photons
            squeezing_dB: Squeezing in dB
        
        Returns:
            Phase uncertainty
        """
        if N_photons <= 0:
            return float('inf')
        # Simplified: improvement factor from squeezing
        r = squeezing_dB / (20.0 * math.log10(math.e))
        factor = math.exp(-r)
        return factor / math.sqrt(N_photons)
    
    def noo_n_state_sensitivity(self, N_photons: float) -> float:
        """
        Compute N00N state Heisenberg limit.
        
        Args:
            N_photons: Number of photons
        
        Returns:
            Phase uncertainty
        """
        if N_photons <= 0:
            return float('inf')
        return 1.0 / N_photons


class QuantumInterferometry:
    """
    Unified quantum interferometry controller.
    """
    
    def __init__(self):
        self.mach_zehnder = MachZehnderInterferometer()
        self.michelson = MichelsonInterferometer()
        self.sagnac = SagnacInterferometer()
        self.sensitivity = QuantumEnhancedSensitivity()
    
    def interferometry_summary(self) -> Dict:
        """Get summary."""
        return {
            "interferometers": ["Mach-Zehnder", "Michelson", "Sagnac"],
            "sensitivities": ["shot_noise", "squeezed", "Heisenberg"]
        }
