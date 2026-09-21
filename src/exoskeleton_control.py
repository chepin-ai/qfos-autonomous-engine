"""
Exoskeleton Control Module
Gait assistance, impedance control,
interaction force estimation, and adaptive support for autonomous wearable robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class JointState:
    """Exoskeleton joint state."""
    angle_rad: float
    velocity_rad_s: float
    torque_Nm: float


class ImpedanceControl:
    """
    Impedance control for human-exoskeleton interaction.
    """
    
    def __init__(self, stiffness_Nm_rad: float = 100.0,
                 damping_Nms_rad: float = 10.0,
                 inertia_kgm2: float = 0.5):
        """
        Args:
            stiffness_Nm_rad: Stiffness
            damping_Nms_rad: Damping
            inertia_kgm2: Inertia
        """
        self.K = stiffness_Nm_rad
        self.B = damping_Nms_rad
        self.M = inertia_kgm2
    
    def desired_torque(self, position_error_rad: float,
                      velocity_error_rad_s: float,
                      acceleration_error_rad_s2: float = 0.0) -> float:
        """
        Compute desired torque from impedance law.
        
        Args:
            position_error_rad: Position error
            velocity_error_rad_s: Velocity error
            acceleration_error_rad_s2: Acceleration error
        
        Returns:
            Torque (Nm)
        """
        return (self.K * position_error_rad +
                self.B * velocity_error_rad_s +
                self.M * acceleration_error_rad_s2)
    
    def apparent_inertia(self) -> float:
        """
        Compute apparent inertia.
        
        Returns:
            Apparent inertia
        """
        return self.M


class GaitAssistance:
    """
    Gait phase detection and assistance torque.
    """
    
    def __init__(self):
        pass
    
    def gait_phase(self, hip_angle_rad: float,
                  thigh_angular_velocity_rad_s: float) -> str:
        """
        Detect gait phase.
        
        Args:
            hip_angle_rad: Hip angle
            thigh_angular_velocity_rad_s: Thigh angular velocity
        
        Returns:
            Phase name
        """
        if thigh_angular_velocity_rad_s > 0.5:
            return "swing"
        elif thigh_angular_velocity_rad_s < -0.5:
            return "stance_preparation"
        else:
            return "stance"
    
    def assistance_torque(self, gait_phase: str,
                         biological_torque_Nm: float,
                         assistance_ratio: float = 0.3) -> float:
        """
        Compute assistance torque.
        
        Args:
            gait_phase: Current phase
            biological_torque_Nm: Biological joint torque
            assistance_ratio: Assistance ratio
        
        Returns:
            Assistance torque (Nm)
        """
        if gait_phase == "swing":
            return 0.0  # No assistance during swing
        return assistance_ratio * biological_torque_Nm


class InteractionForceEstimation:
    """
    Estimate human-exoskeleton interaction force.
    """
    
    def __init__(self):
        pass
    
    def interaction_torque(self, motor_torque_Nm: float,
                          joint_acceleration_rad_s2: float,
                          exoskeleton_inertia_kgm2: float = 0.3) -> float:
        """
        Compute interaction torque.
        
        Args:
            motor_torque_Nm: Motor torque
            joint_acceleration_rad_s2: Joint acceleration
            exoskeleton_inertia_kgm2: Exoskeleton inertia
        
        Returns:
            Interaction torque (Nm)
        """
        return motor_torque_Nm - exoskeleton_inertia_kgm2 * joint_acceleration_rad_s2
    
    def interaction_power(self, interaction_torque_Nm: float,
                         joint_velocity_rad_s: float) -> float:
        """
        Compute interaction power.
        
        Args:
            interaction_torque_Nm: Interaction torque
            joint_velocity_rad_s: Joint velocity
        
        Returns:
            Power (W)
        """
        return interaction_torque_Nm * joint_velocity_rad_s


class AdaptiveSupport:
    """
    Adaptive support level based on user intent.
    """
    
    def __init__(self, max_assistance_ratio: float = 0.5):
        """
        Args:
            max_assistance_ratio: Maximum assistance
        """
        self.max_ratio = max_assistance_ratio
    
    def support_level(self, user_effort_Nm: float,
                     task_difficulty: float = 1.0) -> float:
        """
        Compute adaptive support ratio.
        
        Args:
            user_effort_Nm: User effort
            task_difficulty: Task difficulty
        
        Returns:
            Support ratio
        """
        if task_difficulty <= 0:
            return 0.0
        # More support when user effort is low relative to difficulty
        ratio = 1.0 - min(1.0, user_effort_Nm / (10.0 * task_difficulty))
        return min(self.max_ratio, ratio)
    
    def fatigue_compensation(self, time_on_task_s: float,
                            baseline_endurance_s: float = 300.0) -> float:
        """
        Increase support as user fatigues.
        
        Args:
            time_on_task_s: Time on task
            baseline_endurance_s: Baseline endurance
        
        Returns:
            Compensation factor
        """
        if baseline_endurance_s <= 0:
            return self.max_ratio
        fatigue = min(1.0, time_on_task_s / baseline_endurance_s)
        return self.max_ratio * fatigue


class ExoskeletonControl:
    """
    Unified exoskeleton control controller.
    """
    
    def __init__(self):
        self.impedance = ImpedanceControl()
        self.gait = GaitAssistance()
        self.interaction = InteractionForceEstimation()
        self.adaptive = AdaptiveSupport()
    
    def exoskeleton_summary(self) -> Dict:
        """Get summary."""
        return {
            "capabilities": ["impedance_control", "gait_assistance", "interaction_estimation", "adaptive_support"],
            "joints": ["hip", "knee", "ankle"]
        }
