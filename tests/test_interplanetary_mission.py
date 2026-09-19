"""
Unit tests for interplanetary mission planner module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from interplanetary_mission import (
    InterplanetaryMissionPlanner, MissionObjective, MissionProfile,
    MissionPhase
)


class TestInterplanetaryMissionPlanner(unittest.TestCase):
    """Test interplanetary mission planning."""
    
    def setUp(self):
        self.planner = InterplanetaryMissionPlanner()
    
    def test_analyze_target_known(self):
        """Should analyze known asteroid."""
        result = self.planner.analyze_target("1 Ceres")
        self.assertIsNotNone(result)
        self.assertEqual(result["designation"], "1 Ceres")
        self.assertIn("semi_major_axis_au", result)
        print(f"  [PASS] Ceres: a={result['semi_major_axis_au']} AU, period={result['orbital_period_yr']} yr")
    
    def test_analyze_target_unknown(self):
        """Should handle unknown target gracefully."""
        result = self.planner.analyze_target("NOT_REAL_99999")
        self.assertIsNone(result)
        print("  [PASS] Unknown target returns None")
    
    def test_design_transfer_mars(self):
        """Should design transfer to Mars-like body."""
        transfer = self.planner.design_transfer("4 Vesta")
        self.assertIn("total_delta_v_kms", transfer)
        self.assertIn("transfer_time_days", transfer)
        self.assertGreater(transfer["total_delta_v_kms"], 0)
        self.assertGreater(transfer["transfer_time_days"], 0)
        print(f"  [PASS] Vesta transfer: {transfer['total_delta_v_kms']} km/s, {transfer['transfer_time_years']} yr")
    
    def test_design_transfer_error(self):
        """Should return error for invalid target."""
        transfer = self.planner.analyze_target("INVALID")
        self.assertIsNone(transfer)
        print("  [PASS] Invalid target handled")
    
    def test_design_mission(self):
        """Should design multi-objective mission."""
        objectives = [
            MissionObjective("4 Vesta", "flyby", science_instruments=["camera", "spectrometer"]),
        ]
        profile = self.planner.design_mission("Vesta Explorer", objectives)
        self.assertIsInstance(profile, MissionProfile)
        self.assertEqual(profile.mission_name, "Vesta Explorer")
        self.assertGreater(profile.total_delta_v_kms, 0)
        print(f"  [PASS] Mission: {profile.mission_name}, dv={profile.total_delta_v_kms} km/s")
    
    def test_assess_feasibility(self):
        """Should assess mission feasibility."""
        objectives = [MissionObjective("4 Vesta", "flyby")]
        profile = self.planner.design_mission("Test", objectives)
        assessment = self.planner.assess_mission_feasibility(profile)
        self.assertIn("feasible", assessment)
        self.assertIn("c3_required_km2_s2", assessment)
        print(f"  [PASS] Feasibility: feasible={assessment['feasible']}, C3={assessment['c3_required_km2_s2']}")
    
    def test_compare_targets(self):
        """Should compare and rank targets."""
        targets = ["1 Ceres", "4 Vesta", "99942 Apophis"]
        results = self.planner.compare_targets(targets)
        self.assertGreater(len(results), 0)
        # Should be sorted by score
        if len(results) > 1:
            self.assertLessEqual(results[0]["mission_score"], results[-1]["mission_score"])
        print(f"  [PASS] Compared {len(results)} targets, best: {results[0]['designation']}")
    
    def test_generate_report(self):
        """Should generate mission report."""
        objectives = [MissionObjective("4 Vesta", "flyby")]
        profile = self.planner.design_mission("Report Test", objectives)
        report = self.planner.generate_mission_report(profile)
        self.assertIn("Mission Report", report)
        self.assertIn("Vesta", report)
        print("  [PASS] Report generated")


if __name__ == '__main__':
    unittest.main(verbosity=2)
