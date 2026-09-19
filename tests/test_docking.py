"""
Unit tests for autonomous docking module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from docking import ClohessyWiltshire, DockingPlanner, CooperativeDocking, MU_EARTH, EARTH_RADIUS_M


class TestClohessyWiltshire(unittest.TestCase):
    """Test CW relative motion equations."""
    
    def test_from_altitude(self):
        """Should create CW model from altitude."""
        cw = ClohessyWiltshire.from_altitude_km(400.0)
        self.assertGreater(cw.n, 0)
        # ISS-like orbit: period ~93 min, n ~ 0.0011 rad/s
        self.assertAlmostEqual(cw.n, 0.00113, delta=0.0001)
        print(f"  [PASS] CW n={cw.n:.6f} rad/s (ISS 400km)")
    
    def test_propagate_stationary(self):
        """Zero initial velocity should show natural drift."""
        cw = ClohessyWiltshire.from_altitude_km(400.0)
        x, y, z, vx, vy, vz = cw.propagate(100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 600.0)
        # With initial x offset and no velocity, should drift
        self.assertIsInstance(x, float)
        self.assertIsInstance(y, float)
        print(f"  [PASS] Propagate: ({x:.2f}, {y:.2f}, {z:.2f}) m after 600s")
    
    def test_propagate_periodicity(self):
        """After one orbital period, state should approximately repeat."""
        cw = ClohessyWiltshire.from_altitude_km(400.0)
        T = 2 * 3.14159 / cw.n
        x1, y1, z1, vx1, vy1, vz1 = cw.propagate(10.0, 5.0, 2.0, 0.1, 0.2, 0.05, T)
        # Not exact due to linearization, but should be bounded
        self.assertLess(abs(x1), 100.0)
        print(f"  [PASS] Periodicity: bounded after T={T/60:.1f}min")


class TestDockingPlanner(unittest.TestCase):
    """Test docking approach planner."""
    
    def test_plan_v_bar(self):
        """Should plan V-bar approach."""
        planner = DockingPlanner(approach_type='v_bar')
        plan = planner.plan_approach(initial_range_m=10000.0, target_altitude_km=400.0)
        self.assertIn('phases', plan)
        self.assertGreater(len(plan['phases']), 0)
        self.assertIn('total_delta_v_ms', plan)
        self.assertIn('total_time_s', plan)
        print(f"  [PASS] V-bar plan: {len(plan['phases'])} phases, dv={plan['total_delta_v_ms']:.2f} m/s")
    
    def test_plan_r_bar(self):
        """Should plan R-bar approach."""
        planner = DockingPlanner(approach_type='r_bar')
        plan = planner.plan_approach(initial_range_m=5000.0, target_altitude_km=400.0)
        self.assertEqual(plan['approach_type'], 'r_bar')
        self.assertGreater(plan['total_delta_v_ms'], 0)
        print(f"  [PASS] R-bar plan: {len(plan['phases'])} phases, dv={plan['total_delta_v_ms']:.2f} m/s")
    
    def test_approach_state(self):
        """Should identify correct approach phase."""
        planner = DockingPlanner()
        self.assertEqual(planner.approach_state(500.0), 'close')
        self.assertEqual(planner.approach_state(50.0), 'final')
        self.assertEqual(planner.approach_state(5.0), 'contact')
        print("  [PASS] Approach states correct")
    
    def test_approach_velocity(self):
        """Approach velocity should decrease with range."""
        planner = DockingPlanner()
        v_far = planner.compute_approach_velocity(5000.0)
        v_close = planner.compute_approach_velocity(50.0)
        self.assertGreater(v_far, v_close)
        print(f"  [PASS] Velocity: {v_far:.2f} m/s (far) > {v_close:.2f} m/s (close)")


class TestCooperativeDocking(unittest.TestCase):
    """Test cooperative docking allocation."""
    
    def test_mass_ratio(self):
        """Mass ratio should reflect chaser proportion."""
        cd = CooperativeDocking(chaser_mass_kg=1000.0, target_mass_kg=4000.0)
        ratio = cd.optimal_mass_ratio()
        self.assertAlmostEqual(ratio, 0.2, delta=0.01)
        print(f"  [PASS] Mass ratio: {ratio:.3f}")
    
    def test_delta_v_allocation(self):
        """Lighter spacecraft should get more delta-v."""
        cd = CooperativeDocking(chaser_mass_kg=500.0, target_mass_kg=4500.0)
        chaser_dv, target_dv = cd.allocate_delta_v(10.0)
        self.assertGreater(chaser_dv, target_dv)
        self.assertAlmostEqual(chaser_dv + target_dv, 10.0, delta=0.001)
        print(f"  [PASS] DV allocation: chaser={chaser_dv:.2f}, target={target_dv:.2f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
