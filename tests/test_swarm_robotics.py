"""
Unit tests for swarm robotics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from swarm_robotics import (RobotState, FlockingBehavior,
                            ConsensusAlgorithm,
                            CoverageControl,
                            FormationControl,
                            SwarmRobotics)


class TestFlockingBehavior(unittest.TestCase):
    """Test flocking."""
    
    def setUp(self):
        self.fb = FlockingBehavior(2.0, 5.0, 5.0)
    
    def test_separation(self):
        """Should compute separation."""
        r = RobotState(0.0, 0.0, 0.0, 0.0)
        n = [RobotState(1.0, 0.0, 0.0, 0.0)]
        fx, fy = self.fb.separation(r, n)
        self.assertNotEqual(fx, 0.0)
        print(f"  [PASS] Sep: ({fx:.2f}, {fy:.2f})")
    
    def test_alignment(self):
        """Should compute alignment."""
        r = RobotState(0.0, 0.0, 0.0, 0.0)
        n = [RobotState(1.0, 0.0, 1.0, 0.0)]
        fx, fy = self.fb.alignment(r, n)
        self.assertNotEqual(fx, 0.0)
        print(f"  [PASS] Ali: ({fx:.2f}, {fy:.2f})")
    
    def test_cohesion(self):
        """Should compute cohesion."""
        r = RobotState(0.0, 0.0, 0.0, 0.0)
        n = [RobotState(2.0, 2.0, 0.0, 0.0)]
        fx, fy = self.fb.cohesion(r, n)
        self.assertNotEqual(fx, 0.0)
        print(f"  [PASS] Coh: ({fx:.2f}, {fy:.2f})")


class TestConsensusAlgorithm(unittest.TestCase):
    """Test consensus."""
    
    def setUp(self):
        self.ca = ConsensusAlgorithm()
    
    def test_average(self):
        """Should compute consensus."""
        adj = [[0.0, 1.0], [1.0, 0.0]]
        v = self.ca.average_consensus([1.0, 3.0], adj, 20)
        self.assertAlmostEqual(v[0], v[1], delta=0.1)
        print(f"  [PASS] Cons: {v}")
    
    def test_error(self):
        """Should compute error."""
        e = self.ca.consensus_error([1.0, 1.1, 0.9])
        self.assertGreater(e, 0)
        print(f"  [PASS] Err: {e:.3f}")


class TestCoverageControl(unittest.TestCase):
    """Test coverage."""
    
    def setUp(self):
        self.cc = CoverageControl()
    
    def test_area(self):
        """Should compute area."""
        r = RobotState(0.0, 0.0, 0.0, 0.0)
        a = self.cc.voronoi_cell_area(r, [], [(0, 0), (10, 0), (10, 10), (0, 10)])
        self.assertGreater(a, 0)
        print(f"  [PASS] Area: {a:.1f}")
    
    def test_objective(self):
        """Should compute objective."""
        robots = [RobotState(0.0, 0.0, 0.0, 0.0), RobotState(3.0, 4.0, 0.0, 0.0)]
        o = self.cc.coverage_objective(robots)
        self.assertEqual(o, 5.0)
        print(f"  [PASS] Obj: {o:.1f}")


class TestFormationControl(unittest.TestCase):
    """Test formation."""
    
    def setUp(self):
        self.fc = FormationControl()
    
    def test_error(self):
        """Should compute error."""
        robots = [RobotState(0.0, 0.0, 0.0, 0.0), RobotState(3.0, 4.0, 0.0, 0.0)]
        e = self.fc.formation_error(robots, {(0, 1): 5.0})
        self.assertEqual(e, 0.0)
        print(f"  [PASS] Err: {e:.2f}")
    
    def test_desired(self):
        """Should compute desired position."""
        l = RobotState(1.0, 1.0, 0.0, 0.0)
        x, y = self.fc.desired_position(l, 2.0, 0.0)
        self.assertEqual(x, 3.0)
        print(f"  [PASS] Pos: ({x:.1f}, {y:.1f})")


class TestSwarmRobotics(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sr = SwarmRobotics()
    
    def test_summary(self):
        """Should summarize."""
        s = self.sr.swarm_summary()
        self.assertIn("behaviors", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
