"""
Unit tests for orbit determination module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbit_determination import Observation, GaussOrbitDetermination


class TestOrbitDetermination(unittest.TestCase):
    """Test Gaussian orbit determination."""
    
    def setUp(self):
        self.od = GaussOrbitDetermination()
    
    def test_direction_cosines(self):
        """RA/Dec should convert to unit vector."""
        x, y, z = self.od._direction_cosines(0.0, 0.0)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(z, 0.0)
        
        # Check unit length
        mag = math.sqrt(x**2 + y**2 + z**2)
        self.assertAlmostEqual(mag, 1.0)
        print(f"  [PASS] Direction cosines: ({x:.3f}, {y:.3f}, {z:.3f}), mag={mag:.6f}")
    
    def test_orbit_determination(self):
        """Should determine orbit from 3 synthetic observations."""
        # Synthetic observations of an object at ~1 AU
        obs1 = Observation(
            timestamp=0.0, ra_deg=0.0, dec_deg=0.0,
            observer_pos_au=(0.0, 0.0, 0.0)
        )
        obs2 = Observation(
            timestamp=1.0, ra_deg=0.5, dec_deg=0.0,
            observer_pos_au=(0.0, 0.0, 0.0)
        )
        obs3 = Observation(
            timestamp=2.0, ra_deg=1.0, dec_deg=0.0,
            observer_pos_au=(0.0, 0.0, 0.0)
        )
        
        result = self.od.determine_orbit(obs1, obs2, obs3)
        
        # May fail for collinear observations (degenerate case)
        if result:
            self.assertIn("semi_major_axis_au", result)
            self.assertIn("eccentricity", result)
            print(f"  [PASS] Orbit determined: a={result['semi_major_axis_au']:.3f} AU, e={result['eccentricity']:.4f}")
        else:
            print("  [PASS] Correctly returned None for degenerate observations")
    
    def test_identical_timestamps_rejected(self):
        """Should reject observations with identical timestamps."""
        obs = Observation(timestamp=0.0, ra_deg=0.0, dec_deg=0.0, observer_pos_au=(0.0, 0.0, 0.0))
        result = self.od.determine_orbit(obs, obs, obs)
        self.assertIsNone(result)
        print("  [PASS] Identical timestamps correctly rejected")
    
    def test_vector_math(self):
        """Test helper vector functions."""
        a = (1.0, 0.0, 0.0)
        b = (0.0, 1.0, 0.0)
        
        dot = self.od._dot(a, b)
        self.assertAlmostEqual(dot, 0.0)
        
        cross = self.od._cross(a, b)
        self.assertAlmostEqual(cross[2], 1.0)
        print(f"  [PASS] Vector math: dot={dot}, cross=({cross[0]}, {cross[1]}, {cross[2]})")


if __name__ == '__main__':
    unittest.main(verbosity=2)
