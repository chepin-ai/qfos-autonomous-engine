"""
Unit tests for thermal management module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermal_management import (ThermalNode, Radiator, HeatPipe,
                                ThermalNetwork, TemperatureController,
                                ThermalManagement)


class TestThermalNode(unittest.TestCase):
    """Test thermal node."""
    
    def test_capacity(self):
        """Should compute thermal capacity."""
        node = ThermalNode("CPU", mass=0.5, specific_heat=800)
        self.assertEqual(node.thermal_capacity(), 400.0)
        print("  [PASS] Capacity: 400 J/K")


class TestRadiator(unittest.TestCase):
    """Test radiator."""
    
    def setUp(self):
        self.rad = Radiator("main", area=2.0, emissivity=0.85, absorptivity=0.2)
    
    def test_radiated_power(self):
        """Should compute radiated power."""
        power = self.rad.radiated_power(temp=300.0)
        self.assertGreater(power, 0)
        print(f"  [PASS] Radiated: {power:.1f} W")
    
    def test_required_area(self):
        """Should compute required area."""
        area = self.rad.required_area(power=100.0, temp=300.0)
        self.assertGreater(area, 0)
        print(f"  [PASS] Area: {area:.2f} m^2")


class TestHeatPipe(unittest.TestCase):
    """Test heat pipe."""
    
    def setUp(self):
        self.pipe = HeatPipe("HP1", thermal_conductance=10.0, max_heat_transfer=50.0)
    
    def test_transfer(self):
        """Should transfer heat."""
        q = self.pipe.transfer_heat(350.0, 300.0)
        self.assertEqual(q, 50.0)  # Clamped to max_heat_transfer
        print(f"  [PASS] Transfer: {q:.1f} W")
    
    def test_no_transfer(self):
        """Should not transfer if cold > hot."""
        q = self.pipe.transfer_heat(300.0, 350.0)
        self.assertEqual(q, 0.0)
        print("  [PASS] No transfer: 0 W")


class TestThermalNetwork(unittest.TestCase):
    """Test thermal network."""
    
    def setUp(self):
        self.net = ThermalNetwork()
        self.net.add_node(ThermalNode("CPU", 0.5, 800, 350.0, 50.0))
        self.net.add_node(ThermalNode("panel", 2.0, 500, 250.0, 0.0))
        self.net.add_heat_pipe("CPU", "panel", HeatPipe("hp", 5.0, 30.0))
        self.net.add_radiator("panel", Radiator("rad", 1.0, 0.9, 0.1))
    
    def test_step(self):
        """Should advance simulation."""
        temps = self.net.step(dt=1.0)
        self.assertIn("CPU", temps)
        self.assertIn("panel", temps)
        print(f"  [PASS] Step: CPU={temps['CPU']:.1f}K, panel={temps['panel']:.1f}K")
    
    def test_simulate(self):
        """Should run simulation."""
        history = self.net.simulate(duration=10.0, dt=1.0)
        self.assertEqual(len(history["CPU"]), 11)
        print(f"  [PASS] Simulate: {len(history['CPU'])} steps")
    
    def test_get_temperatures(self):
        """Should get temperatures."""
        temps = self.net.get_temperatures()
        self.assertEqual(temps["CPU"], 350.0)
        print(f"  [PASS] Temps: CPU={temps['CPU']}K")


class TestTemperatureController(unittest.TestCase):
    """Test temperature controller."""
    
    def setUp(self):
        self.ctrl = TemperatureController(kp=1.0, ki=0.1, kd=0.5)
    
    def test_compute(self):
        """Should compute control output."""
        output = self.ctrl.compute(setpoint=300.0, measurement=320.0, dt=1.0)
        self.assertLess(output, 0)  # Need cooling
        print(f"  [PASS] Control: {output:.1f} W")
    
    def test_reset(self):
        """Should reset."""
        self.ctrl.compute(300.0, 320.0, 1.0)
        self.ctrl.reset()
        self.assertEqual(self.ctrl.integral, 0.0)
        print("  [PASS] Reset: zero")


class TestThermalManagement(unittest.TestCase):
    """Test unified thermal management."""
    
    def setUp(self):
        self.tm = ThermalManagement()
        self.tm.add_node(ThermalNode("CPU", 0.5, 800, 350.0, 50.0))
        self.tm.add_controller("CPU", TemperatureController())
    
    def test_regulate(self):
        """Should regulate temperature."""
        outputs = self.tm.regulate(dt=1.0)
        self.assertIn("CPU", outputs)
        print(f"  [PASS] Regulate: {outputs['CPU']:.1f} W")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.tm.thermal_summary()
        self.assertIn("avg_temperature", summary)
        print(f"  [PASS] Summary: avg={summary['avg_temperature']:.1f}K")


if __name__ == '__main__':
    unittest.main(verbosity=2)
