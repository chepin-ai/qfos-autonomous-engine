"""
Compliance Control Module
Impedance control, admittance control, stiffness, damping,
and interaction force regulation for autonomous robotic manipulation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ControlMode(Enum):
    """Compliance control modes."""
    IMPEDANCE = "impedance"
    ADMITTANCE = "admittance"
    HYBRID = "hybrid"


@dataclass
class CartesianState:
    """Cartesian position and force state."""
    position: Tuple[float, float, float]
    velocity: Tuple[float, float, float]
    force: Tuple[float, float, float] = (0.0, 0.0, 0.0)


class ImpedanceController:
    """
    Impedance controller: F = M*(xdd - xdd_des) + B*(xd - xd_des) + K*(x - x_des)
    """
    
    def __init__(self, mass_kg: float = 1.0,
                 damping_Ns_m: float = 10.0,
                 stiffness_N_m: float = 100.0):
        """
        Args:
            mass_kg: Desired mass
            damping_Ns_m: Desired damping
            stiffness_N_m: Desired stiffness
        """
        self.M = mass_kg
        self.B = damping_Ns_m
        self.K = stiffness_N_m
    
    def compute_force(self, position: float, velocity: float,
                     desired_position: float = 0.0,
                     desired_velocity: float = 0.0,
                     desired_acceleration: float = 0.0) -> float:
        """
        Compute desired interaction force.
        
        Args:
            position: Current position
            velocity: Current velocity
            desired_position: Target position
            desired_velocity: Target velocity
            desired_acceleration: Target acceleration
        
        Returns:
            Force command
        """
        pos_err = position - desired_position
        vel_err = velocity - desired_velocity
        
        force = (self.M * (-desired_acceleration) +
                self.B * vel_err +
                self.K * pos_err)
        
        return force
    
    def natural_frequency(self) -> float:
        """
        Compute natural frequency.
        
        Returns:
            omega_n in rad/s
        """
        if self.M <= 0:
            return 0.0
        return math.sqrt(self.K / self.M)
    
    def damping_ratio(self) -> float:
        """
        Compute damping ratio.
        
        Returns:
            Zeta
        """
        omega_n = self.natural_frequency()
        if omega_n == 0:
            return 1.0
        return self.B / (2.0 * self.M * omega_n)


class AdmittanceController:
    """
    Admittance controller: x = (1/K) * F + (1/B) * integral(F) + (1/M) * double_integral(F)
    """
    
    def __init__(self, mass_kg: float = 1.0,
                 damping_Ns_m: float = 10.0,
                 stiffness_N_m: float = 100.0,
                 dt: float = 0.001):
        """
        Args:
            mass_kg: Virtual mass
            damping_Ns_m: Virtual damping
            stiffness_N_m: Virtual stiffness
            dt: Time step
        """
        self.M = mass_kg
        self.B = damping_Ns_m
        self.K = stiffness_N_m
        self.dt = dt
        self.position = 0.0
        self.velocity = 0.0
    
    def update(self, force: float) -> Tuple[float, float]:
        """
        Update position based on external force.
        
        Args:
            force: External force
        
        Returns:
            New position and velocity
        """
        # M*xdd + B*xd + K*x = F
        # xdd = (F - B*xd - K*x) / M
        if self.M <= 0:
            return self.position, self.velocity
        
        acceleration = (force - self.B * self.velocity - self.K * self.position) / self.M
        self.velocity += acceleration * self.dt
        self.position += self.velocity * self.dt
        
        return self.position, self.velocity
    
    def reset(self, position: float = 0.0, velocity: float = 0.0):
        """Reset state."""
        self.position = position
        self.velocity = velocity


class StiffnessRegulator:
    """
    Variable stiffness regulator.
    """
    
    def __init__(self, min_stiffness: float = 10.0,
                 max_stiffness: float = 1000.0):
        """
        Args:
            min_stiffness: Minimum stiffness
            max_stiffness: Maximum stiffness
        """
        self.k_min = min_stiffness
        self.k_max = max_stiffness
    
    def from_force(self, desired_force: float,
                  displacement: float) -> float:
        """
        Compute stiffness from desired force and displacement.
        
        Args:
            desired_force: Target force
            displacement: Expected displacement
        
        Returns:
            Stiffness value
        """
        if abs(displacement) < 1e-6:
            return self.k_max
        k = abs(desired_force / displacement)
        return max(self.k_min, min(self.k_max, k))
    
    def from_safety(self, force_limit: float,
                   max_displacement: float) -> float:
        """
        Compute safety stiffness.
        
        Args:
            force_limit: Maximum force
            max_displacement: Maximum displacement
        
        Returns:
            Safety stiffness
        """
        if max_displacement <= 0:
            return self.k_max
        k = force_limit / max_displacement
        return max(self.k_min, min(self.k_max, k))


class DampingRegulator:
    """
    Damping coefficient regulator.
    """
    
    def __init__(self, min_damping: float = 1.0,
                 max_damping: float = 100.0):
        """
        Args:
            min_damping: Minimum damping
            max_damping: Maximum damping
        """
        self.b_min = min_damping
        self.b_max = max_damping
    
    def critical_damping(self, mass: float, stiffness: float) -> float:
        """
        Compute critical damping.
        
        Args:
            mass: Mass
            stiffness: Stiffness
        
        Returns:
            Critical damping
        """
        return 2.0 * math.sqrt(mass * stiffness)
    
    def optimal_damping(self, mass: float, stiffness: float,
                       damping_ratio: float = 0.7) -> float:
        """
        Compute damping for desired damping ratio.
        
        Args:
            mass: Mass
            stiffness: Stiffness
            damping_ratio: Target zeta
        
        Returns:
            Damping value
        """
        b = damping_ratio * self.critical_damping(mass, stiffness)
        return max(self.b_min, min(self.b_max, b))


class ComplianceControl:
    """
    Unified compliance control controller.
    """
    
    def __init__(self):
        self.impedance = ImpedanceController()
        self.admittance = AdmittanceController()
        self.stiffness = StiffnessRegulator()
        self.damping = DampingRegulator()
        self.mode = ControlMode.IMPEDANCE
    
    def set_mode(self, mode: ControlMode):
        """Set control mode."""
        self.mode = mode
    
    def control(self, position: float, velocity: float,
               external_force: float,
               desired_position: float = 0.0) -> float:
        """
        Compute control output.
        
        Args:
            position: Current position
            velocity: Current velocity
            external_force: Measured force
            desired_position: Target position
        
        Returns:
            Control command
        """
        if self.mode == ControlMode.IMPEDANCE:
            return self.impedance.compute_force(position, velocity, desired_position)
        elif self.mode == ControlMode.ADMITTANCE:
            self.admittance.update(external_force)
            return self.admittance.position
        else:
            return 0.0
    
    def compliance_summary(self) -> Dict:
        """Get compliance summary."""
        return {
            "mode": self.mode.value,
            "mass": self.impedance.M,
            "stiffness": self.impedance.K,
            "damping": self.impedance.B,
            "natural_freq_hz": self.impedance.natural_frequency() / (2.0 * math.pi),
            "damping_ratio": self.impedance.damping_ratio()
        }
