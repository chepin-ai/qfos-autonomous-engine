"""
Unit tests for digital twin module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from digital_twin import DigitalTwin, TwinState, PhysicsModel


class TestPhysicsModel(unittest.TestCase):
    """Test physics model."""
    
    def setUp(self):
        self.physics = PhysicsModel()
    
    def test_gravity(self):
        """Should compute gravity."""
        g = self.physics.compute_gravity((7000000.0, 0.0, 0.0), 1000.0)
        self.assertLess(g[0], 0)  # Toward origin
        print(f"  [PASS] Gravity: gx={g[0]:.4f}")
    
    def test_integrate(self):
        """Should integrate state."""
        state = TwinState(position_m=(7000000.0, 0.0, 0.0),
                         velocity_ms=(0.0, 7500.0, 0.0),
                         mass_kg=1000.0, fuel_kg=500.0)
        new_state = self.physics.integrate(state, (0.0, 0.0, 0.0), dt_s=1.0)
        self.assertNotEqual(new_state.position_m[1], 0.0)
        print(f"  [PASS] Integrate: y={new_state.position_m[1]:.1f}")
    
    def test_thrust(self):
        """Should apply thrust."""
        state = TwinState(position_m=(7000000.0, 0.0, 0.0),
                         velocity_ms=(0.0, 0.0, 0.0),
                         mass_kg=1000.0, fuel_kg=100.0)
        new_state = self.physics.integrate(state, (10000.0, 0.0, 0.0), dt_s=1.0)
        self.assertGreater(new_state.velocity_ms[0], 0)
        self.assertLess(new_state.fuel_kg, state.fuel_kg)
        print(f"  [PASS] Thrust: vx={new_state.velocity_ms[0]:.3f}, fuel={new_state.fuel_kg:.2f}")


class TestDigitalTwin(unittest.TestCase):
    """Test digital twin."""
    
    def setUp(self):
        self.twin = DigitalTwin("sc_001")
        self.twin.state = TwinState(position_m=(7000000.0, 0.0, 0.0),
                                    velocity_ms=(0.0, 7500.0, 0.0),
                                    mass_kg=1000.0, fuel_kg=500.0)
    
    def test_synchronize(self):
        """Should sync with measured state."""
        measured = TwinState(position_m=(7000100.0, 0.0, 0.0),
                            velocity_ms=(0.0, 7500.0, 0.0),
                            mass_kg=1000.0, fuel_kg=500.0)
        self.twin.synchronize(measured)
        self.assertAlmostEqual(self.twin.sync_offset, 100.0, delta=1.0)
        print(f"  [PASS] Sync: offset={self.twin.sync_offset:.1f}m")
    
    def test_predict(self):
        """Should predict future states."""
        states = self.twin.predict(duration_s=100.0)
        self.assertGreater(len(states), 0)
        print(f"  [PASS] Predict: {len(states)} states")
    
    def test_predict_with_thrust(self):
        """Should predict with thrust profile."""
        thrust = [(0.0, (50.0, 0.0, 0.0))]
        states = self.twin.predict(duration_s=100.0, thrust_profile=thrust)
        self.assertGreater(len(states), 0)
        print(f"  [PASS] Predict thrust: {len(states)} states")
    
    def test_detect_divergence(self):
        """Should detect divergence."""
        measured = TwinState(position_m=(7000000.0, 0.0, 0.0),
                            velocity_ms=(0.0, 7500.0, 0.0))
        div = self.twin.detect_divergence(measured, threshold_m=100.0)
        self.assertFalse(div["is_diverged"])
        print(f"  [PASS] Divergence: {div['position_divergence_m']:.1f}m")
    
    def test_detect_divergence_true(self):
        """Should detect true divergence."""
        measured = TwinState(position_m=(7005000.0, 0.0, 0.0),
                            velocity_ms=(0.0, 7500.0, 0.0))
        div = self.twin.detect_divergence(measured, threshold_m=100.0)
        self.assertTrue(div["is_diverged"])
        print(f"  [PASS] Diverged: {div['position_divergence_m']:.1f}m")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.twin.twin_summary()
        self.assertEqual(summary["spacecraft_id"], "sc_001")
        print(f"  [PASS] Summary: {summary['spacecraft_id']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
