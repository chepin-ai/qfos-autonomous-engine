"""
Unit tests for quantum optimization module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_optimization import (OptimizationResult, QuantumGradientDescent,
                                  VariationalQuantumEigensolver,
                                  QAOA,
                                  QuantumConvexOptimizer,
                                  QuantumOptimization)


class TestQuantumGradientDescent(unittest.TestCase):
    """Test QGD."""
    
    def setUp(self):
        self.qgd = QuantumGradientDescent(0.1, 0.9)
    
    def test_optimize(self):
        """Should optimize."""
        def obj(x):
            return (x[0] - 2.0)**2 + (x[1] - 3.0)**2
        
        def grad(x):
            return [2.0*(x[0]-2.0), 2.0*(x[1]-3.0)]
        
        r = self.qgd.optimize(obj, [0.0, 0.0], grad, 50)
        self.assertLess(abs(r.optimal_value), 1.0)
        print(f"  [PASS] Opt: val={r.optimal_value:.4f}")


class TestVariationalQuantumEigensolver(unittest.TestCase):
    """Test VQE."""
    
    def setUp(self):
        self.vqe = VariationalQuantumEigensolver(2)
    
    def test_ansatz(self):
        """Should create ansatz."""
        a = self.vqe.ansatz([0.5, 0.5])
        self.assertEqual(len(a), 4)
        print("  [PASS] Ansatz")
    
    def test_expectation(self):
        """Should compute expectation."""
        a = self.vqe.ansatz([0.0, 0.0])
        h = [[1.0, 0.0], [0.0, 2.0]]
        e = self.vqe.expectation_value(a[:2], h)
        self.assertIsNotNone(e)
        print(f"  [PASS] Exp: {e:.4f}")
    
    def test_solve(self):
        """Should solve VQE."""
        h = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 2.0, 0.0, 0.0],
             [0.0, 0.0, 3.0, 0.0],
             [0.0, 0.0, 0.0, 4.0]]
        r = self.vqe.solve(h, [0.5, 0.5], 10)
        self.assertIn("optimal_value", vars(r))
        print(f"  [PASS] VQE: {r.optimal_value:.4f}")


class TestQAOA(unittest.TestCase):
    """Test QAOA."""
    
    def setUp(self):
        self.qaoa = QAOA(4, 2)
    
    def test_cost(self):
        """Should compute cost."""
        bits = [1, -1, 1, -1]
        edges = [(0, 1), (1, 2), (2, 3)]
        c = self.qaoa.cost_hamiltonian(bits, edges)
        self.assertGreaterEqual(c, 0)
        print(f"  [PASS] Cost: {c}")
    
    def test_optimize(self):
        """Should optimize."""
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        r = self.qaoa.optimize(edges, 20)
        self.assertIn("optimal_value", vars(r))
        print(f"  [PASS] QAOA: {r.optimal_value:.4f}")


class TestQuantumConvexOptimizer(unittest.TestCase):
    """Test convex."""
    
    def setUp(self):
        self.qco = QuantumConvexOptimizer(2)
    
    def test_quadratic(self):
        """Should evaluate quadratic."""
        x = [1.0, 2.0]
        Q = [[2.0, 0.0], [0.0, 2.0]]
        c = [0.0, 0.0]
        v = self.qco.quadratic_objective(x, Q, c)
        self.assertEqual(v, 10.0)
        print(f"  [PASS] Quad: {v}")
    
    def test_gradient(self):
        """Should compute gradient."""
        x = [1.0, 2.0]
        Q = [[2.0, 0.0], [0.0, 2.0]]
        c = [0.0, 0.0]
        g = self.qco.gradient_quadratic(x, Q, c)
        self.assertEqual(len(g), 2)
        print(f"  [PASS] Grad: {g}")


class TestQuantumOptimization(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qo = QuantumOptimization(4)
    
    def test_vqe(self):
        """Should run VQE."""
        h = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 2.0, 0.0, 0.0],
             [0.0, 0.0, 3.0, 0.0],
             [0.0, 0.0, 0.0, 4.0]]
        r = self.qo.minimize_vqe(h, [0.5, 0.5])
        self.assertIn("optimal_value", vars(r))
        print(f"  [PASS] VQE: {r.optimal_value:.4f}")
    
    def test_maxcut(self):
        """Should solve Max-Cut."""
        edges = [(0, 1), (1, 2)]
        r = self.qo.maxcut(edges, 1)
        self.assertIn("optimal_value", vars(r))
        print(f"  [PASS] MaxCut: {r.optimal_value:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qo.qopt_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
