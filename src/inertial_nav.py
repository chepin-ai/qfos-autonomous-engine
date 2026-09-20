"""
Inertial Navigation Module
IMU integration, attitude estimation, and dead reckoning
for autonomous system navigation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class IMUReading:
    """Inertial measurement unit reading."""
    accel_x_ms2: float = 0.0
    accel_y_ms2: float = 0.0
    accel_z_ms2: float = 0.0
    gyro_x_rads: float = 0.0
    gyro_y_rads: float = 0.0
    gyro_z_rads: float = 0.0
    timestamp_s: float = 0.0


class Quaternion:
    """
    Quaternion attitude representation.
    """
    
    def __init__(self, w: float = 1.0, x: float = 0.0,
                 y: float = 0.0, z: float = 0.0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z
    
    def normalize(self):
        """Normalize quaternion."""
        norm = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if norm > 0:
            self.w /= norm
            self.x /= norm
            self.y /= norm
            self.z /= norm
    
    def to_euler(self) -> Tuple[float, float, float]:
        """
        Convert to Euler angles (roll, pitch, yaw).
        
        Returns:
            (roll_rad, pitch_rad, yaw_rad)
        """
        # Roll
        sinr_cosp = 2.0 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1.0 - 2.0 * (self.x**2 + self.y**2)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch
        sinp = 2.0 * (self.w * self.y - self.z * self.x)
        sinp = max(-1.0, min(1.0, sinp))
        pitch = math.asin(sinp)
        
        # Yaw
        siny_cosp = 2.0 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1.0 - 2.0 * (self.y**2 + self.z**2)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return (roll, pitch, yaw)
    
    def from_euler(self, roll_rad: float, pitch_rad: float, yaw_rad: float):
        """
        Set from Euler angles.
        
        Args:
            roll_rad: Roll angle
            pitch_rad: Pitch angle
            yaw_rad: Yaw angle
        """
        cr = math.cos(roll_rad * 0.5)
        sr = math.sin(roll_rad * 0.5)
        cp = math.cos(pitch_rad * 0.5)
        sp = math.sin(pitch_rad * 0.5)
        cy = math.cos(yaw_rad * 0.5)
        sy = math.sin(yaw_rad * 0.5)
        
        self.w = cr * cp * cy + sr * sp * sy
        self.x = sr * cp * cy - cr * sp * sy
        self.y = cr * sp * cy + sr * cp * sy
        self.z = cr * cp * sy - sr * sp * cy
        self.normalize()
    
    def rotate_vector(self, vx: float, vy: float, vz: float
                     ) -> Tuple[float, float, float]:
        """
        Rotate a vector by quaternion.
        
        Args:
            vx, vy, vz: Vector components
        
        Returns:
            Rotated vector
        """
        # q * v * q_conj
        tx = 2.0 * (self.y * vz - self.z * vy)
        ty = 2.0 * (self.z * vx - self.x * vz)
        tz = 2.0 * (self.x * vy - self.y * vx)
        
        rx = vx + self.w * tx + (self.y * tz - self.z * ty)
        ry = vy + self.w * ty + (self.z * tx - self.x * tz)
        rz = vz + self.w * tz + (self.x * ty - self.y * tx)
        
        return (rx, ry, rz)


class AttitudeEstimator:
    """
    Estimate attitude from gyro and accel.
    """
    
    def __init__(self):
        self.quat = Quaternion()
        self.gyro_bias = (0.0, 0.0, 0.0)
        self.accel_gain = 0.02
    
    def update_gyro(self, gyro_x: float, gyro_y: float, gyro_z: float,
                   dt_s: float):
        """
        Update attitude from gyro.
        
        Args:
            gyro_x, gyro_y, gyro_z: Gyro rates (rad/s)
            dt_s: Time step
        """
        # Remove bias
        wx = gyro_x - self.gyro_bias[0]
        wy = gyro_y - self.gyro_bias[1]
        wz = gyro_z - self.gyro_bias[2]
        
        # Quaternion derivative: dq/dt = 0.5 * q * omega
        half_dt = 0.5 * dt_s
        
        qw = self.quat.w - half_dt * (self.quat.x * wx + self.quat.y * wy + self.quat.z * wz)
        qx = self.quat.x + half_dt * (self.quat.w * wx + self.quat.y * wz - self.quat.z * wy)
        qy = self.quat.y + half_dt * (self.quat.w * wy + self.quat.z * wx - self.quat.x * wz)
        qz = self.quat.z + half_dt * (self.quat.w * wz + self.quat.x * wy - self.quat.y * wx)
        
        self.quat = Quaternion(qw, qx, qy, qz)
        self.quat.normalize()
    
    def correct_accel(self, accel_x: float, accel_y: float, accel_z: float):
        """
        Correct attitude with accelerometer.
        
        Args:
            accel_x, accel_y, accel_z: Acceleration (m/s^2)
        """
        # Gravity direction in body frame
        mag = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        if mag < 0.1:
            return
        
        # Expected gravity in body frame based on current attitude
        # Gravity in NED: (0, 0, g)
        gx, gy, gz = self.quat.rotate_vector(0.0, 0.0, 9.81)
        
        # Measured gravity (normalized)
        ax = accel_x / mag * 9.81
        ay = accel_y / mag * 9.81
        az = accel_z / mag * 9.81
        
        # Error is cross product
        ex = ay * gz - az * gy
        ey = az * gx - ax * gz
        ez = ax * gy - ay * gx
        
        # Apply correction
        self.quat.w += 0.0  # no correction to scalar
        self.quat.x += self.accel_gain * ex
        self.quat.y += self.accel_gain * ey
        self.quat.z += self.accel_gain * ez
        self.quat.normalize()
    
    def get_euler(self) -> Tuple[float, float, float]:
        """Get Euler angles."""
        return self.quat.to_euler()


class DeadReckoning:
    """
    Position estimation from IMU.
    """
    
    def __init__(self):
        self.position = (0.0, 0.0, 0.0)
        self.velocity = (0.0, 0.0, 0.0)
        self.attitude = AttitudeEstimator()
        self.readings: List[IMUReading] = []
    
    def update(self, reading: IMUReading):
        """
        Update navigation state.
        
        Args:
            reading: IMU reading
        """
        self.readings.append(reading)
        
        if len(self.readings) < 2:
            return
        
        prev = self.readings[-2]
        dt = reading.timestamp_s - prev.timestamp_s
        if dt <= 0:
            dt = 0.01
        
        # Update attitude
        self.attitude.update_gyro(reading.gyro_x_rads,
                                  reading.gyro_y_rads,
                                  reading.gyro_z_rads, dt)
        self.attitude.correct_accel(reading.accel_x_ms2,
                                    reading.accel_y_ms2,
                                    reading.accel_z_ms2)
        
        # Remove gravity from accel
        roll, pitch, yaw = self.attitude.get_euler()
        grav_x = -9.81 * math.sin(pitch)
        grav_y = 9.81 * math.sin(roll) * math.cos(pitch)
        grav_z = 9.81 * math.cos(roll) * math.cos(pitch)
        
        ax = reading.accel_x_ms2 - grav_x
        ay = reading.accel_y_ms2 - grav_y
        az = reading.accel_z_ms2 - grav_z
        
        # Integrate to velocity
        vx = self.velocity[0] + ax * dt
        vy = self.velocity[1] + ay * dt
        vz = self.velocity[2] + az * dt
        
        # Integrate to position
        px = self.position[0] + vx * dt
        py = self.position[1] + vy * dt
        pz = self.position[2] + vz * dt
        
        self.velocity = (vx, vy, vz)
        self.position = (px, py, pz)
    
    def reset(self):
        """Reset navigation state."""
        self.position = (0.0, 0.0, 0.0)
        self.velocity = (0.0, 0.0, 0.0)
        self.readings.clear()
        self.attitude = AttitudeEstimator()
    
    def drift_estimate(self) -> float:
        """
        Estimate position drift.
        
        Returns:
            Drift magnitude (m)
        """
        # Simple drift grows with time and number of readings
        return len(self.readings) * 0.001


class InertialNav:
    """
    Unified inertial navigation controller.
    """
    
    def __init__(self):
        self.dead_reckoning = DeadReckoning()
        self.calibrated = False
        self.calibration_readings: List[IMUReading] = []
    
    def calibrate(self, readings: List[IMUReading]):
        """
        Calibrate IMU biases.
        
        Args:
            readings: Stationary readings
        """
        if len(readings) < 10:
            return
        
        # Average gyro readings for bias
        avg_gx = sum(r.gyro_x_rads for r in readings) / len(readings)
        avg_gy = sum(r.gyro_y_rads for r in readings) / len(readings)
        avg_gz = sum(r.gyro_z_rads for r in readings) / len(readings)
        
        self.dead_reckoning.attitude.gyro_bias = (avg_gx, avg_gy, avg_gz)
        self.calibrated = True
    
    def feed_imu(self, reading: IMUReading):
        """Feed IMU reading."""
        if not self.calibrated:
            self.calibration_readings.append(reading)
            if len(self.calibration_readings) >= 10:
                self.calibrate(self.calibration_readings)
        
        self.dead_reckoning.update(reading)
    
    def get_position(self) -> Tuple[float, float, float]:
        """Get estimated position."""
        return self.dead_reckoning.position
    
    def get_velocity(self) -> Tuple[float, float, float]:
        """Get estimated velocity."""
        return self.dead_reckoning.velocity
    
    def get_attitude(self) -> Tuple[float, float, float]:
        """Get estimated attitude (roll, pitch, yaw)."""
        return self.dead_reckoning.attitude.get_euler()
    
    def reset(self):
        """Reset navigation."""
        self.dead_reckoning.reset()
        self.calibrated = False
        self.calibration_readings.clear()
    
    def nav_summary(self) -> Dict:
        """Get navigation summary."""
        roll, pitch, yaw = self.get_attitude()
        return {
            "position_m": self.get_position(),
            "velocity_ms": self.get_velocity(),
            "attitude_rad": (roll, pitch, yaw),
            "attitude_deg": (math.degrees(roll), math.degrees(pitch), math.degrees(yaw)),
            "calibrated": self.calibrated,
            "readings": len(self.dead_reckoning.readings),
            "drift_m": self.dead_reckoning.drift_estimate()
        }
