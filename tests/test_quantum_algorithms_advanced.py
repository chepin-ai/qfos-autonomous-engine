"""
Unit tests for quantum algorithms advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_algorithms_advanced import (PhaseEstimate, QuantumPhaseEstimation,
                                         OrderFinding,
                                         QuantumGradientDescent,
                                         ShorsAlgorithm,
                                         QuantumAlgorithmsAdvanced)


class TestQuantumPhaseEstimation(unittest.TestCase):
    """Test QPE."""
    
    def setUp(self):
        self.qpe = QuantumPhaseEstimation(8)
    
    def test_bits(self):
        """Should compute bits."""
        b = self.qpe.required_bits(0.01)
        self.assertGreater(b, 0)
        print(f"  [PASS] Bits: {b}")
    
    def test_phase(self):
        """Should convert phase."""
        p = self.qpe.phase_from_measurement(64)
        self.assertEqual(p, 0.25)
        print(f"  [PASS] Phase: {p:.2f}")
    
    def test_precision(self):
        """Should compute precision."""
        p = self.qpe.precision()
        self.assertGreater(p, 0)
        print(f"  [PASS] Prec: {p:.5f}")


class TestOrderFinding(unittest.TestCase):
    """Test order."""
    
    def setUp(self):
        self.of = OrderFinding()
    
    def test_classical(self):
        """Should find order."""
        r = self.of.order_classical(2, 15)
        self.assertGreater(r, 0)
        print(f"  [PASS] r: {r}")
    
    def test_period(self):
        """Should estimate period."""
        r = self.of.period_from_phase(0.25, 15)
        self.assertGreater(r, 0)
        print(f"  [PASS] Period: {r}")


class TestQuantumGradientDescent(unittest.TestCase):
    """Test gradient."""
    
    def setUp(self):
        self.qgd = QuantumGradientDescent()
    
    def test_gradient(self):
        """Should compute gradient."""
        g = self.qgd.quantum_gradient([1.0, 2.0], lambda p: sum(p))
        self.assertEqual(len(g), 2)
        print(f"  [PASS] Grad: {g}")
    
    def test_update(self):
        """Should update."""
        u = self.qgd.update([1.0, 2.0], [0.1, 0.2])
        self.assertEqual(len(u), 2)
        print(f"  [PASS] Upd: {u}")


class TestShorsAlgorithm(unittest.TestCase):
    """Test Shor."""
    
    def setUp(self):
        self.shor = ShorsAlgorithm()
    
    def test_factor(self):
        """Should find factors."""
        f = self.shor.factor_from_order(15, 2, 4)
        self.assertIsNotNone(f)
        print(f"  [PASS] F: {f}")
    
    def test_prob(self):
        """Should compute prob."""
        p = self.shor.success_probability(15)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.3f}")


class TestQuantumAlgorithmsAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qaa = QuantumAlgorithmsAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qaa.algorithms_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
