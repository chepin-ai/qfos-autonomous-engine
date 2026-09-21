"""
Electrochemistry Module
Cyclic voltammetry, Tafel analysis, corrosion rate,
potentiostat control, and electrochemical impedance for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VoltammetryPoint:
    """Voltammetry data point."""
    potential_V: float
    current_A: float
    time_s: float


class CyclicVoltammetry:
    """
    Cyclic voltammetry analysis.
    """
    
    def __init__(self, scan_rate_vs: float = 0.1):
        """
        Args:
            scan_rate_vs: Scan rate in V/s
        """
        self.scan_rate = scan_rate_vs
    
    def peak_current_randles_sevcik(self, n: int,
                                   area_cm2: float,
                                   concentration_mol_L: float,
                                   diffusion_coeff_cm2_s: float) -> float:
        """
        Compute peak current using Randles-Sevcik equation.
        
        Args:
            n: Number of electrons
            area_cm2: Electrode area
            concentration_mol_L: Concentration
            diffusion_coeff_cm2_s: Diffusion coefficient
        
        Returns:
            Peak current in A
        """
        # ip = 0.4463 * n * F * A * C * sqrt(n * F * v * D / (R * T))
        F = 96485.0  # C/mol
        R = 8.314    # J/(mol*K)
        T = 298.15   # K
        
        return (0.4463 * n * F * area_cm2 * concentration_mol_L *
                math.sqrt(n * F * self.scan_rate * diffusion_coeff_cm2_s / (R * T)))
    
    def find_peaks(self, data: List[VoltammetryPoint]) -> Dict:
        """
        Find anodic and cathodic peaks.
        
        Args:
            data: Voltammetry data
        
        Returns:
            Peak info
        """
        if not data:
            return {}
        
        anodic = max(data, key=lambda p: p.current_A)
        cathodic = min(data, key=lambda p: p.current_A)
        
        return {
            "anodic_potential_V": anodic.potential_V,
            "anodic_current_A": anodic.current_A,
            "cathodic_potential_V": cathodic.potential_V,
            "cathodic_current_A": cathodic.current_A,
            "peak_separation_V": abs(anodic.potential_V - cathodic.potential_V)
        }
    
    def formal_potential(self, e_pa_V: float,
                        e_pc_V: float) -> float:
        """
        Compute formal potential.
        
        Args:
            e_pa_V: Anodic peak potential
            e_pc_V: Cathodic peak potential
        
        Returns:
            Formal potential
        """
        return (e_pa_V + e_pc_V) / 2.0


class TafelAnalysis:
    """
    Tafel slope analysis.
    """
    
    def __init__(self):
        pass
    
    def tafel_slope(self, overpotential_V: float,
                   current_density_A_cm2: float,
                   exchange_current_A_cm2: float) -> float:
        """
        Compute Tafel slope from single point.
        
        Args:
            overpotential_V: Overpotential
            current_density_A_cm2: Current density
            exchange_current_A_cm2: Exchange current density
        
        Returns:
            Tafel slope in V/decade
        """
        if current_density_A_cm2 <= 0 or exchange_current_A_cm2 <= 0:
            return 0.0
        
        return overpotential_V / math.log10(current_density_A_cm2 / exchange_current_A_cm2)
    
    def exchange_current_from_tafel(self, slope_V_decade: float,
                                   overpotential_V: float,
                                   current_density_A_cm2: float) -> float:
        """
        Compute exchange current density.
        
        Args:
            slope_V_decade: Tafel slope
            overpotential_V: Overpotential
            current_density_A_cm2: Current density
        
        Returns:
            Exchange current density
        """
        if slope_V_decade == 0:
            return 0.0
        
        decades = overpotential_V / slope_V_decade
        return current_density_A_cm2 / (10.0 ** decades)


class CorrosionAnalyzer:
    """
    Analyze corrosion rates.
    """
    
    def __init__(self):
        pass
    
    def corrosion_rate_mpy(self, current_density_uA_cm2: float,
                          equivalent_weight_g_eq: float,
                          density_g_cm3: float) -> float:
        """
        Compute corrosion rate in mils per year.
        
        Args:
            current_density_uA_cm2: Current density
            equivalent_weight_g_eq: Equivalent weight
            density_g_cm3: Density
        
        Returns:
            Corrosion rate in mpy
        """
        if density_g_cm3 <= 0:
            return 0.0
        # Constant: 0.1288
        return 0.1288 * current_density_uA_cm2 * equivalent_weight_g_eq / density_g_cm3
    
    def polarization_resistance(self, beta_a_V: float,
                               beta_c_V: float,
                               r_p_ohm_cm2: float,
                               current_density_A_cm2: float) -> float:
        """
        Compute corrosion current from polarization resistance.
        
        Args:
            beta_a_V: Anodic Tafel slope
            beta_c_V: Cathodic Tafel slope
            r_p_ohm_cm2: Polarization resistance
            current_density_A_cm2: Current density
        
        Returns:
            Corrosion current density
        """
        if r_p_ohm_cm2 <= 0:
            return 0.0
        
        b = (beta_a_V * beta_c_V) / (2.303 * (beta_a_V + beta_c_V))
        return b / r_p_ohm_cm2


class Potentiostat:
    """
    Potentiostat control simulation.
    """
    
    def __init__(self, compliance_V: float = 10.0,
                 scan_rate_vs: float = 0.1):
        """
        Args:
            compliance_V: Compliance voltage
            scan_rate_vs: Scan rate in V/s
        """
        self.compliance = compliance_V
        self.scan_rate = scan_rate_vs
        self.measurements: List[VoltammetryPoint] = []
    
    def apply_potential(self, potential_V: float,
                       measured_current_A: float,
                       time_s: float) -> VoltammetryPoint:
        """
        Apply potential and measure.
        
        Args:
            potential_V: Applied potential
            measured_current_A: Measured current
            time_s: Time
        
        Returns:
            Measurement point
        """
        point = VoltammetryPoint(potential_V, measured_current_A, time_s)
        self.measurements.append(point)
        return point
    
    def sweep(self, start_V: float, end_V: float,
             num_points: int,
             current_func) -> List[VoltammetryPoint]:
        """
        Linear potential sweep.
        
        Args:
            start_V: Start potential
            end_V: End potential
            num_points: Number of points
            current_func: Function(potential) -> current
        
        Returns:
            Sweep data
        """
        data = []
        for i in range(num_points):
            frac = i / (num_points - 1) if num_points > 1 else 0
            pot = start_V + frac * (end_V - start_V)
            curr = current_func(pot)
            point = VoltammetryPoint(pot, curr, frac * abs(end_V - start_V) / self.scan_rate if self.scan_rate > 0 else 0)
            data.append(point)
            self.measurements.append(point)
        return data


class Electrochemistry:
    """
    Unified electrochemistry controller.
    """
    
    def __init__(self):
        self.cv = CyclicVoltammetry()
        self.tafel = TafelAnalysis()
        self.corrosion = CorrosionAnalyzer()
        self.potentiostat = Potentiostat()
    
    def analyze_cv(self, data: List[VoltammetryPoint]) -> Dict:
        """
        Analyze cyclic voltammetry data.
        
        Args:
            data: CV data
        
        Returns:
            Results
        """
        peaks = self.cv.find_peaks(data)
        
        if "anodic_potential_V" in peaks and "cathodic_potential_V" in peaks:
            peaks["formal_potential_V"] = self.cv.formal_potential(
                peaks["anodic_potential_V"],
                peaks["cathodic_potential_V"])
        
        return peaks
    
    def ec_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["cyclic_voltammetry", "tafel", "corrosion", "potentiostat"],
            "measurements": len(self.potentiostat.measurements)
        }
