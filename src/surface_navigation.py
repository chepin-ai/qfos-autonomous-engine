"""
Surface Navigation Module
Planetary surface navigation: dead reckoning, terrain-relative
navigation, hazard detection, and path planning for rovers/landers.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SurfacePosition:
    """Position on planetary surface."""
    lat_deg: float
    lon_deg: float
    elevation_m: float = 0.0
    heading_deg: float = 0.0


@dataclass
class TerrainCell:
    """A cell in the terrain map."""
    lat_idx: int
    lon_idx: int
    elevation_m: float
    slope_deg: float
    roughness_m: float
    hazard_level: str = "LOW"  # LOW, MEDIUM, HIGH
    traversable: bool = True


class TerrainMap:
    """
    Digital terrain map for surface navigation.
    """
    
    def __init__(self, lat_min_deg: float, lat_max_deg: float,
                 lon_min_deg: float, lon_max_deg: float,
                 resolution_m: float = 10.0,
                 planet_radius_m: float = 3396190.0):
        """
        Args:
            lat_min_deg, lat_max_deg: Latitude bounds
            lon_min_deg, lon_max_deg: Longitude bounds
            resolution_m: Grid resolution in meters
            planet_radius_m: Planet radius
        """
        self.lat_min = lat_min_deg
        self.lat_max = lat_max_deg
        self.lon_min = lon_min_deg
        self.lon_max = lon_max_deg
        self.resolution_m = resolution_m
        self.planet_radius = planet_radius_m
        
        # Compute grid size
        lat_range_m = math.radians(lat_max_deg - lat_min_deg) * planet_radius_m
        lon_range_m = (math.radians(lon_max_deg - lon_min_deg) *
                       planet_radius_m * math.cos(math.radians((lat_min_deg + lat_max_deg) / 2.0)))
        
        self.n_lat = max(2, int(lat_range_m / resolution_m))
        self.n_lon = max(2, int(lon_range_m / resolution_m))
        
        # Generate terrain
        self.grid: List[List[TerrainCell]] = []
        self._generate_terrain()
    
    def _generate_terrain(self):
        """Generate synthetic terrain."""
        random.seed(42)
        for i in range(self.n_lat):
            row = []
            lat = self.lat_min + (self.lat_max - self.lat_min) * i / (self.n_lat - 1)
            
            for j in range(self.n_lon):
                lon = self.lon_min + (self.lon_max - self.lon_min) * j / (self.n_lon - 1)
                
                # Synthetic elevation
                elev = (math.sin(lat * 0.5) * 50.0 +
                        math.cos(lon * 0.3) * 30.0 +
                        random.uniform(-5.0, 5.0))
                
                # Compute slope from neighbors
                slope = random.uniform(0.0, 15.0)
                if abs(elev) > 40.0:
                    slope += 10.0
                
                roughness = random.uniform(0.0, 2.0)
                
                # Hazard classification
                if slope > 20.0 or roughness > 1.5:
                    hazard = "HIGH"
                    traversable = False
                elif slope > 10.0 or roughness > 1.0:
                    hazard = "MEDIUM"
                    traversable = True
                else:
                    hazard = "LOW"
                    traversable = True
                
                row.append(TerrainCell(
                    lat_idx=i, lon_idx=j,
                    elevation_m=round(elev, 2),
                    slope_deg=round(slope, 2),
                    roughness_m=round(roughness, 3),
                    hazard_level=hazard,
                    traversable=traversable
                ))
            
            self.grid.append(row)
    
    def get_cell(self, lat_deg: float, lon_deg: float) -> Optional[TerrainCell]:
        """Get terrain cell at position."""
        if not (self.lat_min <= lat_deg <= self.lat_max and
                self.lon_min <= lon_deg <= self.lon_max):
            return None
        
        i = int((lat_deg - self.lat_min) / (self.lat_max - self.lat_min) * (self.n_lat - 1))
        j = int((lon_deg - self.lon_min) / (self.lon_max - self.lon_min) * (self.n_lon - 1))
        
        i = max(0, min(i, self.n_lat - 1))
        j = max(0, min(j, self.n_lon - 1))
        
        return self.grid[i][j]
    
    def elevation_at(self, lat_deg: float, lon_deg: float) -> float:
        """Get elevation at position."""
        cell = self.get_cell(lat_deg, lon_deg)
        return cell.elevation_m if cell else 0.0
    
    def slope_at(self, lat_deg: float, lon_deg: float) -> float:
        """Get slope at position."""
        cell = self.get_cell(lat_deg, lon_deg)
        return cell.slope_deg if cell else 0.0


class SurfaceNavigator:
    """
    Surface navigator for planetary rovers/landers.
    
    Dead reckoning, terrain-relative position updates,
    and hazard avoidance path planning.
    """
    
    def __init__(self, terrain: TerrainMap,
                 wheel_radius_m: float = 0.3,
                 wheel_base_m: float = 2.0):
        """
        Args:
            terrain: Terrain map
            wheel_radius_m: Wheel radius
            wheel_base_m: Wheelbase
        """
        self.terrain = terrain
        self.wheel_radius = wheel_radius_m
        self.wheel_base = wheel_base_m
        self.position = SurfacePosition(lat_deg=0.0, lon_deg=0.0)
        self.position_history: List[SurfacePosition] = []
        self.odometry_error_m = 0.0
    
    def set_position(self, position: SurfacePosition):
        """Set current position."""
        self.position = position
        self.position_history.append(position)
    
    def dead_reckoning(self, wheel_speed_left_rpm: float,
                       wheel_speed_right_rpm: float,
                       dt_s: float) -> SurfacePosition:
        """
        Update position by dead reckoning.
        
        Args:
            wheel_speed_left_rpm: Left wheel speed
            wheel_speed_right_rpm: Right wheel speed
            dt_s: Time step
        
        Returns:
            New position estimate
        """
        # Convert to m/s
        v_left = wheel_speed_left_rpm * 2.0 * math.pi * self.wheel_radius / 60.0
        v_right = wheel_speed_right_rpm * 2.0 * math.pi * self.wheel_radius / 60.0
        
        # Differential drive kinematics
        v = (v_left + v_right) / 2.0
        omega = (v_right - v_left) / self.wheel_base
        
        heading_rad = math.radians(self.position.heading_deg)
        
        # Update
        new_heading = self.position.heading_deg + math.degrees(omega * dt_s)
        avg_heading = math.radians((self.position.heading_deg + new_heading) / 2.0)
        
        distance = v * dt_s
        
        # Convert to lat/lon
        lat_change = math.degrees(distance * math.cos(avg_heading) / self.terrain.planet_radius)
        lon_change = math.degrees(distance * math.sin(avg_heading) /
                                  (self.terrain.planet_radius * math.cos(math.radians(self.position.lat_deg))))
        
        new_pos = SurfacePosition(
            lat_deg=self.position.lat_deg + lat_change,
            lon_deg=self.position.lon_deg + lon_change,
            elevation_m=self.terrain.elevation_at(
                self.position.lat_deg + lat_change,
                self.position.lon_deg + lon_change
            ),
            heading_deg=new_heading
        )
        
        # Accumulate odometry error (~2% of distance)
        self.odometry_error_m += abs(distance) * 0.02
        
        self.position = new_pos
        self.position_history.append(new_pos)
        
        return new_pos
    
    def terrain_relative_update(self, observed_features: List[Dict],
                                actual_features: List[Dict]) -> SurfacePosition:
        """
        Update position using terrain-relative navigation.
        
        Matches observed terrain features to map.
        
        Args:
            observed_features: Observed feature positions
            actual_features: Map feature positions
        
        Returns:
            Corrected position
        """
        if len(observed_features) < 2 or len(actual_features) < 2:
            return self.position
        
        # Simple shift based on first feature match
        dx = actual_features[0]["x"] - observed_features[0]["x"]
        dy = actual_features[0]["y"] - observed_features[0]["y"]
        
        lat_correction = math.degrees(dy / self.terrain.planet_radius)
        lon_correction = math.degrees(dx / (self.terrain.planet_radius *
                                            math.cos(math.radians(self.position.lat_deg))))
        
        self.position.lat_deg += lat_correction
        self.position.lon_deg += lon_correction
        self.odometry_error_m = max(0.0, self.odometry_error_m - 5.0)
        
        return self.position
    
    def compute_bearing(self, target: SurfacePosition) -> float:
        """
        Compute bearing to target.
        
        Args:
            target: Target position
        
        Returns:
            Bearing in degrees
        """
        dlat = math.radians(target.lat_deg - self.position.lat_deg)
        dlon = math.radians(target.lon_deg - self.position.lon_deg)
        
        lat1 = math.radians(self.position.lat_deg)
        lat2 = math.radians(target.lat_deg)
        
        y = math.sin(dlon) * math.cos(lat2)
        x = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
        
        bearing = math.degrees(math.atan2(y, x))
        if bearing < 0:
            bearing += 360.0
        
        return bearing
    
    def distance_to(self, target: SurfacePosition) -> float:
        """
        Compute surface distance to target.
        
        Args:
            target: Target position
        
        Returns:
            Distance in meters
        """
        dlat = math.radians(target.lat_deg - self.position.lat_deg)
        dlon = math.radians(target.lon_deg - self.position.lon_deg)
        
        lat1 = math.radians(self.position.lat_deg)
        lat2 = math.radians(target.lat_deg)
        
        a = (math.sin(dlat/2)**2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2.0 * math.asin(min(1.0, math.sqrt(a)))
        
        return self.terrain.planet_radius * c
    
    def plan_path(self, target: SurfacePosition,
                  max_slope_deg: float = 15.0) -> List[SurfacePosition]:
        """
        Plan path to target avoiding hazards.
        
        Simple A* on terrain grid.
        
        Args:
            target: Target position
            max_slope_deg: Maximum allowable slope
        
        Returns:
            List of waypoints
        """
        # Simple straight-line with hazard checks
        path = [self.position]
        
        current = self.position
        max_steps = 100
        steps = 0
        
        while self.distance_to(target) > self.terrain.resolution_m and steps < max_steps:
            bearing = self.compute_bearing(target)
            step_m = min(self.terrain.resolution_m, self.distance_to(target))
            
            # Check ahead for hazards
            test_lat = current.lat_deg + math.degrees(
                step_m * math.cos(math.radians(bearing)) / self.terrain.planet_radius
            )
            test_lon = current.lon_deg + math.degrees(
                step_m * math.sin(math.radians(bearing)) /
                (self.terrain.planet_radius * math.cos(math.radians(current.lat_deg)))
            )
            
            cell = self.terrain.get_cell(test_lat, test_lon)
            if cell and not cell.traversable:
                # Turn 30 degrees and try again
                bearing += 30.0
                test_lat = current.lat_deg + math.degrees(
                    step_m * math.cos(math.radians(bearing)) / self.terrain.planet_radius
                )
                test_lon = current.lon_deg + math.degrees(
                    step_m * math.sin(math.radians(bearing)) /
                    (self.terrain.planet_radius * math.cos(math.radians(current.lat_deg)))
                )
            
            current = SurfacePosition(
                lat_deg=test_lat, lon_deg=test_lon,
                elevation_m=self.terrain.elevation_at(test_lat, test_lon),
                heading_deg=bearing
            )
            path.append(current)
            steps += 1
        
        path.append(target)
        return path
    
    def navigation_status(self) -> Dict:
        """Get navigation status."""
        return {
            "position": {
                "lat_deg": round(self.position.lat_deg, 6),
                "lon_deg": round(self.position.lon_deg, 6),
                "elevation_m": round(self.position.elevation_m, 2)
            },
            "heading_deg": round(self.position.heading_deg, 2),
            "odometry_error_m": round(self.odometry_error_m, 3),
            "position_history_length": len(self.position_history)
        }
