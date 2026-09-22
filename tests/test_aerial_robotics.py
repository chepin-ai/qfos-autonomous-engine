"""
Unit tests for aerial robotics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aerial_robotics import (Pose, QuadcopterDynamics,
                             TrajectoryPlanning,
                             AttitudeControl,
                             ObstacleAvoidance,
                             AerialRobotics)


class TestQuadcopterDynamics(unittest.TestCase):
    """Test dynamics."""
    
    def setUp(self):
        self.qd = QuadcopterDynamics()
    
    def test_thrust(self):
        """Should compute thrust."""
        T = self.qd.thrust([500.0, 500.0, 500.0, 500.0])
        self.assertGreater(T, 0)
        print(f"  [PASS] T: {T:.4f}")
    
    def test_torque(self):
        """Should compute torque."""
        tau = self.qd.torque([500.0, 500.0, 500.0, 500.0])
        self.assertEqual(len(tau), 3)
        print(f"  [PASS] Tau: {tau}")
    
    def test_hover(self):
        """Should compute hover thrust."""
        h = self.qd.hover_thrust()
        self.assertEqual(h, 9.81)
        print(f"  [PASS] Hover: {h:.2f}")


class TestTrajectoryPlanning(unittest.TestCase):
    """Test trajectory."""
    
    def setUp(self):
        self.tp = TrajectoryPlanning()
    
    def test_waypoint(self):
        """Should compute waypoint."""
        p = self.tp.minimum_snap_waypoint((0.0, 0.0, 0.0), (10.0, 0.0, 0.0), 10.0, 5.0)
        self.assertAlmostEqual(p[0], 5.0, delta=0.1)
        print(f"  [PASS] WP: {p}")
    
    def test_length(self):
        """Should compute length."""
        l = self.tp.trajectory_length([(0.0, 0.0, 0.0), (3.0, 4.0, 0.0)])
        self.assertEqual(l, 5.0)
        print(f"  [PASS] Len: {l:.1f}")


class TestAttitudeControl(unittest.TestCase):
    """Test attitude."""
    
    def setUp(self):
        self.ac = AttitudeControl()
    
    def test_pd(self):
        """Should compute PD."""
        u = self.ac.pd_control(0.0, 1.0, 0.0)
        self.assertEqual(u, 1.0)
        print(f"  [PASS] PD: {u:.2f}")
    
    def test_error(self):
        """Should compute error."""
        e = self.ac.attitude_error(0.0, 0.0, 0.0, 1.0, 0.5, 0.2)
        self.assertEqual(e, (1.0, 0.5, 0.2))
        print(f"  [PASS] Err: {e}")


class TestObstacleAvoidance(unittest.TestCase):
    """Test avoidance."""
    
    def setUp(self):
        self.oa = ObstacleAvoidance()
    
    def test_distance(self):
        """Should compute distance."""
        d = self.oa.distance_to_obstacle((0.0, 0.0, 0.0), (3.0, 4.0, 0.0))
        self.assertEqual(d, 5.0)
        print(f"  [PASS] Dist: {d:.1f}")
    
    def test_collision(self):
        """Should check collision."""
        c = self.oa.collision_risk((0.0, 0.0, 0.0), (0.5, 0.0, 0.0))
        self.assertTrue(c)
        print(f"  [PASS] Col: {c}")
    
    def test_repulsive(self):
        """Should compute repulsive."""
        f = self.oa.repulsive_force((1.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        self.assertGreater(f[0], 0)
        print(f"  [PASS] Rep: {f}")


class TestAerialRobotics(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ar = AerialRobotics()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ar.aerial_summary()
        self.assertIn("modules", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
