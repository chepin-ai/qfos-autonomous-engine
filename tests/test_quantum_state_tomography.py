"""
Unit tests for quantum state tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_state_tomography import (DensityMatrix, StateTomography,
                                      StateFidelity, QuantumStateTomography)


class TestDensityMatrix(unittest.TestCase):
    """Test density matrix."""
    
    def setUp(self):
        self.rho = DensityMatrix(2)
    
    def test_trace(self):
        """Should have trace 1."""
        tr = self.rho.trace()
        self.assertAlmostEqual(tr.real, 1.0, places=6)
        print(f"  [PASS] Tr: {tr}")
    
    def test_purity(self):
        """Should compute purity."""
        p = self.rho.purity()
        self.assertGreater(p, 0)
        print(f"  [PASS] Purity: {p:.4f}")
    
    def test_pure_state(self):
        """Should set pure state."""
        state = [complex(1.0, 0.0), complex(0.0, 0.0)]
        self.rho.set_pure_state(state)
        p = self.rho.purity()
        self.assertAlmostEqual(p, 1.0, places=5)
        print(f"  [PASS] Pure: {p:.4f}")
    
    def test_physical(self):
        """Should be physical."""
        self.assertTrue(self.rho.is_physical())
        print("  [PASS] Phys")
    
    def test_expectation(self):
        """Should compute expectation."""
        Z = [[complex(1.0, 0.0), complex(0.0, 0.0)],
             [complex(0.0, 0.0), complex(-1.0, 0.0)]]
        e = self.rho.expectation(Z)
        self.assertAlmostEqual(e, 0.0, places=5)
        print(f"  [PASS] Exp: {e:.4f}")


class TestStateTomography(unittest.TestCase):
    """Test state tomography."""
    
    def setUp(self):
        self.tomo = StateTomography(1)
    
    def test_add_measurement(self):
        """Should add measurement."""
        self.tomo.add_measurement("Z", 0.5, 1000)
        self.assertEqual(len(self.tomo.measurements), 1)
        print("  [PASS] Add")
    
    def test_reconstruct(self):
        """Should reconstruct state."""
        self.tomo.add_measurement("Z", 0.5, 1000)
        rho = self.tomo.reconstruct()
        self.assertIsNotNone(rho)
        self.assertTrue(rho.is_physical())
        print("  [PASS] Rec")
    
    def test_tensor(self):
        """Should compute tensor product."""
        I = self.tomo.identity()
        X = self.tomo.pauli_x()
        T = self.tomo.tensor_product(I, X)
        self.assertEqual(len(T), 4)
        print("  [PASS] Tensor")


class TestStateFidelity(unittest.TestCase):
    """Test fidelity."""
    
    def setUp(self):
        self.fid = StateFidelity()
        self.rho1 = DensityMatrix(2)
        self.rho2 = DensityMatrix(2)
    
    def test_same_state(self):
        """Fidelity of same state should be ~1."""
        f = self.fid.fidelity(self.rho1, self.rho2)
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] Same: {f:.4f}")
    
    def test_trace_dist(self):
        """Should compute trace distance."""
        t = self.fid.trace_distance(self.rho1, self.rho2)
        self.assertEqual(t, 0.0)
        print(f"  [PASS] TrDist: {t}")


class TestQuantumStateTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qst = QuantumStateTomography()
    
    def test_setup(self):
        """Should setup."""
        self.qst.setup(1)
        self.assertIsNotNone(self.qst.tomography)
        print("  [PASS] Setup")
    
    def test_measure_reconstruct(self):
        """Should measure and reconstruct."""
        self.qst.setup(1)
        self.qst.measure("Z", 0.5, 1000)
        self.qst.measure("X", 0.3, 1000)
        rho = self.qst.reconstruct()
        self.assertIsNotNone(rho)
        print("  [PASS] MR")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        self.qst.setup(1)
        self.qst.measure("Z", 1.0, 1000)
        self.qst.reconstruct()
        target = DensityMatrix(2)
        f = self.qst.fidelity_with(target)
        self.assertGreaterEqual(f, 0.0)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        self.qst.setup(1)
        self.qst.measure("Z", 0.5, 1000)
        self.qst.reconstruct()
        s = self.qst.tomography_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
