"""
Unit tests for collaborative manipulation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from collaborative_manipulation import (RobotState, TaskAllocation,
                                        CoordinationController,
                                        ConsensusAlgorithm,
                                        CollisionAvoidance,
                                        CollaborativeManipulation)


class TestTaskAllocation(unittest.TestCase):
    """Test allocation."""
    
    def setUp(self):
        self.ta = TaskAllocation()
    
    def test_nearest(self):
        """Should find nearest."""
        robots = [RobotState(0.0, 0.0, 0.0, True), RobotState(5.0, 0.0, 0.0, True)]
        n = self.ta.nearest_robot((1.0, 0.0), robots)
        self.assertEqual(n, 0)
        print(f"  [PASS] Near: {n}")
    
    def test_greedy(self):
        """Should assign greedily."""
        robots = [RobotState(0.0, 0.0, 0.0, True), RobotState(5.0, 0.0, 0.0, True)]
        tasks = [(1.0, 0.0), (6.0, 0.0)]
        a = self.ta.greedy_assignment(tasks, robots)
        self.assertEqual(len(a), 2)
        print(f"  [PASS] Assign: {a}")


class TestCoordinationController(unittest.TestCase):
    """Test coordination."""
    
    def setUp(self):
        self.cc = CoordinationController()
    
    def test_separation(self):
        """Should check separation."""
        r1 = RobotState(0.0, 0.0, 0.0, True)
        r2 = RobotState(1.0, 0.0, 0.0, True)
        self.assertTrue(self.cc.separation_constraint(r1, r2))
        print("  [PASS] Sep")
    
    def test_velocity(self):
        """Should adjust velocity."""
        v = self.cc.velocity_adjustment(1.0, 0.3)
        self.assertEqual(v, 0.0)
        print(f"  [PASS] Vel: {v:.1f}")


class TestConsensusAlgorithm(unittest.TestCase):
    """Test consensus."""
    
    def setUp(self):
        self.ca = ConsensusAlgorithm()
    
    def test_average(self):
        """Should converge."""
        vals = [0.0, 10.0]
        neigh = [[1], [0]]
        new = self.ca.average_consensus(vals, neigh)
        self.assertGreater(new[0], vals[0])
        print(f"  [PASS] Avg: {new}")
    
    def test_error(self):
        """Should compute error."""
        e = self.ca.consensus_error([0.0, 10.0])
        self.assertEqual(e, 5.0)
        print(f"  [PASS] Err: {e:.1f}")


class TestCollisionAvoidance(unittest.TestCase):
    """Test avoidance."""
    
    def setUp(self):
        self.ca = CollisionAvoidance()
    
    def test_reciprocal(self):
        """Should adjust velocity."""
        v = self.ca.reciprocal_velocity((0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (0.0, 0.0))
        self.assertLess(v[0], 1.0)
        print(f"  [PASS] Recip: {v}")


class TestCollaborativeManipulation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.cm = CollaborativeManipulation()
    
    def test_summary(self):
        """Should summarize."""
        s = self.cm.collaborative_summary()
        self.assertIn("capabilities", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
