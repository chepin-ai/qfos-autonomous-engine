"""
Landing Guidance Module
Powered descent, hazard detection, and terrain-relative
navigation for autonomous landing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LandingSite:
    """Candidate landing site."""
    lat: float  # degrees
    lon: float  # degrees
    elevation: float  # meters
    slope_deg: float  # terrain slope in degrees
    roughness: float  # roughness metric (0-1)
    hazard_score: float = 0.0  # 0 = safe, 1 = hazardous


class HazardDetector:
    """
    Detect landing hazards from terrain data.
    """
    
    def __init__(self, max_slope_deg: float = 15.0,
                 max_roughness: float = 0.3):
        """
        Args:
            max_slope_deg: Maximum acceptable slope (degrees)
            max_roughness: Maximum acceptable roughness
        """
        self.max_slope = max_slope_deg
        self.max_roughness = max_roughness
    
    def assess_site(self, site: LandingSite) -> float:
        """
        Assess landing site safety.
        
        Args:
            site: Landing site
        
        Returns:
            Safety score (0-1, higher = safer)
        """
        slope_ok = max(0, 1 - site.slope_deg / self.max_slope)
        rough_ok = max(0, 1 - site.roughness / self.max_roughness)
        hazard_ok = max(0, 1 - site.hazard_score)
        
        return (slope_ok + rough_ok + hazard_ok) / 3.0
    
    def is_safe(self, site: LandingSite) -> bool:
        """Check if site is safe for landing."""
        return (site.slope_deg <= self.max_slope and
                site.roughness <= self.max_roughness and
                site.hazard_score < 0.5)
    
    def rank_sites(self, sites: List[LandingSite]) -> List[Tuple[LandingSite, float]]:
        """
        Rank sites by safety.
        
        Args:
            sites: List of sites
        
        Returns:
            Sorted list of (site, score)
        """
        scored = [(s, self.assess_site(s)) for s in sites]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


class PoweredDescent:
    """
    Powered descent guidance.
    """
    
    def __init__(self, g: float = 1.62,  # Moon gravity m/s^2
                 max_thrust: float = 45000.0,  # N
                 dry_mass: float = 2000.0,  # kg
                 isp: float = 310.0):  # seconds
        """
        Args:
            g: Surface gravity (m/s^2)
            max_thrust: Max engine thrust (N)
            dry_mass: Vehicle dry mass (kg)
            isp: Specific impulse (s)
        """
        self.g = g
        self.max_thrust = max_thrust
        self.dry_mass = dry_mass
        self.isp = isp
        self.ve = isp * 9.80665  # exhaust velocity (m/s)
    
    def delta_v_budget(self, altitude: float, velocity: float) -> float:
        """
        Estimate delta-v needed for landing.
        
        Args:
            altitude: Current altitude (m)
            velocity: Current velocity magnitude (m/s)
        
        Returns:
            Required delta-v (m/s)
        """
        # Gravity + kinetic energy
        gravity_loss = math.sqrt(2 * self.g * altitude)
        return velocity + gravity_loss * 0.5
    
    def fuel_required(self, delta_v: float, wet_mass: float) -> float:
        """
        Calculate fuel required.
        
        Args:
            delta_v: Required delta-v (m/s)
            wet_mass: Current wet mass (kg)
        
        Returns:
            Fuel mass (kg)
        """
        if self.ve <= 0:
            return float('inf')
        final_mass = wet_mass * math.exp(-delta_v / self.ve)
        return wet_mass - final_mass
    
    def thrust_profile(self, altitude: float, velocity: float,
                      mass: float) -> Tuple[float, float]:
        """
        Compute thrust magnitude and angle.
        
        Args:
            altitude: Altitude (m)
            velocity: Velocity (m/s, positive downward)
            mass: Current mass (kg)
        
        Returns:
            (thrust_N, angle_deg) angle from vertical
        """
        # Simple gravity turn
        weight = mass * self.g
        
        if altitude < 100:
            # Terminal descent: hover
            thrust = weight * 1.1
            angle = 0.0
        elif velocity > 50:
            # High speed: angled thrust to kill horizontal
            thrust = min(self.max_thrust, weight * 2.0)
            angle = 30.0
        else:
            # Normal descent
            thrust = weight * 1.3
            angle = 5.0
        
        return (min(thrust, self.max_thrust), angle)
    
    def time_to_land(self, altitude: float, velocity: float) -> float:
        """
        Estimate time to landing.
        
        Args:
            altitude: Altitude (m)
            velocity: Current downward velocity (m/s)
        
        Returns:
            Estimated time (s)
        """
        if velocity > 0:
            return altitude / velocity
        return altitude / 10.0  # default descent rate


class TerrainRelativeNav:
    """
    Terrain-relative navigation for landing.
    """
    
    def __init__(self, map_resolution: float = 10.0):  # meters
        """
        Args:
            map_resolution: Terrain map resolution (m)
        """
        self.map_resolution = map_resolution
        self.terrain_map: Dict[Tuple[int, int], float] = {}  # (x,y) -> elevation
    
    def add_terrain_point(self, x: float, y: float, elevation: float):
        """Add terrain point."""
        ix = int(round(x / self.map_resolution))
        iy = int(round(y / self.map_resolution))
        self.terrain_map[(ix, iy)] = elevation
    
    def get_elevation(self, x: float, y: float) -> Optional[float]:
        """Get elevation at position."""
        ix = int(round(x / self.map_resolution))
        iy = int(round(y / self.map_resolution))
        return self.terrain_map.get((ix, iy))
    
    def estimate_slope(self, x: float, y: float) -> float:
        """
        Estimate terrain slope at position.
        
        Args:
            x, y: Position (m)
        
        Returns:
            Slope in degrees
        """
        ix = int(round(x / self.map_resolution))
        iy = int(round(y / self.map_resolution))
        
        # Sample neighbors
        samples = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                h = self.terrain_map.get((ix + dx, iy + dy))
                if h is not None:
                    dist = math.sqrt(dx**2 + dy**2) * self.map_resolution
                    if dist > 0:
                        samples.append((h, dist))
        
        if not samples:
            return 0.0
        
        # Max slope
        max_slope = 0.0
        for h, dist in samples:
            center = self.terrain_map.get((ix, iy), h)
            slope = math.degrees(math.atan(abs(h - center) / dist))
            max_slope = max(max_slope, slope)
        
        return max_slope


class LandingGuidance:
    """
    Unified landing guidance controller.
    """
    
    def __init__(self):
        self.hazard = HazardDetector()
        self.descent = PoweredDescent()
        self.terrain = TerrainRelativeNav()
        self.target_site: Optional[LandingSite] = None
        self.current_altitude: float = 0.0
        self.current_velocity: float = 0.0
        self.current_mass: float = 0.0
    
    def select_landing_site(self, candidates: List[LandingSite]) -> Optional[LandingSite]:
        """
        Select best landing site from candidates.
        
        Args:
            candidates: Candidate sites
        
        Returns:
            Best site or None
        """
        ranked = self.hazard.rank_sites(candidates)
        for site, score in ranked:
            if self.hazard.is_safe(site):
                self.target_site = site
                return site
        return None
    
    def update_state(self, altitude: float, velocity: float, mass: float):
        """Update vehicle state."""
        self.current_altitude = altitude
        self.current_velocity = velocity
        self.current_mass = mass
    
    def compute_guidance(self) -> Dict:
        """
        Compute landing guidance commands.
        
        Returns:
            Guidance commands
        """
        dv = self.descent.delta_v_budget(self.current_altitude, self.current_velocity)
        fuel = self.descent.fuel_required(dv, self.current_mass)
        thrust, angle = self.descent.thrust_profile(
            self.current_altitude, self.current_velocity, self.current_mass
        )
        t_land = self.descent.time_to_land(self.current_altitude, self.current_velocity)
        
        return {
            "delta_v": dv,
            "fuel_required": fuel,
            "thrust": thrust,
            "thrust_angle": angle,
            "time_to_land": t_land,
            "target_site": self.target_site
        }
    
    def add_terrain_data(self, x: float, y: float, elevation: float):
        """Add terrain data."""
        self.terrain.add_terrain_point(x, y, elevation)
    
    def guidance_summary(self) -> Dict:
        """Get guidance summary."""
        return {
            "altitude": self.current_altitude,
            "velocity": self.current_velocity,
            "mass": self.current_mass,
            "target": self.target_site.lat if self.target_site else None,
            "terrain_points": len(self.terrain.terrain_map)
        }
