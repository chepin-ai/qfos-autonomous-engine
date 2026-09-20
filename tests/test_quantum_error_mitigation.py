"""
Unit tests for quantum error mitigation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_mitigation import (ZeroNoiseExtrapolation,
                                      ProbabilisticErrorCancellation,
                                      MeasurementErrorMitigation,
                                      QuantumErrorMitigation)


class TestZNE(unittest.TestCase):
    """Test ZNE."""
    
    def setUp(self):
        self.zne = ZeroNoiseExtrapolation()
    
    def test_linear(self):
        """Should linear extrapolate."""
        self.zne.add_point(1.0, 0.9)
        self.zne.add_point(2.0, 0.8)
        val = self.zne.linear_extrapolate()
        self.assertGreater(val, 0.9)
        print(f"  [PASS] Lin: {val:.4f}")
    
    def test_richardson(self):
        """Should Richardson extrapolate."""
        self.zne.add_point(1.0, 0.9)
        self.zne.add_point(2.0, 0.8)
        val = self.zne.richardson_extrapolate()
        self.assertIsNotNone(val)
        print(f"  [PASS] Rich: {val:.4f}")


class TestPEC(unittest.TestCase):
    """Test PEC."""
    
    def setUp(self):
        self.pec = ProbabilisticErrorCancellation()
    
    def test_noise_model(self):
        """Should add noise model."""
        self.pec.add_noise_model(0.01, "depolarizing")
        self.assertEqual(len(self.pec.noise_channels), 1)
        print("  [PASS] Noise")
    
    def test_weight(self):
        """Should compute weight."""
        w = self.pec.mitigation_weight(10, 0.01)
        self.assertGreater(w, 1.0)
        print(f"  [PASS] Weight: {w:.4f}")
    
    def test_sample(self):
        """Should sample."""
        val = self.pec.sample_mitigated(0.5, 0.01, 100)
        self.assertIsNotNone(val)
        print(f"  [PASS] Sample: {val:.4f}")


class TestMEM(unittest.TestCase):
    """Test measurement error mitigation."""
    
    def setUp(self):
        self.mem = MeasurementErrorMitigation(1)
    
    def test_calibration(self):
        """Should add calibration."""
        self.mem.add_calibration(0, 0, 0.95)
        self.assertAlmostEqual(self.mem.calibration_matrix[0][0], 0.95)
        print("  [PASS] Cal")
    
    def test_inverse(self):
        """Should compute inverse."""
        inv = self.mem.inverse_matrix()
        self.assertEqual(len(inv), 2)
        print("  [PASS] Inv")
    
    def test_mitigate(self):
        """Should mitigate counts."""
        counts = {0: 900, 1: 100}
        mit = self.mem.mitigate_counts(counts)
        self.assertIn(0, mit)
        self.assertIn(1, mit)
        print(f"  [PASS] Mit: {mit}")


class TestQuantumErrorMitigation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qem = QuantumErrorMitigation()
    
    def test_zne(self):
        """Should run ZNE."""
        val = self.qem.extrapolate_zne([1.0, 2.0], [0.9, 0.8])
        self.assertIsNotNone(val)
        print(f"  [PASS] ZNE: {val:.4f}")
    
    def test_setup_mem(self):
        """Should setup MEM."""
        self.qem.setup_measurement(2)
        self.assertIsNotNone(self.qem.mem)
        print("  [PASS] MEM")
    
    def test_mitigate_counts(self):
        """Should mitigate counts."""
        counts = {0: 900, 1: 100}
        mit = self.qem.mitigate_counts(counts)
        self.assertIn(0, mit)
        print(f"  [PASS] Counts: {mit}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qem.mitigation_summary()
        self.assertIn("zne_points", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
