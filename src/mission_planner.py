"""
Mission Planner Module
Goal decomposition, resource allocation, and task scheduling
for autonomous mission execution.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class Priority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    """A mission task."""
    task_id: str
    description: str
    priority: Priority = Priority.MEDIUM
    duration_estimate: float = 0.0  # seconds
    dependencies: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class ResourcePool:
    """
    Manage mission resources.
    """
    
    def __init__(self):
        self.resources: Dict[str, float] = {}  # resource -> available units
        self.allocations: Dict[str, Dict[str, float]] = {}  # task -> {resource: amount}
    
    def register(self, resource: str, amount: float):
        """Register a resource."""
        self.resources[resource] = amount
    
    def allocate(self, task_id: str, resource: str, amount: float) -> bool:
        """Allocate resource to task."""
        if resource not in self.resources:
            return False
        used = sum(a.get(resource, 0) for a in self.allocations.values())
        if used + amount > self.resources[resource]:
            return False
        if task_id not in self.allocations:
            self.allocations[task_id] = {}
        self.allocations[task_id][resource] = self.allocations[task_id].get(resource, 0) + amount
        return True
    
    def deallocate(self, task_id: str):
        """Deallocate all resources from task."""
        if task_id in self.allocations:
            del self.allocations[task_id]
    
    def available(self, resource: str) -> float:
        """Get available amount of resource."""
        if resource not in self.resources:
            return 0.0
        used = sum(a.get(resource, 0) for a in self.allocations.values())
        return self.resources[resource] - used


class GoalDecomposer:
    """
    Decompose high-level goals into tasks.
    """
    
    def decompose(self, goal: str, priority: Priority = Priority.MEDIUM
                 ) -> List[Task]:
        """
        Decompose goal into tasks.
        
        Args:
            goal: Goal description
            priority: Base priority
        
        Returns:
            List of tasks
        """
        tasks = []
        
        if "orbit" in goal.lower():
            tasks.append(Task("T1", "Calculate orbital insertion", priority, 300, [], ["cpu", "fuel"]))
            tasks.append(Task("T2", "Execute burn", priority, 120, ["T1"], ["thruster", "fuel"]))
            tasks.append(Task("T3", "Verify orbit", priority, 60, ["T2"], ["sensor", "cpu"]))
        elif "land" in goal.lower():
            tasks.append(Task("T1", "Select landing site", priority, 180, [], ["sensor", "cpu"]))
            tasks.append(Task("T2", "Descent burn", priority, 300, ["T1"], ["thruster", "fuel"]))
            tasks.append(Task("T3", "Surface contact", priority, 60, ["T2"], ["sensor"]))
        elif "dock" in goal.lower():
            tasks.append(Task("T1", "Rendezvous burn", priority, 240, [], ["thruster", "fuel"]))
            tasks.append(Task("T2", "Approach maneuver", priority, 180, ["T1"], ["thruster"]))
            tasks.append(Task("T3", "Final docking", priority, 120, ["T2"], ["sensor", "thruster"]))
        else:
            tasks.append(Task("T1", f"Plan for: {goal}", priority, 100, [], ["cpu"]))
        
        return tasks
    
    def get_critical_path(self, tasks: List[Task]) -> List[str]:
        """
        Find critical path (longest dependency chain).
        
        Args:
            tasks: Task list
        
        Returns:
            List of task IDs in critical path
        """
        task_map = {t.task_id: t for t in tasks}
        
        def path_length(task_id: str, memo: Dict[str, float]) -> float:
            if task_id in memo:
                return memo[task_id]
            task = task_map.get(task_id)
            if not task:
                return 0
            max_dep = 0
            for dep in task.dependencies:
                max_dep = max(max_dep, path_length(dep, memo))
            memo[task_id] = task.duration_estimate + max_dep
            return memo[task_id]
        
        memo: Dict[str, float] = {}
        max_length = 0
        critical_end = ""
        for t in tasks:
            pl = path_length(t.task_id, memo)
            if pl > max_length:
                max_length = pl
                critical_end = t.task_id
        
        # Backtrack
        path = []
        current = critical_end
        while current:
            path.append(current)
            task = task_map.get(current)
            if not task or not task.dependencies:
                break
            # Find dependency with longest path
            current = max(task.dependencies, key=lambda d: path_length(d, memo))
        
        path.reverse()
        return path


class TaskScheduler:
    """
    Schedule tasks for execution.
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.schedule: List[str] = []
        self.current_time: float = 0.0
    
    def add_tasks(self, tasks: List[Task]):
        """Add tasks to scheduler."""
        for t in tasks:
            self.tasks[t.task_id] = t
    
    def schedule_tasks(self) -> List[str]:
        """
        Schedule tasks respecting dependencies and priority.
        
        Returns:
            Ordered task IDs
        """
        scheduled: List[str] = []
        completed: Set[str] = set()
        
        while len(scheduled) < len(self.tasks):
            ready = []
            for tid, task in self.tasks.items():
                if tid in completed or tid in scheduled:
                    continue
                if all(d in completed for d in task.dependencies):
                    ready.append(task)
            
            if not ready:
                break
            
            # Sort by priority, then by ID for determinism
            ready.sort(key=lambda t: (t.priority.value, t.task_id))
            next_task = ready[0]
            scheduled.append(next_task.task_id)
            completed.add(next_task.task_id)
        
        self.schedule = scheduled
        return scheduled
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks ready to execute."""
        completed = {tid for tid, t in self.tasks.items() if t.status == TaskStatus.COMPLETED}
        ready = []
        for tid, task in self.tasks.items():
            if task.status == TaskStatus.PENDING and all(d in completed for d in task.dependencies):
                ready.append(task)
        ready.sort(key=lambda t: (t.priority.value, t.task_id))
        return ready
    
    def mark_completed(self, task_id: str):
        """Mark task as completed."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].end_time = self.current_time
    
    def mark_failed(self, task_id: str):
        """Mark task as failed."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
    
    def mission_progress(self) -> float:
        """Get mission progress (0-1)."""
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        return completed / len(self.tasks)


class MissionPlanner:
    """
    Unified mission planning controller.
    """
    
    def __init__(self):
        self.decomposer = GoalDecomposer()
        self.scheduler = TaskScheduler()
        self.resources = ResourcePool()
    
    def plan_mission(self, goal: str, priority: Priority = Priority.MEDIUM
                    ) -> List[Task]:
        """
        Plan a mission from a high-level goal.
        
        Args:
            goal: Mission goal
            priority: Mission priority
        
        Returns:
            Planned tasks
        """
        tasks = self.decomposer.decompose(goal, priority)
        self.scheduler.add_tasks(tasks)
        self.scheduler.schedule_tasks()
        return tasks
    
    def get_critical_path(self) -> List[str]:
        """Get critical path of current mission."""
        return self.decomposer.get_critical_path(list(self.scheduler.tasks.values()))
    
    def get_ready_tasks(self) -> List[Task]:
        """Get ready tasks."""
        return self.scheduler.get_ready_tasks()
    
    def execute_next(self) -> Optional[Task]:
        """Mark next ready task as in progress."""
        ready = self.get_ready_tasks()
        if ready:
            task = ready[0]
            task.status = TaskStatus.IN_PROGRESS
            task.start_time = self.scheduler.current_time
            return task
        return None
    
    def complete_task(self, task_id: str):
        """Complete a task."""
        self.scheduler.mark_completed(task_id)
    
    def mission_progress(self) -> float:
        """Get mission progress."""
        return self.scheduler.mission_progress()
    
    def planner_summary(self) -> Dict:
        """Get planner summary."""
        return {
            "total_tasks": len(self.scheduler.tasks),
            "completed": sum(1 for t in self.scheduler.tasks.values() if t.status == TaskStatus.COMPLETED),
            "in_progress": sum(1 for t in self.scheduler.tasks.values() if t.status == TaskStatus.IN_PROGRESS),
            "pending": sum(1 for t in self.scheduler.tasks.values() if t.status == TaskStatus.PENDING),
            "progress": self.mission_progress(),
            "resources": dict(self.resources.resources)
        }
