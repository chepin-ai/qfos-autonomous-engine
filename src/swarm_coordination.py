"""
Swarm Coordination Module
Multi-agent formation control, flocking behaviors,
and distributed task allocation for spacecraft swarms.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class SwarmAgent:
    """An agent in the swarm."""
    id: str
    position_m: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity_ms: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    mass_kg: float = 100.0
    max_thrust_n: float = 10.0
    communication_range_m: float = 10000.0
    role: str = "follower"  # leader, follower, sentry
    assigned_task: Optional[str] = None
    status: str = "active"


class FormationController:
    """
    Formation control for spacecraft swarm.
    
    Maintains geometric formations using relative position
    control with collision avoidance.
    """
    
    def __init__(self, formation_pattern: Optional[Dict[str, Tuple[float, float, float]]] = None):
        """
        Args:
            formation_pattern: Dict of agent_id -> relative_position
        """
        self.formation = formation_pattern or {}
        self.separation_distance_m = 500.0
        self.alignment_gain = 0.5
        self.cohesion_gain = 0.3
        self.separation_gain = 1.0
    
    def compute_control(self, agent: SwarmAgent,
                       neighbors: List[SwarmAgent],
                       leader_position: Optional[Tuple[float, float, float]] = None) -> Tuple[float, float, float]:
        """
        Compute control force for agent.
        
        Args:
            agent: Agent to control
            neighbors: Visible neighbors
            leader_position: Leader position (if any)
        
        Returns:
            Control force (Fx, Fy, Fz) in N
        """
        fx, fy, fz = 0.0, 0.0, 0.0
        
        # Separation: avoid collisions
        for neighbor in neighbors:
            if neighbor.id == agent.id:
                continue
            dx = agent.position_m[0] - neighbor.position_m[0]
            dy = agent.position_m[1] - neighbor.position_m[1]
            dz = agent.position_m[2] - neighbor.position_m[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist > 0 and dist < self.separation_distance_m * 2.0:
                # Repulsive force
                force = self.separation_gain * (1.0 / dist - 1.0 / (self.separation_distance_m * 2.0))
                fx += force * dx / dist
                fy += force * dy / dist
                fz += force * dz / dist
        
        # Cohesion: move toward center of neighbors
        if neighbors:
            cx = sum(n.position_m[0] for n in neighbors) / len(neighbors)
            cy = sum(n.position_m[1] for n in neighbors) / len(neighbors)
            cz = sum(n.position_m[2] for n in neighbors) / len(neighbors)
            
            fx += self.cohesion_gain * (cx - agent.position_m[0])
            fy += self.cohesion_gain * (cy - agent.position_m[1])
            fz += self.cohesion_gain * (cz - agent.position_m[2])
        
        # Alignment: match velocity
        if neighbors:
            vx = sum(n.velocity_ms[0] for n in neighbors) / len(neighbors)
            vy = sum(n.velocity_ms[1] for n in neighbors) / len(neighbors)
            vz = sum(n.velocity_ms[2] for n in neighbors) / len(neighbors)
            
            fx += self.alignment_gain * (vx - agent.velocity_ms[0])
            fy += self.alignment_gain * (vy - agent.velocity_ms[1])
            fz += self.alignment_gain * (vz - agent.velocity_ms[2])
        
        # Formation position
        if agent.id in self.formation and leader_position:
            rel = self.formation[agent.id]
            target = (leader_position[0] + rel[0],
                     leader_position[1] + rel[1],
                     leader_position[2] + rel[2])
            
            fx += 0.8 * (target[0] - agent.position_m[0])
            fy += 0.8 * (target[1] - agent.position_m[1])
            fz += 0.8 * (target[2] - agent.position_m[2])
        
        # Limit to max thrust
        mag = math.sqrt(fx*fx + fy*fy + fz*fz)
        if mag > agent.max_thrust_n and mag > 0:
            scale = agent.max_thrust_n / mag
            fx *= scale
            fy *= scale
            fz *= scale
        
        return fx, fy, fz
    
    def update_agent(self, agent: SwarmAgent, force: Tuple[float, float, float],
                    dt_s: float = 1.0):
        """
        Update agent state with control force.
        
        Args:
            agent: Agent to update
            force: Control force
            dt_s: Time step
        """
        ax = force[0] / agent.mass_kg
        ay = force[1] / agent.mass_kg
        az = force[2] / agent.mass_kg
        
        vx = agent.velocity_ms[0] + ax * dt_s
        vy = agent.velocity_ms[1] + ay * dt_s
        vz = agent.velocity_ms[2] + az * dt_s
        
        px = agent.position_m[0] + vx * dt_s
        py = agent.position_m[1] + vy * dt_s
        pz = agent.position_m[2] + vz * dt_s
        
        agent.velocity_ms = (vx, vy, vz)
        agent.position_m = (px, py, pz)
    
    @staticmethod
    def create_line_formation(num_agents: int, spacing_m: float = 1000.0) -> Dict[str, Tuple[float, float, float]]:
        """Create line formation pattern."""
        return {
            f"agent_{i}": (i * spacing_m, 0.0, 0.0)
            for i in range(num_agents)
        }
    
    @staticmethod
    def create_triangle_formation(side_m: float = 1000.0) -> Dict[str, Tuple[float, float, float]]:
        """Create triangle formation pattern."""
        h = side_m * math.sqrt(3.0) / 2.0
        return {
            "agent_0": (0.0, 0.0, 0.0),
            "agent_1": (side_m, 0.0, 0.0),
            "agent_2": (side_m / 2.0, h, 0.0)
        }


class TaskAllocator:
    """
    Distributed task allocation for swarm.
    
    Assigns tasks to agents based on capability and proximity.
    """
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.assignments: Dict[str, str] = {}  # task_id -> agent_id
    
    def add_task(self, task_id: str, position: Tuple[float, float, float],
                 priority: int = 1, required_agents: int = 1):
        """Add a task."""
        self.tasks[task_id] = {
            "position": position,
            "priority": priority,
            "required_agents": required_agents,
            "assigned_agents": []
        }
    
    def allocate(self, agents: List[SwarmAgent]) -> Dict[str, str]:
        """
        Allocate tasks to agents.
        
        Args:
            agents: Available agents
        
        Returns:
            agent_id -> task_id mapping
        """
        assignments = {}
        
        # Sort tasks by priority
        sorted_tasks = sorted(self.tasks.items(),
                             key=lambda x: x[1]["priority"])
        
        for task_id, task in sorted_tasks:
            needed = task["required_agents"] - len(task["assigned_agents"])
            if needed <= 0:
                continue
            
            # Find closest available agents
            available = [a for a in agents
                        if a.id not in assignments and a.status == "active"]
            
            available.sort(key=lambda a: math.sqrt(
                (a.position_m[0] - task["position"][0])**2 +
                (a.position_m[1] - task["position"][1])**2 +
                (a.position_m[2] - task["position"][2])**2
            ))
            
            for agent in available[:needed]:
                assignments[agent.id] = task_id
                task["assigned_agents"].append(agent.id)
                agent.assigned_task = task_id
        
        self.assignments.update(assignments)
        return assignments
    
    def task_summary(self) -> Dict:
        """Get task allocation summary."""
        total = len(self.tasks)
        fully_assigned = sum(1 for t in self.tasks.values()
                            if len(t["assigned_agents"]) >= t["required_agents"])
        
        return {
            "total_tasks": total,
            "fully_assigned": fully_assigned,
            "partially_assigned": total - fully_assigned,
            "assigned_agents": len(self.assignments)
        }
