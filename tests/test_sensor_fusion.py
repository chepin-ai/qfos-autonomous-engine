"""
Unit tests for sensor fusion module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sensor_fusion import SensorReading, SensorFusionEngine


class TestSensorFusion(unittest.TestCase):
    """Test sensor fusion engine."""
    
    def setUp(self):
        self.engine = SensorFusionEngine()
    
    def test_single_sensor_fusion(self):
        """Should return reading when only one sensor."""
        r = SensorReading(
            sensor_type='radar',
            position_m=(1e6, 2e6, 3e6),
            velocity_ms=(100, 200, 300),
            timestamp=0.0,
            uncertainty_m=100.0,
            confidence=0.9
        )
        self.engine.add_reading(r)
        fused = self.engine.fuse()
        
        self.assertIsNotNone(fused)
        self.assertEqual(fused.sensor_count, 1)
        self.assertAlmostEqual(fused.position_m[0], 1e6)
        print(f"  [PASS] Single sensor fused: pos=({fused.position_m[0]:.0e}, ...)")
    
    def test_multi_sensor_fusion(self):
        """Should average multiple sensor readings."""
        r1 = SensorReading('radar', (1e6, 0, 0), (100, 0, 0), 0.0, 100.0, 0.9)
        r2 = SensorReading('lidar', (1.01e6, 0, 0), (102, 0, 0), 0.0, 50.0, 0.95)
        r3 = SensorReading('optical', (0.99e6, 0, 0), (98, 0, 0), 0.0, 200.0, 0.8)
        
        for r in [r1, r2, r3]:
            self.engine.add_reading(r)
        
        fused = self.engine.fuse()
        self.assertIsNotNone(fused)
        self.assertEqual(fused.sensor_count, 3)
        # Should be close to weighted average (lidar has highest weight)
        self.assertGreater(fused.position_m[0], 0.99e6)
        self.assertLess(fused.position_m[0], 1.01e6)
        print(f"  [PASS] 3-sensor fusion: pos={fused.position_m[0]:.0f} m, unc={fused.position_uncertainty_m:.1f} m")
    
    def test_anomaly_detection(self):
        """Should detect anomalous reading."""
        r1 = SensorReading('radar', (1e6, 0, 0), (100, 0, 0), 0.0, 100.0, 0.9)
        r2 = SensorReading('radar', (1.001e6, 0, 0), (101, 0, 0), 0.0, 100.0, 0.9)
        r_bad = SensorReading('radar', (2e6, 0, 0), (500, 0, 0), 0.0, 100.0, 0.3)
        
        for r in [r1, r2]:
            self.engine.add_reading(r)
        fused = self.engine.fuse()
        
        is_anomaly = self.engine.detect_anomaly(r_bad, fused, threshold_sigma=3.0)
        self.assertTrue(is_anomaly)
        print(f"  [PASS] Anomaly detected for outlier at {r_bad.position_m[0]:.0e} m")
    
    def test_sensor_health(self):
        """Should report sensor health status."""
        r1 = SensorReading('radar', (1e6, 0, 0), (100, 0, 0), 0.0, 100.0, 0.9)
        r2 = SensorReading('star_tracker', (1e6, 0, 0), (100, 0, 0), 0.0, 10.0, 0.98)
        
        for r in [r1, r2]:
            self.engine.add_reading(r)
        
        health = self.engine.get_sensor_health()
        self.assertIn('radar', health)
        self.assertIn('star_tracker', health)
        self.assertEqual(health['radar']['status'], 'HEALTHY')
        self.assertEqual(health['star_tracker']['status'], 'HEALTHY')
        print(f"  [PASS] Sensor health: {len(health)} types, radar={health['radar']['avg_confidence']}")
    
    def test_empty_fusion(self):
        """Should return None with no readings."""
        fused = self.engine.fuse()
        self.assertIsNone(fused)
        print("  [PASS] Empty fusion returns None")


if __name__ == '__main__':
    unittest.main(verbosity=2)
