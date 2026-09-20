"""
Hardness Testing Module
Brinell, Rockwell, Vickers, Knoop, and Shore hardness testing
with indentation analysis for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Indentation:
    """Indentation measurement."""
    diameter_mm: float
    depth_mm: float
    load_N: float


class BrinellHardness:
    """
    Brinell hardness test.
    """
    
    def __init__(self, ball_diameter_mm: float = 10.0):
        """
        Args:
            ball_diameter_mm: Ball diameter
        """
        self.D = ball_diameter_mm
    
    def hardness(self, load_N: float,
                indentation_diameter_mm: float) -> float:
        """
        Compute Brinell hardness.
        
        Args:
            load_N: Applied load
            indentation_diameter_mm: Indentation diameter
        
        Returns:
            HBW
        """
        if self.D <= 0 or indentation_diameter_mm >= self.D:
            return 0.0
        
        d = indentation_diameter_mm
        D = self.D
        
        area = math.pi * D / 2.0 * (D - math.sqrt(D**2 - d**2))
        if area <= 0:
            return 0.0
        
        return load_N / area
    
    def indentation_diameter(self, load_N: float,
                            hardness_HBW: float) -> float:
        """
        Compute indentation diameter from hardness.
        
        Args:
            load_N: Load
            hardness_HBW: Hardness
        
        Returns:
            Diameter in mm
        """
        if hardness_HBW <= 0:
            return 0.0
        
        # Simplified approximation
        area = load_N / hardness_HBW
        # area = pi * D/2 * (D - sqrt(D^2 - d^2))
        # Solve for d
        term = 2.0 * area / (math.pi * self.D)
        inner = self.D - term
        if inner < 0:
            return 0.0
        d_sq = self.D**2 - inner**2
        return math.sqrt(d_sq) if d_sq >= 0 else 0.0


class RockwellHardness:
    """
    Rockwell hardness test.
    """
    
    def __init__(self):
        self.scales = {
            "A": {"preload_N": 98.07, "load_N": 490.3},
            "B": {"preload_N": 98.07, "load_N": 882.6},
            "C": {"preload_N": 98.07, "load_N": 1373.0}
        }
    
    def c_scale_hardness(self, residual_depth_mm: float) -> float:
        """
        Compute Rockwell C hardness.
        
        Args:
            residual_depth_mm: Residual depth
        
        Returns:
            HRC
        """
        # HRC = 100 - 500 * e (e in mm)
        return 100.0 - 500.0 * residual_depth_mm
    
    def b_scale_hardness(self, residual_depth_mm: float) -> float:
        """
        Compute Rockwell B hardness.
        
        Args:
            residual_depth_mm: Residual depth
        
        Returns:
            HRB
        """
        return 130.0 - 500.0 * residual_depth_mm
    
    def depth_from_hrc(self, hrc: float) -> float:
        """
        Compute depth from HRC.
        
        Args:
            hrc: HRC value
        
        Returns:
            Depth in mm
        """
        return (100.0 - hrc) / 500.0


class VickersHardness:
    """
    Vickers hardness test.
    """
    
    def __init__(self):
        self.pyramid_angle_deg = 136.0
    
    def hardness(self, load_N: float,
                diagonal_mm: float) -> float:
        """
        Compute Vickers hardness.
        
        Args:
            load_N: Load
            diagonal_mm: Mean diagonal
        
        Returns:
            HV
        """
        if diagonal_mm <= 0:
            return 0.0
        
        # HV = 1.8544 * F / d^2 (F in kgf, d in mm)
        # Convert N to kgf: 1 kgf = 9.80665 N
        load_kgf = load_N / 9.80665
        
        return 1.8544 * load_kgf / (diagonal_mm ** 2)
    
    def diagonal_from_hv(self, load_N: float,
                        hv: float) -> float:
        """
        Compute diagonal from HV.
        
        Args:
            load_N: Load
            hv: Hardness
        
        Returns:
            Diagonal in mm
        """
        if hv <= 0:
            return 0.0
        load_kgf = load_N / 9.80665
        return math.sqrt(1.8544 * load_kgf / hv)
    
    def indentation_depth(self, diagonal_mm: float) -> float:
        """
        Compute indentation depth.
        
        Args:
            diagonal_mm: Diagonal
        
        Returns:
            Depth in mm
        """
        angle_rad = math.radians(self.pyramid_angle_deg / 2.0)
        return diagonal_mm / (2.0 * math.sqrt(2.0) * math.tan(angle_rad))


class KnoopHardness:
    """
    Knoop hardness test.
    """
    
    def __init__(self):
        pass
    
    def hardness(self, load_N: float,
                long_diagonal_mm: float) -> float:
        """
        Compute Knoop hardness.
        
        Args:
            load_N: Load
            long_diagonal_mm: Long diagonal
        
        Returns:
            HK
        """
        if long_diagonal_mm <= 0:
            return 0.0
        
        load_kgf = load_N / 9.80665
        return 14.229 * load_kgf / (long_diagonal_mm ** 2)


class ShoreHardness:
    """
    Shore hardness test (durometer).
    """
    
    def __init__(self, scale: str = "A"):
        """
        Args:
            scale: Scale (A or D)
        """
        self.scale = scale
    
    def hardness(self, indentation_depth_mm: float) -> float:
        """
        Compute Shore hardness.
        
        Args:
            indentation_depth_mm: Indentation depth
        
        Returns:
            Shore value
        """
        max_depth = 2.54  # mm for Shore A
        if self.scale == "D":
            max_depth = 2.54
        
        return 100.0 - (indentation_depth_mm / max_depth) * 100.0


class HardnessConverter:
    """
    Convert between hardness scales.
    """
    
    def __init__(self):
        pass
    
    def hrc_to_hv(self, hrc: float) -> float:
        """
        Approximate HRC to HV conversion.
        
        Args:
            hrc: HRC value
        
        Returns:
            Approximate HV
        """
        # Simplified linear approximation
        return hrc * 10.0
    
    def hv_to_hrc(self, hv: float) -> float:
        """
        Approximate HV to HRC conversion.
        
        Args:
            hv: HV value
        
        Returns:
            Approximate HRC
        """
        return hv / 10.0
    
    def hbw_to_hv(self, hbw: float) -> float:
        """
        Approximate HBW to HV conversion.
        
        Args:
            hbw: HBW value
        
        Returns:
            Approximate HV
        """
        return hbw * 1.05


class HardnessTesting:
    """
    Unified hardness testing controller.
    """
    
    def __init__(self):
        self.brinell = BrinellHardness()
        self.rockwell = RockwellHardness()
        self.vickers = VickersHardness()
        self.knoop = KnoopHardness()
        self.shore = ShoreHardness()
        self.converter = HardnessConverter()
        self.measurements: List[Dict] = []
    
    def test_all(self, indentation: Indentation) -> Dict:
        """
        Test with all methods.
        
        Args:
            indentation: Indentation data
        
        Returns:
            Results
        """
        results = {
            "brinell_HBW": self.brinell.hardness(
                indentation.load_N, indentation.diameter_mm),
            "rockwell_C": self.rockwell.c_scale_hardness(
                indentation.depth_mm),
            "vickers_HV": self.vickers.hardness(
                indentation.load_N, indentation.diameter_mm),
            "knoop_HK": self.knoop.hardness(
                indentation.load_N, indentation.diameter_mm),
            "shore_A": self.shore.hardness(indentation.depth_mm)
        }
        
        self.measurements.append(results)
        return results
    
    def ht_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["Brinell", "Rockwell", "Vickers", "Knoop", "Shore"],
            "measurements": len(self.measurements)
        }
