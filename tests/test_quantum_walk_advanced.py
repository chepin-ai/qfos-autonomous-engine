"""
Unit tests for quantum walk advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_walk_advanced import (WalkState, DiscreteTimeQuantumWalk,
                                   ContinuousTimeQuantumWalk,
                                   HittingTime,
                                   SpatialSearch,
                                   QuantumWalkAdvanced)


class TestDiscreteTimeQuantumWalk(unittest.TestCase):
    """Test discrete."""
    
    def setUp(self):
        self.dtw = DiscreteTimeQuantumWalk(8)
    
    def test_coin(self):
        """Should apply coin."""
        c = self.dtw.coin_operator(0)
        self.assertEqual(len(c), 2)
        print(f"  [PASS] Coin: {len(c)} states")
    
    def test_shift(self):
        """Should shift."""
        p = self.dtw.shift_operator(4, 1)
        self.assertEqual(p, 5)
        print(f"  [PASS] Shift: {p}")
    
    def test_step(self):
        """Should evolve."""
        s = WalkState(4, 0, complex(1.0, 0.0))
        r = self.dtw.step(s)
        self.assertEqual(len(r), 2)
        print(f"  [PASS] Step: {len(r)} states")


class TestContinuousTimeQuantumWalk(unittest.TestCase):
    """Test continuous."""
    
    def setUp(self):
        self.ctw = ContinuousTimeQuantumWalk(8)
    
    def test_adjacency(self):
        """Should create adjacency."""
        a = self.ctw.adjacency_line()
        self.assertEqual(len(a), 8)
        print(f"  [PASS] Adj: {len(a)} nodes")
    
    def test_probability(self):
        """Should compute prob."""
        p = self.ctw.evolution_probability(1.0, 0, 1)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.4f}")


class TestHittingTime(unittest.TestCase):
    """Test hitting."""
    
    def setUp(self):
        self.ht = HittingTime()
    
    def test_expected(self):
        """Should compute hitting time."""
        t = self.ht.expected_hitting_time(100)
        self.assertGreater(t, 0)
        print(f"  [PASS] HT: {t:.1f}")
    
    def test_speedup(self):
        """Should compute speedup."""
        s = self.ht.quantum_speedup(100.0, 10.0)
        self.assertEqual(s, 10.0)
        print(f"  [PASS] SU: {s:.1f}")


class TestSpatialSearch(unittest.TestCase):
    """Test search."""
    
    def setUp(self):
        self.ss = SpatialSearch()
    
    def test_complexity(self):
        """Should compute complexity."""
        c = self.ss.search_complexity(100)
        self.assertEqual(c, 10.0)
        print(f"  [PASS] O: {c:.1f}")
    
    def test_success(self):
        """Should compute probability."""
        p = self.ss.success_probability(1, 100, 7)
        self.assertGreaterEqual(p, 0)
        print(f"  [PASS] Ps: {p:.4f}")


class TestQuantumWalkAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qwa = QuantumWalkAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qwa.walk_summary()
        self.assertIn("types", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
