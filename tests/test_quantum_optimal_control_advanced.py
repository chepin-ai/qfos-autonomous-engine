"""
Unit tests for quantum optimal control advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_optimal_control_advanced import (ControlPulse, GRAPEAlgorithm,
                                              CRABOptimization,
                                              KrotovMethod,
                                              PulseShaping,
                                              QuantumOptimalControlAdvanced)


class TestGRAPEAlgorithm(unittest.TestCase):
    """Test GRAPE."""
    
    def setUp(self):
        self.grape = GRAPEAlgorithm()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        U = [[1.0, 0.0], [0.0, 1.0]]
        f = self.grape.fidelity(U, U)
        self.assertAlmostEqual(f, 1.0, delta=1e-6)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_step(self):
        """Should update pulse."""
        p = ControlPulse([0.1] * 10, 0.01)
        g = [0.1] * 10
        u = self.grape.gradient_step(p, g)
        self.assertEqual(len(u.amplitudes), 10)
        print(f"  [PASS] Step: {u.amplitudes[0]:.4f}")
    
    def test_optimize(self):
        """Should optimize."""
        p = ControlPulse([0.0] * 10, 0.01)
        U = [[1.0, 0.0], [0.0, 1.0]]
        o = self.grape.optimize(p, U, 10)
        self.assertEqual(len(o.amplitudes), 10)
        print(f"  [PASS] Opt: {len(o.amplitudes)}")


class TestCRABOptimization(unittest.TestCase):
    """Test CRAB."""
    
    def setUp(self):
        self.crab = CRABOptimization()
    
    def test_basis(self):
        """Should compute basis."""
        b = self.crab.basis_pulse(0.25, 1.0, 1.0)
        self.assertAlmostEqual(b, 1.0, delta=1e-6)
        print(f"  [PASS] Basis: {b:.4f}")
    
    def test_expand(self):
        """Should expand pulse."""
        c = [1.0, 0.5]
        t = [0.0, 0.5, 1.0]
        p = self.crab.expand_pulse(c, t, 1.0)
        self.assertEqual(len(p), 3)
        print(f"  [PASS] Exp: {len(p)}")
    
    def test_optimize(self):
        """Should optimize coeffs."""
        c = self.crab.optimize_coefficients([0.0, 0.0], lambda x: sum(a**2 for a in x), 10)
        self.assertEqual(len(c), 2)
        print(f"  [PASS] Coeff: {c}")


class TestKrotovMethod(unittest.TestCase):
    """Test Krotov."""
    
    def setUp(self):
        self.krotov = KrotovMethod()
    
    def test_update(self):
        """Should update pulse."""
        p = [0.1, 0.2]
        f = [1.0, 1.0]
        b = [0.5, 0.5]
        u = self.krotov.update_rule(p, f, b)
        self.assertEqual(len(u), 2)
        print(f"  [PASS] Upd: {u}")
    
    def test_converge(self):
        """Should check convergence."""
        c = self.krotov.convergence_check(0.99, 0.9900001)
        self.assertTrue(c)
        print(f"  [PASS] Conv: {c}")


class TestPulseShaping(unittest.TestCase):
    """Test pulse."""
    
    def setUp(self):
        self.ps = PulseShaping()
    
    def test_gaussian(self):
        """Should compute Gaussian."""
        g = self.ps.gaussian_pulse(0.0)
        self.assertAlmostEqual(g, 1.0, delta=1e-6)
        print(f"  [PASS] Gau: {g:.4f}")
    
    def test_sinc(self):
        """Should compute sinc."""
        s = self.ps.sinc_pulse(0.0)
        self.assertEqual(s, 1.0)
        print(f"  [PASS] Sinc: {s:.4f}")
    
    def test_bandwidth(self):
        """Should compute bandwidth."""
        b = self.ps.pulse_bandwidth(1e-6)
        self.assertEqual(b, 1e6)
        print(f"  [PASS] BW: {b:.1e}")


class TestQuantumOptimalControlAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qoca = QuantumOptimalControlAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qoca.optimal_control_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
