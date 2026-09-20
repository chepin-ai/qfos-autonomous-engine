"""
Unit tests for quantum generative adversarial network module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_generative_adversarial_network import (QuantumGenerator,
                                                    QuantumDiscriminator,
                                                    AdversarialTrainer,
                                                    QuantumGenerativeAdversarialNetwork)


class TestQuantumGenerator(unittest.TestCase):
    """Test quantum generator."""
    
    def setUp(self):
        self.gen = QuantumGenerator(noise_dim=4, output_dim=2)
    
    def test_generate(self):
        """Should generate sample."""
        s = self.gen.generate()
        self.assertEqual(len(s), 2)
        print(f"  [PASS] Gen: {s}")
    
    def test_generate_batch(self):
        """Should generate batch."""
        b = self.gen.generate_batch(3)
        self.assertEqual(len(b), 3)
        print("  [PASS] Batch")
    
    def test_with_noise(self):
        """Should use provided noise."""
        s = self.gen.generate([1.0, 0.0, -1.0, 0.5])
        self.assertEqual(len(s), 2)
        print(f"  [PASS] Noise: {s}")


class TestQuantumDiscriminator(unittest.TestCase):
    """Test quantum discriminator."""
    
    def setUp(self):
        self.disc = QuantumDiscriminator(input_dim=2)
    
    def test_discriminate(self):
        """Should discriminate."""
        p = self.disc.discriminate([0.5, 0.5])
        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)
        print(f"  [PASS] Disc: {p:.4f}")
    
    def test_classify_batch(self):
        """Should classify batch."""
        ps = self.disc.classify_batch([[0.5, 0.5], [-0.5, -0.5]])
        self.assertEqual(len(ps), 2)
        print(f"  [PASS] Batch: {ps}")


class TestAdversarialTrainer(unittest.TestCase):
    """Test adversarial trainer."""
    
    def setUp(self):
        self.gen = QuantumGenerator(4, 2)
        self.disc = QuantumDiscriminator(2)
        self.trainer = AdversarialTrainer(self.gen, self.disc)
    
    def test_bce(self):
        """Should compute BCE."""
        loss = self.trainer.binary_cross_entropy(0.8, 1.0)
        self.assertGreater(loss, 0)
        print(f"  [PASS] BCE: {loss:.4f}")
    
    def test_train_step(self):
        """Should train."""
        real = [[0.5, 0.5], [0.6, 0.4], [0.4, 0.6]]
        self.trainer.train_step(real, 3)
        self.assertEqual(len(self.trainer.gen_losses), 1)
        self.assertEqual(len(self.trainer.disc_losses), 1)
        print(f"  [PASS] Step: G={self.trainer.gen_losses[-1]:.4f} D={self.trainer.disc_losses[-1]:.4f}")


class TestQuantumGenerativeAdversarialNetwork(unittest.TestCase):
    """Test unified QGAN."""
    
    def setUp(self):
        self.qgan = QuantumGenerativeAdversarialNetwork()
    
    def test_build(self):
        """Should build."""
        self.qgan.build(4, 2)
        self.assertIsNotNone(self.qgan.generator)
        print("  [PASS] Build")
    
    def test_train(self):
        """Should train."""
        self.qgan.build(4, 2)
        self.qgan.train(epochs=2, batch_size=4)
        self.assertEqual(len(self.qgan.trainer.gen_losses), 2)
        print("  [PASS] Train")
    
    def test_generate(self):
        """Should generate."""
        self.qgan.build(4, 2)
        samples = self.qgan.generate(3)
        self.assertEqual(len(samples), 3)
        print("  [PASS] Gen")
    
    def test_evaluate(self):
        """Should evaluate."""
        self.qgan.build(4, 2)
        scores = self.qgan.evaluate([[0.5, 0.5], [-0.5, -0.5]])
        self.assertEqual(len(scores), 2)
        print(f"  [PASS] Eval: {scores}")
    
    def test_summary(self):
        """Should summarize."""
        self.qgan.build(4, 2)
        self.qgan.train(epochs=1, batch_size=4)
        s = self.qgan.qgan_summary()
        self.assertEqual(s["epochs_trained"], 1)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
