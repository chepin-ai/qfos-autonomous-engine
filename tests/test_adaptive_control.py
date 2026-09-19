"""
Unit tests for adaptive control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from adaptive_control import ReferenceModel, MRACController, GainScheduler, AdaptiveController


class TestReferenceModel(unittest.TestCase):
    """Test reference model."""
    
    def setUp(self):
        self.ref = ReferenceModel(natural_frequency=2.0, damping_ratio=0.7)
    
    def test_response(self):
        """Should compute response."""
        out, state = self.ref.response(1.0, {"y": 0.0, "yd": 0.0, "dt": 0.01})
        self.assertNotEqual(out, 0.0)
        print(f"  [PASS] Response: {out:.4f}")
    
    def test_step_tracking(self):
        """Should track step input."""
        state = {"y": 0.0, "yd": 0.0, "dt": 0.01}
        for _ in range(500):
            out, state = self.ref.response(1.0, state)
        self.assertAlmostEqual(out, 1.0, delta=0.1)
        print(f"  [PASS] Step: final={out:.4f}")


class TestMRACController(unittest.TestCase):
    """Test MRAC controller."""
    
    def setUp(self):
        ref = ReferenceModel(natural_frequency=1.0, damping_ratio=0.7)
        self.ctrl = MRACController(reference=ref)
    
    def test_control(self):
        """Should compute control."""
        u, info = self.ctrl.control(setpoint=1.0, measurement=0.0, dt=0.01)
        self.assertIsInstance(u, float)
        print(f"  [PASS] Control: u={u:.4f}, err={info['error']:.4f}")
    
    def test_adaptation(self):
        """Should adapt gains."""
        Kp_before = self.ctrl.gains.Kp
        for i in range(100):
            u, info = self.ctrl.control(setpoint=1.0, measurement=0.5, dt=0.01)
        Kp_after = self.ctrl.gains.Kp
        self.assertNotEqual(Kp_before, Kp_after)
        print(f"  [PASS] Adaptation: Kp {Kp_before:.3f} -> {Kp_after:.3f}")
    
    def test_reset(self):
        """Should reset state."""
        self.ctrl.control(1.0, 0.0)
        self.ctrl.reset()
        self.assertEqual(self.ctrl.error_integral, 0.0)
        print("  [PASS] Reset: integral=0")


class TestGainScheduler(unittest.TestCase):
    """Test gain scheduler."""
    
    def setUp(self):
        self.sched = GainScheduler()
        self.sched.add_schedule_point("altitude", (0.0, 10000.0),
                                     {"Kp": 2.0, "Ki": 0.2, "Kd": 1.0})
        self.sched.add_schedule_point("altitude", (10000.0, 50000.0),
                                     {"Kp": 1.0, "Ki": 0.1, "Kd": 0.5})
    
    def test_get_gains(self):
        """Should get gains for conditions."""
        gains = self.sched.get_gains({"altitude": 5000.0})
        self.assertEqual(gains["Kp"], 2.0)
        print(f"  [PASS] Gains: Kp={gains['Kp']}")
    
    def test_get_gains_default(self):
        """Should return default if no match."""
        gains = self.sched.get_gains({"altitude": 100000.0})
        self.assertEqual(gains["Kp"], 1.0)
        print("  [PASS] Default: Kp=1.0")
    
    def test_interpolate(self):
        """Should interpolate gains."""
        gains = self.sched.interpolate_gains({"altitude": 50000.0})
        self.assertGreater(gains["Kp"], 0.0)
        print(f"  [PASS] Interpolate: Kp={gains['Kp']:.2f}")


class TestAdaptiveController(unittest.TestCase):
    """Test unified adaptive controller."""
    
    def setUp(self):
        self.ctrl = AdaptiveController()
    
    def test_control_mrac(self):
        """Should control in MRAC mode."""
        u, info = self.ctrl.control(1.0, 0.0)
        self.assertIsInstance(u, float)
        print(f"  [PASS] MRAC: u={u:.4f}")
    
    def test_control_scheduled(self):
        """Should control in scheduled mode."""
        self.ctrl.set_mode("scheduled")
        self.ctrl.scheduler.add_schedule_point("speed", (0.0, 10.0),
                                              {"Kp": 3.0})
        u, info = self.ctrl.control(1.0, 0.0, {"speed": 5.0})
        self.assertIsInstance(u, float)
        print(f"  [PASS] Scheduled: u={u:.4f}")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.ctrl.controller_summary()
        self.assertEqual(summary["mode"], "mrac")
        print(f"  [PASS] Summary: mode={summary['mode']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
