"""
Unit tests for quantum control advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_control_advanced import (ControlPulse, PulseShaping,
                                      OptimalControl,
                                      DynamicalDecoupling,
                                      CRABControl,
                                      QuantumControlAdvanced)


class TestPulseShaping(unittest.TestCase):
    """Test shaping."""
    
    def setUp(self):
        self.ps = PulseShaping()
    
    def test_gaussian(self):
        """Should compute Gaussian."""
        g = self.ps.gaussian_pulse(10.0, 10.0, 2.0)
        self.assertEqual(g, 1.0)
        print(f"  [PASS] Gauss: {g:.4f}")
    
    def test_drag(self):
        """Should compute DRAG."""
        I, Q = self.ps.drag_pulse(10.0, 10.0, 2.0)
        self.assertEqual(I, 1.0)
        print(f"  [PASS] DRAG: ({I:.2f}, {Q:.4f})")
    
    def test_blackman(self):
        """Should compute Blackman."""
        b = self.ps.blackman_pulse(5.0, 10.0)
        self.assertGreater(b, 0)
        print(f"  [PASS] Black: {b:.4f}")


class TestOptimalControl(unittest.TestCase):
    """Test optimal."""
    
    def setUp(self):
        self.oc = OptimalControl()
    
    def test_gradient(self):
        """Should compute gradient."""
        g = self.oc.fidelity_gradient([0.5, 0.3], [[1, 0], [0, 1]])
        self.assertEqual(len(g), 2)
        print(f"  [PASS] Grad: {g}")
    
    def test_update(self):
        """Should update."""
        u = self.oc.update_control([0.5, 0.3], [0.1, 0.2])
        self.assertEqual(len(u), 2)
        print(f"  [PASS] Upd: {u}")


class TestDynamicalDecoupling(unittest.TestCase):
    """Test decoupling."""
    
    def setUp(self):
        self.dd = DynamicalDecoupling()
    
    def test_echo(self):
        """Should compute coherence."""
        c = self.dd.spin_echo(50.0, 100.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] Echo: {c:.4f}")
    
    def test_cpmg(self):
        """Should compute CPMG."""
        c = self.dd.cpmg_sequence(4, 200.0, 100.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] CPMG: {c:.4f}")


class TestCRABControl(unittest.TestCase):
    """Test CRAB."""
    
    def setUp(self):
        self.cc = CRABControl()
    
    def test_basis(self):
        """Should compute basis."""
        b = self.cc.basis_function(0, 5.0, 10.0)
        self.assertEqual(b, 1.0)
        print(f"  [PASS] Basis: {b:.4f}")
    
    def test_pulse(self):
        """Should reconstruct pulse."""
        p = self.cc.pulse_from_coefficients([1.0, 0.5], 5.0, 10.0)
        self.assertNotEqual(p, 0.0)
        print(f"  [PASS] Pulse: {p:.4f}")


class TestQuantumControlAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qca = QuantumControlAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qca.control_summary()
        self.assertIn("techniques", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
