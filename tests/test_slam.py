"""
Unit tests for SLAM module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slam import (Pose, Landmark, OccupancyGrid,
                  ParticleFilterSLAM,
                  ScanMatcher,
                  SLAM)


class TestOccupancyGrid(unittest.TestCase):
    """Test grid."""
    
    def setUp(self):
        self.g = OccupancyGrid(50, 50, 0.1)
    
    def test_world_to_grid(self):
        """Should convert."""
        gx, gy = self.g.world_to_grid(0.0, 0.0)
        self.assertTrue(0 <= gx < 50)
        self.assertTrue(0 <= gy < 50)
        print(f"  [PASS] Grid: ({gx}, {gy})")
    
    def test_update(self):
        """Should update."""
        self.g.update_cell(1.0, 1.0, True)
        self.assertTrue(self.g.is_occupied(1.0, 1.0))
        print("  [PASS] Upd")
    
    def test_not_occupied(self):
        """Should be free."""
        self.assertFalse(self.g.is_occupied(0.0, 0.0))
        print("  [PASS] Free")


class TestParticleFilterSLAM(unittest.TestCase):
    """Test PF."""
    
    def setUp(self):
        self.pf = ParticleFilterSLAM(50)
    
    def test_init(self):
        """Should init."""
        self.assertEqual(len(self.pf.particles), 50)
        print("  [PASS] Init")
    
    def test_predict(self):
        """Should predict."""
        p0 = self.pf.particles[0]
        self.pf.predict(1.0, 0.0, 0.1)
        p1 = self.pf.particles[0]
        self.assertNotEqual((p0.x, p0.y), (p1.x, p1.y))
        print("  [PASS] Pred")
    
    def test_observe(self):
        """Should observe."""
        self.pf.observe_landmark(1, 5.0, 3.0)
        self.assertIn(1, self.pf.landmarks)
        print("  [PASS] Obs")
    
    def test_resample(self):
        """Should resample."""
        self.pf.predict(1.0, 0.0, 0.0)
        self.pf.observe_landmark(1, 2.0, 0.0)
        self.pf.resample()
        self.assertAlmostEqual(sum(self.pf.weights), 1.0, places=5)
        print("  [PASS] Resamp")
    
    def test_estimate(self):
        """Should estimate."""
        self.pf.observe_landmark(1, 5.0, 0.0)
        pose = self.pf.estimated_pose()
        self.assertIsInstance(pose.x, float)
        print(f"  [PASS] Est: ({pose.x:.2f}, {pose.y:.2f})")


class TestScanMatcher(unittest.TestCase):
    """Test matcher."""
    
    def setUp(self):
        self.sm = ScanMatcher()
    
    def test_icp(self):
        """Should align."""
        src = [(0.0, 0.0), (1.0, 0.0)]
        tgt = [(1.0, 0.0), (2.0, 0.0)]
        dx, dy, dt = self.sm.icp_step(src, tgt)
        self.assertAlmostEqual(dx, 1.0, delta=0.1)
        print(f"  [PASS] ICP: dx={dx:.2f}")


class TestSLAM(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.slam = SLAM()
    
    def test_summary(self):
        """Should summarize."""
        s = self.slam.slam_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
