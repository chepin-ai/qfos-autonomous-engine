"""
Unit tests for quantum phase estimation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_phase_estimation import (InverseQFT, ControlledUnitary,
                                      PhaseEstimator, QuantumPhaseEstimation)


class TestInverseQFT(unittest.TestCase):
    """Test IQFT."""
    
    def setUp(self):
        self.iqft = InverseQFT(3)
    
    def test_apply(self):
        """Should apply IQFT."""
        state = [complex(1.0 / math.sqrt(8), 0.0)] * 8
        result = self.iqft.apply(state)
        self.assertEqual(len(result), 8)
        print("  [PASS] IQFT")


class TestControlledUnitary(unittest.TestCase):
    """Test controlled unitary."""
    
    def setUp(self):
        self.cu = ControlledUnitary(math.pi / 4.0)
    
    def test_matrix(self):
        """Should generate matrix."""
        U = self.cu.apply_power(0)
        self.assertEqual(len(U), 2)
        print("  [PASS] U")
    
    def test_apply(self):
        """Should apply to state."""
        state = [complex(1.0, 0.0), complex(0.0, 0.0)]
        result = self.cu.apply_to_state(state, 0)
        self.assertEqual(len(result), 2)
        print(f"  [PASS] Apply: {result}")


class TestPhaseEstimator(unittest.TestCase):
    """Test estimator."""
    
    def setUp(self):
        self.est = PhaseEstimator(3)
    
    def test_binary_fraction(self):
        """Should convert to fraction."""
        f = self.est.binary_fraction(4)
        self.assertEqual(f, 0.5)
        print(f"  [PASS] Frac: {f}")
    
    def test_estimate(self):
        """Should estimate phase."""
        r = self.est.estimate(math.pi / 4.0, 50)
        self.assertIn("estimated_phase", r)
        print(f"  [PASS] Est: {r['estimated_phase']:.4f}")
    
    def test_precision(self):
        """Should compute precision."""
        p = self.est.precision()
        self.assertGreater(p, 0)
        print(f"  [PASS] Prec: {p:.4f}")


class TestQuantumPhaseEstimation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qpe = QuantumPhaseEstimation()
    
    def test_setup(self):
        """Should setup."""
        self.qpe.setup(4)
        self.assertIsNotNone(self.qpe.estimator)
        print("  [PASS] Setup")
    
    def test_estimate(self):
        """Should estimate."""
        r = self.qpe.estimate(math.pi / 4.0, 50)
        self.assertIn("estimated_phase", r)
        print(f"  [PASS] Est: {r['estimated_phase']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        self.qpe.estimate(math.pi / 4.0, 30)
        s = self.qpe.qpe_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
