"""
Manipulator Kinematics Module
DH parameters, forward kinematics, inverse kinematics,
Jacobian matrix, and workspace analysis for autonomous robotics.
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


class ForwardKinematics:
    """
    Forward kinematics for serial manipulators.
    """
    
    def __init__(self):
        pass
    
    def dh_transform(self, dh: DHParameter) -> List[List[float]]:
        """
        Compute DH transformation matrix.
        
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
    
    def multiply_matrices(self, a: List[List[float]],
                         b: List[List[float]]) -> List[List[float]]:
        """
        Multiply 4x4 matrices.
        
        Args:
            a: Matrix A
            b: Matrix B
        
        Returns:
            A * B
        """
        result = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += a[i][k] * b[k][j]
        return result
    
    def solve(self, dh_params: List[DHParameter]) -> List[List[float]]:
        """
        Compute end-effector pose.
        
        Args:
            dh_params: List of DH parameters
        
        Returns:
            End-effector transformation matrix
        """
        T = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
        
        for dh in dh_params:
            T_i = self.dh_transform(dh)
            T = self.multiply_matrices(T, T_i)
        
        return T
    
    def extract_position(self, T: List[List[float]]) -> Tuple[float, float, float]:
        """
        Extract position from transformation matrix.
        
        Args:
            T: Transformation matrix
        
        Returns:
            (x, y, z)
        """
        return (T[0][3], T[1][3], T[2][3])


class InverseKinematics:
    """
    Inverse kinematics for serial manipulators.
    """
    
    def __init__(self):
        pass
    
    def planar_2r(self, x: float, y: float,
                 link1_length: float,
                 link2_length: float) -> List[Tuple[float, float]]:
        """
        Solve 2R planar manipulator inverse kinematics.
        
        Args:
            x: Target x
            y: Target y
            link1_length: L1
            link2_length: L2
        
        Returns:
            List of (theta1, theta2) solutions
        """
        r = math.sqrt(x**2 + y**2)
        
        if r > link1_length + link2_length or r < abs(link1_length - link2_length):
            return []
        
        # Cosine law for theta2
        cos_theta2 = (r**2 - link1_length**2 - link2_length**2) / (2.0 * link1_length * link2_length)
        cos_theta2 = max(-1.0, min(1.0, cos_theta2))
        
        theta2_1 = math.acos(cos_theta2)
        theta2_2 = -math.acos(cos_theta2)
        
        solutions = []
        
        for theta2 in [theta2_1, theta2_2]:
            k1 = link1_length + link2_length * math.cos(theta2)
            k2 = link2_length * math.sin(theta2)
            
            theta1 = math.atan2(y, x) - math.atan2(k2, k1)
            solutions.append((theta1, theta2))
        
        return solutions


class JacobianCalculator:
    """
    Calculate Jacobian matrices.
    """
    
    def __init__(self):
        pass
    
    def planar_2r_jacobian(self, theta1: float,
                          theta2: float,
                          link1_length: float,
                          link2_length: float) -> List[List[float]]:
        """
        Compute 2R planar Jacobian.
        
        Args:
            theta1: Joint 1 angle
            theta2: Joint 2 angle
            link1_length: L1
            link2_length: L2
        
        Returns:
            2x2 Jacobian
        """
        s1 = math.sin(theta1)
        c1 = math.cos(theta1)
        s12 = math.sin(theta1 + theta2)
        c12 = math.cos(theta1 + theta2)
        
        J = [
            [-link1_length * s1 - link2_length * s12, -link2_length * s12],
            [link1_length * c1 + link2_length * c12, link2_length * c12]
        ]
        
        return J
    
    def determinant(self, J: List[List[float]]) -> float:
        """
        Compute determinant of 2x2 Jacobian.
        
        Args:
            J: Jacobian
        
        Returns:
            Determinant
        """
        if len(J) != 2 or len(J[0]) != 2:
            return 0.0
        return J[0][0] * J[1][1] - J[0][1] * J[1][0]


class WorkspaceAnalyzer:
    """
    Analyze manipulator workspace.
    """
    
    def __init__(self):
        pass
    
    def planar_2r_workspace(self, link1_length: float,
                           link2_length: float) -> Dict:
        """
        Compute 2R planar workspace.
        
        Args:
            link1_length: L1
            link2_length: L2
        
        Returns:
            Workspace bounds
        """
        r_max = link1_length + link2_length
        r_min = abs(link1_length - link2_length)
        
        return {
            "r_max": r_max,
            "r_min": r_min,
            "area": math.pi * (r_max**2 - r_min**2)
        }
    
    def is_reachable(self, x: float, y: float,
                    link1_length: float,
                    link2_length: float) -> bool:
        """
        Check if point is reachable.
        
        Args:
            x: Target x
            y: Target y
            link1_length: L1
            link2_length: L2
        
        Returns:
            True if reachable
        """
        r = math.sqrt(x**2 + y**2)
        r_max = link1_length + link2_length
        r_min = abs(link1_length - link2_length)
        return r_min <= r <= r_max


class ManipulatorKinematics:
    """
    Unified manipulator kinematics controller.
    """
    
    def __init__(self):
        self.fk = ForwardKinematics()
        self.ik = InverseKinematics()
        self.jacobian = JacobianCalculator()
        self.workspace = WorkspaceAnalyzer()
        self.dh_params: List[DHParameter] = []
    
    def set_dh_params(self, params: List[DHParameter]):
        """
        Set DH parameters.
        
        Args:
            params: DH parameters
        """
        self.dh_params = params
    
    def forward_solve(self) -> Dict:
        """
        Solve forward kinematics.
        
        Returns:
            End-effector pose
        """
        T = self.fk.solve(self.dh_params)
        pos = self.fk.extract_position(T)
        
        return {
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "transformation": T
        }
    
    def mk_summary(self) -> Dict:
        """Get summary."""
        return {
            "joints": len(self.dh_params),
            "methods": ["forward_kinematics", "inverse_kinematics", "jacobian", "workspace"]
        }
