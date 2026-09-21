"""
Thermal Analysis Module
Heat transfer, thermal conductivity, specific heat,
thermal expansion, and temperature distribution for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ThermalPoint:
    """Thermal data point."""
    position_m: float
    temperature_K: float
    time_s: float


class HeatConduction:
    """
    Steady-state heat conduction.
    """
    
    def __init__(self, thermal_conductivity_W_mK: float = 1.0):
        """
        Args:
            thermal_conductivity_W_mK: Thermal conductivity
        """
        self.k = thermal_conductivity_W_mK
    
    def heat_flux(self, area_m2: float,
                 thickness_m: float,
                 delta_T_K: float) -> float:
        """
        Compute heat flux (Fourier's law).
        
        Args:
            area_m2: Cross-sectional area
            thickness_m: Thickness
            delta_T_K: Temperature difference
        
        Returns:
            Heat flux in W
        """
        if thickness_m <= 0:
            return 0.0
        return self.k * area_m2 * delta_T_K / thickness_m
    
    def thermal_resistance(self, thickness_m: float,
                          area_m2: float) -> float:
        """
        Compute thermal resistance.
        
        Args:
            thickness_m: Thickness
            area_m2: Area
        
        Returns:
            Thermal resistance in K/W
        """
        if self.k <= 0 or area_m2 <= 0:
            return float('inf')
        return thickness_m / (self.k * area_m2)
    
    def temperature_distribution(self, length_m: float,
                                T_left_K: float,
                                T_right_K: float,
                                num_points: int = 10) -> List[ThermalPoint]:
        """
        Compute 1D temperature distribution.
        
        Args:
            length_m: Length
            T_left_K: Left boundary temperature
            T_right_K: Right boundary temperature
            num_points: Number of points
        
        Returns:
            Temperature distribution
        """
        result = []
        for i in range(num_points):
            x = i * length_m / (num_points - 1)
            T = T_left_K + (T_right_K - T_left_K) * x / length_m
            result.append(ThermalPoint(x, T, 0.0))
        return result


class TransientHeat:
    """
    Transient heat analysis.
    """
    
    def __init__(self, thermal_diffusivity_m2_s: float = 1e-5):
        """
        Args:
            thermal_diffusivity_m2_s: Thermal diffusivity
        """
        self.alpha = thermal_diffusivity_m2_s
    
    def cooling_time(self, initial_T_K: float,
                    ambient_T_K: float,
                    target_T_K: float,
                    characteristic_length_m: float,
                    h_W_m2K: float = 10.0,
                    rho_kg_m3: float = 1000.0,
                    cp_J_kgK: float = 1000.0) -> float:
        """
        Estimate cooling time using lumped capacitance.
        
        Args:
            initial_T_K: Initial temperature
            ambient_T_K: Ambient temperature
            target_T_K: Target temperature
            characteristic_length_m: Characteristic length
            h_W_m2K: Convective coefficient
            rho_kg_m3: Density
            cp_J_kgK: Specific heat
        
        Returns:
            Time in seconds
        """
        if initial_T_K <= ambient_T_K or target_T_K <= ambient_T_K:
            return 0.0
        
        biot = h_W_m2K * characteristic_length_m / (rho_kg_m3 * cp_J_kgK * self.alpha)
        
        ratio = (target_T_K - ambient_T_K) / (initial_T_K - ambient_T_K)
        if ratio <= 0:
            return float('inf')
        
        return -characteristic_length_m ** 2 / (self.alpha * biot) * math.log(ratio)
    
    def biot_number(self, h_W_m2K: float,
                   characteristic_length_m: float,
                   k_W_mK: float) -> float:
        """
        Compute Biot number.
        
        Args:
            h_W_m2K: Convective coefficient
            characteristic_length_m: Characteristic length
            k_W_mK: Thermal conductivity
        
        Returns:
            Biot number
        """
        if k_W_mK <= 0:
            return 0.0
        return h_W_m2K * characteristic_length_m / k_W_mK


class ThermalExpansion:
    """
    Thermal expansion analysis.
    """
    
    def __init__(self, coefficient_1_K: float = 1e-5):
        """
        Args:
            coefficient_1_K: Coefficient of thermal expansion
        """
        self.alpha = coefficient_1_K
    
    def delta_length(self, initial_length_m: float,
                    delta_T_K: float) -> float:
        """
        Compute length change.
        
        Args:
            initial_length_m: Initial length
            delta_T_K: Temperature change
        
        Returns:
            Length change in m
        """
        return self.alpha * initial_length_m * delta_T_K
    
    def delta_volume(self, initial_volume_m3: float,
                    delta_T_K: float) -> float:
        """
        Compute volume change.
        
        Args:
            initial_volume_m3: Initial volume
            delta_T_K: Temperature change
        
        Returns:
            Volume change in m^3
        """
        return 3.0 * self.alpha * initial_volume_m3 * delta_T_K
    
    def thermal_stress(self, E_GPa: float,
                      delta_T_K: float) -> float:
        """
        Compute thermal stress (constrained expansion).
        
        Args:
            E_GPa: Young's modulus
            delta_T_K: Temperature change
        
        Returns:
            Stress in MPa
        """
        return self.alpha * E_GPa * 1000.0 * delta_T_K  # Convert GPa to MPa


class SpecificHeatAnalysis:
    """
    Specific heat analysis.
    """
    
    def __init__(self):
        pass
    
    def heat_capacity(self, mass_kg: float,
                     cp_J_kgK: float) -> float:
        """
        Compute heat capacity.
        
        Args:
            mass_kg: Mass
            cp_J_kgK: Specific heat
        
        Returns:
            Heat capacity in J/K
        """
        return mass_kg * cp_J_kgK
    
    def energy_required(self, mass_kg: float,
                       cp_J_kgK: float,
                       delta_T_K: float) -> float:
        """
        Compute energy to change temperature.
        
        Args:
            mass_kg: Mass
            cp_J_kgK: Specific heat
            delta_T_K: Temperature change
        
        Returns:
            Energy in J
        """
        return mass_kg * cp_J_kgK * delta_T_K


class ThermalAnalysis:
    """
    Unified thermal analysis controller.
    """
    
    def __init__(self):
        self.conduction = HeatConduction()
        self.transient = TransientHeat()
        self.expansion = ThermalExpansion()
        self.specific_heat = SpecificHeatAnalysis()
    
    def ta_summary(self) -> Dict:
        """Get summary."""
        return {
            "analyses": ["conduction", "transient", "expansion", "specific_heat"],
            "conductivity_W_mK": self.conduction.k,
            "expansion_coeff_1_K": self.expansion.alpha
        }
