"""
Unit tests for mission planner module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mission_planner import (TaskStatus, Priority, Task,
                             ResourcePool, GoalDecomposer,
                             TaskScheduler, MissionPlanner)


class TestResourcePool(unittest.TestCase):
    """Test resource pool."""
    
    def setUp(self):
        self.pool = ResourcePool()
        self.pool.register("fuel", 100.0)
        self.pool.register("cpu", 2.0)
    
    def test_register(self):
        """Should register resources."""
        self.assertEqual(self.pool.resources["fuel"], 100.0)
        print("  [PASS] Register: fuel=100")
    
    def test_allocate(self):
        """Should allocate resources."""
        ok = self.pool.allocate("task1", "fuel", 30.0)
        self.assertTrue(ok)
        self.assertEqual(self.pool.available("fuel"), 70.0)
        print(f"  [PASS] Allocate: avail={self.pool.available('fuel')}")
    
    def test_allocate_over(self):
        """Should fail when over-allocating."""
        ok = self.pool.allocate("task1", "fuel", 150.0)
        self.assertFalse(ok)
        print("  [PASS] Over-alloc: False")
    
    def test_deallocate(self):
        """Should deallocate."""
        self.pool.allocate("task1", "fuel", 30.0)
        self.pool.deallocate("task1")
        self.assertEqual(self.pool.available("fuel"), 100.0)
        print("  [PASS] Dealloc: restored")


class TestGoalDecomposer(unittest.TestCase):
    """Test goal decomposer."""
    
    def setUp(self):
        self.decomp = GoalDecomposer()
    
    def test_decompose_orbit(self):
        """Should decompose orbit goal."""
        tasks = self.decomp.decompose("Insert into orbit", Priority.HIGH)
        self.assertGreaterEqual(len(tasks), 2)
        self.assertTrue(any("orbit" in t.description.lower() for t in tasks))
        print(f"  [PASS] Orbit: {len(tasks)} tasks")
    
    def test_decompose_land(self):
        """Should decompose landing goal."""
        tasks = self.decomp.decompose("Land on surface", Priority.CRITICAL)
        self.assertGreaterEqual(len(tasks), 2)
        print(f"  [PASS] Land: {len(tasks)} tasks")
    
    def test_decompose_dock(self):
        """Should decompose docking goal."""
        tasks = self.decomp.decompose("Dock with station", Priority.HIGH)
        self.assertGreaterEqual(len(tasks), 2)
        print(f"  [PASS] Dock: {len(tasks)} tasks")
    
    def test_critical_path(self):
        """Should find critical path."""
        tasks = self.decomp.decompose("Test mission", Priority.MEDIUM)
        cp = self.decomp.get_critical_path(tasks)
        self.assertGreater(len(cp), 0)
        print(f"  [PASS] CP: {'->'.join(cp)}")


class TestTaskScheduler(unittest.TestCase):
    """Test task scheduler."""
    
    def setUp(self):
        self.sched = TaskScheduler()
        self.sched.add_tasks([
            Task("A", "Task A", Priority.MEDIUM, 10, [], []),
            Task("B", "Task B", Priority.HIGH, 5, ["A"], []),
            Task("C", "Task C", Priority.LOW, 8, ["A"], []),
        ])
    
    def test_schedule(self):
        """Should schedule with deps."""
        order = self.sched.schedule_tasks()
        self.assertEqual(order[0], "A")
        self.assertIn("B", order[1:])
        self.assertIn("C", order[1:])
        print(f"  [PASS] Schedule: {'->'.join(order)}")
    
    def test_get_ready(self):
        """Should get ready tasks."""
        ready = self.sched.get_ready_tasks()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].task_id, "A")
        print(f"  [PASS] Ready: {ready[0].task_id}")
    
    def test_progress(self):
        """Should track progress."""
        self.assertEqual(self.sched.mission_progress(), 0.0)
        self.sched.mark_completed("A")
        self.assertAlmostEqual(self.sched.mission_progress(), 1/3, places=2)
        print(f"  [PASS] Progress: {self.sched.mission_progress():.2f}")


class TestMissionPlanner(unittest.TestCase):
    """Test unified mission planner."""
    
    def setUp(self):
        self.mp = MissionPlanner()
        self.mp.resources.register("fuel", 100.0)
        self.mp.resources.register("cpu", 4.0)
    
    def test_plan_mission(self):
        """Should plan mission."""
        tasks = self.mp.plan_mission("Orbit insertion", Priority.HIGH)
        self.assertGreater(len(tasks), 0)
        print(f"  [PASS] Plan: {len(tasks)} tasks")
    
    def test_execute_flow(self):
        """Should execute task flow."""
        self.mp.plan_mission("Dock", Priority.HIGH)
        task = self.mp.execute_next()
        self.assertIsNotNone(task)
        self.mp.complete_task(task.task_id)
        self.assertGreater(self.mp.mission_progress(), 0)
        print(f"  [PASS] Execute: {task.task_id}, progress={self.mp.mission_progress():.2f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.mp.plan_mission("Test", Priority.MEDIUM)
        summary = self.mp.planner_summary()
        self.assertIn("total_tasks", summary)
        print(f"  [PASS] Summary: {summary['total_tasks']} tasks")


if __name__ == '__main__':
    unittest.main(verbosity=2)
