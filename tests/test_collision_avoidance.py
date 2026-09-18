"""
Unit tests for collision avoidance system.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbital_mechanics import OrbitalBody
from collision_avoidance import CollisionAvoidanceSystem, HazardAssessment


class TestCollisionAvoidance(unittest.TestCase):
    """Test collision avoidance logic."""
    
    def setUp(self):
        self.spacecraft = OrbitalBody(
            name="TestSC", spkid="SC1",
            a_au=1.0, e=0.0167, i_deg=0.0
        )
        self.cas = CollisionAvoidanceSystem(self.spacecraft)
        
        # Create test targets
        self.apophis = OrbitalBody(
            name="Apophis", spkid="99942",
            a_au=0.922, e=0.191, i_deg=3.33
        )
        self.bennu = OrbitalBody(
            name="Bennu", spkid="101955",
            a_au=1.126, e=0.204, i_deg=6.03
        )
        self.yr4 = OrbitalBody(
            name="2024 YR4", spkid="",
            a_au=2.516, e=0.66, i_deg=3.41
        )
    
    def test_hazard_assessment_structure(self):
        """Assessment should have all required fields."""
        result = self.cas.assess_target(self.apophis)
        self.assertIsNotNone(result.target_name)
        self.assertIn(result.risk_level, ["LOW", "MODERATE", "HIGH", "CRITICAL"])
        self.assertGreaterEqual(result.impact_probability, 0)
        self.assertLessEqual(result.impact_probability, 1)
        print(f"  [PASS] Apophis risk: {result.risk_level}, MOID: {result.moid_au:.4f} AU")
    
    def test_scan_field(self):
        """Scan multiple targets and verify sorting."""
        targets = [self.apophis, self.bennu, self.yr4]
        results = self.cas.scan_field(targets)
        
        self.assertEqual(len(results), 3)
        # Results should be sorted by risk (most dangerous first)
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
        for i in range(len(results) - 1):
            self.assertLessEqual(
                risk_order.get(results[i].risk_level, 99),
                risk_order.get(results[i+1].risk_level, 99)
            )
        print(f"  [PASS] Scan field: {len(results)} targets assessed and sorted")
    
    def test_critical_hazards_filter(self):
        """Critical hazards filter should return only high-risk items."""
        targets = [self.apophis, self.bennu, self.yr4]
        self.cas.scan_field(targets)
        critical = self.cas.get_critical_hazards()
        
        for h in critical:
            self.assertIn(h.risk_level, ["CRITICAL", "HIGH"])
        
        print(f"  [PASS] Critical hazards: {len(critical)} found")


if __name__ == '__main__':
    unittest.main(verbosity=2)
