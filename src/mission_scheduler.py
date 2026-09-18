"""
Mission Scheduler Module
Autonomous mission activity planning and scheduling.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ActivityPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class ActivityStatus(Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class MissionActivity:
    """A single mission activity/task."""
    activity_id: str
    name: str
    priority: ActivityPriority
    duration_seconds: float
    power_requirement_w: float
    data_volume_mb: float = 0.0
    earliest_start: float = 0.0
    latest_start: Optional[float] = None
    prerequisites: List[str] = field(default_factory=list)
    resources_required: List[str] = field(default_factory=list)
    status: ActivityStatus = ActivityStatus.PENDING
    scheduled_start: Optional[float] = None
    scheduled_end: Optional[float] = None


class MissionScheduler:
    """
    Priority-based mission activity scheduler.
    
    Schedules activities considering power, data, and temporal constraints.
    """
    
    def __init__(self, available_power_w: float = 100.0,
                 available_data_rate_mbps: float = 10.0):
        self.available_power = available_power_w
        self.available_data_rate = available_data_rate_mbps
        self.activities: Dict[str, MissionActivity] = {}
        self.schedule: List[Tuple[float, str]] = []  # (start_time, activity_id)
        self.resource_usage: Dict[str, List[Tuple[float, float, str]]] = {}
    
    def add_activity(self, activity: MissionActivity):
        """Add an activity to the mission plan."""
        self.activities[activity.activity_id] = activity
    
    def schedule_activities(self, start_time: float = 0.0,
                            end_time: float = 86400.0) -> Dict:
        """
        Schedule all pending activities within the time window.
        
        Uses priority-first scheduling with constraint checking.
        
        Returns:
            Scheduling results summary
        """
        # Sort by priority (lower number = higher priority)
        pending = sorted(
            [a for a in self.activities.values() if a.status == ActivityStatus.PENDING],
            key=lambda x: (x.priority.value, x.earliest_start)
        )
        
        scheduled_count = 0
        failed_count = 0
        current_time = start_time
        
        for activity in pending:
            # Check prerequisites
            prereqs_met = all(
                self.activities[p].status == ActivityStatus.COMPLETED
                for p in activity.prerequisites if p in self.activities
            )
            
            if not prereqs_met:
                continue
            
            # Find earliest valid start time
            proposed_start = max(current_time, activity.earliest_start)
            
            if activity.latest_start is not None and proposed_start > activity.latest_start:
                activity.status = ActivityStatus.FAILED
                failed_count += 1
                continue
            
            # Check resource availability
            proposed_end = proposed_start + activity.duration_seconds
            
            if proposed_end > end_time:
                activity.status = ActivityStatus.FAILED
                failed_count += 1
                continue
            
            if not self._check_resource_availability(activity, proposed_start, proposed_end):
                # Try to find a later slot
                proposed_start = self._find_next_available_slot(activity, proposed_start, end_time)
                if proposed_start is None:
                    activity.status = ActivityStatus.FAILED
                    failed_count += 1
                    continue
                proposed_end = proposed_start + activity.duration_seconds
            
            # Schedule activity
            activity.scheduled_start = proposed_start
            activity.scheduled_end = proposed_end
            activity.status = ActivityStatus.SCHEDULED
            
            self.schedule.append((proposed_start, activity.activity_id))
            self._reserve_resources(activity, proposed_start, proposed_end)
            
            scheduled_count += 1
            current_time = proposed_end
        
        # Sort schedule by start time
        self.schedule.sort(key=lambda x: x[0])
        
        return {
            "scheduled": scheduled_count,
            "failed": failed_count,
            "total": len(pending),
            "utilization": round((current_time - start_time) / max(1, end_time - start_time), 3)
        }
    
    def _check_resource_availability(self, activity: MissionActivity,
                                     start: float, end: float) -> bool:
        """Check if resources are available for the activity."""
        # Check power
        power_used = self._get_resource_usage("power", start, end)
        if power_used + activity.power_requirement_w > self.available_power:
            return False
        
        return True
    
    def _get_resource_usage(self, resource: str, start: float, end: float) -> float:
        """Get total resource usage in a time interval."""
        if resource not in self.resource_usage:
            return 0.0
        
        total = 0.0
        for (s, e, _) in self.resource_usage[resource]:
            if s < end and e > start:
                total += self.activities[_].power_requirement_w
        
        return total
    
    def _reserve_resources(self, activity: MissionActivity, start: float, end: float):
        """Reserve resources for an activity."""
        if "power" not in self.resource_usage:
            self.resource_usage["power"] = []
        self.resource_usage["power"].append((start, end, activity.activity_id))
    
    def _find_next_available_slot(self, activity: MissionActivity,
                                  after: float, before: float) -> Optional[float]:
        """Find next available time slot for an activity."""
        step = 60.0  # Check every minute
        t = after
        
        while t + activity.duration_seconds <= before:
            if self._check_resource_availability(activity, t, t + activity.duration_seconds):
                return t
            t += step
        
        return None
    
    def execute_next(self, current_time: float) -> Optional[MissionActivity]:
        """Get the next activity to execute at current time."""
        for start, activity_id in self.schedule:
            activity = self.activities[activity_id]
            if activity.status == ActivityStatus.SCHEDULED and start <= current_time:
                activity.status = ActivityStatus.EXECUTING
                return activity
        return None
    
    def complete_activity(self, activity_id: str, success: bool = True):
        """Mark an activity as completed or failed."""
        if activity_id in self.activities:
            activity = self.activities[activity_id]
            if success:
                activity.status = ActivityStatus.COMPLETED
            else:
                activity.status = ActivityStatus.FAILED
    
    def get_schedule_summary(self) -> Dict:
        """Get summary of the mission schedule."""
        by_status = {s: [] for s in ActivityStatus}
        for activity in self.activities.values():
            by_status[activity.status].append(activity.activity_id)
        
        return {
            "total_activities": len(self.activities),
            "timeline": [
                {
                    "start": start,
                    "activity": self.activities[aid].name,
                    "duration": self.activities[aid].duration_seconds
                }
                for start, aid in sorted(self.schedule)
            ],
            "by_status": {k.value: len(v) for k, v in by_status.items()}
        }
    
    def optimize_for_power(self, solar_power_profile: List[Tuple[float, float]],
                           battery_capacity_wh: float) -> Dict:
        """
        Optimize schedule to match solar power availability.
        
        Args:
            solar_power_profile: List of (time_s, power_w) for solar generation
            battery_capacity_wh: Available battery capacity
        
        Returns:
            Optimization results
        """
        # Simple heuristic: schedule high-power activities during peak solar
        sorted_power = sorted(solar_power_profile, key=lambda x: x[1], reverse=True)
        
        high_power_activities = sorted(
            [a for a in self.activities.values() 
             if a.power_requirement_w > self.available_power * 0.5 
             and a.status == ActivityStatus.PENDING],
            key=lambda x: x.power_requirement_w,
            reverse=True
        )
        
        reassigned = 0
        for activity in high_power_activities:
            for time_s, power in sorted_power:
                if power >= activity.power_requirement_w:
                    if self._check_resource_availability(activity, time_s, 
                                                          time_s + activity.duration_seconds):
                        activity.earliest_start = time_s
                        reassigned += 1
                        break
        
        return {
            "high_power_activities": len(high_power_activities),
            "reassigned_to_peak_solar": reassigned
        }
