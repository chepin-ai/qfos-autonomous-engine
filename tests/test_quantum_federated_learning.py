"""
Unit tests for quantum federated learning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_federated_learning import (QuantumClientModel, SecureAggregator,
                                        DifferentialPrivacy,
                                        FederatedAveraging,
                                        QuantumFederatedLearning)


class TestSecureAggregator(unittest.TestCase):
    """Test aggregator."""
    
    def setUp(self):
        self.sa = SecureAggregator()
    
    def test_weighted(self):
        """Should compute weighted average."""
        models = [
            QuantumClientModel("a", [1.0, 2.0], 10),
            QuantumClientModel("b", [3.0, 4.0], 30)
        ]
        avg = self.sa.weighted_average(models)
        self.assertAlmostEqual(avg[0], 2.5, places=5)
        print(f"  [PASS] WAvg: {avg}")
    
    def test_simple(self):
        """Should compute simple average."""
        models = [
            QuantumClientModel("a", [1.0, 2.0], 10),
            QuantumClientModel("b", [3.0, 4.0], 10)
        ]
        avg = self.sa.simple_average(models)
        self.assertAlmostEqual(avg[0], 2.0, places=5)
        print(f"  [PASS] SAvg: {avg}")


class TestDifferentialPrivacy(unittest.TestCase):
    """Test DP."""
    
    def setUp(self):
        self.dp = DifferentialPrivacy(1.0, 1e-5)
    
    def test_noise(self):
        """Should add noise."""
        p = self.dp.add_noise([1.0, 2.0])
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Noise: {p}")
    
    def test_clip(self):
        """Should clip."""
        p = self.dp.clip_gradients([10.0, 0.0], 1.0)
        norm = sum(x**2 for x in p) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Clip: norm={norm:.4f}")


class TestFederatedAveraging(unittest.TestCase):
    """Test FedAvg."""
    
    def setUp(self):
        self.fa = FederatedAveraging(SecureAggregator())
    
    def test_init(self):
        """Should initialize."""
        self.fa.initialize(4)
        self.assertEqual(len(self.fa.global_model), 4)
        print("  [PASS] Init")
    
    def test_aggregate(self):
        """Should aggregate."""
        self.fa.initialize(2)
        models = [
            QuantumClientModel("a", [1.0, 2.0], 10),
            QuantumClientModel("b", [3.0, 4.0], 10)
        ]
        g = self.fa.aggregate(models)
        self.assertEqual(len(g), 2)
        print(f"  [PASS] Agg: {g}")
    
    def test_distribute(self):
        """Should distribute."""
        self.fa.initialize(2)
        d = self.fa.distribute()
        self.assertEqual(len(d), 2)
        print("  [PASS] Dist")


class TestQuantumFederatedLearning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qfl = QuantumFederatedLearning()
    
    def test_register(self):
        """Should register client."""
        self.qfl.register_client("c1", [1.0, 2.0], 100)
        self.assertEqual(len(self.qfl.clients), 1)
        print("  [PASS] Reg")
    
    def test_round(self):
        """Should run training round."""
        self.qfl.register_client("c1", [1.0, 2.0], 100)
        self.qfl.register_client("c2", [3.0, 4.0], 200)
        r = self.qfl.train_round(apply_privacy=False)
        self.assertIn("round", r)
        print(f"  [PASS] Round: {r}")
    
    def test_evaluate(self):
        """Should evaluate."""
        self.qfl.register_client("c1", [1.0, 0.0], 100)
        self.qfl.train_round(apply_privacy=False)
        acc = self.qfl.evaluate([[1.0, 0.0], [0.0, 1.0]])
        self.assertGreaterEqual(acc, 0.0)
        print(f"  [PASS] Eval: {acc:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        self.qfl.register_client("c1", [1.0, 2.0], 100)
        s = self.qfl.qfl_summary()
        self.assertIn("clients", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
