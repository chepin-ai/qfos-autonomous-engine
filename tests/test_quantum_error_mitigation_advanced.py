"""
Unit tests for quantum error mitigation advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_mitigation_advanced import (ErrorMitigationResult,
                                               ZeroNoiseExtrapolation,
                                               ProbabilisticErrorCancellation,
                                               CliffordDataRegression,
                                               MeasurementErrorMitigation,
                                               QuantumErrorMitigationAdvanced)


class TestZeroNoiseExtrapolation(unittest.TestCase):
    """Test ZNE."""
    
    def setUp(self):
        self.zne = ZeroNoiseExtrapolation()
    
    def test_richardson(self):
        """Should extrapolate."""
        v = self.zne.richardson_extrapolation([0.8, 0.6], [1.0, 2.0])
        self.assertGreater(v, 0.8)
        print(f"  [PASS] Rich: {v:.4f}")
    
    def test_exp(self):
        """Should exponential extrapolate."""
        v = self.zne.exponential_extrapolation([0.8, 0.7], [1.0, 2.0])
        self.assertIsInstance(v, float)
        print(f"  [PASS] Exp: {v:.4f}")


class TestProbabilisticErrorCancellation(unittest.TestCase):
    """Test PEC."""
    
    def setUp(self):
        self.pec = ProbabilisticErrorCancellation()
    
    def test_cost(self):
        """Should compute cost."""
        c = self.pec.mitigation_cost(0.01, 4)
        self.assertGreater(c, 1.0)
        print(f"  [PASS] Cost: {c:.4f}")
    
    def test_estimate(self):
        """Should compute unbiased."""
        e = self.pec.unbiased_estimate([0.8, 0.9], [1, -1])
        self.assertIsInstance(e, float)
        print(f"  [PASS] Est: {e:.4f}")


class TestCliffordDataRegression(unittest.TestCase):
    """Test CDR."""
    
    def setUp(self):
        self.cdr = CliffordDataRegression()
    
    def test_fit(self):
        """Should fit linear."""
        a, b = self.cdr.linear_fit([0.8, 0.9], [1.0, 1.1])
        self.assertIsNotNone(a)
        print(f"  [PASS] Fit: a={a:.4f}, b={b:.4f}")
    
    def test_predict(self):
        """Should predict."""
        p = self.cdr.predict(0.8, (1.25, 0.0))
        self.assertAlmostEqual(p, 1.0, delta=1e-6)
        print(f"  [PASS] Pred: {p:.4f}")


class TestMeasurementErrorMitigation(unittest.TestCase):
    """Test MEM."""
    
    def setUp(self):
        self.mem = MeasurementErrorMitigation()
    
    def test_inverse(self):
        """Should invert confusion."""
        inv = self.mem.confusion_matrix_inverse([[0.9, 0.1], [0.1, 0.9]])
        self.assertEqual(len(inv), 2)
        print(f"  [PASS] Inv: {inv}")
    
    def test_apply(self):
        """Should apply mitigation."""
        m = self.mem.apply_mitigation([0.5, 0.5], [[1.0, 0.0], [0.0, 1.0]])
        self.assertAlmostEqual(sum(m), 1.0, delta=1e-6)
        print(f"  [PASS] App: {m}")
    
    def test_expectation(self):
        """Should compute expectation."""
        e = self.mem.expectation_from_probs([0.7, 0.3])
        self.assertAlmostEqual(e, 0.4, delta=1e-6)
        print(f"  [PASS] Exp: {e:.2f}")


class TestQuantumErrorMitigationAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qema = QuantumErrorMitigationAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qema.mitigation_summary()
        self.assertIn("techniques", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
