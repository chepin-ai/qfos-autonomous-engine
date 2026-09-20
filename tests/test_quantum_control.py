"""
Unit tests for quantum control module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_control import (ControlPulse, PulseShaper,
                             OptimalControl,
                             GateCalibrator,
                             FeedbackControl,
                             DynamicalDecoupling,
                             QuantumControl)


class TestPulseShaper(unittest.TestCase):
    """Test pulse shaper."""
    
    def setUp(self):
        self.ps = PulseShaper(1e-9)
    
    def test_gaussian(self):
        """Should generate Gaussian."""
        p = self.ps.gaussian_pulse(1.0, 1e-9, 5e-9, 10e-9)
        self.assertGreater(len(p), 0)
        print(f"  [PASS] Gauss: {len(p)} pts")
    
    def test_rectangular(self):
        """Should generate rectangular."""
        p = self.ps.rectangular_pulse(1.0, 0.0, 10e-9)
        self.assertGreater(len(p), 0)
        print(f"  [PASS] Rect: {len(p)} pts")
    
    def test_ramp(self):
        """Should generate ramp."""
        p = self.ps.ramp_pulse(0.0, 1.0, 10e-9)
        self.assertGreater(len(p), 0)
        print(f"  [PASS] Ramp: {len(p)} pts")


class TestOptimalControl(unittest.TestCase):
    """Test optimal control."""
    
    def setUp(self):
        self.oc = OptimalControl(1)
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.oc.fidelity([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_unitary_fidelity(self):
        """Should compute unitary fidelity."""
        u = [[1.0, 0.0], [0.0, 1.0]]
        f = self.oc.unitary_fidelity(u, u)
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] UFid: {f:.4f}")


class TestGateCalibrator(unittest.TestCase):
    """Test calibrator."""
    
    def setUp(self):
        self.gc = GateCalibrator()
    
    def test_add(self):
        """Should add calibration."""
        self.gc.add_calibration("X", math.pi, math.pi * 1.01)
        self.assertIn("X", self.gc.calibration_data)
        print("  [PASS] AddCal")
    
    def test_corrected(self):
        """Should correct angle."""
        self.gc.add_calibration("X", math.pi, math.pi * 1.01)
        a = self.gc.corrected_angle("X", math.pi)
        self.assertAlmostEqual(a, math.pi * 0.99, places=5)
        print(f"  [PASS] Corr: {a:.4f}")
    
    def test_budget(self):
        """Should compute budget."""
        self.gc.add_calibration("X", math.pi, math.pi * 1.01)
        b = self.gc.error_budget()
        self.assertIn("max_error_rad", b)
        print(f"  [PASS] Bud: {b}")


class TestFeedbackControl(unittest.TestCase):
    """Test feedback."""
    
    def setUp(self):
        self.fc = FeedbackControl(1.0, 0.1, 0.01)
    
    def test_pid(self):
        """Should update PID."""
        o = self.fc.pid_update(10.0, 8.0, 0.1)
        self.assertGreater(o, 0)
        print(f"  [PASS] PID: {o:.4f}")
    
    def test_reset(self):
        """Should reset."""
        self.fc.pid_update(10.0, 8.0, 0.1)
        self.fc.reset()
        self.assertEqual(self.fc.integral, 0.0)
        print("  [PASS] Rst")


class TestDynamicalDecoupling(unittest.TestCase):
    """Test decoupling."""
    
    def setUp(self):
        self.dd = DynamicalDecoupling()
    
    def test_hahn(self):
        """Should generate Hahn echo."""
        s = self.dd.hahn_echo(1e-6)
        self.assertEqual(len(s), 3)
        print(f"  [PASS] Hahn: {s}")
    
    def test_cp(self):
        """Should generate CP."""
        s = self.dd.cp_sequence(4, 1e-6)
        self.assertGreater(len(s), 0)
        print(f"  [PASS] CP: {len(s)} steps")
    
    def test_cpmg(self):
        """Should generate CPMG."""
        s = self.dd.cpmg_sequence(4, 1e-6)
        self.assertGreater(len(s), 0)
        print(f"  [PASS] CPMG: {len(s)} steps")


class TestQuantumControl(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumControl(1)
    
    def test_pulse(self):
        """Should generate pulse."""
        p = self.qc.generate_pulse_sequence("gaussian", 1.0, 10e-9)
        self.assertGreater(len(p), 0)
        print(f"  [PASS] Pul: {len(p)} pts")
    
    def test_calibrate(self):
        """Should calibrate."""
        self.qc.calibrate_gate("X", math.pi, math.pi * 1.01)
        self.assertIn("X", self.qc.calibrator.calibration_data)
        print("  [PASS] Cal")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qc.qctrl_summary()
        self.assertIn("pulse_types", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
