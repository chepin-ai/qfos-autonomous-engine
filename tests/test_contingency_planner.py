"""
Unit tests for contingency planner.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from contingency_planner import ContingencyPlanner, FailureMode, FailureSeverity, ContingencyPlan, ContingencyType


class TestContingencyPlanner(unittest.TestCase):
    """Test contingency planner."""
    
    def setUp(self):
        self.planner = ContingencyPlanner()
        
        for mode in ContingencyPlanner.create_standard_failure_modes():
            self.planner.add_failure_mode(mode)
        
        self.planner.add_contingency_plan(
            ContingencyPlan("prop_degrade", "thruster_degradation",
                           ContingencyType.DEGRADE,
                           ["reduce_thrust", "switch_to_backup_thruster"],
                           estimated_success_rate=0.85)
        )
        self.planner.add_contingency_plan(
            ContingencyPlan("comm_safe", "communication_loss",
                           ContingencyType.SAFE_MODE,
                           ["safe_mode_entry"],
                           estimated_success_rate=0.95)
        )
    
    def test_add_failure_mode(self):
        """Should add failure mode."""
        self.assertEqual(len(self.planner.failure_modes), 6)
        print("  [PASS] Failure modes: 6 added")
    
    def test_detect_failures(self):
        """Should detect failures."""
        status = {
            "propulsion": {"efficiency": 0.6},
            "power": {"voltage": 28.0}
        }
        failures = self.planner.detect_failures(status)
        self.assertGreater(len(failures), 0)
        print(f"  [PASS] Detected: {len(failures)} failures")
    
    def test_assess_severity(self):
        """Should assess severity."""
        failures = [
            FailureMode("test", "sys", FailureSeverity.MAJOR, "test"),
            FailureMode("test2", "sys2", FailureSeverity.MINOR, "test")
        ]
        sev = self.planner.assess_severity(failures)
        self.assertEqual(sev, FailureSeverity.MAJOR)
        print(f"  [PASS] Severity: {sev.value}")
    
    def test_select_contingency(self):
        """Should select contingency."""
        failures = [
            FailureMode("thruster_degradation", "propulsion",
                       FailureSeverity.MINOR, "test")
        ]
        plan = self.planner.select_contingency(failures)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.response_type, ContingencyType.DEGRADE)
        print(f"  [PASS] Contingency: {plan.name}")
    
    def test_abort_decision_tree(self):
        """Should make abort decision."""
        failures = [
            FailureMode("thermal_runaway", "thermal",
                       FailureSeverity.CATASTROPHIC, "test")
        ]
        decision = self.planner.abort_decision_tree(failures)
        self.assertEqual(decision["decision"], "ABORT_IMMEDIATE")
        print(f"  [PASS] Decision: {decision['decision']}")
    
    def test_abort_crew_safety(self):
        """Should prioritize crew safety."""
        failures = [
            FailureMode("power_bus_anomaly", "power",
                       FailureSeverity.CRITICAL, "test")
        ]
        decision = self.planner.abort_decision_tree(failures, crew_safety=True)
        self.assertEqual(decision["decision"], "ABORT_IMMEDIATE")
        print("  [PASS] Crew safety: ABORT_IMMEDIATE")
    
    def test_safe_mode_entry(self):
        """Should generate safe mode sequence."""
        actions = self.planner.safe_mode_entry("comm_loss")
        self.assertGreater(len(actions), 3)
        print(f"  [PASS] Safe mode: {len(actions)} actions")
    
    def test_reconfigure(self):
        """Should reconfigure for redundancy."""
        plan = self.planner.reconfigure_for_redundancy("star_tracker_a", "star_tracker_b")
        self.assertEqual(plan["switch_to"], "star_tracker_b")
        print("  [PASS] Reconfigure: star_tracker_a -> star_tracker_b")
    
    def test_contingency_summary(self):
        """Should provide summary."""
        summary = self.planner.contingency_summary()
        self.assertIn("failure_modes_tracked", summary)
        print(f"  [PASS] Summary: {summary['failure_modes_tracked']} modes")
    
    def test_standard_failure_modes(self):
        """Should create standard modes."""
        modes = ContingencyPlanner.create_standard_failure_modes()
        self.assertEqual(len(modes), 6)
        print(f"  [PASS] Standard modes: {len(modes)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
