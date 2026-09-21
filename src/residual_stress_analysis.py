"""
Residual Stress Analysis Module
Hole drilling, X-ray diffraction,
sin2psi method, and stress relaxation for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StrainRosette:
    """Strain gauge rosette readings."""
    e0: float
    e45: float
    e90: float


class HoleDrillingMethod:
    """
    Hole-drilling residual stress measurement.
    """
    
    def __init__(self, hole_diameter_mm: float = 2.0):
        """
        Args:
            hole_diameter_mm: Hole diameter
        """
        self.d = hole_diameter_mm
    
    def principal_stresses(self, strains: StrainRosette,
                          youngs_modulus_GPa: float = 200.0,
                          poisson_ratio: float = 0.3) -> Tuple[float, float]:
        """
        Compute principal stresses from strain rosette.
        
        Args:
            strains: Rosette readings
            youngs_modulus_GPa: Young's modulus
            poisson_ratio: Poisson ratio
        
        Returns:
            (sigma1, sigma2) MPa
        """
        E = youngs_modulus_GPa * 1e3
        e_avg = (strains.e0 + strains.e90) / 2.0
        e_diff = (strains.e0 - strains.e90) / 2.0
        e_shear = strains.e45 - e_avg
        
        denom = 1.0 - poisson_ratio**2
        sigma_avg = E * e_avg / denom
        tau_max = E * math.sqrt(e_diff**2 + e_shear**2) / denom
        
        sigma1 = sigma_avg + tau_max
        sigma2 = sigma_avg - tau_max
        return sigma1, sigma2
    
    def stress_direction(self, strains: StrainRosette) -> float:
        """
        Compute principal stress direction.
        
        Args:
            strains: Rosette readings
        
        Returns:
            Angle (degrees)
        """
        e_diff = (strains.e0 - strains.e90) / 2.0
        e_shear = strains.e45 - (strains.e0 + strains.e90) / 2.0
        if abs(e_diff) < 1e-10:
            return 45.0 if e_shear > 0 else -45.0
        return 0.5 * math.degrees(math.atan2(e_shear, e_diff))


class XrayDiffraction:
    """
    X-ray diffraction stress measurement.
    """
    
    def __init__(self):
        pass
    
    def d_spacing(self, theta_deg: float,
                 wavelength_nm: float = 0.154) -> float:
        """
        Compute d-spacing from Bragg angle.
        
        Args:
            theta_deg: Bragg angle
            wavelength_nm: X-ray wavelength
        
        Returns:
            d-spacing (nm)
        """
        theta_rad = math.radians(theta_deg)
        return wavelength_nm / (2.0 * math.sin(theta_rad))
    
    def strain_from_d(self, d_measured_nm: float,
                     d0_nm: float) -> float:
        """
        Compute strain from d-spacing change.
        
        Args:
            d_measured_nm: Measured d
            d0_nm: Stress-free d
        
        Returns:
            Strain
        """
        if d0_nm <= 0:
            return 0.0
        return (d_measured_nm - d0_nm) / d0_nm


class Sin2PsiMethod:
    """
    sin2psi XRD stress analysis.
    """
    
    def __init__(self):
        pass
    
    def stress_from_slope(self, slope: float,
                         youngs_modulus_GPa: float = 200.0,
                         poisson_ratio: float = 0.3,
                         psi_angles_deg: List[float] = None) -> float:
        """
        Compute stress from d vs sin2psi slope.
        
        Args:
            slope: d vs sin2psi slope
            youngs_modulus_GPa: Young's modulus
            poisson_ratio: Poisson ratio
            psi_angles_deg: Psi angles used
        
        Returns:
            Stress (MPa)
        """
        E = youngs_modulus_GPa * 1e3
        # Stress = slope * E / (1 + nu) * conversion factor
        return slope * E / (1.0 + poisson_ratio)
    
    def sin2psi_values(self, psi_angles_deg: List[float]) -> List[float]:
        """
        Compute sin2psi values.
        
        Args:
            psi_angles_deg: Psi tilt angles
        
        Returns:
            sin2psi values
        """
        return [math.sin(math.radians(p))**2 for p in psi_angles_deg]


class StressRelaxation:
    """
    Stress relaxation analysis.
    """
    
    def __init__(self):
        pass
    
    def relaxed_stress(self, initial_stress_MPa: float,
                      time_h: float,
                      relaxation_time_h: float = 100.0) -> float:
        """
        Compute relaxed stress (exponential decay).
        
        Args:
            initial_stress_MPa: Initial stress
            time_h: Time
            relaxation_time_h: Relaxation time constant
        
        Returns:
            Remaining stress (MPa)
        """
        if relaxation_time_h <= 0:
            return initial_stress_MPa
        return initial_stress_MPa * math.exp(-time_h / relaxation_time_h)
    
    def relaxation_rate(self, stress_MPa: float,
                       time_h: float) -> float:
        """
        Compute relaxation rate.
        
        Args:
            stress_MPa: Current stress
            time_h: Time
        
        Returns:
            Rate (MPa/h)
        """
        if time_h <= 0:
            return 0.0
        return -stress_MPa / time_h


class ResidualStressAnalysis:
    """
    Unified residual stress analysis controller.
    """
    
    def __init__(self):
        self.hole_drilling = HoleDrillingMethod()
        self.xrd = XrayDiffraction()
        self.sin2psi = Sin2PsiMethod()
        self.relaxation = StressRelaxation()
    
    def stress_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["hole_drilling", "xrd", "sin2psi", "relaxation"],
            "applications": ["welding", "machining", "additive_manufacturing"]
        }
