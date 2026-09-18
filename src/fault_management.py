"""
Fault Detection, Isolation, and Recovery (FDIR) Module
Autonomous fault management for spacecraft operations.
"""

import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class FaultSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FaultStatus(Enum):
    ACTIVE = "ACTIVE"
    ISOLATED = "ISOLATED"
    RECOVERED = "RECOVERED"
    IGNORED = "IGNORED"


@dataclass
class Fault:
    """A detected fault in the spacecraft."""
    fault_id: str
    subsystem: str
    description: str
    severity: FaultSeverity
    timestamp: float
    status: FaultStatus = FaultStatus.ACTIVE
    recovery_action: Optional[str] = None
    recovery_successful: Optional[bool] = None


@dataclass
class TelemetryPoint:
    """A single telemetry measurement."""
    name: str
    value: float
    timestamp: float
    min_limit: Optional[float] = None
    max_limit: Optional[float] = None
    expected_range: Optional[tuple] = None


class FaultDetector:
    """
    Detect faults by monitoring telemetry against limits and trends.
    """
    
    def __init__(self):
        self.history: Dict[str, List[TelemetryPoint]] = {}
        self.max_history = 100
    
    def add_telemetry(self, point: TelemetryPoint):
        """Add a telemetry point to the monitoring buffer."""
        if point.name not in self.history:
            self.history[point.name] = []
        self.history[point.name].append(point)
        
        # Trim history
        if len(self.history[point.name]) > self.max_history:
            self.history[point.name] = self.history[point.name][-self.max_history:]
    
    def check_limits(self, point: TelemetryPoint) -> Optional[Fault]:
        """Check if telemetry point exceeds defined limits."""
        if point.min_limit is not None and point.value < point.min_limit:
            return Fault(
                fault_id=f"LIMIT_MIN_{point.name}",
                subsystem=point.name.split('.')[0] if '.' in point.name else "UNKNOWN",
                description=f"{point.name} below minimum: {point.value:.2f} < {point.min_limit:.2f}",
                severity=FaultSeverity.HIGH,
                timestamp=point.timestamp
            )
        
        if point.max_limit is not None and point.value > point.max_limit:
            return Fault(
                fault_id=f"LIMIT_MAX_{point.name}",
                subsystem=point.name.split('.')[0] if '.' in point.name else "UNKNOWN",
                description=f"{point.name} above maximum: {point.value:.2f} > {point.max_limit:.2f}",
                severity=FaultSeverity.HIGH,
                timestamp=point.timestamp
            )
        
        return None
    
    def check_stuck_value(self, name: str, threshold: float = 0.001,
                          window: int = 10) -> Optional[Fault]:
        """Detect if a telemetry point is stuck (not changing)."""
        if name not in self.history or len(self.history[name]) < window:
            return None
        
        recent = self.history[name][-window:]
        values = [p.value for p in recent]
        
        if max(values) - min(values) < threshold:
            return Fault(
                fault_id=f"STUCK_{name}",
                subsystem=name.split('.')[0] if '.' in name else "UNKNOWN",
                description=f"{name} stuck at {values[-1]:.4f} for {window} samples",
                severity=FaultSeverity.MEDIUM,
                timestamp=recent[-1].timestamp
            )
        
        return None
    
    def check_rate_of_change(self, name: str, max_rate: float,
                             dt_seconds: float = 1.0) -> Optional[Fault]:
        """Detect excessive rate of change."""
        if name not in self.history or len(self.history[name]) < 2:
            return None
        
        recent = self.history[name][-2:]
        dv = recent[1].value - recent[0].value
        dt = recent[1].timestamp - recent[0].timestamp
        
        if dt > 0 and abs(dv / dt) > max_rate:
            return Fault(
                fault_id=f"RATE_{name}",
                subsystem=name.split('.')[0] if '.' in name else "UNKNOWN",
                description=f"{name} rate {dv/dt:.4f}/s exceeds {max_rate:.4f}/s",
                severity=FaultSeverity.MEDIUM,
                timestamp=recent[1].timestamp
            )
        
        return None


class FaultIsolationEngine:
    """
    Isolate faults to specific components using dependency analysis.
    """
    
    def __init__(self):
        # Component dependency graph
        self.dependencies: Dict[str, List[str]] = {}
        self.component_status: Dict[str, str] = {}
    
    def add_dependency(self, component: str, depends_on: List[str]):
        """Register component dependencies."""
        self.dependencies[component] = depends_on
        self.component_status[component] = "HEALTHY"
    
    def isolate_fault(self, fault: Fault) -> List[str]:
        """
        Determine which component(s) are likely responsible for the fault.
        
        Returns:
            List of potentially faulty components
        """
        subsystem = fault.subsystem
        suspects = [subsystem]
        
        # Check if parent components could cause this
        for component, deps in self.dependencies.items():
            if subsystem in deps:
                suspects.append(component)
        
        # Mark subsystem as suspect
        self.component_status[subsystem] = "SUSPECT"
        
        return suspects
    
    def get_root_cause(self, faults: List[Fault]) -> Optional[str]:
        """
        Find the most likely root cause among multiple faults.
        
        Uses simple heuristic: component with most associated faults.
        """
        fault_counts: Dict[str, int] = {}
        
        for fault in faults:
            suspects = self.isolate_fault(fault)
            for s in suspects:
                fault_counts[s] = fault_counts.get(s, 0) + 1
        
        if not fault_counts:
            return None
        
        return max(fault_counts, key=fault_counts.get)


