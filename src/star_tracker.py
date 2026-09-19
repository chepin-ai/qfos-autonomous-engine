"""
Star Tracker Module
Star identification, attitude determination from star images,
and catalog-based attitude estimation.
"""

import math
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Star:
    """A star in the catalog."""
    id: int
    ra_deg: float  # Right ascension
    dec_deg: float  # Declination
    magnitude: float  # Visual magnitude
    
    def to_unit_vector(self) -> Tuple[float, float, float]:
        """Convert to 3D unit vector."""
        ra = math.radians(self.ra_deg)
        dec = math.radians(self.dec_deg)
        x = math.cos(dec) * math.cos(ra)
        y = math.cos(dec) * math.sin(ra)
        z = math.sin(dec)
        return (x, y, z)
    
    def angular_distance_deg(self, other: 'Star') -> float:
        """Angular distance to another star."""
        # Haversine formula
        ra1, dec1 = math.radians(self.ra_deg), math.radians(self.dec_deg)
        ra2, dec2 = math.radians(other.ra_deg), math.radians(other.dec_deg)
        
        d_ra = ra2 - ra1
        d_dec = dec2 - dec1
        
        a = (math.sin(d_dec/2)**2 +
             math.cos(dec1) * math.cos(dec2) * math.sin(d_ra/2)**2)
        c = 2 * math.asin(min(1.0, math.sqrt(a)))
        
        return math.degrees(c)


@dataclass
class StarObservation:
    """An observed star in the sensor frame."""
    x: float  # Unit vector x in sensor frame
    y: float
    z: float
    magnitude: float
    pixel_x: float = 0.0
    pixel_y: float = 0.0


class StarCatalog:
    """
    Star catalog for star tracker.
    
    Provides star lookup and pattern matching.
    """
    
    def __init__(self, stars: Optional[List[Star]] = None):
        self.stars = stars or []
    
    @staticmethod
    def create_sample_catalog(num_stars: int = 100,
                               magnitude_limit: float = 6.0) -> 'StarCatalog':
        """
        Create a sample star catalog.
        
        Args:
            num_stars: Number of stars
            magnitude_limit: Brightness limit
        
        Returns:
            Sample catalog
        """
        random.seed(42)
        stars = []
        
        for i in range(num_stars):
            ra = random.uniform(0.0, 360.0)
            dec = math.degrees(math.asin(random.uniform(-1.0, 1.0)))
            mag = random.uniform(1.0, magnitude_limit)
            stars.append(Star(id=i, ra_deg=ra, dec_deg=dec, magnitude=mag))
        
        return StarCatalog(stars)
    
    def stars_in_fov(self, center_ra_deg: float, center_dec_deg: float,
                     fov_deg: float, magnitude_limit: float = 6.0) -> List[Star]:
        """
        Find stars within field of view.
        
        Args:
            center_ra_deg: FOV center RA
            center_dec_deg: FOV center Dec
            fov_deg: Field of view diameter
            magnitude_limit: Brightness limit
        
        Returns:
            Stars in FOV
        """
        center = Star(id=-1, ra_deg=center_ra_deg, dec_deg=center_dec_deg, magnitude=0.0)
        
        result = []
        for star in self.stars:
            if star.magnitude > magnitude_limit:
                continue
            if center.angular_distance_deg(star) <= fov_deg / 2.0:
                result.append(star)
        
        # Sort by brightness
        result.sort(key=lambda s: s.magnitude)
        return result
    
    def find_star_pair(self, star1_id: int, star2_id: int) -> Optional[Tuple[Star, Star]]:
        """Find a pair of stars by ID."""
        s1 = next((s for s in self.stars if s.id == star1_id), None)
        s2 = next((s for s in self.stars if s.id == star2_id), None)
        if s1 and s2:
            return (s1, s2)
        return None


