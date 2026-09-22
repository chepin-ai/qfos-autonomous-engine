"""
Unit tests for quantum differential privacy advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_differential_privacy_advanced import (PrivacyBudget,
                                                   QuantumNoiseMechanisms,
                                                   QuantumPrivacyAccounting,
                                                   QuantumCompositionTheorems,
                                                   QuantumSensitivityAnalysis,
                                                   QuantumDifferentialPrivacyAdvanced)


class TestQuantumNoiseMechanisms(unittest.TestCase):
    """Test noise."""
    
    def setUp(self):
        self.qnm = QuantumNoiseMechanisms()
    
    def test_laplace(self):
        """Should generate noise."""
        n = self.qnm.laplace_noise(1.0, 1.0)
        self.assertIsInstance(n, float)
        print(f"  [PASS] Lap: {n:.4f}")
    
    def test_gaussian(self):
        """Should generate noise."""
        n = self.qnm.gaussian_noise(1.0, 1.0, 1e-5)
        self.assertIsInstance(n, float)
        print(f"  [PASS] Gau: {n:.4f}")
    
    def test_add(self):
        """Should add noise."""
        v = self.qnm.add_noise(10.0, 1.0, PrivacyBudget(1.0, 0.0))
        self.assertIsInstance(v, float)
        print(f"  [PASS] Val: {v:.4f}")


class TestQuantumPrivacyAccounting(unittest.TestCase):
    """Test accounting."""
    
    def setUp(self):
        self.qpa = QuantumPrivacyAccounting()
    
    def test_spend(self):
        """Should spend."""
        self.qpa.spend(0.1, 1e-6)
        self.assertEqual(len(self.qpa.spent), 1)
        print(f"  [PASS] Spend: {len(self.qpa.spent)}")
    
    def test_total(self):
        """Should compute total."""
        self.qpa.spend(0.1, 1e-6)
        self.qpa.spend(0.2, 1e-6)
        e = self.qpa.total_epsilon()
        self.assertAlmostEqual(e, 0.3, delta=1e-6)
        print(f"  [PASS] Eps: {e:.2f}")
    
    def test_remaining(self):
        """Should compute remaining."""
        self.qpa.spend(0.5, 1e-5)
        r = self.qpa.remaining_budget(1.0, 1e-4)
        self.assertGreaterEqual(r.epsilon, 0)
        print(f"  [PASS] Rem: eps={r.epsilon:.2f}")


class TestQuantumCompositionTheorems(unittest.TestCase):
    """Test composition."""
    
    def setUp(self):
        self.qct = QuantumCompositionTheorems()
    
    def test_basic(self):
        """Should compose basic."""
        b = self.qct.basic_composition(0.1, 1e-6, 10)
        self.assertEqual(b.epsilon, 1.0)
        print(f"  [PASS] Basic: eps={b.epsilon:.2f}")
    
    def test_advanced(self):
        """Should compose advanced."""
        b = self.qct.advanced_composition(0.1, 1e-6, 10)
        self.assertGreater(b.epsilon, 0)
        print(f"  [PASS] Adv: eps={b.epsilon:.4f}")


class TestQuantumSensitivityAnalysis(unittest.TestCase):
    """Test sensitivity."""
    
    def setUp(self):
        self.qsa = QuantumSensitivityAnalysis()
    
    def test_l1(self):
        """Should compute L1."""
        s = self.qsa.l1_sensitivity([[1.0, 2.0], [2.0, 3.0]])
        self.assertEqual(s, 2.0)
        print(f"  [PASS] L1: {s:.2f}")
    
    def test_l2(self):
        """Should compute L2."""
        s = self.qsa.l2_sensitivity([[0.0, 0.0], [3.0, 4.0]])
        self.assertEqual(s, 5.0)
        print(f"  [PASS] L2: {s:.2f}")


class TestQuantumDifferentialPrivacyAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qdpa = QuantumDifferentialPrivacyAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qdpa.dp_summary()
        self.assertIn("mechanisms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
