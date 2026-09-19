"""
Unit tests for autonomous decision engine.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from decision_engine import DecisionEngine, MissionState, ActionPriority, SystemStatus, Action


class TestDecisionEngine(unittest.TestCase):
    """Test decision engine."""
    
    def setUp(self):
        self.engine = DecisionEngine()
        self.engine.add_system(SystemStatus("propulsion", health_percent=100.0))
        self.engine.add_system(SystemStatus("power", health_percent=100.0))
        self.engine.add_system(SystemStatus("comm", health_percent=100.0))
        
        self.engine.add_action(Action("burn", ActionPriority.HIGH,
                                     preconditions=["propulsion:health_percent>50"],
                                     effects={"propulsion": -5.0}))
        self.engine.add_action(Action("transmit", ActionPriority.MEDIUM,
                                     preconditions=["comm:health_percent>30"],
                                     effects={"comm": -2.0}))
        self.engine.add_action(Action("safe_mode", ActionPriority.CRITICAL,
                                     effects={"power": 10.0}))
    
    def test_add_system(self):
        """Should add system."""
        self.assertEqual(len(self.engine.systems), 3)
        print("  [PASS] Systems: 3 added")
    
    def test_add_action(self):
        """Should add action."""
        self.assertEqual(len(self.engine.actions), 3)
        print("  [PASS] Actions: 3 added")
    
    def test_check_preconditions(self):
        """Should check preconditions."""
        action = self.engine.actions["burn"]
        met, missing = self.engine.check_preconditions(action)
        self.assertTrue(met)
        print("  [PASS] Preconditions: met")
    
    def test_check_preconditions_fail(self):
        """Should detect failed preconditions."""
        self.engine.update_system("propulsion", health_percent=30.0)
        action = self.engine.actions["burn"]
        met, missing = self.engine.check_preconditions(action)
        self.assertFalse(met)
        print(f"  [PASS] Preconditions: failed, missing={missing}")
    
    def test_score_action(self):
        """Should score action."""
        action = self.engine.actions["burn"]
        score = self.engine.score_action(action)
        self.assertGreater(score, 0.0)
        print(f"  [PASS] Score: {score}")
    
    def test_select_action(self):
        """Should select best action."""
        action = self.engine.select_action()
        self.assertIsNotNone(action)
        print(f"  [PASS] Selected: {action.name}")
    
    def test_generate_plan(self):
        """Should generate plan."""
        plan = self.engine.generate_plan(["complete_mission"])
        self.assertGreater(len(plan), 0)
        print(f"  [PASS] Plan: {len(plan)} actions")
    
    def test_execute_action(self):
        """Should execute action."""
        result = self.engine.execute_action("transmit")
        self.assertTrue(result["success"])
        print("  [PASS] Executed: transmit")
    
    def test_mission_state_degraded(self):
        """Should detect degraded state."""
        self.engine.update_system("propulsion", health_percent=50.0)
        self.engine.update_system("power", health_percent=50.0)
        self.assertEqual(self.engine.state, MissionState.DEGRADED)
        print(f"  [PASS] State: {self.engine.state.value}")
    
    def test_mission_summary(self):
        """Should provide summary."""
        summary = self.engine.mission_summary()
        self.assertIn("systems_monitored", summary)
        print(f"  [PASS] Summary: {summary['systems_monitored']} systems")


if __name__ == '__main__':
    unittest.main(verbosity=2)
