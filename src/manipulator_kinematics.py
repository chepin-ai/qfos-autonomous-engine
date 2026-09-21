"""
Manipulator Kinematics Module
Forward kinematics, inverse kinematics,
DH parameters, Jacobian, and workspace analysis for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DHParameter:
    """Denavit-Hartenberg parameter."""
    theta: float
    d: float
    a: float
    alpha: float


@dataclass
class Pose3D:
    """3D pose."""
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float


class ForwardKinematics:
    """
    Forward kinematics for serial manipulators.
    """
    
    def __init__(self, dh_params: List[DHParameter]):
        """
        Args:
            dh_params: DH parameters for each joint
        """
        self.dh_params = dh_params
    
    def transformation_matrix(self, dh: DHParameter) -> List[List[float]]:
        """
        Compute transformation matrix from DH parameters.
        
        Args:
            dh: DH parameter
        
        Returns:
            4x4 transformation matrix
        """
        ct = math.cos(dh.theta)
        st = math.sin(dh.theta)
        ca = math.cos(dh.alpha)
        sa = math.sin(dh.alpha)
        
        return [
            [ct, -st * ca, st * sa, dh.a * ct],
            [st, ct * ca, -ct * sa, dh.a * st],
            [0.0, sa, ca, dh.d],
            [0.0, 0.0, 0.0, 1.0]
        ]
    
    def matrix_multiply(self, A: List[List[float]],
                       B: List[List[float]]) -> List[List[float]]:
        """
        Multiply two 4x4 matrices.
        
        Args:
            A: First matrix
            B: Second matrix
        
        Returns:
            Result
        """
        result = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += A[i][k] * B[k][j]
        return result
    
    def end_effector_pose(self, joint_angles: List[float]) -> Pose3D:
        """
        Compute end-effector pose from joint angles.
        
        Args:
            joint_angles: Joint angles in radians
        
        Returns:
            End-effector pose
        """
        T = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
        
        for i, dh in enumerate(self.dh_params):
            dh_joint = DHParameter(
                dh.theta + joint_angles[i],
                dh.d, dh.a, dh.alpha
            )
            T_i = self.transformation_matrix(dh_joint)
            T = self.matrix_multiply(T, T_i)
        
        # Extract position
        x = T[0][3]
        y = T[1][3]
        z = T[2][3]
        
        # Extract orientation (simplified roll, pitch, yaw)
        yaw = math.atan2(T[1][0], T[0][0])
        pitch = math.atan2(-T[2][0], math.sqrt(T[2][1] ** 2 + T[2][2] ** 2))
        roll = math.atan2(T[2][1], T[2][2])
        
        return Pose3D(x, y, z, roll, pitch, yaw)


class InverseKinematics:
    """
    Inverse kinematics for 2-DOF planar arm.
    """
    
    def __init__(self, link1_length: float = 1.0,
                 link2_length: float = 1.0):
        """
        Args:
            link1_length: Length of link 1
            link2_length: Length of link 2
        """
        self.l1 = link1_length
        self.l2 = link2_length
    
    def solve_2dof(self, x: float, y: float) -> List[Tuple[float, float]]:
        """
        Solve 2-DOF planar IK.
        
        Args:
            x: Target x
            y: Target y
        
        Returns:
            List of (theta1, theta2) solutions
        """
        d2 = x ** 2 + y ** 2
        d = math.sqrt(d2)
        
        if d > self.l1 + self.l2 or d < abs(self.l1 - self.l2):
            return []
        
        cos_theta2 = (d2 - self.l1 ** 2 - self.l2 ** 2) / (2.0 * self.l1 * self.l2)
        cos_theta2 = max(-1.0, min(1.0, cos_theta2))
        
        theta2_1 = math.acos(cos_theta2)
        theta2_2 = -theta2_1
        
        solutions = []
        for theta2 in [theta2_1, theta2_2]:
            k1 = self.l1 + self.l2 * math.cos(theta2)
            k2 = self.l2 * math.sin(theta2)
            theta1 = math.atan2(y, x) - math.atan2(k2, k1)
            solutions.append((theta1, theta2))
        
        return solutions


class JacobianCalculator:
    """
    Jacobian matrix calculation.
    """
    
    def __init__(self, link_lengths: List[float]):
        """
        Args:
            link_lengths: Link lengths
        """
        self.link_lengths = link_lengths
    
    def planar_jacobian(self, joint_angles: List[float]) -> List[List[float]]:
        """
        Compute 2-DOF planar Jacobian.
        
        Args:
            joint_angles: Joint angles
        
        Returns:
            2x2 Jacobian
        """
        theta1 = joint_angles[0]
        theta2 = joint_angles[1]
        l1 = self.link_lengths[0]
        l2 = self.link_lengths[1]
        
        J = [
            [-l1 * math.sin(theta1) - l2 * math.sin(theta1 + theta2),
             -l2 * math.sin(theta1 + theta2)],
            [l1 * math.cos(theta1) + l2 * math.cos(theta1 + theta2),
             l2 * math.cos(theta1 + theta2)]
        ]
        return J
    
    def manipulability(self, jacobian: List[List[float]]) -> float:
        """
        Compute Yoshikawa manipulability measure.
        
        Args:
            jacobian: Jacobian matrix
        
        Returns:
            Manipulability
        """
        # sqrt(det(J * J^T))
        # For 2x2: sqrt(det(J)^2) = |det(J)|
        det = jacobian[0][0] * jacobian[1][1] - jacobian[0][1] * jacobian[1][0]
        return abs(det)


class WorkspaceAnalyzer:
    """
    Robot workspace analysis.
    """
    
    def __init__(self, link_lengths: List[float]):
        """
        Args:
            link_lengths: Link lengths
        """
        self.link_lengths = link_lengths
    
    def reachable_radius(self) -> Tuple[float, float]:
        """
        Compute reachable workspace radius.
        
        Returns:
            (min_radius, max_radius)
        """
        total = sum(self.link_lengths)
        max_link = max(self.link_lengths)
        min_radius = max(0.0, max_link - (total - max_link))
        return (min_radius, total)
    
    def dexterous_workspace(self) -> float:
        """
        Compute dexterous workspace area.
        
        Returns:
            Area
        """
        min_r, max_r = self.reachable_radius()
        return math.pi * (max_r ** 2 - min_r ** 2)


class ManipulatorKinematics:
    """
    Unified manipulator kinematics controller.
    """
    
    def __init__(self):
        self.fk = None
        self.ik = InverseKinematics()
        self.jacobian = JacobianCalculator([1.0, 1.0])
        self.workspace = WorkspaceAnalyzer([1.0, 1.0])
    
    def set_dh_params(self, dh_params: List[DHParameter]):
        """
        Set DH parameters.
        
        Args:
            dh_params: DH parameters
        """
        self.fk = ForwardKinematics(dh_params)
    
    def mk_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["forward_kinematics", "inverse_kinematics", "jacobian", "workspace"],
            "dimensions": ["2D_planar", "3D_serial"]
        }
