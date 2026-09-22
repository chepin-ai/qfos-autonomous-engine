"""
Unit tests for swarm robotics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from swarm_robotics import (RobotState, BoidFlocking,
                            ConsensusAlgorithms,
                            TaskAllocation,
                            FormationControl,
                            SwarmRobotics)


class TestBoidFlocking(unittest.TestCase):
    """Test flocking."""
    
    def setUp(self):
        self.bf = BoidFlocking()
        self.r1 = RobotState(0.0, 0.0, 1.0, 0.0)
        self.r2 = RobotState(1.0, 0.0, 1.0, 0.0)
        self.r3 = RobotState(0.0, 1.0, 0.0, 1.0)
    
    def test_separation(self):
        """Should compute separation."""
        f = self.bf.separation(self.r1, [self.r2, self.r3])
        self.assertNotEqual(f, (0.0, 0.0))
        print(f"  [PASS] Sep: {f}")
    
    def test_alignment(self):
        """Should compute alignment."""
        f = self.bf.alignment(self.r1, [self.r2, self.r3])
        self.assertEqual(len(f), 2)
        print(f"  [PASS] Ali: {f}")
    
    def test_cohesion(self):
        """Should compute cohesion."""
        f = self.bf.cohesion(self.r1, [self.r2, self.r3])
        self.assertEqual(len(f), 2)
        print(f"  [PASS] Coh: {f}")
    
    def test_flocking(self):
        """Should compute flocking velocity."""
        v = self.bf.flocking_velocity(self.r1, [self.r2, self.r3])
        self.assertEqual(len(v), 2)
        print(f"  [PASS] Vel: {v}")


class TestConsensusAlgorithms(unittest.TestCase):
    """Test consensus."""
    
    def setUp(self):
        self.ca = ConsensusAlgorithms()
    
    def test_average(self):
        """Should reach average consensus."""
        v = [1.0, 3.0, 5.0]
        adj = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        r = self.ca.average_consensus(v, adj, 100)
        self.assertAlmostEqual(r[0], 3.0, delta=0.1)
        print(f"  [PASS] Cons: {r}")
    
    def test_value(self):
        """Should compute consensus value."""
        v = self.ca.consensus_value([1.0, 3.0, 5.0])
        self.assertEqual(v, 3.0)
        print(f"  [PASS] Val: {v}")


class TestTaskAllocation(unittest.TestCase):
    """Test allocation."""
    
    def setUp(self):
        self.ta = TaskAllocation()
    
    def test_greedy(self):
        """Should allocate tasks."""
        robots = [RobotState(0.0, 0.0, 0.0, 0.0),
                  RobotState(10.0, 0.0, 0.0, 0.0)]
        tasks = [(1.0, 0.0), (9.0, 0.0)]
        a = self.ta.greedy_allocation(robots, tasks)
        self.assertGreater(len(a), 0)
        print(f"  [PASS] Alloc: {a}")
    
    def test_distance(self):
        """Should compute travel distance."""
        robots = [RobotState(0.0, 0.0, 0.0, 0.0)]
        tasks = [(3.0, 4.0)]
        a = self.ta.greedy_allocation(robots, tasks)
        d = self.ta.total_travel_distance(robots, a, tasks)
        self.assertEqual(d, 5.0)
        print(f"  [PASS] Dist: {d:.1f}")


class TestFormationControl(unittest.TestCase):
    """Test formation."""
    
    def setUp(self):
        self.fc = FormationControl()
    
    def test_desired(self):
        """Should compute desired position."""
        p = self.fc.desired_position((0.0, 0.0), 0.0, 1.0, 0, 4)
        self.assertAlmostEqual(p[0], 1.0, delta=1e-6)
        print(f"  [PASS] Pos: {p}")
    
    def test_error(self):
        """Should compute formation error."""
        r = RobotState(1.0, 0.0, 0.0, 0.0)
        e = self.fc.formation_error(r, (0.0, 0.0))
        self.assertEqual(e, 1.0)
        print(f"  [PASS] Err: {e:.1f}")


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
