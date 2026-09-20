"""
Grasp Planning Module
Grasp quality, force closure, antipodal grasp detection,
and hand configuration for autonomous manipulation.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class GraspType(Enum):
    """Type of grasp."""
    PINCH = "pinch"
    POWER = "power"
    PRECISION = "precision"
    HOOK = "hook"
    SUCTION = "suction"
    CAGING = "caging"


@dataclass
class ContactPoint:
    """A contact point on an object."""
    position: Tuple[float, float, float]
    normal: Tuple[float, float, float]
    friction_coeff: float = 0.5


class ForceClosureChecker:
    """
    Check force closure conditions for a grasp.
    """
    
    def __init__(self, friction_cone_resolution: int = 8):
        """
        Args:
            friction_cone_resolution: Number of edges in friction cone
        """
        self.cone_res = friction_cone_resolution
    
    def friction_cone_edges(self, contact: ContactPoint) -> List[Tuple[float, float, float]]:
        """
        Compute friction cone edge vectors.
        
        Args:
            contact: Contact point
        
        Returns:
            List of edge direction vectors
        """
        mu = contact.friction_coeff
        nx, ny, nz = contact.normal
        
        # Simplified: generate cone edges in tangent plane
        edges = []
        for i in range(self.cone_res):
            angle = 2.0 * math.pi * i / self.cone_res
            # Tangent direction (simplified, assumes normal is z-aligned)
            tx = math.cos(angle)
            ty = math.sin(angle)
            tz = 0.0
            
            # Cone edge = normal + mu * tangent
            ex = nx + mu * tx
            ey = ny + mu * ty
            ez = nz + mu * tz
            
            # Normalize
            mag = math.sqrt(ex**2 + ey**2 + ez**2)
            if mag > 0:
                edges.append((ex/mag, ey/mag, ez/mag))
        
        return edges
    
    def is_force_closure(self, contacts: List[ContactPoint]) -> bool:
        """
        Check if grasp achieves force closure.
        
        Args:
            contacts: List of contact points
        
        Returns:
            True if force closure
        """
        if len(contacts) < 2:
            return False
        
        # Simplified: check if contact normals oppose each other
        # and contacts are on opposite sides of object center
        if len(contacts) == 2:
            n1 = contacts[0].normal
            n2 = contacts[1].normal
            
            # Dot product of normals should be negative (opposing)
            dot = n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2]
            
            # Check if contacts are antipodal
            p1 = contacts[0].position
            p2 = contacts[1].position
            
            # Line between contacts should align with normals
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            dist = math.sqrt(dx**2 + dy**2 + dz**2)
            
            if dist > 0:
                # Direction from p1 to p2 should align with n1
                align1 = (dx * n1[0] + dy * n1[1] + dz * n1[2]) / dist
                align2 = (-dx * n2[0] - dy * n2[1] - dz * n2[2]) / dist
                
                # Both should point inward
                if align1 > 0.7 and align2 > 0.7 and dot < -0.5:
                    return True
        
        # For more contacts, use simplified check
        return len(contacts) >= 3
    
    def grasp_wrench_space(self, contacts: List[ContactPoint]) -> List[Tuple[float, float, float, float, float, float]]:
        """
        Compute grasp wrench space (simplified 2D).
        
        Args:
            contacts: Contact points
        
        Returns:
            List of wrenches (Fx, Fy, Fz, Tx, Ty, Tz)
        """
        wrenches = []
        
        for c in contacts:
            fx, fy, fz = c.normal
            # Torque = r x F (simplified, only z-component)
            tx = c.position[1] * fz - c.position[2] * fy
            ty = c.position[2] * fx - c.position[0] * fz
            tz = c.position[0] * fy - c.position[1] * fx
            
            wrenches.append((fx, fy, fz, tx, ty, tz))
        
        return wrenches


class GraspQualityEvaluator:
    """
    Evaluate grasp quality metrics.
    """
    
    def __init__(self):
        self.fc_checker = ForceClosureChecker()
    
    def epsilon_quality(self, contacts: List[ContactPoint]) -> float:
        """
        Compute epsilon quality (radius of largest inscribed sphere
        in grasp wrench space).
        
        Args:
            contacts: Contact points
        
        Returns:
            Epsilon quality
        """
        if not self.fc_checker.is_force_closure(contacts):
            return 0.0
        
        # Simplified: based on contact spread and alignment
        if len(contacts) == 2:
            p1 = contacts[0].position
            p2 = contacts[1].position
            dist = math.sqrt(sum((a-b)**2 for a, b in zip(p1, p2)))
            
            # Epsilon proportional to distance and friction
            mu = min(c.friction_coeff for c in contacts)
            return min(0.1 * dist * mu, 1.0)
        
        return 0.5  # Default for multi-contact
    
    def volume_quality(self, contacts: List[ContactPoint]) -> float:
        """
        Compute volume quality (volume of grasp wrench space).
        
        Args:
            contacts: Contact points
        
        Returns:
            Volume metric
        """
        if len(contacts) < 2:
            return 0.0
        
        # Simplified: product of contact distances
        volume = 0.0
        for i in range(len(contacts)):
            for j in range(i+1, len(contacts)):
                p1 = contacts[i].position
                p2 = contacts[j].position
                dist = math.sqrt(sum((a-b)**2 for a, b in zip(p1, p2)))
                volume += dist
        
        return volume / max(1, len(contacts) * (len(contacts) - 1) / 2)
    
    def antipodal_quality(self, contacts: List[ContactPoint]) -> float:
        """
        Measure how antipodal the grasp is.
        
        Args:
            contacts: Contact points
        
        Returns:
            Antipodal score (0-1)
        """
        if len(contacts) != 2:
            return 0.0
        
        n1 = contacts[0].normal
        n2 = contacts[1].normal
        
        # Normals should be opposite
        dot = n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2]
        
        # Position alignment
        p1 = contacts[0].position
        p2 = contacts[1].position
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        dist = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if dist == 0:
            return 0.0
        
        # Line between contacts should align with both normals
        align = abs(dx*n1[0] + dy*n1[1] + dz*n1[2]) / dist
        
        # Combine normal opposition and alignment
        score = (-dot + align) / 2.0
        return max(0.0, min(1.0, score))


class HandConfiguration:
    """
    Hand/finger configuration for grasping.
    """
    
    def __init__(self, num_fingers: int = 3):
        """
        Args:
            num_fingers: Number of fingers
        """
        self.num_fingers = num_fingers
        self.joint_angles: List[float] = [0.0] * num_fingers * 3
        self.finger_positions: List[Tuple[float, float, float]] = []
    
    def set_joint_angles(self, angles: List[float]):
        """Set joint angles."""
        self.joint_angles = angles[:self.num_fingers * 3]
    
    def fingertip_positions(self, palm_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> List[Tuple[float, float, float]]:
        """
        Compute fingertip positions.
        
        Args:
            palm_position: Palm center
        
        Returns:
            Fingertip positions
        """
        positions = []
        
        for i in range(self.num_fingers):
            # Simplified: fingers arranged radially
            angle = 2.0 * math.pi * i / self.num_fingers
            finger_len = 0.08  # 8cm finger
            
            x = palm_position[0] + finger_len * math.cos(angle)
            y = palm_position[1] + finger_len * math.sin(angle)
            z = palm_position[2]
            
            positions.append((x, y, z))
        
        self.finger_positions = positions
        return positions
    
    def to_contacts(self, object_normals: List[Tuple[float, float, float]]) -> List[ContactPoint]:
        """
        Convert to contact points.
        
        Args:
            object_normals: Surface normals at contact
        
        Returns:
            Contact points
        """
        contacts = []
        for pos, normal in zip(self.finger_positions, object_normals):
            contacts.append(ContactPoint(pos, normal))
        return contacts


class GraspPlanner:
    """
    Plan grasps for objects.
    """
    
    def __init__(self):
        self.quality = GraspQualityEvaluator()
        self.fc = ForceClosureChecker()
    
    def plan_antipodal(self, object_radius_m: float = 0.05,
                      object_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> List[ContactPoint]:
        """
        Plan antipodal grasp on spherical object.
        
        Args:
            object_radius_m: Object radius
            object_center: Object center
        
        Returns:
            Contact points
        """
        # Two opposing contacts
        c1 = (object_center[0] + object_radius_m, object_center[1], object_center[2])
        c2 = (object_center[0] - object_radius_m, object_center[1], object_center[2])
        
        n1 = (1.0, 0.0, 0.0)
        n2 = (-1.0, 0.0, 0.0)
        
        return [ContactPoint(c1, n1, 0.5), ContactPoint(c2, n2, 0.5)]
    
    def plan_circular(self, object_radius_m: float = 0.05,
                     num_contacts: int = 3) -> List[ContactPoint]:
        """
        Plan circular grasp with multiple contacts.
        
        Args:
            object_radius_m: Object radius
            num_contacts: Number of contact points
        
        Returns:
            Contact points
        """
        contacts = []
        
        for i in range(num_contacts):
            angle = 2.0 * math.pi * i / num_contacts
            x = object_radius_m * math.cos(angle)
            y = object_radius_m * math.sin(angle)
            z = 0.0
            
            # Normal points inward
            nx = -math.cos(angle)
            ny = -math.sin(angle)
            nz = 0.0
            
            contacts.append(ContactPoint((x, y, z), (nx, ny, nz), 0.5))
        
        return contacts
    
    def select_best_grasp(self, candidates: List[List[ContactPoint]]) -> Tuple[List[ContactPoint], float]:
        """
        Select best grasp from candidates.
        
        Args:
            candidates: List of candidate grasps
        
        Returns:
            (best grasp, quality score)
        """
        best = None
        best_score = -1.0
        
        for grasp in candidates:
            score = self.quality.epsilon_quality(grasp)
            if score > best_score:
                best_score = score
                best = grasp
        
        return (best or [], best_score)


class GraspPlanning:
    """
    Unified grasp planning system.
    """
    
    def __init__(self):
        self.planner = GraspPlanner()
        self.hand = HandConfiguration()
        self.quality = GraspQualityEvaluator()
        self.grasps: List[List[ContactPoint]] = []
    
    def add_grasp(self, contacts: List[ContactPoint]):
        """Add grasp candidate."""
        self.grasps.append(contacts)
    
    def best_grasp(self) -> Tuple[Optional[List[ContactPoint]], float]:
        """Get best grasp."""
        return self.planner.select_best_grasp(self.grasps)
    
    def plan_for_object(self, radius_m: float = 0.05) -> List[ContactPoint]:
        """
        Plan grasp for spherical object.
        
        Args:
            radius_m: Object radius
        
        Returns:
            Contact points
        """
        antipodal = self.planner.plan_antipodal(radius_m)
        circular = self.planner.plan_circular(radius_m, 3)
        
        self.grasps = [antipodal, circular]
        best, score = self.best_grasp()
        return best or []
    
    def grasp_summary(self) -> Dict:
        """Get grasp summary."""
        best, score = self.best_grasp()
        return {
            "candidates": len(self.grasps),
            "best_quality": score,
            "force_closure": self.quality.fc_checker.is_force_closure(best) if best else False
        }
