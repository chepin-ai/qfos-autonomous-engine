"""
Sensor Fusion Module
Multi-sensor Kalman fusion, IMU/GPS/Lidar integration
for autonomous spacecraft navigation.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class SensorReading:
    """A reading from a sensor."""
    sensor_id: str
    timestamp: float
    values: List[float]
    covariance: List[List[float]]


@dataclass
class FusedState:
    """Fused state estimate."""
    position: List[float]
    velocity: List[float]
    orientation: List[float]
    covariance: List[List[float]]
    timestamp: float = 0.0


class KalmanFusion:
    """
    Multi-sensor Extended Kalman Filter for state estimation.
    """
    
    def __init__(self, state_dim: int = 6):
        """
        Args:
            state_dim: State dimension (pos + vel)
        """
        self.state_dim = state_dim
        self.state: List[float] = [0.0] * state_dim
        self.covariance: List[List[float]] = self._identity(state_dim, 1.0)
        self.process_noise: List[List[float]] = self._identity(state_dim, 0.01)
    
    def _identity(self, n: int, scale: float = 1.0) -> List[List[float]]:
        """Create scaled identity matrix."""
        return [[scale if i == j else 0.0 for j in range(n)] for i in range(n)]
    
    def _mat_add(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Matrix addition."""
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
    
    def _mat_mul(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Matrix multiplication."""
        result = [[0.0] * len(B[0]) for _ in range(len(A))]
        for i in range(len(A)):
            for j in range(len(B[0])):
                for k in range(len(B)):
                    result[i][j] += A[i][k] * B[k][j]
        return result
    
    def _mat_vec_mul(self, A: List[List[float]], v: List[float]) -> List[float]:
        """Matrix-vector multiplication."""
        return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]
    
    def _transpose(self, A: List[List[float]]) -> List[List[float]]:
        """Matrix transpose."""
        return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]
    
    def _inverse_2x2(self, A: List[List[float]]) -> List[List[float]]:
        """Inverse of 2x2 matrix."""
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if abs(det) < 1e-10:
            return [[1.0, 0.0], [0.0, 1.0]]
        inv_det = 1.0 / det
        return [
            [A[1][1] * inv_det, -A[0][1] * inv_det],
            [-A[1][0] * inv_det, A[0][0] * inv_det]
        ]
    
    def _inverse(self, A: List[List[float]]) -> List[List[float]]:
        """Matrix inverse (supports 2x2 and diagonal)."""
        n = len(A)
        if n == 2:
            return self._inverse_2x2(A)
        
        # For diagonal or near-diagonal matrices
        result = [[0.0] * n for _ in range(n)]
        for i in range(n):
            if abs(A[i][i]) > 1e-10:
                result[i][i] = 1.0 / A[i][i]
        return result
    
    def predict(self, dt: float):
        """
        Prediction step.
        
        Args:
            dt: Time step
        """
        n = self.state_dim
        # State transition: position += velocity * dt
        F = self._identity(n)
        half = n // 2
        for i in range(half):
            F[i][i + half] = dt
        
        # Predict state
        self.state = self._mat_vec_mul(F, self.state)
        
        # Predict covariance
        FT = self._transpose(F)
        self.covariance = self._mat_add(
            self._mat_mul(self._mat_mul(F, self.covariance), FT),
            self.process_noise
        )
    
    def update(self, reading: SensorReading,
              measurement_matrix: List[List[float]]):
        """
        Update step with sensor reading.
        
        Args:
            reading: Sensor reading
            measurement_matrix: H matrix
        """
        z = reading.values
        R = reading.covariance
        H = measurement_matrix
        HT = self._transpose(H)
        
        # Innovation
        y = [z[i] - sum(H[i][j] * self.state[j] for j in range(self.state_dim))
             for i in range(len(z))]
        
        # Innovation covariance
        S = self._mat_add(self._mat_mul(self._mat_mul(H, self.covariance), HT), R)
        
        # Kalman gain
        S_inv = self._inverse(S)
        K = self._mat_mul(self._mat_mul(self.covariance, HT), S_inv)
        
        # Update state
        self.state = [self.state[i] + sum(K[i][j] * y[j] for j in range(len(y)))
                      for i in range(self.state_dim)]
        
        # Update covariance
        I = self._identity(self.state_dim)
        KH = self._mat_mul(K, H)
        self.covariance = [[self.covariance[i][j] - KH[i][j]
                           for j in range(self.state_dim)]
                          for i in range(self.state_dim)]
    
    def get_state(self) -> List[float]:
        """Get current state estimate."""
        return self.state[:]
    
    def get_position(self) -> List[float]:
        """Get position estimate."""
        half = self.state_dim // 2
        return self.state[:half]
    
    def get_velocity(self) -> List[float]:
        """Get velocity estimate."""
        half = self.state_dim // 2
        return self.state[half:]


class IMUProcessor:
    """
    Process IMU readings (accelerometer + gyroscope).
    """
    
    def __init__(self):
        self.accel_bias: List[float] = [0.0, 0.0, 0.0]
        self.gyro_bias: List[float] = [0.0, 0.0, 0.0]
        self.last_accel: List[float] = [0.0, 0.0, 0.0]
        self.last_gyro: List[float] = [0.0, 0.0, 0.0]
    
    def process_accel(self, raw: List[float]) -> List[float]:
        """
        Process accelerometer reading.
        
        Args:
            raw: Raw acceleration [ax, ay, az] m/s^2
        
        Returns:
            Calibrated acceleration
        """
        calibrated = [raw[i] - self.accel_bias[i] for i in range(3)]
        self.last_accel = calibrated
        return calibrated
    
    def process_gyro(self, raw: List[float]) -> List[float]:
        """
        Process gyroscope reading.
        
        Args:
            raw: Raw angular velocity [wx, wy, wz] rad/s
        
        Returns:
            Calibrated angular velocity
        """
        calibrated = [raw[i] - self.gyro_bias[i] for i in range(3)]
        self.last_gyro = calibrated
        return calibrated
    
    def integrate_velocity(self, accel: List[float], dt: float,
                          current_vel: List[float]) -> List[float]:
        """
        Integrate acceleration to velocity.
        
        Args:
            accel: Acceleration
            dt: Time step
            current_vel: Current velocity
        
        Returns:
            Updated velocity
        """
        return [current_vel[i] + accel[i] * dt for i in range(3)]
    
    def calibrate_bias(self, accel_samples: List[List[float]],
                      gyro_samples: List[List[float]]):
        """
        Calibrate biases from stationary samples.
        
        Args:
            accel_samples: Stationary accelerometer readings
            gyro_samples: Stationary gyroscope readings
        """
        if accel_samples:
            self.accel_bias = [sum(s[i] for s in accel_samples) / len(accel_samples)
                              for i in range(3)]
        if gyro_samples:
            self.gyro_bias = [sum(s[i] for s in gyro_samples) / len(gyro_samples)
                             for i in range(3)]


class SensorFusion:
    """
    Unified sensor fusion controller.
    """
    
    def __init__(self, state_dim: int = 6):
        """
        Args:
            state_dim: State dimension
        """
        self.kalman = KalmanFusion(state_dim)
        self.imu = IMUProcessor()
        self.readings: List[SensorReading] = []
    
    def add_reading(self, reading: SensorReading):
        """Add sensor reading."""
        self.readings.append(reading)
    
    def fuse_gps(self, reading: SensorReading, dt: float):
        """
        Fuse GPS reading.
        
        Args:
            reading: GPS position reading
            dt: Time step
        """
        self.kalman.predict(dt)
        
        half = self.kalman.state_dim // 2
        H = [[0.0] * self.kalman.state_dim for _ in range(half)]
        for i in range(half):
            H[i][i] = 1.0
        
        self.kalman.update(reading, H)
    
    def fuse_imu(self, accel: List[float], gyro: List[float],
                dt: float):
        """
        Fuse IMU reading.
        
        Args:
            accel: Acceleration [ax, ay, az]
            gyro: Angular velocity [wx, wy, wz]
            dt: Time step
        """
        calibrated_accel = self.imu.process_accel(accel)
        self.imu.process_gyro(gyro)
        
        self.kalman.predict(dt)
        
        # Use accelerometer as indirect velocity measurement
        half = self.kalman.state_dim // 2
        vel = self.kalman.get_velocity()
        new_vel = self.imu.integrate_velocity(calibrated_accel, dt, vel)
        
        reading = SensorReading(
            sensor_id="imu",
            timestamp=0.0,
            values=new_vel,
            covariance=[[0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        )
        
        H = [[0.0] * self.kalman.state_dim for _ in range(half)]
        for i in range(half):
            H[i][i + half] = 1.0
        
        self.kalman.update(reading, H)
    
    def get_fused_state(self) -> FusedState:
        """Get fused state estimate."""
        half = self.kalman.state_dim // 2
        pos = self.kalman.get_position()
        vel = self.kalman.get_velocity()
        
        return FusedState(
            position=pos,
            velocity=vel,
            orientation=[0.0, 0.0, 0.0],
            covariance=self.kalman.covariance,
            timestamp=0.0
        )
    
    def fusion_summary(self) -> Dict:
        """Get fusion summary."""
        return {
            "readings_processed": len(self.readings),
            "state_dim": self.kalman.state_dim,
            "position": self.kalman.get_position(),
            "velocity": self.kalman.get_velocity()
        }
