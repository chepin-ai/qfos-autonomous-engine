"""
Unit tests for optical navigation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from optical_navigation import (
    OpticalNavigator, OpticalObservation, KnownTarget
)
from orbital_mechanics import OrbitalBody


class TestOpticalNavigator(unittest.TestCase):
    """Test optical navigation algorithms."""
    
    def setUp(self):
        self.nav = OpticalNavigator()
        
        # Add some targets
        self.nav.add_target(KnownTarget(
            name="Mars", 
            body=OrbitalBody(name="Mars", spkid="499", a_au=1.524, e=0.093,
                            i_deg=1.85, omega_deg=286.5, Omega_deg=49.6),
            visual_magnitude=-2.0
        ))
        self.nav.add_target(KnownTarget(
            name="Venus",
            body=OrbitalBody(name="Venus", spkid="299", a_au=0.723, e=0.007,
                            i_deg=3.39, omega_deg=54.9, Omega_deg=76.7),
            visual_magnitude=-4.4
        ))
        self.nav.add_target(KnownTarget(
            name="Ceres",
            body=OrbitalBody(name="Ceres", spkid="2000001", a_au=2.769, e=0.076,
                            i_deg=10.59, omega_deg=73.6, Omega_deg=80.3),
            visual_magnitude=7.0
        ))
    
    def test_unit_vector(self):
        """Should convert RA/Dec to unit vector."""
        v = OpticalNavigator.unit_vector(0.0, 0.0)
        self.assertAlmostEqual(v[0], 1.0, delta=0.01)
        self.assertAlmostEqual(v[1], 0.0, delta=0.01)
        
        v = OpticalNavigator.unit_vector(90.0, 0.0)
        self.assertAlmostEqual(v[0], 0.0, delta=0.01)
        self.assertAlmostEqual(v[1], 1.0, delta=0.01)
        print("  [PASS] Unit vector conversion")
    
    def test_angle_between(self):
        """Should compute angle between vectors."""
        v1 = (1.0, 0.0, 0.0)
        v2 = (0.0, 1.0, 0.0)
        angle = OpticalNavigator.angle_between(v1, v2)
        self.assertAlmostEqual(angle, 90.0, delta=0.1)
        print(f"  [PASS] Angle between: {angle:.1f}°")
    
    def test_triangulate_position(self):
        """Should triangulate from 3 observations."""
        obs1 = OpticalObservation("Mars", 0.0, 0.0, 0.0)
        obs2 = OpticalObservation("Venus", 0.0, 90.0, 0.0)
        obs3 = OpticalObservation("Ceres", 0.0, 180.0, 0.0)
        
        pos = self.nav.triangulate_position(obs1, obs2, obs3)
        self.assertIsNotNone(pos)
        self.assertEqual(len(pos), 3)
        print(f"  [PASS] Triangulation: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}) AU")
    
    def test_triangulate_unknown_target(self):
        """Should fail for unknown target."""
        obs1 = OpticalObservation("Unknown", 0.0, 0.0, 0.0)
        obs2 = OpticalObservation("Venus", 0.0, 90.0, 0.0)
        obs3 = OpticalObservation("Mars", 0.0, 180.0, 0.0)
        
        pos = self.nav.triangulate_position(obs1, obs2, obs3)
        self.assertIsNone(pos)
        print("  [PASS] Unknown target handled")
    
    def test_estimate_position_single(self):
        """Should estimate position from single observation."""
        obs = OpticalObservation("Mars", 0.0, 0.0, 0.0)
        pos = self.nav.estimate_position_single(obs, assumed_distance_au=0.5)
        self.assertIsNotNone(pos)
        self.assertEqual(len(pos), 3)
        print(f"  [PASS] Single obs: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}) AU")
    
    def test_compute_residual(self):
        """Should compute LOS residual."""
        obs = OpticalObservation("Mars", 0.0, 0.0, 0.0)
        # Place spacecraft at origin
        residual = self.nav.compute_line_of_sight_residual(obs, (0.0, 0.0, 0.0))
        self.assertNotEqual(residual, float('inf'))
        print(f"  [PASS] Residual: {residual:.2f} arcsec")
    
    def test_batch_estimate(self):
        """Should batch estimate position."""
        observations = [
            OpticalObservation("Mars", 0.0, 0.0, 0.0, sigma_arcsec=1.0),
            OpticalObservation("Venus", 0.0, 90.0, 0.0, sigma_arcsec=1.0),
            OpticalObservation("Ceres", 0.0, 180.0, 0.0, sigma_arcsec=1.0),
        ]
        
        result = self.nav.batch_position_estimate(observations, initial_guess_au=(1.0, 0.0, 0.0))
        self.assertIn("position_au", result)
        self.assertIn("rms_residual_arcsec", result)
        print(f"  [PASS] Batch estimate: pos={result['position_au']}, RMS={result['rms_residual_arcsec']:.2f}")
    
    def test_brightness_filter(self):
        """Should filter targets by brightness."""
        bright = self.nav.catalog_brightness_filter(max_visual_magnitude=0.0)
        self.assertIn("Mars", bright)
        self.assertIn("Venus", bright)
        self.assertNotIn("Ceres", bright)
        print(f"  [PASS] Bright filter: {len(bright)} targets")
    
    def test_navigation_summary(self):
        """Should provide navigation summary."""
        summary = self.nav.get_navigation_summary()
        self.assertEqual(summary["registered_targets"], 3)
        self.assertIn("bright_targets", summary)
        print(f"  [PASS] Summary: {summary}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
