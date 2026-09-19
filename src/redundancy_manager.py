"""
Redundancy Manager Module
Component replication, hot standby, and switchover logic
for spacecraft subsystem redundancy.
"""

import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class ComponentState(Enum):
    """State of a redundant component."""
    ACTIVE = "active"
    STANDBY = "standby"
    DEGRADED = "degraded"
    FAILED = "failed"
    OFFLINE = "offline"


@dataclass
class Component:
    """A spacecraft component."""
    component_id: str
    component_type: str
    state: ComponentState = ComponentState.STANDBY
    health_score: float = 1.0
    last_heartbeat: float = 0.0
    activation_count: int = 0
    
    def __post_init__(self):
        if self.last_heartbeat == 0.0:
            self.last_heartbeat = time.time()
    
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.state in (ComponentState.ACTIVE, ComponentState.STANDBY) and \
               self.health_score > 0.5
    
    def activate(self):
        """Activate component."""
        self.state = ComponentState.ACTIVE
        self.activation_count += 1
    
    def standby(self):
        """Put component in standby."""
        if self.state != ComponentState.FAILED:
            self.state = ComponentState.STANDBY
    
    def fail(self):
        """Mark component as failed."""
        self.state = ComponentState.FAILED
        self.health_score = 0.0


@dataclass
class RedundancyGroup:
    """A group of redundant components."""
    group_id: str
    group_type: str
    components: Dict[str, Component] = field(default_factory=dict)
    active_component: Optional[str] = None
    failover_policy: str = "priority"  # priority, round_robin, health
    
    def add_component(self, component: Component):
        """Add component to group."""
        self.components[component.component_id] = component
        if self.active_component is None and component.is_healthy():
            self.active_component = component.component_id
            component.activate()
    
    def get_active(self) -> Optional[Component]:
        """Get currently active component."""
        if self.active_component and self.active_component in self.components:
            return self.components[self.active_component]
        return None
    
    def get_standby(self) -> List[Component]:
        """Get standby components."""
        return [c for c in self.components.values()
                if c.state == ComponentState.STANDBY and c.is_healthy()]
    
    def get_healthy(self) -> List[Component]:
        """Get all healthy components."""
        return [c for c in self.components.values() if c.is_healthy()]
    
    def failover(self) -> Optional[str]:
        """
        Failover to next available component.
        
        Returns:
            New active component ID or None
        """
        standby = self.get_standby()
        if not standby:
            return None
        
        if self.failover_policy == "health":
            # Select healthiest
            next_comp = max(standby, key=lambda c: c.health_score)
        else:
            # Priority: first available
            next_comp = standby[0]
        
        # Deactivate current
        if self.active_component and self.active_component in self.components:
            self.components[self.active_component].standby()
        
        # Activate new
        next_comp.activate()
        self.active_component = next_comp.component_id
        
        return next_comp.component_id
    
    def redundancy_level(self) -> int:
        """Get current redundancy level."""
        return len(self.get_healthy())
    
    def is_degraded(self) -> bool:
        """Check if group is degraded."""
        healthy = len(self.get_healthy())
        total = len(self.components)
        return healthy < total


class HealthMonitor:
    """
    Monitor component health.
    """
    
    def __init__(self, heartbeat_timeout: float = 10.0):
        """
        Args:
            heartbeat_timeout: Heartbeat timeout in seconds
        """
        self.heartbeat_timeout = heartbeat_timeout
        self.health_checks: Dict[str, Callable[[], float]] = {}
        self.heartbeats: Dict[str, float] = {}
    
    def register_check(self, component_id: str,
                      check_fn: Callable[[], float]):
        """Register health check function."""
        self.health_checks[component_id] = check_fn
    
    def update_heartbeat(self, component_id: str):
        """Update component heartbeat."""
        self.heartbeats[component_id] = time.time()
    
    def check_health(self, component: Component) -> float:
        """
        Check component health.
        
        Args:
            component: Component to check
        
        Returns:
            Health score 0-1
        """
        # Check heartbeat
        last_hb = self.heartbeats.get(component.component_id, 0)
        if time.time() - last_hb > self.heartbeat_timeout:
            component.health_score *= 0.9
        
        # Run custom check
        if component.component_id in self.health_checks:
            try:
                score = self.health_checks[component.component_id]()
                component.health_score = 0.7 * component.health_score + 0.3 * score
            except Exception:
                component.health_score *= 0.8
        
        component.health_score = max(0.0, min(1.0, component.health_score))
        
        # Update state based on health
        if component.health_score < 0.2:
            component.fail()
        elif component.health_score < 0.5:
            component.state = ComponentState.DEGRADED
        
        return component.health_score


