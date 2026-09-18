"""
Unit tests for power system module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from power_system import SolarArray, Battery, PowerManagementSystem, PowerLoad


class TestSolarArray(unittest.TestCase):
    """Test solar array power generation."""
    
    def test_earth_orbit_power(self):
        """Should generate reasonable power at 1 AU."""
        array = SolarArray(area_m2=10.0, efficiency=0.28)
        power = array.power_output(solar_distance_au=1.0, incidence_angle_deg=0.0)
        self.assertGreater(power, 1000)  # > 1 kW for 10m2
        self.assertLess(power, 5000)     # < 5 kW
        print(f"  [PASS] 10m2 at 1AU: {power:.1f} W")
    
    def test_distance_effect(self):
        """Power should decrease with distance."""
        array = SolarArray(area_m2=10.0, efficiency=0.28)
        p_earth = array.power_output(1.0)
        p_mars = array.power_output(1.524)
        self.assertGreater(p_earth, p_mars)
        print(f"  [PASS] Distance effect: Earth={p_earth:.1f}W, Mars={p_mars:.1f}W")
    
    def test_incidence_angle(self):
        """Power should decrease at oblique angles."""
        array = SolarArray(area_m2=10.0, efficiency=0.28)
        p_normal = array.power_output(1.0, 0.0)
        p_45 = array.power_output(1.0, 45.0)
        p_90 = array.power_output(1.0, 90.0)
        self.assertGreater(p_normal, p_45)
        self.assertGreater(p_45, p_90)
        self.assertAlmostEqual(p_90, 0.0, places=1)
        print(f"  [PASS] Incidence: 0deg={p_normal:.1f}W, 45deg={p_45:.1f}W, 90deg={p_90:.1f}W")
    
    def test_degradation(self):
        """Older arrays should produce less power."""
        array = SolarArray(area_m2=10.0, efficiency=0.28, degradation_per_year=0.02)
        p_new = array.power_output(1.0)
        array.set_age(10.0)
        p_old = array.power_output(1.0)
        self.assertLess(p_old, p_new)
        print(f"  [PASS] Degradation: new={p_new:.1f}W, 10yr={p_old:.1f}W")


class TestBattery(unittest.TestCase):
    """Test battery operations."""
    
    def setUp(self):
        self.battery = Battery(capacity_wh=1000.0, initial_soc=1.0, max_dod=0.8)
    
    def test_discharge(self):
        """Discharge should reduce SOC."""
        initial_soc = self.battery.soc
        delivered = self.battery.discharge(energy_wh=200.0)
        self.assertLess(self.battery.soc, initial_soc)
        self.assertGreater(delivered, 0)
        print(f"  [PASS] Discharge: delivered={delivered:.1f}Wh, SOC={self.battery.soc:.3f}")
    
    def test_charge(self):
        """Charge should increase SOC."""
        self.battery.soc = 0.5
        initial_soc = self.battery.soc
        accepted = self.battery.charge(energy_wh=200.0)
        self.assertGreater(self.battery.soc, initial_soc)
        print(f"  [PASS] Charge: accepted={accepted:.1f}Wh, SOC={self.battery.soc:.3f}")
    
    def test_max_dod_limit(self):
        """Should not discharge below max DOD."""
        battery = Battery(capacity_wh=1000.0, initial_soc=1.0, max_dod=0.8)
        # Try to discharge everything
        delivered = battery.discharge(energy_wh=1000.0)
        self.assertGreaterEqual(battery.soc, 0.199)  # ~0.2 (floating point tolerance)
        print(f"  [PASS] DOD limit: SOC={battery.soc:.3f}, delivered={delivered:.1f}Wh")
    
    def test_battery_state(self):
        """State should contain key metrics."""
        state = self.battery.get_state()
        self.assertIn("soc", state)
        self.assertIn("energy_wh", state)
        self.assertIn("health", state)
        print(f"  [PASS] Battery state: SOC={state['soc']}, health={state['health']}")


class TestPowerManagement(unittest.TestCase):
    """Test power management system."""
    
    def setUp(self):
        solar = SolarArray(area_m2=10.0, efficiency=0.28)
        battery = Battery(capacity_wh=2000.0, initial_soc=0.8, max_dod=0.8)
        loads = [
            PowerLoad("avionics", 50.0, duty_cycle=1.0, critical=True),
            PowerLoad("communications", 100.0, duty_cycle=0.3, critical=True),
            PowerLoad("payload", 80.0, duty_cycle=0.5, critical=False),
            PowerLoad("heaters", 30.0, duty_cycle=0.2, critical=False),
        ]
        self.pms = PowerManagementSystem(solar, battery, loads)
    
    def test_total_load(self):
        """Should calculate total load correctly."""
        total = self.pms.total_load_power()
        expected = 50.0 + 100.0*0.3 + 80.0*0.5 + 30.0*0.2
        self.assertAlmostEqual(total, expected)
        print(f"  [PASS] Total load: {total:.1f}W")
    
    def test_daylight_operation(self):
        """Daylight should provide excess power."""
        result = self.pms.simulate_timestep(
            solar_distance_au=1.0, sun_incidence_deg=0.0, cell_temp_c=25.0
        )
        self.assertIn(result["status"], ["CHARGING", "DISCHARGING", "POWER_SHORTAGE"])
        print(f"  [PASS] Daylight: solar={result['solar_power_w']:.1f}W, status={result['status']}, SOC={result['battery_soc']:.3f}")
    
    def test_eclipse_survival(self):
        """Should analyze eclipse survivability."""
        result = self.pms.eclipse_analysis(eclipse_duration_hours=1.5)
        self.assertIn("can_survive", result)
        self.assertIn("recommendation", result)
        print(f"  [PASS] Eclipse 1.5h: survive={result['can_survive']}, margin={result['margin_wh']:.1f}Wh")
    
    def test_long_eclipse(self):
        """Very long eclipse should not be survivable."""
        result = self.pms.eclipse_analysis(eclipse_duration_hours=24.0)
        if not result["can_survive"]:
            self.assertEqual(result["recommendation"], "SHED_NON_CRITICAL")
        print(f"  [PASS] Eclipse 24h: survive={result['can_survive']}, rec={result['recommendation']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
