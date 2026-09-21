"""
Unit tests for quantum decision tree advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_decision_tree_advanced import (TreeNode, QuantumEntropySplitting,
                                            QuantumInformationGain,
                                            QuantumInspiredTreeBuilding,
                                            EnsembleQuantumForest,
                                            QuantumDecisionTreeAdvanced)


class TestQuantumEntropySplitting(unittest.TestCase):
    """Test entropy."""
    
    def setUp(self):
        self.qes = QuantumEntropySplitting()
    
    def test_vn(self):
        """Should compute entropy."""
        e = self.qes.von_neumann_entropy([0.5, 0.5])
        self.assertEqual(e, 1.0)
        print(f"  [PASS] H: {e:.2f}")
    
    def test_gain(self):
        """Should compute gain."""
        g = self.qes.quantum_information_gain([0.5, 0.5], [0.8, 0.2], [0.2, 0.8])
        self.assertGreater(g, 0)
        print(f"  [PASS] G: {g:.4f}")


class TestQuantumInformationGain(unittest.TestCase):
    """Test gain."""
    
    def setUp(self):
        self.qig = QuantumInformationGain()
    
    def test_split(self):
        """Should evaluate split."""
        f = [1.0, 2.0, 3.0, 4.0]
        l = [0, 0, 1, 1]
        q = self.qig.binary_split_quality(f, l, 2.5)
        self.assertGreaterEqual(q, 0)
        print(f"  [PASS] Q: {q:.4f}")
    
    def test_best(self):
        """Should find best threshold."""
        f = [1.0, 2.0, 3.0, 4.0]
        l = [0, 0, 1, 1]
        t, g = self.qig.best_threshold(f, l)
        self.assertGreaterEqual(g, 0)
        print(f"  [PASS] T: {t:.2f}, G: {g:.4f}")


class TestQuantumInspiredTreeBuilding(unittest.TestCase):
    """Test tree."""
    
    def setUp(self):
        self.qitb = QuantumInspiredTreeBuilding()
    
    def test_leaf(self):
        """Should build leaf."""
        n = self.qitb.build_leaf([0, 1, 1])
        self.assertEqual(n.prediction, 1)
        print(f"  [PASS] Leaf: {n.prediction}")
    
    def test_should_split(self):
        """Should decide split."""
        s = self.qitb.should_split([0, 1], 0)
        self.assertTrue(s)
        print(f"  [PASS] Split: {s}")
    
    def test_predict(self):
        """Should predict."""
        n = TreeNode(None, None, None, None, 1)
        p = self.qitb.predict(n, [1.0, 2.0])
        self.assertEqual(p, 1)
        print(f"  [PASS] Pred: {p}")


class TestEnsembleQuantumForest(unittest.TestCase):
    """Test forest."""
    
    def setUp(self):
        self.eqf = EnsembleQuantumForest()
    
    def test_vote(self):
        """Should vote."""
        v = self.eqf.majority_vote([0, 1, 1, 0, 1])
        self.assertEqual(v, 1)
        print(f"  [PASS] Vote: {v}")


class TestQuantumDecisionTreeAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qdta = QuantumDecisionTreeAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qdta.decision_tree_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
