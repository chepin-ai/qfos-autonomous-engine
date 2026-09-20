"""
Unit tests for quantum Boltzmann machine module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_boltzmann_machine import (BoltzmannDistribution,
                                       RestrictedBoltzmannMachine,
                                       QuantumBoltzmannMachine,
                                       QBMInference,
                                       QuantumBoltzmannController)


class TestBoltzmannDistribution(unittest.TestCase):
    """Test Boltzmann distribution."""
    
    def setUp(self):
        self.bd = BoltzmannDistribution(temperature=1.0)
    
    def test_probability(self):
        """Should compute probability."""
        p = self.bd.probability(0.0)
        self.assertAlmostEqual(p, 1.0)
        print("  [PASS] Prob")
    
    def test_sample(self):
        """Should sample."""
        idx = self.bd.sample([0.0, 1.0, 2.0])
        self.assertIn(idx, [0, 1, 2])
        print(f"  [PASS] Sample: {idx}")


class TestRestrictedBoltzmannMachine(unittest.TestCase):
    """Test RBM."""
    
    def setUp(self):
        self.rbm = RestrictedBoltzmannMachine(num_visible=4, num_hidden=2)
    
    def test_hidden_probs(self):
        """Should compute hidden probs."""
        v = [1, 0, 1, 0]
        h = self.rbm.hidden_probabilities(v)
        self.assertEqual(len(h), 2)
        self.assertTrue(all(0 <= p <= 1 for p in h))
        print(f"  [PASS] H: {h}")
    
    def test_visible_probs(self):
        """Should compute visible probs."""
        h = [1, 0]
        v = self.rbm.visible_probabilities(h)
        self.assertEqual(len(v), 4)
        print(f"  [PASS] V: {v}")
    
    def test_cd(self):
        """Should train with CD."""
        old_b = self.rbm.b_visible[:]
        for _ in range(10):
            self.rbm.contrastive_divergence([1, 0, 1, 0], lr=1.0)
        changed = any(self.rbm.b_visible[i] != old_b[i] for i in range(4))
        self.assertTrue(changed)
        print("  [PASS] CD")


class TestQuantumBoltzmannMachine(unittest.TestCase):
    """Test QBM."""
    
    def setUp(self):
        self.qbm = QuantumBoltzmannMachine(num_visible=4, num_hidden=2)
    
    def test_quantum_energy(self):
        """Should compute energy."""
        E = self.qbm.quantum_energy([1, 0, 1, 0], [1, 0])
        self.assertIsInstance(E, float)
        print(f"  [PASS] E: {E:.4f}")
    
    def test_quantum_sample(self):
        """Should quantum sample."""
        h, E = self.qbm.quantum_sample([1, 0, 1, 0])
        self.assertEqual(len(h), 2)
        print(f"  [PASS] QS: h={h}, E={E:.4f}")
    
    def test_train(self):
        """Should train."""
        old_b = self.qbm.rbm.b_visible[:]
        for _ in range(10):
            self.qbm.train_quantum([1, 0, 1, 0], lr=1.0)
        changed = any(self.qbm.rbm.b_visible[i] != old_b[i] for i in range(4))
        self.assertTrue(changed)
        print("  [PASS] QTrain")


class TestQBMInference(unittest.TestCase):
    """Test QBM inference."""
    
    def setUp(self):
        self.qbm = QuantumBoltzmannMachine(4, 2)
        self.inf = QBMInference(self.qbm)
    
    def test_reconstruct(self):
        """Should reconstruct."""
        r = self.inf.reconstruct([1, None, 1, None])
        self.assertEqual(len(r), 4)
        self.assertEqual(r[0], 1)
        self.assertEqual(r[2], 1)
        print(f"  [PASS] Recon: {r}")
    
    def test_features(self):
        """Should extract features."""
        f = self.inf.feature_representation([1, 0, 1, 0])
        self.assertEqual(len(f), 2)
        print(f"  [PASS] Feat: {f}")
    
    def test_free_energy(self):
        """Should compute free energy."""
        fe = self.inf.free_energy([1, 0, 1, 0])
        self.assertIsInstance(fe, float)
        print(f"  [PASS] FE: {fe:.4f}")


class TestQuantumBoltzmannController(unittest.TestCase):
    """Test unified QBM controller."""
    
    def setUp(self):
        self.qbc = QuantumBoltzmannController()
    
    def test_build(self):
        """Should build."""
        self.qbc.build(4, 2)
        self.assertIsNotNone(self.qbc.qbm)
        print("  [PASS] Build")
    
    def test_train(self):
        """Should train."""
        self.qbc.build(4, 2)
        self.qbc.train([[1, 0, 1, 0], [0, 1, 0, 1]], epochs=2, lr=0.1)
        self.assertEqual(len(self.qbc.training_history), 2)
        print(f"  [PASS] Train: hist={self.qbc.training_history}")
    
    def test_predict(self):
        """Should predict."""
        self.qbc.build(4, 2)
        p = self.qbc.predict([1, None, 1, None])
        self.assertEqual(len(p), 4)
        print(f"  [PASS] Pred: {p}")
    
    def test_summary(self):
        """Should summarize."""
        self.qbc.build(4, 2)
        s = self.qbc.qbm_summary()
        self.assertEqual(s["visible"], 4)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
