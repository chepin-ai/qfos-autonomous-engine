"""
Unit tests for radiation environment module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from radiation_environment import RadiationEnvironment, ParticleType


class TestRadiationEnvironment(unittest.TestCase):
    """Test radiation environment."""
    
    def setUp(self):
        self.env = RadiationEnvironment(
            altitude_km=400.0,
            inclination_deg=51.6,
            shielding_mm_al=2.0
        )
    
    def test_attenuation_factor(self):
        """Should compute attenuation."""
        atten = self.env._attenuation_factor(ParticleType.ELECTRON)
        self.assertGreater(atten, 0.0)
        self.assertLess(atten, 1.0)
        print(f"  [PASS] Attenuation: electron={atten:.3f}")
    
    def test_belt_dose_rate(self):
        """Should compute belt dose rate."""
        rate = self.env._belt_dose_rate()
        self.assertGreaterEqual(rate, 0.0)
        print(f"  [PASS] Belt dose @400km: {rate:.6f} krad/day")
    
    def test_gcr_dose_rate(self):
        """Should compute GCR dose rate."""
        rate_min = self.env._gcr_dose_rate(solar_maximum=False)
        rate_max = self.env._gcr_dose_rate(solar_maximum=True)
        self.assertGreater(rate_min, rate_max)  # Less GCR at solar max
        print(f"  [PASS] GCR: min={rate_min:.6f}, max={rate_max:.6f} krad/day")
    
    def test_mission_total_dose(self):
        """Should compute mission total dose."""
        dose = self.env.mission_total_dose(mission_duration_days=365.0)
        self.assertGreater(dose.total_dose_krad, 0.0)
        self.assertIn("trapped_radiation", dose.component_doses)
        print(f"  [PASS] Annual dose: {dose.total_dose_krad:.4f} krad")
    
    def test_shielding_effect(self):
        """More shielding should reduce dose."""
        env_thin = RadiationEnvironment(altitude_km=400.0, shielding_mm_al=1.0)
        env_thick = RadiationEnvironment(altitude_km=400.0, shielding_mm_al=5.0)
        
        dose_thin = env_thin.mission_total_dose(365.0)
        dose_thick = env_thick.mission_total_dose(365.0)
        
        self.assertGreater(dose_thin.total_dose_krad, dose_thick.total_dose_krad)
        print(f"  [PASS] Shielding: 1mm={dose_thin.total_dose_krad:.4f}, 5mm={dose_thick.total_dose_krad:.4f} krad")
    
    def test_shielding_optimization(self):
        """Should find minimum shielding."""
        result = self.env.shielding_optimization(
            target_dose_krad=50.0,
            mission_days=365.0
        )
        self.assertIn("required_shielding_mm", result)
        print(f"  [PASS] Optimal shielding: {result['required_shielding_mm']} mm")
    
    def test_component_tolerance(self):
        """Should return component tolerances."""
        tol_cmos = self.env.component_radiation_tolerance("commercial_cmos")
        tol_rad = self.env.component_radiation_tolerance("radiation_hardened")
        self.assertGreater(tol_rad, tol_cmos)
        print(f"  [PASS] Tolerance: CMOS={tol_cmos}, RAD-HARD={tol_rad} krad")
    
    def test_survivability(self):
        """Should assess component survivability."""
        components = [
            {"name": "CPU", "type": "radiation_tolerant", "shielding_mm": 5.0},
            {"name": "Solar", "type": "solar_cell_gaas", "shielding_mm": 0.1}
        ]
        result = self.env.survivability_assessment(365.0, components)
        self.assertEqual(len(result["components"]), 2)
        print(f"  [PASS] Survivability: {result['all_survive']}")
    
    def test_inner_belt_higher_dose(self):
        """Inner belt should have higher dose."""
        env_inner = RadiationEnvironment(altitude_km=3000.0, shielding_mm_al=2.0)
        env_leo = RadiationEnvironment(altitude_km=400.0, shielding_mm_al=2.0)
        
        dose_inner = env_inner.mission_total_dose(30.0)
        dose_leo = env_leo.mission_total_dose(30.0)
        
        self.assertGreater(dose_inner.total_dose_krad, dose_leo.total_dose_krad)
        print(f"  [PASS] Inner belt: {dose_inner.total_dose_krad:.4f} > LEO: {dose_leo.total_dose_krad:.4f} krad/30d")


if __name__ == '__main__':
    unittest.main(verbosity=2)
