"""
Unit tests for surface navigation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from surface_navigation import TerrainMap, SurfaceNavigator, SurfacePosition


class TestTerrainMap(unittest.TestCase):
    """Test terrain map."""
    
    def setUp(self):
        self.terrain = TerrainMap(
            lat_min_deg=-0.5, lat_max_deg=0.5,
            lon_min_deg=-0.5, lon_max_deg=0.5,
            resolution_m=500.0, planet_radius_m=3396190.0
        )
    
    def test_grid_created(self):
        """Should create grid."""
        self.assertGreater(self.terrain.n_lat, 1)
        self.assertGreater(self.terrain.n_lon, 1)
        print(f"  [PASS] Grid: {self.terrain.n_lat}x{self.terrain.n_lon}")
    
    def test_get_cell(self):
        """Should get cell."""
        cell = self.terrain.get_cell(0.0, 0.0)
        self.assertIsNotNone(cell)
        self.assertIn(cell.hazard_level, ["LOW", "MEDIUM", "HIGH"])
        print(f"  [PASS] Cell: elev={cell.elevation_m:.1f}m, slope={cell.slope_deg:.1f}deg")
    
    def test_elevation(self):
        """Should return elevation."""
        elev = self.terrain.elevation_at(0.0, 0.0)
        self.assertIsInstance(elev, float)
        print(f"  [PASS] Elevation: {elev:.1f}m")
    
    def test_out_of_bounds(self):
        """Should handle out of bounds."""
        cell = self.terrain.get_cell(100.0, 100.0)
        self.assertIsNone(cell)
        print("  [PASS] Out of bounds: None")


class TestSurfaceNavigator(unittest.TestCase):
    """Test surface navigator."""
    
    def setUp(self):
        self.terrain = TerrainMap(
            lat_min_deg=-0.1, lat_max_deg=0.1,
            lon_min_deg=-0.1, lon_max_deg=0.1,
            resolution_m=500.0, planet_radius_m=3396190.0
        )
        self.nav = SurfaceNavigator(self.terrain)
        self.nav.set_position(SurfacePosition(lat_deg=0.0, lon_deg=0.0, heading_deg=0.0))
    
    def test_set_position(self):
        """Should set position."""
        self.assertEqual(self.nav.position.lat_deg, 0.0)
        print("  [PASS] Position set")
    
    def test_dead_reckoning(self):
        """Should update by dead reckoning."""
        pos = self.nav.dead_reckoning(wheel_speed_left_rpm=10.0,
                                       wheel_speed_right_rpm=10.0, dt_s=60.0)
        self.assertNotEqual(pos.lat_deg, 0.0)
        print(f"  [PASS] DR: lat={pos.lat_deg:.6f}, lon={pos.lon_deg:.6f}")
    
    def test_dead_reckoning_turn(self):
        """Should turn with differential drive."""
        pos = self.nav.dead_reckoning(wheel_speed_left_rpm=5.0,
                                       wheel_speed_right_rpm=10.0, dt_s=60.0)
        self.assertNotEqual(pos.heading_deg, 0.0)
        print(f"  [PASS] Turn: heading={pos.heading_deg:.2f}deg")
    
    def test_compute_bearing(self):
        """Should compute bearing."""
        target = SurfacePosition(lat_deg=0.0, lon_deg=1.0)
        bearing = self.nav.compute_bearing(target)
        self.assertGreater(bearing, 80.0)
        self.assertLess(bearing, 100.0)
        print(f"  [PASS] Bearing: {bearing:.1f}deg")
    
    def test_distance_to(self):
        """Should compute distance."""
        target = SurfacePosition(lat_deg=0.0, lon_deg=1.0)
        dist = self.nav.distance_to(target)
        self.assertGreater(dist, 50000.0)
        print(f"  [PASS] Distance: {dist/1000:.1f} km")
    
    def test_plan_path(self):
        """Should plan path."""
        target = SurfacePosition(lat_deg=0.05, lon_deg=0.0)
        path = self.nav.plan_path(target)
        self.assertGreater(len(path), 1)
        print(f"  [PASS] Path: {len(path)} waypoints")
    
    def test_navigation_status(self):
        """Should provide status."""
        status = self.nav.navigation_status()
        self.assertIn("position", status)
        self.assertIn("heading_deg", status)
        print(f"  [PASS] Status: heading={status['heading_deg']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
