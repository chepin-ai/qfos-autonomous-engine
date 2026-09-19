"""
System Health Monitor Module
Real-time health dashboard, anomaly detection, and
trend analysis for spacecraft subsystems.
"""

import math
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels."""
    NOMINAL = "nominal"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MetricSample:
    """A single metric sample."""
    timestamp: float
    value: float
    unit: str = ""


@dataclass
class HealthMetric:
    """A tracked health metric."""
    name: str
    unit: str
    nominal_min: float
    nominal_max: float
    warning_min: float
    warning_max: float
    critical_min: float
    critical_max: float
    samples: List[MetricSample] = field(default_factory=list)
    max_samples: int = 1000


class AnomalyDetector:
    """
    Statistical anomaly detector.
    
    Uses moving average and standard deviation
    to detect deviations from normal behavior.
    """
    
    def __init__(self, window_size: int = 10,
                 threshold_sigma: float = 3.0):
        """
        Args:
            window_size: Moving window size
            threshold_sigma: Threshold in standard deviations
        """
        self.window_size = window_size
        self.threshold_sigma = threshold_sigma
        self.history: List[float] = []
    
    def add_sample(self, value: float):
        """Add a sample."""
        self.history.append(value)
        if len(self.history) > self.window_size:
            self.history.pop(0)
    
    def is_anomalous(self, value: float) -> Tuple[bool, float]:
        """
        Check if value is anomalous.
        
        Args:
            value: Value to check
        
        Returns:
            (is_anomalous, z_score)
        """
        if len(self.history) < 3:
            return False, 0.0
        
        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean)**2 for x in self.history) / len(self.history)
        std = math.sqrt(variance) if variance > 0 else 1.0
        
        z_score = abs(value - mean) / std
        return z_score > self.threshold_sigma, z_score
    
    def trend(self) -> str:
        """
        Detect trend direction.
        
        Returns:
            "increasing", "decreasing", "stable"
        """
        if len(self.history) < 5:
            return "stable"
        
        half = len(self.history) // 2
        first_half = sum(self.history[:half]) / half
        second_half = sum(self.history[half:]) / (len(self.history) - half)
        
        diff = second_half - first_half
        threshold = abs(first_half) * 0.05  # 5% change
        
        if diff > threshold:
            return "increasing"
        elif diff < -threshold:
            return "decreasing"
        return "stable"


class SystemHealthMonitor:
    """
    Real-time system health monitor.
    
    Tracks metrics, detects anomalies, generates alerts,
    and provides health dashboard data.
    """
    
    def __init__(self):
        self.metrics: Dict[str, HealthMetric] = {}
        self.detectors: Dict[str, AnomalyDetector] = {}
        self.alerts: List[Dict] = []
        self.alert_history: List[Dict] = []
        self.start_time = time.time()
    
    def register_metric(self, metric: HealthMetric):
        """Register a metric to monitor."""
        self.metrics[metric.name] = metric
        self.detectors[metric.name] = AnomalyDetector()
    
    def record_sample(self, metric_name: str, value: float,
                      timestamp: Optional[float] = None):
        """
        Record a metric sample.
        
        Args:
            metric_name: Metric name
            value: Sample value
            timestamp: Sample timestamp
        """
        if metric_name not in self.metrics:
            return
        
        ts = timestamp or time.time()
        metric = self.metrics[metric_name]
        
        sample = MetricSample(timestamp=ts, value=value, unit=metric.unit)
        metric.samples.append(sample)
        
        if len(metric.samples) > metric.max_samples:
            metric.samples.pop(0)
        
        # Anomaly detection
        detector = self.detectors[metric_name]
        detector.add_sample(value)
        is_anomalous, z_score = detector.is_anomalous(value)
        
        if is_anomalous:
            self._add_alert(AlertLevel.WARNING, metric_name,
                          f"Anomalous value {value:.2f}{metric.unit} (z={z_score:.2f})")
        
        # Threshold checking
        self._check_thresholds(metric_name, value)
    
    def _check_thresholds(self, metric_name: str, value: float):
        """Check value against thresholds."""
        metric = self.metrics[metric_name]
        
        if value < metric.critical_min or value > metric.critical_max:
            level = AlertLevel.CRITICAL
        elif value < metric.warning_min or value > metric.warning_max:
            level = AlertLevel.WARNING
        elif value < metric.nominal_min or value > metric.nominal_max:
            level = AlertLevel.WATCH
        else:
            level = AlertLevel.NOMINAL
        
        if level in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
            self._add_alert(level, metric_name,
                          f"Value {value:.2f}{metric.unit} outside {level.value} range")
    
    def _add_alert(self, level: AlertLevel, metric: str, message: str):
        """Add an alert."""
        alert = {
            "timestamp": time.time(),
            "level": level.value,
            "metric": metric,
            "message": message
        }
        self.alerts.append(alert)
        self.alert_history.append(alert)
    
    def get_metric_stats(self, metric_name: str) -> Optional[Dict]:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Metric name
        
        Returns:
            Statistics dict or None
        """
        if metric_name not in self.metrics:
            return None
        
        samples = self.metrics[metric_name].samples
        if not samples:
            return None
        
        values = [s.value for s in samples]
        
        return {
            "name": metric_name,
            "samples": len(values),
            "current": round(values[-1], 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
            "mean": round(sum(values) / len(values), 3),
            "trend": self.detectors[metric_name].trend()
        }
    
    def get_active_alerts(self, min_level: AlertLevel = AlertLevel.WATCH) -> List[Dict]:
        """
        Get active alerts above threshold.
        
        Args:
            min_level: Minimum alert level
        
        Returns:
            List of alerts
        """
        level_order = [AlertLevel.NOMINAL, AlertLevel.WATCH,
                      AlertLevel.WARNING, AlertLevel.CRITICAL, AlertLevel.EMERGENCY]
        min_idx = level_order.index(min_level)
        
        return [a for a in self.alerts
                if level_order.index(AlertLevel(a["level"])) >= min_idx]
    
    def clear_alert(self, metric: str):
        """Clear alerts for a metric."""
        self.alerts = [a for a in self.alerts if a["metric"] != metric]
    
    def health_dashboard(self) -> Dict:
        """
        Generate health dashboard.
        
        Returns:
            Dashboard data
        """
        stats = {}
        for name in self.metrics:
            s = self.get_metric_stats(name)
            if s:
                stats[name] = s
        
        # Overall health score
        if stats:
            health_scores = []
            for name, metric in self.metrics.items():
                if metric.samples:
                    val = metric.samples[-1].value
                    # Score 0-100 based on position within nominal range
                    range_size = metric.nominal_max - metric.nominal_min
                    if range_size > 0:
                        mid = (metric.nominal_max + metric.nominal_min) / 2.0
                        dist = abs(val - mid)
                        score = max(0.0, 100.0 - (dist / range_size) * 100.0)
                        health_scores.append(score)
            
            overall = sum(health_scores) / len(health_scores) if health_scores else 100.0
        else:
            overall = 100.0
        
        return {
            "timestamp": time.time(),
            "uptime_seconds": round(time.time() - self.start_time, 1),
            "overall_health": round(overall, 1),
            "metrics_tracked": len(self.metrics),
            "active_alerts": len(self.alerts),
            "alert_counts": {
                "watch": sum(1 for a in self.alerts if a["level"] == "watch"),
                "warning": sum(1 for a in self.alerts if a["level"] == "warning"),
                "critical": sum(1 for a in self.alerts if a["level"] == "critical")
            },
            "metric_stats": stats
        }
    
    def detect_aging(self, metric_name: str,
                     degradation_threshold_percent: float = 10.0) -> Optional[Dict]:
        """
        Detect performance degradation over time.
        
        Args:
            metric_name: Metric to analyze
            degradation_threshold_percent: Threshold for degradation
        
        Returns:
            Degradation report or None
        """
        if metric_name not in self.metrics:
            return None
        
        samples = self.metrics[metric_name].samples
        if len(samples) < 20:
            return None
        
        # Compare first 20% vs last 20%
        n = len(samples)
        early = [s.value for s in samples[:n//5]]
        recent = [s.value for s in samples[-n//5:]]
        
        early_avg = sum(early) / len(early)
        recent_avg = sum(recent) / len(recent)
        
        if early_avg == 0:
            change_pct = 0.0
        else:
            change_pct = ((recent_avg - early_avg) / abs(early_avg)) * 100.0
        
        is_degrading = abs(change_pct) > degradation_threshold_percent
        
        return {
            "metric": metric_name,
            "degrading": is_degrading,
            "change_percent": round(change_pct, 2),
            "early_average": round(early_avg, 3),
            "recent_average": round(recent_avg, 3),
            "trend": self.detectors[metric_name].trend()
        }
