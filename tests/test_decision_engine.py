"""
Unit tests for decision engine module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from decision_engine import MDP, State, Action, Transition, ValueIteration, PolicyEvaluator, DecisionEngine


class TestMDP(unittest.TestCase):
    """Test MDP."""
    
    def setUp(self):
        self.mdp = MDP(gamma=0.9)
        self.mdp.add_state(State("s1"))
        self.mdp.add_state(State("s2"))
        self.mdp.add_state(State("s3"))
        self.mdp.add_action(Action("a1"))
        self.mdp.add_action(Action("a2"))
        self.mdp.add_transition(Transition("s1", "a1", "s2", 1.0, 10.0))
        self.mdp.add_transition(Transition("s2", "a2", "s3", 1.0, 20.0))
    
    def test_states(self):
        """Should have states."""
        self.assertEqual(len(self.mdp.states), 3)
        print("  [PASS] States: 3")
    
    def test_transitions(self):
        """Should have transitions."""
        trans = self.mdp.get_transitions("s1", "a1")
        self.assertEqual(len(trans), 1)
        self.assertEqual(trans[0][0], "s2")
        print("  [PASS] Trans: s1->s2")
    
    def test_actions(self):
        """Should get available actions."""
        actions = self.mdp.get_available_actions("s1")
        self.assertIn("a1", actions)
        print("  [PASS] Actions: available")


class TestValueIteration(unittest.TestCase):
    """Test value iteration."""
    
    def setUp(self):
        self.mdp = MDP(gamma=0.9)
        self.mdp.add_state(State("start"))
        self.mdp.add_state(State("goal"))
        self.mdp.add_action(Action("go"))
        self.mdp.add_transition(Transition("start", "go", "goal", 1.0, 100.0))
        self.vi = ValueIteration(self.mdp)
    
    def test_solve(self):
        """Should solve MDP."""
        values = self.vi.solve()
        self.assertIn("start", values)
        self.assertIn("goal", values)
        print("  [PASS] Solve: converged")
    
    def test_values_positive(self):
        """Should have positive values."""
        values = self.vi.solve()
        self.assertGreater(values["start"], 0)
        print(f"  [PASS] Value: {values['start']:.1f}")
    
    def test_policy(self):
        """Should extract policy."""
        self.vi.solve()
        policy = self.vi.get_policy()
        self.assertEqual(policy.get("start"), "go")
        print("  [PASS] Policy: go")
    
    def test_evaluate(self):
        """Should evaluate state."""
        self.vi.solve()
        v = self.vi.evaluate_state("start")
        self.assertGreater(v, 0)
        print(f"  [PASS] Evaluate: {v:.1f}")


class TestPolicyEvaluator(unittest.TestCase):
    """Test policy evaluator."""
    
    def setUp(self):
        self.mdp = MDP(gamma=0.9)
        self.mdp.add_state(State("s1"))
        self.mdp.add_state(State("s2"))
        self.mdp.add_action(Action("a"))
        self.mdp.add_transition(Transition("s1", "a", "s2", 1.0, 50.0))
        self.evaluator = PolicyEvaluator(self.mdp)
    
    def test_evaluate(self):
        """Should evaluate policy."""
        values = self.evaluator.evaluate({"s1": "a"})
        self.assertGreater(values["s1"], 0)
        print(f"  [PASS] Eval: {values['s1']:.1f}")


class TestDecisionEngine(unittest.TestCase):
    """Test decision engine."""
    
    def setUp(self):
        self.de = DecisionEngine()
    
    def test_define_mdp(self):
        """Should define MDP."""
        self.de.define_mdp(
            [State("s1"), State("s2")],
            [Action("a")],
            [Transition("s1", "a", "s2", 1.0, 10.0)]
        )
        self.assertEqual(len(self.de.mdp.states), 2)
        print("  [PASS] Define: 2 states")
    
    def test_optimal_policy(self):
        """Should compute optimal policy."""
        self.de.define_mdp(
            [State("start"), State("goal")],
            [Action("go")],
            [Transition("start", "go", "goal", 1.0, 100.0)]
        )
        policy = self.de.compute_optimal_policy()
        self.assertEqual(policy["start"], "go")
        print("  [PASS] Optimal: go")
    
    def test_decide(self):
        """Should make decision."""
        self.de.define_mdp(
            [State("start"), State("goal")],
            [Action("go")],
            [Transition("start", "go", "goal", 1.0, 100.0)]
        )
        action = self.de.decide("start")
        self.assertEqual(action, "go")
        print("  [PASS] Decide: go")
    
    def test_summary(self):
        """Should provide summary."""
        self.de.define_mdp(
            [State("s1")],
            [Action("a")],
            []
        )
        summary = self.de.engine_summary()
        self.assertEqual(summary["states"], 1)
        print(f"  [PASS] Summary: {summary}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
