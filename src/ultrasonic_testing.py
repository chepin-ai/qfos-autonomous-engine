"""
Ultrasonic Testing Module
Pulse-echo, TOFD, phased array,
attenuation, flaw sizing, and velocity measurement for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class UTSignal:
    """Ultrasonic signal point."""
    time_us: float
    amplitude: float


class PulseEcho:
    """
    Pulse-echo ultrasonic testing.
    """
    
    def __init__(self, velocity_mm_us: float = 5.9):
        """
        Args:
            velocity_mm_us: Material sound velocity in mm/us
        """
        self.velocity = velocity_mm_us
    
    def thickness_from_tof(self, time_of_flight_us: float) -> float:
        """
        Compute thickness from time of flight.
        
        Args:
            time_of_flight_us: Round-trip time
        
        Returns:
            Thickness in mm
        """
        return self.velocity * time_of_flight_us / 2.0
    
    def tof_from_thickness(self, thickness_mm: float) -> float:
        """
        Compute time of flight from thickness.
        
        Args:
            thickness_mm: Thickness
        
        Returns:
            Round-trip time in us
        """
        if self.velocity <= 0:
            return 0.0
        return 2.0 * thickness_mm / self.velocity
    
    def flaw_depth(self, time_of_flight_us: float,
                   surface_tof_us: float = 0.0) -> float:
        """
        Compute flaw depth from echo time.
        
        Args:
            time_of_flight_us: Echo time
            surface_tof_us: Surface echo time offset
        
        Returns:
            Flaw depth in mm
        """
        return self.velocity * (time_of_flight_us - surface_tof_us) / 2.0
    
    def near_field_distance(self, diameter_mm: float,
                           wavelength_mm: float) -> float:
        """
        Compute near field (Fresnel) distance.
        
        Args:
            diameter_mm: Transducer diameter
            wavelength_mm: Wavelength
        
        Returns:
            Near field distance in mm
        """
        if wavelength_mm <= 0:
            return 0.0
        return diameter_mm ** 2 / (4.0 * wavelength_mm)
    
    def wavelength(self, frequency_MHz: float) -> float:
        """
        Compute wavelength.
        
        Args:
            frequency_MHz: Frequency
        
        Returns:
            Wavelength in mm
        """
        if frequency_MHz <= 0:
            return 0.0
        return self.velocity / frequency_MHz


class TOFDAnalyzer:
    """
    Time-of-Flight Diffraction analysis.
    """
    
    def __init__(self, velocity_mm_us: float = 5.9,
                 probe_separation_mm: float = 50.0):
        """
        Args:
            velocity_mm_us: Sound velocity
            probe_separation_mm: Probe separation
        """
        self.velocity = velocity_mm_us
        self.separation = probe_separation_mm
    
    def lateral_wave_tof(self) -> float:
        """
        Compute lateral wave time of flight.
        
        Returns:
            Time in us
        """
        if self.velocity <= 0:
            return 0.0
        return self.separation / self.velocity
    
    def backwall_tof(self, thickness_mm: float) -> float:
        """
        Compute backwall echo time of flight.
        
        Args:
            thickness_mm: Thickness
        
        Returns:
            Time in us
        """
        if self.velocity <= 0:
            return 0.0
        path = math.sqrt(self.separation ** 2 + (2.0 * thickness_mm) ** 2)
        return path / self.velocity
    
    def flaw_tof(self, depth_mm: float) -> float:
        """
        Compute flaw diffracted signal time of flight.
        
        Args:
            depth_mm: Flaw depth
        
        Returns:
            Time in us
        """
        if self.velocity <= 0:
            return 0.0
        path1 = math.sqrt((self.separation / 2.0) ** 2 + depth_mm ** 2)
        return 2.0 * path1 / self.velocity
    
    def flaw_height(self, top_tof_us: float,
                   bottom_tof_us: float) -> float:
        """
        Estimate flaw height from top and bottom diffraction signals.
        
        Args:
            top_tof_us: Top tip TOF
            bottom_tof_us: Bottom tip TOF
        
        Returns:
            Flaw height in mm
        """
        if self.velocity <= 0:
            return 0.0
        # Simplified: height from time difference
        dt = bottom_tof_us - top_tof_us
        return self.velocity * dt / 2.0


class PhasedArray:
    """
    Phased array ultrasonic testing.
    """
    
    def __init__(self, num_elements: int = 16,
                 pitch_mm: float = 1.0,
                 velocity_mm_us: float = 5.9):
        """
        Args:
            num_elements: Number of elements
            pitch_mm: Element pitch
            velocity_mm_us: Sound velocity
        """
        self.num_elements = num_elements
        self.pitch = pitch_mm
        self.velocity = velocity_mm_us
    
    def steering_angle(self, wavefront_delay_us: float) -> float:
        """
        Compute steering angle from element delays.
        
        Args:
            wavefront_delay_us: Delay between adjacent elements
        
        Returns:
            Steering angle in degrees
        """
        if self.velocity <= 0 or self.pitch <= 0:
            return 0.0
        sin_theta = self.velocity * wavefront_delay_us / self.pitch
        sin_theta = max(-1.0, min(1.0, sin_theta))
        return math.degrees(math.asin(sin_theta))
    
    def focal_distance(self, delays_us: List[float]) -> float:
        """
        Estimate focal distance from delay profile.
        
        Args:
            delays_us: Element delays
        
        Returns:
            Focal distance in mm
        """
        if not delays_us or self.velocity <= 0:
            return 0.0
        # Simplified: use maximum delay
        max_delay = max(abs(d) for d in delays_us)
        # Approximate focal distance
        aperture = self.num_elements * self.pitch
        return (aperture ** 2) / (8.0 * self.velocity * max_delay) if max_delay > 0 else float('inf')
    
    def aperture_size(self) -> float:
        """
        Compute total aperture size.
        
        Returns:
            Aperture in mm
        """
        return self.num_elements * self.pitch


class AttenuationAnalyzer:
    """
    Ultrasonic attenuation analysis.
    """
    
    def __init__(self):
        pass
    
    def attenuation_coefficient(self, initial_amplitude: float,
                                final_amplitude: float,
                                distance_mm: float) -> float:
        """
        Compute attenuation coefficient.
        
        Args:
            initial_amplitude: Initial amplitude
            final_amplitude: Final amplitude
            distance_mm: Distance
        
        Returns:
            Attenuation in dB/mm
        """
        if initial_amplitude <= 0 or final_amplitude <= 0 or distance_mm <= 0:
            return 0.0
        return 20.0 * math.log10(initial_amplitude / final_amplitude) / distance_mm
    
    def corrected_amplitude(self, amplitude: float,
                           attenuation_dB_mm: float,
                           distance_mm: float) -> float:
        """
        Apply attenuation correction.
        
        Args:
            amplitude: Measured amplitude
            attenuation_dB_mm: Attenuation coefficient
            distance_mm: Distance
        
        Returns:
            Corrected amplitude
        """
        loss_dB = attenuation_dB_mm * distance_mm
        linear_loss = 10.0 ** (loss_dB / 20.0)
        return amplitude * linear_loss


class UltrasonicTesting:
    """
    Unified ultrasonic testing controller.
    """
    
    def __init__(self):
        self.pulse_echo = PulseEcho()
        self.tofd = TOFDAnalyzer()
        self.phased_array = PhasedArray()
        self.attenuation = AttenuationAnalyzer()
    
    def ut_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["pulse_echo", "TOFD", "phased_array", "attenuation"],
            "velocity_mm_us": self.pulse_echo.velocity,
            "aperture_mm": self.phased_array.aperture_size()
        }
