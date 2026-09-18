"""
Path Planner Module
Orbital transfer path planning using graph-based node search.
"""

import math
import heapq
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

try:
    from .orbital_mechanics import OrbitalBody, hohmann_transfer_delta_v, MU_SUN, AU
except ImportError:
    from orbital_mechanics import OrbitalBody, hohmann_transfer_delta_v, MU_SUN, AU


@dataclass
class PathNode:
    """A node in the orbital transfer graph."""
    body: OrbitalBody
    arrival_time_days: float = 0.0
    cumulative_delta_v: float = 0.0
    parent: Optional['PathNode'] = None
    
    def __hash__(self):
        return hash(self.body.name)
    
    def __eq__(self, other):
        return isinstance(other, PathNode) and self.body.name == other.body.name


class OrbitalPathPlanner:
    """
    Plan multi-leg orbital transfers between celestial bodies.
    Uses A* search with delta-v as cost metric.
    """
    
    def __init__(self, bodies: List[OrbitalBody]):
        self.bodies = {b.name: b for b in bodies}
        self.body_list = bodies
    
    def _heuristic(self, from_body: OrbitalBody, to_body: OrbitalBody) -> float:
        """Estimate remaining cost (Hohmann transfer delta-v)."""
        try:
            dv, _ = hohmann_transfer_delta_v(from_body, to_body)
            return dv
        except:
            # Fallback: use semi-major axis difference
            return abs(from_body.semi_major_axis_au - to_body.semi_major_axis_au) * 1000
    
    def plan_transfer(self, start_name: str, target_name: str,
                      max_legs: int = 3) -> Optional[Dict]:
        """
        Plan a transfer from start to target.
        
        Returns dict with path details or None if no path found.
        """
        if start_name not in self.bodies or target_name not in self.bodies:
            return None
        
        start_body = self.bodies[start_name]
        target_body = self.bodies[target_name]
        
        # Direct transfer
        direct_dv, direct_time = hohmann_transfer_delta_v(start_body, target_body)
        
        best_plan = {
            "path": [start_name, target_name],
            "total_delta_v_ms": direct_dv,
            "total_time_days": direct_time,
            "legs": 1,
            "type": "direct"
        }
        
        # Try intermediate waypoints
        if max_legs >= 2:
            best_multi = self._find_multi_leg_path(start_body, target_body, max_legs)
            if best_multi and best_multi["total_delta_v_ms"] < best_plan["total_delta_v_ms"]:
                best_plan = best_multi
        
        return best_plan
    
    def _find_multi_leg_path(self, start: OrbitalBody, target: OrbitalBody,
                             max_legs: int) -> Optional[Dict]:
        """Find best multi-leg path using A* search."""
        
        open_set = []
        start_node = PathNode(start, 0.0, 0.0)
        heapq.heappush(open_set, (0.0, 0, start_node))
        
        visited = set()
        best_result = None
        
        while open_set:
            _, _, current = heapq.heappop(open_set)
            
            if current.body.name == target.name:
                # Reconstruct path
                path = []
                node = current
                while node:
                    path.append(node.body.name)
                    node = node.parent
                path.reverse()
                
                return {
                    "path": path,
                    "total_delta_v_ms": current.cumulative_delta_v,
                    "total_time_days": current.arrival_time_days,
                    "legs": len(path) - 1,
                    "type": "multi-leg"
                }
            
            if current.body.name in visited:
                continue
            visited.add(current.body.name)
            
            # Count depth (number of legs from start)
            depth = 0
            node = current
            while node.parent:
                depth += 1
                node = node.parent
            
            if depth >= max_legs:
                continue
            
            # Explore neighbors
            for body in self.body_list:
                if body.name == current.body.name or body.name in visited:
                    continue
                
                try:
                    dv, dt = hohmann_transfer_delta_v(current.body, body)
                except:
                    continue
                
                new_cost = current.cumulative_delta_v + dv
                new_time = current.arrival_time_days + dt
                
                h = self._heuristic(body, target)
                priority = new_cost + h
                
                neighbor = PathNode(body, new_time, new_cost, current)
                heapq.heappush(open_set, (priority, id(neighbor), neighbor))
        
        return None
    
    def compare_transfer_options(self, start_name: str, target_name: str) -> List[Dict]:
        """Compare all available transfer options."""
        seen_paths = set()
        options = []
        
        for max_legs in [1, 2, 3]:
            plan = self.plan_transfer(start_name, target_name, max_legs)
            if plan:
                path_key = tuple(plan["path"])
                if path_key not in seen_paths:
                    seen_paths.add(path_key)
                    options.append(plan)
        
        # Sort by delta-v
        options.sort(key=lambda x: x["total_delta_v_ms"])
        return options
