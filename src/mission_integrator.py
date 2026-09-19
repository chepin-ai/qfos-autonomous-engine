"""
Mission Integrator Module
End-to-end mission orchestration integrating all subsystems
into a unified autonomous control loop.
"""

import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class MissionPhase(Enum):
    """Mission execution phases."""
    PRE_LAUNCH = "pre_launch"
    LAUNCH = "launch"
    ORBIT_INSERTION = "orbit_insertion"
    CRUISE = "cruise"
    APPROACH = "approach"
    ARRIVAL = "arrival"
    SURFACE_OPS = "surface_ops"
    RETURN = "return"
    COMPLETE = "complete"


@dataclass
class SubsystemHandle:
    """Handle to a registered subsystem."""
    name: str
    version: str
    health_percent: float = 100.0
    status: str = "nominal"
    last_update: float = field(default_factory=time.time)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    commands_accepted: List[str] = field(default_factory=list)


class MissionIntegrator:
    """
    Mission control integrator.
    
    Orchestrates all subsystems into a unified control loop,
    manages cross-subsystem dependencies, and provides
    end-to-end mission state management.
    """
    
    def __init__(self, mission_name: str = "QF-OS Mission"):
        self.mission_name = mission_name
        self.phase = MissionPhase.PRE_LAUNCH
        self.subsystems: Dict[str, SubsystemHandle] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.command_queue: List[Dict] = []
        self.event_log: List[Dict] = []
        self.mission_start_time = time.time()
        self.mission_elapsed_s = 0.0
        self.goals: List[str] = []
        self.completed_goals: List[str] = []
    
    def register_subsystem(self, handle: SubsystemHandle,
                           depends_on: Optional[List[str]] = None):
        """
        Register a subsystem.
        
        Args:
            handle: Subsystem handle
            depends_on: List of subsystem names this depends on
        """
        self.subsystems[handle.name] = handle
        self.dependencies[handle.name] = depends_on or []
        self._log_event("SUBSYSTEM_REGISTERED", f"{handle.name} v{handle.version}")
    
    def update_subsystem(self, name: str, **kwargs):
        """Update subsystem telemetry."""
        if name not in self.subsystems:
            return
        
        handle = self.subsystems[name]
        for key, value in kwargs.items():
            if hasattr(handle, key):
                setattr(handle, key, value)
        
        handle.last_update = time.time()
    
    def check_dependencies(self, subsystem_name: str) -> Tuple[bool, List[str]]:
        """
        Check if all dependencies are healthy.
        
        Args:
            subsystem_name: Subsystem to check
        
        Returns:
            (healthy, missing/unhealthy dependencies)
        """
        if subsystem_name not in self.dependencies:
            return True, []
        
        missing = []
        for dep in self.dependencies[subsystem_name]:
            if dep not in self.subsystems:
                missing.append(f"{dep}:not_found")
            elif self.subsystems[dep].health_percent < 50.0:
                missing.append(f"{dep}:unhealthy")
        
        return len(missing) == 0, missing
    
    def advance_phase(self, target_phase: Optional[MissionPhase] = None) -> bool:
        """
        Advance mission phase.
        
        Args:
            target_phase: Target phase (default: next in sequence)
        
        Returns:
            Success
        """
        phase_order = list(MissionPhase)
        current_idx = phase_order.index(self.phase)
        
        if target_phase is None:
            target_idx = current_idx + 1
        else:
            target_idx = phase_order.index(target_phase)
        
        if target_idx <= current_idx:
            return False
        
        # Check all subsystems are healthy enough for phase transition
        for name, handle in self.subsystems.items():
            if handle.health_percent < 30.0:
                self._log_event("PHASE_BLOCKED",
                              f"Cannot advance: {name} at {handle.health_percent}%")
                return False
        
        old_phase = self.phase
        self.phase = phase_order[target_idx]
        self._log_event("PHASE_ADVANCE", f"{old_phase.value} -> {self.phase.value}")
        return True
    
    def execute_command(self, subsystem: str, command: str,
                       params: Optional[Dict] = None) -> Dict:
        """
        Execute command on subsystem.
        
        Args:
            subsystem: Target subsystem
            command: Command name
            params: Command parameters
        
        Returns:
            Execution result
        """
        if subsystem not in self.subsystems:
            return {"success": False, "error": "Subsystem not found"}
        
        handle = self.subsystems[subsystem]
        
        # Check dependencies
        deps_ok, missing = self.check_dependencies(subsystem)
        if not deps_ok:
            return {"success": False, "error": f"Dependencies unhealthy: {missing}"}
        
        # Check command accepted
        if handle.commands_accepted and command not in handle.commands_accepted:
            return {"success": False, "error": "Command not accepted"}
        
        result = {
            "subsystem": subsystem,
            "command": command,
            "params": params,
            "success": True,
            "phase": self.phase.value
        }
        
        self.command_queue.append(result)
        self._log_event("COMMAND_EXECUTED", f"{subsystem}.{command}")
        return result
    
    def add_goal(self, goal: str):
        """Add a mission goal."""
        if goal not in self.goals:
            self.goals.append(goal)
    
    def complete_goal(self, goal: str):
        """Mark goal as complete."""
        if goal in self.goals and goal not in self.completed_goals:
            self.completed_goals.append(goal)
            self._log_event("GOAL_COMPLETE", goal)
    
    def get_mission_progress(self) -> Dict:
        """Get mission progress."""
        self.mission_elapsed_s = time.time() - self.mission_start_time
        
        total_goals = len(self.goals)
        completed = len(self.completed_goals)
        
        # Compute overall health
        if self.subsystems:
            avg_health = sum(s.health_percent for s in self.subsystems.values()) / len(self.subsystems)
        else:
            avg_health = 0.0
        
        return {
            "mission_name": self.mission_name,
            "phase": self.phase.value,
            "elapsed_seconds": round(self.mission_elapsed_s, 1),
            "subsystems_registered": len(self.subsystems),
            "goals_total": total_goals,
            "goals_completed": completed,
            "progress_percent": round(100.0 * completed / max(1, total_goals), 1),
            "overall_health": round(avg_health, 1),
            "commands_issued": len(self.command_queue),
            "events_logged": len(self.event_log)
        }
    
    def cross_subsystem_check(self) -> List[Dict]:
        """
        Check for cross-subsystem issues.
        
        Returns:
            List of issues
        """
        issues = []
        
        # Check power budget
        total_power = sum(s.telemetry.get("power_w", 0.0)
                         for s in self.subsystems.values())
        power_limit = 5000.0  # W
        if total_power > power_limit:
            issues.append({
                "type": "POWER_BUDGET",
                "severity": "WARNING",
                "message": f"Total power {total_power:.0f}W exceeds limit {power_limit:.0f}W"
            })
        
        # Check data rate
        total_data_rate = sum(s.telemetry.get("data_rate_mbps", 0.0)
                             for s in self.subsystems.values())
        data_limit = 100.0  # Mbps
        if total_data_rate > data_limit:
            issues.append({
                "type": "DATA_BUDGET",
                "severity": "WARNING",
                "message": f"Total data rate {total_data_rate:.1f}Mbps exceeds limit {data_limit:.1f}Mbps"
            })
        
        # Check thermal
        max_temp = max((s.telemetry.get("temperature_c", 20.0)
                       for s in self.subsystems.values()), default=20.0)
        if max_temp > 60.0:
            issues.append({
                "type": "THERMAL",
                "severity": "CRITICAL" if max_temp > 80.0 else "WARNING",
                "message": f"Max temperature {max_temp:.1f}C exceeds threshold"
            })
        
        return issues
    
    def _log_event(self, event_type: str, message: str):
        """Log an event."""
        self.event_log.append({
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "phase": self.phase.value
        })
    
    def mission_report(self) -> Dict:
        """Generate full mission report."""
        progress = self.get_mission_progress()
        issues = self.cross_subsystem_check()
        
        subsystem_status = {
            name: {
                "health": round(s.health_percent, 1),
                "status": s.status,
                "last_update": round(time.time() - s.last_update, 1)
            }
            for name, s in self.subsystems.items()
        }
        
        return {
            "progress": progress,
            "subsystems": subsystem_status,
            "issues": issues,
            "recent_events": self.event_log[-10:],
            "pending_goals": [g for g in self.goals if g not in self.completed_goals]
        }
