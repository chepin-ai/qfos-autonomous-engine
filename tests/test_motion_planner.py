"""
Unit tests for motion planner module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from motion_planner import AStarPlanner, RRTPlanner, MotionPlanner, Obstacle, Node


class TestAStarPlanner(unittest.TestCase):
    """Test A* planner."""
    
    def setUp(self):
        self.planner = AStarPlanner(grid_size=1.0)
    
    def test_plan_straight(self):
        """Should plan straight path."""
        path = self.planner.plan((0, 0, 0), (5, 0, 0))
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0, 0))
        self.assertEqual(path[-1], (5, 0, 0))
        print(f"  [PASS] Straight: {len(path)} points")
    
    def test_plan_with_obstacle(self):
        """Should plan around obstacle."""
        self.planner.add_obstacle(Obstacle(2, 0, 0, 0.8))
        path = self.planner.plan((0, 0, 0), (5, 0, 0))
        self.assertIsNotNone(path)
        # Path should avoid (2, 0, 0) - check all points near obstacle center in 3D
        for p in path:
            dist_to_obs = ((p[0]-2)**2 + (p[1]-0)**2 + (p[2]-0)**2) ** 0.5
            self.assertGreater(
                dist_to_obs, 0.75,
                f"Path goes through obstacle at {p}, dist={dist_to_obs:.2f}"
            )
        print(f"  [PASS] Avoid: {len(path)} points")
    
    def test_collision_detection(self):
        """Should detect collisions."""
        self.planner.add_obstacle(Obstacle(1, 1, 0, 1.0))
        self.assertTrue(self.planner.is_collision(1, 1, 0))
        self.assertFalse(self.planner.is_collision(5, 5, 0))
        print("  [PASS] Collision: detected")
    
    def test_no_path(self):
        """Should return None when blocked."""
        self.planner.add_obstacle(Obstacle(0, 0, 0, 2.0))
        path = self.planner.plan((0, 0, 0), (5, 0, 0))
        self.assertIsNone(path)
        print("  [PASS] Blocked: None")
    
    def test_heuristic(self):
        """Should compute heuristic."""
        h = self.planner.heuristic((0, 0, 0), (3, 4, 0))
        self.assertEqual(h, 5.0)
        print(f"  [PASS] Heuristic: {h}")


class TestRRTPlanner(unittest.TestCase):
    """Test RRT planner."""
    
    def setUp(self):
        self.planner = RRTPlanner(step_size=1.0, max_iterations=5000, seed=42)
        self.planner.set_bounds(0, 10, 0, 10, 0, 0)
    
    def test_plan(self):
        """Should plan path."""
        path = self.planner.plan((0, 0, 0), (8, 8, 0), goal_tolerance=1.0)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0, 0))
        self.assertEqual(path[-1], (8, 8, 0))
        print(f"  [PASS] RRT: {len(path)} points")
    
    def test_plan_with_obstacle(self):
        """Should plan around obstacle."""
        self.planner.add_obstacle(Obstacle(4, 4, 0, 2.0))
        path = self.planner.plan((0, 0, 0), (8, 8, 0), goal_tolerance=1.5)
        self.assertIsNotNone(path)
        print(f"  [PASS] RRT avoid: {len(path)} points")
    
    def test_nearest(self):
        """Should find nearest node."""
        self.planner.nodes = [Node(0, 0), Node(3, 4), Node(10, 10)]
        nearest = self.planner.nearest(0.5, 0.5, 0)
        self.assertEqual((nearest.x, nearest.y), (0, 0))
        print(f"  [PASS] Nearest: ({nearest.x}, {nearest.y})")
    
    def test_steer(self):
        """Should steer toward target."""
        from_node = Node(0, 0)
        new_node = self.planner.steer(from_node, 3, 4, 0)
        dist = self.planner.distance(from_node, new_node)
        self.assertAlmostEqual(dist, 1.0, places=5)
        print(f"  [PASS] Steer: dist={dist:.2f}")


class TestMotionPlanner(unittest.TestCase):
    """Test unified motion planner."""
    
    def setUp(self):
        self.mp = MotionPlanner()
    
    def test_add_obstacle(self):
        """Should add obstacle."""
        self.mp.add_obstacle(Obstacle(1, 1, 0, 1.0))
        self.assertEqual(len(self.mp.astar.obstacles), 1)
        print("  [PASS] Add obs: 1")
    
    def test_plan_astar(self):
        """Should plan with A*."""
        path = self.mp.plan_astar((0, 0, 0), (5, 5, 0))
        self.assertIsNotNone(path)
        print(f"  [PASS] A*: {len(path)} points")
    
    def test_plan_rrt(self):
        """Should plan with RRT."""
        self.mp.rrt.set_bounds(0, 10, 0, 10, 0, 0)
        path = self.mp.plan_rrt((0, 0, 0), (8, 8, 0))
        self.assertIsNotNone(path)
        print(f"  [PASS] RRT: {len(path)} points")
    
    def test_path_length(self):
        """Should compute path length."""
        path = [(0, 0, 0), (3, 4, 0)]
        length = self.mp.path_length(path)
        self.assertEqual(length, 5.0)
        print(f"  [PASS] Length: {length}")
    
    def test_summary(self):
        """Should provide summary."""
        self.mp.add_obstacle(Obstacle(1, 1, 0, 1.0))
        summary = self.mp.planner_summary()
        self.assertEqual(summary["astar_obstacles"], 1)
        print(f"  [PASS] Summary: {summary}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
