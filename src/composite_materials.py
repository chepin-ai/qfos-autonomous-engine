"""
Composite Materials Module
Fiber volume fraction, rule of mixtures, laminate analysis,
stress-strain prediction, and failure criteria for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PlyProperties:
    """Composite ply properties."""
    E1_GPa: float  # Longitudinal modulus
    E2_GPa: float  # Transverse modulus
    G12_GPa: float  # In-plane shear modulus
    nu12: float    # Major Poisson ratio
    thickness_mm: float
    angle_deg: float  # Fiber orientation


class RuleOfMixtures:
    """
    Rule of mixtures for composite properties.
    """
    
    def __init__(self):
        pass
    
    def longitudinal_modulus(self, E_fiber_GPa: float,
                            E_matrix_GPa: float,
                            V_f: float) -> float:
        """
        Compute longitudinal modulus.
        
        Args:
            E_fiber_GPa: Fiber modulus
            E_matrix_GPa: Matrix modulus
            V_f: Fiber volume fraction
        
        Returns:
            Longitudinal modulus in GPa
        """
        return E_fiber_GPa * V_f + E_matrix_GPa * (1.0 - V_f)
    
    def transverse_modulus(self, E_fiber_GPa: float,
                          E_matrix_GPa: float,
                          V_f: float) -> float:
        """
        Compute transverse modulus (inverse rule of mixtures).
        
        Args:
            E_fiber_GPa: Fiber modulus
            E_matrix_GPa: Matrix modulus
            V_f: Fiber volume fraction
        
        Returns:
            Transverse modulus in GPa
        """
        if E_fiber_GPa <= 0 or E_matrix_GPa <= 0:
            return 0.0
        return 1.0 / (V_f / E_fiber_GPa + (1.0 - V_f) / E_matrix_GPa)
    
    def shear_modulus(self, G_fiber_GPa: float,
                     G_matrix_GPa: float,
                     V_f: float) -> float:
        """
        Compute in-plane shear modulus.
        
        Args:
            G_fiber_GPa: Fiber shear modulus
            G_matrix_GPa: Matrix shear modulus
            V_f: Fiber volume fraction
        
        Returns:
            Shear modulus in GPa
        """
        if G_fiber_GPa <= 0 or G_matrix_GPa <= 0:
            return 0.0
        return 1.0 / (V_f / G_fiber_GPa + (1.0 - V_f) / G_matrix_GPa)
    
    def fiber_volume_fraction(self, fiber_mass_g: float,
                             matrix_mass_g: float,
                             rho_fiber_g_cm3: float,
                             rho_matrix_g_cm3: float) -> float:
        """
        Compute fiber volume fraction from masses.
        
        Args:
            fiber_mass_g: Fiber mass
            matrix_mass_g: Matrix mass
            rho_fiber_g_cm3: Fiber density
            rho_matrix_g_cm3: Matrix density
        
        Returns:
            Fiber volume fraction
        """
        if rho_fiber_g_cm3 <= 0 or rho_matrix_g_cm3 <= 0:
            return 0.0
        V_f = fiber_mass_g / rho_fiber_g_cm3
        V_m = matrix_mass_g / rho_matrix_g_cm3
        total = V_f + V_m
        if total <= 0:
            return 0.0
        return V_f / total


class LaminateAnalysis:
    """
    Classical Lamination Theory (CLT).
    """
    
    def __init__(self):
        self.plies: List[PlyProperties] = []
    
    def add_ply(self, ply: PlyProperties):
        """
        Add ply.
        
        Args:
            ply: Ply properties
        """
        self.plies.append(ply)
    
    def total_thickness(self) -> float:
        """
        Compute total thickness.
        
        Returns:
            Total thickness in mm
        """
        return sum(p.thickness_mm for p in self.plies)
    
    def engineering_constants(self) -> Dict[str, float]:
        """
        Compute laminate engineering constants.
        
        Returns:
            Engineering constants
        """
        if not self.plies:
            return {"Ex": 0.0, "Ey": 0.0, "Gxy": 0.0}
        
        # Simplified: average properties weighted by thickness
        total_t = self.total_thickness()
        if total_t <= 0:
            return {"Ex": 0.0, "Ey": 0.0, "Gxy": 0.0}
        
        Ex = sum(p.E1_GPa * p.thickness_mm for p in self.plies) / total_t
        Ey = sum(p.E2_GPa * p.thickness_mm for p in self.plies) / total_t
        Gxy = sum(p.G12_GPa * p.thickness_mm for p in self.plies) / total_t
        
        return {"Ex": Ex, "Ey": Ey, "Gxy": Gxy}
    
    def abd_matrix(self) -> Tuple[List[List[float]], List[List[float]], List[List[float]]]:
        """
        Compute A, B, D matrices.
        
        Returns:
            (A, B, D) matrices
        """
        # Simplified 3x3 matrices
        A = [[0.0] * 3 for _ in range(3)]
        B = [[0.0] * 3 for _ in range(3)]
        D = [[0.0] * 3 for _ in range(3)]
        
        for ply in self.plies:
            t = ply.thickness_mm / 1000.0  # Convert to m
            Q11 = ply.E1_GPa * 1e9  # Convert to Pa
            Q22 = ply.E2_GPa * 1e9
            
            for i in range(3):
                A[i][i] += Q11 * t
                D[i][i] += Q11 * t ** 3 / 12.0
        
        return (A, B, D)


class FailureCriteria:
    """
    Composite failure criteria.
    """
    
    def __init__(self):
        pass
    
    def tsai_hill(self, sigma1: float,
                 sigma2: float,
                 tau12: float,
                 Xt: float,
                 Xc: float,
                 Yt: float,
                 Yc: float,
                 S: float) -> float:
        """
        Tsai-Hill failure criterion.
        
        Args:
            sigma1: Longitudinal stress
            sigma2: Transverse stress
            tau12: Shear stress
            Xt: Longitudinal tensile strength
            Xc: Longitudinal compressive strength
            Yt: Transverse tensile strength
            Yc: Transverse compressive strength
            S: Shear strength
        
        Returns:
            Failure index (>= 1 means failure)
        """
        X = Xt if sigma1 >= 0 else Xc
        Y = Yt if sigma2 >= 0 else Yc
        
        if X <= 0 or Y <= 0 or S <= 0:
            return float('inf')
        
        term1 = (sigma1 / X) ** 2
        term2 = (sigma2 / Y) ** 2
        term3 = (tau12 / S) ** 2
        term4 = sigma1 * sigma2 / X ** 2
        
        return term1 - term4 + term2 + term3
    
    def maximum_stress(self, sigma1: float,
                      sigma2: float,
                      tau12: float,
                      Xt: float,
                      Xc: float,
                      Yt: float,
                      Yc: float,
                      S: float) -> float:
        """
        Maximum stress criterion.
        
        Returns:
            Maximum failure index
        """
        indices = []
        
        if sigma1 >= 0:
            indices.append(abs(sigma1) / Xt if Xt > 0 else 0.0)
        else:
            indices.append(abs(sigma1) / Xc if Xc > 0 else 0.0)
        
        if sigma2 >= 0:
            indices.append(abs(sigma2) / Yt if Yt > 0 else 0.0)
        else:
            indices.append(abs(sigma2) / Yc if Yc > 0 else 0.0)
        
        indices.append(abs(tau12) / S if S > 0 else 0.0)
        
        return max(indices)


class CompositeMaterials:
    """
    Unified composite materials controller.
    """
    
    def __init__(self):
        self.rom = RuleOfMixtures()
        self.laminate = LaminateAnalysis()
        self.failure = FailureCriteria()
    
    def cm_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["rule_of_mixtures", "lamination_theory", "failure_criteria"],
            "plies": len(self.laminate.plies)
        }
