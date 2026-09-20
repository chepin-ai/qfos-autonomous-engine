"""
Unit tests for thermal management module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermal_management import (ThermalZone, CoolingMode, TemperatureReading,
                                HeatPipe, Radiator, FluidLoop,
                                Cryocooler, ThermalManagement)


class TestHeatPipe(unittest.TestCase):
    """Test heat pipe."""
    
    def setUp(self):
        self.hp = HeatPipe(max_power_W=500.0, thermal_resistance_K_W=0.1)
    
    def test_transfer_inactive(self):
        """Should not transfer when inactive."""
        rate = self.hp.transfer_rate(50.0)
        self.assertEqual(rate, 0.0)
        print("  [PASS] Inactive: 0")
    
    def test_transfer_active(self):
        """Should transfer heat."""
        self.hp.activate()
        rate = self.hp.transfer_rate(50.0)
        self.assertEqual(rate, 500.0)  # 50/0.1 = 500, capped at max
        print(f"  [PASS] Transfer: {rate} W")
    
    def test_efficiency(self):
        """Should compute efficiency."""
        self.hp.activate()
        eff = self.hp.efficiency(25.0)
        self.assertGreater(eff, 0)
        print(f"  [PASS] Efficiency: {eff:.3f}")


class TestRadiator(unittest.TestCase):
    """Test radiator."""
    
    def setUp(self):
        self.rad = Radiator(area_m2=10.0, emissivity=0.9)
    
    def test_rejection_inactive(self):
        """Should not reject when inactive."""
        q = self.rad.heat_rejection(350.0)
        self.assertEqual(q, 0.0)
        print("  [PASS] Inactive: 0")
    
    def test_rejection(self):
        """Should compute heat rejection."""
        self.rad.activate()
        q = self.rad.heat_rejection(350.0)
        self.assertGreater(q, 0)
        print(f"  [PASS] Rejection: {q:.1f} W")
    
    def test_required_area(self):
        """Should compute required area."""
        area = self.rad.required_area(1000.0, 350.0)
        self.assertGreater(area, 0)
        print(f"  [PASS] Area: {area:.3f} m^2")


class TestFluidLoop(unittest.TestCase):
    """Test fluid loop."""
    
    def setUp(self):
        self.fl = FluidLoop(flow_rate_kg_s=0.1, specific_heat_J_kgK=3900.0)
    
    def test_capacity_inactive(self):
        """Should have zero capacity when inactive."""
        cap = self.fl.cooling_capacity()
        self.assertEqual(cap, 0.0)
        print("  [PASS] Inactive: 0")
    
    def test_capacity(self):
        """Should compute cooling capacity."""
        self.fl.activate()
        cap = self.fl.cooling_capacity()
        self.assertEqual(cap, 0.1 * 3900.0 * 20.0)  # delta T = 20K
        print(f"  [PASS] Capacity: {cap:.1f} W")
    
    def test_pump_power(self):
        """Should compute pump power."""
        self.fl.activate()
        p = self.fl.pump_power()
        self.assertGreater(p, 0)
        print(f"  [PASS] Pump: {p:.1f} W")


class TestCryocooler(unittest.TestCase):
    """Test cryocooler."""
    
    def setUp(self):
        self.cc = Cryocooler(cooling_power_W=1.0, min_temp_K=4.0)
    
    def test_input_power(self):
        """Should compute input power."""
        p = self.cc.required_input_power(80.0, 300.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] Input: {p:.1f} W")
    
    def test_achievable_temp(self):
        """Should compute achievable temp."""
        t = self.cc.achievable_temp(0.5)
        self.assertGreaterEqual(t, 4.0)
        print(f"  [PASS] Temp: {t:.1f} K")
    
    def test_inf_power(self):
        """Should return inf for invalid temps."""
        p = self.cc.required_input_power(350.0, 300.0)
        self.assertEqual(p, float('inf'))
        print("  [PASS] Inf: invalid")


class TestThermalManagement(unittest.TestCase):
    """Test unified thermal management."""
    
    def setUp(self):
        self.tm = ThermalManagement()
        self.tm.set_temperature_limits(ThermalZone.ELECTRONICS, 250.0, 350.0)
    
    def test_add_reading(self):
        """Should add reading."""
        r = TemperatureReading(ThermalZone.ELECTRONICS, 300.0)
        self.tm.add_reading(r)
        self.assertEqual(len(self.tm.readings), 1)
        print("  [PASS] Add: 1 reading")
    
    def test_zone_temp(self):
        """Should get zone temperature."""
        self.tm.add_reading(TemperatureReading(ThermalZone.ELECTRONICS, 300.0))
        t = self.tm.get_zone_temperature(ThermalZone.ELECTRONICS)
        self.assertEqual(t, 300.0)
        print(f"  [PASS] Temp: {t} K")
    
    def test_zone_health(self):
        """Should check zone health."""
        self.tm.add_reading(TemperatureReading(ThermalZone.ELECTRONICS, 300.0))
        healthy, margin = self.tm.check_zone_health(ThermalZone.ELECTRONICS)
        self.assertTrue(healthy)
        self.assertGreater(margin, 0)
        print(f"  [PASS] Health: {healthy}, margin={margin:.3f}")
    
    def test_select_mode(self):
        """Should select cooling mode."""
        self.tm.add_reading(TemperatureReading(ThermalZone.ELECTRONICS, 340.0))
        mode = self.tm.select_cooling_mode(ThermalZone.ELECTRONICS, 100.0)
        self.assertIn(mode, CoolingMode)
        print(f"  [PASS] Mode: {mode.value}")
    
    def test_deactivate_all(self):
        """Should deactivate all."""
        self.tm.radiator.activate()
        self.tm.deactivate_all()
        self.assertFalse(self.tm.radiator.active)
        print("  [PASS] Deactivate all")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.tm.thermal_summary()
        self.assertIn("zones_monitored", summary)
        print(f"  [PASS] Summary: {summary['zones_monitored']} zones")


if __name__ == '__main__':
    unittest.main(verbosity=2)
