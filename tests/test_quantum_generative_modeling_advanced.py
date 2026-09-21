"""
Unit tests for quantum generative modeling advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_generative_modeling_advanced import (QuantumStateVector,
                                                  QuantumBoltzmannMachine,
                                                  QuantumAutoencoder,
                                                  QuantumNormalizingFlow,
                                                  QuantumVariationalAutoencoder,
                                                  QuantumGenerativeModelingAdvanced)


class TestQuantumBoltzmannMachine(unittest.TestCase):
    """Test RBM."""
    
    def setUp(self):
        self.qrbm = QuantumBoltzmannMachine()
    
    def test_energy(self):
        """Should compute energy."""
        e = self.qrbm.energy([1, 0, 1, 0], [1, 0])
        self.assertEqual(e, 0.0)
        print(f"  [PASS] E: {e}")
    
    def test_sample(self):
        """Should sample hidden."""
        p = self.qrbm.sample_hidden([1, 0, 1, 0])
        self.assertEqual(len(p), 2)
        print(f"  [PASS] H: {p}")


class TestQuantumAutoencoder(unittest.TestCase):
    """Test AE."""
    
    def setUp(self):
        self.qae = QuantumAutoencoder()
    
    def test_encode(self):
        """Should encode."""
        e = self.qae.encode([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(len(e), 2)
        print(f"  [PASS] Enc: {e}")
    
    def test_decode(self):
        """Should decode."""
        d = self.qae.decode([1.0, 2.0])
        self.assertEqual(len(d), 4)
        print(f"  [PASS] Dec: {d}")
    
    def test_error(self):
        """Should compute error."""
        err = self.qae.reconstruction_error([1.0, 2.0, 3.0, 4.0],
                                            [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(err, 0.0)
        print(f"  [PASS] Err: {err}")


class TestQuantumNormalizingFlow(unittest.TestCase):
    """Test flow."""
    
    def setUp(self):
        self.qnf = QuantumNormalizingFlow()
    
    def test_affine(self):
        """Should transform."""
        t = self.qnf.affine_transform([1.0, 2.0], 2.0, 1.0)
        self.assertEqual(t, [3.0, 5.0])
        print(f"  [PASS] T: {t}")
    
    def test_jacobian(self):
        """Should compute log det."""
        j = self.qnf.log_det_jacobian(2.0)
        self.assertGreater(j, 0)
        print(f"  [PASS] LogDet: {j:.4f}")


class TestQuantumVariationalAutoencoder(unittest.TestCase):
    """Test VAE."""
    
    def setUp(self):
        self.qvae = QuantumVariationalAutoencoder()
    
    def test_encode(self):
        """Should encode mean/std."""
        m, s = self.qvae.encode_mean_std([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(len(m), 2)
        self.assertEqual(len(s), 2)
        print(f"  [PASS] Mu: {m}, Sig: {s}")
    
    def test_kl(self):
        """Should compute KL."""
        kl = self.qvae.kl_divergence([0.0, 0.0], [1.0, 1.0])
        self.assertAlmostEqual(kl, 0.0, delta=1e-9)
        print(f"  [PASS] KL: {kl:.4f}")


class TestQuantumGenerativeModelingAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgma = QuantumGenerativeModelingAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qgma.generative_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
