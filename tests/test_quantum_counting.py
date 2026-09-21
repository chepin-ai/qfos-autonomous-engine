"""
Unit tests for quantum counting module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_counting import (AmplitudeEstimate,
                              QuantumAmplitudeEstimation,
                              QuantumMonteCarlo,
                              QuantumIntegration,
                              QuantumCounting)


class TestQuantumAmplitudeEstimation(unittest.TestCase):
    """Test QAE."""
    
    def setUp(self):
        self.qae = QuantumAmplitudeEstimation(4)
    
    def test_estimate(self):
        """Should estimate amplitude."""
        est = self.qae.estimate(0.3)
        self.assertAlmostEqual(est.amplitude, 0.3, delta=0.01)
        print(f"  [PASS] Amp: {est.amplitude:.3f} +/- {est.error_bound:.3f}")
    
    def test_precision(self):
        """Should compute required bits."""
        bits = self.qae.required_precision(0.1)
        self.assertGreater(bits, 0)
        print(f"  [PASS] Bits: {bits}")
    
    def test_speedup(self):
        """Should compute speedup."""
        q = self.qae.quadratic_speedup(10000)
        self.assertEqual(q, 100)
        print(f"  [PASS] Speedup: {q}")


class TestQuantumMonteCarlo(unittest.TestCase):
    """Test QMC."""
    
    def setUp(self):
        self.qmc = QuantumMonteCarlo()
    
    def test_expected_value(self):
        """Should estimate expected value."""
        samples = [1.0, 2.0, 3.0, 4.0, 5.0]
        mean, err = self.qmc.expected_value_estimate(samples)
        self.assertAlmostEqual(mean, 3.0, delta=0.01)
        print(f"  [PASS] EV: {mean:.2f} +/- {err:.4f}")
    
    def test_probability(self):
        """Should estimate probability."""
        est = self.qmc.probability_estimate(3, 10, 3)
        self.assertAlmostEqual(est.amplitude, 0.3, delta=0.01)
        print(f"  [PASS] P: {est.amplitude:.3f}")


class TestQuantumIntegration(unittest.TestCase):
    """Test integration."""
    
    def setUp(self):
        self.qi = QuantumIntegration()
    
    def test_integrate(self):
        """Should integrate."""
        f = [0.0, 1.0, 2.0, 3.0, 4.0]
        integral, err = self.qi.integrate_1d(f, 1.0)
        self.assertGreater(integral, 0)
        print(f"  [PASS] Int: {integral:.2f} +/- {err:.4f}")


class TestQuantumCounting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumCounting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qc.counting_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
