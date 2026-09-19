"""
Unit tests for power distribution module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from power_distribution import (PowerLoad, Battery, SolarArray,
                                LoadBalancer, BusRegulator,
                                PowerDistribution)


class TestPowerLoad(unittest.TestCase):
    """Test power load."""
    
    def test_current_power(self):
        """Should compute current power."""
        load = PowerLoad("comms", 50.0, duty_cycle=0.5)
        self.assertEqual(load.current_power(), 25.0)
        print("  [PASS] Power: 25.0 W")
    
    def test_disabled(self):
        """Should be zero when disabled."""
        load = PowerLoad("heater", 100.0, is_enabled=False)
        self.assertEqual(load.current_power(), 0.0)
        print("  [PASS] Disabled: 0 W")


class TestBattery(unittest.TestCase):
    """Test battery."""
    
    def setUp(self):
        self.bat = Battery("main", capacity=1000.0, voltage=28.0,
                          state_of_charge=0.8)
    
    def test_available_energy(self):
        """Should compute available energy."""
        avail = self.bat.available_energy()
        self.assertEqual(avail, 760.0)  # 1000 * 0.8 * 0.95
        print(f"  [PASS] Available: {avail:.0f} Wh")
    
    def test_charge(self):
        """Should charge."""
        stored = self.bat.charge(power=50.0, dt=1.0)
        self.assertGreater(stored, 0)
        self.assertGreater(self.bat.state_of_charge, 0.8)
        print(f"  [PASS] Charge: SOC={self.bat.state_of_charge:.3f}")
    
    def test_discharge(self):
        """Should discharge."""
        delivered = self.bat.discharge(power=50.0, dt=1.0)
        self.assertGreater(delivered, 0)
        self.assertLess(self.bat.state_of_charge, 0.8)
        print(f"  [PASS] Discharge: SOC={self.bat.state_of_charge:.3f}")
    
    def test_dod(self):
        """Should compute depth of discharge."""
        dod = self.bat.depth_of_discharge()
        self.assertAlmostEqual(dod, 0.2, places=5)
        print(f"  [PASS] DoD: {dod:.1f}")


class TestSolarArray(unittest.TestCase):
    """Test solar array."""
    
    def setUp(self):
        self.array = SolarArray("SA1", area=5.0, efficiency=0.28)
    
    def test_output_power(self):
        """Should compute output power."""
        power = self.array.output_power(sun_angle=0.0, distance_au=1.0)
        self.assertAlmostEqual(power, 1905.4, places=0)
        print(f"  [PASS] Output: {power:.0f} W")
    
    def test_angled(self):
        """Should reduce at angle."""
        power = self.array.output_power(sun_angle=1.0)
        self.assertLess(power, 1905.0)
        print(f"  [PASS] Angled: {power:.0f} W")


class TestLoadBalancer(unittest.TestCase):
    """Test load balancer."""
    
    def setUp(self):
        self.lb = LoadBalancer()
        self.lb.add_load(PowerLoad("comms", 50.0, priority=2))
        self.lb.add_load(PowerLoad("heater", 200.0, priority=5))
        self.lb.add_load(PowerLoad("payload", 100.0, priority=1))
    
    def test_total_demand(self):
        """Should compute total demand."""
        self.assertEqual(self.lb.total_demand(), 350.0)
        print("  [PASS] Demand: 350 W")
    
    def test_balance(self):
        """Should balance loads."""
        self.lb.set_available_power(300.0)
        states = self.lb.balance()
        self.assertTrue(states["payload"])  # Priority 1
        self.assertTrue(states["comms"])    # Priority 2
        print("  [PASS] Balance: high priority on")
    
    def test_shed(self):
        """Should shed low priority."""
        self.lb.set_available_power(100.0)
        self.lb.balance()
        shed = self.lb.get_shed_loads()
        self.assertIn("heater", shed)
        print(f"  [PASS] Shed: {shed}")


class TestBusRegulator(unittest.TestCase):
    """Test bus regulator."""
    
    def setUp(self):
        self.reg = BusRegulator(nominal_voltage=28.0, tolerance=0.05)
    
    def test_regulate_sufficient(self):
        """Should maintain voltage when sufficient."""
        v = self.reg.regulate(source_power=500.0, load_power=300.0)
        self.assertEqual(v, 28.0)
        print(f"  [PASS] Regulate: {v:.1f} V")
    
    def test_regulate_insufficient(self):
        """Should sag when insufficient."""
        v = self.reg.regulate(source_power=100.0, load_power=500.0)
        self.assertLess(v, 28.0)
        print(f"  [PASS] Sag: {v:.1f} V")
    
    def test_within_tolerance(self):
        """Should check tolerance."""
        self.reg.regulate(500.0, 300.0)
        self.assertTrue(self.reg.is_within_tolerance())
        print("  [PASS] Tolerance: ok")


class TestPowerDistribution(unittest.TestCase):
    """Test unified power distribution."""
    
    def setUp(self):
        self.pd = PowerDistribution()
        self.pd.add_battery(Battery("bat1", 1000.0, 28.0, state_of_charge=0.9))
        self.pd.add_solar_array(SolarArray("sa1", 5.0, 0.28))
        self.pd.add_load(PowerLoad("comms", 50.0))
        self.pd.add_load(PowerLoad("heater", 100.0))
    
    def test_generation(self):
        """Should compute generation."""
        gen = self.pd.compute_generation()
        self.assertGreater(gen, 0)
        print(f"  [PASS] Generation: {gen:.0f} W")
    
    def test_distribute(self):
        """Should distribute power."""
        self.pd.compute_generation()
        status = self.pd.distribute(dt_hours=1.0)
        self.assertIn("generation", status)
        self.assertIn("demand", status)
        print(f"  [PASS] Distribute: gen={status['generation']:.0f}W")
    
    def test_summary(self):
        """Should provide summary."""
        self.pd.compute_generation()
        self.pd.distribute()
        summary = self.pd.power_summary()
        self.assertIn("battery_soc", summary)
        print(f"  [PASS] Summary: SOC={summary['battery_soc']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
