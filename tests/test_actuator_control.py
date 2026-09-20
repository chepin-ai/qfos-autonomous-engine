"""
Unit tests for actuator control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from actuator_control import (ControlMode, ControlState,
                              PIDController, FeedforwardController,
                              SaturationLimiter, HybridController,
                              ActuatorControl)


class TestPIDController(unittest.TestCase):
    """Test PID controller."""
    
    def setUp(self):
        self.pid = PIDController(kp=2.0, ki=0.5, kd=0.1)
    
    def test_proportional(self):
        """Should produce proportional output."""
        pid = PIDController(kp=2.0, ki=0.0, kd=0.0)
        out = pid.update(10.0, 0.0, dt_s=0.01)
        self.assertAlmostEqual(out, 20.0, places=1)
        print(f"  [PASS] P: {out:.1f}")
    
    def test_integral(self):
        """Should accumulate integral."""
        self.pid.reset()
        for _ in range(10):
            out = self.pid.update(1.0, 0.0, dt_s=0.01)
        self.assertGreater(self.pid.integral, 0)
        print(f"  [PASS] I: int={self.pid.integral:.4f}")
    
    def test_reset(self):
        """Should reset state."""
        self.pid.update(1.0, 0.0)
        self.pid.reset()
        self.assertEqual(self.pid.integral, 0.0)
        print("  [PASS] Reset")
    
    def test_saturation(self):
        """Should saturate output."""
        pid = PIDController(kp=1000.0, output_limit=50.0)
        out = pid.update(10.0, 0.0)
        self.assertEqual(abs(out), 50.0)
        print(f"  [PASS] Sat: {out}")


class TestFeedforwardController(unittest.TestCase):
    """Test feedforward controller."""
    
    def setUp(self):
        self.ff = FeedforwardController(mass_kg=2.0)
    
    def test_compute(self):
        """Should compute force."""
        f = self.ff.compute(1.0)
        self.assertAlmostEqual(f, 2.0)
        print(f"  [PASS] F=ma: {f}")
    
    def test_gravity(self):
        """Should include gravity."""
        f = self.ff.compute(0.0, gravity_compensation=True)
        self.assertAlmostEqual(f, 2.0 * 9.81)
        print(f"  [PASS] Gravity: {f:.2f}")
    
    def test_trajectory(self):
        """Should compute trajectory forces."""
        pos = [0.0, 0.01, 0.04, 0.09, 0.16]
        forces = self.ff.compute_trajectory(pos, dt_s=0.01)
        self.assertEqual(len(forces), 5)
        print(f"  [PASS] Traj: {len(forces)} points")


class TestSaturationLimiter(unittest.TestCase):
    """Test saturation limiter."""
    
    def setUp(self):
        self.lim = SaturationLimiter(max_magnitude=10.0, max_rate=100.0)
    
    def test_magnitude(self):
        """Should limit magnitude."""
        # Rate limit allows 1.0 per 0.01s step, so first call gives 1.0
        out = self.lim.limit(20.0, dt_s=0.01)
        self.assertAlmostEqual(out, 1.0, places=3)
        # After 20 steps at max rate, should reach magnitude limit
        for _ in range(20):
            out = self.lim.limit(20.0, dt_s=0.01)
        self.assertAlmostEqual(out, 10.0, places=3)
        print(f"  [PASS] Mag: reaches 10.0")
    
    def test_rate(self):
        """Should limit rate."""
        self.lim.reset()
        out1 = self.lim.limit(5.0, dt_s=0.01)
        out2 = self.lim.limit(50.0, dt_s=0.01)  # rate would be 4500/s
        self.assertLessEqual(abs(out2 - out1), 1.0 + 1e-6)
        print(f"  [PASS] Rate: {out1:.1f} -> {out2:.1f}")


class TestHybridController(unittest.TestCase):
    """Test hybrid controller."""
    
    def setUp(self):
        self.hc = HybridController()
    
    def test_position_mode(self):
        """Should control position."""
        self.hc.set_mode(ControlMode.POSITION)
        out = self.hc.update(1.0, 0.0, dt_s=0.01)
        self.assertNotEqual(out, 0.0)
        print(f"  [PASS] Pos: {out:.1f}")
    
    def test_force_mode(self):
        """Should control force."""
        self.hc.set_mode(ControlMode.FORCE)
        out = self.hc.update(10.0, 0.0, force_feedback=5.0, dt_s=0.01)
        self.assertNotEqual(out, 0.0)
        print(f"  [PASS] Force: {out:.1f}")
    
    def test_feedforward(self):
        """Should compute feedforward."""
        ff = self.hc.add_feedforward(1.0)
        self.assertGreater(ff, 0)
        print(f"  [PASS] FF: {ff:.2f}")


class TestActuatorControl(unittest.TestCase):
    """Test unified actuator control."""
    
    def setUp(self):
        self.ac = ActuatorControl()
    
    def test_register(self):
        """Should register actuator."""
        self.ac.register_actuator("joint1")
        self.assertIn("joint1", self.ac.controllers)
        print("  [PASS] Register")
    
    def test_update(self):
        """Should update actuator."""
        self.ac.register_actuator("joint1")
        self.ac.set_target("joint1", 1.0)
        out = self.ac.update("joint1", 0.0, dt_s=0.01)
        self.assertNotEqual(out, 0.0)
        print(f"  [PASS] Update: {out:.1f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.ac.register_actuator("j1")
        self.ac.register_actuator("j2")
        s = self.ac.control_summary()
        self.assertEqual(s["actuators"], 2)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
