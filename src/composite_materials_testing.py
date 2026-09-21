"""
Composite Materials Testing Module
Fiber volume fraction, laminate stiffness,
failure criteria, interlaminar stresses, and delamination for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PlyProperties:
    """Ply material properties."""
    E1_GPa: float
    E2_GPa: float
    G12_GPa: float
    nu12: float
    thickness_mm: float
    angle_deg: float = 0.0


class FiberVolumeFraction:
    """
    Fiber volume fraction analysis.
    """
    
    def __init__(self):
        pass
    
    def rule_of_mixtures_E(self, E_f_GPa: float,
                          E_m_GPa: float,
                          V_f: float) -> float:
        """
        Compute longitudinal modulus using rule of mixtures.
        
        Args:
            E_f_GPa: Fiber modulus
            E_m_GPa: Matrix modulus
            V_f: Fiber volume fraction
        
        Returns:
            Composite modulus (GPa)
        """
        V_m = 1.0 - V_f
        return E_f_GPa * V_f + E_m_GPa * V_m
    
    def inverse_rule_E2(self, E_f_GPa: float,
                       E_m_GPa: float,
                       V_f: float) -> float:
        """
        Compute transverse modulus.
        
        Args:
            E_f_GPa: Fiber modulus
            E_m_GPa: Matrix modulus
            V_f: Fiber volume fraction
        
        Returns:
            Transverse modulus (GPa)
        """
        V_m = 1.0 - V_f
        if E_f_GPa <= 0 or E_m_GPa <= 0:
            return 0.0
        return (E_f_GPa * E_m_GPa) / (E_m_GPa * V_f + E_f_GPa * V_m)
    
    def void_content(self, theoretical_density: float,
                    measured_density: float) -> float:
        """
        Compute void content.
        
        Args:
            theoretical_density: Theoretical density
            measured_density: Measured density
        
        Returns:
            Void fraction
        """
        if theoretical_density <= 0:
            return 0.0
        return (theoretical_density - measured_density) / theoretical_density


class LaminateStiffness:
    """
    Classical Lamination Theory (CLT) stiffness.
    """
    
    def __init__(self):
        pass
    
    def transformed_stiffness(self, ply: PlyProperties) -> Tuple[float, float, float, float, float]:
        """
        Compute transformed stiffness for angled ply.
        
        Args:
            ply: Ply properties
        
        Returns:
            (Q11_bar, Q12_bar, Q22_bar, Q16_bar, Q26_bar, Q66_bar)
        """
        theta = math.radians(ply.angle_deg)
        c = math.cos(theta)
        s = math.sin(theta)
        c2 = c * c
        s2 = s * s
        c4 = c2 * c2
        s4 = s2 * s2
        
        nu21 = ply.nu12 * ply.E2_GPa / ply.E1_GPa
        Q11 = ply.E1_GPa / (1.0 - ply.nu12 * nu21)
        Q12 = ply.nu12 * ply.E2_GPa / (1.0 - ply.nu12 * nu21)
        Q22 = ply.E2_GPa / (1.0 - ply.nu12 * nu21)
        Q66 = ply.G12_GPa
        
        Q11_bar = Q11 * c4 + 2.0 * (Q12 + 2.0 * Q66) * s2 * c2 + Q22 * s4
        Q12_bar = (Q11 + Q22 - 4.0 * Q66) * s2 * c2 + Q12 * (s4 + c4)
        Q22_bar = Q11 * s4 + 2.0 * (Q12 + 2.0 * Q66) * s2 * c2 + Q22 * c4
        Q66_bar = (Q11 + Q22 - 2.0 * Q12 - 2.0 * Q66) * s2 * c2 + Q66 * (s4 + c4)
        
        return Q11_bar, Q12_bar, Q22_bar, Q66_bar
    
    def A_matrix(self, plies: List[PlyProperties]) -> float:
        """
        Compute extensional stiffness A11 (simplified).
        
        Args:
            plies: List of plies
        
        Returns:
            A11 in GPa.mm
        """
        A11 = 0.0
        for ply in plies:
            Q11_bar, _, _, _ = self.transformed_stiffness(ply)
            A11 += Q11_bar * ply.thickness_mm
        return A11


class FailureCriteria:
    """
    Composite failure criteria.
    """
    
    def __init__(self):
        pass
    
    def tsai_wu(self, sigma1_MPa: float,
               sigma2_MPa: float,
               tau12_MPa: float,
               Xt: float, Xc: float,
               Yt: float, Yc: float,
               S: float) -> float:
        """
        Tsai-Wu failure criterion.
        
        Args:
            sigma1_MPa: Stress in fiber direction
            sigma2_MPa: Stress transverse
            tau12_MPa: Shear stress
            Xt: Tensile strength fiber
            Xc: Compressive strength fiber
            Yt: Tensile strength transverse
            Yc: Compressive strength transverse
            S: Shear strength
        
        Returns:
            Failure index (>=1 = failure)
        """
        F1 = 1.0 / Xt - 1.0 / Xc
        F2 = 1.0 / Yt - 1.0 / Yc
        F11 = 1.0 / (Xt * Xc)
        F22 = 1.0 / (Yt * Yc)
        F12 = -0.5 * math.sqrt(F11 * F22)
        F66 = 1.0 / (S ** 2)
        
        index = (F1 * sigma1_MPa + F2 * sigma2_MPa +
                F11 * sigma1_MPa**2 + F22 * sigma2_MPa**2 +
                2.0 * F12 * sigma1_MPa * sigma2_MPa +
                F66 * tau12_MPa**2)
        return index
    
    def max_stress(self, sigma1_MPa: float,
                  sigma2_MPa: float,
                  tau12_MPa: float,
                  Xt: float, Xc: float,
                  Yt: float, Yc: float,
                  S: float) -> float:
        """
        Maximum stress criterion.
        
        Args:
            sigma1_MPa: Stress in fiber direction
            sigma2_MPa: Stress transverse
            tau12_MPa: Shear stress
            Xt: Tensile strength fiber
            Xc: Compressive strength fiber
            Yt: Tensile strength transverse
            Yc: Compressive strength transverse
            S: Shear strength
        
        Returns:
            Maximum failure ratio
        """
        ratios = []
        if sigma1_MPa >= 0:
            ratios.append(abs(sigma1_MPa) / Xt)
        else:
            ratios.append(abs(sigma1_MPa) / Xc)
        if sigma2_MPa >= 0:
            ratios.append(abs(sigma2_MPa) / Yt)
        else:
            ratios.append(abs(sigma2_MPa) / Yc)
        ratios.append(abs(tau12_MPa) / S)
        return max(ratios)


class DelaminationAnalysis:
    """
    Interlaminar fracture and delamination.
    """
    
    def __init__(self):
        pass
    
    def strain_energy_release_rate(self, force_N: float,
                                  displacement_m: float,
                                  crack_area_m2: float) -> float:
        """
        Compute mode I strain energy release rate.
        
        Args:
            force_N: Applied force
            displacement_m: Displacement
            crack_area_m2: Crack area
        
        Returns:
            G_I (J/m^2)
        """
        if crack_area_m2 <= 0:
            return 0.0
        return 0.5 * force_N * displacement_m / crack_area_m2
    
    def critical_load(self, G_Ic: float,
                     crack_length_m: float,
                     compliance_slope: float) -> float:
        """
        Compute critical load for delamination growth.
        
        Args:
            G_Ic: Critical strain energy release rate
            crack_length_m: Crack length
            compliance_slope: dC/da
        
        Returns:
            Critical load
        """
        if compliance_slope <= 0:
            return 0.0
        return math.sqrt(2.0 * G_Ic / (crack_length_m * compliance_slope))


class CompositeMaterialsTesting:
    """
    Unified composite materials testing controller.
    """
    
    def __init__(self):
        self.fiber_vol = FiberVolumeFraction()
        self.laminate = LaminateStiffness()
        self.failure = FailureCriteria()
        self.delam = DelaminationAnalysis()
    
    def composite_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["rule_of_mixtures", "CLT", "Tsai-Wu", "delamination"],
            "properties": ["stiffness", "strength", "fracture_toughness"]
        }
