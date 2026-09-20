"""
Unit tests for quantum differential privacy module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_differential_privacy import (PrivacyBudget, QuantumNoiseGenerator,
                                          PrivacyAccountant,
                                          QuantumMechanismComposer,
                                          QuantumDifferentialPrivacy)


class TestQuantumNoiseGenerator(unittest.TestCase):
    """Test noise generator."""
    
    def setUp(self):
        self.qng = QuantumNoiseGenerator()
    
    def test_gaussian(self):
        """Should generate Gaussian noise."""
        n = self.qng.gaussian_noise(5, 1.0)
        self.assertEqual(len(n), 5)
        print(f"  [PASS] Gau: {n}")
    
    def test_laplace(self):
        """Should generate Laplace noise."""
        n = self.qng.laplace_noise(5, 1.0)
        self.assertEqual(len(n), 5)
        print(f"  [PASS] Lap: {n}")
    
    def test_coherent(self):
        """Should generate coherent noise."""
        n = self.qng.quantum_coherent_noise(5, 0.1)
        self.assertEqual(len(n), 5)
        print(f"  [PASS] Coh: {len(n)} complex")


class TestPrivacyAccountant(unittest.TestCase):
    """Test accountant."""
    
    def setUp(self):
        self.pa = PrivacyAccountant(PrivacyBudget(1.0, 1e-5))
    
    def test_compose(self):
        """Should compose."""
        eps = self.pa.compose_gaussian(1.0, 1.0, 10)
        self.assertGreater(eps, 0)
        print(f"  [PASS] Comp: {eps:.4f}")
    
    def test_remaining(self):
        """Should track remaining."""
        self.pa.compose_gaussian(10.0, 1.0, 1)
        eps, delta = self.pa.remaining_budget()
        self.assertGreater(eps, 0)
        print(f"  [PASS] Rem: eps={eps:.4f}")
    
    def test_exhausted(self):
        """Should detect exhaustion."""
        self.assertFalse(self.pa.is_exhausted())
        print("  [PASS] Exh")


class TestQuantumMechanismComposer(unittest.TestCase):
    """Test composer."""
    
    def setUp(self):
        self.qmc = QuantumMechanismComposer()
    
    def test_compose(self):
        """Should compose mechanisms."""
        eps, delta = self.qmc.compose([0.1, 0.1], [1e-5, 1e-5])
        self.assertGreater(eps, 0)
        print(f"  [PASS] Mech: eps={eps:.4f}")
    
    def test_adaptive(self):
        """Should allocate budget."""
        queries = [{"weight": 1.0}, {"weight": 2.0}]
        alloc = self.qmc.adaptive_budget(queries, 1.0, 1e-5)
        self.assertEqual(len(alloc), 2)
        self.assertEqual(alloc[1], 2.0 * alloc[0])
        print(f"  [PASS] Adap: {alloc}")


class TestQuantumDifferentialPrivacy(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qdp = QuantumDifferentialPrivacy(1.0, 1e-5)
    
    def test_add_noise(self):
        """Should add noise."""
        p = self.qdp.add_noise([1.0, 2.0, 3.0], "gaussian")
        self.assertEqual(len(p), 3)
        print(f"  [PASS] Noise: {p}")
    
    def test_laplace_noise(self):
        """Should add Laplace noise."""
        p = self.qdp.add_noise([1.0, 2.0], "laplace")
        self.assertEqual(len(p), 2)
        print(f"  [PASS] LapN: {p}")
    
    def test_remaining(self):
        """Should report remaining."""
        self.qdp.add_noise([1.0], "gaussian")
        eps, delta = self.qdp.remaining()
        self.assertGreaterEqual(eps, 0)
        print(f"  [PASS] Rem: {eps:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qdp.qdp_summary()
        self.assertIn("initial_epsilon", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
