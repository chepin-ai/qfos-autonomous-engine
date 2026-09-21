"""
Visual Servoing Module
Image-based visual servoing, position-based visual servoing,
feature tracking, and camera calibration for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ImageFeature:
    """2D image feature point."""
    u: float
    v: float


@dataclass
class Point3D:
    """3D world point."""
    x: float
    y: float
    z: float


class ImageBasedVisualServoing:
    """
    Image-based visual servoing (IBVS).
    """
    
    def __init__(self, focal_length_px: float = 500.0):
        """
        Args:
            focal_length_px: Camera focal length
        """
        self.f = focal_length_px
    
    def interaction_matrix(self, feature: ImageFeature,
                          depth_m: float = 1.0) -> List[List[float]]:
        """
        Compute interaction matrix for single feature.
        
        Args:
            feature: Image feature
            depth_m: Scene depth
        
        Returns:
            2x6 interaction matrix
        """
        u, v = feature.u, feature.v
        Z = depth_m
        L = [
            [-self.f / Z, 0.0, u / Z, u * v / self.f, -(self.f + u**2 / self.f), v],
            [0.0, -self.f / Z, v / Z, self.f + v**2 / self.f, -u * v / self.f, -u]
        ]
        return L
    
    def feature_error(self, current: ImageFeature,
                     desired: ImageFeature) -> List[float]:
        """
        Compute feature error.
        
        Args:
            current: Current feature
            desired: Desired feature
        
        Returns:
            Error vector [du, dv]
        """
        return [current.u - desired.u, current.v - desired.v]
    
    def camera_velocity(self, current: ImageFeature,
                       desired: ImageFeature,
                       depth_m: float = 1.0,
                       gain: float = 0.5) -> List[float]:
        """
        Compute camera velocity command.
        
        Args:
            current: Current feature
            desired: Desired feature
            depth_m: Scene depth
            gain: Control gain
        
        Returns:
            Velocity [vx, vy, vz, wx, wy, wz]
        """
        error = self.feature_error(current, desired)
        L = self.interaction_matrix(current, depth_m)
        # Simplified: pseudo-inverse of L times error
        # L is 2x6, use transpose as approximation
        v = [0.0] * 6
        for j in range(6):
            v[j] = -gain * (L[0][j] * error[0] + L[1][j] * error[1])
        return v


class PositionBasedVisualServoing:
    """
    Position-based visual servoing (PBVS).
    """
    
    def __init__(self):
        pass
    
    def pose_error(self, current_pose: List[float],
                  desired_pose: List[float]) -> List[float]:
        """
        Compute pose error (simplified 3D translation).
        
        Args:
            current_pose: Current [x, y, z]
            desired_pose: Desired [x, y, z]
        
        Returns:
            Error [dx, dy, dz]
        """
        return [c - d for c, d in zip(current_pose, desired_pose)]
    
    def velocity_command(self, current_pose: List[float],
                        desired_pose: List[float],
                        gain: float = 0.5) -> List[float]:
        """
        Compute velocity command.
        
        Args:
            current_pose: Current pose
            desired_pose: Desired pose
            gain: Control gain
        
        Returns:
            Velocity [vx, vy, vz]
        """
        error = self.pose_error(current_pose, desired_pose)
        return [-gain * e for e in error]


class FeatureTracking:
    """
    Track features across frames.
    """
    
    def __init__(self):
        self.tracks: Dict[int, List[ImageFeature]] = {}
    
    def update_track(self, feature_id: int, feature: ImageFeature):
        """
        Update feature track.
        
        Args:
            feature_id: Feature ID
            feature: New position
        """
        if feature_id not in self.tracks:
            self.tracks[feature_id] = []
        self.tracks[feature_id].append(feature)
    
    def track_velocity(self, feature_id: int,
                      dt: float = 1.0) -> Tuple[float, float]:
        """
        Compute feature velocity from track.
        
        Args:
            feature_id: Feature ID
            dt: Time step
        
        Returns:
            (du/dt, dv/dt)
        """
        track = self.tracks.get(feature_id, [])
        if len(track) < 2:
            return (0.0, 0.0)
        last = track[-1]
        prev = track[-2]
        return ((last.u - prev.u) / dt, (last.v - prev.v) / dt)
    
    def num_tracks(self) -> int:
        """Return number of active tracks."""
        return len(self.tracks)


class CameraCalibration:
    """
    Camera intrinsic calibration.
    """
    
    def __init__(self, fx: float = 500.0, fy: float = 500.0,
                 cx: float = 320.0, cy: float = 240.0):
        """
        Args:
            fx, fy: Focal lengths
            cx, cy: Principal point
        """
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy
    
    def project(self, point3d: Point3D) -> ImageFeature:
        """
        Project 3D point to image.
        
        Args:
            point3d: 3D point
        
        Returns:
            Image feature
        """
        if point3d.z <= 0:
            return ImageFeature(self.cx, self.cy)
        u = self.fx * point3d.x / point3d.z + self.cx
        v = self.fy * point3d.y / point3d.z + self.cy
        return ImageFeature(u, v)
    
    def backproject(self, feature: ImageFeature,
                   depth: float = 1.0) -> Point3D:
        """
        Backproject image point to 3D.
        
        Args:
            feature: Image feature
            depth: Depth
        
        Returns:
            3D point
        """
        x = (feature.u - self.cx) * depth / self.fx
        y = (feature.v - self.cy) * depth / self.fy
        return Point3D(x, y, depth)


class VisualServoing:
    """
    Unified visual servoing controller.
    """
    
    def __init__(self):
        self.ibvs = ImageBasedVisualServoing()
        self.pbvs = PositionBasedVisualServoing()
        self.tracking = FeatureTracking()
        self.camera = CameraCalibration()
    
    def servoing_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["ibvs", "pbvs", "feature_tracking", "camera_calibration"],
            "outputs": ["camera_velocity", "feature_velocity", "3d_position"]
        }