class SwitchoverController:
    """
    Control switchover between redundant components.
    """
    
    def __init__(self):
        self.groups: Dict[str, RedundancyGroup] = {}
        self.monitor = HealthMonitor()
        self.switch_log: List[Dict] = []
    
    def create_group(self, group_id: str, group_type: str,
                    policy: str = "priority"):
        """Create redundancy group."""
        self.groups[group_id] = RedundancyGroup(
            group_id=group_id,
            group_type=group_type,
            failover_policy=policy
        )
    
    def add_to_group(self, group_id: str, component: Component):
        """Add component to group."""
        if group_id in self.groups:
            self.groups[group_id].add_component(component)
    
    def perform_switchover(self, group_id: str,
                          reason: str = "manual") -> Optional[str]:
        """
        Perform manual switchover.
        
        Args:
            group_id: Group ID
            reason: Switchover reason
        
        Returns:
            New active component ID or None
        """
        if group_id not in self.groups:
            return None
        
        group = self.groups[group_id]
        old_active = group.active_component
        new_active = group.failover()
        
        if new_active:
            self.switch_log.append({
                "time": time.time(),
                "group": group_id,
                "from": old_active,
                "to": new_active,
                "reason": reason
            })
        
        return new_active
    
    def auto_failover(self, group_id: str) -> Optional[str]:
        """
        Perform automatic failover if active is unhealthy.
        
        Args:
            group_id: Group ID
        
        Returns:
            New active component ID or None
        """
        if group_id not in self.groups:
            return None
        
        group = self.groups[group_id]
        active = group.get_active()
        
        if active and not active.is_healthy():
            return self.perform_switchover(group_id, "auto_failover")
        
        return None
    
    def get_group_status(self, group_id: str) -> Dict:
        """Get group status."""
        if group_id not in self.groups:
            return {}
        
        group = self.groups[group_id]
        return {
            "group_id": group_id,
            "active": group.active_component,
            "standby": [c.component_id for c in group.get_standby()],
            "healthy_count": len(group.get_healthy()),
            "total_count": len(group.components),
            "degraded": group.is_degraded()
        }
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all groups."""
        return {gid: self.get_group_status(gid) for gid in self.groups}


class RedundancyManager:
    """
    Unified redundancy management controller.
    """
    
    def __init__(self):
        self.switchover = SwitchoverController()
        self.groups: Dict[str, RedundancyGroup] = {}
    
    def create_redundant_pair(self, group_id: str, group_type: str,
                             primary_id: str, backup_id: str):
        """
        Create simple primary-backup pair.
        
        Args:
            group_id: Group identifier
            group_type: Component type
            primary_id: Primary component ID
            backup_id: Backup component ID
        """
        self.switchover.create_group(group_id, group_type)
        
        primary = Component(primary_id, group_type, ComponentState.ACTIVE)
        backup = Component(backup_id, group_type, ComponentState.STANDBY)
        
        self.switchover.add_to_group(group_id, primary)
        self.switchover.add_to_group(group_id, backup)
        
        self.groups[group_id] = self.switchover.groups[group_id]
    
    def create_n_plus_m(self, group_id: str, group_type: str,
                       active_ids: List[str], standby_ids: List[str]):
        """
        Create N+M redundancy group.
        
        Args:
            group_id: Group identifier
            group_type: Component type
            active_ids: Active component IDs
            standby_ids: Standby component IDs
        """
        self.switchover.create_group(group_id, group_type)
        
        for i, cid in enumerate(active_ids):
            state = ComponentState.ACTIVE if i == 0 else ComponentState.STANDBY
            comp = Component(cid, group_type, state)
            self.switchover.add_to_group(group_id, comp)
        
        for cid in standby_ids:
            comp = Component(cid, group_type, ComponentState.STANDBY)
            self.switchover.add_to_group(group_id, comp)
        
        self.groups[group_id] = self.switchover.groups[group_id]
    
    def failover(self, group_id: str) -> Optional[str]:
        """Failover group."""
        return self.switchover.perform_switchover(group_id)
    
    def rm_summary(self) -> Dict:
        """Get redundancy summary."""
        total_components = sum(len(g.components) for g in self.groups.values())
        healthy_components = sum(len(g.get_healthy()) for g in self.groups.values())
        
        return {
            "groups": len(self.groups),
            "total_components": total_components,
            "healthy_components": healthy_components,
            "switchovers": len(self.switchover.switch_log),
            "group_status": self.switchover.get_all_status()
        }
