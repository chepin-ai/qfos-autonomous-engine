"""
Unit tests for quantum variational algorithms module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_variational_algorithms import (Parameter, VariationalAnsatz,
                                            ExpectationValue,
                                            VQESolver,
                                            QAOASolver,
                                            GradientEstimator,
                                            QuantumVariationalAlgorithms)


class TestVariationalAnsatz(unittest.TestCase):
    """Test ansatz."""
    
    def setUp(self):
        self.ansatz = VariationalAnsatz(2, 2)
    
    def test_num_params(self):
        """Should count params."""
        n = self.ansatz.num_parameters()
        self.assertEqual(n, 4)
        print(f"  [PASS] Np: {n}")
    
    def test_set_get(self):
        """Should set and get."""
        self.ansatz.set_parameters([0.1, 0.2, 0.3, 0.4])
        p = self.ansatz.get_parameters()
        self.assertEqual(len(p), 4)
        print(f"  [PASS] P: {p}")


class TestExpectationValue(unittest.TestCase):
    """Test expectation."""
    
    def setUp(self):
        self.ev = ExpectationValue()
    
    def test_compute(self):
        """Should compute."""
        state = [complex(1.0 / math.sqrt(2)), complex(1.0 / math.sqrt(2))]
        obs = [[1.0, 0.0], [0.0, -1.0]]
        e = self.ev.compute(state, obs)
        self.assertIsNotNone(e)
        print(f"  [PASS] Exp: {e:.4f}")


class TestVQESolver(unittest.TestCase):
    """Test VQE."""
    
    def setUp(self):
        self.ansatz = VariationalAnsatz(2, 1)
        self.vqe = VQESolver(self.ansatz)
    
    def test_energy(self):
        """Should compute energy."""
        h = [[1.0, 0.0, 0.0, 0.0],
             [0.0, -1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, -1.0]]
        e = self.vqe.energy(h, [0.0])
        self.assertIsNotNone(e)
        print(f"  [PASS] E: {e:.4f}")


class TestQAOASolver(unittest.TestCase):
    """Test QAOA."""
    
    def setUp(self):
        self.qaoa = QAOASolver(4, 2)
    
    def test_cost(self):
        """Should compute cost."""
        edges = [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0)]
        c = self.qaoa.cost(edges)
        self.assertEqual(c, 3.0)
        print(f"  [PASS] C: {c}")


class TestQuantumVariationalAlgorithms(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qva = QuantumVariationalAlgorithms(2)
    
    def test_summary(self):
        """Should summarize."""
        s = self.qva.qva_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
