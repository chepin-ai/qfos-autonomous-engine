"""
Hardness Tester Module
Brinell, Rockwell, Vickers, and Knoop hardness testing
for autonomous materials characterization.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class HardnessScale(Enum):
    """Hardness testing scales."""
    BRINELL = "hb"
    ROCKWELL_B = "hrb"
    ROCKWELL_C = "hrc"
    VICKERS = "hv"
    KNOOP = "hk"


@dataclass
class Indentation:
    """An indentation measurement."""
    diameter_mm: float = 0.0
    depth_mm: float = 0.0
    diagonal_mm: float = 0.0
    major_axis_mm: float = 0.0
    minor_axis_mm: float = 0.0


class BrinellHardness:
    """
    Brinell hardness tester.
    HBW = 2F / (pi * D * (D - sqrt(D^2 - d^2)))
    """
    
    def __init__(self, ball_diameter_mm: float = 10.0):
        """
        Args:
            ball_diameter_mm: Indenter ball diameter
        """
        self.D = ball_diameter_mm
    
    def compute(self, force_N: float,
               indentation_diameter_mm: float) -> float:
        """
        Compute Brinell hardness.
        
        Args:
            force_N: Applied force
            indentation_diameter_mm: Indentation diameter
        
        Returns:
            HBW value
        """
        d = indentation_diameter_mm
        if d >= self.D or d <= 0:
            return 0.0
        
        term = self.D - math.sqrt(self.D**2 - d**2)
        if term <= 0:
            return 0.0
        
        return (2.0 * force_N) / (math.pi * self.D * term)
    
    def estimate_diameter(self, force_N: float,
                         hardness_hbw: float) -> float:
        """
        Estimate indentation diameter from hardness.
        
        Args:
            force_N: Force
            hardness_hbw: Hardness
        
        Returns:
            Estimated diameter
        """
        if hardness_hbw <= 0:
            return 0.0
        
        # Rearranged: d = D * sqrt(1 - (1 - 2F/(pi*D^2*HBW))^2)
        inner = 1.0 - (2.0 * force_N) / (math.pi * self.D**2 * hardness_hbw)
        if inner < -1.0 or inner > 1.0:
            return 0.0
        
        return self.D * math.sqrt(1.0 - inner**2)


class RockwellHardness:
    """
    Rockwell hardness tester.
    """
    
    def __init__(self):
        self.preload_N = 98.07  # 10 kgf
        self.hrc_load_N = 1471.0  # 150 kgf
        self.hrb_load_N = 980.7  # 100 kgf
    
    def hrc(self, depth_mm: float) -> float:
        """
        Compute Rockwell C hardness.
        
        Args:
            depth_mm: Penetration depth
        
        Returns:
            HRC value
        """
        # HRC = 100 - 500 * h (h in mm)
        return 100.0 - 500.0 * depth_mm
    
    def hrb(self, depth_mm: float) -> float:
        """
        Compute Rockwell B hardness.
        
        Args:
            depth_mm: Penetration depth
        
        Returns:
            HRB value
        """
        # HRB = 130 - 500 * h
        return 130.0 - 500.0 * depth_mm
    
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
    Vickers hardness tester.
    HV = 1.8544 * F / d^2
    """
    
    def __init__(self):
        self.constant = 1.8544
    
    def compute(self, force_N: float,
               diagonal_mm: float) -> float:
        """
        Compute Vickers hardness.
        
        Args:
            force_N: Force
            diagonal_mm: Mean diagonal length
        
        Returns:
            HV value
        """
        if diagonal_mm <= 0:
            return 0.0
        return self.constant * force_N / (diagonal_mm**2)
    
    def diagonal_from_hv(self, force_N: float,
                        hv: float) -> float:
        """
        Estimate diagonal from HV.
        
        Args:
            force_N: Force
            hv: Hardness
        
        Returns:
            Diagonal length
        """
        if hv <= 0:
            return 0.0
        return math.sqrt(self.constant * force_N / hv)


class KnoopHardness:
    """
    Knoop hardness tester.
    HK = 14.229 * F / L^2
    """
    
    def __init__(self):
        self.constant = 14.229
    
    def compute(self, force_N: float,
               major_axis_mm: float) -> float:
        """
        Compute Knoop hardness.
        
        Args:
            force_N: Force
            major_axis_mm: Long diagonal
        
        Returns:
            HK value
        """
        if major_axis_mm <= 0:
            return 0.0
        return self.constant * force_N / (major_axis_mm**2)


class HardnessConverter:
    """
    Approximate hardness conversions.
    """
    
    @staticmethod
    def hrc_to_hv(hrc: float) -> float:
        """
        Approximate HRC to Vickers.
        
        Args:
            hrc: HRC value
        
        Returns:
            Approximate HV
        """
        # Empirical approximation
        return 2.2 * hrc + 50.0 if hrc > 20 else 0.0
    
    @staticmethod
    def hv_to_hrc(hv: float) -> float:
        """
        Approximate Vickers to HRC.
        
        Args:
            hv: HV value
        
        Returns:
            Approximate HRC
        """
        return (hv - 50.0) / 2.2 if hv > 50 else 0.0
    
    @staticmethod
    def hbw_to_hv(hbw: float) -> float:
        """
        Approximate Brinell to Vickers.
        
        Args:
            hbw: HBW value
        
        Returns:
            Approximate HV
        """
        return hbw  # Rough approximation for steel


class HardnessTester:
    """
    Unified hardness testing controller.
    """
    
    def __init__(self):
        self.brinell = BrinellHardness()
        self.rockwell = RockwellHardness()
        self.vickers = VickersHardness()
        self.knoop = KnoopHardness()
        self.converter = HardnessConverter()
        self.measurements: List[Dict] = []
    
    def measure_brinell(self, force_N: float,
                       diameter_mm: float) -> Dict:
        """
        Measure Brinell hardness.
        
        Args:
            force_N: Force
            diameter_mm: Indentation diameter
        
        Returns:
            Results dict
        """
        hbw = self.brinell.compute(force_N, diameter_mm)
        result = {"scale": "HBW", "value": hbw, "force_N": force_N,
                 "diameter_mm": diameter_mm}
        self.measurements.append(result)
        return result
    
    def measure_vickers(self, force_N: float,
                       diagonal_mm: float) -> Dict:
        """
        Measure Vickers hardness.
        
        Args:
            force_N: Force
            diagonal_mm: Diagonal
        
        Returns:
            Results dict
        """
        hv = self.vickers.compute(force_N, diagonal_mm)
        result = {"scale": "HV", "value": hv, "force_N": force_N,
                 "diagonal_mm": diagonal_mm}
        self.measurements.append(result)
        return result
    
    def hardness_report(self) -> Dict:
        """
        Generate hardness report.
        
        Returns:
            Summary dict
        """
        if not self.measurements:
            return {"status": "no_data"}
        
        values = [m["value"] for m in self.measurements]
        return {
            "count": len(self.measurements),
            "avg_hardness": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }
