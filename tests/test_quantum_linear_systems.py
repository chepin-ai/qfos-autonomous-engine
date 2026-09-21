"""
Unit tests for quantum linear systems module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_linear_systems import (LinearSystemSolution,
                                    ClassicalLinearSolver,
                                    QuantumPhaseEstimationForHHL,
                                    QuantumMatrixInversion,
                                    QuantumLinearSystems)


class TestClassicalLinearSolver(unittest.TestCase):
    """Test classical solver."""
    
    def setUp(self):
        self.solver = ClassicalLinearSolver()
    
    def test_solve_2x2(self):
        """Should solve 2x2."""
        A = [[2.0, 1.0], [1.0, 3.0]]
        b = [5.0, 8.0]
        x = self.solver.solve_2x2(A, b)
        self.assertIsNotNone(x)
        self.assertEqual(len(x), 2)
        print(f"  [PASS] x: [{x[0]:.2f}, {x[1]:.2f}]")
    
    def test_residual(self):
        """Should compute residual."""
        A = [[2.0, 0.0], [0.0, 2.0]]
        b = [4.0, 6.0]
        x = [2.0, 3.0]
        r = self.solver.residual(A, b, x)
        self.assertAlmostEqual(r, 0.0, delta=1e-6)
        print(f"  [PASS] Res: {r:.6f}")


class TestQuantumPhaseEstimationForHHL(unittest.TestCase):
    """Test QPE."""
    
    def setUp(self):
        self.pe = QuantumPhaseEstimationForHHL(4)
    
    def test_estimate_phase(self):
        """Should estimate phase."""
        p = self.pe.estimate_phase(math.pi)
        self.assertAlmostEqual(p, 0.5, delta=0.01)
        print(f"  [PASS] Phase: {p:.3f}")
    
    def test_binary(self):
        """Should convert to binary."""
        b = self.pe.binary_representation(0.5, 2)
        self.assertEqual(len(b), 2)
        print(f"  [PASS] Bin: {b}")


class TestQuantumMatrixInversion(unittest.TestCase):
    """Test matrix inversion."""
    
    def setUp(self):
        self.qmi = QuantumMatrixInversion()
    
    def test_condition_number(self):
        """Should compute condition number."""
        k = self.qmi.condition_number([1.0, 10.0])
        self.assertEqual(k, 10.0)
        print(f"  [PASS] Kappa: {k:.1f}")
    
    def test_inverse_eigenvalue(self):
        """Should invert eigenvalue."""
        inv = self.qmi.inverse_eigenvalue(2.0, 10.0)
        self.assertGreater(inv, 0)
        print(f"  [PASS] Inv: {inv:.4f}")
    
    def test_hhl_solution(self):
        """Should solve via HHL."""
        A = [[2.0, 0.0], [0.0, 2.0]]
        b = [4.0, 6.0]
        sol = self.qmi.hhl_solution_2x2(A, b, [2.0, 2.0])
        self.assertIsNotNone(sol)
        print(f"  [PASS] HHL: x={sol.x}, res={sol.residual:.4f}")


class TestQuantumLinearSystems(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qls = QuantumLinearSystems()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qls.hhl_summary()
        self.assertIn("algorithm", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
