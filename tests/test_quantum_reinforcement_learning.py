"""
Unit tests for quantum reinforcement learning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_reinforcement_learning import (QuantumPolicy, QuantumQFunction,
                                            QuantumPolicyGradient,
                                            QuantumQLearning,
                                            QuantumReinforcementLearning)


class TestQuantumPolicy(unittest.TestCase):
    """Test quantum policy."""
    
    def setUp(self):
        self.qp = QuantumPolicy(num_qubits=4, num_actions=2)
    
    def test_probabilities(self):
        """Should compute probabilities."""
        probs = self.qp.action_probabilities(0)
        self.assertEqual(len(probs), 2)
        self.assertAlmostEqual(sum(probs), 1.0, places=5)
        print(f"  [PASS] Probs: {probs}")
    
    def test_select_action(self):
        """Should select valid action."""
        a = self.qp.select_action(0)
        self.assertIn(a, [0, 1])
        print(f"  [PASS] Action: {a}")
    
    def test_update(self):
        """Should update params."""
        old = self.qp.params[0]
        self.qp.update([0.1] * len(self.qp.params))
        self.assertNotEqual(self.qp.params[0], old)
        print("  [PASS] Update")


class TestQuantumQFunction(unittest.TestCase):
    """Test Q-function."""
    
    def setUp(self):
        self.qf = QuantumQFunction(num_states=4, num_actions=2)
    
    def test_get_set(self):
        """Should get/set Q-values."""
        self.qf.set(0, 0, 1.0)
        self.assertAlmostEqual(self.qf.get(0, 0), 1.0)
        print("  [PASS] GetSet")
    
    def test_best_action(self):
        """Should select best action."""
        self.qf.set(0, 0, 1.0)
        self.qf.set(0, 1, 0.5)
        self.assertEqual(self.qf.best_action(0), 0)
        print("  [PASS] Best")
    
    def test_max_q(self):
        """Should compute max Q."""
        self.qf.set(0, 0, 2.0)
        self.qf.set(0, 1, 1.0)
        self.assertAlmostEqual(self.qf.max_q(0), 2.0)
        print("  [PASS] MaxQ")


class TestQuantumPolicyGradient(unittest.TestCase):
    """Test policy gradient."""
    
    def setUp(self):
        self.pg = QuantumPolicyGradient(QuantumPolicy(4, 2))
    
    def test_record(self):
        """Should record trajectory."""
        self.pg.record(0, 0, 1.0)
        self.assertEqual(len(self.pg.trajectory), 1)
        print("  [PASS] Record")
    
    def test_update(self):
        """Should update policy."""
        self.pg.record(0, 0, 1.0)
        old = self.pg.policy.params[0]
        self.pg.update()
        self.assertNotEqual(self.pg.policy.params[0], old)
        print("  [PASS] PG update")


class TestQuantumQLearning(unittest.TestCase):
    """Test Q-learning."""
    
    def setUp(self):
        self.ql = QuantumQLearning(num_states=4, num_actions=2)
    
    def test_select(self):
        """Should select action."""
        a = self.ql.select_action(0)
        self.assertIn(a, [0, 1])
        print(f"  [PASS] Select: {a}")
    
    def test_update(self):
        """Should update Q-values."""
        self.ql.update(0, 0, 1.0, 1)
        self.assertNotEqual(self.ql.q.get(0, 0), 0.0)
        print("  [PASS] Q update")


class TestQuantumReinforcementLearning(unittest.TestCase):
    """Test unified RL controller."""
    
    def setUp(self):
        self.qrl = QuantumReinforcementLearning()
    
    def test_setup_pg(self):
        """Should setup policy gradient."""
        self.qrl.setup_policy_gradient(4, 2)
        self.assertIsNotNone(self.qrl.policy_grad)
        print("  [PASS] Setup PG")
    
    def test_setup_q(self):
        """Should setup Q-learning."""
        self.qrl.setup_q_learning(4, 2)
        self.assertIsNotNone(self.qrl.q_learning)
        print("  [PASS] Setup Q")
    
    def test_episode(self):
        """Should run episode."""
        self.qrl.setup_q_learning(4, 2)
        r = self.qrl.run_episode(5)
        self.assertIsInstance(r, float)
        print(f"  [PASS] Episode: {r:.2f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.qrl.setup_q_learning(4, 2)
        self.qrl.run_episode(5)
        s = self.qrl.rl_summary()
        self.assertEqual(s["episodes"], 1)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
