"""
Unit tests for quantum active learning module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_active_learning import (UncertaintySampler, QueryByCommittee,
                                      QuantumUncertaintyEstimator,
                                      BatchSelector, QuantumActiveLearning)


class TestUncertaintySampler(unittest.TestCase):
    """Test uncertainty."""
    
    def setUp(self):
        self.us = UncertaintySampler()
    
    def test_entropy(self):
        """Should compute entropy."""
        h = self.us.entropy([0.5, 0.5])
        self.assertAlmostEqual(h, 1.0, places=5)
        print(f"  [PASS] Ent: {h:.4f}")
    
    def test_margin(self):
        """Should compute margin."""
        m = self.us.margin([0.6, 0.4])
        self.assertAlmostEqual(m, 0.8, places=5)
        print(f"  [PASS] Marg: {m:.4f}")
    
    def test_least_confident(self):
        """Should compute least confident."""
        c = self.us.least_confident([0.9, 0.1])
        self.assertAlmostEqual(c, 0.1, places=5)
        print(f"  [PASS] LC: {c:.4f}")


class TestQueryByCommittee(unittest.TestCase):
    """Test committee."""
    
    def setUp(self):
        self.qbc = QueryByCommittee(3)
    
    def test_vote_entropy(self):
        """Should compute vote entropy."""
        v = self.qbc.vote_entropy([0, 1, 0], 2)
        self.assertGreater(v, 0)
        print(f"  [PASS] VE: {v:.4f}")
    
    def test_disagreement(self):
        """Should compute disagreement."""
        d = self.qbc.disagreement([0, 1, 0])
        self.assertAlmostEqual(d, 2.0/3.0, places=5)
        print(f"  [PASS] Dis: {d:.4f}")


class TestQuantumUncertaintyEstimator(unittest.TestCase):
    """Test quantum uncertainty."""
    
    def setUp(self):
        self.que = QuantumUncertaintyEstimator()
    
    def test_quantum_entropy(self):
        """Should compute quantum entropy."""
        amps = [complex(1/math.sqrt(2), 0), complex(1/math.sqrt(2), 0)]
        h = self.que.quantum_entropy(amps)
        self.assertAlmostEqual(h, 1.0, places=5)
        print(f"  [PASS] QE: {h:.4f}")
    
    def test_uncertainty(self):
        """Should compute uncertainty."""
        u = self.que.uncertainty_from_superposition([0.1, 0.9, 0.2])
        self.assertGreater(u, 0)
        print(f"  [PASS] Unc: {u:.4f}")


class TestBatchSelector(unittest.TestCase):
    """Test selector."""
    
    def setUp(self):
        self.bs = BatchSelector(3)
    
    def test_uncertainty(self):
        """Should select by uncertainty."""
        sel = self.bs.select_uncertainty([0.1, 0.9, 0.5, 0.8], [0, 1, 2, 3])
        self.assertEqual(len(sel), 3)
        print(f"  [PASS] Sel: {sel}")
    
    def test_diverse(self):
        """Should select diverse."""
        emb = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]]
        sel = self.bs.select_diverse(emb, [0, 1, 2, 3])
        self.assertEqual(len(sel), 3)
        print(f"  [PASS] Div: {sel}")


class TestQuantumActiveLearning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qal = QuantumActiveLearning()
    
    def test_init(self):
        """Should initialize pool."""
        self.qal.initialize_pool(100, [0, 1, 2])
        self.assertEqual(len(self.qal.labeled), 3)
        self.assertEqual(len(self.qal.unlabeled), 97)
        print("  [PASS] Init")
    
    def test_query_uncertainty(self):
        """Should query by uncertainty."""
        self.qal.initialize_pool(10, [0])
        probs = [[0.5, 0.5] for _ in range(9)]
        sel = self.qal.query_uncertainty(probs)
        self.assertGreater(len(sel), 0)
        print(f"  [PASS] Qry: {sel}")
    
    def test_query_committee(self):
        """Should query by committee."""
        self.qal.initialize_pool(10, [0])
        votes = [[0, 1, 0] for _ in range(9)]
        sel = self.qal.query_committee(votes)
        self.assertGreater(len(sel), 0)
        print(f"  [PASS] Com: {sel}")
    
    def test_summary(self):
        """Should summarize."""
        self.qal.initialize_pool(100, [0, 1])
        s = self.qal.qal_summary()
        self.assertIn("labeled", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
