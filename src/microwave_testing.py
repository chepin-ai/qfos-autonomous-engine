"""
Microwave Testing Module
Microwave NDT with reflection/transmission measurements,
dielectric property estimation, and subsurface imaging.
"""

import math
import cmath
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MicrowaveMode(Enum):
    """Microwave measurement modes."""
    REFLECTION = "reflection"
    TRANSMISSION = "transmission"
    SCATTERING = "scattering"


@dataclass
class SParameter:
    """S-parameter measurement."""
    frequency_GHz: float
    s11_magnitude: float
    s11_phase: float
    s21_magnitude: float = 0.0
    s21_phase: float = 0.0


class DielectricEstimator:
    """
    Estimate dielectric properties from S-parameters.
    """
    
    def __init__(self, thickness_mm: float = 10.0):
        """
        Args:
            thickness_mm: Sample thickness
        """
        self.thickness = thickness_mm * 1e-3  # meters
    
    def permittivity_from_reflection(self, s11_mag: float,
                                    s11_phase: float,
                                    frequency_GHz: float) -> complex:
        """
        Estimate relative permittivity from reflection.
        
        Args:
            s11_mag: S11 magnitude
            s11_phase: S11 phase
            frequency_GHz: Frequency
        
        Returns:
            Complex permittivity
        """
        # Simplified: use reflection coefficient
        gamma = s11_mag * cmath.exp(1j * s11_phase)
        # For normal incidence: gamma = (sqrt(eps) - 1) / (sqrt(eps) + 1)
        # eps = ((1 + gamma) / (1 - gamma))^2
        if abs(1.0 - gamma) < 1e-10:
            return complex(1.0, 0.0)
        sqrt_eps = (1.0 + gamma) / (1.0 - gamma)
        return sqrt_eps ** 2
    
    def loss_tangent(self, permittivity: complex) -> float:
        """
        Compute loss tangent.
        
        Args:
            permittivity: Complex permittivity
        
        Returns:
            tan(delta)
        """
        if permittivity.real == 0:
            return 0.0
        return permittivity.imag / permittivity.real
    
    def penetration_depth_mm(self, frequency_GHz: float,
                           permittivity: complex) -> float:
        """
        Compute penetration depth.
        
        Args:
            frequency_GHz: Frequency
            permittivity: Permittivity
        
        Returns:
            Depth in mm
        """
        # delta = c / (2*pi*f*sqrt(eps')*tan(delta))
        c = 3e8  # m/s
        f = frequency_GHz * 1e9
        eps_prime = max(permittivity.real, 1.0)
        tan_d = self.loss_tangent(permittivity)
        
        if tan_d < 1e-10:
            return 1e6  # Very large
        
        delta_m = c / (2.0 * math.pi * f * math.sqrt(eps_prime) * tan_d)
        return delta_m * 1e3  # mm


class MicrowaveAntenna:
    """
    Microwave antenna model.
    """
    
    def __init__(self, frequency_GHz: float = 10.0,
                 diameter_mm: float = 50.0):
        """
        Args:
            frequency_GHz: Frequency
            diameter_mm: Aperture diameter
        """
        self.frequency = frequency_GHz
        self.diameter = diameter_mm * 1e-3
        self.wavelength_m = 0.3 / frequency_GHz  # In air
    
    def beamwidth_deg(self) -> float:
        """
        Compute beamwidth.
        
        Returns:
            Beamwidth in degrees
        """
        # theta = 70 * lambda / D
        theta_rad = 1.22 * self.wavelength_m / max(self.diameter, 1e-6)
        return math.degrees(theta_rad)
    
    def focal_distance_mm(self) -> float:
        """
        Compute focal distance.
        
        Returns:
            Focal distance in mm
        """
        # For lens-focused antenna
        return self.diameter ** 2 / (4.0 * self.wavelength_m) * 1e3
    
    def near_field_mm(self) -> float:
        """
        Compute near field distance.
        
        Returns:
            Distance in mm
        """
        return 2.0 * self.diameter ** 2 / self.wavelength_m * 1e3


class SubsurfaceImager:
    """
    Subsurface imaging from microwave data.
    """
    
    def __init__(self, scan_resolution_mm: float = 5.0):
        """
        Args:
            scan_resolution_mm: Resolution
        """
        self.resolution = scan_resolution_mm
    
    def bscan(self, a_scans: List[List[float]]) -> List[List[float]]:
        """
        Generate B-scan from A-scans.
        
        Args:
            a_scans: List of A-scans
        
        Returns:
            B-scan image
        """
        if not a_scans:
            return []
        
        # Transpose: depth vs position
        num_scans = len(a_scans)
        num_points = max(len(scan) for scan in a_scans)
        
        bscan = []
        for depth in range(num_points):
            row = []
            for scan in a_scans:
                if depth < len(scan):
                    row.append(scan[depth])
                else:
                    row.append(0.0)
            bscan.append(row)
        
        return bscan
    
    def cscan(self, b_scan: List[List[float]],
             depth_index: int = 0) -> List[List[float]]:
        """
        Extract C-scan at depth.
        
        Args:
            b_scan: B-scan
            depth_index: Depth index
        
        Returns:
            C-scan slice
        """
        if not b_scan or depth_index >= len(b_scan):
            return []
        
        # Return single depth slice as 2D
        return [[b_scan[depth_index][i]] for i in range(len(b_scan[depth_index]))]


class MicrowaveTesting:
    """
    Unified microwave testing controller.
    """
    
    def __init__(self):
        self.dielectric = DielectricEstimator()
        self.antenna = MicrowaveAntenna()
        self.imager = SubsurfaceImager()
        self.measurements: List[SParameter] = []
        self.a_scans: List[List[float]] = []
    
    def measure_reflection(self, frequency_GHz: float,
                          s11_mag: float,
                          s11_phase: float):
        """
        Record reflection measurement.
        
        Args:
            frequency_GHz: Frequency
            s11_mag: S11 magnitude
            s11_phase: S11 phase
        """
        self.measurements.append(SParameter(
            frequency_GHz=frequency_GHz,
            s11_magnitude=s11_mag,
            s11_phase=s11_phase
        ))
    
    def analyze_permittivity(self, measurement_index: int = 0) -> Dict:
        """
        Analyze dielectric properties.
        
        Args:
            measurement_index: Measurement index
        
        Returns:
            Properties
        """
        if measurement_index >= len(self.measurements):
            return {}
        
        m = self.measurements[measurement_index]
        eps = self.dielectric.permittivity_from_reflection(
            m.s11_magnitude, m.s11_phase, m.frequency_GHz
        )
        tan_d = self.dielectric.loss_tangent(eps)
        depth = self.dielectric.penetration_depth_mm(m.frequency_GHz, eps)
        
        return {
            "permittivity_real": eps.real,
            "permittivity_imag": eps.imag,
            "loss_tangent": tan_d,
            "penetration_depth_mm": depth
        }
    
    def microwave_summary(self) -> Dict:
        """Get summary."""
        return {
            "measurements": len(self.measurements),
            "a_scans": len(self.a_scans),
            "beamwidth_deg": self.antenna.beamwidth_deg(),
            "near_field_mm": self.antenna.near_field_mm()
        }
