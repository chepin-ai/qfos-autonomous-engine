"""
Force Control Module
Hybrid position/force control, admittance control,
force tracking, and contact detection for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ForceTorque:
    """Force/torque vector."""
    fx_N: float
    fy_N: float
    fz_N: float
    tx_Nm: float = 0.0
    ty_Nm: float = 0.0
    tz_Nm: float = 0.0


class HybridPositionForceControl:
    """
    Hybrid position/force control.
    """
    
    def __init__(self, position_gain: float = 100.0,
                 force_gain: float = 10.0):
        """
        Args:
            position_gain: Position control gain
            force_gain: Force control gain
        """
        self.Kp = position_gain
        self.Kf = force_gain
    
    def position_control(self, position_error_m: float) -> float:
        """
        Compute position control output.
        
        Args:
            position_error_m: Position error
        
        Returns:
            Velocity command
        """
        return self.Kp * position_error_m
    
    def force_control(self, force_error_N: float) -> float:
        """
        Compute force control output.
        
        Args:
            force_error_N: Force error
        
        Returns:
            Velocity command
        """
        return self.Kf * force_error_N
    
    def hybrid_command(self, position_error_m: float,
                      force_error_N: float,
                      direction: str = "position") -> float:
        """
        Compute hybrid command.
        
        Args:
            position_error_m: Position error
            force_error_N: Force error
            direction: "position" or "force"
        
        Returns:
            Command
        """
        if direction == "position":
            return self.position_control(position_error_m)
        return self.force_control(force_error_N)


class AdmittanceControl:
    """
    Admittance control for compliant interaction.
    """
    
    def __init__(self, mass_kg: float = 1.0,
                 damping_Ns_m: float = 10.0,
                 stiffness_N_m: float = 100.0):
        """
        Args:
            mass_kg: Virtual mass
            damping_Ns_m: Virtual damping
            stiffness_N_m: Virtual stiffness
        """
        self.M = mass_kg
        self.B = damping_Ns_m
        self.K = stiffness_N_m
    
    def desired_acceleration(self, force_error_N: float,
                            velocity_m_s: float = 0.0,
                            position_error_m: float = 0.0) -> float:
        """
        Compute desired acceleration from force error.
        
        Args:
            force_error_N: Force error
            velocity_m_s: Current velocity
            position_error_m: Position error
        
        Returns:
            Acceleration (m/s^2)
        """
        if self.M <= 0:
            return 0.0
        return (force_error_N - self.B * velocity_m_s - self.K * position_error_m) / self.M
    
    def apparent_stiffness(self) -> float:
        """
        Get apparent stiffness.
        
        Returns:
            Stiffness (N/m)
        """
        return self.K


class ForceTracking:
    """
    Force trajectory tracking.
    """
    
    def __init__(self):
        pass
    
    def ramp_force(self, time_s: float,
                  ramp_rate_N_s: float = 1.0,
                  max_force_N: float = 10.0) -> float:
        """
        Compute ramp force profile.
        
        Args:
            time_s: Time
            ramp_rate_N_s: Ramp rate
            max_force_N: Maximum force
        
        Returns:
            Desired force (N)
        """
        return min(max_force_N, ramp_rate_N_s * time_s)
    
    def sinusoidal_force(self, time_s: float,
                        amplitude_N: float = 5.0,
                        frequency_Hz: float = 1.0) -> float:
        """
        Compute sinusoidal force profile.
        
        Args:
            time_s: Time
            amplitude_N: Amplitude
            frequency_Hz: Frequency
        
        Returns:
            Desired force (N)
        """
        return amplitude_N * math.sin(2.0 * math.pi * frequency_Hz * time_s)
    
    def tracking_error(self, desired_N: float,
                      actual_N: float) -> float:
        """
        Compute tracking error.
        
        Args:
            desired_N: Desired force
            actual_N: Actual force
        
        Returns:
            Error (N)
        """
        return desired_N - actual_N


class ContactDetection:
    """
    Contact and collision detection.
    """
    
    def __init__(self, force_threshold_N: float = 1.0):
        """
        Args:
            force_threshold_N: Contact threshold
        """
        self.threshold = force_threshold_N
    
    def is_in_contact(self, measured_force_N: float) -> bool:
        """
        Detect contact.
        
        Args:
            measured_force_N: Measured force
        
        Returns:
            True if in contact
        """
        return abs(measured_force_N) > self.threshold
    
    def contact_force_magnitude(self, force: ForceTorque) -> float:
        """
        Compute contact force magnitude.
        
        Args:
            force: Force/torque
        
        Returns:
            Magnitude (N)
        """
        return math.sqrt(force.fx_N**2 + force.fy_N**2 + force.fz_N**2)
    
    def contact_normal(self, force: ForceTorque) -> Tuple[float, float, float]:
        """
        Estimate contact normal.
        
        Args:
            force: Force/torque
        
        Returns:
            Normal vector (nx, ny, nz)
        """
        mag = self.contact_force_magnitude(force)
        if mag <= 0:
            return (0.0, 0.0, 1.0)
        return (force.fx_N / mag, force.fy_N / mag, force.fz_N / mag)


class ForceControl:
    """
    Unified force control controller.
    """
    
    def __init__(self):
        self.hybrid = HybridPositionForceControl()
        self.admittance = AdmittanceControl()
        self.tracking = ForceTracking()
        self.contact = ContactDetection()
    
    def force_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["hybrid", "admittance", "force_tracking", "contact_detection"],
            "applications": ["assembly", "polishing", "grinding"]
        }
