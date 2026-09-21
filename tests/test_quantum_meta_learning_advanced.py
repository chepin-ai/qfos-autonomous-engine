"""
Unit tests for quantum meta-learning advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_meta_learning_advanced import (MetaTask, QuantumMAML,
                                            QuantumHypernetwork,
                                            QuantumFewShotLearning,
                                            QuantumTransferLearning,
                                            QuantumMetaLearningAdvanced)


class TestQuantumMAML(unittest.TestCase):
    """Test MAML."""
    
    def setUp(self):
        self.qmaml = QuantumMAML()
    
    def test_inner(self):
        """Should update weights."""
        task = MetaTask([[1.0]], [1], [[1.0]], [1])
        w = self.qmaml.inner_loop_update([0.5, 0.5], task)
        self.assertEqual(len(w), 2)
        print(f"  [PASS] W: {w}")
    
    def test_loss(self):
        """Should compute meta-loss."""
        task = MetaTask([[1.0]], [1], [[1.0]], [1])
        l = self.qmaml.meta_loss([0.5, 0.5], [task])
        self.assertGreaterEqual(l, 0)
        print(f"  [PASS] L: {l:.4f}")


class TestQuantumHypernetwork(unittest.TestCase):
    """Test hyper."""
    
    def setUp(self):
        self.qh = QuantumHypernetwork()
    
    def test_generate(self):
        """Should generate weights."""
        w = self.qh.generate_weights([1.0, 0.5], 3)
        self.assertEqual(len(w), 3)
        print(f"  [PASS] W: {w}")
    
    def test_embed(self):
        """Should embed task."""
        e = self.qh.task_embedding([[1.0, 0.0], [0.0, 1.0]], [0, 1])
        self.assertEqual(len(e), 3)
        print(f"  [PASS] E: {e}")


class TestQuantumFewShotLearning(unittest.TestCase):
    """Test few-shot."""
    
    def setUp(self):
        self.qfsl = QuantumFewShotLearning()
    
    def test_proto(self):
        """Should compute prototype."""
        p = self.qfsl.prototype_embedding([[1.0, 0.0], [0.0, 1.0]], [0, 1], 0)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] P: {p}")
    
    def test_dist(self):
        """Should compute distance."""
        d = self.qfsl.prototype_distance([0.0, 0.0], [3.0, 4.0])
        self.assertEqual(d, 5.0)
        print(f"  [PASS] D: {d:.1f}")
    
    def test_predict(self):
        """Should predict."""
        protos = {0: [0.0, 0.0], 1: [10.0, 0.0]}
        p = self.qfsl.predict([1.0, 0.0], protos)
        self.assertEqual(p, 0)
        print(f"  [PASS] Pred: {p}")


class TestQuantumTransferLearning(unittest.TestCase):
    """Test transfer."""
    
    def setUp(self):
        self.qtl = QuantumTransferLearning()
    
    def test_score(self):
        """Should compute score."""
        s = self.qtl.transfer_score([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(s, 1.0, delta=1e-10)
        print(f"  [PASS] S: {s:.4f}")
    
    def test_schedule(self):
        """Should generate schedule."""
        sch = self.qtl.fine_tuning_schedule(0.1, 3)
        self.assertEqual(len(sch), 3)
        print(f"  [PASS] Sch: {sch}")


class TestQuantumMetaLearningAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qmla = QuantumMetaLearningAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qmla.meta_learning_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