class StarTracker:
    """
    Star tracker for attitude determination.
    
    Matches observed stars to catalog and computes
    spacecraft attitude.
    """
    
    def __init__(self, catalog: StarCatalog,
                 fov_deg: float = 8.0,
                 resolution_px: int = 1024,
                 pixel_size_um: float = 15.0,
                 focal_length_mm: float = 50.0):
        """
        Args:
            catalog: Star catalog
            fov_deg: Field of view
            resolution_px: Sensor resolution
            pixel_size_um: Pixel size
            focal_length_mm: Focal length
        """
        self.catalog = catalog
        self.fov_deg = fov_deg
        self.resolution = resolution_px
        self.pixel_size_um = pixel_size_um
        self.focal_length_mm = focal_length_mm
        
        # Compute focal length in pixels
        self.focal_length_px = focal_length_mm * 1000.0 / pixel_size_um
    
    def _compute_fov_from_focal(self) -> float:
        """Compute FOV from focal length."""
        sensor_size_mm = self.resolution * self.pixel_size_um / 1000.0
        fov = 2.0 * math.degrees(math.atan(sensor_size_mm / (2.0 * self.focal_length_mm)))
        return fov
    
    def generate_observation(self, attitude_matrix: List[List[float]],
                             center_ra_deg: float = 0.0,
                             center_dec_deg: float = 0.0,
                             noise_arcsec: float = 5.0) -> List[StarObservation]:
        """
        Generate simulated star observation.
        
        Args:
            attitude_matrix: 3x3 DCM body->inertial
            center_ra_deg: Pointing direction RA
            center_dec_deg: Pointing direction Dec
            noise_arcsec: Centroid noise
        
        Returns:
            Observed stars
        """
        stars = self.catalog.stars_in_fov(
            center_ra_deg, center_dec_deg, self.fov_deg
        )
        
        observations = []
        for star in stars:
            # Star in inertial frame
            v_inertial = star.to_unit_vector()
            
            # Transform to body frame using attitude matrix
            v_body = (
                attitude_matrix[0][0]*v_inertial[0] + attitude_matrix[0][1]*v_inertial[1] + attitude_matrix[0][2]*v_inertial[2],
                attitude_matrix[1][0]*v_inertial[0] + attitude_matrix[1][1]*v_inertial[1] + attitude_matrix[1][2]*v_inertial[2],
                attitude_matrix[2][0]*v_inertial[0] + attitude_matrix[2][1]*v_inertial[1] + attitude_matrix[2][2]*v_inertial[2],
            )
            
            # Check if in FOV (z > 0)
            if v_body[2] <= 0:
                continue
            
            # Project to focal plane
            pixel_scale = self.fov_deg / self.resolution  # deg/pixel
            pixel_x = v_body[0] / v_body[2] / math.radians(pixel_scale) + self.resolution / 2.0
            pixel_y = v_body[1] / v_body[2] / math.radians(pixel_scale) + self.resolution / 2.0
            
            # Add noise
            noise_px = noise_arcsec / 3600.0 / pixel_scale
            pixel_x += random.gauss(0.0, noise_px)
            pixel_y += random.gauss(0.0, noise_px)
            
            # Back to unit vector
            x = (pixel_x - self.resolution / 2.0) * math.radians(pixel_scale)
            y = (pixel_y - self.resolution / 2.0) * math.radians(pixel_scale)
            z = 1.0
            norm = math.sqrt(x**2 + y**2 + z**2)
            
            observations.append(StarObservation(
                x=x/norm, y=y/norm, z=z/norm,
                magnitude=star.magnitude,
                pixel_x=pixel_x, pixel_y=pixel_y
            ))
        
        return observations
    
    def attitude_determination_triad(self, obs1: StarObservation,
                                      obs2: StarObservation,
                                      catalog_star1: Star,
                                      catalog_star2: Star) -> List[List[float]]:
        """
        TRIAD attitude determination.
        
        Uses two star observations to compute attitude.
        
        Args:
            obs1: First observed star
            obs2: Second observed star
            catalog_star1: First catalog star
            catalog_star2: Second catalog star
        
        Returns:
            3x3 attitude matrix body->inertial
        """
        # Body frame vectors
        b1 = (obs1.x, obs1.y, obs1.z)
        b2 = (obs2.x, obs2.y, obs2.z)
        
        # Inertial frame vectors
        r1 = catalog_star1.to_unit_vector()
        r2 = catalog_star2.to_unit_vector()
        
        # TRIAD algorithm
        # t1 = r1
        # t2 = r1 x r2 / |r1 x r2|
        # t3 = t1 x t2
        
        def cross(a, b):
            return (a[1]*b[2] - a[2]*b[1],
                    a[2]*b[0] - a[0]*b[2],
                    a[0]*b[1] - a[1]*b[0])
        
        def normalize(v):
            n = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            if n < 1e-10:
                return (1.0, 0.0, 0.0)
            return (v[0]/n, v[1]/n, v[2]/n)
        
        t1_r = normalize(r1)
        t2_r = normalize(cross(r1, r2))
        t3_r = cross(t1_r, t2_r)
        
        t1_b = normalize(b1)
        t2_b = normalize(cross(b1, b2))
        t3_b = cross(t1_b, t2_b)
        
        # Attitude matrix A = [t1_r t2_r t3_r] * [t1_b t2_b t3_b]^T
        # Each column of A is a body axis in inertial frame
        A = [
            [t1_r[0]*t1_b[0] + t2_r[0]*t2_b[0] + t3_r[0]*t3_b[0],
             t1_r[0]*t1_b[1] + t2_r[0]*t2_b[1] + t3_r[0]*t3_b[1],
             t1_r[0]*t1_b[2] + t2_r[0]*t2_b[2] + t3_r[0]*t3_b[2]],
            [t1_r[1]*t1_b[0] + t2_r[1]*t2_b[0] + t3_r[1]*t3_b[0],
             t1_r[1]*t1_b[1] + t2_r[1]*t2_b[1] + t3_r[1]*t3_b[1],
             t1_r[1]*t1_b[2] + t2_r[1]*t2_b[2] + t3_r[1]*t3_b[2]],
            [t1_r[2]*t1_b[0] + t2_r[2]*t2_b[0] + t3_r[2]*t3_b[0],
             t1_r[2]*t1_b[1] + t2_r[2]*t2_b[1] + t3_r[2]*t3_b[1],
             t1_r[2]*t1_b[2] + t2_r[2]*t2_b[2] + t3_r[2]*t3_b[2]],
        ]
        
        return A
    
    def identify_stars(self, observations: List[StarObservation],
                       center_ra_deg: float,
                       center_dec_deg: float) -> List[Tuple[StarObservation, Optional[Star]]]:
        """
        Identify observed stars from catalog.
        
        Args:
            observations: Observed stars
            center_ra_deg: Estimated pointing RA
            center_dec_deg: Estimated pointing Dec
        
        Returns:
            List of (observation, matched_star) tuples
        """
        candidates = self.catalog.stars_in_fov(
            center_ra_deg, center_dec_deg, self.fov_deg * 1.5
        )
        
        results = []
        for obs in observations:
            best_match = None
            best_error = float('inf')
            
            for star in candidates:
                # Simple nearest-neighbor in angular space
                # Convert obs to RA/Dec
                ra_obs = math.degrees(math.atan2(obs.y, obs.x))
                if ra_obs < 0:
                    ra_obs += 360.0
                dec_obs = math.degrees(math.asin(max(-1.0, min(1.0, obs.z))))
                
                error = abs(star.ra_deg - ra_obs) + abs(star.dec_deg - dec_obs)
                
                if error < best_error and error < 2.0:  # 2 degree tolerance
                    best_error = error
                    best_match = star
            
            results.append((obs, best_match))
        
        return results
    
    def compute_attitude_accuracy(self, attitude_matrix: List[List[float]],
                                   true_attitude: List[List[float]]) -> float:
        """
        Compute attitude determination error.
        
        Args:
            attitude_matrix: Estimated attitude
            true_attitude: True attitude
        
        Returns:
            Error in degrees
        """
        # Trace of error matrix
        trace = sum(attitude_matrix[i][j] * true_attitude[i][j]
                    for i in range(3) for j in range(3))
        
        # Error angle: cos(theta) = (trace - 1) / 2
        cos_theta = (trace - 1.0) / 2.0
        cos_theta = max(-1.0, min(1.0, cos_theta))
        
        return math.degrees(math.acos(cos_theta))
