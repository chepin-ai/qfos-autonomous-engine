"""
Unit tests for quantum adversarial ML module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_adversarial_ml import (AdversarialPerturbation, QuantumAdversarialExamples,
                                    RobustnessCertification,
                                    QuantumGANComponents,
                                    DefenseStrategies,
                                    QuantumAdversarialML)


class TestQuantumAdversarialExamples(unittest.TestCase):
    """Test adversarial."""
    
    def setUp(self):
        self.qae = QuantumAdversarialExamples()
    
    def test_fgsm(self):
        """Should compute perturbation."""
        p = self.qae.fast_gradient_sign([0.1, -0.2, 0.3], 0.5)
        self.assertEqual(len(p), 3)
        print(f"  [PASS] FGSM: {len(p)} dims")
    
    def test_distance_inf(self):
        """Should compute Linf."""
        d = self.qae.perturbation_distance([0.0, 0.0], [0.1, 0.2])
        self.assertAlmostEqual(d, 0.2, delta=1e-10)
        print(f"  [PASS] Dinf: {d:.2f}")
    
    def test_distance_l2(self):
        """Should compute L2."""
        d = self.qae.perturbation_distance([0.0, 0.0], [0.3, 0.4], "2")
        self.assertAlmostEqual(d, 0.5, delta=1e-10)
        print(f"  [PASS] DL2: {d:.2f}")


class TestRobustnessCertification(unittest.TestCase):
    """Test robustness."""
    
    def setUp(self):
        self.rc = RobustnessCertification()
    
    def test_lipschitz(self):
        """Should compute L."""
        l = self.rc.local_lipschitz_bound(0.1, 0.5)
        self.assertEqual(l, 5.0)
        print(f"  [PASS] L: {l:.1f}")
    
    def test_radius(self):
        """Should compute radius."""
        r = self.rc.certified_radius(0.5, 2.0)
        self.assertEqual(r, 0.25)
        print(f"  [PASS] R: {r:.2f}")


class TestQuantumGANComponents(unittest.TestCase):
    """Test GAN."""
    
    def setUp(self):
        self.gan = QuantumGANComponents()
    
    def test_gen(self):
        """Should compute generator loss."""
        l = self.gan.generator_loss(0.7)
        self.assertGreater(l, 0)
        print(f"  [PASS] Lgen: {l:.4f}")
    
    def test_disc(self):
        """Should compute discriminator loss."""
        l = self.gan.discriminator_loss(0.8, 0.3)
        self.assertGreater(l, 0)
        print(f"  [PASS] Ldisc: {l:.4f}")
    
    def test_wgen(self):
        """Should compute WGAN-G loss."""
        l = self.gan.wasserstein_generator_loss(0.5)
        self.assertEqual(l, -0.5)
        print(f"  [PASS] Wgen: {l:.2f}")
    
    def test_wdisc(self):
        """Should compute WGAN-D loss."""
        l = self.gan.wasserstein_discriminator_loss(0.8, 0.3)
        self.assertEqual(l, -0.5)
        print(f"  [PASS] Wdisc: {l:.2f}")


class TestDefenseStrategies(unittest.TestCase):
    """Test defense."""
    
    def setUp(self):
        self.ds = DefenseStrategies()
    
    def test_training(self):
        """Should compute training loss."""
        l = self.ds.adversarial_training_loss(1.0, 2.0, 0.5)
        self.assertEqual(l, 1.5)
        print(f"  [PASS] Lat: {l:.2f}")
    
    def test_randomization(self):
        """Should randomize."""
        r = self.ds.input_randomization([1.0, 1.0])
        self.assertEqual(len(r), 2)
        print(f"  [PASS] Rand: {r}")


class TestQuantumAdversarialML(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qaml = QuantumAdversarialML()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qaml.adversarial_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
