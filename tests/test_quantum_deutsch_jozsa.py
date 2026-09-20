"""
Unit tests for quantum Deutsch-Jozsa module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_deutsch_jozsa import (FunctionType, QuantumOracle,
                                   HadamardTransform, DeutschJozsa,
                                   QuantumDeutschJozsa)


class TestQuantumOracle(unittest.TestCase):
    """Test quantum oracle."""
    
    def test_constant_zero(self):
        """Should evaluate constant zero."""
        o = QuantumOracle(2)
        o.set_constant(0)
        self.assertEqual(o.evaluate(0), 0)
        self.assertEqual(o.evaluate(3), 0)
        print("  [PASS] Const 0")
    
    def test_constant_one(self):
        """Should evaluate constant one."""
        o = QuantumOracle(2)
        o.set_constant(1)
        self.assertEqual(o.evaluate(0), 1)
        self.assertEqual(o.evaluate(3), 1)
        print("  [PASS] Const 1")
    
    def test_balanced(self):
        """Should evaluate balanced."""
        o = QuantumOracle(2)
        o.set_balanced(1)
        self.assertEqual(o.evaluate(0), 0)
        self.assertEqual(o.evaluate(1), 1)
        self.assertEqual(o.evaluate(2), 0)
        self.assertEqual(o.evaluate(3), 1)
        print("  [PASS] Balanced")
    
    def test_check_constant(self):
        """Should detect constant."""
        o = QuantumOracle(2)
        o.set_constant(0)
        self.assertEqual(o.check_type(), FunctionType.CONSTANT)
        print("  [PASS] Check const")
    
    def test_check_balanced(self):
        """Should detect balanced."""
        o = QuantumOracle(2)
        o.set_balanced(1)
        self.assertEqual(o.check_type(), FunctionType.BALANCED)
        print("  [PASS] Check bal")


class TestHadamardTransform(unittest.TestCase):
    """Test Hadamard transform."""
    
    def test_single_identity(self):
        """Should preserve |+>."""
        state = [1.0 / (2**0.5), 1.0 / (2**0.5)]
        out = HadamardTransform.single(state, 0)
        self.assertAlmostEqual(abs(out[0]), 1.0, places=5)
        print("  [PASS] H|+>")
    
    def test_single_flip(self):
        """Should flip |->."""
        state = [1.0 / (2**0.5), -1.0 / (2**0.5)]
        out = HadamardTransform.single(state, 0)
        self.assertAlmostEqual(abs(out[1]), 1.0, places=5)
        print("  [PASS] H|->")


class TestDeutschJozsa(unittest.TestCase):
    """Test Deutsch-Jozsa algorithm."""
    
    def test_constant(self):
        """Should identify constant."""
        dj = DeutschJozsa(2)
        result = dj.run(lambda x: 0)
        self.assertEqual(result, FunctionType.CONSTANT)
        print("  [PASS] DJ const")
    
    def test_balanced(self):
        """Should identify balanced."""
        dj = DeutschJozsa(2)
        result = dj.run(lambda x: x & 1)
        self.assertEqual(result, FunctionType.BALANCED)
        print("  [PASS] DJ bal")
    
    def test_verify_constant(self):
        """Should verify constant result."""
        dj = DeutschJozsa(2)
        dj.run(lambda x: 1)
        self.assertTrue(dj.verify())
        print("  [PASS] Verify const")
    
    def test_verify_balanced(self):
        """Should verify balanced result."""
        dj = DeutschJozsa(3)
        dj.run(lambda x: (x >> 1) & 1)
        self.assertTrue(dj.verify())
        print("  [PASS] Verify bal")


class TestQuantumDeutschJozsa(unittest.TestCase):
    """Test unified DJ controller."""
    
    def setUp(self):
        self.qdj = QuantumDeutschJozsa()
    
    def test_setup(self):
        """Should setup."""
        self.qdj.setup(2)
        self.assertIsNotNone(self.qdj.dj)
        print("  [PASS] Setup")
    
    def test_solve_constant(self):
        """Should solve constant."""
        self.qdj.setup(2)
        r = self.qdj.solve(lambda x: 0)
        self.assertEqual(r["result"], "constant")
        self.assertTrue(r["verified"])
        print("  [PASS] Solve const")
    
    def test_solve_balanced(self):
        """Should solve balanced."""
        self.qdj.setup(2)
        r = self.qdj.solve(lambda x: x & 1)
        self.assertEqual(r["result"], "balanced")
        self.assertTrue(r["verified"])
        print("  [PASS] Solve bal")
    
    def test_summary(self):
        """Should provide summary."""
        self.qdj.setup(2)
        self.qdj.solve(lambda x: 0)
        s = self.qdj.deutsch_jozsa_summary()
        self.assertEqual(s["runs"], 1)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
