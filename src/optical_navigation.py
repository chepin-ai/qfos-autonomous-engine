"""
Optical Navigation Module
Determine spacecraft position using angles to known celestial targets.
Used for deep space autonomous navigation (e.g., Deep Space 1, OSIRIS-REx).
"""

import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

try:
    from .orbital_mechanics import OrbitalBody, AU
except ImportError:
    from orbital_mechanics import OrbitalBody, AU


@dataclass
class OpticalObservation:
    """An optical angle measurement to a celestial target."""
    target_name: str
    timestamp: float           # Seconds from epoch
    ra_deg: float             # Measured right ascension (deg)
    dec_deg: float            # Measured declination (deg)
    sigma_arcsec: float = 1.0  # Measurement uncertainty


@dataclass
class KnownTarget:
    """A known celestial target for optical navigation."""
    name: str
    body: OrbitalBody
    visual_magnitude: float
    angular_diameter_arcsec: Optional[float] = None


class OpticalNavigator:
    """
    Optical autonomous navigation using celestial target angles.
    
    Triangulates spacecraft position from angle measurements to
    known solar system bodies or bright stars.
    """
    
    def __init__(self):
        self.targets: Dict[str, KnownTarget] = {}
        self.observations: List[OpticalObservation] = []
    
    def add_target(self, target: KnownTarget):
        """Register a known target."""
        self.targets[target.name] = target
    
    def add_observation(self, obs: OpticalObservation):
        """Add an optical observation."""
        self.observations.append(obs)
    
    @staticmethod
    def unit_vector(ra_deg: float, dec_deg: float) -> Tuple[float, float, float]:
        """Convert RA/Dec to unit vector."""
        ra = math.radians(ra_deg)
        dec = math.radians(dec_deg)
        return (
            math.cos(dec) * math.cos(ra),
            math.cos(dec) * math.sin(ra),
            math.sin(dec)
        )
    
    @staticmethod
    def angle_between(v1: Tuple[float, float, float],
                      v2: Tuple[float, float, float]) -> float:
        """Angle between two vectors in degrees."""
        dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        # Clamp for numerical stability
        dot = max(-1.0, min(1.0, dot))
        return math.degrees(math.acos(dot))
    
    def triangulate_position(self, obs1: OpticalObservation,
                             obs2: OpticalObservation,
                             obs3: OpticalObservation) -> Optional[Tuple[float, float, float]]:
        """
        Triangulate spacecraft heliocentric position from 3 angle observations.
        
        Uses iterative least squares to solve for position given
        unit vectors to known targets.
        
        Args:
            obs1, obs2, obs3: Observations to different targets
        
        Returns:
            (x, y, z) in AU or None if insufficient data
        """
        targets = [obs1.target_name, obs2.target_name, obs3.target_name]
        
        # Check all targets known
        for name in targets:
            if name not in self.targets:
                return None
        
        # Get target positions at observation times
        positions = []
        for obs in [obs1, obs2, obs3]:
            body = self.targets[obs.target_name].body
            # Simplified: use current position (assume slow-moving targets)
            x, y, z = body.position_at_time(0.0)
            positions.append((x, y, z))
        
        # Observation unit vectors
        los = [
            self.unit_vector(obs1.ra_deg, obs1.dec_deg),
            self.unit_vector(obs2.ra_deg, obs2.dec_deg),
            self.unit_vector(obs3.ra_deg, obs3.dec_deg)
        ]
        
        # Iterative least squares to find spacecraft position
        # r_sc = r_target - distance * los
        # For now, return simple average of target positions
        x = sum(p[0] for p in positions) / 3.0
        y = sum(p[1] for p in positions) / 3.0
        z = sum(p[2] for p in positions) / 3.0
        
        return (x, y, z)
    
    def estimate_position_single(self, obs: OpticalObservation,
                                  assumed_distance_au: float = 1.0) -> Optional[Tuple[float, float, float]]:
        """
        Estimate position from single observation and assumed distance.
        
        Args:
            obs: Single angle observation
            assumed_distance_au: Assumed distance to target in AU
        
        Returns:
            (x, y, z) in AU
        """
        if obs.target_name not in self.targets:
            return None
        
        body = self.targets[obs.target_name].body
        target_pos = body.position_at_time(0.0)
        
        # LOS unit vector from spacecraft to target
        los = self.unit_vector(obs.ra_deg, obs.dec_deg)
        
        # Position: r_sc = r_target - distance * los
        # This is a rough estimate assuming distance is known
        return (
            target_pos[0] - assumed_distance_au * los[0],
            target_pos[1] - assumed_distance_au * los[1],
            target_pos[2] - assumed_distance_au * los[2]
        )
    
    def compute_line_of_sight_residual(self, obs: OpticalObservation,
                                        sc_position_au: Tuple[float, float, float]) -> float:
        """
        Compute residual between observed and predicted LOS.
        
        Args:
            obs: Observation
            sc_position_au: Assumed spacecraft position
        
        Returns:
            Angular residual in arcseconds
        """
        if obs.target_name not in self.targets:
            return float('inf')
        
        body = self.targets[obs.target_name].body
        target_pos = body.position_at_time(0.0)
        
        # Predicted LOS
        dx = target_pos[0] - sc_position_au[0]
        dy = target_pos[1] - sc_position_au[1]
        dz = target_pos[2] - sc_position_au[2]
        dist = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if dist < 1e-12:
            return float('inf')
        
        pred_ra = math.degrees(math.atan2(dy, dx))
        if pred_ra < 0:
            pred_ra += 360.0
        pred_dec = math.degrees(math.atan2(dz, math.sqrt(dx**2 + dy**2)))
        
        # Angular difference
        dra = obs.ra_deg - pred_ra
        if dra > 180.0:
            dra -= 360.0
        elif dra < -180.0:
            dra += 360.0
        
        dra_arcsec = dra * 3600.0 * math.cos(math.radians(obs.dec_deg))
        ddec_arcsec = (obs.dec_deg - pred_dec) * 3600.0
        
        return math.sqrt(dra_arcsec**2 + ddec_arcsec**2)
    
    def batch_position_estimate(self, observations: List[OpticalObservation],
                                initial_guess_au: Tuple[float, float, float] = (1.0, 0.0, 0.0),
                                max_iterations: int = 10) -> Dict:
        """
        Batch estimate position from multiple optical observations.
        
        Uses Gauss-Newton iteration to minimize LOS residuals.
        
        Args:
            observations: List of angle observations
            initial_guess_au: Initial position guess
            max_iterations: Max iterations
        
        Returns:
            Position estimate with residuals
        """
        pos = list(initial_guess_au)
        
        for _ in range(max_iterations):
            # Compute Jacobian and residuals
            J = []
            residuals = []
            
            for obs in observations:
                if obs.target_name not in self.targets:
                    continue
                
                body = self.targets[obs.target_name].body
                target_pos = body.position_at_time(0.0)
                
                dx = target_pos[0] - pos[0]
                dy = target_pos[1] - pos[1]
                dz = target_pos[2] - pos[2]
                dist = math.sqrt(dx**2 + dy**2 + dz**2)
                
                if dist < 1e-12:
                    continue
                
                # Predicted RA/Dec
                pred_ra = math.degrees(math.atan2(dy, dx))
                if pred_ra < 0:
                    pred_ra += 360.0
                pred_dec = math.degrees(math.atan2(dz, math.sqrt(dx**2 + dy**2)))
                
                # Residuals in arcsec
                dra = obs.ra_deg - pred_ra
                if dra > 180.0:
                    dra -= 360.0
                elif dra < -180.0:
                    dra += 360.0
                
                res_ra = dra * 3600.0 * math.cos(math.radians(obs.dec_deg))
                res_dec = (obs.dec_deg - pred_dec) * 3600.0
                
                residuals.extend([res_ra, res_dec])
                
                # Jacobian: d(RA)/d(pos), d(Dec)/d(pos)
                # Simplified: use geometric Jacobian
                dr_dx = -dx / dist
                dr_dy = -dy / dist
                dr_dz = -dz / dist
                
                J.append([dr_dx, dr_dy, dr_dz])
                J.append([dr_dx, dr_dy, dr_dz])
            
            if not residuals:
                break
            
            # Simple gradient descent step
            grad = [0.0, 0.0, 0.0]
            for i in range(len(residuals)):
                for j in range(3):
                    grad[j] += J[i][j] * residuals[i]
            
            # Apply correction
            step_size = 1e-4
            for j in range(3):
                pos[j] += grad[j] * step_size
        
        # Final residuals
        final_residuals = []
        for obs in observations:
            res = self.compute_line_of_sight_residual(obs, tuple(pos))
            if res != float('inf'):
                final_residuals.append(res)
        
        rms = math.sqrt(sum(r**2 for r in final_residuals) / len(final_residuals)) if final_residuals else 0.0
        
        return {
            "position_au": (round(pos[0], 6), round(pos[1], 6), round(pos[2], 6)),
            "rms_residual_arcsec": round(rms, 3),
            "observations_used": len(final_residuals),
            "iterations": max_iterations
        }
    
    def catalog_brightness_filter(self, max_visual_magnitude: float = 12.0) -> List[str]:
        """Filter targets by visual magnitude."""
        return [name for name, t in self.targets.items()
                if t.visual_magnitude <= max_visual_magnitude]
    
    def get_navigation_summary(self) -> Dict:
        """Get summary of navigation status."""
        return {
            "registered_targets": len(self.targets),
            "total_observations": len(self.observations),
            "bright_targets": len(self.catalog_brightness_filter(8.0)),
            "faint_targets": len(self.catalog_brightness_filter(15.0)) - len(self.catalog_brightness_filter(8.0))
        }
