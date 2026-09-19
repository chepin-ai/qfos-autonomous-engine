"""
Unit tests for coverage analysis module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from coverage_analysis import CoverageAnalyzer, GroundTarget


class TestCoverageAnalyzer(unittest.TestCase):
    """Test coverage analysis."""
    
    def setUp(self):
        self.analyzer = CoverageAnalyzer(
            satellite_altitude_km=400.0,
            inclination_deg=51.6
        )
    
    def test_period_computation(self):
        """Should compute orbital period."""
        self.assertGreater(self.analyzer.period_min, 90.0)
        self.assertLess(self.analyzer.period_min, 100.0)
        print(f"  [PASS] Period: {self.analyzer.period_min:.2f} min")
    
    def test_can_access(self):
        """Should determine access."""
        # Satellite directly overhead
        access = self.analyzer.can_access(
            target_lat_deg=0.0, target_lon_deg=0.0,
            satellite_lat_deg=0.0, satellite_lon_deg=0.0
        )
        self.assertTrue(access)
        
        # Far away
        access = self.analyzer.can_access(
            target_lat_deg=0.0, target_lon_deg=0.0,
            satellite_lat_deg=60.0, satellite_lon_deg=0.0
        )
        self.assertFalse(access)
        print("  [PASS] Access determination")
    
    def test_compute_access_windows(self):
        """Should compute access windows."""
        target = GroundTarget(name="Beijing", latitude_deg=39.9, longitude_deg=116.4)
        passes = self.analyzer.compute_access_windows(target, simulation_duration_min=1440.0)
        self.assertIsInstance(passes, list)
        print(f"  [PASS] Passes: {len(passes)} in 24hr")
    
    def test_revisit_time(self):
        """Should compute revisit statistics."""
        target = GroundTarget(name="Test", latitude_deg=0.0, longitude_deg=0.0)
        stats = self.analyzer.revisit_time(target, simulation_duration_min=2880.0)
        self.assertIn("num_passes", stats)
        self.assertIn("avg_revisit_min", stats)
        print(f"  [PASS] Revisit: {stats['num_passes']} passes")
    
    def test_swath_width(self):
        """Should compute swath width."""
        swath = self.analyzer.swath_width_km()
        self.assertGreater(swath, 1000.0)
        self.assertLess(swath, 5000.0)
        print(f"  [PASS] Swath: {swath:.1f} km")
    
    def test_coverage_fraction(self):
        """Should compute coverage fraction."""
        frac = self.analyzer.coverage_fraction(latitude_band_deg=(-51.6, 51.6))
        self.assertGreater(frac, 0.5)
        self.assertLessEqual(frac, 1.0)
        print(f"  [PASS] Coverage: {frac*100:.1f}%")
    
    def test_elevation_angle(self):
        """Should convert elevation to earth angle."""
        angle = self.analyzer.elevation_to_earth_angle(5.0)
        self.assertGreater(angle, 0.0)
        angle_0 = self.analyzer.elevation_to_earth_angle(0.0)
        self.assertGreater(angle_0, angle)  # Lower elevation = larger angle
        print(f"  [PASS] Earth angle: 5deg->{math.degrees(angle):.1f}deg, 0deg->{math.degrees(angle_0):.1f}deg")


if __name__ == '__main__':
    unittest.main(verbosity=2)
