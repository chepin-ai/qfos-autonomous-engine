"""
Cognitive Engine Module
Belief-Desire-Intention (BDI) agent framework for
autonomous spacecraft reasoning.
"""

import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class BeliefConfidence(Enum):
    """Confidence levels for beliefs."""
    UNCERTAIN = 0.3
    LIKELY = 0.6
    CONFIDENT = 0.9
    CERTAIN = 1.0


@dataclass
class Belief:
    """A belief about the world."""
    id: str
    proposition: str
    confidence: float = 0.9
    timestamp: float = field(default_factory=time.time)
    source: str = "sensor"
    expiration: float = 3600.0  # seconds


@dataclass
class Desire:
    """A goal or objective."""
    id: str
    description: str
    priority: int = 1  # lower is higher priority
    deadline: Optional[float] = None
    active: bool = True
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class Intention:
    """A committed plan to achieve a desire."""
    id: str
    desire_id: str
    plan_steps: List[str] = field(default_factory=list)
    current_step: int = 0
    status: str = "pending"  # pending, active, completed, failed
    started_at: float = field(default_factory=time.time)


class CognitiveEngine:
    """
    BDI-based cognitive engine for autonomous reasoning.
    
    Manages beliefs, desires, and intentions with
    situation assessment and plan revision.
    """
    
    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}
        self.desires: Dict[str, Desire] = {}
        self.intentions: Dict[str, Intention] = {}
        self.reasoning_log: List[Dict] = []
    
    def add_belief(self, belief: Belief):
        """Add or update a belief."""
        self.beliefs[belief.id] = belief
    
    def add_desire(self, desire: Desire):
        """Add a desire."""
        self.desires[desire.id] = desire
    
    def revoke_belief(self, belief_id: str):
        """Revoke a belief."""
        if belief_id in self.beliefs:
            del self.beliefs[belief_id]
    
    def get_beliefs_about(self, topic: str,
                          min_confidence: float = 0.5) -> List[Belief]:
        """
        Get beliefs about a topic.
        
        Args:
            topic: Topic substring to match
            min_confidence: Minimum confidence
        
        Returns:
            Matching beliefs
        """
        results = []
        now = time.time()
        for belief in self.beliefs.values():
            if topic.lower() in belief.proposition.lower():
                if belief.confidence >= min_confidence:
                    if now - belief.timestamp < belief.expiration:
                        results.append(belief)
        return results
    
    def assess_situation(self) -> Dict:
        """
        Assess current situation from beliefs.
        
        Returns:
            Situation assessment
        """
        now = time.time()
        active_beliefs = [b for b in self.beliefs.values()
                         if now - b.timestamp < b.expiration]
        
        # Count by confidence
        certain = sum(1 for b in active_beliefs if b.confidence >= 0.9)
        likely = sum(1 for b in active_beliefs if 0.6 <= b.confidence < 0.9)
        uncertain = sum(1 for b in active_beliefs if b.confidence < 0.6)
        
        # Check for anomalies
        anomaly_beliefs = [b for b in active_beliefs
                          if "anomaly" in b.proposition.lower() or
                             "failure" in b.proposition.lower() or
                             "error" in b.proposition.lower()]
        
        # Determine situation
        if anomaly_beliefs and any(b.confidence > 0.7 for b in anomaly_beliefs):
            situation = "degraded"
        elif uncertain > certain + likely:
            situation = "uncertain"
        else:
            situation = "nominal"
        
        return {
            "situation": situation,
            "active_beliefs": len(active_beliefs),
            "certain": certain,
            "likely": likely,
            "uncertain": uncertain,
            "anomalies": len(anomaly_beliefs),
            "anomaly_confidence": max((b.confidence for b in anomaly_beliefs), default=0.0)
        }
    
    def select_desires(self) -> List[Desire]:
        """
        Select active desires sorted by priority.
        
        Returns:
            Ordered desires
        """
        active = [d for d in self.desires.values() if d.active]
        
        # Filter: check prerequisites met
        feasible = []
        for desire in active:
            prereqs_met = all(pid in self.beliefs for pid in desire.prerequisites)
            if prereqs_met:
                feasible.append(desire)
        
        # Sort by priority then deadline
        feasible.sort(key=lambda d: (d.priority, d.deadline or float('inf')))
        return feasible
    
    def form_intention(self, desire: Desire,
                       plan_steps: List[str]) -> Optional[Intention]:
        """
        Form an intention from a desire and plan.
        
        Args:
            desire: Desire to pursue
            plan_steps: Plan steps
        
        Returns:
            Intention or None
        """
        if not plan_steps:
            return None
        
        intention = Intention(
            id=f"int_{desire.id}",
            desire_id=desire.id,
            plan_steps=plan_steps,
            status="pending"
        )
        
        self.intentions[intention.id] = intention
        self.reasoning_log.append({
            "timestamp": time.time(),
            "action": "intention_formed",
            "desire": desire.id,
            "plan": plan_steps
        })
        
        return intention
    
    def execute_intention_step(self, intention_id: str) -> Dict:
        """
        Execute next step of an intention.
        
        Args:
            intention_id: Intention ID
        
        Returns:
            Execution result
        """
        if intention_id not in self.intentions:
            return {"success": False, "error": "Intention not found"}
        
        intention = self.intentions[intention_id]
        
        if intention.status in ["completed", "failed"]:
            return {"success": False, "error": f"Intention already {intention.status}"}
        
        if intention.current_step >= len(intention.plan_steps):
            intention.status = "completed"
            return {"success": True, "status": "completed"}
        
        step = intention.plan_steps[intention.current_step]
        intention.current_step += 1
        intention.status = "active"
        
        return {
            "success": True,
            "step_executed": step,
            "step_number": intention.current_step,
            "total_steps": len(intention.plan_steps),
            "status": intention.status
        }
    
    def revise_plan(self, intention_id: str,
                    new_steps: List[str]) -> bool:
        """
        Revise an intention's plan.
        
        Args:
            intention_id: Intention to revise
            new_steps: New plan steps
        
        Returns:
            Success
        """
        if intention_id not in self.intentions:
            return False
        
        intention = self.intentions[intention_id]
        intention.plan_steps = new_steps
        intention.current_step = min(intention.current_step, len(new_steps))
        
        self.reasoning_log.append({
            "timestamp": time.time(),
            "action": "plan_revised",
            "intention": intention_id,
            "new_plan": new_steps
        })
        
        return True
    
    def detect_conflict(self) -> List[Tuple[str, str, str]]:
        """
        Detect conflicts between intentions.
        
        Returns:
            List of (intention_a, intention_b, reason) tuples
        """
        conflicts = []
        active_intentions = [i for i in self.intentions.values()
                            if i.status in ["pending", "active"]]
        
        for i, int_a in enumerate(active_intentions):
            for int_b in active_intentions[i+1:]:
                # Check if they share desires
                desire_a = self.desires.get(int_a.desire_id)
                desire_b = self.desires.get(int_b.desire_id)
                
                if desire_a and desire_b:
                    # Simple conflict: same priority competing
                    if desire_a.priority == desire_b.priority:
                        conflicts.append((int_a.id, int_b.id, "same_priority"))
        
        return conflicts
    
    def cognitive_summary(self) -> Dict:
        """Get cognitive state summary."""
        situation = self.assess_situation()
        active_desires = len([d for d in self.desires.values() if d.active])
        active_intentions = len([i for i in self.intentions.values()
                                if i.status in ["pending", "active"]])
        
        return {
            "beliefs": len(self.beliefs),
            "desires": len(self.desires),
            "intentions": len(self.intentions),
            "active_desires": active_desires,
            "active_intentions": active_intentions,
            "situation": situation["situation"],
            "reasoning_steps": len(self.reasoning_log)
        }
