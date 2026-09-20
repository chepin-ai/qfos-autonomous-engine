"""
Unit tests for inertial navigation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from inertial_nav import (IMUReading, Quaternion,
                          AttitudeEstimator, DeadReckoning,
                          InertialNav)


class TestQuaternion(unittest.TestCase):
    """Test quaternion."""
    
    def test_normalize(self):
        """Should normalize."""
        q = Quaternion(2.0, 0.0, 0.0, 0.0)
        q.normalize()
        self.assertAlmostEqual(q.w, 1.0)
        print("  [PASS] Normalize: 1.0")
    
    def test_identity_euler(self):
        """Should convert identity to zero Euler."""
        q = Quaternion()
        roll, pitch, yaw = q.to_euler()
        self.assertAlmostEqual(roll, 0.0)
        self.assertAlmostEqual(pitch, 0.0)
        self.assertAlmostEqual(yaw, 0.0)
        print("  [PASS] Identity: (0,0,0)")
    
    def test_from_euler(self):
        """Should set from Euler."""
        q = Quaternion()
        q.from_euler(0.0, math.pi/4, 0.0)
        roll, pitch, yaw = q.to_euler()
        self.assertAlmostEqual(pitch, math.pi/4, places=5)
        print(f"  [PASS] From euler: pitch={math.degrees(pitch):.1f}")
    
    def test_rotate_vector(self):
        """Should rotate vector."""
        q = Quaternion()
        q.from_euler(0.0, 0.0, math.pi/2)
        rx, ry, rz = q.rotate_vector(1.0, 0.0, 0.0)
        self.assertAlmostEqual(rx, 0.0, places=5)
        self.assertAlmostEqual(ry, 1.0, places=5)
        print(f"  [PASS] Rotate: ({rx:.3f}, {ry:.3f})")


class TestAttitudeEstimator(unittest.TestCase):
    """Test attitude estimator."""
    
    def setUp(self):
        self.ae = AttitudeEstimator()
    
    def test_initial_attitude(self):
        """Should start level."""
        roll, pitch, yaw = self.ae.get_euler()
        self.assertAlmostEqual(roll, 0.0)
        self.assertAlmostEqual(pitch, 0.0)
        print("  [PASS] Initial: level")
    
    def test_update_gyro(self):
        """Should update from gyro."""
        self.ae.update_gyro(0.0, 0.0, math.pi/4, 1.0)
        roll, pitch, yaw = self.ae.get_euler()
        self.assertGreater(abs(yaw), 0)
        print(f"  [PASS] Gyro: yaw={math.degrees(yaw):.1f}")
    
    def test_correct_accel(self):
        """Should correct with accel."""
        self.ae.correct_accel(0.0, 0.0, 9.81)
        roll, pitch, yaw = self.ae.get_euler()
        self.assertAlmostEqual(roll, 0.0, places=2)
        self.assertAlmostEqual(pitch, 0.0, places=2)
        print("  [PASS] Accel: corrected")


class TestDeadReckoning(unittest.TestCase):
    """Test dead reckoning."""
    
    def setUp(self):
        self.dr = DeadReckoning()
    
    def test_update(self):
        """Should update position."""
        r1 = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, 0.0)
        r2 = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, 0.1)
        self.dr.update(r1)
        self.dr.update(r2)
        self.assertEqual(len(self.dr.readings), 2)
        print("  [PASS] Update: 2 readings")
    
    def test_drift(self):
        """Should estimate drift."""
        for i in range(10):
            r = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, i * 0.01)
            self.dr.update(r)
        drift = self.dr.drift_estimate()
        self.assertGreater(drift, 0)
        print(f"  [PASS] Drift: {drift:.3f} m")
    
    def test_reset(self):
        """Should reset state."""
        self.dr.update(IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, 0.0))
        self.dr.reset()
        self.assertEqual(len(self.dr.readings), 0)
        self.assertEqual(self.dr.position, (0.0, 0.0, 0.0))
        print("  [PASS] Reset")


class TestInertialNav(unittest.TestCase):
    """Test unified inertial navigation."""
    
    def setUp(self):
        self.inav = InertialNav()
    
    def test_not_calibrated(self):
        """Should not be calibrated initially."""
        self.assertFalse(self.inav.calibrated)
        print("  [PASS] Not calibrated")
    
    def test_calibration(self):
        """Should auto-calibrate."""
        for i in range(15):
            r = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, i * 0.01)
            self.inav.feed_imu(r)
        self.assertTrue(self.inav.calibrated)
        print("  [PASS] Calibrated")
    
    def test_position(self):
        """Should estimate position."""
        for i in range(15):
            r = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, i * 0.01)
            self.inav.feed_imu(r)
        pos = self.inav.get_position()
        self.assertEqual(len(pos), 3)
        print(f"  [PASS] Position: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")
    
    def test_attitude(self):
        """Should estimate attitude."""
        for i in range(15):
            r = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, i * 0.01)
            self.inav.feed_imu(r)
        roll, pitch, yaw = self.inav.get_attitude()
        self.assertIsInstance(roll, float)
        print(f"  [PASS] Attitude: r={math.degrees(roll):.1f}, p={math.degrees(pitch):.1f}")
    
    def test_reset(self):
        """Should reset."""
        for i in range(15):
            r = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, i * 0.01)
            self.inav.feed_imu(r)
        self.inav.reset()
        self.assertFalse(self.inav.calibrated)
        self.assertEqual(self.inav.get_position(), (0.0, 0.0, 0.0))
        print("  [PASS] Reset")
    
    def test_summary(self):
        """Should provide summary."""
        for i in range(15):
            r = IMUReading(0.0, 0.0, 9.81, 0.0, 0.0, 0.0, i * 0.01)
            self.inav.feed_imu(r)
        summary = self.inav.nav_summary()
        self.assertIn("position_m", summary)
        self.assertIn("calibrated", summary)
        print(f"  [PASS] Summary: cal={summary['calibrated']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
