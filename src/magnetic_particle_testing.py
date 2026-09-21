"""
Magnetic Particle Testing Module
Magnetization, indication detection, field strength measurement,
particle concentration, and sensitivity verification for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MTIndication:
    """Magnetic particle indication."""
    x: float
    y: float
    length_mm: float
    width_mm: float
    orientation_deg: float
    severity: str


class Magnetizer:
    """
    Magnetization for magnetic particle testing.
    """
    
    def __init__(self):
        pass
    
    def longitudinal_magnetization(self, current_A: float,
                                   turns: int,
                                   length_m: float) -> float:
        """
        Compute longitudinal magnetization field.
        
        Args:
            current_A: Current
            turns: Number of coil turns
            length_m: Part length
        
        Returns:
            Magnetic field in A/m
        """
        if length_m <= 0:
            return 0.0
        return (current_A * turns) / length_m
    
    def circular_magnetization(self, current_A: float,
                              diameter_m: float) -> float:
        """
        Compute circular magnetization field.
        
        Args:
            current_A: Current
            diameter_m: Part diameter
        
        Returns:
            Magnetic field in A/m
        """
        if diameter_m <= 0:
            return 0.0
        return current_A / (math.pi * diameter_m)
    
    def required_current(self, diameter_m: float,
                        standard: str = "ASTM") -> float:
        """
        Compute required magnetizing current.
        
        Args:
            diameter_m: Part diameter
            standard: Standard to use
        
        Returns:
            Current in A
        """
        if diameter_m <= 0:
            return 0.0
        if standard == "ASTM":
            return 350.0 * diameter_m / 25.4e-3  # 350 A per inch
        return 0.0
    
    def flux_density(self, magnetic_field_A_m: float,
                    permeability_H_m: float = 4.0e-7 * math.pi) -> float:
        """
        Compute magnetic flux density.
        
        Args:
            magnetic_field_A_m: Magnetic field
            permeability_H_m: Permeability
        
        Returns:
            Flux density in Tesla
        """
        return permeability_H_m * magnetic_field_A_m


class IndicationAnalyzer:
    """
    Magnetic particle indication analysis.
    """
    
    def __init__(self):
        pass
    
    def indication_area(self, length_mm: float,
                       width_mm: float) -> float:
        """
        Compute indication area.
        
        Args:
            length_mm: Length
            width_mm: Width
        
        Returns:
            Area in mm^2
        """
        return length_mm * width_mm
    
    def severity_rating(self, length_mm: float,
                       standard: str = "ASTM") -> str:
        """
        Rate indication severity.
        
        Args:
            length_mm: Indication length
            standard: Standard
        
        Returns:
            Severity rating
        """
        if standard == "ASTM":
            if length_mm < 1.5:
                return "minor"
            elif length_mm < 3.0:
                return "moderate"
            else:
                return "severe"
        return "unknown"
    
    def false_call_probability(self, indication_length_mm: float,
                              background_level: float) -> float:
        """
        Estimate false call probability.
        
        Args:
            indication_length_mm: Indication length
            background_level: Background level
        
        Returns:
            Probability
        """
        # Simplified: shorter indications in high background more likely false
        if indication_length_mm < 1.0 and background_level > 0.5:
            return 0.7
        elif indication_length_mm < 2.0:
            return 0.3
        return 0.1


class ParticleConcentration:
    """
    Magnetic particle concentration control.
    """
    
    def __init__(self):
        pass
    
    def concentration_from_settling(self, settled_volume_ml: float,
                                   bath_volume_ml: float) -> float:
        """
        Compute particle concentration from settling test.
        
        Args:
            settled_volume_ml: Settled particle volume
            bath_volume_ml: Total bath volume
        
        Returns:
            Concentration in ml/100ml
        """
        if bath_volume_ml <= 0:
            return 0.0
        return settled_volume_ml / bath_volume_ml * 100.0
    
    def is_acceptable(self, concentration_ml_per_100ml: float,
                     particle_type: str = "wet") -> bool:
        """
        Check if concentration is acceptable.
        
        Args:
            concentration_ml_per_100ml: Concentration
            particle_type: Particle type
        
        Returns:
            Whether acceptable
        """
        if particle_type == "wet":
            return 0.1 <= concentration_ml_per_100ml <= 0.4
        return False


class SensitivityVerifier:
    """
    MT sensitivity verification.
    """
    
    def __init__(self):
        pass
    
    def pie_gauge_sensitivity(self, visible_sectors: int) -> float:
        """
        Compute sensitivity from pie gauge.
        
        Args:
            visible_sectors: Number of visible sectors
        
        Returns:
            Sensitivity fraction
        """
        return visible_sectors / 8.0
    
    def ketos_ring_sensitivity(self, visible_holes: int) -> float:
        """
        Compute sensitivity from Ketos ring.
        
        Args:
            visible_holes: Number of visible holes
        
        Returns:
            Sensitivity fraction
        """
        return visible_holes / 12.0


class MagneticParticleTesting:
    """
    Unified magnetic particle testing controller.
    """
    
    def __init__(self):
        self.magnetizer = Magnetizer()
        self.indication = IndicationAnalyzer()
        self.concentration = ParticleConcentration()
        self.sensitivity = SensitivityVerifier()
    
    def mpt_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["magnetization", "indication_analysis", "concentration", "sensitivity"],
            "standards": ["ASTM", "ISO"]
        }
