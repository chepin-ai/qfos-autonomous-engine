"""
Unit tests for fault injection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fault_injector import FaultInjector, SensorFaultInjector, ActuatorFaultInjector, CommunicationFaultInjector, FaultConfig, FaultType


class TestSensorFaultInjector(unittest.TestCase):
    """Test sensor fault injector."""
    
    def setUp(self):
        self.inj = SensorFaultInjector(seed=42)
    
    def test_noise(self):
        """Should inject noise."""
        self.inj.add_fault(FaultConfig(FaultType.SENSOR_NOISE, "s1", probability=1.0, magnitude=0.5))
        val, desc = self.inj.inject("s1", 10.0)
        self.assertNotEqual(val, 10.0)
        self.assertIsNotNone(desc)
        print(f"  [PASS] Noise: {val:.2f} ({desc})")
    
    def test_dropout(self):
        """Should inject dropout."""
        self.inj.add_fault(FaultConfig(FaultType.SENSOR_DROPOUT, "s1", probability=1.0))
        val, desc = self.inj.inject("s1", 10.0)
        self.assertTrue(val != val)  # NaN check
        print("  [PASS] Dropout: NaN")
    
    def test_bias(self):
        """Should inject bias."""
        self.inj.add_fault(FaultConfig(FaultType.SENSOR_BIAS, "s1", probability=1.0, magnitude=2.0))
        val, desc = self.inj.inject("s1", 10.0)
        self.assertEqual(val, 12.0)
        print(f"  [PASS] Bias: {val:.1f}")
    
    def test_no_fault(self):
        """Should pass through when no fault."""
        val, desc = self.inj.inject("s1", 10.0)
        self.assertEqual(val, 10.0)
        self.assertIsNone(desc)
        print("  [PASS] No fault: 10.0")
    
    def test_summary(self):
        """Should provide summary."""
        self.inj.add_fault(FaultConfig(FaultType.SENSOR_NOISE, "s1", probability=1.0))
        self.inj.inject("s1", 10.0)
        summary = self.inj.get_event_summary()
        self.assertGreater(summary["total_events"], 0)
        print(f"  [PASS] Summary: {summary['total_events']} events")


class TestActuatorFaultInjector(unittest.TestCase):
    """Test actuator fault injector."""
    
    def setUp(self):
        self.inj = ActuatorFaultInjector()
    
    def test_stuck(self):
        """Should make actuator stuck."""
        self.inj.set_stuck("thruster_1", 0.5)
        cmd = self.inj.inject("thruster_1", 1.0)
        self.assertEqual(cmd, 0.5)
        print(f"  [PASS] Stuck: {cmd}")
    
    def test_normal(self):
        """Should pass through normal actuator."""
        cmd = self.inj.inject("thruster_2", 0.8)
        self.assertEqual(cmd, 0.8)
        print("  [PASS] Normal: 0.8")
    
    def test_is_stuck(self):
        """Should detect stuck."""
        self.inj.set_stuck("a1", 0.0)
        self.assertTrue(self.inj.is_stuck("a1"))
        print("  [PASS] Is stuck: True")
    
    def test_release(self):
        """Should release stuck actuator."""
        self.inj.set_stuck("a1", 0.0)
        self.inj.release("a1")
        self.assertFalse(self.inj.is_stuck("a1"))
        print("  [PASS] Release: OK")


class TestCommunicationFaultInjector(unittest.TestCase):
    """Test communication fault injector."""
    
    def setUp(self):
        self.inj = CommunicationFaultInjector(seed=42)
    
    def test_packet_loss(self):
        """Should drop packets."""
        self.inj.set_packet_loss("ch1", 1.0)
        dropped = self.inj.should_drop("ch1")
        self.assertTrue(dropped)
        print("  [PASS] Drop: True")
    
    def test_latency(self):
        """Should add latency."""
        self.inj.set_latency("ch1", 500.0)
        lat = self.inj.get_latency("ch1")
        self.assertEqual(lat, 500.0)
        print(f"  [PASS] Latency: {lat}ms")
    
    def test_corruption(self):
        """Should corrupt packets."""
        self.inj.set_corruption("ch1", 1.0)
        corrupted = self.inj.is_corrupted("ch1")
        self.assertTrue(corrupted)
        print("  [PASS] Corrupt: True")
    
    def test_status(self):
        """Should provide channel status."""
        self.inj.set_packet_loss("ch1", 0.1)
        status = self.inj.get_channel_status("ch1")
        self.assertEqual(status["packet_loss"], 0.1)
        print(f"  [PASS] Status: loss={status['packet_loss']}")


class TestFaultInjector(unittest.TestCase):
    """Test unified fault injector."""
    
    def setUp(self):
        self.fi = FaultInjector(seed=42)
    
    def test_scenario(self):
        """Should define and activate scenario."""
        faults = [FaultConfig(FaultType.SENSOR_NOISE, "s1", probability=1.0, magnitude=0.1)]
        self.fi.define_scenario("sensor_degradation", faults)
        result = self.fi.activate_scenario("sensor_degradation")
        self.assertTrue(result)
        print("  [PASS] Scenario: activated")
    
    def test_clear(self):
        """Should clear all faults."""
        self.fi.sensor.add_fault(FaultConfig(FaultType.SENSOR_NOISE, "s1", probability=1.0))
        self.fi.clear_all()
        self.assertEqual(len(self.fi.sensor.active_faults), 0)
        print("  [PASS] Clear: OK")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.fi.injector_summary()
        self.assertEqual(summary["scenarios_defined"], 0)
        print(f"  [PASS] Summary: {summary['scenarios_defined']} scenarios")


if __name__ == '__main__':
    unittest.main(verbosity=2)
