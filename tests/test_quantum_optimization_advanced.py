"""
Unit tests for quantum optimization advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_optimization_advanced import (QAOAParams, QAOA,
                                           QuantumAlternatingOperator,
                                           VQEExtensions,
                                           QuantumOptimizationAdvanced)


class TestQAOA(unittest.TestCase):
    """Test QAOA."""
    
    def setUp(self):
        self.qaoa = QAOA(4, 2)
    
    def test_init(self):
        """Should init params."""
        p = self.qaoa.initialize()
        self.assertEqual(len(p.gamma), 2)
        self.assertEqual(len(p.beta), 2)
        print(f"  [PASS] Params: {len(p.gamma)}")
    
    def test_expectation(self):
        """Should compute expectation."""
        p = QAOAParams([0.5, 0.5], [0.3, 0.3], 2)
        e = self.qaoa.cost_hamiltonian_expectation(p, [(0, 1), (1, 2)], [1.0, -1.0])
        self.assertIsInstance(e, float)
        print(f"  [PASS] Exp: {e:.4f}")
    
    def test_ratio(self):
        """Should compute ratio."""
        r = self.qaoa.approximation_ratio(-0.8, -1.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] Ratio: {r:.2f}")


class TestQuantumAlternatingOperator(unittest.TestCase):
    """Test alternating."""
    
    def setUp(self):
        self.qao = QuantumAlternatingOperator(4)
    
    def test_mixer(self):
        """Should compute mixer."""
        m = self.qao.mixer_hamiltonian(2)
        self.assertIsInstance(m, float)
        print(f"  [PASS] Mix: {m:.4f}")
    
    def test_apply(self):
        """Should apply mixer."""
        s = self.qao.apply_mixer([1.0, 0.0, 0.5], 0.5)
        self.assertEqual(len(s), 3)
        print(f"  [PASS] Apply: {s}")


class TestVQEExtensions(unittest.TestCase):
    """Test VQE."""
    
    def setUp(self):
        self.vqe = VQEExtensions()
    
    def test_schedule(self):
        """Should compute schedule."""
        s = self.vqe.adiabatic_schedule(0.5, 1.0)
        self.assertAlmostEqual(s, 0.25, delta=0.01)
        print(f"  [PASS] Sched: {s:.2f}")
    
    def test_gradient(self):
        """Should compute gradient."""
        grad = self.vqe.energy_gradient([1.0, 2.0], lambda p: sum(p), 1e-3)
        self.assertEqual(len(grad), 2)
        self.assertAlmostEqual(grad[0], 1.0, delta=0.01)
        print(f"  [PASS] Grad: {grad}")


class TestQuantumOptimizationAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qoa = QuantumOptimizationAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qoa.optimization_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
