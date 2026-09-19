"""
Unit tests for self diagnostics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from self_diagnostics import (HealthStatus, DiagnosticLevel, DiagnosticResult,
                              HealthMonitor, FaultDiagnosis,
                              SystemChecker, SelfDiagnostics)


class TestHealthMonitor(unittest.TestCase):
    """Test health monitor."""
    
    def setUp(self):
        self.hm = HealthMonitor()
        self.hm.register_component("cpu", 0.7, 0.5, 0.3)
    
    def test_register(self):
        """Should register component."""
        self.assertIn("cpu", self.hm.health_scores)
        print("  [PASS] Register: cpu")
    
    def test_healthy(self):
        """Should be healthy."""
        self.hm.update_health("cpu", 0.9)
        self.assertEqual(self.hm.get_status("cpu"), HealthStatus.HEALTHY)
        print("  [PASS] Healthy: 0.9")
    
    def test_warning(self):
        """Should be warning."""
        self.hm.update_health("cpu", 0.6)
        self.assertEqual(self.hm.get_status("cpu"), HealthStatus.WARNING)
        print("  [PASS] Warning: 0.6")
    
    def test_critical(self):
        """Should be critical."""
        self.hm.update_health("cpu", 0.2)
        self.assertEqual(self.hm.get_status("cpu"), HealthStatus.CRITICAL)
        print("  [PASS] Critical: 0.2")
    
    def test_overall(self):
        """Should compute overall."""
        self.hm.register_component("mem", 0.7, 0.5, 0.3)
        self.hm.update_health("cpu", 0.9)
        self.hm.update_health("mem", 0.8)
        self.assertAlmostEqual(self.hm.overall_health(), 0.85, places=2)
        print(f"  [PASS] Overall: {self.hm.overall_health():.2f}")


class TestFaultDiagnosis(unittest.TestCase):
    """Test fault diagnosis."""
    
    def setUp(self):
        self.fd = FaultDiagnosis()
        self.fd.add_rule("power_failure", ["low_voltage", "high_current"])
        self.fd.add_rule("sensor_error", ["no_data", "stale_data"])
    
    def test_diagnose_none(self):
        """Should have no faults without symptoms."""
        probs = self.fd.diagnose()
        self.assertEqual(probs["power_failure"], 0.0)
        print("  [PASS] None: 0.0")
    
    def test_diagnose_partial(self):
        """Should diagnose partial match."""
        self.fd.report_symptom("low_voltage", True)
        probs = self.fd.diagnose()
        self.assertEqual(probs["power_failure"], 0.5)
        print(f"  [PASS] Partial: {probs['power_failure']}")
    
    def test_diagnose_full(self):
        """Should diagnose full match."""
        self.fd.report_symptom("low_voltage", True)
        self.fd.report_symptom("high_current", True)
        probs = self.fd.diagnose()
        self.assertEqual(probs["power_failure"], 1.0)
        print(f"  [PASS] Full: {probs['power_failure']}")
    
    def test_most_likely(self):
        """Should find most likely."""
        self.fd.report_symptom("low_voltage", True)
        self.fd.report_symptom("high_current", True)
        likely = self.fd.most_likely_fault()
        self.assertIsNotNone(likely)
        self.assertEqual(likely[0], "power_failure")
        print(f"  [PASS] Likely: {likely[0]}={likely[1]}")


class TestSystemChecker(unittest.TestCase):
    """Test system checker."""
    
    def setUp(self):
        self.sc = SystemChecker()
        self.sc.register_check("cpu", "temp",
                               lambda: (True, 0.6, "OK"), 0.8)
        self.sc.register_check("mem", "usage",
                               lambda: (False, 0.3, "High"), 0.5)
    
    def test_run_check(self):
        """Should run check."""
        result = self.sc.run_check("cpu:temp")
        self.assertIsNotNone(result)
        self.assertTrue(result.passed)
        print(f"  [PASS] Check: {result.check_name}={result.passed}")
    
    def test_run_all(self):
        """Should run all checks."""
        results = self.sc.run_all()
        self.assertEqual(len(results), 2)
        print(f"  [PASS] All: {len(results)} checks")
    
    def test_failures(self):
        """Should identify failures."""
        self.sc.run_all()
        failures = self.sc.get_failures()
        self.assertEqual(len(failures), 1)
        print(f"  [PASS] Failures: {len(failures)}")
    
    def test_pass_rate(self):
        """Should compute pass rate."""
        self.sc.run_all()
        rate = self.sc.pass_rate()
        self.assertEqual(rate, 0.5)
        print(f"  [PASS] Rate: {rate}")


class TestSelfDiagnostics(unittest.TestCase):
    """Test unified self diagnostics."""
    
    def setUp(self):
        self.sd = SelfDiagnostics()
        self.sd.register_component("cpu")
        self.sd.register_component("mem")
        self.sd.add_fault_rule("thermal", ["high_temp", "fan_off"])
        self.sd.register_check("cpu", "temp", lambda: (True, 0.7, "OK"), 0.5)
    
    def test_update_health(self):
        """Should update health."""
        self.sd.update_component_health("cpu", 0.8)
        self.assertEqual(self.sd.health.get_status("cpu"), HealthStatus.HEALTHY)
        print("  [PASS] Update: healthy")
    
    def test_run_diagnostics(self):
        """Should run diagnostics."""
        self.sd.update_component_health("cpu", 0.9)
        self.sd.update_component_health("mem", 0.8)
        result = self.sd.run_diagnostics()
        self.assertIn("checks_run", result)
        self.assertIn("overall_health", result)
        print(f"  [PASS] Diagnostics: {result['checks_run']} checks, health={result['overall_health']:.2f}")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.sd.diagnostics_summary()
        self.assertEqual(summary["monitored_components"], 2)
        print(f"  [PASS] Summary: {summary['monitored_components']} components")


if __name__ == '__main__':
    unittest.main(verbosity=2)
