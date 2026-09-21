"""
Unit tests for quantum error mitigation advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_mitigation_advanced import (NoiseScale, ZeroNoiseExtrapolation,
                                               ProbabilisticErrorCancellation,
                                               MeasurementMitigation,
                                               CliffordDataRegression,
                                               QuantumErrorMitigationAdvanced)


class TestZeroNoiseExtrapolation(unittest.TestCase):
    """Test ZNE."""
    
    def setUp(self):
        self.zne = ZeroNoiseExtrapolation()
    
    def test_richardson(self):
        """Should extrapolate."""
        v = self.zne.richardson_extrapolation([0.8, 0.6], [1.0, 2.0])
        self.assertGreater(v, 0.8)
        print(f"  [PASS] Rich: {v:.3f}")
    
    def test_exp(self):
        """Should extrapolate exponentially."""
        v = self.zne.exponential_extrapolation([0.8, 0.64], [1.0, 2.0])
        self.assertGreater(v, 0.8)
        print(f"  [PASS] Exp: {v:.3f}")


class TestProbabilisticErrorCancellation(unittest.TestCase):
    """Test PEC."""
    
    def setUp(self):
        self.pec = ProbabilisticErrorCancellation()
    
    def test_overhead(self):
        """Should compute overhead."""
        o = self.pec.sampling_overhead(0.5)
        self.assertGreater(o, 1.0)
        print(f"  [PASS] OH: {o:.3f}")
    
    def test_cost(self):
        """Should compute cost."""
        c = self.pec.mitigation_cost(10, 0.05)
        self.assertGreater(c, 1.0)
        print(f"  [PASS] Cost: {c:.3f}")


class TestMeasurementMitigation(unittest.TestCase):
    """Test measurement."""
    
    def setUp(self):
        self.mm = MeasurementMitigation()
    
    def test_confusion(self):
        """Should build matrix."""
        m = self.mm.confusion_matrix(0.05)
        self.assertEqual(len(m), 2)
        print(f"  [PASS] Conf: {m}")
    
    def test_inverse(self):
        """Should invert."""
        m = [[0.95, 0.05], [0.05, 0.95]]
        inv = self.mm.inverse_confusion(m)
        self.assertIsNotNone(inv)
        print(f"  [PASS] Inv: {inv}")
    
    def test_mitigate(self):
        """Should mitigate."""
        m = [[0.95, 0.05], [0.05, 0.95]]
        inv = self.mm.inverse_confusion(m)
        counts = {'0': 90, '1': 10}
        r = self.mm.mitigate_counts(counts, inv)
        self.assertIn('0', r)
        print(f"  [PASS] Mit: {r}")


class TestCliffordDataRegression(unittest.TestCase):
    """Test CDR."""
    
    def setUp(self):
        self.cdr = CliffordDataRegression()
    
    def test_fit(self):
        """Should fit."""
        a, b = self.cdr.linear_fit([0.8, 0.7], [1.0, 0.9])
        self.assertAlmostEqual(a, 1.0, delta=0.1)
        print(f"  [PASS] Fit: a={a:.3f}, b={b:.3f}")
    
    def test_predict(self):
        """Should predict."""
        p = self.cdr.predict(0.8, 1.0, 0.2)
        self.assertEqual(p, 1.0)
        print(f"  [PASS] Pred: {p:.3f}")


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
