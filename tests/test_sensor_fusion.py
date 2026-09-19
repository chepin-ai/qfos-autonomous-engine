"""
Unit tests for sensor fusion module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sensor_fusion import KalmanFusion, IMUProcessor, SensorFusion, SensorReading, FusedState


class TestKalmanFusion(unittest.TestCase):
    """Test Kalman filter fusion."""
    
    def setUp(self):
        self.kf = KalmanFusion(state_dim=6)
    
    def test_initial_state(self):
        """Should initialize to zero."""
        state = self.kf.get_state()
        self.assertEqual(len(state), 6)
        self.assertEqual(sum(state), 0.0)
        print("  [PASS] Init: 6D zero")
    
    def test_predict(self):
        """Should predict state."""
        self.kf.state = [1.0, 2.0, 3.0, 1.0, 0.0, 0.0]
        self.kf.predict(dt=1.0)
        pos = self.kf.get_position()
        self.assertEqual(pos[0], 2.0)  # 1 + 1*1
        print(f"  [PASS] Predict: pos={pos}")
    
    def test_update(self):
        """Should update with measurement."""
        reading = SensorReading(
            sensor_id="gps",
            timestamp=0.0,
            values=[5.0, 5.0, 5.0],
            covariance=[[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]]
        )
        H = [[1, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0],
             [0, 0, 1, 0, 0, 0]]
        self.kf.update(reading, H)
        pos = self.kf.get_position()
        self.assertNotEqual(sum(pos), 0.0)
        print(f"  [PASS] Update: pos={pos}")
    
    def test_get_position(self):
        """Should get position."""
        self.kf.state = [10.0, 20.0, 30.0, 0, 0, 0]
        pos = self.kf.get_position()
        self.assertEqual(pos, [10.0, 20.0, 30.0])
        print(f"  [PASS] Position: {pos}")
    
    def test_get_velocity(self):
        """Should get velocity."""
        self.kf.state = [0, 0, 0, 5.0, 10.0, 15.0]
        vel = self.kf.get_velocity()
        self.assertEqual(vel, [5.0, 10.0, 15.0])
        print(f"  [PASS] Velocity: {vel}")


class TestIMUProcessor(unittest.TestCase):
    """Test IMU processor."""
    
    def setUp(self):
        self.imu = IMUProcessor()
    
    def test_process_accel(self):
        """Should calibrate acceleration."""
        raw = [9.81, 0.0, 0.0]
        calibrated = self.imu.process_accel(raw)
        self.assertEqual(calibrated, raw)  # No bias yet
        print(f"  [PASS] Accel: {calibrated}")
    
    def test_process_gyro(self):
        """Should calibrate gyroscope."""
        raw = [0.1, 0.2, 0.3]
        calibrated = self.imu.process_gyro(raw)
        self.assertEqual(calibrated, raw)
        print(f"  [PASS] Gyro: {calibrated}")
    
    def test_integrate_velocity(self):
        """Should integrate to velocity."""
        accel = [1.0, 0.0, 0.0]
        current = [0.0, 0.0, 0.0]
        vel = self.imu.integrate_velocity(accel, 2.0, current)
        self.assertEqual(vel[0], 2.0)
        print(f"  [PASS] Integrate: {vel}")
    
    def test_calibrate_bias(self):
        """Should calibrate biases."""
        samples = [[0.0, 0.0, 9.8], [0.0, 0.0, 9.9]]
        self.imu.calibrate_bias(samples, [])
        self.assertAlmostEqual(self.imu.accel_bias[2], 9.85, places=5)
        print(f"  [PASS] Bias: {self.imu.accel_bias[2]:.2f}")


class TestSensorFusion(unittest.TestCase):
    """Test unified sensor fusion."""
    
    def setUp(self):
        self.sf = SensorFusion(state_dim=6)
    
    def test_fuse_gps(self):
        """Should fuse GPS reading."""
        reading = SensorReading(
            sensor_id="gps",
            timestamp=0.0,
            values=[100.0, 200.0, 300.0],
            covariance=[[10.0, 0, 0], [0, 10.0, 0], [0, 0, 10.0]]
        )
        self.sf.fuse_gps(reading, dt=1.0)
        pos = self.sf.kalman.get_position()
        self.assertNotEqual(sum(pos), 0.0)
        print(f"  [PASS] GPS fuse: {pos}")
    
    def test_fuse_imu(self):
        """Should fuse IMU reading."""
        self.sf.fuse_imu([0.0, 0.0, 9.8], [0.0, 0.0, 0.0], dt=1.0)
        vel = self.sf.kalman.get_velocity()
        self.assertIsNotNone(vel)
        print(f"  [PASS] IMU fuse: {vel}")
    
    def test_get_fused_state(self):
        """Should get fused state."""
        reading = SensorReading(
            sensor_id="gps",
            timestamp=0.0,
            values=[10.0, 20.0, 30.0],
            covariance=[[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]]
        )
        self.sf.fuse_gps(reading, dt=1.0)
        state = self.sf.get_fused_state()
        self.assertIsInstance(state, FusedState)
        self.assertEqual(len(state.position), 3)
        print(f"  [PASS] State: pos={state.position}")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.sf.fusion_summary()
        self.assertEqual(summary["state_dim"], 6)
        print(f"  [PASS] Summary: {summary['state_dim']}D")


if __name__ == '__main__':
    unittest.main(verbosity=2)
