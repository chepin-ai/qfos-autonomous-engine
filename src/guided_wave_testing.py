"""
Guided Wave Testing Module
Lamb waves, shear horizontal waves, dispersion curves,
and defect localization for autonomous long-range NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class WaveMode(Enum):
    """Guided wave modes."""
    LAMB_SYMMETRIC = "A0/S0"
    LAMB_ANTISYMMETRIC = "A0"
    SHEAR_HORIZONTAL = "SH"
    TORSIONAL = "T"


@dataclass
class GuidedWaveSignal:
    """Guided wave signal."""
    time_us: float
    amplitude: float
    frequency_MHz: float
    mode: WaveMode
    group_velocity_mm_us: float = 0.0


class DispersionCurve:
    """
    Dispersion curve for guided waves.
    """
    
    def __init__(self, thickness_mm: float = 5.0,
                 material_velocity_mm_us: float = 5.9):
        """
        Args:
            thickness_mm: Plate thickness
            material_velocity_mm_us: Material velocity
        """
        self.thickness = thickness_mm
        self.c_l = material_velocity_mm_us
        self.c_t = material_velocity_mm_us * 0.6  # Transverse velocity
    
    def lamb_wave_velocity(self, frequency_MHz: float,
                          mode: str = "A0") -> float:
        """
        Compute Lamb wave group velocity.
        
        Args:
            frequency_MHz: Frequency
            mode: "A0" or "S0"
        
        Returns:
            Group velocity mm/us
        """
        fd = frequency_MHz * self.thickness  # Frequency-thickness product
        
        # Simplified approximation
        if mode == "A0":
            # A0 mode: lower velocity at low fd
            return self.c_t * math.tanh(fd / 10.0)
        elif mode == "S0":
            # S0 mode: approaches plate velocity
            return self.c_l * (1.0 - 0.5 * math.exp(-fd / 5.0))
        else:
            return self.c_t
    
    def phase_velocity(self, frequency_MHz: float,
                      mode: str = "A0") -> float:
        """
        Compute phase velocity.
        
        Args:
            frequency_MHz: Frequency
            mode: Mode
        
        Returns:
            Phase velocity
        """
        vg = self.lamb_wave_velocity(frequency_MHz, mode)
        # Simplified: vp ~ vg for low dispersion
        return vg * 1.1
    
    def wavelength_mm(self, frequency_MHz: float,
                     velocity_mm_us: float) -> float:
        """
        Compute wavelength.
        
        Args:
            frequency_MHz: Frequency
            velocity_mm_us: Velocity
        
        Returns:
            Wavelength
        """
        return velocity_mm_us / frequency_MHz


class WaveTransducer:
    """
    Guided wave transducer.
    """
    
    def __init__(self, transducer_id: int,
                 position_mm: float,
                 angle_deg: float = 0.0):
        """
        Args:
            transducer_id: ID
            position_mm: Position
            angle_deg: Wedge angle
        """
        self.transducer_id = transducer_id
        self.position = position_mm
        self.angle = angle_deg
    
    def excite(self, frequency_MHz: float,
              amplitude: float = 1.0,
              cycles: int = 5) -> List[GuidedWaveSignal]:
        """
        Generate toneburst excitation.
        
        Args:
            frequency_MHz: Frequency
            amplitude: Amplitude
            cycles: Cycles
        
        Returns:
            Signal train
        """
        period_us = 1.0 / frequency_MHz
        signals = []
        
        for i in range(cycles):
            t = i * period_us
            amp = amplitude * math.sin(2.0 * math.pi * frequency_MHz * t)
            signals.append(GuidedWaveSignal(
                time_us=t,
                amplitude=amp,
                frequency_MHz=frequency_MHz,
                mode=WaveMode.LAMB_SYMMETRIC
            ))
        
        return signals


class DefectLocalizer:
    """
    Defect localization from guided wave signals.
    """
    
    def __init__(self, transducer_positions_mm: List[float]):
        """
        Args:
            transducer_positions_mm: Transducer positions
        """
        self.positions = transducer_positions_mm
    
    def time_of_flight(self, distance_mm: float,
                      velocity_mm_us: float) -> float:
        """
        Compute time of flight.
        
        Args:
            distance_mm: Distance
            velocity_mm_us: Velocity
        
        Returns:
            Time of flight
        """
        if velocity_mm_us <= 0:
            return 0.0
        return distance_mm / velocity_mm_us
    
    def localize_1d(self, tof_us: float,
                   velocity_mm_us: float,
                   exciter_pos_mm: float) -> List[float]:
        """
        1D defect localization.
        
        Args:
            tof_us: Time of flight
            velocity_mm_us: Velocity
            exciter_pos_mm: Exciter position
        
        Returns:
            Possible defect positions
        """
        distance = tof_us * velocity_mm_us / 2.0  # Round trip
        return [exciter_pos_mm + distance, exciter_pos_mm - distance]
    
    def triangulate(self, tofs_us: List[float],
                   velocities_mm_us: List[float],
                   transducer_indices: List[int]) -> Tuple[float, float]:
        """
        Triangulate defect position.
        
        Args:
            tofs_us: Times of flight
            velocities_mm_us: Velocities
            transducer_indices: Transducer indices
        
        Returns:
            (x, y) position
        """
        if not tofs_us or not transducer_indices:
            return (0.0, 0.0)
        
        # Simplified: average position weighted by distance
        x_sum = 0.0
        y_sum = 0.0
        
        for tof, vel, idx in zip(tofs_us, velocities_mm_us, transducer_indices):
            if idx < len(self.positions):
                dist = tof * vel / 2.0
                x_sum += self.positions[idx]
                y_sum += dist
        
        n = len(tofs_us)
        return (x_sum / n, y_sum / n)


class GuidedWaveTesting:
    """
    Unified guided wave testing controller.
    """
    
    def __init__(self, thickness_mm: float = 5.0):
        """
        Args:
            thickness_mm: Plate thickness
        """
        self.dispersion = DispersionCurve(thickness_mm)
        self.transducers: List[WaveTransducer] = []
        self.localizer: Optional[DefectLocalizer] = None
        self.signals: List[GuidedWaveSignal] = []
        self.defects: List[Dict] = []
    
    def add_transducer(self, position_mm: float, angle_deg: float = 0.0):
        """
        Add transducer.
        
        Args:
            position_mm: Position
            angle_deg: Angle
        """
        tid = len(self.transducers)
        self.transducers.append(WaveTransducer(tid, position_mm, angle_deg))
        self.localizer = DefectLocalizer([t.position for t in self.transducers])
    
    def excite(self, transducer_id: int,
              frequency_MHz: float,
              amplitude: float = 1.0) -> List[GuidedWaveSignal]:
        """
        Excite guided wave.
        
        Args:
            transducer_id: Transducer
            frequency_MHz: Frequency
            amplitude: Amplitude
        
        Returns:
            Signals
        """
        if transducer_id >= len(self.transducers):
            return []
        
        signals = self.transducers[transducer_id].excite(frequency_MHz, amplitude)
        self.signals.extend(signals)
        return signals
    
    def analyze(self, tof_us: float,
               frequency_MHz: float,
               mode: str = "A0") -> Dict:
        """
        Analyze signal.
        
        Args:
            tof_us: Time of flight
            frequency_MHz: Frequency
            mode: Mode
        
        Returns:
            Analysis report
        """
        velocity = self.dispersion.lamb_wave_velocity(frequency_MHz, mode)
        wavelength = self.dispersion.wavelength_mm(frequency_MHz, velocity)
        
        # Estimate distance
        distance_mm = tof_us * velocity / 2.0
        
        report = {
            "velocity_mm_us": velocity,
            "wavelength_mm": wavelength,
            "distance_mm": distance_mm,
            "mode": mode
        }
        return report
    
    def gwut_summary(self) -> Dict:
        """Get GWUT summary."""
        return {
            "transducers": len(self.transducers),
            "thickness_mm": self.dispersion.thickness,
            "signals": len(self.signals),
            "defects": len(self.defects)
        }
