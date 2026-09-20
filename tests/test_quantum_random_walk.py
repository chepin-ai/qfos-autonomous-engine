"""
Unit tests for quantum random walk module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_random_walk import (CoinOperator, ShiftOperator,
                                  QuantumWalkLine, QuantumWalkGraph,
                                  QuantumRandomWalk)


class TestCoinOperator(unittest.TestCase):
    """Test coin."""
    
    def setUp(self):
        self.coin = CoinOperator("hadamard")
    
    def test_hadamard(self):
        """Should create Hadamard."""
        h = self.coin.hadamard()
        self.assertEqual(len(h), 2)
        self.assertEqual(len(h[0]), 2)
        print("  [PASS] H")
    
    def test_apply(self):
        """Should apply coin."""
        state = [complex(1.0, 0.0), complex(0.0, 0.0)]
        new_state = self.coin.apply(state)
        self.assertEqual(len(new_state), 2)
        print(f"  [PASS] Apply: {new_state}")


class TestShiftOperator(unittest.TestCase):
    """Test shift."""
    
    def setUp(self):
        self.shift = ShiftOperator(11)
    
    def test_step(self):
        """Should step."""
        probs = [0.0] * 11
        probs[5] = 1.0
        coin = [complex(0.5**0.5, 0.0), complex(0.5**0.5, 0.0)]
        new_probs = self.shift.step(probs, coin)
        self.assertAlmostEqual(sum(new_probs), 1.0, places=5)
        print(f"  [PASS] Step: sum={sum(new_probs):.4f}")


class TestQuantumWalkLine(unittest.TestCase):
    """Test line walk."""
    
    def setUp(self):
        self.qwl = QuantumWalkLine(21)
    
    def test_walk(self):
        """Should walk."""
        dist = self.qwl.walk(10)
        self.assertAlmostEqual(sum(dist), 1.0, places=5)
        print(f"  [PASS] Walk: sum={sum(dist):.4f}")
    
    def test_mean(self):
        """Should compute mean."""
        self.qwl.walk(10)
        m = self.qwl.mean_position()
        print(f"  [PASS] Mean: {m:.4f}")
    
    def test_spread(self):
        """Should compute spread."""
        self.qwl.walk(10)
        s = self.qwl.spread()
        self.assertGreater(s, 0)
        print(f"  [PASS] Spread: {s:.4f}")


class TestQuantumWalkGraph(unittest.TestCase):
    """Test graph walk."""
    
    def setUp(self):
        self.qwg = QuantumWalkGraph(5)
        self.qwg.add_edge(0, 1)
        self.qwg.add_edge(1, 2)
        self.qwg.add_edge(2, 3)
        self.qwg.add_edge(3, 4)
    
    def test_degree(self):
        """Should compute degree."""
        self.assertEqual(self.qwg.degree(1), 2)
        print("  [PASS] Degree")
    
    def test_walk(self):
        """Should walk on graph."""
        dist = self.qwg.walk(5)
        self.assertAlmostEqual(sum(dist), 1.0, places=5)
        print(f"  [PASS] Graph: sum={sum(dist):.4f}")


class TestQuantumRandomWalk(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qrw = QuantumRandomWalk()
    
    def test_line(self):
        """Should run line walk."""
        r = self.qrw.run_line(10)
        self.assertIn("mean_position", r)
        print(f"  [PASS] Line: mean={r['mean_position']:.4f}")
    
    def test_graph(self):
        """Should run graph walk."""
        self.qrw.graph(4)
        self.qrw.graph_walk.add_edge(0, 1)
        self.qrw.graph_walk.add_edge(1, 2)
        r = self.qrw.run_graph(3)
        self.assertIn("final_distribution", r)
        print("  [PASS] Graph")
    
    def test_summary(self):
        """Should summarize."""
        self.qrw.run_line(5)
        s = self.qrw.walk_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
