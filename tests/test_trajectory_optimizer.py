"""
Unit tests for trajectory optimizer module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from trajectory_optimizer import (Waypoint, MinimumSnapOptimizer, TimeOptimalPath,
                                  TrajectoryOptimizer, PolynomialSegment)


class TestMinimumSnapOptimizer(unittest.TestCase):
    """Test minimum snap optimizer."""
    
    def setUp(self):
        self.opt = MinimumSnapOptimizer()
    
    def test_solve_segment(self):
        """Should solve polynomial segment."""
        coeffs = self.opt.solve_segment(0, 10, 0, 0, 0, 0, 5.0)
        self.assertEqual(len(coeffs), 6)
        # At t=0: p=c0=0
        self.assertEqual(coeffs[0], 0)
        print(f"  [PASS] Segment: 6 coeffs")
    
    def test_optimize(self):
        """Should optimize waypoints."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(5, 5, 0, t=5),
            Waypoint(10, 0, 0, t=10)
        ]
        segments = self.opt.optimize(waypoints)
        self.assertEqual(len(segments), 2)
        print(f"  [PASS] Optimize: {len(segments)} segments")
    
    def test_evaluate(self):
        """Should evaluate trajectory."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(10, 0, 0, t=10)
        ]
        segments = self.opt.optimize(waypoints)
        pos = segments[0].evaluate(5.0)
        self.assertIsNotNone(pos)
        print(f"  [PASS] Evaluate: ({pos[0]:.1f}, {pos[1]:.1f})")
    
    def test_start_end_match(self):
        """Should match start and end positions."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(10, 5, 2, t=10)
        ]
        segments = self.opt.optimize(waypoints)
        start = segments[0].evaluate(0.0)
        end = segments[0].evaluate(10.0)
        self.assertAlmostEqual(start[0], 0.0, places=5)
        self.assertAlmostEqual(end[0], 10.0, places=5)
        print(f"  [PASS] Match: start={start[0]:.1f}, end={end[0]:.1f}")
    
    def test_velocity_evaluation(self):
        """Should evaluate velocity."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(10, 0, 0, t=10)
        ]
        segments = self.opt.optimize(waypoints)
        v = segments[0].evaluate_velocity(0.0)
        self.assertIsNotNone(v)
        print(f"  [PASS] Velocity: ({v[0]:.2f}, {v[1]:.2f})")


class TestTimeOptimalPath(unittest.TestCase):
    """Test time-optimal path."""
    
    def setUp(self):
        self.top = TimeOptimalPath(max_velocity=2.0, max_acceleration=1.0)
    
    def test_trapezoidal(self):
        """Should compute trapezoidal profile."""
        t_accel, t_coast, t_decel = self.top.compute_trapezoidal_profile(10.0)
        self.assertGreater(t_accel, 0)
        self.assertGreater(t_decel, 0)
        total_time = t_accel + t_coast + t_decel
        self.assertGreater(total_time, 0)
        print(f"  [PASS] Trapezoidal: total={total_time:.2f}s")
    
    def test_triangular(self):
        """Should compute triangular profile for short distances."""
        t_accel, t_coast, t_decel = self.top.compute_trapezoidal_profile(1.0)
        self.assertGreater(t_accel, 0)
        self.assertEqual(t_coast, 0.0)
        print(f"  [PASS] Triangular: accel={t_accel:.2f}s")
    
    def test_parameterize(self):
        """Should parameterize path."""
        path = [(0, 0, 0), (5, 0, 0), (10, 0, 0)]
        waypoints = self.top.parameterize_path(path)
        self.assertEqual(len(waypoints), 3)
        self.assertEqual(waypoints[0].t, 0.0)
        self.assertGreater(waypoints[-1].t, 0)
        print(f"  [PASS] Parameterize: {len(waypoints)} wps, T={waypoints[-1].t:.2f}s")


class TestTrajectoryOptimizer(unittest.TestCase):
    """Test unified trajectory optimizer."""
    
    def setUp(self):
        self.opt = TrajectoryOptimizer()
    
    def test_optimize_waypoints(self):
        """Should optimize waypoints."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(5, 5, 0, t=5)
        ]
        segments = self.opt.optimize_waypoints(waypoints)
        self.assertEqual(len(segments), 1)
        print("  [PASS] Waypoints: 1 segment")
    
    def test_optimize_path(self):
        """Should optimize path timing."""
        path = [(0, 0, 0), (3, 4, 0)]
        waypoints = self.opt.optimize_path(path, max_velocity=1.0, max_acceleration=0.5)
        self.assertEqual(len(waypoints), 2)
        self.assertGreater(waypoints[-1].t, 0)
        print(f"  [PASS] Path: T={waypoints[-1].t:.2f}s")
    
    def test_duration(self):
        """Should compute duration."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(10, 0, 0, t=10)
        ]
        segments = self.opt.optimize_waypoints(waypoints)
        duration = self.opt.get_trajectory_duration(segments)
        self.assertEqual(duration, 10.0)
        print(f"  [PASS] Duration: {duration:.1f}s")
    
    def test_velocity_constraints(self):
        """Should check velocity constraints."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(1, 0, 0, t=10)
        ]
        segments = self.opt.optimize_waypoints(waypoints)
        ok = self.opt.check_velocity_constraints(segments, max_v=1.0)
        self.assertTrue(ok)
        print("  [PASS] Velocity: ok")
    
    def test_summary(self):
        """Should provide summary."""
        waypoints = [
            Waypoint(0, 0, 0, t=0),
            Waypoint(10, 0, 0, t=10)
        ]
        self.opt.optimize_waypoints(waypoints)
        summary = self.opt.optimizer_summary()
        self.assertEqual(summary["segments"], 1)
        print(f"  [PASS] Summary: {summary}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
