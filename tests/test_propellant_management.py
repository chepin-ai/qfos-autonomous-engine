"""
Unit tests for propellant management module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from propellant_management import (TankState, Tank,
                                   ConsumptionTracker,
                                   UllageManager,
                                   PressurizationSystem,
                                   PropellantManagement)


class TestTank(unittest.TestCase):
    """Test tank."""
    
    def test_fill_level(self):
        """Should compute fill level."""
        t = Tank("t1", "LOX", 1000.0, 500.0)
        self.assertEqual(t.fill_level(), 0.5)
        print("  [PASS] Fill: 0.5")
    
    def test_state_nominal(self):
        """Should be nominal."""
        t = Tank("t1", "LOX", 1000.0, 500.0)
        self.assertEqual(t.state(), TankState.NOMINAL)
        print("  [PASS] State: nominal")
    
    def test_state_critical(self):
        """Should be critical when low."""
        t = Tank("t1", "LOX", 1000.0, 50.0)
        self.assertEqual(t.state(), TankState.CRITICAL)
        print("  [PASS] State: critical")
    
    def test_state_empty(self):
        """Should be empty."""
        t = Tank("t1", "LOX", 1000.0, 0.0)
        self.assertEqual(t.state(), TankState.EMPTY)
        print("  [PASS] State: empty")


class TestConsumptionTracker(unittest.TestCase):
    """Test consumption tracker."""
    
    def setUp(self):
        self.ct = ConsumptionTracker()
        self.ct.record(0, 1000.0, 10.0)
        self.ct.record(10, 900.0, 10.0)
    
    def test_total_consumed(self):
        """Should track consumption."""
        self.assertEqual(self.ct.total_consumed, 100.0)
        print(f"  [PASS] Consumed: {self.ct.total_consumed}")
    
    def test_average_flow(self):
        """Should compute average flow."""
        rate = self.ct.average_flow_rate()
        self.assertAlmostEqual(rate, 10.0, places=1)
        print(f"  [PASS] Flow: {rate:.1f} kg/s")
    
    def test_time_to_empty(self):
        """Should estimate empty time."""
        t = self.ct.time_to_empty(900.0)
        self.assertEqual(t, 90.0)
        print(f"  [PASS] Empty: {t:.0f}s")
    
    def test_burn_time(self):
        """Should estimate burn time."""
        t = self.ct.remaining_burn_time(900.0, 45000.0, 310.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Burn: {t:.0f}s")


class TestUllageManager(unittest.TestCase):
    """Test ullage manager."""
    
    def setUp(self):
        self.um = UllageManager(settling_accel=0.1)
        self.tank = Tank("t1", "LOX", 1000.0, 500.0)
    
    def test_required_thrust(self):
        """Should compute settling thrust."""
        thrust = self.um.required_settling_burn(self.tank, 5000.0)
        self.assertEqual(thrust, 500.0)
        print(f"  [PASS] Settling: {thrust:.0f}N")
    
    def test_assess_ullage(self):
        """Should assess ullage."""
        full_tank = Tank("t2", "LOX", 1000.0, 900.0)
        ok = self.um.assess_ullage(full_tank)
        self.assertTrue(ok)
        print("  [PASS] Ullage: ok")
    
    def test_settle(self):
        """Should settle propellant."""
        self.um.settle_propellant(self.tank)
        self.assertTrue(self.um.settling_active)
        self.assertAlmostEqual(self.tank.ullage_fraction, 0.02)
        print("  [PASS] Settle: active")


class TestPressurizationSystem(unittest.TestCase):
    """Test pressurization."""
    
    def setUp(self):
        self.ps = PressurizationSystem(max_pressure=30.0)
        self.tank = Tank("t1", "LOX", 1000.0, 500.0)
    
    def test_required_pressure(self):
        """Should compute required pressure."""
        p = self.ps.required_pressure(self.tank, 20.0)
        self.assertEqual(p, 24.0)
        print(f"  [PASS] Required: {p:.0f} bar")
    
    def test_pressurize(self):
        """Should pressurize tank."""
        self.ps.pressurize(self.tank, 25.0)
        self.assertEqual(self.tank.pressure, 25.0)
        print(f"  [PASS] Pressure: {self.tank.pressure}")
    
    def test_max_pressure(self):
        """Should not exceed max."""
        self.ps.pressurize(self.tank, 50.0)
        self.assertEqual(self.tank.pressure, 30.0)
        print(f"  [PASS] Max: {self.tank.pressure}")


class TestPropellantManagement(unittest.TestCase):
    """Test unified propellant management."""
    
    def setUp(self):
        self.pm = PropellantManagement()
        self.pm.add_tank(Tank("ox", "LOX", 1000.0, 800.0))
        self.pm.add_tank(Tank("fuel", "RP-1", 600.0, 400.0))
    
    def test_add_tank(self):
        """Should add tanks."""
        self.assertEqual(len(self.pm.tanks), 2)
        print("  [PASS] Tanks: 2")
    
    def test_consume(self):
        """Should record consumption."""
        self.pm.consume("ox", 100.0, 10.0)
        self.assertAlmostEqual(self.pm.tanks["ox"].current_mass, 700.0)
        print(f"  [PASS] Consume: {self.pm.tanks['ox'].current_mass}")
    
    def test_transfer(self):
        """Should transfer propellant."""
        self.pm.transfer("ox", "fuel", 50.0)
        self.assertAlmostEqual(self.pm.tanks["ox"].current_mass, 750.0)
        self.assertAlmostEqual(self.pm.tanks["fuel"].current_mass, 450.0)
        print("  [PASS] Transfer: 50kg")
    
    def test_total(self):
        """Should compute totals."""
        self.assertAlmostEqual(self.pm.total_propellant(), 1200.0)
        self.assertAlmostEqual(self.pm.total_capacity(), 1600.0)
        print(f"  [PASS] Total: {self.pm.total_propellant()}")
    
    def test_fill_level(self):
        """Should compute fill level."""
        level = self.pm.overall_fill_level()
        self.assertAlmostEqual(level, 0.75, places=2)
        print(f"  [PASS] Level: {level:.2f}")
    
    def test_critical(self):
        """Should find critical tanks."""
        self.pm.consume("ox", 790.0, 0.0)
        critical = self.pm.get_critical_tanks()
        self.assertEqual(len(critical), 1)
        print(f"  [PASS] Critical: {len(critical)}")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.pm.propellant_summary()
        self.assertEqual(summary["tanks"], 2)
        print(f"  [PASS] Summary: {summary['tanks']} tanks")


if __name__ == '__main__':
    unittest.main(verbosity=2)
