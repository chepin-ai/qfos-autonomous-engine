"""
Residual Stress Analysis Module
XRD sin2psi, hole drilling, strain relaxation,
stress tensor calculation, and depth profiling for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StressTensor:
    """Stress tensor components."""
    sigma_11: float
    sigma_22: float
    sigma_12: float
    sigma_33: float = 0.0


class XRDSin2Psi:
    """
    X-ray diffraction sin^2(psi) method.
    """
    
    def __init__(self, youngs_modulus_GPa: float = 200.0,
                 poisson_ratio: float = 0.3,
                 diffraction_angle_deg: float = 150.0):
        """
        Args:
            youngs_modulus_GPa: Young's modulus
            poisson_ratio: Poisson's ratio
            diffraction_angle_deg: 2*theta angle
        """
        self.E = youngs_modulus_GPa * 1e3
        self.nu = poisson_ratio
        self.theta0 = math.radians(diffraction_angle_deg / 2.0)
    
    def strain_from_psi(self, d_spacing_angstrom: List[float],
                       psi_degrees: List[float]) -> List[float]:
        """
        Compute strain from d-spacing vs sin^2(psi).
        
        Args:
            d_spacing_angstrom: Measured d-spacings
            psi_degrees: Tilt angles
        
        Returns:
            Strain values
        """
        if not d_spacing_angstrom:
            return []
        d0 = d_spacing_angstrom[0]
        strains = []
        for d in d_spacing_angstrom:
            strain = (d - d0) / d0
            strains.append(strain)
        return strains
    
    def stress_from_slope(self, slope: float) -> float:
        """
        Compute stress from d vs sin^2(psi) slope.
        
        Args:
            slope: Slope of d vs sin^2(psi)
        
        Returns:
            Stress in MPa
        """
        # Stress = E / (1 + nu) * 1 / d0 * slope / (pi / 180 * cot(theta0))
        # Simplified:
        cot_theta = 1.0 / math.tan(self.theta0)
        if cot_theta == 0:
            return 0.0
        factor = self.E / (1.0 + self.nu) * slope * cot_theta
        return factor * 1e-6  # Convert to MPa
    
    def linear_fit(self, sin2psi: List[float],
                  d_spacing: List[float]) -> Tuple[float, float]:
        """
        Linear fit d = a + b * sin^2(psi).
        
        Args:
            sin2psi: sin^2(psi) values
            d_spacing: d-spacings
        
        Returns:
            (intercept, slope)
        """
        n = len(sin2psi)
        if n == 0:
            return 0.0, 0.0
        
        sx = sum(sin2psi)
        sy = sum(d_spacing)
        sxx = sum(x ** 2 for x in sin2psi)
        sxy = sum(x * y for x, y in zip(sin2psi, d_spacing))
        
        denom = n * sxx - sx ** 2
        if denom == 0:
            return sy / n, 0.0
        
        slope = (n * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / n
        return intercept, slope


class HoleDrilling:
    """
    Hole drilling strain gauge method.
    """
    
    def __init__(self, rosette_radius_mm: float = 5.0):
        """
        Args:
            rosette_radius_mm: Rosette radius
        """
        self.r = rosette_radius_mm
    
    def relaxed_strains(self, strains_before: List[float],
                       strains_after: List[float]) -> List[float]:
        """
        Compute relaxed strains.
        
        Args:
            strains_before: Strains before drilling
            strains_after: Strains after drilling
        
        Returns:
            Relaxed strains
        """
        return [b - a for b, a in zip(strains_before, strains_after)]
    
    def principal_stresses(self, epsilon_0: float,
                          epsilon_45: float,
                          epsilon_90: float,
                          E_GPa: float = 200.0,
                          nu: float = 0.3) -> Tuple[float, float, float]:
        """
        Compute principal stresses from rosette.
        
        Args:
            epsilon_0: 0 degree strain
            epsilon_45: 45 degree strain
            epsilon_90: 90 degree strain
            E_GPa: Young's modulus
            nu: Poisson's ratio
        
        Returns:
            (sigma_1, sigma_2, theta_deg)
        """
        E = E_GPa * 1e3
        
        # Average and difference
        eps_avg = (epsilon_0 + epsilon_90) / 2.0
        eps_diff = (epsilon_0 - epsilon_90) / 2.0
        eps_shear = epsilon_45 - eps_avg
        
        # Principal strains
        gamma = math.sqrt(eps_diff ** 2 + eps_shear ** 2)
        eps_1 = eps_avg + gamma
        eps_2 = eps_avg - gamma
        
        # Principal stresses
        sigma_1 = E / (1.0 - nu ** 2) * (eps_1 + nu * eps_2) * 1e-6
        sigma_2 = E / (1.0 - nu ** 2) * (eps_2 + nu * eps_1) * 1e-6
        
        # Angle
        theta = 0.5 * math.degrees(math.atan2(eps_shear, eps_diff))
        
        return sigma_1, sigma_2, theta


class DepthProfiler:
    """
    Residual stress depth profiling.
    """
    
    def __init__(self):
        pass
    
    def layer_removal_correction(self, stress_measured_MPa: float,
                                layer_thickness_mm: float,
                                total_thickness_mm: float) -> float:
        """
        Apply layer removal correction.
        
        Args:
            stress_measured_MPa: Measured stress
            layer_thickness_mm: Removed layer thickness
            total_thickness_mm: Total thickness
        
        Returns:
            Corrected stress
        """
        if total_thickness_mm <= 0:
            return stress_measured_MPa
        ratio = layer_thickness_mm / total_thickness_mm
        # Simplified correction factor
        correction = 1.0 / (1.0 - ratio)
        return stress_measured_MPa * correction
    
    def integrate_stress(self, stresses_MPa: List[float],
                        depths_mm: List[float]) -> float:
        """
        Integrate stress over depth.
        
        Args:
            stresses_MPa: Stress profile
            depths_mm: Depths
        
        Returns:
            Integrated force per unit width in N/mm
        """
        if len(stresses_MPa) < 2 or len(depths_mm) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(stresses_MPa) - 1):
            dz = depths_mm[i + 1] - depths_mm[i]
            avg_stress = (stresses_MPa[i] + stresses_MPa[i + 1]) / 2.0
            total += avg_stress * dz
        
        return total


class ResidualStressAnalysis:
    """
    Unified residual stress analysis controller.
    """
    
    def __init__(self):
        self.xrd = XRDSin2Psi()
        self.drilling = HoleDrilling()
        self.profiler = DepthProfiler()
    
    def stress_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["XRD_sin2psi", "hole_drilling", "depth_profiling"],
            "applications": ["welds", "coatings", "machined_surfaces"]
        }
