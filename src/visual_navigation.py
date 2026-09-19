"""
Visual Navigation Module
Feature matching, visual odometry, and landmark-based
navigation for autonomous systems.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Feature:
    """A visual feature."""
    feature_id: int
    x: float  # pixel x
    y: float  # pixel y
    descriptor: Tuple[float, ...] = ()


@dataclass
class Landmark:
    """A known landmark."""
    landmark_id: str
    world_position: Tuple[float, float, float]  # meters
    features: List[Feature] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []


class FeatureMatcher:
    """
    Match features between frames.
    """
    
    def __init__(self, threshold: float = 0.7):
        """
        Args:
            threshold: Matching threshold (0-1)
        """
        self.threshold = threshold
    
    def _descriptor_distance(self, d1: Tuple[float, ...],
                            d2: Tuple[float, ...]) -> float:
        """
        Compute descriptor distance.
        
        Args:
            d1, d2: Descriptors
        
        Returns:
            Distance (0-1)
        """
        if len(d1) != len(d2) or len(d1) == 0:
            return 1.0
        
        # Normalized cross-correlation
        dot = sum(a * b for a, b in zip(d1, d2))
        norm1 = math.sqrt(sum(a * a for a in d1))
        norm2 = math.sqrt(sum(b * b for b in d2))
        
        if norm1 * norm2 < 1e-15:
            return 1.0
        
        similarity = dot / (norm1 * norm2)
        return 1.0 - max(0.0, similarity)
    
    def match(self, features1: List[Feature],
             features2: List[Feature]) -> List[Tuple[Feature, Feature, float]]:
        """
        Match features between two frames.
        
        Args:
            features1: Features from frame 1
            features2: Features from frame 2
        
        Returns:
            List of (feature1, feature2, distance)
        """
        matches = []
        
        for f1 in features1:
            best_match = None
            best_dist = float('inf')
            second_best = float('inf')
            
            for f2 in features2:
                dist = self._descriptor_distance(f1.descriptor, f2.descriptor)
                if dist < best_dist:
                    second_best = best_dist
                    best_dist = dist
                    best_match = f2
                elif dist < second_best:
                    second_best = dist
            
            # Ratio test
            if best_match and second_best > 0 and best_dist / second_best < self.threshold:
                matches.append((f1, best_match, best_dist))
        
        return matches
    
    def count_matches(self, features1: List[Feature],
                     features2: List[Feature]) -> int:
        """Count number of matches."""
        return len(self.match(features1, features2))


class VisualOdometry:
    """
    Estimate motion from visual features.
    """
    
    def __init__(self, focal_length_px: float = 500.0,
                 principal_point: Tuple[float, float] = (320, 240)):
        """
        Args:
            focal_length_px: Camera focal length (pixels)
            principal_point: Image center (px, py)
        """
        self.focal_length = focal_length_px
        self.principal = principal_point
    
    def _pixel_to_bearing(self, x: float, y: float
                         ) -> Tuple[float, float, float]:
        """
        Convert pixel to unit bearing vector.
        
        Args:
            x, y: Pixel coordinates
        
        Returns:
            Unit direction vector
        """
        dx = x - self.principal[0]
        dy = y - self.principal[1]
        
        # Bearing: (x/f, y/f, 1) normalized
        bx = dx / self.focal_length
        by = dy / self.focal_length
        bz = 1.0
        
        norm = math.sqrt(bx**2 + by**2 + bz**2)
        return (bx/norm, by/norm, bz/norm)
    
    def estimate_translation(self, matches: List[Tuple[Feature, Feature, float]],
                            depth_scale: float = 1.0
                            ) -> Tuple[float, float, float]:
        """
        Estimate translation from feature matches.
        
        Args:
            matches: Feature matches
            depth_scale: Assumed depth scale
        
        Returns:
            Translation vector (meters)
        """
        if len(matches) < 2:
            return (0.0, 0.0, 0.0)
        
        # Optical flow based translation
        tx_sum = 0.0
        ty_sum = 0.0
        
        for f1, f2, _ in matches:
            dx = f2.x - f1.x
            dy = f2.y - f1.y
            tx_sum += dx
            ty_sum += dy
        
        n = len(matches)
        # Scale by focal length and assumed depth
        tx = -(tx_sum / n) * depth_scale / self.focal_length
        ty = -(ty_sum / n) * depth_scale / self.focal_length
        
        return (tx, ty, 0.0)
    
    def estimate_rotation(self, matches: List[Tuple[Feature, Feature, float]]
                         ) -> float:
        """
        Estimate yaw rotation from feature matches.
        
        Args:
            matches: Feature matches
        
        Returns:
            Rotation angle (radians)
        """
        if len(matches) < 2:
            return 0.0
        
        # Compute average angular displacement around principal point
        angle_sum = 0.0
        count = 0
        
        for f1, f2, _ in matches:
            dx1 = f1.x - self.principal[0]
            dy1 = f1.y - self.principal[1]
            dx2 = f2.x - self.principal[0]
            dy2 = f2.y - self.principal[1]
            
            angle1 = math.atan2(dy1, dx1)
            angle2 = math.atan2(dy2, dx2)
            
            d_angle = angle2 - angle1
            # Normalize
            while d_angle > math.pi:
                d_angle -= 2 * math.pi
            while d_angle < -math.pi:
                d_angle += 2 * math.pi
            
            angle_sum += d_angle
            count += 1
        
        return angle_sum / count if count > 0 else 0.0


class LandmarkNavigator:
    """
    Navigate using known landmarks.
    """
    
    def __init__(self):
        self.landmarks: Dict[str, Landmark] = {}
        self.observed_landmarks: List[str] = []
    
    def add_landmark(self, landmark: Landmark):
        """Add known landmark."""
        self.landmarks[landmark.landmark_id] = landmark
    
    def recognize(self, features: List[Feature],
                 tolerance: float = 0.3) -> List[str]:
        """
        Recognize landmarks from features.
        
        Args:
            features: Observed features
            tolerance: Matching tolerance
        
        Returns:
            List of recognized landmark IDs
        """
        matcher = FeatureMatcher(threshold=tolerance)
        recognized = []
        
        for lid, landmark in self.landmarks.items():
            matches = matcher.match(landmark.features, features)
            if len(matches) >= 3:  # Need at least 3 matches
                recognized.append(lid)
        
        self.observed_landmarks = recognized
        return recognized
    
    def triangulate_position(self, landmark_observations: List[Tuple[str, float, float]]
                            ) -> Optional[Tuple[float, float, float]]:
        """
        Triangulate position from landmark observations.
        
        Args:
            landmark_observations: List of (landmark_id, bearing_deg, distance_m)
        
        Returns:
            Estimated position or None
        """
        if len(landmark_observations) < 2:
            return None
        
        # Simple averaging of back-projected positions
        positions = []
        for lid, bearing_deg, dist in landmark_observations:
            landmark = self.landmarks.get(lid)
            if not landmark:
                continue
            
            bearing = math.radians(bearing_deg)
            lx, ly, lz = landmark.world_position
            
            # Back-project from landmark
            px = lx + dist * math.cos(bearing)
            py = ly + dist * math.sin(bearing)
            pz = lz
            
            positions.append((px, py, pz))
        
        if not positions:
            return None
        
        n = len(positions)
        return (
            sum(p[0] for p in positions) / n,
            sum(p[1] for p in positions) / n,
            sum(p[2] for p in positions) / n
        )


class VisualNavigation:
    """
    Unified visual navigation controller.
    """
    
    def __init__(self):
        self.matcher = FeatureMatcher()
        self.vo = VisualOdometry()
        self.navigator = LandmarkNavigator()
        self.position = (0.0, 0.0, 0.0)
        self.orientation = 0.0
    
    def extract_features(self, keypoints: List[Tuple[float, float]]
                        ) -> List[Feature]:
        """
        Extract features from keypoints.
        
        Args:
            keypoints: List of (x, y) keypoints
        
        Returns:
            Features with simple descriptors
        """
        features = []
        for i, (x, y) in enumerate(keypoints):
            # Simple descriptor: relative position in image
            desc = (x / 640.0, y / 480.0, (x + y) / 1000.0)
            features.append(Feature(i, x, y, desc))
        return features
    
    def track_motion(self, prev_features: List[Feature],
                    curr_features: List[Feature],
                    depth_scale: float = 1.0) -> Dict[str, float]:
        """
        Track motion between frames.
        
        Args:
            prev_features: Previous frame features
            curr_features: Current frame features
            depth_scale: Depth scale
        
        Returns:
            Motion estimate
        """
        matches = self.matcher.match(prev_features, curr_features)
        
        translation = self.vo.estimate_translation(matches, depth_scale)
        rotation = self.vo.estimate_rotation(matches)
        
        # Update pose
        self.position = (
            self.position[0] + translation[0],
            self.position[1] + translation[1],
            self.position[2] + translation[2]
        )
        self.orientation += rotation
        
        return {
            "dx": translation[0],
            "dy": translation[1],
            "dz": translation[2],
            "dtheta_rad": rotation,
            "matches": len(matches)
        }
    
    def add_landmark(self, landmark_id: str,
                    world_pos: Tuple[float, float, float],
                    features: List[Feature]):
        """Add landmark to map."""
        lm = Landmark(landmark_id, world_pos, features)
        self.navigator.add_landmark(lm)
    
    def localize(self, observed_features: List[Feature]
                ) -> Optional[Tuple[float, float, float]]:
        """
        Localize using landmarks.
        
        Args:
            observed_features: Observed features
        
        Returns:
            Position or None
        """
        recognized = self.navigator.recognize(observed_features)
        if not recognized:
            return None
        
        # Create synthetic observations
        observations = []
        for lid in recognized:
            lm = self.navigator.landmarks.get(lid)
            if lm:
                # Simple distance estimate
                dist = math.sqrt(
                    (self.position[0] - lm.world_position[0])**2 +
                    (self.position[1] - lm.world_position[1])**2
                )
                observations.append((lid, 0.0, dist))
        
        if len(observations) == 1:
            # Single landmark: return back-projected position
            lid, bearing_deg, dist = observations[0]
            lm = self.navigator.landmarks.get(lid)
            if lm:
                bearing = math.radians(bearing_deg)
                lx, ly, lz = lm.world_position
                return (lx + dist * math.cos(bearing),
                        ly + dist * math.sin(bearing), lz)
            return None
        
        return self.navigator.triangulate_position(observations)
    
    def navigation_summary(self) -> Dict:
        """Get navigation summary."""
        return {
            "position": self.position,
            "orientation_rad": self.orientation,
            "landmarks_in_map": len(self.navigator.landmarks),
            "landmarks_observed": len(self.navigator.observed_landmarks)
        }
