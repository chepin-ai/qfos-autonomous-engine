"""
Unit tests for quantum Bernstein-Vazirani module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_bernstein_vazirani import (BVOracle, BernsteinVazirani,
                                        QuantumBernsteinVazirani)


class TestBVOracle(unittest.TestCase):
    """Test BV oracle."""
    
    def test_evaluate_zero(self):
        """Should evaluate zero string."""
        o = BVOracle(3)
        o.set_hidden_string(0)
        self.assertEqual(o.evaluate(5), 0)
        print("  [PASS] Zero s")
    
    def test_evaluate(self):
        """Should evaluate dot product."""
        o = BVOracle(3)
        o.set_hidden_string(5)  # 101
        # s . x = 1*x0 + 0*x1 + 1*x2
        self.assertEqual(o.evaluate(1), 1)   # 001 -> 1
        self.assertEqual(o.evaluate(2), 0)   # 010 -> 0
        self.assertEqual(o.evaluate(5), 0)   # 101 -> 1+0+1=2 mod 2=0
        print("  [PASS] Eval")
    
    def test_phase(self):
        """Should apply phase."""
        o = BVOracle(2)
        o.set_hidden_string(1)
        state = [0.5, 0.5, 0.5, 0.5]
        out = o.apply(state)
        # f(0)=0, f(1)=1, f(2)=0, f(3)=1
        self.assertAlmostEqual(out[0], 0.5)
        self.assertAlmostEqual(out[1], -0.5)
        self.assertAlmostEqual(out[2], 0.5)
        self.assertAlmostEqual(out[3], -0.5)
        print("  [PASS] Phase")


class TestBernsteinVazirani(unittest.TestCase):
    """Test BV algorithm."""
    
    def test_zero_string(self):
        """Should find zero string."""
        bv = BernsteinVazirani(2)
        result = bv.run(0)
        self.assertEqual(result, 0)
        print("  [PASS] Zero")
    
    def test_hidden_string(self):
        """Should find hidden string."""
        bv = BernsteinVazirani(3)
        result = bv.run(5)
        self.assertEqual(result, 5)
        print(f"  [PASS] Found: {result}")
    
    def test_verify(self):
        """Should verify."""
        bv = BernsteinVazirani(3)
        bv.run(5)
        self.assertTrue(bv.verify())
        print("  [PASS] Verify")
    
    def test_all_ones(self):
        """Should find all-ones."""
        bv = BernsteinVazirani(2)
        result = bv.run(3)
        self.assertEqual(result, 3)
        print("  [PASS] All ones")


class TestQuantumBernsteinVazirani(unittest.TestCase):
    """Test unified BV controller."""
    
    def setUp(self):
        self.qbv = QuantumBernsteinVazirani()
    
    def test_setup(self):
        """Should setup."""
        self.qbv.setup(3)
        self.assertIsNotNone(self.qbv.bv)
        print("  [PASS] Setup")
    
    def test_solve(self):
        """Should solve."""
        self.qbv.setup(3)
        r = self.qbv.solve(5)
        self.assertTrue(r["verified"])
        self.assertEqual(r["discovered"], 5)
        print(f"  [PASS] Solve: {r['discovered']}")
    
    def test_summary(self):
        """Should provide summary."""
        self.qbv.setup(2)
        self.qbv.solve(1)
        s = self.qbv.bv_summary()
        self.assertEqual(s["runs"], 1)
        self.assertEqual(s["correct"], 1)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
