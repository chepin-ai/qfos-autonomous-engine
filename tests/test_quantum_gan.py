"""
Unit tests for quantum GAN module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_gan import (QuantumState, QuantumGenerator,
                         QuantumDiscriminator,
                         AdversarialTrainer,
                         FidelityEvaluator,
                         QuantumGAN)


class TestQuantumGenerator(unittest.TestCase):
    """Test generator."""
    
    def setUp(self):
        self.gen = QuantumGenerator(3, 4)
    
    def test_init(self):
        """Should initialize."""
        self.gen.initialize()
        self.assertEqual(len(self.gen.parameters), 9)
        print("  [PASS] Init")
    
    def test_generate(self):
        """Should generate state."""
        s = self.gen.generate([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(s.amplitudes), 8)
        print(f"  [PASS] Gen: {len(s.amplitudes)} amps")


class TestQuantumDiscriminator(unittest.TestCase):
    """Test discriminator."""
    
    def setUp(self):
        self.disc = QuantumDiscriminator(3)
    
    def test_init(self):
        """Should initialize."""
        self.disc.initialize()
        self.assertEqual(len(self.disc.weights), 3)
        print("  [PASS] Init")
    
    def test_discriminate(self):
        """Should discriminate."""
        self.disc.initialize()
        s = QuantumState([1.0/math.sqrt(8)] * 8)
        d = self.disc.discriminate(s)
        self.assertGreaterEqual(d, 0.0)
        self.assertLessEqual(d, 1.0)
        print(f"  [PASS] Disc: {d:.4f}")


class TestAdversarialTrainer(unittest.TestCase):
    """Test trainer."""
    
    def setUp(self):
        self.gen = QuantumGenerator(2, 4)
        self.disc = QuantumDiscriminator(2)
        self.trainer = AdversarialTrainer(self.gen, self.disc)
    
    def test_step(self):
        """Should train step."""
        real = [QuantumState([1.0, 0.0, 0.0, 0.0])]
        g_loss, d_loss = self.trainer.train_step(real, 2)
        self.assertIsNotNone(g_loss)
        print(f"  [PASS] Step: G={g_loss:.4f}, D={d_loss:.4f}")


class TestFidelityEvaluator(unittest.TestCase):
    """Test fidelity."""
    
    def setUp(self):
        self.fe = FidelityEvaluator()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        s1 = QuantumState([1.0, 0.0])
        s2 = QuantumState([1.0, 0.0])
        f = self.fe.state_fidelity(s1, s2)
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_average(self):
        """Should compute average."""
        g = [QuantumState([1.0, 0.0])]
        t = [QuantumState([1.0, 0.0])]
        a = self.fe.average_fidelity(g, t)
        self.assertAlmostEqual(a, 1.0, places=5)
        print(f"  [PASS] Avg: {a:.4f}")


class TestQuantumGAN(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgan = QuantumGAN(2, 4)
    
    def test_train(self):
        """Should train."""
        real = [QuantumState([1.0, 0.0, 0.0, 0.0])]
        r = self.qgan.train(real, 2)
        self.assertIn("final_gen_loss", r)
        print(f"  [PASS] Train: G={r['final_gen_loss']:.4f}")
    
    def test_generate(self):
        """Should generate."""
        s = self.qgan.generate(2)
        self.assertEqual(len(s), 2)
        print(f"  [PASS] Gen: {len(s)}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qgan.qgan_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
