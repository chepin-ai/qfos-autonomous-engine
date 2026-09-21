"""
Unit tests for quantum error mitigation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_mitigation import (MitigatedResult, ZeroNoiseExtrapolation,
                                      MeasurementErrorMitigation,
                                      ProbabilisticErrorCancellation,
                                      CliffordDataRegression,
                                      QuantumErrorMitigation)


class TestZeroNoiseExtrapolation(unittest.TestCase):
    """Test ZNE."""
    
    def setUp(self):
        self.zne = ZeroNoiseExtrapolation()
        self.zne.add_point(1.0, 0.8)
        self.zne.add_point(2.0, 0.6)
        self.zne.add_point(3.0, 0.4)
    
    def test_linear(self):
        """Should extrapolate."""
        e = self.zne.linear_extrapolate()
        self.assertAlmostEqual(e, 1.0, delta=0.1)
        print(f"  [PASS] ZNE: {e:.4f}")


class TestMeasurementErrorMitigation(unittest.TestCase):
    """Test MEM."""
    
    def setUp(self):
        self.mem = MeasurementErrorMitigation(1)
    
    def test_mitigate(self):
        """Should mitigate."""
        r = self.mem.mitigate({"0": 0.8, "1": 0.2})
        self.assertAlmostEqual(r["0"] + r["1"], 1.0)
        print(f"  [PASS] MEM: {r}")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.mem.fidelity({"0": 1.0}, {"0": 0.9, "1": 0.1})
        self.assertGreater(f, 0)
        print(f"  [PASS] Fid: {f:.4f}")


class TestProbabilisticErrorCancellation(unittest.TestCase):
    """Test PEC."""
    
    def setUp(self):
        self.pec = ProbabilisticErrorCancellation()
        self.pec.add_noise("X", 0.01)
    
    def test_factor(self):
        """Should compute factor."""
        f = self.pec.correction_factor(["X", "X"])
        self.assertGreater(f, 1.0)
        print(f"  [PASS] PEC: {f:.4f}")


class TestCliffordDataRegression(unittest.TestCase):
    """Test CDR."""
    
    def setUp(self):
        self.cdr = CliffordDataRegression()
        self.cdr.add_training_point([1.0], 0.9)
        self.cdr.add_training_point([2.0], 0.8)
    
    def test_predict(self):
        """Should predict."""
        p = self.cdr.predict([1.5])
        self.assertIsNotNone(p)
        print(f"  [PASS] CDR: {p:.4f}")


class TestQuantumErrorMitigation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qem = QuantumErrorMitigation(1)
    
    def test_mitigate(self):
        """Should mitigate."""
        self.qem.zne.add_point(1.0, 0.9)
        self.qem.zne.add_point(2.0, 0.8)
        r = self.qem.mitigate(0.9, "zne")
        self.assertIsNotNone(r.mitigated_value)
        print(f"  [PASS] Mit: {r.mitigated_value:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qem.qem_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
