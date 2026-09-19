"""
Self Diagnostics Module
Health assessment, fault diagnosis, and system check
for autonomous system self-monitoring.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Component health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class DiagnosticLevel(Enum):
    """Diagnostic check level."""
    ROUTINE = 1
    STANDARD = 2
    EXTENDED = 3
    COMPREHENSIVE = 4


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""
    component: str
    check_name: str
    passed: bool
    status: HealthStatus
    value: float
    threshold: float
    message: str = ""


class HealthMonitor:
    """
    Monitor component health.
    """
    
    def __init__(self):
        self.health_scores: Dict[str, float] = {}
        self.status_map: Dict[str, HealthStatus] = {}
        self.thresholds: Dict[str, Tuple[float, float, float]] = {}
        # (warning, degraded, critical)
    
    def register_component(self, component: str,
                          warning: float = 0.7,
                          degraded: float = 0.5,
                          critical: float = 0.3):
        """
        Register component with thresholds.
        
        Args:
            component: Component name
            warning: Warning threshold
            degraded: Degraded threshold
            critical: Critical threshold
        """
        self.thresholds[component] = (warning, degraded, critical)
        self.health_scores[component] = 1.0
        self.status_map[component] = HealthStatus.HEALTHY
    
    def update_health(self, component: str, score: float):
        """
        Update component health score.
        
        Args:
            component: Component name
            score: Health score (0-1)
        """
        score = max(0.0, min(1.0, score))
        self.health_scores[component] = score
        
        thresholds = self.thresholds.get(component, (0.7, 0.5, 0.3))
        warn, deg, crit = thresholds
        
        if score >= warn:
            self.status_map[component] = HealthStatus.HEALTHY
        elif score >= deg:
            self.status_map[component] = HealthStatus.WARNING
        elif score >= crit:
            self.status_map[component] = HealthStatus.DEGRADED
        else:
            self.status_map[component] = HealthStatus.CRITICAL
    
    def get_status(self, component: str) -> HealthStatus:
        """Get component status."""
        return self.status_map.get(component, HealthStatus.UNKNOWN)
    
    def get_score(self, component: str) -> float:
        """Get component health score."""
        return self.health_scores.get(component, 0.0)
    
    def overall_health(self) -> float:
        """Get overall system health."""
        if not self.health_scores:
            return 0.0
        return sum(self.health_scores.values()) / len(self.health_scores)
    
    def critical_components(self) -> List[str]:
        """Get components in critical state."""
        return [c for c, s in self.status_map.items()
                if s == HealthStatus.CRITICAL]


class FaultDiagnosis:
    """
    Diagnose faults from symptoms.
    """
    
    def __init__(self):
        self.fault_rules: Dict[str, List[str]] = {}
        # fault -> list of symptoms
        self.symptoms: Dict[str, bool] = {}
    
    def add_rule(self, fault: str, symptoms: List[str]):
        """Add fault-symptom rule."""
        self.fault_rules[fault] = symptoms
    
    def report_symptom(self, symptom: str, present: bool = True):
        """Report a symptom."""
        self.symptoms[symptom] = present
    
    def diagnose(self) -> Dict[str, float]:
        """
        Diagnose faults.
        
        Returns:
            Fault probabilities
        """
        probabilities = {}
        
        for fault, required in self.fault_rules.items():
            if not required:
                probabilities[fault] = 0.0
                continue
            
            matched = sum(1 for s in required if self.symptoms.get(s, False))
            probabilities[fault] = matched / len(required)
        
        return probabilities
    
    def most_likely_fault(self) -> Optional[Tuple[str, float]]:
        """Get most likely fault."""
        probs = self.diagnose()
        if not probs:
            return None
        
        best = max(probs.items(), key=lambda x: x[1])
        return best if best[1] > 0 else None


class SystemChecker:
    """
    Run systematic diagnostic checks.
    """
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], Tuple[bool, float, str]]] = {}
        self.results: List[DiagnosticResult] = []
    
    def register_check(self, component: str, check_name: str,
                      check_func: Callable[[], Tuple[bool, float, str]],
                      threshold: float = 0.5):
        """
        Register a diagnostic check.
        
        Args:
            component: Component name
            check_name: Check name
            check_func: Function returning (passed, value, message)
            threshold: Pass threshold
        """
        self.checks[f"{component}:{check_name}"] = (component, check_name, check_func, threshold)
    
    def run_check(self, check_id: str) -> Optional[DiagnosticResult]:
        """Run a single check."""
        entry = self.checks.get(check_id)
        if not entry:
            return None
        
        component, check_name, check_func, threshold = entry
        passed, value, message = check_func()
        
        if passed:
            status = HealthStatus.HEALTHY
        elif value > threshold * 0.8:
            status = HealthStatus.WARNING
        elif value > threshold * 0.5:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL
        
        result = DiagnosticResult(
            component=component,
            check_name=check_name,
            passed=passed,
            status=status,
            value=value,
            threshold=threshold,
            message=message
        )
        self.results.append(result)
        return result
    
    def run_all(self) -> List[DiagnosticResult]:
        """Run all checks."""
        self.results.clear()
        for check_id in self.checks:
            self.run_check(check_id)
        return self.results
    
    def get_failures(self) -> List[DiagnosticResult]:
        """Get failed checks."""
        return [r for r in self.results if not r.passed]
    
    def pass_rate(self) -> float:
        """Get check pass rate."""
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)


class SelfDiagnostics:
    """
    Unified self-diagnostics controller.
    """
    
    def __init__(self):
        self.health = HealthMonitor()
        self.faults = FaultDiagnosis()
        self.checker = SystemChecker()
    
    def register_component(self, component: str,
                          warning: float = 0.7,
                          degraded: float = 0.5,
                          critical: float = 0.3):
        """Register component for monitoring."""
        self.health.register_component(component, warning, degraded, critical)
    
    def update_component_health(self, component: str, score: float):
        """Update component health."""
        self.health.update_health(component, score)
    
    def add_fault_rule(self, fault: str, symptoms: List[str]):
        """Add fault diagnosis rule."""
        self.faults.add_rule(fault, symptoms)
    
    def report_symptom(self, symptom: str, present: bool = True):
        """Report symptom."""
        self.faults.report_symptom(symptom, present)
    
    def register_check(self, component: str, check_name: str,
                      check_func, threshold: float = 0.5):
        """Register diagnostic check."""
        self.checker.register_check(component, check_name, check_func, threshold)
    
    def run_diagnostics(self) -> Dict:
        """
        Run full diagnostic suite.
        
        Returns:
            Diagnostic summary
        """
        results = self.checker.run_all()
        fault_probs = self.faults.diagnose()
        most_likely = self.faults.most_likely_fault()
        
        return {
            "checks_run": len(results),
            "checks_passed": sum(1 for r in results if r.passed),
            "pass_rate": self.checker.pass_rate(),
            "overall_health": self.health.overall_health(),
            "critical_components": self.health.critical_components(),
            "fault_probabilities": fault_probs,
            "most_likely_fault": most_likely[0] if most_likely else None,
            "fault_confidence": most_likely[1] if most_likely else 0.0
        }
    
    def diagnostics_summary(self) -> Dict:
        """Get diagnostics summary."""
        return {
            "monitored_components": len(self.health.health_scores),
            "fault_rules": len(self.faults.fault_rules),
            "registered_checks": len(self.checker.checks),
            "overall_health": self.health.overall_health()
        }
