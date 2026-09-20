"""
Unit tests for quantum order finding module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_order_finding import (ModularArithmetic, PhaseEstimator,
                                   OrderFinder, QuantumOrderFinding)


class TestModularArithmetic(unittest.TestCase):
    """Test modular arithmetic."""
    
    def test_gcd(self):
        """Should compute GCD."""
        self.assertEqual(ModularArithmetic.gcd(12, 8), 4)
        self.assertEqual(ModularArithmetic.gcd(17, 5), 1)
        print("  [PASS] GCD")
    
    def test_mod_exp(self):
        """Should compute modular exponentiation."""
        self.assertEqual(ModularArithmetic.mod_exp(2, 10, 1000), 24)
        self.assertEqual(ModularArithmetic.mod_exp(3, 4, 7), 4)
        print("  [PASS] ModExp")
    
    def test_order(self):
        """Should find order."""
        r = ModularArithmetic.order(2, 15)
        self.assertEqual(r, 4)
        print(f"  [PASS] Order: {r}")
    
    def test_order_coprime(self):
        """Should reject non-coprime."""
        r = ModularArithmetic.order(3, 15)
        self.assertEqual(r, 0)
        print("  [PASS] Non-coprime")


class TestPhaseEstimator(unittest.TestCase):
    """Test phase estimator."""
    
    def setUp(self):
        self.pe = PhaseEstimator(num_precision_qubits=8)
    
    def test_estimate(self):
        """Should estimate phase."""
        phase = self.pe.estimate_phase(2, 15)
        self.assertGreaterEqual(phase, 0.0)
        self.assertLess(phase, 1.0)
        print(f"  [PASS] Phase: {phase:.4f}")
    
    def test_continued_fraction(self):
        """Should compute convergent."""
        num, den = self.pe.continued_fraction(0.25, 100)
        self.assertEqual(den, 4)
        print(f"  [PASS] CF: {num}/{den}")
    
    def test_cf_exact(self):
        """Should handle exact fraction."""
        num, den = self.pe.continued_fraction(0.5, 100)
        self.assertEqual(den, 2)
        print(f"  [PASS] CF exact: {num}/{den}")


class TestOrderFinder(unittest.TestCase):
    """Test order finder."""
    
    def setUp(self):
        self.of = OrderFinder()
    
    def test_classical(self):
        """Should find order classically."""
        r = self.of.classical_order(2, 15)
        self.assertEqual(r, 4)
        print(f"  [PASS] Classical: {r}")
    
    def test_quantum(self):
        """Should find order quantum."""
        r = self.of.quantum_order(2, 15)
        self.assertGreater(r, 0)
        self.assertEqual(ModularArithmetic.mod_exp(2, r, 15), 1)
        print(f"  [PASS] Quantum: {r}")
    
    def test_find_order(self):
        """Should find order."""
        result = self.of.find_order(2, 15, "classical")
        self.assertTrue(result["verified"])
        print(f"  [PASS] Find: r={result['order']}")
    
    def test_factor(self):
        """Should extract factors."""
        factors = self.of.factor_from_order(2, 15, 4)
        self.assertIsNotNone(factors)
        p, q = factors
        self.assertEqual(p * q, 15)
        print(f"  [PASS] Factor: {p}*{q}")


class TestQuantumOrderFinding(unittest.TestCase):
    """Test unified quantum order finding."""
    
    def setUp(self):
        self.qof = QuantumOrderFinding()
    
    def test_solve(self):
        """Should attempt factoring."""
        result = self.qof.solve(15)
        self.assertIn("factors", result)
        print(f"  [PASS] Solve: {result.get('factors')}")
    
    def test_summary(self):
        """Should provide summary."""
        self.qof.solve(15)
        s = self.qof.order_finding_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
