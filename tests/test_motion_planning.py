"""
Unit tests for motion planning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from motion_planning import (Waypoint, CubicSpline,
                             VelocityProfiler,
                             JerkLimitedProfile,
                             TrajectoryGenerator,
                             MotionPlanning)


class TestCubicSpline(unittest.TestCase):
    """Test spline."""
    
    def setUp(self):
        self.spline = CubicSpline([(0.0, 0.0), (1.0, 1.0), (2.0, 0.0)])
    
    def test_evaluate(self):
        """Should evaluate."""
        y = self.spline.evaluate(0.5)
        self.assertIsNotNone(y)
        print(f"  [PASS] Spl: {y:.4f}")
    
    def test_endpoints(self):
        """Should match endpoints."""
        y0 = self.spline.evaluate(0.0)
        y1 = self.spline.evaluate(2.0)
        self.assertEqual(y0, 0.0)
        self.assertEqual(y1, 0.0)
        print(f"  [PASS] EP: {y0}, {y1}")


class TestVelocityProfiler(unittest.TestCase):
    """Test profiler."""
    
    def setUp(self):
        self.vp = VelocityProfiler(2.0, 1.0)
    
    def test_profile_time(self):
        """Should compute time."""
        t = self.vp.profile_time(4.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] T: {t:.4f}")
    
    def test_velocity_at_time(self):
        """Should compute velocity."""
        v = self.vp.velocity_at_time(4.0, 1.0)
        self.assertGreaterEqual(v, 0)
        print(f"  [PASS] V: {v:.4f}")


class TestJerkLimitedProfile(unittest.TestCase):
    """Test jerk."""
    
    def setUp(self):
        self.jp = JerkLimitedProfile(1.0, 1.0, 1.0)
    
    def test_time(self):
        """Should compute time."""
        t = self.jp.profile_time(2.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] JT: {t:.4f}")


class TestTrajectoryGenerator(unittest.TestCase):
    """Test trajectory."""
    
    def setUp(self):
        self.tg = TrajectoryGenerator()
    
    def test_generate(self):
        """Should generate."""
        wps = [Waypoint(0.0, 0.0, 0.0, 1.0), Waypoint(1.0, 0.0, 0.0, 1.0)]
        traj = self.tg.generate(wps)
        self.assertGreater(len(traj), 0)
        print(f"  [PASS] Traj: {len(traj)} pts")


class TestMotionPlanning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mp = MotionPlanning()
    
    def test_plan(self):
        """Should plan."""
        wps = [Waypoint(0.0, 0.0, 0.0, 1.0), Waypoint(1.0, 1.0, 0.0, 0.5)]
        traj = self.mp.plan_trajectory(wps)
        self.assertGreater(len(traj), 0)
        print(f"  [PASS] Plan: {len(traj)} pts")
    
    def test_summary(self):
        """Should summarize."""
        s = self.mp.mp_summary()
        self.assertIn("profiles", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
