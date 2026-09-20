"""
Unit tests for quantum natural gradient module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_natural_gradient import (QuantumFisherInformation,
                                      NaturalGradientDescent,
                                      VariationalQuantumOptimizer,
                                      QuantumNaturalGradient)


class TestQuantumFisherInformation(unittest.TestCase):
    """Test QFIM."""
    
    def setUp(self):
        self.qfi = QuantumFisherInformation(3)
    
    def test_compute(self):
        """Should compute from states."""
        states = [
            [complex(1.0, 0.0), complex(0.0, 0.0)],
            [complex(0.0, 0.0), complex(1.0, 0.0)],
            [complex(0.707, 0.0), complex(0.707, 0.0)]
        ]
        F = self.qfi.compute_from_states(states)
        self.assertEqual(len(F), 3)
        self.assertEqual(len(F[0]), 3)
        print("  [PASS] Compute")
    
    def test_regularize(self):
        """Should regularize."""
        self.qfi.F[0][0] = 1.0
        self.qfi.regularize(0.01)
        self.assertAlmostEqual(self.qfi.F[0][0], 1.01)
        print("  [PASS] Reg")


class TestNaturalGradientDescent(unittest.TestCase):
    """Test NGD."""
    
    def setUp(self):
        self.ngd = NaturalGradientDescent()
    
    def test_solve(self):
        """Should solve linear."""
        A = [[2.0, 0.0], [0.0, 2.0]]
        b = [4.0, 6.0]
        x = self.ngd.solve_linear(A, b)
        self.assertAlmostEqual(x[0], 2.0, places=3)
        self.assertAlmostEqual(x[1], 3.0, places=3)
        print(f"  [PASS] Solve: {x}")
    
    def test_step(self):
        """Should step."""
        params = [1.0, 1.0]
        grad = [0.1, 0.1]
        fisher = [[1.0, 0.0], [0.0, 1.0]]
        new_p = self.ngd.step(params, grad, fisher)
        self.assertEqual(len(new_p), 2)
        print(f"  [PASS] Step: {new_p}")


class TestVariationalQuantumOptimizer(unittest.TestCase):
    """Test VQO."""
    
    def setUp(self):
        self.vqo = VariationalQuantumOptimizer(2, 0.1)
    
    def test_state(self):
        """Should compute state."""
        state = self.vqo.rotation_state([0.5, 0.5])
        self.assertGreater(len(state), 0)
        norm = sum(abs(z)**2 for z in state)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] State: norm={norm:.4f}")
    
    def test_gradient(self):
        """Should compute gradient."""
        def loss_fn(p): return sum(x**2 for x in p)
        grad = self.vqo.compute_gradient(loss_fn)
        self.assertEqual(len(grad), 2)
        print(f"  [PASS] Grad: {grad}")
    
    def test_optimize(self):
        """Should optimize."""
        def loss_fn(p): return sum(x**2 for x in p)
        params = self.vqo.optimize(loss_fn, 10)
        self.assertEqual(len(params), 2)
        self.assertEqual(len(self.vqo.loss_history), 10)
        print(f"  [PASS] Opt: loss={self.vqo.loss_history[-1]:.4f}")


class TestQuantumNaturalGradient(unittest.TestCase):
    """Test unified QNG."""
    
    def setUp(self):
        self.qng = QuantumNaturalGradient()
    
    def test_build(self):
        """Should build."""
        self.qng.build(2, 0.1)
        self.assertIsNotNone(self.qng.optimizer)
        print("  [PASS] Build")
    
    def test_optimize(self):
        """Should optimize."""
        self.qng.build(2, 0.1)
        def loss_fn(p): return sum(x**2 for x in p)
        r = self.qng.optimize(loss_fn, 10)
        self.assertIn("final_loss", r)
        print(f"  [PASS] Opt: {r['final_loss']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        self.qng.build(2, 0.1)
        def loss_fn(p): return sum(x**2 for x in p)
        self.qng.optimize(loss_fn, 5)
        s = self.qng.qng_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
