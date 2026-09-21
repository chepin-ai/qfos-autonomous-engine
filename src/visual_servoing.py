"""
Visual Servoing Module
Image-based servoing, position-based servoing,
feature tracking, camera-robot calibration for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ImageFeature:
    """2D image feature."""
    u: float
    v: float


class ImageBasedServoing:
    """
    Image-based visual servoing (IBVS).
    """
    
    def __init__(self, focal_length: float = 500.0,
                 gain: float = 0.1):
        """
        Args:
            focal_length: Camera focal length in pixels
            gain: Control gain
        """
        self.f = focal_length
        self.gain = gain
    
    def interaction_matrix(self, feature: ImageFeature,
                          depth_m: float) -> List[List[float]]:
        """
        Compute interaction matrix for point feature.
        
        Args:
            feature: Image feature
            depth_m: Depth
        
        Returns:
            2x6 interaction matrix
        """
        u = feature.u
        v = feature.v
        Z = depth_m
        
        L = [
            [-self.f / Z, 0.0, u / Z, u * v / self.f, -(self.f + u**2 / self.f), v],
            [0.0, -self.f / Z, v / Z, self.f + v**2 / self.f, -u * v / self.f, -u]
        ]
        return L
    
    def error_vector(self, current: ImageFeature,
                    desired: ImageFeature) -> List[float]:
        """
        Compute image error.
        
        Args:
            current: Current feature
            desired: Desired feature
        
        Returns:
            Error vector [du, dv]
        """
        return [current.u - desired.u, current.v - desired.v]
    
    def camera_velocity(self, current: ImageFeature,
                       desired: ImageFeature,
                       depth_m: float) -> List[float]:
        """
        Compute camera velocity from image error.
        
        Args:
            current: Current feature
            desired: Desired feature
            depth_m: Depth
        
        Returns:
            Camera velocity [vx, vy, vz, wx, wy, wz]
        """
        e = self.error_vector(current, desired)
        L = self.interaction_matrix(current, depth_m)
        
        # Simplified: pseudo-inverse of L
        # L is 2x6, use L^T for simplicity
        velocity = [0.0] * 6
        for j in range(6):
            for i in range(2):
                velocity[j] -= self.gain * L[i][j] * e[i]
        
        return velocity


class PositionBasedServoing:
    """
    Position-based visual servoing (PBVS).
    """
    
    def __init__(self, gain: float = 0.5):
        """
        Args:
            gain: Control gain
        """
        self.gain = gain
    
    def position_error(self, current_pose: List[float],
                      desired_pose: List[float]) -> List[float]:
        """
        Compute position error.
        
        Args:
            current_pose: Current [x, y, z, roll, pitch, yaw]
            desired_pose: Desired [x, y, z, roll, pitch, yaw]
        
        Returns:
            Error vector
        """
        return [c - d for c, d in zip(current_pose, desired_pose)]
    
    def camera_velocity_pbvs(self, current_pose: List[float],
                            desired_pose: List[float]) -> List[float]:
        """
        Compute camera velocity for PBVS.
        
        Args:
            current_pose: Current pose
            desired_pose: Desired pose
        
        Returns:
            Velocity
        """
        error = self.position_error(current_pose, desired_pose)
        return [-self.gain * e for e in error]


class FeatureTracker:
    """
    Feature tracking for visual servoing.
    """
    
    def __init__(self):
        pass
    
    def centroid(self, features: List[ImageFeature]) -> ImageFeature:
        """
        Compute centroid of features.
        
        Args:
            features: List of features
        
        Returns:
            Centroid
        """
        if not features:
            return ImageFeature(0.0, 0.0)
        u = sum(f.u for f in features) / len(features)
        v = sum(f.v for f in features) / len(features)
        return ImageFeature(u, v)
    
    def bounding_box(self, features: List[ImageFeature]) -> Tuple[float, float, float, float]:
        """
        Compute bounding box.
        
        Args:
            features: Features
        
        Returns:
            (min_u, min_v, max_u, max_v)
        """
        if not features:
            return 0.0, 0.0, 0.0, 0.0
        us = [f.u for f in features]
        vs = [f.v for f in features]
        return min(us), min(vs), max(us), max(vs)


class CameraRobotCalibration:
    """
    Camera-robot hand-eye calibration.
    """
    
    def __init__(self):
        pass
    
    def pixel_to_meter(self, pixel_coord: float,
                      depth_m: float,
                      focal_length: float = 500.0) -> float:
        """
        Convert pixel coordinate to meters.
        
        Args:
            pixel_coord: Pixel coordinate
            depth_m: Depth
            focal_length: Focal length
        
        Returns:
            Meters
        """
        return pixel_coord * depth_m / focal_length
    
    def meter_to_pixel(self, meter_coord: float,
                      depth_m: float,
                      focal_length: float = 500.0) -> float:
        """
        Convert meters to pixels.
        
        Args:
            meter_coord: Meter coordinate
            depth_m: Depth
            focal_length: Focal length
        
        Returns:
            Pixels
        """
        if depth_m <= 0:
            return 0.0
        return meter_coord * focal_length / depth_m


class VisualServoing:
    """
    Unified visual servoing controller.
    """
    
    def __init__(self):
        self.ibvs = ImageBasedServoing()
        self.pbvs = PositionBasedServoing()
        self.tracker = FeatureTracker()
        self.calibration = CameraRobotCalibration()
    
    def vs_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["IBVS", "PBVS"],
            "components": ["feature_tracking", "calibration", "velocity_control"]
        }
