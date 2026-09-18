"""
Sensor Fusion Module
Multi-sensor data fusion for autonomous navigation state estimation.
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SensorReading:
    """A single sensor measurement."""
    sensor_type: str  # 'radar', 'lidar', 'optical', 'thermal', 'radio'
    position_m: Tuple[float, float, float]
    velocity_ms: Tuple[float, float, float]
    timestamp: float
    uncertainty_m: float  # Position uncertainty in meters
    confidence: float  # 0.0 to 1.0


@dataclass 
class FusedState:
    """Fused navigation state from multiple sensors."""
    position_m: Tuple[float, float, float]
    velocity_ms: Tuple[float, float, float]
    position_uncertainty_m: float
    velocity_uncertainty_ms: float
    sensor_count: int
    timestamp: float


class SensorFusionEngine:
    """
    Weighted least-squares sensor fusion engine.
    Combines multiple sensor readings into optimal state estimate.
    """
    
    # Sensor type weights (higher = more reliable)
    SENSOR_WEIGHTS = {
        'radar': 0.9,
        'lidar': 0.95,
        'optical': 0.85,
        'thermal': 0.7,
        'radio': 0.8,
        'star_tracker': 0.98,
        'imu': 0.75
    }
    
    def __init__(self):
        self.readings: List[SensorReading] = []
    
    def add_reading(self, reading: SensorReading):
        """Add a sensor reading to the fusion buffer."""
        self.readings.append(reading)
    
    def clear_readings(self):
        """Clear all readings."""
        self.readings = []
    
    def fuse(self, timestamp: Optional[float] = None) -> Optional[FusedState]:
        """
        Fuse all available sensor readings into a single state estimate.
        Uses weighted average based on sensor reliability and confidence.
        """
        if not self.readings:
            return None
        
        # Filter by timestamp if provided
        readings = self.readings
        if timestamp is not None:
            readings = [r for r in readings if abs(r.timestamp - timestamp) < 1.0]
        
        if not readings:
            return None
        
        # Calculate weights
        weights = []
        for r in readings:
            type_weight = self.SENSOR_WEIGHTS.get(r.sensor_type, 0.5)
            # Lower uncertainty and higher confidence = higher weight
            uncertainty_weight = 1.0 / (1.0 + r.uncertainty_m / 1000.0)
            w = type_weight * r.confidence * uncertainty_weight
            weights.append(w)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return None
        
        # Weighted average for position
        pos_x = sum(r.position_m[0] * w for r, w in zip(readings, weights)) / total_weight
        pos_y = sum(r.position_m[1] * w for r, w in zip(readings, weights)) / total_weight
        pos_z = sum(r.position_m[2] * w for r, w in zip(readings, weights)) / total_weight
        
        # Weighted average for velocity
        vel_x = sum(r.velocity_ms[0] * w for r, w in zip(readings, weights)) / total_weight
        vel_y = sum(r.velocity_ms[1] * w for r, w in zip(readings, weights)) / total_weight
        vel_z = sum(r.velocity_ms[2] * w for r, w in zip(readings, weights)) / total_weight
        
        # Uncertainty calculation (weighted standard deviation)
        pos_unc = math.sqrt(
            sum(w * (sum((r.position_m[i] - [pos_x, pos_y, pos_z][i])**2 for i in range(3)))
                for r, w in zip(readings, weights))
            / total_weight
        )
        
        vel_unc = math.sqrt(
            sum(w * (sum((r.velocity_ms[i] - [vel_x, vel_y, vel_z][i])**2 for i in range(3)))
                for r, w in zip(readings, weights))
            / total_weight
        )
        
        return FusedState(
            position_m=(pos_x, pos_y, pos_z),
            velocity_ms=(vel_x, vel_y, vel_z),
            position_uncertainty_m=pos_unc,
            velocity_uncertainty_ms=vel_unc,
            sensor_count=len(readings),
            timestamp=timestamp or readings[0].timestamp
        )
    
    def detect_anomaly(self, reading: SensorReading, 
                       fused_state: FusedState,
                       threshold_sigma: float = 3.0) -> bool:
        """
        Detect if a sensor reading is anomalous compared to fused state.
        Returns True if reading deviates more than threshold_sigma from fused state.
        """
        dx = reading.position_m[0] - fused_state.position_m[0]
        dy = reading.position_m[1] - fused_state.position_m[1]
        dz = reading.position_m[2] - fused_state.position_m[2]
        
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Compare to fused uncertainty
        if fused_state.position_uncertainty_m > 0:
            sigma = distance / fused_state.position_uncertainty_m
            return sigma > threshold_sigma
        
        return distance > reading.uncertainty_m * threshold_sigma
    
    def get_sensor_health(self) -> Dict[str, Dict]:
        """Get health status of each sensor type."""
        health = {}
        for sensor_type in self.SENSOR_WEIGHTS.keys():
            type_readings = [r for r in self.readings if r.sensor_type == sensor_type]
            if type_readings:
                avg_conf = sum(r.confidence for r in type_readings) / len(type_readings)
                avg_unc = sum(r.uncertainty_m for r in type_readings) / len(type_readings)
                health[sensor_type] = {
                    "readings": len(type_readings),
                    "avg_confidence": round(avg_conf, 3),
                    "avg_uncertainty_m": round(avg_unc, 1),
                    "status": "HEALTHY" if avg_conf > 0.7 else "DEGRADED"
                }
        return health
