"""
Unit tests for quantum control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_control import (ControlPulse, OptimalControl,
                             PulseShaper,
                             DynamicalDecoupling,
                             GateCalibration,
                             QuantumControl)


class TestOptimalControl(unittest.TestCase):
    """Test optimal control."""
    
    def setUp(self):
        self.oc = OptimalControl()
        self.oc.add_pulse(1.0, 0.0, 1.0, 1.0)
        self.oc.add_pulse(0.5, 0.0, 2.0, 1.0)
    
    def test_duration(self):
        """Should compute duration."""
        d = self.oc.total_duration()
        self.assertEqual(d, 3.0)
        print(f"  [PASS] Dur: {d}")
    
    def test_power(self):
        """Should compute power."""
        p = self.oc.average_power()
        self.assertGreater(p, 0)
        print(f"  [PASS] Pwr: {p:.4f}")
    
    def test_infidelity(self):
        """Should compute infidelity."""
        U = [[1.0, 0.0], [0.0, 1.0]]
        inf = self.oc.infidelity(U, U)
        self.assertEqual(inf, 0.0)
        print(f"  [PASS] Inf: {inf}")


class TestPulseShaper(unittest.TestCase):
    """Test pulse shaper."""
    
    def setUp(self):
        self.ps = PulseShaper()
    
    def test_gaussian(self):
        """Should shape Gaussian."""
        g = self.ps.gaussian_pulse(0.0, 1.0, 1.0, 0.0)
        self.assertEqual(g, 1.0)
        print(f"  [PASS] G: {g}")
    
    def test_drag(self):
        """Should shape DRAG."""
        i, q = self.ps.drag_pulse(0.0, 1.0, 1.0, 0.0)
        self.assertEqual(i, 1.0)
        print(f"  [PASS] DRAG: I={i:.4f}, Q={q:.4f}")
    
    def test_square(self):
        """Should shape square."""
        s = self.ps.square_pulse(0.5, 1.0, 0.0, 1.0)
        self.assertEqual(s, 1.0)
        print(f"  [PASS] Sq: {s}")


class TestDynamicalDecoupling(unittest.TestCase):
    """Test DD."""
    
    def setUp(self):
        self.dd = DynamicalDecoupling()
    
    def test_cp(self):
        """Should generate CP."""
        s = self.dd.carr_purcell(4)
        self.assertEqual(len(s), 4)
        print(f"  [PASS] CP: {s}")
    
    def test_cpmg(self):
        """Should generate CPMG."""
        s = self.dd.carr_purcell_meiboom_gill(4)
        self.assertEqual(len(s), 4)
        print(f"  [PASS] CPMG: {s}")
    
    def test_xy4(self):
        """Should generate XY4."""
        s = self.dd.xy4()
        self.assertEqual(len(s), 4)
        print(f"  [PASS] XY4: {s}")


class TestGateCalibration(unittest.TestCase):
    """Test calibration."""
    
    def setUp(self):
        self.gc = GateCalibration()
        self.gc.add_data("X", 0.99)
        self.gc.add_data("X", 0.98)
    
    def test_avg(self):
        """Should compute average."""
        a = self.gc.average_fidelity("X")
        self.assertAlmostEqual(a, 0.985)
        print(f"  [PASS] Avg: {a:.4f}")
    
    def test_best(self):
        """Should get best."""
        b = self.gc.best_fidelity("X")
        self.assertEqual(b, 0.99)
        print(f"  [PASS] Best: {b}")


class TestQuantumControl(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumControl()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qc.qc_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
