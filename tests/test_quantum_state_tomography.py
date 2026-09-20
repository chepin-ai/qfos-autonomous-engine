"""
Unit tests for quantum state tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_state_tomography import (MeasurementOutcome, LinearInversionTomography,
                                      MaximumLikelihoodEstimator,
                                      StateValidator,
                                      ProcessTomography,
                                      QuantumStateTomography)


class TestLinearInversionTomography(unittest.TestCase):
    """Test linear inversion."""
    
    def setUp(self):
        self.li = LinearInversionTomography(1)
    
    def test_reconstruct(self):
        """Should reconstruct."""
        counts = {
            "X": {0: 500, 1: 500},
            "Y": {0: 500, 1: 500},
            "Z": {0: 1000, 1: 0}
        }
        rho = self.li.density_matrix_from_counts(counts)
        self.assertEqual(len(rho), 2)
        print(f"  [PASS] Recon: {rho}")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        rho = [[1.0, 0.0], [0.0, 0.0]]
        f = self.li.fidelity(rho, rho)
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] Fid: {f:.4f}")


class TestMaximumLikelihoodEstimator(unittest.TestCase):
    """Test MLE."""
    
    def setUp(self):
        self.mle = MaximumLikelihoodEstimator(1)
    
    def test_likelihood(self):
        """Should compute likelihood."""
        rho = [[0.5, 0.0], [0.0, 0.5]]
        counts = {"Z": {0: 500, 1: 500}}
        l = self.mle.likelihood(rho, counts)
        self.assertIsInstance(l, float)
        print(f"  [PASS] Like: {l:.2f}")
    
    def test_estimate(self):
        """Should estimate."""
        counts = {"Z": {0: 1000, 1: 0}}
        rho = self.mle.estimate(counts)
        self.assertEqual(len(rho), 2)
        print("  [PASS] Est")


class TestStateValidator(unittest.TestCase):
    """Test validator."""
    
    def setUp(self):
        self.sv = StateValidator()
    
    def test_hermitian(self):
        """Should check Hermitian."""
        rho = [[0.5, 0.0], [0.0, 0.5]]
        h = self.sv.is_hermitian(rho)
        self.assertTrue(h)
        print("  [PASS] Herm")
    
    def test_trace(self):
        """Should compute trace."""
        rho = [[0.5, 0.0], [0.0, 0.5]]
        t = self.sv.trace(rho)
        self.assertAlmostEqual(t, 1.0, places=5)
        print(f"  [PASS] Tr: {t:.4f}")
    
    def test_psd(self):
        """Should check PSD."""
        rho = [[0.5, 0.0], [0.0, 0.5]]
        p = self.sv.is_positive_semidefinite(rho)
        self.assertTrue(p)
        print("  [PASS] PSD")
    
    def test_purity(self):
        """Should compute purity."""
        rho = [[0.5, 0.0], [0.0, 0.5]]
        p = self.sv.purity(rho)
        self.assertAlmostEqual(p, 0.5, places=5)
        print(f"  [PASS] Pur: {p:.4f}")


class TestProcessTomography(unittest.TestCase):
    """Test process."""
    
    def setUp(self):
        self.pt = ProcessTomography(1)
    
    def test_chi(self):
        """Should estimate chi."""
        chi = self.pt.chi_matrix([], [])
        self.assertGreater(len(chi), 0)
        print("  [PASS] Chi")
    
    def test_fidelity(self):
        """Should compute process fidelity."""
        chi = [[1.0, 0.0], [0.0, 0.0]]
        f = self.pt.process_fidelity(chi, chi)
        self.assertEqual(f, 1.0)
        print(f"  [PASS] PFid: {f}")


class TestQuantumStateTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qst = QuantumStateTomography(1)
    
    def test_reconstruct(self):
        """Should reconstruct."""
        counts = {"Z": {0: 1000, 1: 0}}
        rho = self.qst.reconstruct(counts, "linear")
        self.assertEqual(len(rho), 2)
        print("  [PASS] Rec")
    
    def test_validate(self):
        """Should validate."""
        rho = [[0.5, 0.0], [0.0, 0.5]]
        v = self.qst.validate(rho)
        self.assertIn("purity", v)
        print(f"  [PASS] Val: {v}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qst.qst_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
