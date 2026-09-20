"""
Manipulator Kinematics Module
Forward/inverse kinematics, Jacobian, workspace, and
singularity detection for autonomous robotic manipulation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class JointType(Enum):
    """Robot joint type."""
    REVOLUTE = "revolute"
    PRISMATIC = "prismatic"


@dataclass
class DHParameter:
    """Denavit-Hartenberg parameter."""
    theta: float  # Joint angle
    d: float      # Link offset
    a: float      # Link length
    alpha: float  # Link twist
    joint_type: JointType = JointType.REVOLUTE


class ForwardKinematics:
    """
    Forward kinematics solver.
    """
    
    def __init__(self, dh_params: List[DHParameter]):
        """
        Args:
            dh_params: DH parameters for each link
        """
        self.dh = dh_params
    
    def dh_transform(self, params: DHParameter,
                    joint_angle: float) -> List[List[float]]:
        """
        Compute DH transformation matrix.
        
        Args:
            params: DH parameters
            joint_angle: Joint angle
        
        Returns:
            4x4 transformation matrix
        """
        if params.joint_type == JointType.REVOLUTE:
            theta = joint_angle
            d = params.d
        else:
            theta = params.theta
            d = joint_angle
        
        a = params.a
        alpha = params.alpha
        
        ct = math.cos(theta)
        st = math.sin(theta)
        ca = math.cos(alpha)
        sa = math.sin(alpha)
        
        return [
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0, sa, ca, d],
            [0, 0, 0, 1]
        ]
    
    def solve(self, joint_angles: List[float]) -> Tuple[float, float, float]:
        """
        Compute end-effector position.
        
        Args:
            joint_angles: Joint angles
        
        Returns:
            (x, y, z) position
        """
        T = [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 1]]
        
        for i, params in enumerate(self.dh):
            angle = joint_angles[i] if i < len(joint_angles) else 0.0
            T_i = self.dh_transform(params, angle)
            T = self._mat_mult(T, T_i)
        
        return (T[0][3], T[1][3], T[2][3])
    
    def _mat_mult(self, A: List[List[float]],
                 B: List[List[float]]) -> List[List[float]]:
        """Multiply 4x4 matrices."""
        result = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += A[i][k] * B[k][j]
        return result


class InverseKinematics:
    """
    Inverse kinematics solver (simplified 2-DOF planar).
    """
    
    def __init__(self, link_lengths: List[float]):
        """
        Args:
            link_lengths: Link lengths
        """
        self.lengths = link_lengths
    
    def solve_2dof(self, target_x: float,
                  target_y: float) -> List[Tuple[float, float]]:
        """
        Solve 2-DOF planar arm.
        
        Args:
            target_x, target_y: Target position
        
        Returns:
            List of (theta1, theta2) solutions
        """
        if len(self.lengths) < 2:
            return []
        
        l1 = self.lengths[0]
        l2 = self.lengths[1]
        
        r2 = target_x**2 + target_y**2
        r = math.sqrt(r2)
        
        # Check reachability
        if r > l1 + l2 or r < abs(l1 - l2):
            return []
        
        # Cosine law
        cos_theta2 = (r2 - l1**2 - l2**2) / (2 * l1 * l2)
        cos_theta2 = max(-1.0, min(1.0, cos_theta2))
        
        theta2_1 = math.acos(cos_theta2)
        theta2_2 = -theta2_1
        
        solutions = []
        
        for theta2 in [theta2_1, theta2_2]:
            k1 = l1 + l2 * math.cos(theta2)
            k2 = l2 * math.sin(theta2)
            
            theta1 = math.atan2(target_y, target_x) - math.atan2(k2, k1)
            solutions.append((theta1, theta2))
        
        return solutions
    
    def reachable(self, target_x: float, target_y: float) -> bool:
        """
        Check if target is reachable.
        
        Args:
            target_x, target_y: Target position
        
        Returns:
            True if reachable
        """
        if len(self.lengths) < 2:
            return False
        
        l1 = self.lengths[0]
        l2 = self.lengths[1]
        r = math.sqrt(target_x**2 + target_y**2)
        
        return abs(l1 - l2) <= r <= l1 + l2


class JacobianCalculator:
    """
    Compute manipulator Jacobian.
    """
    
    def __init__(self, link_lengths: List[float]):
        self.lengths = link_lengths
    
    def compute_2dof(self, theta1: float, theta2: float) -> List[List[float]]:
        """
        Compute 2-DOF Jacobian.
        
        Args:
            theta1, theta2: Joint angles
        
        Returns:
            2x2 Jacobian matrix
        """
        l1 = self.lengths[0]
        l2 = self.lengths[1]
        
        # dx/dtheta1, dx/dtheta2
        # dy/dtheta1, dy/dtheta2
        J = [
            [-l1 * math.sin(theta1) - l2 * math.sin(theta1 + theta2),
             -l2 * math.sin(theta1 + theta2)],
            [l1 * math.cos(theta1) + l2 * math.cos(theta1 + theta2),
             l2 * math.cos(theta1 + theta2)]
        ]
        
        return J
    
    def determinant(self, J: List[List[float]]) -> float:
        """
        Compute Jacobian determinant.
        
        Args:
            J: Jacobian matrix
        
        Returns:
            Determinant
        """
        if len(J) == 2 and len(J[0]) == 2:
            return J[0][0] * J[1][1] - J[0][1] * J[1][0]
        return 0.0
    
    def manipulability(self, J: List[List[float]]) -> float:
        """
        Compute Yoshikawa manipulability.
        
        Args:
            J: Jacobian matrix
        
        Returns:
            Manipulability measure
        """
        det = self.determinant(J)
        return math.sqrt(abs(det))


class WorkspaceAnalyzer:
    """
    Analyze manipulator workspace.
    """
    
    def __init__(self, link_lengths: List[float]):
        self.lengths = link_lengths
    
    def reach(self) -> Tuple[float, float]:
        """
        Compute workspace reach.
        
        Returns:
            (min_reach, max_reach)
        """
        if not self.lengths:
            return (0.0, 0.0)
        
        total = sum(self.lengths)
        max_len = max(self.lengths)
        others_sum = total - max_len
        min_reach = max(0.0, max_len - others_sum)
        
        return (min_reach, total)
    
    def is_in_workspace(self, x: float, y: float) -> bool:
        """
        Check if point is in workspace.
        
        Args:
            x, y: Point coordinates
        
        Returns:
            True if in workspace
        """
        r = math.sqrt(x**2 + y**2)
        min_r, max_r = self.reach()
        return min_r <= r <= max_r
    
    def sample_workspace(self, num_samples: int = 100) -> List[Tuple[float, float]]:
        """
        Sample workspace boundary.
        
        Args:
            num_samples: Number of samples
        
        Returns:
            Boundary points
        """
        points = []
        _, max_r = self.reach()
        
        for i in range(num_samples):
            angle = 2.0 * math.pi * i / num_samples
            x = max_r * math.cos(angle)
            y = max_r * math.sin(angle)
            points.append((x, y))
        
        return points


class SingularityDetector:
    """
    Detect kinematic singularities.
    """
    
    def __init__(self, threshold: float = 0.01):
        """
        Args:
            threshold: Determinant threshold
        """
        self.threshold = threshold
    
    def check(self, J: List[List[float]]) -> bool:
        """
        Check if near singularity.
        
        Args:
            J: Jacobian matrix
        
        Returns:
            True if singular
        """
        if len(J) == 2 and len(J[0]) == 2:
            det = J[0][0] * J[1][1] - J[0][1] * J[1][0]
            return abs(det) < self.threshold
        return False
    
    def condition_number(self, J: List[List[float]]) -> float:
        """
        Compute condition number.
        
        Args:
            J: Jacobian matrix
        
        Returns:
            Condition number
        """
        if len(J) == 2 and len(J[0]) == 2:
            # Simplified: ratio of eigenvalues
            a, b, c, d = J[0][0], J[0][1], J[1][0], J[1][1]
            trace = a + d
            det = a * d - b * c
            
            if det == 0:
                return float('inf')
            
            disc = trace**2 - 4 * det
            if disc < 0:
                disc = 0
            
            lambda1 = abs((trace + math.sqrt(disc)) / 2.0)
            lambda2 = abs((trace - math.sqrt(disc)) / 2.0)
            
            if lambda2 == 0:
                return float('inf')
            
            return max(lambda1, lambda2) / min(lambda1, lambda2)
        
        return float('inf')


class ManipulatorKinematics:
    """
    Unified manipulator kinematics controller.
    """
    
    def __init__(self, link_lengths: List[float] = [0.3, 0.3]):
        self.link_lengths = link_lengths
        self.fk = ForwardKinematics([
            DHParameter(0, 0, link_lengths[0], 0),
            DHParameter(0, 0, link_lengths[1], 0)
        ])
        self.ik = InverseKinematics(link_lengths)
        self.jacobian = JacobianCalculator(link_lengths)
        self.workspace = WorkspaceAnalyzer(link_lengths)
        self.singularity = SingularityDetector()
    
    def forward(self, joint_angles: List[float]) -> Tuple[float, float, float]:
        """Compute forward kinematics."""
        return self.fk.solve(joint_angles)
    
    def inverse(self, target: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Compute inverse kinematics."""
        return self.ik.solve_2dof(target[0], target[1])
    
    def check_singularity(self, joint_angles: List[float]) -> bool:
        """Check if configuration is singular."""
        if len(joint_angles) < 2:
            return False
        J = self.jacobian.compute_2dof(joint_angles[0], joint_angles[1])
        return self.singularity.check(J)
    
    def kinematic_summary(self) -> Dict:
        """Get kinematic summary."""
        min_r, max_r = self.workspace.reach()
        return {
            "dof": len(self.link_lengths),
            "min_reach": min_r,
            "max_reach": max_r,
            "total_reach": sum(self.link_lengths)
        }
