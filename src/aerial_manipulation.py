"""
Aerial Manipulation Module
UAV with robotic arm, wrench estimation,
compliance control, and stability for autonomous aerial robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class UAVState:
    """UAV position and orientation."""
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float


class AerialArmKinematics:
    """
    Kinematics for UAV-mounted manipulator.
    """
    
    def __init__(self, arm_length_m: float = 0.5):
        """
        Args:
            arm_length_m: Arm length
        """
        self.L = arm_length_m
    
    def end_effector_position(self, uav: UAVState,
                             joint_angles: List[float]) -> Tuple[float, float, float]:
        """
        Compute end-effector position in world frame.
        
        Args:
            uav: UAV state
            joint_angles: Joint angles
        
        Returns:
            (x, y, z) position
        """
        # Simplified: arm extends along UAV body x
        arm_x = self.L * math.cos(joint_angles[0]) if joint_angles else self.L
        arm_z = -self.L * math.sin(joint_angles[0]) if joint_angles else 0.0
        
        # Rotate by UAV yaw
        cy = math.cos(uav.yaw)
        sy = math.sin(uav.yaw)
        
        x = uav.x + arm_x * cy
        y = uav.y + arm_x * sy
        z = uav.z + arm_z
        
        return x, y, z
    
    def jacobian(self, joint_angles: List[float]) -> List[List[float]]:
        """
        Compute simplified Jacobian.
        
        Args:
            joint_angles: Joint angles
        
        Returns:
            Jacobian matrix
        """
        if not joint_angles:
            return [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        
        theta = joint_angles[0]
        return [[-self.L * math.sin(theta), 0.0],
                [0.0, 0.0],
                [-self.L * math.cos(theta), 0.0]]


class WrenchEstimation:
    """
    Estimate external wrench on aerial manipulator.
    """
    
    def __init__(self):
        pass
    
    def force_from_acceleration(self, mass_kg: float,
                               acceleration_m_s2: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Compute force from acceleration deviation.
        
        Args:
            mass_kg: Mass
            acceleration_m_s2: Acceleration
        
        Returns:
            Force (N)
        """
        return (mass_kg * acceleration_m_s2[0],
                mass_kg * acceleration_m_s2[1],
                mass_kg * acceleration_m_s2[2])
    
    def torque_from_angular_accel(self, inertia_kg_m2: float,
                                 angular_accel_rad_s2: float) -> float:
        """
        Compute torque from angular acceleration.
        
        Args:
            inertia_kg_m2: Moment of inertia
            angular_accel_rad_s2: Angular acceleration
        
        Returns:
            Torque (Nm)
        """
        return inertia_kg_m2 * angular_accel_rad_s2


class AerialCompliance:
    """
    Compliance control for aerial manipulation.
    """
    
    def __init__(self, stiffness_N_m: float = 100.0):
        """
        Args:
            stiffness_N_m: Stiffness
        """
        self.k = stiffness_N_m
    
    def compliant_displacement(self, force_N: float) -> float:
        """
        Compute displacement under force.
        
        Args:
            force_N: Applied force
        
        Returns:
            Displacement (m)
        """
        if self.k <= 0:
            return 0.0
        return force_N / self.k
    
    def damping_force(self, velocity_m_s: float,
                     damping_Ns_m: float = 10.0) -> float:
        """
        Compute damping force.
        
        Args:
            velocity_m_s: Velocity
            damping_Ns_m: Damping coefficient
        
        Returns:
            Damping force (N)
        """
        return damping_Ns_m * velocity_m_s


class AerialStability:
    """
    Stability analysis for aerial manipulation.
    """
    
    def __init__(self):
        pass
    
    def center_of_mass_shift(self, arm_mass_kg: float,
                            arm_extension_m: float,
                            uav_mass_kg: float) -> float:
        """
        Compute COM shift due to arm extension.
        
        Args:
            arm_mass_kg: Arm mass
            arm_extension_m: Arm extension
            uav_mass_kg: UAV mass
        
        Returns:
            COM shift (m)
        """
        total_mass = arm_mass_kg + uav_mass_kg
        if total_mass <= 0:
            return 0.0
        return arm_mass_kg * arm_extension_m / total_mass
    
    def stability_margin(self, max_thrust_N: float,
                        total_weight_N: float,
                        com_offset_m: float) -> float:
        """
        Compute stability margin.
        
        Args:
            max_thrust_N: Maximum thrust
            total_weight_N: Total weight
            com_offset_m: COM offset
        
        Returns:
            Margin (m)
        """
        if total_weight_N <= 0:
            return 0.0
        # Simplified: thrust margin allows tilt
        max_tilt = math.acos(total_weight_N / max_thrust_N) if max_thrust_N > total_weight_N else 0.0
        return com_offset_m * math.tan(max_tilt)


class AerialManipulation:
    """
    Unified aerial manipulation controller.
    """
    
    def __init__(self):
        self.kinematics = AerialArmKinematics()
        self.wrench = WrenchEstimation()
        self.compliance = AerialCompliance()
        self.stability = AerialStability()
    
    def aerial_summary(self) -> Dict:
        """Get summary."""
        return {
            "capabilities": ["kinematics", "wrench_estimation", "compliance", "stability"],
            "platforms": ["UAV", "drone"]
        }
