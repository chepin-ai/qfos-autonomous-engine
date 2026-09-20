"""
Unit tests for quantum diffusion model module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_diffusion_model import (NoiseSchedule, ForwardDiffusion,
                                     QuantumNoiseKernel, ReverseSampler,
                                     QuantumDiffusionModel)


class TestNoiseSchedule(unittest.TestCase):
    """Test noise schedule."""
    
    def setUp(self):
        self.ns = NoiseSchedule(num_steps=50)
    
    def test_betas(self):
        """Should have correct length."""
        self.assertEqual(len(self.ns.betas), 50)
        print("  [PASS] Betas")
    
    def test_alpha_bar(self):
        """Should decay."""
        ab0 = self.ns.alpha_bar(0)
        ab_last = self.ns.alpha_bar(49)
        self.assertGreater(ab0, ab_last)
        print(f"  [PASS] AB: {ab0:.4f}->{ab_last:.4f}")
    
    def test_snr(self):
        """Should compute SNR."""
        snr = self.ns.signal_to_noise_ratio(10)
        self.assertIsInstance(snr, float)
        print(f"  [PASS] SNR: {snr:.2f}dB")


class TestForwardDiffusion(unittest.TestCase):
    """Test forward diffusion."""
    
    def setUp(self):
        self.fd = ForwardDiffusion(NoiseSchedule(50))
    
    def test_add_noise(self):
        """Should add noise."""
        x0 = [1.0, 0.0, -1.0, 0.5]
        xt, noise = self.fd.add_noise(x0, 10)
        self.assertEqual(len(xt), 4)
        self.assertEqual(len(noise), 4)
        print("  [PASS] Noise")
    
    def test_sample_noisy(self):
        """Should sample noisy."""
        x0 = [1.0, 0.0, -1.0, 0.5]
        xt = self.fd.sample_noisy(x0)
        self.assertEqual(len(xt), 4)
        print("  [PASS] Noisy")


class TestQuantumNoiseKernel(unittest.TestCase):
    """Test quantum noise kernel."""
    
    def setUp(self):
        self.qnk = QuantumNoiseKernel()
    
    def test_quantum_noise(self):
        """Should generate quantum noise."""
        n = self.qnk.quantum_noise(4)
        self.assertEqual(len(n), 4)
        print(f"  [PASS] QNoise: {n}")


class TestReverseSampler(unittest.TestCase):
    """Test reverse sampler."""
    
    def setUp(self):
        self.rs = ReverseSampler(NoiseSchedule(50))
    
    def test_denoise(self):
        """Should denoise."""
        xt = [0.5, -0.3, 0.1, 0.8]
        noise = [0.1, 0.1, 0.1, 0.1]
        x_prev = self.rs.denoise_step(xt, 10, noise)
        self.assertEqual(len(x_prev), 4)
        print("  [PASS] Denoise")
    
    def test_simple(self):
        """Should simple denoise."""
        xt = [0.5, -0.3, 0.1, 0.8]
        noise = [0.1, 0.1, 0.1, 0.1]
        x0 = self.rs.simple_denoise(xt, 10, noise)
        self.assertEqual(len(x0), 4)
        print("  [PASS] Simple")


class TestQuantumDiffusionModel(unittest.TestCase):
    """Test unified diffusion model."""
    
    def setUp(self):
        self.qdm = QuantumDiffusionModel(data_dim=4, num_steps=20)
    
    def test_predict(self):
        """Should predict noise."""
        xt = [0.5, -0.3, 0.1, 0.8]
        pred = self.qdm.predict_noise(xt, 5)
        self.assertEqual(len(pred), 4)
        print("  [PASS] Predict")
    
    def test_generate(self):
        """Should generate."""
        samples = self.qdm.generate(2)
        self.assertEqual(len(samples), 2)
        self.assertEqual(len(samples[0]), 4)
        print("  [PASS] Gen")
    
    def test_loss(self):
        """Should compute loss."""
        x0 = [1.0, 0.0, -1.0, 0.5]
        loss = self.qdm.diffusion_loss(x0)
        self.assertGreaterEqual(loss, 0)
        print(f"  [PASS] Loss: {loss:.4f}")
    
    def test_train(self):
        """Should train."""
        dataset = [[1.0, 0.0, -1.0, 0.5], [0.0, 1.0, 0.0, -0.5]]
        self.qdm.train_step(dataset)
        self.assertEqual(len(self.qdm.training_history), 1)
        print("  [PASS] Train")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qdm.diffusion_summary()
        self.assertEqual(s["data_dim"], 4)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
