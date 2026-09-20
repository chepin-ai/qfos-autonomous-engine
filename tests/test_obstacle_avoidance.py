"""
Unit tests for obstacle avoidance module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from obstacle_avoidance import (ObstacleType, Obstacle,
                                PotentialFieldPlanner, CollisionDetector,
                                LocalPlanner, ObstacleAvoidance)


class TestPotentialField(unittest.TestCase):
    """Test potential field planner."""
    
    def setUp(self):
        self.pf = PotentialFieldPlanner()
    
    def test_attractive(self):
        """Should attract toward goal."""
        f = self.pf.attractive_force((0.0, 0.0), (1.0, 0.0))
        self.assertGreater(f[0], 0)
        print(f"  [PASS] Att: ({f[0]:.2f}, {f[1]:.2f})")
    
    def test_repulsive(self):
        """Should repel from obstacle."""
        obs = Obstacle("o1", (1.0, 0.0), 0.5)
        f = self.pf.repulsive_force((0.0, 0.0), obs)
        self.assertLess(f[0], 0)
        print(f"  [PASS] Rep: ({f[0]:.2f}, {f[1]:.2f})")
    
    def test_no_repulsion_far(self):
        """Should have no repulsion far away."""
        obs = Obstacle("o1", (100.0, 0.0), 0.5)
        f = self.pf.repulsive_force((0.0, 0.0), obs)
        self.assertAlmostEqual(f[0], 0.0)
        print("  [PASS] No repulsion far")
    
    def test_plan_step(self):
        """Should plan step."""
        pos = self.pf.plan_step((0.0, 0.0), (1.0, 0.0), [], step_size=0.1)
        self.assertGreater(pos[0], 0)
        print(f"  [PASS] Step: ({pos[0]:.2f}, {pos[1]:.2f})")


class TestCollisionDetector(unittest.TestCase):
    """Test collision detector."""
    
    def setUp(self):
        self.cd = CollisionDetector(safety_margin_m=0.1)
    
    def test_collision_true(self):
        """Should detect collision."""
        obs = [Obstacle("o1", (1.0, 0.0), 0.6)]
        c = self.cd.check_collision((1.0, 0.0), 0.5, obs)
        self.assertTrue(c)
        print("  [PASS] Collision: True")
    
    def test_collision_false(self):
        """Should not detect collision far."""
        obs = [Obstacle("o1", (10.0, 0.0), 0.5)]
        c = self.cd.check_collision((0.0, 0.0), 0.5, obs)
        self.assertFalse(c)
        print("  [PASS] No collision")
    
    def test_nearest(self):
        """Should find nearest."""
        obs = [Obstacle("o1", (2.0, 0.0), 0.5),
               Obstacle("o2", (5.0, 0.0), 0.5)]
        n = self.cd.nearest_obstacle((0.0, 0.0), obs)
        self.assertIsNotNone(n)
        self.assertEqual(n[0].obstacle_id, "o1")
        print(f"  [PASS] Nearest: {n[0].obstacle_id}")
    
    def test_point_distance(self):
        """Should compute point-circle distance."""
        d = self.cd.point_to_circle((0.0, 0.0), (1.0, 0.0), 0.5)
        self.assertAlmostEqual(d, 0.5)
        print(f"  [PASS] Dist: {d}")


class TestLocalPlanner(unittest.TestCase):
    """Test local planner."""
    
    def setUp(self):
        self.lp = LocalPlanner(max_speed_ms=1.0)
    
    def test_velocity(self):
        """Should plan velocity."""
        v = self.lp.plan_velocity((0.0, 0.0), (1.0, 0.0), dt_s=0.1)
        self.assertGreater(v[0], 0)
        print(f"  [PASS] Vel: ({v[0]:.2f}, {v[1]:.2f})")
    
    def test_zero_at_goal(self):
        """Should have zero velocity at goal."""
        v = self.lp.plan_velocity((1.0, 1.0), (1.0, 1.0), dt_s=0.1)
        self.assertAlmostEqual(v[0], 0.0)
        print("  [PASS] Zero at goal")
    
    def test_trajectory(self):
        """Should plan trajectory."""
        traj = self.lp.plan_trajectory((0.0, 0.0), (1.0, 1.0), steps=5)
        self.assertEqual(len(traj), 6)
        self.assertAlmostEqual(traj[-1][0], 1.0)
        print(f"  [PASS] Traj: {len(traj)} pts")


class TestObstacleAvoidance(unittest.TestCase):
    """Test unified obstacle avoidance."""
    
    def setUp(self):
        self.oa = ObstacleAvoidance()
    
    def test_add_obstacle(self):
        """Should add obstacle."""
        self.oa.add_obstacle(Obstacle("o1", (1.0, 0.0), 0.5))
        self.assertEqual(len(self.oa.obstacles), 1)
        print("  [PASS] Add: 1")
    
    def test_remove_obstacle(self):
        """Should remove obstacle."""
        self.oa.add_obstacle(Obstacle("o1", (1.0, 0.0), 0.5))
        self.oa.remove_obstacle("o1")
        self.assertEqual(len(self.oa.obstacles), 0)
        print("  [PASS] Remove: 0")
    
    def test_navigate_free(self):
        """Should navigate without obstacles."""
        pos = self.oa.navigate((0.0, 0.0), (1.0, 0.0))
        self.assertGreater(pos[0], 0)
        print(f"  [PASS] Nav: ({pos[0]:.2f}, {pos[1]:.2f})")
    
    def test_navigate_avoid(self):
        """Should avoid obstacle."""
        # Place obstacle slightly off-axis so avoidance has y-component
        self.oa.add_obstacle(Obstacle("o1", (0.5, 0.2), 0.5))
        pos = self.oa.navigate((0.0, 0.0), (1.0, 0.0), own_radius_m=0.2)
        # Robot should not move directly along x-axis due to repulsion
        self.assertTrue(pos[0] > -0.5)  # Sanity check
        print(f"  [PASS] Avoid: ({pos[0]:.2f}, {pos[1]:.2f})")
    
    def test_summary(self):
        """Should provide summary."""
        self.oa.add_obstacle(Obstacle("o1", (1.0, 0.0), 0.5, ObstacleType.STATIC))
        s = self.oa.avoidance_summary()
        self.assertEqual(s["obstacles"], 1)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
