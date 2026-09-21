"""
Unit tests for quantum state tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_state_tomography import (TomographyResult, PauliTomography,
                                      FidelityEstimator,
                                      MaximumLikelihood,
                                      StateValidator,
                                      QuantumStateTomography)


class TestPauliTomography(unittest.TestCase):
    """Test Pauli."""
    
    def setUp(self):
        self.pt = PauliTomography(1)
    
    def test_pauli_mats(self):
        """Should have matrices."""
        mats = self.pt.pauli_matrices()
        self.assertEqual(len(mats), 4)
        print("  [PASS] Pauli")
    
    def test_expectation(self):
        """Should compute expectation."""
        counts = {"0": 80, "1": 20}
        e = self.pt.expectation_from_counts(counts, "Z")
        self.assertAlmostEqual(e, 0.6, delta=0.01)
        print(f"  [PASS] Exp: {e:.2f}")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        exp = {"X": 0.0, "Y": 0.0, "Z": 1.0}
        rho = self.pt.reconstruct_density_matrix(exp)
        self.assertAlmostEqual(rho[0][0].real, 1.0, delta=0.1)
        print(f"  [PASS] Rec: rho00={rho[0][0].real:.2f}")


class TestFidelityEstimator(unittest.TestCase):
    """Test fidelity."""
    
    def setUp(self):
        self.fe = FidelityEstimator()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        rho = [[1.0, 0.0], [0.0, 0.0]]
        sigma = [[1.0, 0.0], [0.0, 0.0]]
        f = self.fe.state_fidelity(rho, sigma)
        self.assertAlmostEqual(f, 1.0, delta=0.01)
        print(f"  [PASS] Fid: {f:.2f}")
    
    def test_purity(self):
        """Should compute purity."""
        rho = [[1.0, 0.0], [0.0, 0.0]]
        p = self.fe.purity(rho)
        self.assertAlmostEqual(p, 1.0, delta=0.01)
        print(f"  [PASS] Pur: {p:.2f}")


class TestMaximumLikelihood(unittest.TestCase):
    """Test MLE."""
    
    def setUp(self):
        self.mle = MaximumLikelihood(1)
    
    def test_estimate(self):
        """Should estimate."""
        data = [{"basis": "Z", "counts": {"0": 90, "1": 10}}]
        rho = self.mle.estimate(data)
        self.assertGreater(rho[0][0].real, rho[1][1].real)
        print(f"  [PASS] MLE: diag={rho[0][0].real:.2f}, {rho[1][1].real:.2f}")


class TestStateValidator(unittest.TestCase):
    """Test validator."""
    
    def setUp(self):
        self.sv = StateValidator()
    
    def test_psd(self):
        """Should check PSD."""
        rho = [[1.0, 0.0], [0.0, 0.0]]
        self.assertTrue(self.sv.is_positive_semidefinite(rho))
        print("  [PASS] PSD")
    
    def test_trace(self):
        """Should check trace."""
        rho = [[0.5, 0.0], [0.0, 0.5]]
        self.assertTrue(self.sv.is_trace_one(rho))
        print("  [PASS] Trace")
    
    def test_hermitian(self):
        """Should check Hermitian."""
        rho = [[0.5, 0.1], [0.1, 0.5]]
        self.assertTrue(self.sv.is_hermitian(rho))
        print("  [PASS] Herm")


class TestQuantumStateTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qst = QuantumStateTomography(1)
    
    def test_reconstruct(self):
        """Should reconstruct."""
        data = [{"basis": "Z", "counts": {"0": 100, "1": 0}}]
        r = self.qst.reconstruct(data)
        self.assertIsInstance(r.density_matrix, list)
        print(f"  [PASS] Rec: fid={r.fidelity:.2f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qst.qst_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
