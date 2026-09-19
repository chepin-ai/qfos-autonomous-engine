"""
Unit tests for swarm coordination module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from swarm_coordination import SwarmAgent, FormationController, TaskAllocator


class TestFormationController(unittest.TestCase):
    """Test formation controller."""
    
    def setUp(self):
        self.fc = FormationController()
        self.leader = SwarmAgent("leader", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
                                 role="leader")
        self.follower = SwarmAgent("follower", (100.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    
    def test_compute_control(self):
        """Should compute control force."""
        force = self.fc.compute_control(self.follower, [self.leader],
                                       self.leader.position_m)
        self.assertIsInstance(force, tuple)
        self.assertEqual(len(force), 3)
        print(f"  [PASS] Force: ({force[0]:.2f}, {force[1]:.2f}, {force[2]:.2f})")
    
    def test_separation(self):
        """Should repel when too close."""
        close = SwarmAgent("close", (50.0, 0.0, 0.0))
        force = self.fc.compute_control(close, [self.leader])
        self.assertLess(force[0], 0)  # Should push away in x
        print(f"  [PASS] Separation: fx={force[0]:.2f} (repulsive)")
    
    def test_update_agent(self):
        """Should update position."""
        pos_before = self.follower.position_m
        self.fc.update_agent(self.follower, (1.0, 0.0, 0.0), dt_s=1.0)
        pos_after = self.follower.position_m
        self.assertNotEqual(pos_before[0], pos_after[0])
        print(f"  [PASS] Update: x {pos_before[0]:.1f} -> {pos_after[0]:.1f}")
    
    def test_line_formation(self):
        """Should create line formation."""
        pattern = FormationController.create_line_formation(3, 1000.0)
        self.assertEqual(len(pattern), 3)
        self.assertEqual(pattern["agent_1"], (1000.0, 0.0, 0.0))
        print(f"  [PASS] Line: {len(pattern)} agents")
    
    def test_triangle_formation(self):
        """Should create triangle formation."""
        pattern = FormationController.create_triangle_formation(1000.0)
        self.assertEqual(len(pattern), 3)
        print(f"  [PASS] Triangle: {len(pattern)} agents")
    
    def test_max_thrust_limit(self):
        """Should limit force to max thrust."""
        agent = SwarmAgent("test", max_thrust_n=5.0)
        # Put very close to cause large force
        close = SwarmAgent("close", (10.0, 0.0, 0.0))
        force = self.fc.compute_control(agent, [close])
        mag = (force[0]**2 + force[1]**2 + force[2]**2)**0.5
        self.assertLessEqual(mag, 5.0 + 0.01)
        print(f"  [PASS] Thrust limit: {mag:.2f} <= 5.0")


class TestTaskAllocator(unittest.TestCase):
    """Test task allocator."""
    
    def setUp(self):
        self.ta = TaskAllocator()
        self.agents = [
            SwarmAgent("a1", (0.0, 0.0, 0.0)),
            SwarmAgent("a2", (1000.0, 0.0, 0.0)),
            SwarmAgent("a3", (2000.0, 0.0, 0.0))
        ]
    
    def test_add_task(self):
        """Should add task."""
        self.ta.add_task("t1", (500.0, 0.0, 0.0))
        self.assertEqual(len(self.ta.tasks), 1)
        print("  [PASS] Task added")
    
    def test_allocate(self):
        """Should allocate tasks."""
        self.ta.add_task("t1", (500.0, 0.0, 0.0), priority=1)
        assignments = self.ta.allocate(self.agents)
        self.assertIn("a1", assignments)
        print(f"  [PASS] Allocated: {len(assignments)} agents")
    
    def test_allocate_priority(self):
        """Should prioritize higher priority tasks."""
        self.ta.add_task("t_far", (5000.0, 0.0, 0.0), priority=2)
        self.ta.add_task("t_near", (100.0, 0.0, 0.0), priority=1)
        assignments = self.ta.allocate(self.agents)
        # a1 should get t_near (higher priority = lower number)
        self.assertEqual(assignments.get("a1"), "t_near")
        print(f"  [PASS] Priority: a1 -> {assignments.get('a1')}")
    
    def test_task_summary(self):
        """Should provide summary."""
        self.ta.add_task("t1", (0.0, 0.0, 0.0), required_agents=1)
        self.ta.allocate(self.agents)
        summary = self.ta.task_summary()
        self.assertEqual(summary["total_tasks"], 1)
        print(f"  [PASS] Summary: {summary['fully_assigned']} fully assigned")


if __name__ == '__main__':
    unittest.main(verbosity=2)
