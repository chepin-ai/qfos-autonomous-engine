"""
Unit tests for quantum reinforcement learning advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_reinforcement_learning_advanced import (QuantumState, QuantumAction,
                                                     QuantumQLearning,
                                                     QuantumPolicyGradient,
                                                     QuantumActorCritic,
                                                     QuantumRewardShaping,
                                                     QuantumReinforcementLearningAdvanced)


class TestQuantumQLearning(unittest.TestCase):
    """Test Q-learning."""
    
    def setUp(self):
        self.qql = QuantumQLearning()
    
    def test_get(self):
        """Should get Q-value."""
        q = self.qql.get_q(0, 0)
        self.assertEqual(q, 0.0)
        print(f"  [PASS] Q: {q}")
    
    def test_update(self):
        """Should update Q."""
        self.qql.update(0, 0, 1.0, 1)
        q = self.qql.get_q(0, 0)
        self.assertGreater(q, 0)
        print(f"  [PASS] Q: {q:.4f}")
    
    def test_greedy(self):
        """Should select action."""
        a = self.qql.epsilon_greedy(0, epsilon=0.0)
        self.assertIn(a, range(4))
        print(f"  [PASS] A: {a}")


class TestQuantumPolicyGradient(unittest.TestCase):
    """Test policy gradient."""
    
    def setUp(self):
        self.qpg = QuantumPolicyGradient()
    
    def test_softmax(self):
        """Should compute probabilities."""
        p = self.qpg.softmax_policy([1.0, 0.0])
        self.assertAlmostEqual(sum(p), 1.0, delta=1e-6)
        print(f"  [PASS] P: {p}")
    
    def test_update(self):
        """Should update policy."""
        old = list(self.qpg.policy_params)
        self.qpg.policy_gradient_update([1.0], 0, 1.0)
        self.assertNotEqual(self.qpg.policy_params, old)
        print(f"  [PASS] Upd")


class TestQuantumActorCritic(unittest.TestCase):
    """Test actor-critic."""
    
    def setUp(self):
        self.qac = QuantumActorCritic()
    
    def test_value(self):
        """Should get value."""
        v = self.qac.get_value(0)
        self.assertEqual(v, 0.0)
        print(f"  [PASS] V: {v}")
    
    def test_critic(self):
        """Should update critic."""
        td = self.qac.update_critic(0, 1.0, 1)
        self.assertNotEqual(td, 0)
        print(f"  [PASS] TD: {td:.4f}")


class TestQuantumRewardShaping(unittest.TestCase):
    """Test reward."""
    
    def setUp(self):
        self.qrs = QuantumRewardShaping()
    
    def test_shaping(self):
        """Should shape reward."""
        r = self.qrs.potential_based_shaping(1.0, 0.0, 1.0)
        self.assertEqual(r, 1.9)
        print(f"  [PASS] R: {r:.2f}")
    
    def test_potential(self):
        """Should compute potential."""
        p = self.qrs.distance_potential(5.0)
        self.assertEqual(p, -5.0)
        print(f"  [PASS] P: {p:.2f}")


class TestQuantumReinforcementLearningAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qrla = QuantumReinforcementLearningAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qrla.rl_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
