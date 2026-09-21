"""
Unit tests for quantum tomography advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_tomography_advanced import (MeasurementOutcome, StateTomography,
                                         ProcessTomography,
                                         MaximumLikelihood,
                                         CompressedSensingTomography,
                                         QuantumTomographyAdvanced)


class TestStateTomography(unittest.TestCase):
    """Test state."""
    
    def setUp(self):
        self.st = StateTomography()
    
    def test_density(self):
        """Should reconstruct density."""
        rho = self.st.density_matrix_elements({'X': 0.0, 'Y': 0.0, 'Z': 1.0})
        self.assertAlmostEqual(rho[0][0].real, 1.0, delta=1e-10)
        print(f"  [PASS] Rho00: {rho[0][0]}")
    
    def test_purity(self):
        """Should compute purity."""
        rho = [[1.0, 0.0], [0.0, 0.0]]
        p = self.st.purity(rho)
        self.assertEqual(p, 1.0)
        print(f"  [PASS] Pur: {p:.2f}")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        rho = [[1.0, 0.0], [0.0, 0.0]]
        psi = [1.0, 0.0]
        f = self.st.fidelity_with_pure(rho, psi)
        self.assertEqual(f, 1.0)
        print(f"  [PASS] F: {f:.2f}")


class TestProcessTomography(unittest.TestCase):
    """Test process."""
    
    def setUp(self):
        self.pt = ProcessTomography()
    
    def test_chi(self):
        """Should estimate chi."""
        c = self.pt.chi_matrix_element({}, 0, 0)
        self.assertEqual(c, 1.0)
        print(f"  [PASS] Chi: {c}")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        choi = [[1.0, 0.0], [0.0, 0.0]]
        f = self.pt.process_fidelity_from_choi(choi, choi)
        self.assertEqual(f, 0.5)
        print(f"  [PASS] Fp: {f:.2f}")


class TestMaximumLikelihood(unittest.TestCase):
    """Test MLE."""
    
    def setUp(self):
        self.mle = MaximumLikelihood()
    
    def test_likelihood(self):
        """Should compute likelihood."""
        l = self.mle.likelihood([50, 50], [0.5, 0.5])
        self.assertLess(l, 0)
        print(f"  [PASS] LL: {l:.2f}")
    
    def test_residual(self):
        """Should compute residual."""
        r = self.mle.least_squares_residual([0.5, 0.5], [0.4, 0.6])
        self.assertGreater(r, 0)
        print(f"  [PASS] Res: {r:.4f}")


class TestCompressedSensingTomography(unittest.TestCase):
    """Test CS."""
    
    def setUp(self):
        self.cs = CompressedSensingTomography()
    
    def test_complexity(self):
        """Should estimate complexity."""
        n = self.cs.sample_complexity(1, 4)
        self.assertGreater(n, 0)
        print(f"  [PASS] N: {n}")
    
    def test_quality(self):
        """Should compute quality."""
        rho = [[1.0, 0.0], [0.0, 0.0]]
        q = self.cs.reconstruction_quality(rho, rho)
        self.assertEqual(q, 1.0)
        print(f"  [PASS] Q: {q:.2f}")


class TestQuantumTomographyAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qta = QuantumTomographyAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qta.tomography_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
