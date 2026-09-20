"""
Unit tests for power distribution module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from power_distribution import (PowerSource, BatteryState, PowerLoad,
                                BusRegulator, LoadBalancer,
                                BatteryController, SolarArrayTracker,
                                PowerDistribution)


class TestBusRegulator(unittest.TestCase):
    """Test bus regulator."""
    
    def setUp(self):
        self.bus = BusRegulator(nominal_voltage_V=28.0, max_current_A=100.0)
    
    def test_set_voltage(self):
        """Should set voltage within tolerance."""
        ok = self.bus.set_voltage(28.5)
        self.assertTrue(ok)
        self.assertEqual(self.bus.output_voltage, 28.5)
        print("  [PASS] Set: 28.5V")
    
    def test_set_voltage_out_of_range(self):
        """Should reject out-of-range voltage."""
        ok = self.bus.set_voltage(35.0)
        self.assertFalse(ok)
        print("  [PASS] Reject: 35V")
    
    def test_current_draw(self):
        """Should compute current."""
        i = self.bus.current_draw(280.0)
        self.assertEqual(i, 10.0)
        print(f"  [PASS] Current: {i} A")
    
    def test_available_power(self):
        """Should compute available power."""
        p = self.bus.available_power()
        self.assertEqual(p, 2800.0)  # 100A * 28V
        print(f"  [PASS] Available: {p} W")
    
    def test_overloaded(self):
        """Should detect overload."""
        self.bus.add_load(150.0)
        self.assertTrue(self.bus.is_overloaded())
        print("  [PASS] Overloaded")


class TestLoadBalancer(unittest.TestCase):
    """Test load balancer."""
    
    def setUp(self):
        self.lb = LoadBalancer()
        self.lb.register_source(PowerSource.SOLAR, 1000.0)
        self.lb.register_source(PowerSource.BATTERY, 500.0)
    
    def test_total_capacity(self):
        """Should compute total capacity."""
        cap = self.lb.total_capacity()
        self.assertEqual(cap, 1500.0)
        print(f"  [PASS] Capacity: {cap}")
    
    def test_sustainable(self):
        """Should check sustainability."""
        self.lb.add_load(PowerLoad("L1", 200.0, 28.0))
        self.assertTrue(self.lb.is_sustainable())
        print("  [PASS] Sustainable")
    
    def test_not_sustainable(self):
        """Should detect unsustainable."""
        self.lb.add_load(PowerLoad("L1", 1000.0, 28.0))
        self.lb.add_load(PowerLoad("L2", 600.0, 28.0))
        self.assertFalse(self.lb.is_sustainable())
        print("  [PASS] Not sustainable")
    
    def test_shed_load(self):
        """Should shed low priority loads."""
        self.lb.add_load(PowerLoad("L1", 200.0, 28.0, priority=1))
        self.lb.add_load(PowerLoad("L2", 300.0, 28.0, priority=5))
        shed = self.lb.shed_low_priority(250.0)
        self.assertIn("L2", shed)
        print(f"  [PASS] Shed: {shed}")


class TestBatteryController(unittest.TestCase):
    """Test battery controller."""
    
    def setUp(self):
        self.bc = BatteryController(capacity_Ah=100.0, nominal_voltage_V=28.0)
    
    def test_initial_soc(self):
        """Should start at 50% SOC."""
        self.assertEqual(self.bc.state_of_charge, 0.5)
        print("  [PASS] SOC: 0.5")
    
    def test_charge(self):
        """Should charge battery."""
        energy = self.bc.charge(500.0, 1.0)
        self.assertGreater(energy, 0)
        self.assertGreater(self.bc.state_of_charge, 0.5)
        print(f"  [PASS] Charge: {energy:.1f} Wh, SOC={self.bc.state_of_charge:.3f}")
    
    def test_discharge(self):
        """Should discharge battery."""
        self.bc.charge(500.0, 1.0)  # ensure enough charge
        soc_before = self.bc.state_of_charge
        energy = self.bc.discharge(200.0, 1.0)
        self.assertGreater(energy, 0)
        self.assertLess(self.bc.state_of_charge, soc_before)
        print(f"  [PASS] Discharge: {energy:.1f} Wh, SOC={self.bc.state_of_charge:.3f}")
    
    def test_remaining_energy(self):
        """Should compute remaining energy."""
        e = self.bc.remaining_energy_Wh()
        self.assertEqual(e, 0.5 * 100.0 * 28.0)
        print(f"  [PASS] Remaining: {e} Wh")
    
    def test_remaining_time(self):
        """Should compute remaining time."""
        t = self.bc.remaining_time_h(100.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Time: {t:.1f} h")


class TestSolarArrayTracker(unittest.TestCase):
    """Test solar array tracker."""
    
    def setUp(self):
        self.sa = SolarArrayTracker(area_m2=20.0, efficiency=0.28)
    
    def test_generated_power(self):
        """Should compute generated power."""
        p = self.sa.generated_power(sun_elevation_deg=90.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] Power: {p:.1f} W")
    
    def test_cosine_loss(self):
        """Should compute cosine loss."""
        self.sa.set_orientation(0.0, 45.0)
        cos = self.sa.cosine_loss(0.0, 90.0)
        self.assertGreater(cos, 0)
        self.assertLessEqual(cos, 1.0)
        print(f"  [PASS] Cosine: {cos:.3f}")
    
    def test_track_sun(self):
        """Should track sun."""
        self.sa.track_sun(30.0, 60.0)
        self.assertTrue(self.sa.tracking_active)
        self.assertEqual(self.sa.azimuth_deg, 30.0)
        print("  [PASS] Track: 30, 60")
    
    def test_eclipse(self):
        """Should generate zero in eclipse."""
        p = self.sa.generated_power(illumination_factor=0.0)
        self.assertEqual(p, 0.0)
        print("  [PASS] Eclipse: 0")


class TestPowerDistribution(unittest.TestCase):
    """Test unified power distribution."""
    
    def setUp(self):
        self.pd = PowerDistribution()
        self.pd.register_source(PowerSource.SOLAR, 1000.0)
    
    def test_add_load(self):
        """Should add load."""
        self.pd.add_load(PowerLoad("L1", 100.0, 28.0))
        self.assertEqual(self.pd.balancer.total_demand(), 100.0)
        print("  [PASS] Add: 100W")
    
    def test_remove_load(self):
        """Should remove load."""
        self.pd.add_load(PowerLoad("L1", 100.0, 28.0))
        self.pd.remove_load("L1")
        # Load disabled, demand may still show if not filtered
        enabled_demand = sum(l.power_W for l in self.pd.balancer.loads if l.enabled)
        self.assertEqual(enabled_demand, 0.0)
        print("  [PASS] Remove: 0W")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.pd.power_summary()
        self.assertIn("bus_voltage_V", summary)
        self.assertIn("battery_soc", summary)
        print(f"  [PASS] Summary: bus={summary['bus_voltage_V']}V")


if __name__ == '__main__':
    unittest.main(verbosity=2)
