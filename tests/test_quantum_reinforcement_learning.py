"""
Unit tests for quantum reinforcement learning module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_reinforcement_learning import (QuantumPolicy,
                                             QuantumPolicyGradient,
                                             QuantumRLAgent,
                                             QuantumReinforcementLearning)


class TestQuantumPolicy(unittest.TestCase):
    """Test quantum policy."""
    
    def setUp(self):
        self.policy = QuantumPolicy(4, 2)
    
    def test_rotation(self):
        """Should create rotation gate."""
        m = self.policy.rotation_gate(math.pi / 2)
        self.assertEqual(len(m), 2)
        print("  [PASS] Rot")
    
    def test_evaluate(self):
        """Should evaluate."""
        probs = self.policy.evaluate([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(probs), 2)
        self.assertAlmostEqual(sum(probs), 1.0, places=5)
        print(f"  [PASS] Eval: {probs}")
    
    def test_select(self):
        """Should select action."""
        a = self.policy.select_action([0.5, 0.5, 0.5, 0.5])
        self.assertIn(a, [0, 1])
        print(f"  [PASS] Select: {a}")


class TestQuantumPolicyGradient(unittest.TestCase):
    """Test policy gradient."""
    
    def setUp(self):
        self.pg = QuantumPolicyGradient(QuantumPolicy(4, 2))
    
    def test_store(self):
        """Should store transition."""
        self.pg.store_transition(-0.5, 1.0)
        self.assertEqual(len(self.pg.log_probs), 1)
        print("  [PASS] Store")
    
    def test_returns(self):
        """Should compute returns."""
        self.pg.store_transition(-0.5, 1.0)
        self.pg.store_transition(-0.3, 0.5)
        r = self.pg.compute_returns(0.9)
        self.assertEqual(len(r), 2)
        print(f"  [PASS] Returns: {r}")
    
    def test_update(self):
        """Should update."""
        self.pg.store_transition(-0.5, 1.0)
        self.pg.update()
        self.assertEqual(len(self.pg.log_probs), 0)
        print("  [PASS] Update")


class TestQuantumRLAgent(unittest.TestCase):
    """Test quantum RL agent."""
    
    def setUp(self):
        self.agent = QuantumRLAgent(4, 2)
    
    def test_act(self):
        """Should act."""
        a = self.agent.act([0.5, 0.5, 0.5, 0.5])
        self.assertIn(a, [0, 1])
        print(f"  [PASS] Act: {a}")
    
    def test_step(self):
        """Should step."""
        self.agent.step([0.5, 0.5, 0.5, 0.5], 0, 1.0)
        self.assertEqual(len(self.agent.optimizer.rewards), 1)
        print("  [PASS] Step")
    
    def test_episode(self):
        """Should finish episode."""
        self.agent.step([0.5, 0.5, 0.5, 0.5], 0, 1.0)
        self.agent.finish_episode()
        self.assertEqual(len(self.agent.episode_rewards), 1)
        print("  [PASS] Episode")
    
    def test_mean(self):
        """Should compute mean."""
        self.agent.step([0.5, 0.5, 0.5, 0.5], 0, 1.0)
        self.agent.finish_episode()
        m = self.agent.mean_reward()
        self.assertIsNotNone(m)
        print(f"  [PASS] Mean: {m:.4f}")


class TestQuantumReinforcementLearning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qrl = QuantumReinforcementLearning()
    
    def test_build(self):
        """Should build agent."""
        self.qrl.build_agent(4, 2)
        self.assertIsNotNone(self.qrl.agent)
        print("  [PASS] Build")
    
    def test_train(self):
        """Should train."""
        def env(action):
            return [float(action) * 0.5] * 4, float(action)
        
        r = self.qrl.train(env, 5)
        self.assertIn("mean_reward", r)
        print(f"  [PASS] Train: mean={r['mean_reward']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        def env(action):
            return [0.0] * 4, 1.0
        
        self.qrl.train(env, 3)
        s = self.qrl.qrl_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
