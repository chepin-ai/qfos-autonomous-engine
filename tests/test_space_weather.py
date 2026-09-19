"""
Unit tests for space weather module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from space_weather import SpaceWeatherModel, GeomagneticIndices, RadiationRiskLevel


class TestSpaceWeatherModel(unittest.TestCase):
    """Test space weather model."""
    
    def setUp(self):
        self.model = SpaceWeatherModel()
    
    def test_indices(self):
        """Should get geomagnetic indices."""
        indices = self.model.get_indices()
        self.assertGreaterEqual(indices.kp, 0.0)
        self.assertLessEqual(indices.kp, 9.0)
        print(f"  [PASS] Indices: Kp={indices.kp}, Ap={indices.ap}, Dst={indices.dst_nt}")
    
    def test_storm_level(self):
        """Should classify storm level."""
        quiet = GeomagneticIndices(kp=1, ap=3, dst_nt=-5)
        self.assertEqual(quiet.storm_level(), "quiet")
        
        severe = GeomagneticIndices(kp=8, ap=150, dst_nt=-250)
        self.assertEqual(severe.storm_level(), "severe")
        print("  [PASS] Storm levels")
    
    def test_radiation_at_altitude(self):
        """Should estimate radiation environment."""
        rad = self.model.radiation_at_altitude(altitude_km=400.0)
        self.assertGreater(rad.electron_flux_cm2_s, 0.0)
        self.assertGreater(rad.proton_flux_cm2_s, 0.0)
        print(f"  [PASS] Radiation @400km: e-flux={rad.electron_flux_cm2_s:.1e}, p-flux={rad.proton_flux_cm2_s:.1e}")
    
    def test_inner_belt(self):
        """Inner belt should have high proton flux."""
        rad = self.model.radiation_at_altitude(altitude_km=500.0)
        self.assertGreater(rad.proton_flux_cm2_s, 1000.0)
        print(f"  [PASS] Inner belt: p={rad.proton_flux_cm2_s:.0f}, e={rad.electron_flux_cm2_s:.0f}")
    
    def test_outer_belt(self):
        """Outer belt should have high electron flux."""
        rad = self.model.radiation_at_altitude(altitude_km=20000.0)
        self.assertGreater(rad.electron_flux_cm2_s, 1.0e3)
        print(f"  [PASS] Outer belt: e-flux={rad.electron_flux_cm2_s:.1e}")
    
    def test_charging_risk(self):
        """Should assess charging risk."""
        risk = self.model.charging_risk(spacecraft_potential_v=-300.0)
        self.assertIn("risk_level", risk)
        self.assertIn("recommendation", risk)
        print(f"  [PASS] Charging: level={risk['risk_level']}")
    
    def test_atmospheric_expansion(self):
        """Should compute expansion factor."""
        self.model.update_indices(kp=2.0, ap=5.0, dst_nt=-10.0)
        factor = self.model.atmospheric_expansion_factor()
        self.assertAlmostEqual(factor, 1.0, delta=0.1)
        
        self.model.update_indices(kp=8.0, ap=120.0, dst_nt=-150.0)
        factor = self.model.atmospheric_expansion_factor()
        self.assertGreater(factor, 1.0)
        print(f"  [PASS] Expansion: quiet={1.0:.2f}, storm={factor:.2f}")
    
    def test_solar_panel_degradation(self):
        """Should estimate panel degradation."""
        remaining = self.model.solar_panel_degradation_factor(years_in_orbit=5.0)
        self.assertLess(remaining, 1.0)
        self.assertGreater(remaining, 0.5)
        print(f"  [PASS] Panel: {remaining*100:.1f}% remaining after 5yr")
    
    def test_mission_risk(self):
        """Should assess mission risk."""
        risk = self.model.mission_risk_assessment(
            altitude_km=400.0, mission_duration_years=5.0
        )
        self.assertIn("total_mission_dose_rad", risk)
        self.assertIn("radiation_risk", risk)
        print(f"  [PASS] Mission risk: {risk['radiation_risk']}, dose={risk['total_mission_dose_rad']:.1f} rad")


if __name__ == '__main__':
    unittest.main(verbosity=2)
