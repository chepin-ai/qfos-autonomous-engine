"""
Unit tests for RL trainer module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rl_trainer import (ReplayBuffer, Experience, QLearningAgent,
                        PolicyGradientAgent, RLTrainer)


class TestReplayBuffer(unittest.TestCase):
    """Test replay buffer."""
    
    def setUp(self):
        self.buf = ReplayBuffer(capacity=5)
    
    def test_push(self):
        """Should push experience."""
        self.buf.push(Experience("s", "a", 1.0, "s2"))
        self.assertEqual(len(self.buf), 1)
        print("  [PASS] Push: 1")
    
    def test_sample(self):
        """Should sample batch."""
        for i in range(5):
            self.buf.push(Experience(f"s{i}", "a", float(i), f"s{i+1}"))
        batch = self.buf.sample(3)
        self.assertEqual(len(batch), 3)
        print(f"  [PASS] Sample: {len(batch)}")
    
    def test_capacity(self):
        """Should respect capacity."""
        for i in range(10):
            self.buf.push(Experience("s", "a", float(i), "s2"))
        self.assertEqual(len(self.buf), 5)
        print("  [PASS] Capacity: 5")
    
    def test_ready(self):
        """Should check ready."""
        self.assertFalse(self.buf.is_ready(3))
        for i in range(5):
            self.buf.push(Experience("s", "a", float(i), "s2"))
        self.assertTrue(self.buf.is_ready(3))
        print("  [PASS] Ready: True")


class TestQLearningAgent(unittest.TestCase):
    """Test Q-learning agent."""
    
    def setUp(self):
        self.agent = QLearningAgent(["left", "right"], seed=42)
    
    def test_choose_action(self):
        """Should choose action."""
        action = self.agent.choose_action("s1")
        self.assertIn(action, ["left", "right"])
        print(f"  [PASS] Choose: {action}")
    
    def test_learn(self):
        """Should update Q-value."""
        self.agent.learn("s1", "right", 10.0, "s2")
        self.assertGreater(self.agent.get_q("s1", "right"), 0)
        print(f"  [PASS] Learn: Q={self.agent.get_q('s1', 'right'):.2f}")
    
    def test_q_improves(self):
        """Q should improve with positive reward."""
        initial = self.agent.get_q("s1", "right")
        for _ in range(10):
            self.agent.learn("s1", "right", 10.0, "s2")
        self.assertGreater(self.agent.get_q("s1", "right"), initial)
        print(f"  [PASS] Improve: {initial:.2f} -> {self.agent.get_q('s1', 'right'):.2f}")
    
    def test_policy(self):
        """Should extract policy."""
        self.agent.learn("s1", "right", 10.0, "s2")
        policy = self.agent.get_policy()
        self.assertIn("s1", policy)
        print(f"  [PASS] Policy: {policy['s1']}")
    
    def test_value_function(self):
        """Should get value function."""
        self.agent.learn("s1", "right", 10.0, "s2")
        values = self.agent.get_value_function()
        self.assertIn("s1", values)
        print(f"  [PASS] Values: {values['s1']:.2f}")


class TestPolicyGradientAgent(unittest.TestCase):
    """Test policy gradient agent."""
    
    def setUp(self):
        self.agent = PolicyGradientAgent(["left", "right"], seed=42)
    
    def test_choose_action(self):
        """Should choose action."""
        action = self.agent.choose_action("s1")
        self.assertIn(action, ["left", "right"])
        print(f"  [PASS] Choose: {action}")
    
    def test_record(self):
        """Should record trajectory."""
        self.agent.record("s1", "right", 10.0)
        self.assertEqual(len(self.agent.trajectory), 1)
        print("  [PASS] Record: 1 step")
    
    def test_update(self):
        """Should update policy."""
        self.agent.record("s1", "right", 10.0)
        self.agent.update()
        self.assertEqual(len(self.agent.trajectory), 0)
        print("  [PASS] Update: cleared")
    
    def test_policy_probs(self):
        """Should get probabilities."""
        probs = self.agent.get_policy_probs("s1")
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=5)
        print(f"  [PASS] Probs: sum={sum(probs.values()):.3f}")


class TestRLTrainer(unittest.TestCase):
    """Test RL trainer."""
    
    def setUp(self):
        self.trainer = RLTrainer()
    
    def test_create_q_agent(self):
        """Should create Q-agent."""
        agent = self.trainer.create_q_agent(["left", "right"])
        self.assertIsNotNone(agent)
        print("  [PASS] Create Q: ok")
    
    def test_create_pg_agent(self):
        """Should create PG agent."""
        agent = self.trainer.create_pg_agent(["left", "right"])
        self.assertIsNotNone(agent)
        print("  [PASS] Create PG: ok")
    
    def test_train_q(self):
        """Should train Q-learning."""
        self.trainer.create_q_agent(["left", "right"], epsilon=0.5)
        
        def env_step(state, action):
            if action == "right":
                return "goal", 10.0, True
            return "start", -1.0, False
        
        values = self.trainer.train_q_learning(env_step, "start", episodes=50, max_steps=10)
        self.assertIn("start", values)
        print(f"  [PASS] Train Q: {len(values)} states")
    
    def test_train_pg(self):
        """Should train policy gradient."""
        self.trainer.create_pg_agent(["left", "right"])
        
        def env_step(state, action):
            if action == "right":
                return "goal", 10.0, True
            return "start", -1.0, False
        
        policy = self.trainer.train_policy_gradient(env_step, "start", episodes=50, max_steps=10)
        self.assertGreater(len(policy), 0)
        print(f"  [PASS] Train PG: {len(policy)} states")
    
    def test_stats(self):
        """Should provide stats."""
        self.trainer.create_q_agent(["left", "right"], epsilon=0.5)
        
        def env_step(state, action):
            return "s", 1.0, True
        
        self.trainer.train_q_learning(env_step, "s", episodes=10, max_steps=5)
        stats = self.trainer.get_training_stats()
        self.assertEqual(stats["episodes"], 10)
        print(f"  [PASS] Stats: {stats['episodes']} episodes")
    
    def test_summary(self):
        """Should provide summary."""
        self.trainer.create_q_agent(["left", "right"])
        summary = self.trainer.trainer_summary()
        self.assertTrue(summary["q_agent"])
        print(f"  [PASS] Summary: {summary}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
