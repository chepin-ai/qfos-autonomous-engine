"""
Additive Manufacturing Module
Process parameter optimization, melt pool thermal modeling,
residual stress prediction, and support structure design for autonomous materials engineering.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ProcessParameters:
    """AM process parameters."""
    laser_power_W: float
    scan_speed_mm_s: float
    hatch_spacing_mm: float
    layer_thickness_mm: float


class ProcessParameterOptimization:
    """
    Optimize AM process parameters.
    """
    
    def __init__(self):
        pass
    
    def energy_density(self, params: ProcessParameters) -> float:
        """
        Compute volumetric energy density (J/mm^3).
        
        Args:
            params: Process parameters
        
        Returns:
            Energy density
        """
        denom = params.scan_speed_mm_s * params.hatch_spacing_mm * params.layer_thickness_mm
        if denom <= 0:
            return 0.0
        return params.laser_power_W / denom
    
    def linear_energy_density(self, params: ProcessParameters) -> float:
        """
        Compute linear energy density (J/mm).
        
        Args:
            params: Process parameters
        
        Returns:
            Linear energy density
        """
        if params.scan_speed_mm_s <= 0:
            return 0.0
        return params.laser_power_W / params.scan_speed_mm_s
    
    def optimal_power(self, target_energy_density_J_mm3: float,
                     scan_speed_mm_s: float,
                     hatch_spacing_mm: float,
                     layer_thickness_mm: float) -> float:
        """
        Compute optimal laser power for target energy density.
        
        Args:
            target_energy_density_J_mm3: Target EVD
            scan_speed_mm_s: Scan speed
            hatch_spacing_mm: Hatch spacing
            layer_thickness_mm: Layer thickness
        
        Returns:
            Optimal power (W)
        """
        return target_energy_density_J_mm3 * scan_speed_mm_s * hatch_spacing_mm * layer_thickness_mm


class MeltPoolThermalModeling:
    """
    Melt pool thermal modeling.
    """
    
    def __init__(self):
        pass
    
    def melt_pool_depth(self, laser_power_W: float,
                       scan_speed_mm_s: float,
                       absorptivity: float = 0.3,
                       thermal_conductivity_W_mK: float = 25.0,
                       melting_temperature_K: float = 1800.0,
                       ambient_temperature_K: float = 300.0) -> float:
        """
        Estimate melt pool depth (simplified Rosenthal).
        
        Args:
            laser_power_W: Laser power
            scan_speed_mm_s: Scan speed
            absorptivity: Laser absorptivity
            thermal_conductivity_W_mK: Conductivity
            melting_temperature_K: Melting point
            ambient_temperature_K: Ambient
        
        Returns:
            Depth (mm)
        """
        if scan_speed_mm_s <= 0 or thermal_conductivity_W_mK <= 0:
            return 0.0
        # Simplified: depth proportional to P / (v * k * dT)
        delta_T = melting_temperature_K - ambient_temperature_K
        if delta_T <= 0:
            return 0.0
        depth_m = absorptivity * laser_power_W / (scan_speed_mm_s * 1e-3 * thermal_conductivity_W_mK * delta_T)
        return depth_m * 1e3  # Convert to mm
    
    def melt_pool_width(self, laser_power_W: float,
                       scan_speed_mm_s: float,
                       beam_diameter_mm: float = 0.1) -> float:
        """
        Estimate melt pool width.
        
        Args:
            laser_power_W: Laser power
            scan_speed_mm_s: Scan speed
            beam_diameter_mm: Beam diameter
        
        Returns:
            Width (mm)
        """
        if scan_speed_mm_s <= 0:
            return beam_diameter_mm
        # Simplified: width ~ beam + thermal diffusion
        return beam_diameter_mm + 0.5 * laser_power_W / (scan_speed_mm_s * 100.0)
    
    def cooling_rate(self, scan_speed_mm_s: float,
                    thermal_diffusivity_mm2_s: float = 5.0) -> float:
        """
        Estimate cooling rate.
        
        Args:
            scan_speed_mm_s: Scan speed
            thermal_diffusivity_mm2_s: Thermal diffusivity
        
        Returns:
            Cooling rate (K/s)
        """
        if thermal_diffusivity_mm2_s <= 0:
            return 0.0
        return scan_speed_mm_s ** 2 / thermal_diffusivity_mm2_s


class ResidualStressPrediction:
    """
    Residual stress prediction for AM.
    """
    
    def __init__(self):
        pass
    
    def thermal_strain(self, delta_T_K: float,
                      thermal_expansion_coefficient_1_K: float = 1e-5) -> float:
        """
        Compute thermal strain.
        
        Args:
            delta_T_K: Temperature change
            thermal_expansion_coefficient_1_K: CTE
        
        Returns:
            Strain
        """
        return thermal_expansion_coefficient_1_K * delta_T_K
    
    def residual_stress(self, elastic_modulus_GPa: float,
                       thermal_strain: float,
                       yield_strength_MPa: float = 500.0) -> float:
        """
        Estimate residual stress.
        
        Args:
            elastic_modulus_GPa: Young's modulus
            thermal_strain: Thermal strain
            yield_strength_MPa: Yield strength
        
        Returns:
            Residual stress (MPa)
        """
        stress = elastic_modulus_GPa * 1e3 * thermal_strain  # Convert GPa to MPa
        return min(stress, yield_strength_MPa)
    
    def distortion(self, residual_stress_MPa: float,
                  elastic_modulus_GPa: float = 200.0,
                  part_length_mm: float = 100.0,
                  part_thickness_mm: float = 10.0) -> float:
        """
        Estimate part distortion.
        
        Args:
            residual_stress_MPa: Residual stress
            elastic_modulus_GPa: Modulus
            part_length_mm: Length
            part_thickness_mm: Thickness
        
        Returns:
            Distortion (mm)
        """
        if elastic_modulus_GPa <= 0 or part_thickness_mm <= 0:
            return 0.0
        # Simplified: bending deflection
        return residual_stress_MPa * part_length_mm ** 2 / (elastic_modulus_GPa * 1e3 * part_thickness_mm)


class SupportStructureDesign:
    """
    Support structure design for AM.
    """
    
    def __init__(self):
        pass
    
    def overhang_angle(self, horizontal_overhang_mm: float,
                      vertical_height_mm: float) -> float:
        """
        Compute overhang angle.
        
        Args:
            horizontal_overhang_mm: Horizontal projection
            vertical_height_mm: Vertical height
        
        Returns:
            Angle (degrees)
        """
        if vertical_height_mm <= 0:
            return 90.0
        return math.degrees(math.atan(vertical_height_mm / horizontal_overhang_mm))
    
    def needs_support(self, overhang_angle_deg: float,
                     threshold_deg: float = 45.0) -> bool:
        """
        Check if support is needed.
        
        Args:
            overhang_angle_deg: Overhang angle
            threshold_deg: Support threshold
        
        Returns:
            True if support needed
        """
        return overhang_angle_deg < threshold_deg
    
    def support_volume(self, supported_area_mm2: float,
                      support_height_mm: float,
                      density_factor: float = 0.3) -> float:
        """
        Estimate support material volume.
        
        Args:
            supported_area_mm2: Area
            support_height_mm: Height
            density_factor: Support density
        
        Returns:
            Volume (mm^3)
        """
        return supported_area_mm2 * support_height_mm * density_factor


class AdditiveManufacturing:
    """
    Unified additive manufacturing controller.
    """
    
    def __init__(self):
        self.process = ProcessParameterOptimization()
        self.melt_pool = MeltPoolThermalModeling()
        self.residual_stress = ResidualStressPrediction()
        self.support = SupportStructureDesign()
    
    def am_summary(self) -> Dict:
        """Get summary."""
        return {
            "modules": ["process_parameters", "melt_pool", "residual_stress", "support"],
            "outputs": ["energy_density", "melt_pool_dimensions", "residual_stress", "support_volume"]
        }
