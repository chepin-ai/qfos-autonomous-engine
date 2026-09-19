"""
Unit tests for star tracker module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from star_tracker import StarCatalog, StarTracker, Star, StarObservation


class TestStarCatalog(unittest.TestCase):
    """Test star catalog."""
    
    def test_create_catalog(self):
        """Should create catalog."""
        catalog = StarCatalog.create_sample_catalog(num_stars=50)
        self.assertEqual(len(catalog.stars), 50)
        print("  [PASS] Catalog: 50 stars")
    
    def test_star_to_vector(self):
        """Should convert to unit vector."""
        star = Star(id=0, ra_deg=0.0, dec_deg=0.0, magnitude=1.0)
        v = star.to_unit_vector()
        self.assertAlmostEqual(v[0], 1.0, delta=0.01)
        self.assertAlmostEqual(math.sqrt(v[0]**2 + v[1]**2 + v[2]**2), 1.0, delta=0.01)
        print("  [PASS] Unit vector: (1, 0, 0)")
    
    def test_angular_distance(self):
        """Should compute angular distance."""
        s1 = Star(id=0, ra_deg=0.0, dec_deg=0.0, magnitude=1.0)
        s2 = Star(id=1, ra_deg=90.0, dec_deg=0.0, magnitude=1.0)
        dist = s1.angular_distance_deg(s2)
        self.assertAlmostEqual(dist, 90.0, delta=1.0)
        print(f"  [PASS] Distance: {dist:.1f} deg")
    
    def test_stars_in_fov(self):
        """Should find stars in FOV."""
        catalog = StarCatalog.create_sample_catalog(100)
        stars = catalog.stars_in_fov(0.0, 0.0, fov_deg=20.0)
        self.assertGreater(len(stars), 0)
        print(f"  [PASS] FOV stars: {len(stars)}")


class TestStarTracker(unittest.TestCase):
    """Test star tracker."""
    
    def setUp(self):
        self.catalog = StarCatalog.create_sample_catalog(100)
        self.tracker = StarTracker(self.catalog, fov_deg=10.0)
    
    def test_fov_computation(self):
        """Should compute FOV."""
        fov = self.tracker._compute_fov_from_focal()
        self.assertGreater(fov, 0.0)
        print(f"  [PASS] FOV: {fov:.1f} deg")
    
    def test_generate_observation(self):
        """Should generate observations."""
        identity = [[1,0,0],[0,1,0],[0,0,1]]
        obs = self.tracker.generate_observation(identity, 0.0, 0.0)
        self.assertIsInstance(obs, list)
        print(f"  [PASS] Observations: {len(obs)} stars")
    
    def test_attitude_determination(self):
        """Should determine attitude with TRIAD."""
        # Use first two stars from catalog
        stars = self.catalog.stars[:2]
        if len(stars) < 2:
            self.skipTest("Need at least 2 stars")
        
        # Create observations
        obs1 = StarObservation(x=0.0, y=0.0, z=1.0, magnitude=stars[0].magnitude)
        obs2 = StarObservation(x=1.0, y=0.0, z=0.0, magnitude=stars[1].magnitude)
        
        A = self.tracker.attitude_determination_triad(
            obs1, obs2, stars[0], stars[1]
        )
        
        self.assertEqual(len(A), 3)
        self.assertEqual(len(A[0]), 3)
        print("  [PASS] TRIAD: 3x3 matrix")
    
    def test_identify_stars(self):
        """Should identify stars."""
        identity = [[1,0,0],[0,1,0],[0,0,1]]
        obs = self.tracker.generate_observation(identity, 0.0, 0.0)
        if len(obs) > 0:
            matches = self.tracker.identify_stars(obs, 0.0, 0.0)
            self.assertEqual(len(matches), len(obs))
            matched = sum(1 for _, s in matches if s is not None)
            print(f"  [PASS] Identified: {matched}/{len(obs)} stars")
        else:
            print("  [PASS] No stars in FOV")
    
    def test_attitude_accuracy(self):
        """Should compute attitude error."""
        identity = [[1,0,0],[0,1,0],[0,0,1]]
        error = self.tracker.compute_attitude_accuracy(identity, identity)
        self.assertAlmostEqual(error, 0.0, delta=0.01)
        print(f"  [PASS] Identity error: {error:.4f} deg")


if __name__ == '__main__':
    unittest.main(verbosity=2)
