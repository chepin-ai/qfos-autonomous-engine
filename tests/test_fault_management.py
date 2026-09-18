"""
Unit tests for fault management (FDIR) module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fault_management import (
    FaultDetector, FaultIsolationEngine, RecoveryEngine, FDIRSystem,
    Fault, FaultSeverity, FaultStatus, TelemetryPoint
)


class TestFaultDetector(unittest.TestCase):
    """Test fault detection algorithms."""
    
    def setUp(self):
        self.detector = FaultDetector()
    
    def test_limit_violation_high(self):
        """Should detect value above maximum limit."""
        point = TelemetryPoint(
            name="temp.sensor1", value=85.0, timestamp=0.0,
            min_limit=0.0, max_limit=80.0
        )
        fault = self.detector.check_limits(point)
        self.assertIsNotNone(fault)
        self.assertEqual(fault.severity, FaultSeverity.HIGH)
        print(f"  [PASS] High limit fault: {fault.description}")
    
    def test_limit_violation_low(self):
        """Should detect value below minimum limit."""
        point = TelemetryPoint(
            name="voltage.bus", value=-1.0, timestamp=0.0,
            min_limit=0.0, max_limit=50.0
        )
        fault = self.detector.check_limits(point)
        self.assertIsNotNone(fault)
        self.assertEqual(fault.severity, FaultSeverity.HIGH)
        print(f"  [PASS] Low limit fault: {fault.description}")
    
    def test_no_violation(self):
        """Should not detect fault within limits."""
        point = TelemetryPoint(
            name="temp.sensor1", value=50.0, timestamp=0.0,
            min_limit=0.0, max_limit=80.0
        )
        fault = self.detector.check_limits(point)
        self.assertIsNone(fault)
        print("  [PASS] No fault within limits")
    
    def test_stuck_value(self):
        """Should detect stuck telemetry values."""
        for i in range(15):
            point = TelemetryPoint(
                name="pressure.tank", value=101.325, timestamp=float(i)
            )
            self.detector.add_telemetry(point)
        
        fault = self.detector.check_stuck_value("pressure.tank", threshold=0.01, window=10)
        self.assertIsNotNone(fault)
        self.assertEqual(fault.severity, FaultSeverity.MEDIUM)
        print(f"  [PASS] Stuck value detected: {fault.description}")
    
    def test_rate_of_change(self):
        """Should detect excessive rate of change."""
        p1 = TelemetryPoint(name="current.motor", value=1.0, timestamp=0.0)
        p2 = TelemetryPoint(name="current.motor", value=50.0, timestamp=1.0)
        self.detector.add_telemetry(p1)
        self.detector.add_telemetry(p2)
        
        fault = self.detector.check_rate_of_change("current.motor", max_rate=10.0)
        self.assertIsNotNone(fault)
        print(f"  [PASS] Rate fault: {fault.description}")


class TestFaultIsolation(unittest.TestCase):
    """Test fault isolation."""
    
    def setUp(self):
        self.iso = FaultIsolationEngine()
        self.iso.add_dependency("camera", ["power.bus", "data.bus"])
        self.iso.add_dependency("radio", ["power.bus", "antenna"])
    
    def test_isolate_fault(self):
        """Should identify suspect components."""
        fault = Fault(
            fault_id="LIMIT_MAX_power.bus",
            subsystem="power.bus",
            description="Overvoltage",
            severity=FaultSeverity.CRITICAL,
            timestamp=0.0
        )
        suspects = self.iso.isolate_fault(fault)
        self.assertIn("power.bus", suspects)
        print(f"  [PASS] Isolation suspects: {suspects}")
    
    def test_root_cause(self):
        """Should find most likely root cause."""
        faults = [
            Fault("F1", "power.bus", "Overvoltage", FaultSeverity.CRITICAL, 0.0),
            Fault("F2", "camera", "No image", FaultSeverity.HIGH, 1.0),
            Fault("F3", "radio", "No signal", FaultSeverity.HIGH, 2.0),
        ]
        root = self.iso.get_root_cause(faults)
        self.assertIsNotNone(root)
        print(f"  [PASS] Root cause: {root}")


class TestRecoveryEngine(unittest.TestCase):
    """Test recovery procedures."""
    
    def setUp(self):
        self.recovery = RecoveryEngine()
        
        def reset_sensor(fault):
            return True
        
        self.recovery.register_procedure("sensor", reset_sensor)
    
    def test_successful_recovery(self):
        """Should execute recovery procedure."""
        fault = Fault(
            fault_id="STUCK_temp.sensor1",
            subsystem="temp",
            description="Stuck sensor",
            severity=FaultSeverity.MEDIUM,
            timestamp=0.0
        )
        success = self.recovery.attempt_recovery(fault)
        self.assertTrue(success)
        self.assertEqual(fault.status, FaultStatus.RECOVERED)
        print(f"  [PASS] Recovery success: {fault.recovery_action}")
    
    def test_no_procedure(self):
        """Should handle missing recovery procedure."""
        fault = Fault(
            fault_id="UNKNOWN_failure",
            subsystem="unknown",
            description="Unknown failure",
            severity=FaultSeverity.CRITICAL,
            timestamp=0.0
        )
        success = self.recovery.attempt_recovery(fault)
        self.assertFalse(success)
        self.assertEqual(fault.status, FaultStatus.IGNORED)
        print("  [PASS] No procedure handled correctly")


class TestFDIRSystem(unittest.TestCase):
    """Test integrated FDIR system."""
    
    def setUp(self):
        self.fdir = FDIRSystem()
    
    def test_monitor_and_handle(self):
        """Should detect and handle faults end-to-end."""
        telemetry = [
            TelemetryPoint("temp.bus", 90.0, 0.0, min_limit=0.0, max_limit=80.0),
            TelemetryPoint("voltage.bus", 28.0, 0.0, min_limit=20.0, max_limit=35.0),
        ]
        
        faults = self.fdir.monitor(telemetry)
        self.assertEqual(len(faults), 1)  # temp over limit
        
        results = self.fdir.handle_faults(faults)
        self.assertIn("failed", results)  # No recovery procedure registered
        print(f"  [PASS] E2E FDIR: {len(faults)} faults, root_cause={results.get('root_cause')}")
    
    def test_health_summary(self):
        """Should provide health summary."""
        summary = self.fdir.get_health_summary()
        self.assertIn("active_faults", summary)
        self.assertIn("recovery_rate", summary)
        print(f"  [PASS] Health: active={summary['active_faults']}, recovery_rate={summary['recovery_rate']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
