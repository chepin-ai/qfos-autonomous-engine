"""
Unit tests for system health monitor module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from system_health_monitor import SystemHealthMonitor, HealthMetric, AnomalyDetector, AlertLevel


class TestAnomalyDetector(unittest.TestCase):
    """Test anomaly detector."""
    
    def setUp(self):
        self.det = AnomalyDetector(window_size=5, threshold_sigma=2.0)
    
    def test_add_sample(self):
        """Should add sample."""
        self.det.add_sample(10.0)
        self.assertEqual(len(self.det.history), 1)
        print("  [PASS] Sample added")
    
    def test_not_anomalous(self):
        """Should not flag normal values."""
        for v in [10.0, 11.0, 10.5, 11.5, 10.0]:
            self.det.add_sample(v)
        is_anom, z = self.det.is_anomalous(10.5)
        self.assertFalse(is_anom)
        print(f"  [PASS] Normal: z={z:.2f}")
    
    def test_anomalous(self):
        """Should flag anomalous value."""
        for v in [10.0, 11.0, 10.5, 11.5, 10.0]:
            self.det.add_sample(v)
        is_anom, z = self.det.is_anomalous(50.0)
        self.assertTrue(is_anom)
        print(f"  [PASS] Anomaly: z={z:.2f}")
    
    def test_trend_increasing(self):
        """Should detect increasing trend."""
        for v in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
            self.det.add_sample(v)
        self.assertEqual(self.det.trend(), "increasing")
        print("  [PASS] Trend: increasing")
    
    def test_trend_stable(self):
        """Should detect stable trend."""
        for v in [10.0, 10.1, 10.0, 10.2, 10.1]:
            self.det.add_sample(v)
        self.assertEqual(self.det.trend(), "stable")
        print("  [PASS] Trend: stable")


class TestSystemHealthMonitor(unittest.TestCase):
    """Test health monitor."""
    
    def setUp(self):
        self.mon = SystemHealthMonitor()
        self.mon.register_metric(HealthMetric(
            "temperature", "C",
            nominal_min=15.0, nominal_max=35.0,
            warning_min=10.0, warning_max=50.0,
            critical_min=0.0, critical_max=80.0
        ))
    
    def test_register_metric(self):
        """Should register metric."""
        self.assertEqual(len(self.mon.metrics), 1)
        print("  [PASS] Metric: registered")
    
    def test_record_sample(self):
        """Should record sample."""
        self.mon.record_sample("temperature", 25.0)
        self.assertEqual(len(self.mon.metrics["temperature"].samples), 1)
        print("  [PASS] Sample: recorded")
    
    def test_threshold_warning(self):
        """Should detect warning threshold."""
        self.mon.record_sample("temperature", 55.0)
        alerts = self.mon.get_active_alerts(AlertLevel.WARNING)
        self.assertGreater(len(alerts), 0)
        print(f"  [PASS] Warning: {len(alerts)} alert(s)")
    
    def test_threshold_critical(self):
        """Should detect critical threshold."""
        self.mon.record_sample("temperature", 85.0)
        alerts = self.mon.get_active_alerts(AlertLevel.CRITICAL)
        self.assertGreater(len(alerts), 0)
        print(f"  [PASS] Critical: {len(alerts)} alert(s)")
    
    def test_metric_stats(self):
        """Should compute stats."""
        for v in [20.0, 22.0, 21.0, 23.0, 20.0]:
            self.mon.record_sample("temperature", v)
        stats = self.mon.get_metric_stats("temperature")
        self.assertEqual(stats["samples"], 5)
        self.assertEqual(stats["trend"], "stable")
        print(f"  [PASS] Stats: mean={stats['mean']:.1f}, trend={stats['trend']}")
    
    def test_health_dashboard(self):
        """Should generate dashboard."""
        self.mon.record_sample("temperature", 25.0)
        dash = self.mon.health_dashboard()
        self.assertIn("overall_health", dash)
        print(f"  [PASS] Dashboard: health={dash['overall_health']:.1f}%")
    
    def test_detect_aging(self):
        """Should detect degradation."""
        # Simulate degradation: values decreasing
        for i in range(30):
            self.mon.record_sample("temperature", 30.0 - i * 0.5)
        aging = self.mon.detect_aging("temperature")
        self.assertIsNotNone(aging)
        print(f"  [PASS] Aging: change={aging['change_percent']:.1f}%, degrading={aging['degrading']}")
    
    def test_clear_alert(self):
        """Should clear alerts."""
        self.mon.record_sample("temperature", 55.0)
        self.mon.clear_alert("temperature")
        alerts = self.mon.get_active_alerts()
        self.assertEqual(len(alerts), 0)
        print("  [PASS] Alerts: cleared")


if __name__ == '__main__':
    unittest.main(verbosity=2)
