"""
Unit tests for quantum reinforcement learning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_reinforcement_learning import (QuantumPolicy, QuantumPolicyNetwork,
                                            QuantumAdvantageEstimator,
                                            VariationalQLearning,
                                            QuantumReinforcementLearning)


class TestQuantumPolicyNetwork(unittest.TestCase):
    """Test policy."""
    
    def setUp(self):
        self.pn = QuantumPolicyNetwork(4, 4)
    
    def test_init(self):
        """Should initialize."""
        self.pn.initialize()
        self.assertIsNotNone(self.pn.policy)
        print("  [PASS] Init")
    
    def test_probs(self):
        """Should compute probabilities."""
        self.pn.initialize()
        p = self.pn.action_probabilities([0.5, 0.5, 0.5, 0.5])
        self.assertAlmostEqual(sum(p), 1.0, places=5)
        print(f"  [PASS] Probs: {p}")
    
    def test_select(self):
        """Should select action."""
        self.pn.initialize()
        a = self.pn.select_action([0.5, 0.5, 0.5, 0.5])
        self.assertIn(a, range(4))
        print(f"  [PASS] Act: {a}")


class TestQuantumAdvantageEstimator(unittest.TestCase):
    """Test advantage."""
    
    def setUp(self):
        self.ae = QuantumAdvantageEstimator()
    
    def test_gae(self):
        """Should compute GAE."""
        rewards = [1.0, 1.0, 1.0]
        values = [0.0, 0.5, 1.0]
        adv = self.ae.compute_advantage(rewards, values)
        self.assertEqual(len(adv), 3)
        print(f"  [PASS] GAE: {adv}")


class TestVariationalQLearning(unittest.TestCase):
    """Test Q-learning."""
    
    def setUp(self):
        self.ql = VariationalQLearning(4, 4)
    
    def test_q_value(self):
        """Should get Q-value."""
        q = self.ql.q_value(0, 0)
        self.assertEqual(q, 0.0)
        print(f"  [PASS] Q: {q}")
    
    def test_update(self):
        """Should update Q-value."""
        self.ql.update(0, 0, 1.0, 1)
        q = self.ql.q_value(0, 0)
        self.assertGreater(q, 0)
        print(f"  [PASS] Upd: {q:.4f}")
    
    def test_select(self):
        """Should select action."""
        self.ql.update(0, 0, 1.0, 1)
        a = self.ql.select_action(0)
        self.assertIn(a, range(4))
        print(f"  [PASS] Sel: {a}")


class TestQuantumReinforcementLearning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qrl = QuantumReinforcementLearning(4, 4)
    
    def test_train(self):
        """Should train episode."""
        states = [[0.1, 0.2, 0.3, 0.4]] * 5
        actions = [0, 1, 2, 3, 0]
        rewards = [1.0, 0.5, 1.0, 0.5, 1.0]
        r = self.qrl.train_episode(states, actions, rewards)
        self.assertIn("total_reward", r)
        print(f"  [PASS] Train: R={r['total_reward']}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qrl.qrl_summary()
        self.assertIn("episodes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
