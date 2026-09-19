"""
Unit tests for predictive analytics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from predictive_analytics import MovingAveragePredictor, AnomalyDetector, DegradationPredictor, TelemetryPredictor


class TestMovingAveragePredictor(unittest.TestCase):
    """Test moving average predictor."""
    
    def setUp(self):
        self.ma = MovingAveragePredictor(window_size=5)
    
    def test_predict(self):
        """Should predict next value."""
        for v in [10.0, 11.0, 12.0, 13.0, 14.0]:
            self.ma.update(v)
        pred = self.ma.predict()
        self.assertIsNotNone(pred)
        self.assertGreater(pred, 10.0)
        print(f"  [PASS] Predict: {pred:.2f}")
    
    def test_trend(self):
        """Should detect trend."""
        for v in [1.0, 2.0, 3.0, 4.0, 5.0]:
            self.ma.update(v)
        trend = self.ma.trend()
        self.assertGreater(trend, 0)
        print(f"  [PASS] Trend: {trend:.2f} (increasing)")
    
    def test_not_enough_data(self):
        """Should return None with insufficient data."""
        self.ma.update(1.0)
        pred = self.ma.predict()
        self.assertIsNone(pred)
        print("  [PASS] No data: None")


class TestAnomalyDetector(unittest.TestCase):
    """Test anomaly detector."""
    
    def setUp(self):
        self.ad = AnomalyDetector(z_threshold=2.0)
    
    def test_normal(self):
        """Should classify normal values."""
        for v in [10.0, 11.0, 10.5, 11.5, 10.2]:
            result = self.ad.update(v)
        self.assertFalse(result["is_anomaly"])
        print(f"  [PASS] Normal: z={result['z_score']:.2f}")
    
    def test_anomaly(self):
        """Should detect anomaly."""
        for v in [10.0, 10.5, 10.2, 10.8, 10.1, 10.3, 10.6]:
            self.ad.update(v)
        result = self.ad.update(500.0)
        self.assertTrue(result["is_anomaly"])
        print(f"  [PASS] Anomaly: z={result['z_score']:.2f}")
    
    def test_get_anomalies(self):
        """Should retrieve anomalies."""
        for v in [10.0, 10.5, 10.2, 10.8, 10.1, 10.3, 10.6]:
            self.ad.update(v)
        self.ad.update(500.0)
        anomalies = self.ad.get_anomalies()
        self.assertGreater(len(anomalies), 0)
        print(f"  [PASS] Anomalies: {len(anomalies)}")


class TestDegradationPredictor(unittest.TestCase):
    """Test degradation predictor."""
    
    def setUp(self):
        self.dp = DegradationPredictor()
    
    def test_predict_time(self):
        """Should predict time to threshold."""
        for t, h in [(0, 1.0), (1, 0.9), (2, 0.8), (3, 0.7), (4, 0.6)]:
            self.dp.add_measurement(t, h)
        time_to = self.dp.predict_time_to_threshold(0.1)
        self.assertIsNotNone(time_to)
        self.assertGreater(time_to, 0)
        print(f"  [PASS] Time to critical: {time_to:.1f}s")
    
    def test_health_status(self):
        """Should assess health status."""
        self.dp.add_measurement(0, 0.5)
        status = self.dp.get_health_status()
        self.assertEqual(status["status"], "nominal")
        print(f"  [PASS] Status: {status['status']}")
    
    def test_not_degrading(self):
        """Should return None if not degrading."""
        for t, h in [(0, 0.5), (1, 0.5), (2, 0.5)]:
            self.dp.add_measurement(t, h)
        time_to = self.dp.predict_time_to_threshold()
        self.assertIsNone(time_to)
        print("  [PASS] Not degrading: None")


class TestTelemetryPredictor(unittest.TestCase):
    """Test telemetry predictor."""
    
    def setUp(self):
        self.tp = TelemetryPredictor()
    
    def test_update(self):
        """Should update channel."""
        result = self.tp.update("temp", 25.0)
        self.assertEqual(result["channel"], "temp")
        print(f"  [PASS] Update: {result['value']}")
    
    def test_predict(self):
        """Should predict channel value."""
        for v in [20.0, 21.0, 22.0, 23.0, 24.0]:
            self.tp.update("temp", v)
        result = self.tp.update("temp", 25.0)
        self.assertIsNotNone(result["prediction"])
        print(f"  [PASS] Predict: {result['prediction']:.2f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.tp.update("temp", 25.0)
        self.tp.update("pressure", 101.0)
        summary = self.tp.get_summary()
        self.assertEqual(summary["channels"], 2)
        print(f"  [PASS] Summary: {summary['channels']} channels")


if __name__ == '__main__':
    unittest.main(verbosity=2)
