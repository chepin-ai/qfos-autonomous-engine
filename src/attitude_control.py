"""
Attitude Dynamics and Control Module
Spacecraft attitude kinematics, dynamics, and control algorithms.
"""

import math
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class Quaternion:
    """Quaternion representing spacecraft attitude."""
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def normalize(self) -> 'Quaternion':
        """Normalize to unit quaternion."""
        mag = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if mag < 1e-15:
            return Quaternion(1.0, 0.0, 0.0, 0.0)
        return Quaternion(self.w/mag, self.x/mag, self.y/mag, self.z/mag)
    
    def to_euler_angles(self) -> Tuple[float, float, float]:
        """Convert to roll, pitch, yaw (degrees)."""
        q = self.normalize()
        
        # Roll (x-axis rotation)
        sinr_cosp = 2.0 * (q.w * q.x + q.y * q.z)
        cosr_cosp = 1.0 - 2.0 * (q.x**2 + q.y**2)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis rotation)
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        if abs(sinp) >= 1.0:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)
        
        # Yaw (z-axis rotation)
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y**2 + q.z**2)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return (math.degrees(roll), math.degrees(pitch), math.degrees(yaw))
    
    @classmethod
    def from_euler_angles(cls, roll_deg: float, pitch_deg: float, yaw_deg: float) -> 'Quaternion':
        """Create quaternion from Euler angles (degrees)."""
        roll = math.radians(roll_deg)
        pitch = math.radians(pitch_deg)
        yaw = math.radians(yaw_deg)
        
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        
        return cls(w, x, y, z).normalize()
    
    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        """Quaternion multiplication (Hamilton product)."""
        return Quaternion(
            w=self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
            x=self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
            y=self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x,
            z=self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w
        )


class AttitudeDynamics:
    """
    Spacecraft attitude dynamics using Euler's rotational equations.
    """
    
    def __init__(self, inertia_kg_m2: Tuple[float, float, float] = (100.0, 100.0, 100.0)):
        """
        Args:
            inertia_kg_m2: Principal moments of inertia (Ix, Iy, Iz)
        """
        self.Ix, self.Iy, self.Iz = inertia_kg_m2
        self.omega = [0.0, 0.0, 0.0]  # rad/s
        self.quaternion = Quaternion()
    
    def set_state(self, q: Quaternion, omega_rad_s: Tuple[float, float, float]):
        """Set current attitude state."""
        self.quaternion = q.normalize()
        self.omega = list(omega_rad_s)
    
    def step(self, torque_Nm: Tuple[float, float, float], dt_s: float):
        """
        Integrate attitude dynamics for one time step.
        
        Uses simple Euler integration of Euler's equations.
        """
        wx, wy, wz = self.omega
        Mx, My, Mz = torque_Nm
        
        # Euler's rotational equations
        dwx = (Mx - (self.Iz - self.Iy) * wy * wz) / self.Ix
        dwy = (My - (self.Ix - self.Iz) * wz * wx) / self.Iy
        dwz = (Mz - (self.Iy - self.Ix) * wx * wy) / self.Iz
        
        self.omega[0] += dwx * dt_s
        self.omega[1] += dwy * dt_s
        self.omega[2] += dwz * dt_s
        
        # Quaternion kinematics
        q = self.quaternion
        qw, qx, qy, qz = q.w, q.x, q.y, q.z
        
        # dq/dt = 0.5 * q * omega_quat
        dq_w = -0.5 * (qx*wx + qy*wy + qz*wz)
        dq_x = 0.5 * (qw*wx + qy*wz - qz*wy)
        dq_y = 0.5 * (qw*wy - qx*wz + qz*wx)
        dq_z = 0.5 * (qw*wz + qx*wy - qy*wx)
        
        self.quaternion = Quaternion(
            qw + dq_w * dt_s,
            qx + dq_x * dt_s,
            qy + dq_y * dt_s,
            qz + dq_z * dt_s
        ).normalize()
    
    def get_euler_angles_deg(self) -> Tuple[float, float, float]:
        """Get current attitude as Euler angles."""
        return self.quaternion.to_euler_angles()
    
    def get_angular_momentum(self) -> Tuple[float, float, float]:
        """Calculate angular momentum vector."""
        return (
            self.Ix * self.omega[0],
            self.Iy * self.omega[1],
            self.Iz * self.omega[2]
        )


class PIDAttitudeController:
    """
    PID controller for spacecraft attitude stabilization.
    """
    
    def __init__(self, Kp: float = 0.1, Ki: float = 0.01, Kd: float = 0.05,
                 max_torque_Nm: float = 1.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_torque = max_torque_Nm
        self.integral = [0.0, 0.0, 0.0]
        self.prev_error = [0.0, 0.0, 0.0]
    
    def control(self, current_euler_deg: Tuple[float, float, float],
                target_euler_deg: Tuple[float, float, float],
                current_rate_rad_s: Tuple[float, float, float],
                dt_s: float) -> Tuple[float, float, float]:
        """
        Compute control torque to reach target attitude.
        
        Returns:
            Torque vector (Nx, Ny, Nz) in N*m
        """
        # Error in degrees
        error = [
            target_euler_deg[0] - current_euler_deg[0],
            target_euler_deg[1] - current_euler_deg[1],
            target_euler_deg[2] - current_euler_deg[2]
        ]
        
        # Handle angle wrapping
        for i in range(3):
            while error[i] > 180:
                error[i] -= 360
            while error[i] < -180:
                error[i] += 360
        
        # Integral term
        for i in range(3):
            self.integral[i] += error[i] * dt_s
            self.integral[i] = max(-100, min(100, self.integral[i]))  # Anti-windup
        
        # Derivative term (on rate)
        derivative = [
            (error[i] - self.prev_error[i]) / dt_s if dt_s > 0 else 0
            for i in range(3)
        ]
        self.prev_error = error[:]
        
        # PID output
        torque = [
            self.Kp * error[i] + self.Ki * self.integral[i] + self.Kd * derivative[i]
            for i in range(3)
        ]
        
        # Clamp to max torque
        for i in range(3):
            torque[i] = max(-self.max_torque, min(self.max_torque, torque[i]))
        
        return tuple(torque)
    
    def reset(self):
        """Reset controller state."""
        self.integral = [0.0, 0.0, 0.0]
        self.prev_error = [0.0, 0.0, 0.0]
