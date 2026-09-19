"""
Unit tests for relative navigation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from relative_navigation import RelativeNavigator, RelativeState


class TestRelativeNavigator(unittest.TestCase):
    """Test relative navigator."""
    
    def setUp(self):
        self.nav = RelativeNavigator(sensor_types=["camera", "lidar", "radar"])
    
    def test_range_optical(self):
        """Should estimate range from optical."""
        range_m = self.nav.measure_range_optical(
            apparent_diameter_px=100.0,
            focal_length_px=1000.0,
            target_actual_diameter_m=4.0
        )
        self.assertGreater(range_m, 0.0)
        print(f"  [PASS] Optical range: {range_m:.1f} m")
    
    def test_range_lidar(self):
        """Should estimate range from LIDAR."""
        range_m = self.nav.measure_range_lidar(time_of_flight_ns=6667.0)
        self.assertGreater(range_m, 0.0)
        self.assertAlmostEqual(range_m, 1000.0, delta=1.0)
        print(f"  [PASS] LIDAR range: {range_m:.1f} m")
    
    def test_range_rate_doppler(self):
        """Should estimate range rate from Doppler."""
        v = self.nav.measure_range_rate_doppler(
            doppler_shift_hz=10000.0,
            transmit_frequency_hz=2.0e9
        )
        self.assertGreater(abs(v), 0.0)
        print(f"  [PASS] Doppler rate: {v:.2f} m/s")
    
    def test_triangulate(self):
        """Should triangulate position."""
        bearings = [
            {"sensor_pos": (0.0, 0.0, 0.0), "bearing_unit": (1.0, 0.0, 0.0)},
            {"sensor_pos": (10.0, 0.0, 0.0), "bearing_unit": (-1.0, 0.0, 0.0)}
        ]
        pos = self.nav.triangulate_position(bearings)
        self.assertIsNotNone(pos)
        print(f"  [PASS] Triangulate: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
    
    def test_update_filter(self):
        """Should update state filter."""
        meas = {"range_m": 500.0, "range_rate_ms": -1.5, "azimuth_deg": 0.0, "elevation_deg": 0.0}
        state = self.nav.update_filter(meas)
        self.assertEqual(state.range_m, 500.0)
        self.assertLess(state.range_rate_ms, 0.0)
        print(f"  [PASS] Filter: r={state.range_m}m, rdot={state.range_rate_ms}m/s")
    
    def test_approach_time(self):
        """Should estimate approach time."""
        state = RelativeState(
            range_m=1000.0, range_rate_ms=-2.0,
            relative_position_m=(1000.0, 0.0, 0.0),
            relative_velocity_ms=(-2.0, 0.0, 0.0),
            relative_attitude_deg=(0.0, 0.0, 0.0)
        )
        t = self.nav.estimate_approach_time(state)
        self.assertAlmostEqual(t, 500.0, delta=1.0)
        print(f"  [PASS] Approach time: {t:.1f} s")
    
    def test_safety_safe(self):
        """Should assess safe trajectory."""
        state = RelativeState(
            range_m=5000.0, range_rate_ms=-1.0,
            relative_position_m=(5000.0, 0.0, 0.0),
            relative_velocity_ms=(-1.0, 0.0, 0.0),
            relative_attitude_deg=(0.0, 0.0, 0.0)
        )
        safety = self.nav.safety_assessment(state)
        self.assertEqual(safety["status"], "SAFE")
        print(f"  [PASS] Safety: {safety['status']}")
    
    def test_safety_violation(self):
        """Should detect violation."""
        state = RelativeState(
            range_m=100.0, range_rate_ms=-5.0,
            relative_position_m=(50.0, 150.0, 0.0),
            relative_velocity_ms=(-5.0, 0.0, 0.0),
            relative_attitude_deg=(0.0, 0.0, 0.0)
        )
        safety = self.nav.safety_assessment(state)
        self.assertEqual(safety["status"], "VIOLATION")
        print(f"  [PASS] Violation detected")


if __name__ == '__main__':
    unittest.main(verbosity=2)