class RecoveryEngine:
    """
    Execute recovery actions for isolated faults.
    """
    
    def __init__(self):
        self.recovery_procedures: Dict[str, Callable] = {}
        self.recovery_log: List[Dict] = []
    
    def register_procedure(self, fault_pattern: str, procedure: Callable):
        """Register a recovery procedure for a fault pattern."""
        self.recovery_procedures[fault_pattern] = procedure
    
    def attempt_recovery(self, fault: Fault) -> bool:
        """
        Attempt to recover from a fault.
        
        Returns:
            True if recovery was successful
        """
        # Find matching procedure
        procedure = None
        for pattern, proc in self.recovery_procedures.items():
            if pattern in fault.fault_id or pattern in fault.subsystem:
                procedure = proc
                break
        
        if procedure is None:
            fault.status = FaultStatus.IGNORED
            fault.recovery_action = "NO_PROCEDURE_AVAILABLE"
            fault.recovery_successful = False
            return False
        
        fault.recovery_action = procedure.__name__
        
        try:
            success = procedure(fault)
            fault.recovery_successful = success
            fault.status = FaultStatus.RECOVERED if success else FaultStatus.ISOLATED
            
            self.recovery_log.append({
                "fault_id": fault.fault_id,
                "action": fault.recovery_action,
                "success": success,
                "timestamp": time.time()
            })
            
            return success
        except Exception as e:
            fault.recovery_successful = False
            fault.status = FaultStatus.ISOLATED
            return False


class FDIRSystem:
    """
    Integrated Fault Detection, Isolation, and Recovery system.
    """
    
    def __init__(self):
        self.detector = FaultDetector()
        self.isolation = FaultIsolationEngine()
        self.recovery = RecoveryEngine()
        self.active_faults: Dict[str, Fault] = {}
        self.fault_history: List[Fault] = []
    
    def monitor(self, telemetry: List[TelemetryPoint]) -> List[Fault]:
        """
        Process telemetry and detect faults.
        
        Returns:
            List of newly detected faults
        """
        new_faults = []
        
        for point in telemetry:
            self.detector.add_telemetry(point)
            
            # Check limits
            fault = self.detector.check_limits(point)
            if fault and fault.fault_id not in self.active_faults:
                self.active_faults[fault.fault_id] = fault
                self.fault_history.append(fault)
                new_faults.append(fault)
            
            # Check stuck value
            fault = self.detector.check_stuck_value(point.name)
            if fault and fault.fault_id not in self.active_faults:
                self.active_faults[fault.fault_id] = fault
                self.fault_history.append(fault)
                new_faults.append(fault)
        
        return new_faults
    
    def handle_faults(self, faults: List[Fault]) -> Dict:
        """
        Isolate and attempt recovery for detected faults.
        
        Returns:
            Summary of handling results
        """
        results = {"isolated": [], "recovered": [], "failed": []}
        
        root_cause = self.isolation.get_root_cause(faults)
        
        for fault in faults:
            suspects = self.isolation.isolate_fault(fault)
            
            success = self.recovery.attempt_recovery(fault)
            
            if success:
                results["recovered"].append(fault.fault_id)
                if fault.fault_id in self.active_faults:
                    del self.active_faults[fault.fault_id]
            else:
                if fault.severity == FaultSeverity.CRITICAL:
                    results["failed"].append(fault.fault_id)
                else:
                    results["isolated"].append(fault.fault_id)
        
        results["root_cause"] = root_cause
        return results
    
    def get_health_summary(self) -> Dict:
        """Get overall spacecraft health summary."""
        severity_counts = {s: 0 for s in FaultSeverity}
        for fault in self.active_faults.values():
            severity_counts[fault.severity] += 1
        
        total_faults = len(self.fault_history)
        recovered = sum(1 for f in self.fault_history if f.status == FaultStatus.RECOVERED)
        
        return {
            "active_faults": len(self.active_faults),
            "total_faults_ever": total_faults,
            "recovered_faults": recovered,
            "recovery_rate": round(recovered / max(1, total_faults), 3),
            "severity_breakdown": {k.value: v for k, v in severity_counts.items()},
            "component_status": self.isolation.component_status.copy()
        }
