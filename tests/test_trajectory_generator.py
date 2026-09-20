"""
Unit tests for trajectory generator module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from trajectory_generator import (ProfileType, Waypoint,
                                   CubicSpline, VelocityProfile,
                                   TimeOptimalPlanner, TrajectoryGenerator)


class TestCubicSpline(unittest.TestCase):
    """Test cubic spline."""
    
    def test_interpolation(self):
        """Should interpolate between waypoints."""
        pts = [Waypoint(0.0, 0.0), Waypoint(1.0, 1.0), Waypoint(2.0, 0.0)]
        spline = CubicSpline(pts)
        v = spline.evaluate(1.0)
        self.assertAlmostEqual(v, 1.0, places=1)
        print(f"  [PASS] Interp: {v:.3f}")
    
    def test_endpoints(self):
        """Should match endpoints."""
        pts = [Waypoint(0.0, 1.0), Waypoint(2.0, 3.0)]
        spline = CubicSpline(pts)
        v0 = spline.evaluate(0.0)
        v1 = spline.evaluate(2.0)
        self.assertAlmostEqual(v0, 1.0, places=2)
        self.assertAlmostEqual(v1, 3.0, places=2)
        print(f"  [PASS] Endpoints")
    
    def test_derivative(self):
        """Should compute derivative."""
        pts = [Waypoint(0.0, 0.0), Waypoint(1.0, 1.0)]
        spline = CubicSpline(pts)
        d = spline.derivative(0.5)
        self.assertGreater(d, 0)
        print(f"  [PASS] Deriv: {d:.3f}")


class TestVelocityProfile(unittest.TestCase):
    """Test velocity profile."""
    
    def setUp(self):
        self.vp = VelocityProfile(vmax=2.0, amax=4.0)
    
    def test_trapezoidal_time(self):
        """Should compute trapezoidal time."""
        t = self.vp.trapezoidal_time(4.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Trap time: {t:.3f}")
    
    def test_trapezoidal_velocity(self):
        """Should have zero velocity at endpoints."""
        t_total = self.vp.trapezoidal_time(4.0)
        v0 = self.vp.trapezoidal_velocity(0.0, 4.0)
        v1 = self.vp.trapezoidal_velocity(t_total, 4.0)
        self.assertAlmostEqual(v0, 0.0)
        self.assertAlmostEqual(v1, 0.0)
        print("  [PASS] Zero endpoints")
    
    def test_trapezoidal_peak(self):
        """Should reach peak velocity."""
        t_total = self.vp.trapezoidal_time(10.0)
        vm = self.vp.trapezoidal_velocity(t_total / 2.0, 10.0)
        self.assertGreaterEqual(vm, 0)
        print(f"  [PASS] Peak: {vm:.3f}")
    
    def test_s_curve_time(self):
        """Should compute S-curve time."""
        t = self.vp.s_curve_time(4.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Scurve: {t:.3f}")


class TestTimeOptimalPlanner(unittest.TestCase):
    """Test time-optimal planner."""
    
    def setUp(self):
        self.top = TimeOptimalPlanner(vmax=2.0, amax=4.0)
    
    def test_plan(self):
        """Should plan segment durations."""
        pts = [Waypoint(0.0), Waypoint(2.0), Waypoint(5.0)]
        d = self.top.plan(pts)
        self.assertEqual(len(d), 2)
        print(f"  [PASS] Plan: {d}")
    
    def test_total_time(self):
        """Should compute total time."""
        d = self.top.total_time([1.0, 2.0, 0.5])
        self.assertAlmostEqual(d, 3.5)
        print(f"  [PASS] Total: {d}")


class TestTrajectoryGenerator(unittest.TestCase):
    """Test unified trajectory generator."""
    
    def setUp(self):
        self.tg = TrajectoryGenerator()
    
    def test_set_waypoints(self):
        """Should set waypoints."""
        pts = [Waypoint(0.0), Waypoint(1.0), Waypoint(2.0)]
        self.tg.set_waypoints(pts)
        self.assertEqual(len(self.tg.waypoints), 3)
        print("  [PASS] Set")
    
    def test_generate(self):
        """Should generate trajectory."""
        pts = [Waypoint(0.0), Waypoint(1.0)]
        self.tg.set_waypoints(pts)
        traj = self.tg.generate(dt=0.1)
        self.assertGreater(len(traj), 0)
        print(f"  [PASS] Gen: {len(traj)} pts")
    
    def test_summary(self):
        """Should provide summary."""
        pts = [Waypoint(0.0), Waypoint(2.0)]
        self.tg.set_waypoints(pts)
        s = self.tg.trajectory_summary()
        self.assertIn("total_time", s)
        print(f"  [PASS] Summary: t={s['total_time']:.3f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
