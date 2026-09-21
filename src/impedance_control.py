"""
Impedance Control Module
Force-position interaction, admittance control,
compliance regulation, and contact stability for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ImpedanceParams:
    """Impedance parameters."""
    M: float  # Mass
    B: float  # Damping
    K: float  # Stiffness


class ImpedanceController:
    """
    Impedance controller for robot-environment interaction.
    """
    
    def __init__(self, params: ImpedanceParams):
        """
        Args:
            params: Impedance parameters
        """
        self.params = params
    
    def compute_force(self, position_error: float,
                     velocity_error: float,
                     acceleration_error: float = 0.0) -> float:
        """
        Compute desired interaction force.
        
        Args:
            position_error: Position deviation
            velocity_error: Velocity deviation
            acceleration_error: Acceleration deviation
        
        Returns:
            Force
        """
        p = self.params
        return (p.M * acceleration_error +
                p.B * velocity_error +
                p.K * position_error)
    
    def compute_acceleration(self, force: float,
                            position_error: float,
                            velocity_error: float) -> float:
        """
        Compute desired acceleration from force.
        
        Args:
            force: Desired force
            position_error: Position deviation
            velocity_error: Velocity deviation
        
        Returns:
            Acceleration
        """
        p = self.params
        if p.M <= 0:
            return 0.0
        return (force - p.B * velocity_error - p.K * position_error) / p.M
    
    def natural_frequency(self) -> float:
        """
        Compute natural frequency.
        
        Returns:
            Natural frequency in rad/s
        """
        if self.params.M <= 0:
            return 0.0
        return math.sqrt(self.params.K / self.params.M)
    
    def damping_ratio(self) -> float:
        """
        Compute damping ratio.
        
        Returns:
            Damping ratio
        """
        if self.params.M <= 0 or self.params.K <= 0:
            return 0.0
        return self.params.B / (2.0 * math.sqrt(self.params.M * self.params.K))


class AdmittanceController:
    """
    Admittance controller (dual of impedance).
    """
    
    def __init__(self, params: ImpedanceParams):
        """
        Args:
            params: Admittance parameters
        """
        self.params = params
    
    def compute_position(self, force: float,
                        dt: float,
                        current_position: float = 0.0,
                        current_velocity: float = 0.0) -> Tuple[float, float]:
        """
        Compute position update from measured force.
        
        Args:
            force: Measured force
            dt: Time step
            current_position: Current position
            current_velocity: Current velocity
        
        Returns:
            (new_position, new_velocity)
        """
        p = self.params
        if p.M <= 0:
            return current_position, current_velocity
        
        acceleration = (force - p.B * current_velocity - p.K * current_position) / p.M
        new_velocity = current_velocity + acceleration * dt
        new_position = current_position + new_velocity * dt
        
        return new_position, new_velocity


class ComplianceRegulator:
    """
    Compliance regulation for varying stiffness.
    """
    
    def __init__(self):
        pass
    
    def adaptive_stiffness(self, contact_force: float,
                          desired_force: float,
                          current_stiffness: float,
                          gain: float = 0.1) -> float:
        """
        Adapt stiffness based on force error.
        
        Args:
            contact_force: Measured force
            desired_force: Desired force
            current_stiffness: Current stiffness
            gain: Adaptation gain
        
        Returns:
            Updated stiffness
        """
        force_error = desired_force - contact_force
        new_stiffness = current_stiffness + gain * force_error
        return max(0.0, new_stiffness)
    
    def safety_limit(self, force: float,
                    max_force: float = 100.0) -> float:
        """
        Apply force safety limit.
        
        Args:
            force: Computed force
            max_force: Maximum allowed force
        
        Returns:
            Limited force
        """
        return max(-max_force, min(max_force, force))


class ContactStability:
    """
    Contact stability analysis.
    """
    
    def __init__(self):
        pass
    
    def stable_contact(self, params: ImpedanceParams,
                      environment_stiffness: float) -> bool:
        """
        Check if contact is stable.
        
        Args:
            params: Robot impedance
            environment_stiffness: Environment stiffness
        
        Returns:
            Whether stable
        """
        # Simplified: stable if robot stiffness < environment stiffness
        return params.K < environment_stiffness
    
    def passivity_margin(self, params: ImpedanceParams) -> float:
        """
        Compute passivity margin.
        
        Args:
            params: Impedance parameters
        
        Returns:
            Passivity margin (must be >= 0 for passive)
        """
        # For discrete-time: B >= K * dt / 2
        # Simplified: return damping ratio
        if params.M <= 0 or params.K <= 0:
            return -1.0
        return params.B / (2.0 * math.sqrt(params.M * params.K))


class ImpedanceControl:
    """
    Unified impedance control controller.
    """
    
    def __init__(self):
        self.impedance = None
        self.admittance = None
        self.compliance = ComplianceRegulator()
        self.stability = ContactStability()
    
    def set_params(self, M: float, B: float, K: float):
        """Set impedance parameters."""
        params = ImpedanceParams(M, B, K)
        self.impedance = ImpedanceController(params)
        self.admittance = AdmittanceController(params)
    
    def impedance_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["impedance", "admittance", "compliance", "stability"],
            "params": ["M", "B", "K"]
        }
