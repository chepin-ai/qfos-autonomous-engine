"""
Corrosion Testing Module
Electrochemical impedance spectroscopy, polarization curves,
Tafel analysis, pitting potential, and corrosion rate for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EISPoint:
    """EIS measurement point."""
    frequency_Hz: float
    z_real_Ohm: float
    z_imag_Ohm: float


class PolarizationCurve:
    """
    Electrochemical polarization curve analysis.
    """
    
    def __init__(self, tafel_slope_anodic_V_decade: float = 0.12,
                 tafel_slope_cathodic_V_decade: float = -0.12):
        """
        Args:
            tafel_slope_anodic_V_decade: Anodic Tafel slope (V/decade)
            tafel_slope_cathodic_V_decade: Cathodic Tafel slope (V/decade)
        """
        self.beta_a = tafel_slope_anodic_V_decade
        self.beta_c = tafel_slope_cathodic_V_decade
    
    def corrosion_current(self, Rp_Ohm_cm2: float,
                         b_a: float = None,
                         b_c: float = None) -> float:
        """
        Compute corrosion current from polarization resistance.
        
        Args:
            Rp_Ohm_cm2: Polarization resistance
            b_a: Anodic Tafel slope (optional)
            b_c: Cathodic Tafel slope (optional)
        
        Returns:
            Corrosion current density (A/cm^2)
        """
        ba = b_a if b_a is not None else self.beta_a
        bc = b_c if b_c is not None else abs(self.beta_c)
        if Rp_Ohm_cm2 <= 0:
            return 0.0
        return (ba * bc) / (2.303 * Rp_Ohm_cm2 * (ba + bc))
    
    def corrosion_rate_mpy(self, icorr_A_cm2: float,
                          equivalent_weight_g: float = 27.92,
                          density_g_cm3: float = 7.87) -> float:
        """
        Compute corrosion rate in mils per year.
        
        Args:
            icorr_A_cm2: Corrosion current density
            equivalent_weight_g: Equivalent weight
            density_g_cm3: Density
        
        Returns:
            Corrosion rate (mpy)
        """
        if density_g_cm3 <= 0:
            return 0.0
        # Simplified Stern-Geary: CR = 0.1288 * icorr * EW / rho
        return 0.1288 * icorr_A_cm2 * 1e6 * equivalent_weight_g / density_g_cm3
    
    def tafel_potential(self, Ecorr_V: float,
                       current_A_cm2: float,
                       icorr_A_cm2: float,
                       beta_V_decade: float) -> float:
        """
        Compute potential from Tafel equation.
        
        Args:
            Ecorr_V: Corrosion potential
            current_A_cm2: Applied current
            icorr_A_cm2: Corrosion current
            beta_V_decade: Tafel slope
        
        Returns:
            Potential (V)
        """
        if icorr_A_cm2 <= 0:
            return Ecorr_V
        return Ecorr_V + beta_V_decade * math.log10(current_A_cm2 / icorr_A_cm2)


class TafelAnalysis:
    """
    Tafel extrapolation analysis.
    """
    
    def __init__(self):
        pass
    
    def extrapolate_icorr(self, potentials_V: List[float],
                         currents_A_cm2: List[float],
                         Ecorr_V: float) -> float:
        """
        Extrapolate corrosion current from Tafel region.
        
        Args:
            potentials_V: Measured potentials
            currents_A_cm2: Measured currents
            Ecorr_V: Corrosion potential
        
        Returns:
            Corrosion current
        """
        if not potentials_V or not currents_A_cm2:
            return 0.0
        # Find current at Ecorr by interpolation
        for i in range(len(potentials_V) - 1):
            if (potentials_V[i] <= Ecorr_V <= potentials_V[i+1] or
                potentials_V[i+1] <= Ecorr_V <= potentials_V[i]):
                return currents_A_cm2[i]
        return currents_A_cm2[0] if currents_A_cm2 else 0.0
    
    def tafel_slope(self, log_currents: List[float],
                   potentials: List[float]) -> float:
        """
        Compute Tafel slope from linear region.
        
        Args:
            log_currents: log10(current)
            potentials: Corresponding potentials
        
        Returns:
            Tafel slope (V/decade)
        """
        if len(log_currents) < 2 or len(potentials) < 2:
            return 0.0
        # Simple linear fit on first two points
        dV = potentials[1] - potentials[0]
        dlogI = log_currents[1] - log_currents[0]
        if dlogI == 0:
            return 0.0
        return dV / dlogI


class PittingPotential:
    """
    Pitting corrosion potential analysis.
    """
    
    def __init__(self):
        pass
    
    def pitting_potential(self, potentials_V: List[float],
                         currents_A_cm2: List[float],
                         threshold_A_cm2: float = 1e-5) -> Optional[float]:
        """
        Determine pitting potential from cyclic polarization.
        
        Args:
            potentials_V: Measured potentials
            currents_A_cm2: Measured currents
            threshold_A_cm2: Current threshold
        
        Returns:
            Pitting potential (V) or None
        """
        for i in range(len(currents_A_cm2)):
            if currents_A_cm2[i] >= threshold_A_cm2:
                return potentials_V[i] if i < len(potentials_V) else None
        return None
    
    def protection_potential(self, reverse_potentials_V: List[float],
                            reverse_currents_A_cm2: List[float],
                            forward_threshold_A_cm2: float = 1e-5) -> Optional[float]:
        """
        Determine protection potential on reverse scan.
        
        Args:
            reverse_potentials_V: Reverse scan potentials
            reverse_currents_A_cm2: Reverse scan currents
            forward_threshold_A_cm2: Current threshold
        
        Returns:
            Protection potential (V) or None
        """
        for i in range(len(reverse_currents_A_cm2)):
            if reverse_currents_A_cm2[i] <= forward_threshold_A_cm2:
                return reverse_potentials_V[i] if i < len(reverse_potentials_V) else None
        return reverse_potentials_V[-1] if reverse_potentials_V else None


class ElectrochemicalImpedance:
    """
    Electrochemical impedance spectroscopy (EIS) analysis.
    """
    
    def __init__(self):
        pass
    
    def impedance_magnitude(self, z_real: float,
                           z_imag: float) -> float:
        """
        Compute impedance magnitude.
        
        Args:
            z_real: Real part
            z_imag: Imaginary part
        
        Returns:
            |Z| (Ohm)
        """
        return math.sqrt(z_real**2 + z_imag**2)
    
    def phase_angle(self, z_real: float,
                   z_imag: float) -> float:
        """
        Compute phase angle in degrees.
        
        Args:
            z_real: Real part
            z_imag: Imaginary part
        
        Returns:
            Phase angle (degrees)
        """
        return math.degrees(math.atan2(z_imag, z_real))
    
    def polarization_resistance(self, low_freq_points: List[EISPoint]) -> float:
        """
        Extract polarization resistance from low frequency EIS data.
        
        Args:
            low_freq_points: Low frequency EIS points
        
        Returns:
            Rp (Ohm.cm^2)
        """
        if not low_freq_points:
            return 0.0
        # Use lowest frequency point
        point = min(low_freq_points, key=lambda p: p.frequency_Hz)
        return self.impedance_magnitude(point.z_real_Ohm, point.z_imag_Ohm)


class CorrosionTesting:
    """
    Unified corrosion testing controller.
    """
    
    def __init__(self):
        self.polarization = PolarizationCurve()
        self.tafel = TafelAnalysis()
        self.pitting = PittingPotential()
        self.eis = ElectrochemicalImpedance()
    
    def corrosion_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["polarization", "Tafel", "EIS", "pitting_potential"],
            "outputs": ["icorr", "corrosion_rate", "Rp", "Epit"]
        }
