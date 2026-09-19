"""
Unit tests for guidance navigation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from guidance_navigation import (OrbitalState, TransferSolution, InterceptPlan,
                                 LambertSolver, InterceptGuidance, DeltaVBudget,
                                 GuidanceNavigation)


class TestLambertSolver(unittest.TestCase):
    """Test Lambert solver."""
    
    def setUp(self):
        self.solver = LambertSolver(mu=398600.4418)
    
    def test_solve_hohmann(self):
        """Should solve Hohmann-like transfer."""
        r1 = (7000, 0, 0)
        r2 = (0, 7000, 0)  # 90-degree transfer
        tof = 1800  # 30 min
        sol = self.solver.solve(r1, r2, tof)
        self.assertIsNotNone(sol)
        self.assertTrue(sol.is_valid)
        print(f"  [PASS] Lambert: dv={sol.total_delta_v:.3f} km/s")
    
    def test_solve_invalid_tof(self):
        """Should handle invalid TOF."""
        r1 = (7000, 0, 0)
        r2 = (7000, 100, 0)
        sol = self.solver.solve(r1, r2, -1)
        self.assertIsNone(sol)
        print("  [PASS] Invalid TOF: None")
    
    def test_solve_zero_position(self):
        """Should handle zero position."""
        sol = self.solver.solve((0, 0, 0), (1, 0, 0), 100)
        self.assertIsNone(sol)
        print("  [PASS] Zero pos: None")


class TestInterceptGuidance(unittest.TestCase):
    """Test intercept guidance."""
    
    def setUp(self):
        self.g = InterceptGuidance(nav_constant=3.0)
    
    def test_compute_acceleration(self):
        """Should compute lateral acceleration."""
        missile_pos = (0, 0, 0)
        missile_vel = (1, 0, 0)
        target_pos = (10, 5, 0)
        target_vel = (0.9, 0, 0)
        
        accel = self.g.compute_acceleration(missile_pos, missile_vel,
                                            target_pos, target_vel)
        self.assertEqual(len(accel), 3)
        print(f"  [PASS] Acceleration: {accel}")
    
    def test_zero_los(self):
        """Should handle zero line of sight."""
        accel = self.g.compute_acceleration(
            (0, 0, 0), (1, 0, 0),
            (0, 0, 0), (0, 0, 0)
        )
        self.assertEqual(accel, (0, 0, 0))
        print("  [PASS] Zero LOS: (0, 0, 0)")


class TestDeltaVBudget(unittest.TestCase):
    """Test delta-v budget."""
    
    def setUp(self):
        self.db = DeltaVBudget()
    
    def test_add_maneuver(self):
        """Should add maneuver."""
        self.db.add_maneuver("departure", 3.5, 0.1)
        self.assertEqual(len(self.db.maneuvers), 1)
        print("  [PASS] Add: 1 maneuver")
    
    def test_total_budget(self):
        """Should compute total with margin."""
        self.db.add_maneuver("a", 1.0, 0.1)
        self.db.add_maneuver("b", 2.0, 0.1)
        total = self.db.total_budget()
        self.assertAlmostEqual(total, 3.3, places=5)
        print(f"  [PASS] Total: {total:.1f} km/s")
    
    def test_total_nominal(self):
        """Should compute nominal."""
        self.db.add_maneuver("a", 1.0, 0.1)
        self.db.add_maneuver("b", 2.0, 0.1)
        total = self.db.total_nominal()
        self.assertEqual(total, 3.0)
        print(f"  [PASS] Nominal: {total:.1f} km/s")
    
    def test_breakdown(self):
        """Should provide breakdown."""
        self.db.add_maneuver("a", 1.0, 0.1)
        bd = self.db.budget_breakdown()
        self.assertIn("maneuvers", bd)
        self.assertIn("total_with_margin", bd)
        print(f"  [PASS] Breakdown: {bd['total_with_margin']:.1f} km/s")
    
    def test_hohmann(self):
        """Should compute Hohmann transfer."""
        result = self.db.hohmann_transfer(7000, 14000)
        self.assertIn("delta_v1", result)
        self.assertIn("delta_v2", result)
        self.assertGreater(result["total_delta_v"], 0)
        print(f"  [PASS] Hohmann: {result['total_delta_v']:.3f} km/s")


class TestGuidanceNavigation(unittest.TestCase):
    """Test unified guidance navigation."""
    
    def setUp(self):
        self.gn = GuidanceNavigation()
    
    def test_plan_transfer(self):
        """Should plan transfer."""
        s1 = OrbitalState((7000, 0, 0), (0, 7.5, 0))
        s2 = OrbitalState((0, 7000, 0), (-7.5, 0, 0))
        sol = self.gn.plan_transfer(s1, s2, 1800)
        self.assertIsNotNone(sol)
        print(f"  [PASS] Transfer: dv={sol.total_delta_v:.3f} km/s")
    
    def test_compute_intercept(self):
        """Should compute intercept."""
        missile = OrbitalState((0, 0, 0), (1, 0, 0))
        target = OrbitalState((10, 5, 0), (0.9, 0, 0))
        accel = self.gn.compute_intercept(missile, target)
        self.assertEqual(len(accel), 3)
        print("  [PASS] Intercept: ok")
    
    def test_summary(self):
        """Should provide summary."""
        self.gn.budget.add_maneuver("test", 1.0)
        summary = self.gn.gn_summary()
        self.assertEqual(summary["maneuvers_planned"], 1)
        print(f"  [PASS] Summary: {summary['maneuvers_planned']} maneuvers")


if __name__ == '__main__':
    unittest.main(verbosity=2)
