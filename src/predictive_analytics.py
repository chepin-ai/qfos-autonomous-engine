"""
Predictive Analytics Module
Time series forecasting, anomaly prediction, and
trend analysis for spacecraft telemetry.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque


@dataclass
class TimeSeriesPoint:
    """A single point in a time series."""
    timestamp: float
    value: float


class MovingAveragePredictor:
    """
    Simple moving average predictor.
    
    Uses weighted moving average for short-term
    forecasting.
    """
    
    def __init__(self, window_size: int = 10):
        """
        Args:
            window_size: Number of points in window
        """
        self.window_size = window_size
        self.history: deque = deque(maxlen=window_size)
    
    def update(self, value: float):
        """Add new observation."""
        self.history.append(value)
    
    def predict(self, steps_ahead: int = 1) -> Optional[float]:
        """
        Predict next value(s).
        
        Args:
            steps_ahead: Number of steps to forecast
        
        Returns:
            Predicted value or None
        """
        if len(self.history) < 2:
            return None
        
        # Weighted average with recent bias
        weights = [i + 1 for i in range(len(self.history))]
        total_weight = sum(weights)
        weighted_sum = sum(v * w for v, w in zip(self.history, weights))
        
        return weighted_sum / total_weight
    
    def trend(self) -> float:
        """
        Compute trend direction.
        
        Returns:
            Trend value (positive = increasing)
        """
        if len(self.history) < 2:
            return 0.0
        
        values = list(self.history)
        # Simple linear slope
        n = len(values)
        x_mean = (n - 1) / 2.0
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (v - y_mean)
                       for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator


class AnomalyDetector:
    """
    Statistical anomaly detector for telemetry.
    
    Uses Z-score and EWMA for anomaly detection.
    """
    
    def __init__(self, z_threshold: float = 3.0,
                 ewma_alpha: float = 0.3):
        """
        Args:
            z_threshold: Z-score threshold for anomaly
            ewma_alpha: EWMA smoothing factor
        """
        self.z_threshold = z_threshold
        self.ewma_alpha = ewma_alpha
        self.mean = 0.0
        self.variance = 0.0
        self.ewma = 0.0
        self.count = 0
        self.anomaly_history: List[Tuple[float, float, str]] = []
    
    def update(self, value: float, timestamp: float = 0.0):
        """
        Update detector with new value.
        
        Args:
            value: New observation
            timestamp: Observation time
        
        Returns:
            Anomaly info dict
        """
        self.count += 1
        
        # Update running mean and variance
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.variance += delta * delta2
        
        # EWMA
        if self.count == 1:
            self.ewma = value
        else:
            self.ewma = self.ewma_alpha * value + (1 - self.ewma_alpha) * self.ewma
        
        # Z-score check
        std = math.sqrt(self.variance / max(1, self.count - 1)) if self.count > 1 else 1.0
        z_score = abs(value - self.mean) / max(std, 1e-10)
        
        is_anomaly = z_score > self.z_threshold and self.count > 5
        
        result = {
            "value": value,
            "mean": self.mean,
            "std": std,
            "z_score": z_score,
            "ewma": self.ewma,
            "is_anomaly": is_anomaly,
            "severity": "high" if z_score > self.z_threshold * 2 else (
                "medium" if is_anomaly else "normal"
            )
        }
        
        if is_anomaly:
            self.anomaly_history.append((timestamp, value, result["severity"]))
        
        return result
    
    def get_anomalies(self, limit: int = 10) -> List[Tuple[float, float, str]]:
        """
        Get recent anomalies.
        
        Args:
            limit: Maximum number to return
        
        Returns:
            List of (timestamp, value, severity)
        """
        return self.anomaly_history[-limit:]


class DegradationPredictor:
    """
    Predict component degradation over time.
    
    Uses simple linear extrapolation of health metrics.
    """
    
    def __init__(self, warning_threshold: float = 0.3,
                 critical_threshold: float = 0.1):
        """
        Args:
            warning_threshold: Health level for warning
            critical_threshold: Health level for critical
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.health_history: List[Tuple[float, float]] = []  # (time, health)
    
    def add_measurement(self, time: float, health: float):
        """Add health measurement."""
        self.health_history.append((time, health))
    
    def predict_time_to_threshold(self, threshold: Optional[float] = None) -> Optional[float]:
        """
        Predict time until health reaches threshold.
        
        Args:
            threshold: Health threshold (default: critical)
        
        Returns:
            Time until threshold or None
        """
        if len(self.health_history) < 2:
            return None
        
        threshold = threshold or self.critical_threshold
        
        # Linear fit to recent points (last 10)
        recent = self.health_history[-10:]
        n = len(recent)
        
        t_mean = sum(t for t, _ in recent) / n
        h_mean = sum(h for _, h in recent) / n
        
        num = sum((t - t_mean) * (h - h_mean) for t, h in recent)
        den = sum((t - t_mean) ** 2 for t, _ in recent)
        
        if den == 0 or num >= 0:  # Not degrading or flat
            return None
        
        slope = num / den
        last_time, last_health = recent[-1]
        
        # Extrapolate: health = last + slope * (t - last_time)
        # threshold = last + slope * dt
        # dt = (threshold - last) / slope
        time_to = (threshold - last_health) / slope
        
        return time_to if time_to > 0 else None
    
    def get_health_status(self) -> Dict:
        """Get current health prediction status."""
        if not self.health_history:
            return {"status": "unknown"}
        
        current_health = self.health_history[-1][1]
        
        if current_health <= self.critical_threshold:
            status = "critical"
        elif current_health <= self.warning_threshold:
            status = "warning"
        else:
            status = "nominal"
        
        time_to_warning = self.predict_time_to_threshold(self.warning_threshold)
        time_to_critical = self.predict_time_to_threshold(self.critical_threshold)
        
        return {
            "current_health": current_health,
            "status": status,
            "time_to_warning": time_to_warning,
            "time_to_critical": time_to_critical,
            "measurements": len(self.health_history)
        }


class TelemetryPredictor:
    """
    Unified telemetry prediction engine.
    
    Combines moving average, anomaly detection, and
    degradation prediction.
    """
    
    def __init__(self):
        self.predictors: Dict[str, MovingAveragePredictor] = {}
        self.anomaly_detectors: Dict[str, AnomalyDetector] = {}
        self.degradation_predictors: Dict[str, DegradationPredictor] = {}
    
    def register_channel(self, channel: str, predictor_type: str = "ma"):
        """Register a telemetry channel."""
        if channel not in self.predictors:
            self.predictors[channel] = MovingAveragePredictor()
            self.anomaly_detectors[channel] = AnomalyDetector()
    
    def update(self, channel: str, value: float, timestamp: float = 0.0):
        """
        Update channel with new value.
        
        Args:
            channel: Channel name
            value: New value
            timestamp: Observation time
        
        Returns:
            Analysis dict
        """
        if channel not in self.predictors:
            self.register_channel(channel)
        
        self.predictors[channel].update(value)
        anomaly = self.anomaly_detectors[channel].update(value, timestamp)
        
        prediction = self.predictors[channel].predict()
        trend = self.predictors[channel].trend()
        
        return {
            "channel": channel,
            "value": value,
            "prediction": prediction,
            "trend": trend,
            "anomaly": anomaly
        }
    
    def get_summary(self) -> Dict:
        """Get overall prediction summary."""
        return {
            "channels": len(self.predictors),
            "total_anomalies": sum(len(d.anomaly_history)
                                  for d in self.anomaly_detectors.values())
        }
