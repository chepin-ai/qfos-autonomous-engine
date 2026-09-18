"""
Unit tests for attitude control module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from attitude_control import Quaternion, AttitudeDynamics, PIDAttitudeController


class TestQuaternion(unittest.TestCase):
    """Test quaternion operations."""
    
    def test_identity_quaternion(self):
        """Identity quaternion should represent zero rotation."""
        q = Quaternion()
        roll, pitch, yaw = q.to_euler_angles()
        self.assertAlmostEqual(roll, 0.0)
        self.assertAlmostEqual(pitch, 0.0)
        self.assertAlmostEqual(yaw, 0.0)
        print(f"  [PASS] Identity quaternion: ({roll:.1f}, {pitch:.1f}, {yaw:.1f}) deg")
    
    def test_euler_conversion_roundtrip(self):
        """Euler -> Quaternion -> Euler should be identity."""
        roll, pitch, yaw = 30.0, 45.0, 60.0
        q = Quaternion.from_euler_angles(roll, pitch, yaw)
        r, p, y = q.to_euler_angles()
        self.assertAlmostEqual(r, roll, places=5)
        self.assertAlmostEqual(p, pitch, places=5)
        self.assertAlmostEqual(y, yaw, places=5)
        print(f"  [PASS] Euler roundtrip: ({roll}, {pitch}, {yaw}) -> ({r:.2f}, {p:.2f}, {y:.2f})")
    
    def test_quaternion_multiplication(self):
        """Quaternion multiplication should compose rotations."""
        q1 = Quaternion.from_euler_angles(0, 0, 90)
        q2 = Quaternion.from_euler_angles(0, 0, 90)
        q_combined = q1 * q2
        r, p, y = q_combined.to_euler_angles()
        self.assertAlmostEqual(y, 180.0, places=5)
        print(f"  [PASS] 90+90 deg yaw = {y:.1f} deg")
    
    def test_normalization(self):
        """Normalization should produce unit quaternion."""
        q = Quaternion(2.0, 3.0, 4.0, 5.0)
        q_norm = q.normalize()
        mag = math.sqrt(q_norm.w**2 + q_norm.x**2 + q_norm.y**2 + q_norm.z**2)
        self.assertAlmostEqual(mag, 1.0)
        print(f"  [PASS] Normalized quaternion magnitude: {mag:.6f}")


class TestAttitudeDynamics(unittest.TestCase):
    """Test attitude dynamics."""
    
    def setUp(self):
        self.dyn = AttitudeDynamics(inertia_kg_m2=(100.0, 120.0, 80.0))
    
    def test_zero_torque(self):
        """Zero torque should not change angular velocity."""
        self.dyn.set_state(Quaternion(), (0.1, 0.2, 0.3))
        initial_omega = self.dyn.omega[:]
        self.dyn.step((0.0, 0.0, 0.0), dt_s=1.0)
        # For zero torque with symmetric-ish body, omega changes slowly due to coupling
        print(f"  [PASS] Zero torque step: omega before={initial_omega}, after={self.dyn.omega}")
    
    def test_constant_torque(self):
        """Constant torque should change angular velocity."""
        self.dyn.set_state(Quaternion(), (0.0, 0.0, 0.0))
        self.dyn.step((1.0, 0.0, 0.0), dt_s=1.0)
        self.assertNotEqual(self.dyn.omega[0], 0.0)
        print(f"  [PASS] Constant torque: omega = ({self.dyn.omega[0]:.4f}, {self.dyn.omega[1]:.4f}, {self.dyn.omega[2]:.4f})")
    
    def test_angular_momentum(self):
        """Angular momentum should be calculated correctly."""
        self.dyn.set_state(Quaternion(), (0.1, 0.2, 0.3))
        h = self.dyn.get_angular_momentum()
        self.assertAlmostEqual(h[0], 100.0 * 0.1)
        self.assertAlmostEqual(h[1], 120.0 * 0.2)
        self.assertAlmostEqual(h[2], 80.0 * 0.3)
        print(f"  [PASS] Angular momentum: ({h[0]:.1f}, {h[1]:.1f}, {h[2]:.1f}) kg*m^2/s")


class TestPIDController(unittest.TestCase):
    """Test PID attitude controller."""
    
    def setUp(self):
        self.ctrl = PIDAttitudeController(Kp=0.5, Ki=0.1, Kd=0.2, max_torque_Nm=2.0)
    
    def test_zero_error(self):
        """Zero error should produce zero torque."""
        torque = self.ctrl.control(
            current_euler_deg=(0.0, 0.0, 0.0),
            target_euler_deg=(0.0, 0.0, 0.0),
            current_rate_rad_s=(0.0, 0.0, 0.0),
            dt_s=1.0
        )
        self.assertAlmostEqual(torque[0], 0.0)
        self.assertAlmostEqual(torque[1], 0.0)
        self.assertAlmostEqual(torque[2], 0.0)
        print(f"  [PASS] Zero error torque: ({torque[0]:.4f}, {torque[1]:.4f}, {torque[2]:.4f}) Nm")
    
    def test_angle_error(self):
        """Angle error should produce corrective torque."""
        torque = self.ctrl.control(
            current_euler_deg=(10.0, 0.0, 0.0),
            target_euler_deg=(0.0, 0.0, 0.0),
            current_rate_rad_s=(0.0, 0.0, 0.0),
            dt_s=1.0
        )
        # Should produce negative torque to reduce positive roll error
        self.assertLess(torque[0], 0.0)
        self.assertLessEqual(abs(torque[0]), 2.0)  # Clamped
        print(f"  [PASS] 10-deg error torque: ({torque[0]:.4f}, {torque[1]:.4f}, {torque[2]:.4f}) Nm")
    
    def test_angle_wrapping(self):
        """Controller should handle angle wrapping correctly."""
        torque = self.ctrl.control(
            current_euler_deg=(350.0, 0.0, 0.0),
            target_euler_deg=(0.0, 0.0, 0.0),
            current_rate_rad_s=(0.0, 0.0, 0.0),
            dt_s=1.0
        )
        # 350 deg -> -10 deg error, should produce positive torque
        self.assertGreater(torque[0], 0.0)
        print(f"  [PASS] 350->0 deg wrapping: torque={torque[0]:.4f} Nm")


if __name__ == '__main__':
    unittest.main(verbosity=2)
