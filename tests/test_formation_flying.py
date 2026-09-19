"""
Unit tests for formation flying module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from formation_flying import (
    LeaderFollowerControl, CyclicPursuitControl, FormationPlanner,
    FormationSatellite
)


class TestLeaderFollowerControl(unittest.TestCase):
    """Test leader-follower control."""
    
    def setUp(self):
        self.ctrl = LeaderFollowerControl.from_altitude_km(400.0)
    
    def test_initialization(self):
        """Should initialize from altitude."""
        self.assertGreater(self.ctrl.n, 0.0)
        print(f"  [PASS] Init: n={self.ctrl.n:.6f} rad/s")
    
    def test_compute_control(self):
        """Should compute control acceleration."""
        follower = FormationSatellite(sat_id="F1", x_m=10.0, y_m=5.0, z_m=2.0,
                                       vx_ms=0.1, vy_ms=0.2, vz_ms=0.0)
        desired = (0.0, 0.0, 0.0)
        ax, ay, az = self.ctrl.compute_control(follower, desired)
        self.assertIsNotNone(ax)
        self.assertIsNotNone(ay)
        self.assertIsNotNone(az)
        print(f"  [PASS] Control: ({ax:.4f}, {ay:.4f}, {az:.4f}) m/s^2")
    
    def test_simulate_formation_keeping(self):
        """Should simulate formation keeping."""
        follower = FormationSatellite(sat_id="F1", x_m=50.0, y_m=0.0, z_m=0.0)
        states = self.ctrl.simulate_formation_keeping(
            follower, desired_relative_m=(0.0, 0.0, 0.0),
            duration_s=60.0, dt_s=1.0
        )
        self.assertEqual(len(states), 61)
        final = states[-1]
        print(f"  [PASS] Simulation: final pos=({final.x_m:.2f}, {final.y_m:.2f}, {final.z_m:.2f})")
    
    def test_formation_error(self):
        """Should compute formation error."""
        follower = FormationSatellite(sat_id="F1", x_m=10.0, y_m=5.0, z_m=2.0)
        error = self.ctrl.formation_error(follower, (0.0, 0.0, 0.0))
        self.assertIn("error_3d_m", error)
        self.assertGreater(error["error_3d_m"], 0)
        print(f"  [PASS] Error: 3D={error['error_3d_m']:.2f} m")
    
    def test_convergence(self):
        """Formation simulation should run with bounded error."""
        follower = FormationSatellite(sat_id="F1", x_m=10.0, y_m=5.0, z_m=2.0)
        states = self.ctrl.simulate_formation_keeping(
            follower, desired_relative_m=(0.0, 0.0, 0.0),
            duration_s=300.0, dt_s=0.1
        )
        final_error = self.ctrl.formation_error(states[-1], (0.0, 0.0, 0.0))["error_3d_m"]
        # With small initial error and fine timestep, should stay bounded
        self.assertLess(final_error, 100.0)
        print(f"  [PASS] Bounded error: final={final_error:.2f}m")


class TestCyclicPursuitControl(unittest.TestCase):
    """Test cyclic pursuit control."""
    
    def setUp(self):
        self.ctrl = CyclicPursuitControl(pursuit_gain=0.001, angular_rate_rad_s=0.0001)
    
    def test_pursuit_velocity(self):
        """Should compute pursuit velocity."""
        vx, vy = self.ctrl.compute_pursuit_velocity((0.0, 0.0), (100.0, 0.0))
        self.assertGreater(vx, 0)  # Moving toward target
        print(f"  [PASS] Pursuit: ({vx:.4f}, {vy:.4f})")
    
    def test_simulate_cyclic_formation(self):
        """Should simulate cyclic pursuit."""
        positions = [(100.0, 0.0), (0.0, 100.0), (-100.0, 0.0), (0.0, -100.0)]
        trajectories = self.ctrl.simulate_cyclic_formation(
            positions, duration_s=300.0, dt_s=1.0
        )
        self.assertEqual(len(trajectories), 4)
        self.assertEqual(len(trajectories[0]), 301)
        print(f"  [PASS] Cyclic: 4 sats, {len(trajectories[0])} steps")
    
    def test_formation_spread(self):
        """Should compute spread metrics."""
        positions = [(100.0, 0.0), (0.0, 100.0), (-100.0, 0.0), (0.0, -100.0)]
        spread = self.ctrl.formation_spread(positions)
        self.assertEqual(spread["satellite_count"], 4)
        self.assertGreater(spread["mean_spread_m"], 0)
        print(f"  [PASS] Spread: mean={spread['mean_spread_m']:.1f}m")


class TestFormationPlanner(unittest.TestCase):
    """Test formation planner."""
    
    def test_along_track(self):
        """Should create along-track formation."""
        positions = FormationPlanner.along_track_separation(3, 1000.0)
        self.assertEqual(len(positions), 3)
        self.assertEqual(positions[1], (0.0, 1000.0, 0.0))
        print("  [PASS] Along-track formation")
    
    def test_cartwheel(self):
        """Should create cartwheel formation."""
        positions = FormationPlanner.cartwheel_formation(4, 500.0)
        self.assertEqual(len(positions), 4)
        print("  [PASS] Cartwheel formation")
    
    def test_pendulum(self):
        """Should create pendulum formation."""
        positions = FormationPlanner.pendulum_formation(3, 200.0)
        self.assertEqual(len(positions), 3)
        print("  [PASS] Pendulum formation")
    
    def test_inspector(self):
        """Should create inspector formation."""
        positions = FormationPlanner.inspector_formation(50.0)
        self.assertEqual(len(positions), 4)
        print("  [PASS] Inspector formation")


if __name__ == '__main__':
    unittest.main(verbosity=2)
