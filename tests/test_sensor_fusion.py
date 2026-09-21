"""
Unit tests for sensor fusion module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sensor_fusion import (SensorReading, KalmanFilter1D,
                           ComplementaryFilter,
                           ParticleFilter,
                           MultiSensorFusion,
                           SensorFusion)


class TestKalmanFilter1D(unittest.TestCase):
    """Test Kalman."""
    
    def setUp(self):
        self.kf = KalmanFilter1D(1e-5, 0.1, 0.0)
    
    def test_update(self):
        """Should update."""
        e = self.kf.update(1.0)
        self.assertGreater(e, 0)
        print(f"  [PASS] KF: {e:.4f}")
    
    def test_convergence(self):
        """Should converge."""
        for _ in range(10):
            self.kf.update(5.0)
        e = self.kf.get_estimate()
        self.assertAlmostEqual(e, 5.0, delta=0.5)
        print(f"  [PASS] Conv: {e:.4f}")


class TestComplementaryFilter(unittest.TestCase):
    """Test complementary."""
    
    def setUp(self):
        self.cf = ComplementaryFilter(0.98)
    
    def test_update(self):
        """Should update."""
        a = self.cf.update(10.0, 45.0, 0.01)
        self.assertIsNotNone(a)
        print(f"  [PASS] CF: {a:.4f}")


class TestParticleFilter(unittest.TestCase):
    """Test particle."""
    
    def setUp(self):
        self.pf = ParticleFilter(50, (-5.0, 5.0))
    
    def test_estimate(self):
        """Should estimate."""
        e = self.pf.estimate()
        self.assertIsNotNone(e)
        print(f"  [PASS] PF: {e:.4f}")
    
    def test_update(self):
        """Should update."""
        self.pf.predict(1.0, 0.1)
        self.pf.update(2.0, 0.5)
        e = self.pf.estimate()
        self.assertIsNotNone(e)
        print(f"  [PASS] Upd: {e:.4f}")


class TestMultiSensorFusion(unittest.TestCase):
    """Test multi-sensor."""
    
    def setUp(self):
        self.msf = MultiSensorFusion()
    
    def test_add_and_update(self):
        """Should add and update."""
        self.msf.add_sensor("s1", 1e-5, 0.1)
        e = self.msf.update("s1", 3.0)
        self.assertIsNotNone(e)
        print(f"  [PASS] MS: {e:.4f}")
    
    def test_fused(self):
        """Should fuse."""
        self.msf.add_sensor("s1", 1e-5, 0.1)
        self.msf.add_sensor("s2", 1e-5, 0.1)
        self.msf.update("s1", 5.0)
        self.msf.update("s2", 5.0)
        f = self.msf.fused_estimate()
        self.assertAlmostEqual(f, 5.0, delta=0.5)
        print(f"  [PASS] Fus: {f:.4f}")


class TestSensorFusion(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sf = SensorFusion()
    
    def test_summary(self):
        """Should summarize."""
        s = self.sf.sf_summary()
        self.assertIn("filters", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
