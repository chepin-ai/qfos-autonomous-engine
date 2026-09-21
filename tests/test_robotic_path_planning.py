"""
Unit tests for robotic path planning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from robotic_path_planning import (Point2D, AStarPlanner,
                                   RRTPlanner,
                                   PathSmoother,
                                   RoboticPathPlanning)


class TestAStarPlanner(unittest.TestCase):
    """Test A*."""
    
    def setUp(self):
        self.ap = AStarPlanner(1.0)
    
    def test_heuristic(self):
        """Should compute heuristic."""
        h = self.ap.heuristic((0, 0), (3, 4))
        self.assertEqual(h, 5.0)
        print(f"  [PASS] H: {h}")
    
    def test_plan(self):
        """Should plan."""
        path = self.ap.plan(Point2D(0.0, 0.0), Point2D(3.0, 0.0))
        self.assertGreater(len(path), 0)
        print(f"  [PASS] A*: {len(path)} pts")
    
    def test_obstacle(self):
        """Should avoid obstacles."""
        self.ap.add_obstacle(1.5, 0.0)
        path = self.ap.plan(Point2D(0.0, 0.0), Point2D(3.0, 0.0))
        self.assertGreater(len(path), 0)
        print(f"  [PASS] Obs: {len(path)} pts")


class TestRRTPlanner(unittest.TestCase):
    """Test RRT."""
    
    def setUp(self):
        self.rp = RRTPlanner(500, 0.5)
    
    def test_collision(self):
        """Should detect collision."""
        self.rp.add_obstacle(Point2D(5.0, 5.0), 1.0)
        c = self.rp.collision(Point2D(5.0, 5.0))
        self.assertTrue(c)
        print("  [PASS] Col")
    
    def test_nearest(self):
        """Should find nearest."""
        self.rp.nodes = [Point2D(0.0, 0.0), Point2D(1.0, 1.0)]
        idx = self.rp.nearest(Point2D(0.9, 0.9))
        self.assertEqual(idx, 1)
        print(f"  [PASS] Near: {idx}")
    
    def test_steer(self):
        """Should steer."""
        p = self.rp.steer(Point2D(0.0, 0.0), Point2D(10.0, 0.0))
        self.assertEqual(p.x, 0.5)
        print(f"  [PASS] Steer: {p.x}")


class TestPathSmoother(unittest.TestCase):
    """Test smoother."""
    
    def setUp(self):
        self.ps = PathSmoother()
    
    def test_length(self):
        """Should compute length."""
        path = [Point2D(0.0, 0.0), Point2D(3.0, 4.0)]
        l = self.ps.path_length(path)
        self.assertEqual(l, 5.0)
        print(f"  [PASS] Len: {l}")
    
    def test_smooth(self):
        """Should smooth."""
        path = [Point2D(0.0, 0.0), Point2D(1.0, 2.0), Point2D(2.0, 0.0), Point2D(3.0, 0.0)]
        s = self.ps.smooth(path, 1)
        self.assertEqual(len(s), 4)
        print("  [PASS] Smth")


class TestRoboticPathPlanning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.rpp = RoboticPathPlanning()
    
    def test_plan_astar(self):
        """Should plan with A*."""
        path = self.rpp.plan(Point2D(0.0, 0.0), Point2D(2.0, 0.0), "astar")
        self.assertGreater(len(path), 0)
        print(f"  [PASS] Plan: {len(path)}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.rpp.rpp_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
