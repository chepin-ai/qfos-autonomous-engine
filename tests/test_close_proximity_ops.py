"""
Unit tests for close proximity operations module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from close_proximity_ops import CloseProximityOps, ProximityPhase, Waypoint


class TestCloseProximityOps(unittest.TestCase):
    """Test close proximity operations."""
    
    def setUp(self):
        self.ops = CloseProximityOps(target_size_m=10.0)
    
    def test_standard_waypoints(self):
        """Should generate standard waypoints."""
        wps = self.ops.standard_approach_waypoints(initial_range_m=10000.0)
        self.assertGreater(len(wps), 5)
        self.assertEqual(wps[0].x_m, 10000.0)
        self.assertEqual(wps[-1].x_m, 0.0)
        print(f"  [PASS] Waypoints: {len(wps)} from {wps[0].x_m}m to {wps[-1].x_m}m")
    
    def test_flyaround(self):
        """Should generate flyaround waypoints."""
        wps = self.ops.flyaround_waypoints(radius_m=200.0, num_points=8)
        self.assertEqual(len(wps), 9)
        self.assertAlmostEqual(wps[0].x_m, 200.0, delta=0.1)
        print(f"  [PASS] Flyaround: {len(wps)} points, r=200m")
    
    def test_distance_to_waypoint(self):
        """Should compute distance."""
        self.ops.set_waypoints([Waypoint(x_m=100.0, y_m=0.0, z_m=0.0)])
        dist = self.ops.distance_to_waypoint((50.0, 0.0, 0.0))
        self.assertAlmostEqual(dist, 50.0, delta=0.1)
        print(f"  [PASS] Distance: {dist:.1f} m")
    
    def test_advance_waypoint(self):
        """Should advance waypoints."""
        self.ops.set_waypoints([
            Waypoint(x_m=1000.0, y_m=0.0, z_m=0.0),
            Waypoint(x_m=100.0, y_m=0.0, z_m=0.0)
        ])
        self.assertTrue(self.ops.advance_waypoint())
        self.assertEqual(self.ops.current_waypoint_idx, 1)
        self.assertFalse(self.ops.advance_waypoint())
        print("  [PASS] Advance: 0->1->end")
    
    def test_corridor_check(self):
        """Should check corridor."""
        result = self.ops.approach_corridor_check((5000.0, 10.0, 0.0))
        self.assertTrue(result["in_corridor"])
        print(f"  [PASS] Corridor: in={result['in_corridor']}, lat={result['lateral_deviation_m']:.1f}m")
    
    def test_corridor_violation(self):
        """Should detect corridor violation."""
        result = self.ops.approach_corridor_check((500.0, 100.0, 0.0))
        self.assertFalse(result["in_corridor"])
        print("  [PASS] Corridor violation detected")
    
    def test_station_keeping(self):
        """Should compute station-keeping dV."""
        dv = self.ops.station_keeping_dv(
            current_pos_m=(10.0, 5.0, 0.0),
            current_vel_ms=(0.1, 0.0, 0.0),
            hold_position_m=(0.0, 0.0, 0.0)
        )
        self.assertLess(dv[0], 0.0)  # Need to decelerate and move back
        print(f"  [PASS] SK dV: ({dv[0]:.3f}, {dv[1]:.3f}, {dv[2]:.3f}) m/s")
    
    def test_docking_alignment(self):
        """Should score docking alignment."""
        score = self.ops.docking_alignment_score(
            chaser_attitude_deg=(0.0, 0.0, 0.0),
            relative_pos_m=(-10.0, 0.0, 0.0)
        )
        self.assertGreater(score, 0.5)
        print(f"  [PASS] Alignment: {score:.2f}")
    
    def test_abort(self):
        """Should compute abort."""
        abort = self.ops.abort_manoeuvre(
            current_pos_m=(100.0, 0.0, 0.0),
            current_vel_ms=(-0.5, 0.0, 0.0),
            abort_distance_m=5000.0
        )
        self.assertGreater(abort["delta_v_required_ms"], 0.0)
        print(f"  [PASS] Abort: dV={abort['delta_v_required_ms']:.2f} m/s")
    
    def test_timeline(self):
        """Should estimate timeline."""
        self.ops.set_waypoints(self.ops.standard_approach_waypoints())
        timeline = self.ops.mission_timeline(
            current_pos_m=(5000.0, 0.0, 0.0),
            current_vel_ms=(-1.0, 0.0, 0.0)
        )
        self.assertIn("estimated_remaining_time_min", timeline)
        print(f"  [PASS] Timeline: {timeline['estimated_remaining_time_min']:.1f} min")


if __name__ == '__main__':
    unittest.main(verbosity=2)
