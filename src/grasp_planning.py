"""
Grasp Planning Module
Grasp quality metrics, antipodal grasp detection,
force closure, and gripper workspace for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ContactPoint:
    """Grasp contact point."""
    position: Tuple[float, float, float]
    normal: Tuple[float, float, float]


class GraspQualityMetrics:
    """
    Grasp quality evaluation metrics.
    """
    
    def __init__(self):
        pass
    
    def epsilon_quality(self, contact_points: List[ContactPoint],
                       friction_coefficient: float = 0.5) -> float:
        """
        Compute epsilon quality (wrench space distance to origin).
        
        Args:
            contact_points: Contact points
            friction_coefficient: Friction
        
        Returns:
            Epsilon quality
        """
        if len(contact_points) < 2:
            return 0.0
        # Simplified: min distance from origin to wrench hull
        # Use contact normals and friction cone approximation
        distances = []
        for cp in contact_points:
            nx, ny, nz = cp.normal
            mag = math.sqrt(nx**2 + ny**2 + nz**2)
            if mag > 0:
                distances.append(friction_coefficient / mag)
        if not distances:
            return 0.0
        return min(distances)
    
    def volume_quality(self, contact_points: List[ContactPoint]) -> float:
        """
        Compute volume quality (wrench hull volume).
        
        Args:
            contact_points: Contact points
        
        Returns:
            Volume quality
        """
        if len(contact_points) < 3:
            return 0.0
        # Simplified: sum of cross products
        vol = 0.0
        for i in range(len(contact_points)):
            for j in range(i + 1, len(contact_points)):
                p1 = contact_points[i].position
                p2 = contact_points[j].position
                vol += abs(p1[0] * p2[1] - p1[1] * p2[0])
        return vol


class AntipodalGraspDetection:
    """
    Detect antipodal grasps.
    """
    
    def __init__(self):
        pass
    
    def is_antipodal(self, contact1: ContactPoint,
                    contact2: ContactPoint,
                    angular_tolerance_deg: float = 15.0) -> bool:
        """
        Check if two contacts form antipodal grasp.
        
        Args:
            contact1, contact2: Contact points
            angular_tolerance_deg: Tolerance
        
        Returns:
            True if antipodal
        """
        n1 = contact1.normal
        n2 = contact2.normal
        # Antipodal: normals point toward each other
        dot = n1[0] * n2[0] + n1[1] * n2[1] + n1[2] * n2[2]
        mag1 = math.sqrt(sum(c**2 for c in n1))
        mag2 = math.sqrt(sum(c**2 for c in n2))
        if mag1 <= 0 or mag2 <= 0:
            return False
        cos_angle = -dot / (mag1 * mag2)
        tolerance_rad = math.radians(angular_tolerance_deg)
        return cos_angle >= math.cos(tolerance_rad)
    
    def grasp_center(self, contact1: ContactPoint,
                    contact2: ContactPoint) -> Tuple[float, float, float]:
        """
        Compute grasp center point.
        
        Args:
            contact1, contact2: Contact points
        
        Returns:
            Center position
        """
        p1 = contact1.position
        p2 = contact2.position
        return ((p1[0] + p2[0]) / 2.0,
                (p1[1] + p2[1]) / 2.0,
                (p1[2] + p2[2]) / 2.0)


class ForceClosure:
    """
    Force closure analysis.
    """
    
    def __init__(self):
        pass
    
    def is_force_closure(self, contact_points: List[ContactPoint],
                        friction_coefficient: float = 0.5) -> bool:
        """
        Check if grasp has force closure.
        
        Args:
            contact_points: Contact points
            friction_coefficient: Friction
        
        Returns:
            True if force closure
        """
        if len(contact_points) < 2:
            return False
        # Simplified: check if friction cones positively span
        # Force closure if epsilon quality > 0
        from grasp_planning import GraspQualityMetrics
        gqm = GraspQualityMetrics()
        return gqm.epsilon_quality(contact_points, friction_coefficient) > 0.0
    
    def min_normal_force(self, external_wrench: List[float],
                        contact_points: List[ContactPoint],
                        friction_coefficient: float = 0.5) -> float:
        """
        Compute minimum contact normal force to resist wrench.
        
        Args:
            external_wrench: External wrench
            contact_points: Contact points
            friction_coefficient: Friction
        
        Returns:
            Minimum normal force
        """
        if not contact_points:
            return 0.0
        # Simplified: distribute wrench equally
        force_magnitude = math.sqrt(sum(w**2 for w in external_wrench[:3]))
        return force_magnitude / (len(contact_points) * friction_coefficient)


class GripperWorkspace:
    """
    Gripper workspace analysis.
    """
    
    def __init__(self, max_aperture_mm: float = 100.0):
        """
        Args:
            max_aperture_mm: Maximum aperture
        """
        self.max_aperture = max_aperture_mm
    
    def can_grasp(self, object_diameter_mm: float) -> bool:
        """
        Check if object fits in gripper.
        
        Args:
            object_diameter_mm: Object diameter
        
        Returns:
            True if graspable
        """
        return object_diameter_mm <= self.max_aperture
    
    def grasp_span(self, contact1: ContactPoint,
                  contact2: ContactPoint) -> float:
        """
        Compute distance between contacts.
        
        Args:
            contact1, contact2: Contact points
        
        Returns:
            Distance (mm)
        """
        p1 = contact1.position
        p2 = contact2.position
        return math.sqrt(sum((a - b)**2 for a, b in zip(p1, p2)))


class GraspPlanning:
    """
    Unified grasp planning controller.
    """
    
    def __init__(self):
        self.quality = GraspQualityMetrics()
        self.antipodal = AntipodalGraspDetection()
        self.closure = ForceClosure()
        self.workspace = GripperWorkspace()
    
    def grasp_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["quality_metrics", "antipodal", "force_closure", "workspace"],
            "outputs": ["epsilon_quality", "volume_quality", "graspable"]
        }
