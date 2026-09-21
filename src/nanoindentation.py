"""
Nanoindentation Module
Oliver-Pharr analysis, hardness measurement,
modulus extraction, and tip calibration for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LoadDisplacementData:
    """Nanoindentation load-displacement point."""
    load_mN: float
    displacement_nm: float


class OliverPharrAnalysis:
    """
    Oliver-Pharr method for nanoindentation analysis.
    """
    
    def __init__(self, tip_area_coeff_nm2: float = 24.5):
        """
        Args:
            tip_area_coeff_nm2: Tip area coefficient (Berkovich = 24.5)
        """
        self.C = tip_area_coeff_nm2
    
    def contact_stiffness(self, unloading_data: List[LoadDisplacementData]) -> float:
        """
        Compute contact stiffness from unloading slope.
        
        Args:
            unloading_data: Unloading curve points
        
        Returns:
            Stiffness (mN/nm = N/m scaled)
        """
        if len(unloading_data) < 2:
            return 0.0
        # Simplified: slope between first two points
        dP = unloading_data[0].load_mN - unloading_data[-1].load_mN
        dh = unloading_data[0].displacement_nm - unloading_data[-1].displacement_nm
        if dh == 0:
            return 0.0
        return abs(dP / dh)
    
    def contact_depth(self, max_displacement_nm: float,
                     max_load_mN: float,
                     stiffness: float) -> float:
        """
        Compute contact depth hc.
        
        Args:
            max_displacement_nm: Maximum displacement
            max_load_mN: Maximum load
            stiffness: Contact stiffness
        
        Returns:
            Contact depth (nm)
        """
        if stiffness <= 0:
            return max_displacement_nm
        epsilon = 0.75  # fitting parameter
        return max_displacement_nm - epsilon * max_load_mN / stiffness
    
    def contact_area(self, contact_depth_nm: float) -> float:
        """
        Compute projected contact area.
        
        Args:
            contact_depth_nm: Contact depth
        
        Returns:
            Area (nm^2)
        """
        if contact_depth_nm <= 0:
            return 0.0
        return self.C * contact_depth_nm ** 2
    
    def hardness(self, max_load_mN: float,
                contact_area_nm2: float) -> float:
        """
        Compute hardness H = Pmax / A.
        
        Args:
            max_load_mN: Maximum load
            contact_area_nm2: Contact area
        
        Returns:
            Hardness (mN/nm^2 = GPa scaled)
        """
        if contact_area_nm2 <= 0:
            return 0.0
        return max_load_mN / contact_area_nm2
    
    def reduced_modulus(self, stiffness: float,
                       contact_area_nm2: float) -> float:
        """
        Compute reduced modulus Er.
        
        Args:
            stiffness: Contact stiffness
            contact_area_nm2: Contact area
        
        Returns:
            Reduced modulus (mN/nm^2 = GPa scaled)
        """
        if contact_area_nm2 <= 0:
            return 0.0
        beta = 1.034  # correction factor
        return stiffness / (2.0 * beta * math.sqrt(contact_area_nm2))


class TipCalibration:
    """
    Indenter tip area function calibration.
    """
    
    def __init__(self):
        pass
    
    def area_function(self, contact_depth_nm: float,
                     C0: float = 24.5,
                     C1: float = 0.0,
                     C2: float = 0.0) -> float:
        """
        Compute area from depth using calibrated function.
        
        Args:
            contact_depth_nm: Contact depth
            C0, C1, C2: Calibration coefficients
        
        Returns:
            Area (nm^2)
        """
        if contact_depth_nm <= 0:
            return 0.0
        return C0 * contact_depth_nm**2 + C1 * contact_depth_nm + C2 * contact_depth_nm**0.5
    
    def frame_compliance(self, measured_compliance_nm_mN: float,
                        sample_compliance_nm_mN: float) -> float:
        """
        Compute frame compliance.
        
        Args:
            measured_compliance_nm_mN: Measured
            sample_compliance_nm_mN: Sample
        
        Returns:
            Frame compliance
        """
        if measured_compliance_nm_mN <= sample_compliance_nm_mN:
            return 0.0
        return measured_compliance_nm_mN - sample_compliance_nm_mN


class ModulusExtraction:
    """
    Extract Young's modulus from reduced modulus.
    """
    
    def __init__(self):
        pass
    
    def youngs_modulus(self, reduced_modulus_GPa: float,
                      poisson_ratio_sample: float = 0.3,
                      poisson_ratio_tip: float = 0.07,
                      modulus_tip_GPa: float = 1140.0) -> float:
        """
        Compute sample Young's modulus.
        
        Args:
            reduced_modulus_GPa: Er
            poisson_ratio_sample: Sample nu
            poisson_ratio_tip: Tip nu
            modulus_tip_GPa: Tip E
        
        Returns:
            Young's modulus (GPa)
        """
        if reduced_modulus_GPa <= 0:
            return 0.0
        term_tip = (1.0 - poisson_ratio_tip**2) / modulus_tip_GPa
        term_sample = (1.0 - poisson_ratio_sample**2)
        if term_sample <= 0:
            return 0.0
        return term_sample / (1.0 / reduced_modulus_GPa - term_tip)


class CreepCorrection:
    """
    Creep correction for nanoindentation.
    """
    
    def __init__(self):
        pass
    
    def creep_displacement(self, hold_time_s: float,
                          creep_rate_s: float = 1e-3) -> float:
        """
        Estimate creep displacement during hold.
        
        Args:
            hold_time_s: Hold time
            creep_rate_s: Creep rate
        
        Returns:
            Creep displacement (nm)
        """
        return creep_rate_s * hold_time_s * 1000.0  # convert to nm approx


class Nanoindentation:
    """
    Unified nanoindentation controller.
    """
    
    def __init__(self):
        self.oliver_pharr = OliverPharrAnalysis()
        self.tip = TipCalibration()
        self.modulus = ModulusExtraction()
        self.creep = CreepCorrection()
    
    def nanoindentation_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["oliver_pharr", "tip_calibration", "modulus_extraction", "creep_correction"],
            "outputs": ["hardness", "reduced_modulus", "youngs_modulus"]
        }
