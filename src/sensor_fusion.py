"""
Sensor Fusion Module
Kalman filter, particle filter, complementary filter,
and multi-sensor data fusion for autonomous robotics.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SensorReading:
    """Sensor reading."""
    value: float
    timestamp: float
    sensor_id: str
    variance: float


class KalmanFilter1D:
    """
    1D Kalman filter.
    """
    
    def __init__(self, process_variance: float = 1e-5,
                 measurement_variance: float = 1e-2,
                 initial_estimate: float = 0.0):
        """
        Args:
            process_variance: Process noise
            measurement_variance: Measurement noise
            initial_estimate: Initial estimate
        """
        self.process_var = process_variance
        self.measurement_var = measurement_variance
        self.estimate = initial_estimate
        self.estimate_error = 1.0
    
    def update(self, measurement: float) -> float:
        """
        Update with measurement.
        
        Args:
            measurement: Measurement
        
        Returns:
            Updated estimate
        """
        # Prediction
        self.estimate_error += self.process_var
        
        # Update
        kalman_gain = self.estimate_error / (self.estimate_error + self.measurement_var)
        self.estimate += kalman_gain * (measurement - self.estimate)
        self.estimate_error *= (1.0 - kalman_gain)
        
        return self.estimate
    
    def get_estimate(self) -> float:
        """Get current estimate."""
        return self.estimate


class ComplementaryFilter:
    """
    Complementary filter for sensor fusion.
    """
    
    def __init__(self, alpha: float = 0.98):
        """
        Args:
            alpha: Weight for high-pass component
        """
        self.alpha = alpha
        self.angle = 0.0
    
    def update(self, gyro_rate: float,
              accel_angle: float,
              dt: float) -> float:
        """
        Update filter.
        
        Args:
            gyro_rate: Gyroscope rate (deg/s)
            accel_angle: Accelerometer angle (deg)
            dt: Time step
        
        Returns:
            Fused angle
        """
        self.angle = (self.alpha * (self.angle + gyro_rate * dt) +
                     (1.0 - self.alpha) * accel_angle)
        return self.angle


class ParticleFilter:
    """
    Particle filter for localization.
    """
    
    def __init__(self, num_particles: int = 100,
                 state_range: Tuple[float, float] = (-10.0, 10.0)):
        """
        Args:
            num_particles: Number of particles
            state_range: State range
        """
        self.num_particles = num_particles
        self.state_range = state_range
        self.particles: List[float] = []
        self.weights: List[float] = []
        self._init_particles()
    
    def _init_particles(self):
        """Initialize particles."""
        span = self.state_range[1] - self.state_range[0]
        self.particles = [self.state_range[0] + random.random() * span
                         for _ in range(self.num_particles)]
        self.weights = [1.0 / self.num_particles] * self.num_particles
    
    def predict(self, motion: float,
               motion_noise: float = 0.1):
        """
        Predict step.
        
        Args:
            motion: Motion
            motion_noise: Motion noise
        """
        for i in range(self.num_particles):
            self.particles[i] += motion + random.gauss(0.0, motion_noise)
    
    def update(self, measurement: float,
              measurement_noise: float = 0.1):
        """
        Update weights based on measurement.
        
        Args:
            measurement: Measurement
            measurement_noise: Measurement noise
        """
        for i in range(self.num_particles):
            diff = self.particles[i] - measurement
            self.weights[i] *= math.exp(-0.5 * (diff / measurement_noise) ** 2)
        
        # Normalize
        total = sum(self.weights)
        if total > 0:
            self.weights = [w / total for w in self.weights]
    
    def resample(self):
        """Resample particles."""
        new_particles = []
        index = 0
        cumulative = 0.0
        u = random.random() / self.num_particles
        
        for i in range(self.num_particles):
            cumulative += self.weights[i]
            while u < cumulative and index < self.num_particles:
                new_particles.append(self.particles[i])
                u += 1.0 / self.num_particles
                index += 1
        
        while len(new_particles) < self.num_particles:
            new_particles.append(random.choice(self.particles))
        
        self.particles = new_particles
        self.weights = [1.0 / self.num_particles] * self.num_particles
    
    def estimate(self) -> float:
        """
        Compute weighted estimate.
        
        Returns:
            Estimate
        """
        return sum(p * w for p, w in zip(self.particles, self.weights))


class MultiSensorFusion:
    """
    Multi-sensor data fusion.
    """
    
    def __init__(self):
        self.sensors: Dict[str, KalmanFilter1D] = {}
    
    def add_sensor(self, sensor_id: str,
                  process_variance: float = 1e-5,
                  measurement_variance: float = 1e-2):
        """
        Add sensor.
        
        Args:
            sensor_id: Sensor ID
            process_variance: Process variance
            measurement_variance: Measurement variance
        """
        self.sensors[sensor_id] = KalmanFilter1D(process_variance,
                                                   measurement_variance)
    
    def update(self, sensor_id: str, measurement: float) -> float:
        """
        Update sensor.
        
        Args:
            sensor_id: Sensor ID
            measurement: Measurement
        
        Returns:
            Estimate
        """
        if sensor_id not in self.sensors:
            self.add_sensor(sensor_id)
        return self.sensors[sensor_id].update(measurement)
    
    def fused_estimate(self) -> float:
        """
        Compute fused estimate from all sensors.
        
        Returns:
            Fused estimate
        """
        if not self.sensors:
            return 0.0
        
        estimates = [kf.get_estimate() for kf in self.sensors.values()]
        return sum(estimates) / len(estimates)


class SensorFusion:
    """
    Unified sensor fusion controller.
    """
    
    def __init__(self):
        self.kalman = KalmanFilter1D()
        self.complementary = ComplementaryFilter()
        self.particle = ParticleFilter()
        self.multi = MultiSensorFusion()
    
    def sf_summary(self) -> Dict:
        """Get summary."""
        return {
            "filters": ["kalman", "complementary", "particle", "multi_sensor"],
            "sensors": len(self.multi.sensors)
        }
