"""
Guided Wave Testing Module
Dispersion curve calculation, mode selection, group velocity,
and defect reflection analysis for autonomous long-range NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WaveMode:
    """Guided wave mode."""
    name: str
    frequency_Hz: float
    phase_velocity_m_s: float
    group_velocity_m_s: float
    attenuation_dB_m: float


class DispersionCalculator:
    """
    Calculate dispersion curves.
    """
    
    def __init__(self, thickness_mm: float = 10.0,
                 longitudinal_vel_m_s: float = 5900.0,
                 shear_vel_m_s: float = 3230.0):
        """
        Args:
            thickness_mm: Plate thickness
            longitudinal_vel_m_s: Longitudinal velocity
            shear_vel_m_s: Shear velocity
        """
        self.thickness = thickness_mm * 1e-3
        self.c_l = longitudinal_vel_m_s
        self.c_s = shear_vel_m_s
    
    def lamb_phase_velocity(self, fd_product_MHz_mm: float,
                           mode: int = 0) -> float:
        """
        Estimate Lamb wave phase velocity.
        
        Args:
            fd_product_MHz_mm: Frequency-thickness product
            mode: Mode number
        
        Returns:
            Phase velocity in m/s
        """
        fd = fd_product_MHz_mm * 1e6 * 1e-3
        
        # Simplified approximation for low fd
        if mode == 0:
            # A0 mode approximation
            return self.c_s * (1.0 - 0.1 * math.exp(-fd / 1e6))
        else:
            # Higher modes approach shear velocity
            return self.c_s * (1.0 + 0.05 * mode)
    
    def group_velocity(self, phase_vel: float,
                      frequency_Hz: float) -> float:
        """
        Estimate group velocity from phase velocity.
        
        Args:
            phase_vel: Phase velocity
            frequency_Hz: Frequency
        
        Returns:
            Group velocity
        """
        # Simplified: group velocity ≈ phase velocity for low dispersion
        return phase_vel * 0.95
    
    def modes_at_frequency(self, frequency_Hz: float,
                          num_modes: int = 3) -> List[WaveMode]:
        """
        Get modes at frequency.
        
        Args:
            frequency_Hz: Frequency
            num_modes: Number of modes
        
        Returns:
            Modes
        """
        fd = frequency_Hz * self.thickness * 1e-6
        modes = []
        
        for m in range(num_modes):
            cp = self.lamb_phase_velocity(fd, m)
            cg = self.group_velocity(cp, frequency_Hz)
            
            name = f"A{m}" if m % 2 == 0 else f"S{m}"
            modes.append(WaveMode(name, frequency_Hz, cp, cg, 0.1 * m))
        
        return modes


class ModeSelector:
    """
    Select optimal wave modes.
    """
    
    def __init__(self):
        pass
    
    def select_by_penetration(self, modes: List[WaveMode],
                             target_distance_m: float = 10.0) -> Optional[WaveMode]:
        """
        Select mode for maximum penetration.
        
        Args:
            modes: Available modes
            target_distance_m: Target distance
        
        Returns:
            Best mode
        """
        if not modes:
            return None
        
        # Minimize attenuation
        return min(modes, key=lambda m: m.attenuation_dB_m)
    
    def select_by_resolution(self, modes: List[WaveMode],
                            defect_size_mm: float = 5.0) -> Optional[WaveMode]:
        """
        Select mode for best resolution.
        
        Args:
            modes: Available modes
            defect_size_mm: Defect size
        
        Returns:
            Best mode
        """
        if not modes:
            return None
        
        # Higher frequency (shorter wavelength) = better resolution
        return max(modes, key=lambda m: m.frequency_Hz / m.phase_velocity_m_s)


class DefectReflector:
    """
    Analyze defect reflections in guided waves.
    """
    
    def __init__(self):
        pass
    
    def reflection_coefficient(self, defect_depth_mm: float,
                              wall_thickness_mm: float) -> float:
        """
        Compute reflection coefficient.
        
        Args:
            defect_depth_mm: Defect depth
            wall_thickness_mm: Wall thickness
        
        Returns:
            Reflection coefficient
        """
        if wall_thickness_mm <= 0:
            return 0.0
        
        ratio = defect_depth_mm / wall_thickness_mm
        return min(1.0, ratio * 0.5)
    
    def time_of_flight(self, distance_m: float,
                      group_velocity_m_s: float) -> float:
        """
        Compute time of flight.
        
        Args:
            distance_m: Distance
            group_velocity_m_s: Group velocity
        
        Returns:
            Time of flight in seconds
        """
        if group_velocity_m_s <= 0:
            return float('inf')
        return distance_m / group_velocity_m_s
    
    def locate_defect(self, time_of_flight_s: float,
                     group_velocity_m_s: float) -> float:
        """
        Locate defect from TOF.
        
        Args:
            time_of_flight_s: Time of flight
            group_velocity_m_s: Group velocity
        
        Returns:
            Distance in meters
        """
        return time_of_flight_s * group_velocity_m_s / 2.0


class GuidedWaveTesting:
    """
    Unified guided wave testing controller.
    """
    
    def __init__(self):
        self.dispersion = DispersionCalculator()
        self.selector = ModeSelector()
        self.reflector = DefectReflector()
        self.selected_mode: Optional[WaveMode] = None
        self.signals: List[Tuple[float, float]] = []
    
    def select_mode(self, frequency_Hz: float,
                   criterion: str = "penetration"):
        """
        Select mode.
        
        Args:
            frequency_Hz: Frequency
            criterion: Selection criterion
        """
        modes = self.dispersion.modes_at_frequency(frequency_Hz)
        
        if criterion == "penetration":
            self.selected_mode = self.selector.select_by_penetration(modes)
        elif criterion == "resolution":
            self.selected_mode = self.selector.select_by_resolution(modes)
        else:
            self.selected_mode = modes[0] if modes else None
    
    def inspect(self, distances_m: List[float],
               defect_depths_mm: List[float],
               wall_thickness_mm: float = 10.0):
        """
        Inspect pipe/plate.
        
        Args:
            distances_m: Distances
            defect_depths_mm: Defect depths
            wall_thickness_mm: Wall thickness
        """
        self.signals = []
        
        if self.selected_mode is None:
            return
        
        for dist, depth in zip(distances_m, defect_depths_mm):
            refl = self.reflector.reflection_coefficient(depth, wall_thickness_mm)
            tof = self.reflector.time_of_flight(dist, self.selected_mode.group_velocity_m_s)
            self.signals.append((refl, tof))
    
    def gwt_summary(self) -> Dict:
        """Get summary."""
        return {
            "mode": self.selected_mode.name if self.selected_mode else "none",
            "frequency_Hz": self.selected_mode.frequency_Hz if self.selected_mode else 0,
            "group_velocity_m_s": self.selected_mode.group_velocity_m_s if self.selected_mode else 0,
            "signals": len(self.signals)
        }
