"""
Bimanual Manipulation Module
Dual-arm coordination, task allocation,
symmetric/asymmetric grasps, and handoff planning for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ArmPose:
    """Arm end-effector pose."""
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float


class DualArmCoordinator:
    """
    Coordinate two robotic arms.
    """
    
    def __init__(self, arm_separation_m: float = 0.8):
        """
        Args:
            arm_separation_m: Distance between arm bases
        """
        self.separation = arm_separation_m
    
    def relative_pose(self, left_pose: ArmPose,
                     right_pose: ArmPose) -> Tuple[float, float, float]:
        """
        Compute relative position between arms.
        
        Args:
            left_pose: Left arm pose
            right_pose: Right arm pose
        
        Returns:
            Relative (dx, dy, dz)
        """
        dx = right_pose.x - left_pose.x
        dy = right_pose.y - left_pose.y
        dz = right_pose.z - left_pose.z
        return dx, dy, dz
    
    def workspace_overlap(self, left_reach_m: float = 0.6,
                         right_reach_m: float = 0.6) -> float:
        """
        Compute workspace overlap volume.
        
        Args:
            left_reach_m: Left arm reach
            right_reach_m: Right arm reach
        
        Returns:
            Overlap metric
        """
        if self.separation >= left_reach_m + right_reach_m:
            return 0.0
        return (left_reach_m + right_reach_m - self.separation) / (left_reach_m + right_reach_m)
    
    def symmetric_grasp_points(self, object_center: Tuple[float, float, float],
                              object_width_m: float) -> Tuple[ArmPose, ArmPose]:
        """
        Compute symmetric grasp points for bimanual grasp.
        
        Args:
            object_center: Object center
            object_width_m: Object width
        
        Returns:
            (left_grasp, right_grasp)
        """
        cx, cy, cz = object_center
        half_width = object_width_m / 2.0
        left = ArmPose(cx - half_width, cy, cz, 0.0, 0.0, 0.0)
        right = ArmPose(cx + half_width, cy, cz, 0.0, 0.0, math.pi)
        return left, right


class TaskAllocator:
    """
    Allocate tasks between two arms.
    """
    
    def __init__(self):
        pass
    
    def dominant_arm(self, task_complexity: float,
                    left_capability: float = 1.0,
                    right_capability: float = 1.0) -> str:
        """
        Choose dominant arm for task.
        
        Args:
            task_complexity: Task complexity
            left_capability: Left arm capability
            right_capability: Right arm capability
        
        Returns:
            Dominant arm
        """
        if left_capability >= right_capability:
            return "left"
        return "right"
    
    def load_balance(self, left_load: float,
                    right_load: float) -> float:
        """
        Compute load balance metric.
        
        Args:
            left_load: Left arm load
            right_load: Right arm load
        
        Returns:
            Balance (0=perfect, 1=worst)
        """
        total = left_load + right_load
        if total == 0:
            return 0.0
        return abs(left_load - right_load) / total


class HandoffPlanner:
    """
    Plan handoff between two arms.
    """
    
    def __init__(self):
        pass
    
    def handoff_pose(self, left_pose: ArmPose,
                    right_pose: ArmPose) -> ArmPose:
        """
        Compute handoff midpoint.
        
        Args:
            left_pose: Left arm pose
            right_pose: Right arm pose
        
        Returns:
            Handoff pose
        """
        return ArmPose(
            (left_pose.x + right_pose.x) / 2.0,
            (left_pose.y + right_pose.y) / 2.0,
            (left_pose.z + right_pose.z) / 2.0,
            0.0, 0.0, 0.0
        )
    
    def approach_direction(self, from_pose: ArmPose,
                          to_pose: ArmPose) -> Tuple[float, float, float]:
        """
        Compute approach direction.
        
        Args:
            from_pose: Starting pose
            to_pose: Target pose
        
        Returns:
            Direction vector
        """
        dx = to_pose.x - from_pose.x
        dy = to_pose.y - from_pose.y
        dz = to_pose.z - from_pose.z
        dist = math.sqrt(dx**2 + dy**2 + dz**2)
        if dist == 0:
            return 0.0, 0.0, 0.0
        return dx/dist, dy/dist, dz/dist


class BimanualGraspPlanner:
    """
    Plan bimanual grasps.
    """
    
    def __init__(self):
        pass
    
    def grasp_stability(self, left_contact: Tuple[float, float, float],
                       right_contact: Tuple[float, float, float],
                       object_com: Tuple[float, float, float]) -> float:
        """
        Compute grasp stability from contact geometry.
        
        Args:
            left_contact: Left contact point
            right_contact: Right contact point
            object_com: Object center of mass
        
        Returns:
            Stability score
        """
        # Simplified: distance from COM to contact line
        mid_x = (left_contact[0] + right_contact[0]) / 2.0
        mid_y = (left_contact[1] + right_contact[1]) / 2.0
        dist = math.sqrt((mid_x - object_com[0])**2 + (mid_y - object_com[1])**2)
        return max(0.0, 1.0 - dist)
    
    def required_grip_force(self, object_weight_N: float,
                           friction_coefficient: float = 0.5,
                           safety_factor: float = 2.0) -> float:
        """
        Compute required grip force per hand.
        
        Args:
            object_weight_N: Object weight
            friction_coefficient: Friction
            safety_factor: Safety factor
        
        Returns:
            Force per hand in N
        """
        if friction_coefficient <= 0:
            return 0.0
        return object_weight_N * safety_factor / (2.0 * friction_coefficient)


class BimanualManipulation:
    """
    Unified bimanual manipulation controller.
    """
    
    def __init__(self):
        self.coordinator = DualArmCoordinator()
        self.allocator = TaskAllocator()
        self.handoff = HandoffPlanner()
        self.grasp = BimanualGraspPlanner()
    
    def bimanual_summary(self) -> Dict:
        """Get summary."""
        return {
            "capabilities": ["coordination", "task_allocation", "handoff", "grasp"],
            "grasp_types": ["symmetric", "asymmetric"]
        }
