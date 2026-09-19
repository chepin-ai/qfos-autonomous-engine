"""
Contingency Planner Module
Failure mode detection, backup plan generation, and
abort/safe-mode decision trees for autonomous operations.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class FailureSeverity(Enum):
    """Failure severity levels."""
    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class ContingencyType(Enum):
    """Types of contingency actions."""
    CONTINUE = "continue"
    DEGRADE = "degrade"
    RECONFIGURE = "reconfigure"
    ABORT = "abort"
    SAFE_MODE = "safe_mode"
    EMERGENCY = "emergency"


@dataclass
class FailureMode:
    """A identified failure mode."""
    name: str
    system: str
    severity: FailureSeverity
    description: str
    triggers: List[str] = field(default_factory=list)
    auto_response: ContingencyType = ContingencyType.CONTINUE


@dataclass
class ContingencyPlan:
    """A contingency plan."""
    name: str
    trigger: str
    response_type: ContingencyType
    actions: List[str] = field(default_factory=list)
    estimated_success_rate: float = 0.9
    resource_requirements: Dict[str, float] = field(default_factory=dict)


class ContingencyPlanner:
    """
    Contingency planner for autonomous fault management.
    
    Detects failure modes, assesses severity, and generates
    appropriate backup plans with decision trees.
    """
    
    def __init__(self):
        self.failure_modes: Dict[str, FailureMode] = {}
        self.contingency_plans: Dict[str, ContingencyPlan] = {}
        self.active_contingencies: List[str] = []
        self.fault_history: List[Dict] = []
    
    def add_failure_mode(self, mode: FailureMode):
        """Register a failure mode."""
        self.failure_modes[mode.name] = mode
    
    def add_contingency_plan(self, plan: ContingencyPlan):
        """Register a contingency plan."""
        self.contingency_plans[plan.name] = plan
    
    def detect_failures(self, system_status: Dict[str, Dict]) -> List[FailureMode]:
        """
        Detect active failures from system status.
        
        Args:
            system_status: Dict of system_name -> status_dict
        
        Returns:
            List of active failure modes
        """
        active = []
        
        for mode in self.failure_modes.values():
            if mode.system in system_status:
                status = system_status[mode.system]
                
                # Check triggers
                triggered = False
                for trigger in mode.triggers:
                    if ":" in trigger:
                        key, condition = trigger.split(":", 1)
                        key = key.strip()
                        
                        if key in status:
                            val = status[key]
                            
                            if ">" in condition:
                                thresh = float(condition.replace(">", "").strip())
                                if val > thresh:
                                    triggered = True
                            elif "<" in condition:
                                thresh = float(condition.replace("<", "").strip())
                                if val < thresh:
                                    triggered = True
                            elif "==" in condition:
                                expected = condition.replace("==", "").strip()
                                if str(val) == expected:
                                    triggered = True
                
                if triggered:
                    active.append(mode)
        
        return active
    
    def assess_severity(self, failures: List[FailureMode]) -> FailureSeverity:
        """
        Assess overall severity from active failures.
        
        Args:
            failures: Active failure modes
        
        Returns:
            Overall severity
        """
        if not failures:
            return FailureSeverity.NONE
        
        severity_order = [
            FailureSeverity.NONE,
            FailureSeverity.MINOR,
            FailureSeverity.MAJOR,
            FailureSeverity.CRITICAL,
            FailureSeverity.CATASTROPHIC
        ]
        
        max_idx = 0
        for f in failures:
            idx = severity_order.index(f.severity)
            if idx > max_idx:
                max_idx = idx
        
        return severity_order[max_idx]
    
    def select_contingency(self, failures: List[FailureMode]) -> Optional[ContingencyPlan]:
        """
        Select appropriate contingency plan.
        
        Args:
            failures: Active failures
        
        Returns:
            Best contingency plan or None
        """
        if not failures:
            return None
        
        severity = self.assess_severity(failures)
        
        # Map severity to response type
        response_map = {
            FailureSeverity.NONE: ContingencyType.CONTINUE,
            FailureSeverity.MINOR: ContingencyType.DEGRADE,
            FailureSeverity.MAJOR: ContingencyType.RECONFIGURE,
            FailureSeverity.CRITICAL: ContingencyType.ABORT,
            FailureSeverity.CATASTROPHIC: ContingencyType.EMERGENCY
        }
        
        target_response = response_map.get(severity, ContingencyType.CONTINUE)
        
        # Find matching plan
        best_plan = None
        best_score = -1.0
        
        for plan in self.contingency_plans.values():
            if plan.response_type == target_response:
                score = plan.estimated_success_rate
                if score > best_score:
                    best_score = score
                    best_plan = plan
        
        return best_plan
    
    def execute_contingency(self, plan: ContingencyPlan) -> Dict:
        """
        Execute a contingency plan.
        
        Args:
            plan: Plan to execute
        
        Returns:
            Execution result
        """
        self.active_contingencies.append(plan.name)
        
        result = {
            "plan": plan.name,
            "response_type": plan.response_type.value,
            "actions": plan.actions,
            "success_rate": plan.estimated_success_rate,
            "executed": True
        }
        
        self.fault_history.append(result)
        return result
    
    def abort_decision_tree(self, failures: List[FailureMode],
                            mission_critical: bool = True,
                            crew_safety: bool = False) -> Dict:
        """
        Abort decision tree.
        
        Args:
            failures: Active failures
            mission_critical: Is mission critical
            crew_safety: Is crew safety involved
        
        Returns:
            Decision result
        """
        severity = self.assess_severity(failures)
        
        # Decision tree
        if crew_safety and severity.value in ["critical", "catastrophic"]:
            decision = "ABORT_IMMEDIATE"
            reason = "Crew safety at risk"
        elif severity.value == "catastrophic":
            decision = "ABORT_IMMEDIATE"
            reason = "Catastrophic failure"
        elif severity.value == "critical" and mission_critical:
            decision = "ABORT_PLANNED"
            reason = "Critical failure in mission-critical system"
        elif severity.value == "major":
            decision = "DEGRADE_MODE"
            reason = "Major failure - degraded operations"
        elif severity.value == "minor":
            decision = "CONTINUE_MONITOR"
            reason = "Minor failure - continue with monitoring"
        else:
            decision = "CONTINUE"
            reason = "No significant failures"
        
        return {
            "decision": decision,
            "reason": reason,
            "severity": severity.value,
            "active_failures": [f.name for f in failures],
            "mission_critical": mission_critical,
            "crew_safety": crew_safety
        }
    
    def safe_mode_entry(self, trigger: str) -> List[str]:
        """
        Generate safe mode entry sequence.
        
        Args:
            trigger: What triggered safe mode
        
        Returns:
            List of safe mode actions
        """
        return [
            "disable_non_essential_subsystems",
            "orient_solar_arrays_to_sun",
            "establish_ground_communication",
            "dump_fault_telemetry",
            "await_ground_command",
            f"log_trigger:{trigger}"
        ]
    
    def reconfigure_for_redundancy(self, failed_system: str,
                                   redundant_system: Optional[str] = None) -> Dict:
        """
        Reconfigure to use redundant system.
        
        Args:
            failed_system: Failed system name
            redundant_system: Backup system name
        
        Returns:
            Reconfiguration plan
        """
        if redundant_system is None:
            # Auto-detect: "A_primary" -> "A_backup"
            redundant_system = f"{failed_system}_backup"
        
        return {
            "failed_system": failed_system,
            "switch_to": redundant_system,
            "actions": [
                f"isolate_{failed_system}",
                f"activate_{redundant_system}",
                f"verify_{redundant_system}_health",
                "update_telemetry_routing"
            ],
            "estimated_downtime_s": 30.0
        }
    
    def contingency_summary(self) -> Dict:
        """Get contingency status summary."""
        return {
            "failure_modes_tracked": len(self.failure_modes),
            "contingency_plans": len(self.contingency_plans),
            "active_contingencies": self.active_contingencies,
            "total_faults_handled": len(self.fault_history),
            "last_fault": self.fault_history[-1] if self.fault_history else None
        }
    
    @staticmethod
    def create_standard_failure_modes() -> List[FailureMode]:
        """Create standard spacecraft failure modes."""
        return [
            FailureMode("thruster_degradation", "propulsion",
                       FailureSeverity.MINOR, "Thruster efficiency below nominal",
                       ["efficiency:<0.8"], ContingencyType.DEGRADE),
            FailureMode("single_gyro_failure", "attitude",
                       FailureSeverity.MAJOR, "Single gyroscope failure",
                       ["gyros_operational:<3"], ContingencyType.RECONFIGURE),
            FailureMode("power_bus_anomaly", "power",
                       FailureSeverity.CRITICAL, "Main power bus voltage anomaly",
                       ["voltage:<26.0", "voltage:>34.0"], ContingencyType.ABORT),
            FailureMode("communication_loss", "comm",
                       FailureSeverity.MAJOR, "Communication link lost",
                       ["link_status:==down"], ContingencyType.SAFE_MODE),
            FailureMode("thermal_runaway", "thermal",
                       FailureSeverity.CATASTROPHIC, "Thermal runaway detected",
                       ["temperature:>80.0"], ContingencyType.EMERGENCY),
            FailureMode("propellant_leak", "propulsion",
                       FailureSeverity.CRITICAL, "Propellant tank pressure drop",
                       ["tank_pressure:<2.0"], ContingencyType.ABORT)
        ]
