"""
Autonomous Decision Engine
Rule-based and heuristic decision making for spacecraft
autonomous operations: action selection, priority ranking,
and mission state management.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class MissionState(Enum):
    """Mission execution states."""
    IDLE = "idle"
    NOMINAL = "nominal"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    ABORT = "abort"
    SAFE_MODE = "safe_mode"


class ActionPriority(Enum):
    """Action priority levels."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    DEFERRED = 4


@dataclass
class SystemStatus:
    """Status of a spacecraft system."""
    name: str
    health_percent: float = 100.0
    temperature_c: float = 20.0
    power_w: float = 0.0
    fault_code: Optional[str] = None
    operational: bool = True


@dataclass
class Action:
    """A possible action."""
    name: str
    priority: ActionPriority
    preconditions: List[str] = field(default_factory=list)
    effects: Dict[str, float] = field(default_factory=dict)
    estimated_duration_s: float = 60.0
    resource_cost: Dict[str, float] = field(default_factory=dict)
    fallback_action: Optional[str] = None


class DecisionEngine:
    """
    Autonomous decision engine for spacecraft operations.
    
    Rule-based action selection with priority ranking,
    precondition checking, and mission state management.
    """
    
    def __init__(self):
        self.state = MissionState.NOMINAL
        self.systems: Dict[str, SystemStatus] = {}
        self.actions: Dict[str, Action] = {}
        self.rules: List[Callable] = []
        self.decision_log: List[Dict] = []
        self.current_plan: List[str] = []
    
    def add_system(self, status: SystemStatus):
        """Add a system to monitor."""
        self.systems[status.name] = status
    
    def add_action(self, action: Action):
        """Add an available action."""
        self.actions[action.name] = action
    
    def update_system(self, name: str, **kwargs):
        """Update system status."""
        if name in self.systems:
            for key, value in kwargs.items():
                if hasattr(self.systems[name], key):
                    setattr(self.systems[name], key, value)
        
        self._assess_mission_state()
    
    def _assess_mission_state(self):
        """Assess overall mission state from systems."""
        critical_count = 0
        degraded_count = 0
        
        for sys in self.systems.values():
            if sys.health_percent < 30.0 or not sys.operational:
                critical_count += 1
            elif sys.health_percent < 70.0:
                degraded_count += 1
        
        if critical_count >= 2:
            self.state = MissionState.ABORT
        elif critical_count == 1:
            self.state = MissionState.CRITICAL
        elif degraded_count >= 2:
            self.state = MissionState.DEGRADED
        elif critical_count == 0 and degraded_count == 0:
            self.state = MissionState.NOMINAL
    
    def check_preconditions(self, action: Action) -> Tuple[bool, List[str]]:
        """
        Check if action preconditions are met.
        
        Args:
            action: Action to check
        
        Returns:
            (met, missing_preconditions)
        """
        missing = []
        
        for precond in action.preconditions:
            # Parse precondition: "system:health>50" or "state:nominal"
            if ":" in precond:
                target, condition = precond.split(":", 1)
                
                if target in self.systems:
                    sys = self.systems[target]
                    if ">" in condition:
                        attr, val = condition.split(">")
                        attr = attr.strip()
                        val = float(val.strip())
                        actual = getattr(sys, attr, 0.0)
                        if actual <= val:
                            missing.append(precond)
                    elif "==" in condition:
                        attr, val = condition.split("==")
                        actual = getattr(sys, attr.strip(), None)
                        if str(actual) != val.strip():
                            missing.append(precond)
                elif target == "state":
                    if self.state.value != condition.strip():
                        missing.append(precond)
                else:
                    missing.append(precond)
        
        return len(missing) == 0, missing
    
    def score_action(self, action: Action, context: Optional[Dict] = None) -> float:
        """
        Score an action for current context.
        
        Args:
            action: Action to score
            context: Current mission context
        
        Returns:
            Score (higher is better)
        """
        base_score = 100.0 - action.priority.value * 20.0
        
        # Penalize resource cost
        resource_penalty = sum(action.resource_cost.values()) * 5.0
        
        # Penalize long duration
        duration_penalty = action.estimated_duration_s / 3600.0 * 10.0
        
        # Context bonus
        context_bonus = 0.0
        if context:
            for effect, value in action.effects.items():
                if effect in context and context[effect] < value:
                    context_bonus += 20.0
        
        score = base_score - resource_penalty - duration_penalty + context_bonus
        
        return round(max(0.0, score), 2)
    
    def select_action(self, available: Optional[List[str]] = None,
                      context: Optional[Dict] = None) -> Optional[Action]:
        """
        Select best action from available options.
        
        Args:
            available: List of action names (default: all)
            context: Mission context
        
        Returns:
            Best action or None
        """
        candidates = []
        action_names = available or list(self.actions.keys())
        
        for name in action_names:
            if name not in self.actions:
                continue
            
            action = self.actions[name]
            precond_met, missing = self.check_preconditions(action)
            
            if precond_met:
                score = self.score_action(action, context)
                candidates.append((score, action))
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    
    def generate_plan(self, goals: List[str],
                      context: Optional[Dict] = None) -> List[str]:
        """
        Generate action plan to achieve goals.
        
        Simple greedy plan generation.
        
        Args:
            goals: Goal states to achieve
            context: Mission context
        
        Returns:
            Ordered list of action names
        """
        plan = []
        remaining = set(self.actions.keys())
        
        for _ in range(len(self.actions)):
            action = self.select_action(list(remaining), context)
            if action is None:
                break
            
            plan.append(action.name)
            remaining.discard(action.name)
            
            # Update context with action effects
            if context is not None:
                for effect, value in action.effects.items():
                    context[effect] = max(context.get(effect, 0.0), value)
        
        self.current_plan = plan
        return plan
    
    def execute_action(self, action_name: str) -> Dict:
        """
        Execute an action and log decision.
        """
        if action_name not in self.actions:
            return {"success": False, "error": "Unknown action"}
        
        action = self.actions[action_name]
        precond_met, missing = self.check_preconditions(action)
        
        result = {
            "action": action_name,
            "preconditions_met": precond_met,
            "missing_preconditions": missing,
            "state": self.state.value,
            "success": precond_met
        }
        
        if precond_met:
            # Apply effects
            for effect, value in action.effects.items():
                if effect in self.systems:
                    sys = self.systems[effect]
                    if "health" in effect.lower():
                        sys.health_percent = min(100.0, sys.health_percent + value)
                    elif "power" in effect.lower():
                        sys.power_w += value
        
        self.decision_log.append(result)
        return result
    
    def mission_summary(self) -> Dict:
        """Get mission decision summary."""
        return {
            "state": self.state.value,
            "systems_monitored": len(self.systems),
            "actions_available": len(self.actions),
            "decisions_made": len(self.decision_log),
            "current_plan_length": len(self.current_plan),
            "system_healths": {name: round(s.health_percent, 1)
                              for name, s in self.systems.items()}
        }
