"""
Unit tests for quantum Fourier sampling advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_fourier_sampling_advanced import (FourierSample, QuantumFourierTransformSampling,
                                               PeriodFindingSampling,
                                               PhaseEstimationSampling,
                                               HiddenSubgroupSampling,
                                               QuantumFourierSamplingAdvanced)


class TestQuantumFourierTransformSampling(unittest.TestCase):
    """Test QFT."""
    
    def setUp(self):
        self.qft = QuantumFourierTransformSampling(4)
    
    def test_amplitude(self):
        """Should compute amplitude."""
        a = self.qft.qft_amplitude(1, 1)
        self.assertIsInstance(a, complex)
        print(f"  [PASS] Amp: {a}")
    
    def test_probability(self):
        """Should compute probability."""
        coeffs = [complex(1.0, 0.0)] + [complex(0.0, 0.0)] * 15
        p = self.qft.sample_probability(coeffs, 0)
        self.assertGreaterEqual(p, 0)
        print(f"  [PASS] P: {p:.4f}")


class TestPeriodFindingSampling(unittest.TestCase):
    """Test period."""
    
    def setUp(self):
        self.pfs = PeriodFindingSampling()
    
    def test_cf(self):
        """Should approximate."""
        n, d = self.pfs.continued_fraction_approximation(0.25)
        self.assertEqual(d, 4)
        print(f"  [PASS] CF: {n}/{d}")
    
    def test_period(self):
        """Should find period."""
        p = self.pfs.period_from_samples([4, 8], 4)
        self.assertGreater(p, 0)
        print(f"  [PASS] Per: {p}")


class TestPhaseEstimationSampling(unittest.TestCase):
    """Test phase."""
    
    def setUp(self):
        self.pes = PhaseEstimationSampling(4)
    
    def test_estimate(self):
        """Should estimate phase."""
        ph = self.pes.phase_estimate(8)
        self.assertEqual(ph, 0.5)
        print(f"  [PASS] Ph: {ph:.2f}")
    
    def test_precision(self):
        """Should return precision."""
        pr = self.pes.precision()
        self.assertEqual(pr, 1.0 / 16.0)
        print(f"  [PASS] Pr: {pr:.4f}")
    
    def test_success(self):
        """Should compute probability."""
        s = self.pes.success_probability(0.3)
        self.assertGreaterEqual(s, 0)
        print(f"  [PASS] Suc: {s:.2f}")


class TestHiddenSubgroupSampling(unittest.TestCase):
    """Test HSP."""
    
    def setUp(self):
        self.hsp = HiddenSubgroupSampling()
    
    def test_indicator(self):
        """Should check indicator."""
        b = self.hsp.subgroup_indicator(8, 4)
        self.assertTrue(b)
        print(f"  [PASS] Ind: {b}")
    
    def test_orthogonal(self):
        """Should extract subspace."""
        v = self.hsp.sample_orthogonal_subspace([2, 4, 6], 8)
        self.assertEqual(len(v), 3)
        print(f"  [PASS] Orth: {v}")


class TestQuantumFourierSamplingAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qfsa = QuantumFourierSamplingAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qfsa.fourier_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
