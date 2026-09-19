"""
Unit tests for cognitive engine module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cognitive_engine import CognitiveEngine, Belief, Desire, Intention


class TestCognitiveEngine(unittest.TestCase):
    """Test cognitive engine."""
    
    def setUp(self):
        self.ce = CognitiveEngine()
        self.ce.add_belief(Belief("b1", "spacecraft is operational", 0.95))
        self.ce.add_belief(Belief("b2", "fuel level is 80%", 0.9))
        self.ce.add_desire(Desire("d1", "reach Mars orbit", priority=1))
        self.ce.add_desire(Desire("d2", "transmit telemetry", priority=2))
    
    def test_add_belief(self):
        """Should add belief."""
        self.assertEqual(len(self.ce.beliefs), 2)
        print("  [PASS] Beliefs: 2 added")
    
    def test_add_desire(self):
        """Should add desire."""
        self.assertEqual(len(self.ce.desires), 2)
        print("  [PASS] Desires: 2 added")
    
    def test_revoke_belief(self):
        """Should revoke belief."""
        self.ce.revoke_belief("b1")
        self.assertNotIn("b1", self.ce.beliefs)
        print("  [PASS] Revoked: b1")
    
    def test_get_beliefs_about(self):
        """Should get beliefs about topic."""
        beliefs = self.ce.get_beliefs_about("fuel")
        self.assertEqual(len(beliefs), 1)
        print(f"  [PASS] Beliefs about fuel: {len(beliefs)}")
    
    def test_assess_situation_nominal(self):
        """Should assess nominal situation."""
        assessment = self.ce.assess_situation()
        self.assertEqual(assessment["situation"], "nominal")
        print(f"  [PASS] Situation: {assessment['situation']}")
    
    def test_assess_situation_degraded(self):
        """Should detect degraded situation."""
        self.ce.add_belief(Belief("b3", "thruster anomaly detected", 0.95))
        assessment = self.ce.assess_situation()
        self.assertEqual(assessment["situation"], "degraded")
        print(f"  [PASS] Situation: {assessment['situation']}")
    
    def test_select_desires(self):
        """Should select desires by priority."""
        desires = self.ce.select_desires()
        self.assertEqual(desires[0].id, "d1")
        print(f"  [PASS] Selected: {desires[0].id} first")
    
    def test_form_intention(self):
        """Should form intention."""
        desire = self.ce.desires["d1"]
        intention = self.ce.form_intention(desire, ["burn1", "coast", "burn2"])
        self.assertIsNotNone(intention)
        self.assertEqual(intention.desire_id, "d1")
        print(f"  [PASS] Intention: {intention.id}")
    
    def test_execute_step(self):
        """Should execute intention step."""
        desire = self.ce.desires["d1"]
        intention = self.ce.form_intention(desire, ["step1", "step2"])
        result = self.ce.execute_intention_step(intention.id)
        self.assertTrue(result["success"])
        self.assertEqual(result["step_executed"], "step1")
        print(f"  [PASS] Step: {result['step_executed']}")
    
    def test_execute_complete(self):
        """Should complete intention."""
        desire = self.ce.desires["d1"]
        intention = self.ce.form_intention(desire, ["step1"])
        self.ce.execute_intention_step(intention.id)
        result = self.ce.execute_intention_step(intention.id)
        self.assertEqual(result["status"], "completed")
        print("  [PASS] Completed")
    
    def test_revise_plan(self):
        """Should revise plan."""
        desire = self.ce.desires["d1"]
        intention = self.ce.form_intention(desire, ["old1", "old2"])
        result = self.ce.revise_plan(intention.id, ["new1", "new2", "new3"])
        self.assertTrue(result)
        self.assertEqual(len(self.ce.intentions[intention.id].plan_steps), 3)
        print("  [PASS] Revised: 3 steps")
    
    def test_detect_conflict(self):
        """Should detect conflicts."""
        d1 = Desire("d_conflict1", "goal A", priority=1)
        d2 = Desire("d_conflict2", "goal B", priority=1)
        self.ce.add_desire(d1)
        self.ce.add_desire(d2)
        self.ce.form_intention(d1, ["action1"])
        self.ce.form_intention(d2, ["action2"])
        conflicts = self.ce.detect_conflict()
        self.assertGreater(len(conflicts), 0)
        print(f"  [PASS] Conflicts: {len(conflicts)}")
    
    def test_cognitive_summary(self):
        """Should provide summary."""
        summary = self.ce.cognitive_summary()
        self.assertEqual(summary["beliefs"], 2)
        self.assertEqual(summary["desires"], 2)
        print(f"  [PASS] Summary: {summary['beliefs']} beliefs, {summary['desires']} desires")


if __name__ == '__main__':
    unittest.main(verbosity=2)
