"""
Unit tests for rendezvous module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rendezvous import LambertTransfer, PhasingManeuver, RendezvousPlanner


class TestLambertTransfer(unittest.TestCase):
    """Test Lambert's problem solver."""
    
    def setUp(self):
        self.lambert = LambertTransfer(mu_km3_s2=398600.4418)
    
    def test_solve(self):
        """Should solve Lambert's problem."""
        r1 = (6678.0, 0.0, 0.0)  # LEO
        r2 = (0.0, 6678.0, 0.0)  # 90 deg transfer
        result = self.lambert.solve(r1, r2, tof_s=1800.0)
        self.assertIsNotNone(result)
        v1, v2 = result
        self.assertEqual(len(v1), 3)
        print(f"  [PASS] Lambert solve: v1=({v1[0]:.2f}, {v1[1]:.2f}, {v1[2]:.2f})")
    
    def test_transfer_delta_v(self):
        """Should compute transfer delta-v."""
        r1 = (6678.0, 0.0, 0.0)
        v1 = (0.0, 7.725, 0.0)
        r2 = (0.0, 6678.0, 0.0)
        v2 = (-7.725, 0.0, 0.0)
        
        dv = self.lambert.transfer_delta_v(r1, v1, r2, v2, tof_s=1800.0)
        self.assertIsNotNone(dv)
        self.assertGreater(dv, 0.0)
        print(f"  [PASS] Transfer dV: {dv:.1f} m/s")
    
    def test_solve_coaxial(self):
        """Should handle coaxial positions."""
        r1 = (6678.0, 0.0, 0.0)
        r2 = (6678.0, 0.0, 0.0)
        result = self.lambert.solve(r1, r2, tof_s=3600.0)
        # Same position - should still return something
        print(f"  [PASS] Coaxial: {'solved' if result else 'failed gracefully'}")


class TestPhasingManeuver(unittest.TestCase):
    """Test phasing maneuvers."""
    
    def setUp(self):
        self.phasing = PhasingManeuver(mu_km3_s2=398600.4418)
    
    def test_compute_phasing(self):
        """Should compute phasing delta-v."""
        dv = self.phasing.compute_phasing_delta_v(
            initial_altitude_km=400.0,
            target_phase_angle_deg=30.0,
            current_phase_angle_deg=0.0,
            n_revolutions=2
        )
        self.assertGreater(dv, 0.0)
        print(f"  [PASS] Phasing dV: {dv:.2f} m/s")
    
    def test_coelliptic_approach(self):
        """Should compute coelliptic approach."""
        result = self.phasing.coelliptic_approach(
            chaser_altitude_km=400.0,
            target_altitude_km=405.0
        )
        self.assertIn("period_difference_s", result)
        print(f"  [PASS] Coelliptic: dT={result['period_difference_s']:.3f}s")


class TestRendezvousPlanner(unittest.TestCase):
    """Test rendezvous planner."""
    
    def setUp(self):
        self.planner = RendezvousPlanner()
    
    def test_plan_rendezvous(self):
        """Should plan complete rendezvous."""
        plan = self.planner.plan_rendezvous(
            chaser_initial_pos_km=(6678.0, 0.0, 0.0),
            chaser_initial_vel_km_s=(0.0, 7.725, 0.0),
            target_pos_km=(0.0, 6678.0, 0.0),
            target_vel_km_s=(-7.725, 0.0, 0.0),
            tof_s=1800.0
        )
        self.assertIn("total_delta_v_ms", plan)
        self.assertIn("phases", plan)
        self.assertGreater(len(plan["phases"]), 0)
        print(f"  [PASS] Plan: {plan['total_delta_v_ms']:.1f} m/s, {len(plan['phases'])} phases")
    
    def test_tpi(self):
        """Should compute TPI parameters."""
        tpi = self.planner.compute_terminal_phase_initiation(
            range_km=30.0,
            range_rate_ms=2.5,
            los_angle_deg=45.0
        )
        self.assertIn("time_to_go_s", tpi)
        self.assertTrue(tpi["tpi_burn_required"])
        print(f"  [PASS] TPI: t_go={tpi['time_to_go_s']:.1f}s")
    
    def test_tpi_far_range(self):
        """Should not require TPI at far range."""
        tpi = self.planner.compute_terminal_phase_initiation(
            range_km=100.0,
            range_rate_ms=50.0,
            los_angle_deg=0.0
        )
        self.assertFalse(tpi["tpi_burn_required"])
        print("  [PASS] TPI far range: no burn required")


if __name__ == '__main__':
    unittest.main(verbosity=2)
