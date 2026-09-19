"""
Unit tests for delta-V budget module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from delta_v_budget import DeltaVBudget, DeltaVItem, MissionPhase


class TestDeltaVBudget(unittest.TestCase):
    """Test delta-V budget."""
    
    def test_item_with_margin(self):
        """Should compute item with margin."""
        item = DeltaVItem("test", 100.0, 10.0)
        self.assertAlmostEqual(item.total_with_margin(), 110.0, delta=0.01)
        print("  [PASS] Item margin: 100 + 10% = 110")
    
    def test_phase_total(self):
        """Should compute phase total."""
        phase = MissionPhase("test", items=[
            DeltaVItem("a", 100.0, 10.0),
            DeltaVItem("b", 50.0, 5.0)
        ])
        self.assertAlmostEqual(phase.phase_total_ms(), 110.0 + 52.5, delta=0.1)
        print(f"  [PASS] Phase total: {phase.phase_total_ms():.1f} m/s")
    
    def test_budget_total(self):
        """Should compute mission total."""
        budget = DeltaVBudget(dry_mass_kg=1000.0, isp_seconds=300.0)
        budget.add_phase(MissionPhase("sk", items=[
            DeltaVItem("drag", 50.0, 10.0)
        ]))
        
        total = budget.total_delta_v_ms()
        self.assertGreater(total, 50.0)
        print(f"  [PASS] Total: {total:.1f} m/s")
    
    def test_propellant_mass(self):
        """Should compute propellant mass."""
        budget = DeltaVBudget(dry_mass_kg=1000.0, isp_seconds=300.0)
        budget.add_phase(MissionPhase("sk", items=[
            DeltaVItem("drag", 100.0, 0.0)
        ]))
        
        prop = budget.propellant_mass_kg()
        self.assertGreater(prop, 0.0)
        print(f"  [PASS] Propellant: {prop:.2f} kg for 100 m/s")
    
    def test_leo_mission(self):
        """Should create LEO mission budget."""
        budget = DeltaVBudget.create_leo_mission(
            dry_mass_kg=500.0, altitude_km=400.0, mission_years=3.0
        )
        summary = budget.budget_summary()
        self.assertGreater(summary["total_with_contingency_ms"], 0.0)
        self.assertGreater(summary["propellant_mass_kg"], 0.0)
        print(f"  [PASS] LEO mission: {summary['total_with_contingency_ms']:.1f} m/s, {summary['propellant_mass_kg']:.2f} kg")
    
    def test_geo_mission(self):
        """Should create GEO mission budget."""
        budget = DeltaVBudget.create_geo_mission(dry_mass_kg=2000.0)
        summary = budget.budget_summary()
        self.assertGreater(len(summary["phases"]), 2)
        self.assertGreater(summary["total_with_contingency_ms"], 1000.0)
        print(f"  [PASS] GEO mission: {summary['total_with_contingency_ms']:.1f} m/s")
    
    def test_orbit_transfer(self):
        """Should add orbit transfer."""
        budget = DeltaVBudget()
        budget.add_orbit_transfer(200.0, 35786.0)
        self.assertGreater(budget.total_nominal_ms(), 3900.0)
        print(f"  [PASS] LEO->GEO transfer: {budget.total_nominal_ms():.1f} m/s")
    
    def test_summary_structure(self):
        """Should have complete summary."""
        budget = DeltaVBudget.create_leo_mission()
        summary = budget.budget_summary()
        required_keys = ["phases", "total_nominal_ms", "total_with_contingency_ms",
                        "dry_mass_kg", "propellant_mass_kg", "wet_mass_kg", "propellant_fraction"]
        for key in required_keys:
            self.assertIn(key, summary)
        print("  [PASS] Summary structure complete")


if __name__ == '__main__':
    unittest.main(verbosity=2)
