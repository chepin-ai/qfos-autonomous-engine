"""
Unit tests for mission integrator module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mission_integrator import MissionIntegrator, MissionPhase, SubsystemHandle


class TestMissionIntegrator(unittest.TestCase):
    """Test mission integrator."""
    
    def setUp(self):
        self.mi = MissionIntegrator("Test Mission")
        self.mi.register_subsystem(SubsystemHandle("nav", "1.0", health_percent=100.0,
                                                   commands_accepted=["align", "burn"]))
        self.mi.register_subsystem(SubsystemHandle("power", "1.0", health_percent=100.0))
        self.mi.register_subsystem(SubsystemHandle("comm", "1.0", health_percent=100.0))
    
    def test_register_subsystem(self):
        """Should register subsystem."""
        self.assertEqual(len(self.mi.subsystems), 3)
        print("  [PASS] Subsystems: 3 registered")
    
    def test_update_subsystem(self):
        """Should update subsystem."""
        self.mi.update_subsystem("nav", health_percent=95.0, status="nominal")
        self.assertEqual(self.mi.subsystems["nav"].health_percent, 95.0)
        print("  [PASS] Update: nav health=95%")
    
    def test_check_dependencies(self):
        """Should check dependencies."""
        self.mi.register_subsystem(SubsystemHandle("gnc", "1.0"),
                                   depends_on=["nav", "power"])
        ok, missing = self.mi.check_dependencies("gnc")
        self.assertTrue(ok)
        print("  [PASS] Dependencies: healthy")
    
    def test_check_dependencies_missing(self):
        """Should detect missing dependency."""
        self.mi.register_subsystem(SubsystemHandle("camera", "1.0"),
                                   depends_on=["imager"])
        ok, missing = self.mi.check_dependencies("camera")
        self.assertFalse(ok)
        print(f"  [PASS] Missing: {missing}")
    
    def test_advance_phase(self):
        """Should advance phase."""
        result = self.mi.advance_phase()
        self.assertTrue(result)
        self.assertEqual(self.mi.phase, MissionPhase.LAUNCH)
        print(f"  [PASS] Phase: {self.mi.phase.value}")
    
    def test_advance_blocked(self):
        """Should block advance if unhealthy."""
        self.mi.update_subsystem("nav", health_percent=10.0)
        result = self.mi.advance_phase(MissionPhase.CRUISE)
        self.assertFalse(result)
        print("  [PASS] Advance blocked: nav unhealthy")
    
    def test_execute_command(self):
        """Should execute command."""
        result = self.mi.execute_command("nav", "align", {"target": "mars"})
        self.assertTrue(result["success"])
        print("  [PASS] Command: nav.align executed")
    
    def test_execute_unknown_subsystem(self):
        """Should fail for unknown subsystem."""
        result = self.mi.execute_command("unknown", "cmd")
        self.assertFalse(result["success"])
        print("  [PASS] Unknown: rejected")
    
    def test_goals(self):
        """Should manage goals."""
        self.mi.add_goal("orbit_insertion")
        self.mi.complete_goal("orbit_insertion")
        self.assertIn("orbit_insertion", self.mi.completed_goals)
        print("  [PASS] Goal: completed")
    
    def test_mission_progress(self):
        """Should report progress."""
        self.mi.add_goal("a")
        self.mi.add_goal("b")
        self.mi.complete_goal("a")
        progress = self.mi.get_mission_progress()
        self.assertEqual(progress["goals_completed"], 1)
        self.assertEqual(progress["progress_percent"], 50.0)
        print(f"  [PASS] Progress: {progress['progress_percent']}%")
    
    def test_cross_subsystem_check(self):
        """Should detect cross-subsystem issues."""
        self.mi.update_subsystem("power", telemetry={"power_w": 6000.0})
        issues = self.mi.cross_subsystem_check()
        self.assertGreater(len(issues), 0)
        print(f"  [PASS] Issues: {len(issues)} found")
    
    def test_mission_report(self):
        """Should generate report."""
        report = self.mi.mission_report()
        self.assertIn("progress", report)
        self.assertIn("subsystems", report)
        print("  [PASS] Report: generated")


if __name__ == '__main__':
    unittest.main(verbosity=2)
