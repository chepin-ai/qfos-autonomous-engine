"""
Unit tests for quantum walks module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_walks import (WalkPosition, ClassicalRandomWalk,
                           DiscreteQuantumWalk,
                           ContinuousQuantumWalk,
                           QuantumWalkSearch,
                           QuantumWalks)


class TestClassicalRandomWalk(unittest.TestCase):
    """Test classical walk."""
    
    def setUp(self):
        self.cw = ClassicalRandomWalk(10)
    
    def test_step(self):
        """Should step."""
        p = self.cw.step()
        self.assertIn(p, [-1, 1])
        print(f"  [PASS] Step: {p}")
    
    def test_walk(self):
        """Should walk."""
        h = self.cw.walk()
        self.assertEqual(len(h), 11)
        print(f"  [PASS] Walk: {len(h)}")
    
    def test_variance(self):
        """Should compute variance."""
        self.cw.walk()
        v = self.cw.variance()
        self.assertGreater(v, 0)
        print(f"  [PASS] Var: {v:.2f}")


class TestDiscreteQuantumWalk(unittest.TestCase):
    """Test discrete walk."""
    
    def setUp(self):
        self.dq = DiscreteQuantumWalk(8)
    
    def test_coin(self):
        """Should apply coin."""
        s = self.dq.coin_operator([1.0, 0.0])
        self.assertEqual(len(s), 2)
        print("  [PASS] Coin")
    
    def test_shift(self):
        """Should shift."""
        ps = [0.0] * 8
        ps[4] = 1.0
        s = self.dq.shift_operator(ps, [1.0, 0.0])
        self.assertEqual(len(s), 8)
        print("  [PASS] Shift")
    
    def test_walk(self):
        """Should walk."""
        p = self.dq.walk(3)
        self.assertEqual(len(p), 8)
        print(f"  [PASS] QWalk: sum={sum(p):.3f}")
    
    def test_variance(self):
        """Should compute variance."""
        self.dq.walk(3)
        v = self.dq.variance()
        self.assertGreater(v, 0)
        print(f"  [PASS] QVar: {v:.2f}")


class TestContinuousQuantumWalk(unittest.TestCase):
    """Test continuous walk."""
    
    def setUp(self):
        self.cq = ContinuousQuantumWalk(8)
    
    def test_adjacency(self):
        """Should create adjacency."""
        a = self.cq.adjacency_matrix()
        self.assertEqual(len(a), 8)
        print("  [PASS] Adj")
    
    def test_laplacian(self):
        """Should create Laplacian."""
        l = self.cq.laplacian()
        self.assertEqual(len(l), 8)
        print("  [PASS] Lap")
    
    def test_evolve(self):
        """Should evolve."""
        p = self.cq.evolve(1.0)
        self.assertEqual(len(p), 8)
        print(f"  [PASS] Evol: sum={sum(p):.3f}")


class TestQuantumWalkSearch(unittest.TestCase):
    """Test search."""
    
    def setUp(self):
        self.qs = QuantumWalkSearch(8)
    
    def test_search(self):
        """Should search."""
        pos, prob = self.qs.search([3], 5)
        self.assertGreaterEqual(pos, 0)
        print(f"  [PASS] Srch: pos={pos}, P={prob:.3f}")


class TestQuantumWalks(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qw = QuantumWalks(8)
    
    def test_compare(self):
        """Should compare."""
        c = self.qw.compare_variances(5)
        self.assertIn("classical_variance", c)
        print(f"  [PASS] Cmp: {c}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qw.qw_summary()
        self.assertIn("types", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
