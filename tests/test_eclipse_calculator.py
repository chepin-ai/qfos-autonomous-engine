"""
Unit tests for eclipse calculator module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from eclipse_calculator import EclipseCalculator, EclipseType


class TestEclipseCalculator(unittest.TestCase):
    """Test eclipse calculator."""
    
    def setUp(self):
        self.calc = EclipseCalculator(
            satellite_altitude_km=400.0,
            orbit_inclination_deg=51.6
        )
    
    def test_period_computation(self):
        """Should compute orbital period."""
        self.assertGreater(self.calc.period_min, 90.0)
        self.assertLess(self.calc.period_min, 100.0)
        print(f"  [PASS] Period: {self.calc.period_min:.2f} min")
    
    def test_eclipse_duration(self):
        """Should compute eclipse duration."""
        duration = self.calc.eclipse_duration_min()
        self.assertGreater(duration, 0.0)
        self.assertLess(duration, self.calc.period_min * 0.5)
        print(f"  [PASS] Eclipse: {duration:.2f} min ({duration/self.calc.period_min*100:.1f}% of orbit)")
    
    def test_is_in_shadow(self):
        """Should detect shadow."""
        # Satellite opposite to Sun
        sun = (1.0, 0.0, 0.0)
        sat = (-6678.0, 0.0, 0.0)
        eclipse = self.calc.is_in_shadow(sun, sat)
        self.assertIn(eclipse, [EclipseType.UMBRA, EclipseType.PENUMBRA])
        
        # Satellite on Sun side
        sat2 = (6678.0, 0.0, 0.0)
        eclipse2 = self.calc.is_in_shadow(sun, sat2)
        self.assertEqual(eclipse2, EclipseType.NONE)
        print(f"  [PASS] Shadow: antisun={eclipse.value}, sunside={eclipse2.value}")
    
    def test_eclipse_seasons(self):
        """Should compute eclipse seasons."""
        seasons = self.calc.eclipse_seasons()
        self.assertEqual(len(seasons), 2)
        self.assertIn("duration_days", seasons[0])
        print(f"  [PASS] Seasons: {len(seasons)} per year, {seasons[0]['duration_days']:.0f} days each")
    
    def test_daily_eclipse_profile(self):
        """Should generate daily eclipse profile."""
        events = self.calc.daily_eclipse_profile(num_orbits=15)
        self.assertIsInstance(events, list)
        total_eclipse_min = sum(e.duration_min for e in events)
        self.assertGreater(total_eclipse_min, 0.0)
        print(f"  [PASS] Daily: {len(events)} events, total={total_eclipse_min:.1f} min")
    
    def test_power_impact(self):
        """Should assess power impact."""
        impact = self.calc.power_impact(
            solar_array_power_w=500.0,
            battery_capacity_wh=100.0,
            base_load_w=200.0
        )
        self.assertIn("battery_dod_percent", impact)
        self.assertIn("status", impact)
        print(f"  [PASS] Power: DOD={impact['battery_dod_percent']:.1f}%, status={impact['status']}")
    
    def test_sun_direction(self):
        """Should compute Sun direction."""
        sun = EclipseCalculator.sun_direction_eci(2451545.0)
        r = (sun[0]**2 + sun[1]**2 + sun[2]**2) ** 0.5
        self.assertAlmostEqual(r, 1.0, delta=0.01)
        print(f"  [PASS] Sun dir: ({sun[0]:.3f}, {sun[1]:.3f}, {sun[2]:.3f})")


if __name__ == '__main__':
    unittest.main(verbosity=2)
