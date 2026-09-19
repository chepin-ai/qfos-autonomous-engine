"""
Formal Methods Module
State space exploration, invariant checking, and
bounded model checking for spacecraft systems.
"""

from typing import Dict, List, Set, Tuple, Optional, Callable, Any, FrozenSet
from dataclasses import dataclass, field
from collections import deque


@dataclass(frozen=True)
class State:
    """A state in the state space."""
    values: Tuple[Tuple[str, Any], ...]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key."""
        for k, v in self.values:
            if k == key:
                return v
        return default
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "State":
        """Create state from dict."""
        return cls(tuple(sorted(d.items())))


class StateSpaceExplorer:
    """
    Explore reachable state space.
    
    Uses BFS for state space exploration.
    """
    
    def __init__(self):
        self.transitions: List[Callable[[State], List[State]]] = []
        self.visited: Set[State] = set()
        self.frontier: deque = deque()
    
    def add_transition(self, transition: Callable[[State], List[State]]):
        """Add a state transition function."""
        self.transitions.append(transition)
    
    def explore(self, initial_state: State,
               max_depth: int = 100,
               max_states: int = 10000) -> Dict:
        """
        Explore state space from initial state.
        
        Args:
            initial_state: Starting state
            max_depth: Maximum search depth
            max_states: Maximum states to explore
        
        Returns:
            Exploration result
        """
        self.visited.clear()
        self.frontier.clear()
        
        self.visited.add(initial_state)
        self.frontier.append((initial_state, 0))
        
        depth_reached = 0
        
        while self.frontier and len(self.visited) < max_states:
            current, depth = self.frontier.popleft()
            depth_reached = max(depth_reached, depth)
            
            if depth >= max_depth:
                continue
            
            for transition in self.transitions:
                try:
                    next_states = transition(current)
                    for next_state in next_states:
                        if next_state not in self.visited:
                            self.visited.add(next_state)
                            self.frontier.append((next_state, depth + 1))
                except Exception:
                    continue
        
        return {
            "states_explored": len(self.visited),
            "max_depth_reached": depth_reached,
            "frontier_remaining": len(self.frontier),
            "complete": len(self.frontier) == 0
        }
    
    def find_reachable(self, initial_state: State,
                      predicate: Callable[[State], bool],
                      max_depth: int = 100) -> Optional[State]:
        """
        Find a state satisfying predicate.
        
        Args:
            initial_state: Starting state
            predicate: Condition to find
            max_depth: Max search depth
        
        Returns:
            Found state or None
        """
        visited = {initial_state}
        frontier = deque([(initial_state, 0)])
        
        while frontier:
            current, depth = frontier.popleft()
            
            if predicate(current):
                return current
            
            if depth >= max_depth:
                continue
            
            for transition in self.transitions:
                try:
                    next_states = transition(current)
                    for next_state in next_states:
                        if next_state not in visited:
                            visited.add(next_state)
                            frontier.append((next_state, depth + 1))
                except Exception:
                    continue
        
        return None


class InvariantChecker:
    """
    Check invariants over state space.
    """
    
    def __init__(self):
        self.invariants: List[Tuple[str, Callable[[State], bool]]] = []
        self.violations: List[Tuple[str, State]] = []
    
    def add_invariant(self, name: str, check: Callable[[State], bool]):
        """Add an invariant."""
        self.invariants.append((name, check))
    
    def check(self, state: State) -> Dict[str, bool]:
        """
        Check all invariants for a state.
        
        Args:
            state: State to check
        
        Returns:
            Dict of invariant_name -> passed
        """
        results = {}
        for name, check in self.invariants:
            try:
                passed = check(state)
            except Exception:
                passed = False
            
            results[name] = passed
            
            if not passed:
                self.violations.append((name, state))
        
        return results
    
    def check_all_states(self, states: List[State]) -> Dict:
        """
        Check invariants for all states.
        
        Args:
            states: States to check
        
        Returns:
            Summary
        """
        total_checks = 0
        total_passed = 0
        
        for state in states:
            results = self.check(state)
            total_checks += len(results)
            total_passed += sum(1 for v in results.values() if v)
        
        return {
            "states_checked": len(states),
            "total_checks": total_checks,
            "total_passed": total_passed,
            "violations": len(self.violations),
            "pass_rate": round(total_passed / max(1, total_checks), 2)
        }


class BoundedModelChecker:
    """
    Bounded model checker.
    
    Checks properties within a bounded number of steps.
    """
    
    def __init__(self, bound: int = 10):
        """
        Args:
            bound: Maximum depth for BMC
        """
        self.bound = bound
        self.explorer = StateSpaceExplorer()
    
    def add_transition(self, transition: Callable[[State], List[State]]):
        """Add transition."""
        self.explorer.add_transition(transition)
    
    def check_property(self, initial_state: State,
                      property_fn: Callable[[State], bool]) -> Dict:
        """
        Check if property holds within bound.
        
        Args:
            initial_state: Starting state
            property_fn: Property to check
        
        Returns:
            Result dict
        """
        visited = {initial_state}
        frontier = deque([(initial_state, 0)])
        
        counterexamples = []
        
        while frontier:
            current, depth = frontier.popleft()
            
            # Check property
            if not property_fn(current):
                counterexamples.append((depth, current))
            
            if depth >= self.bound:
                continue
            
            for transition in self.explorer.transitions:
                try:
                    next_states = transition(current)
                    for next_state in next_states:
                        if next_state not in visited:
                            visited.add(next_state)
                            frontier.append((next_state, depth + 1))
                except Exception:
                    continue
        
        return {
            "bound": self.bound,
            "states_checked": len(visited),
            "property_holds": len(counterexamples) == 0,
            "counterexamples": len(counterexamples)
        }
    
    def check_reachability(self, initial_state: State,
                          target_predicate: Callable[[State], bool]) -> Dict:
        """
        Check if target is reachable within bound.
        
        Args:
            initial_state: Starting state
            target_predicate: Target condition
        
        Returns:
            Result dict
        """
        found = self.explorer.find_reachable(initial_state, target_predicate, self.bound)
        
        return {
            "bound": self.bound,
            "reachable": found is not None,
            "witness": found
        }


class FormalVerifier:
    """
    Unified formal verification controller.
    """
    
    def __init__(self):
        self.explorer = StateSpaceExplorer()
        self.invariants = InvariantChecker()
        self.bmc = BoundedModelChecker()
    
    def verify_system(self, initial_state: State,
                     properties: List[Callable[[State], bool]],
                     bound: int = 10) -> Dict:
        """
        Comprehensive system verification.
        
        Args:
            initial_state: Starting state
            properties: Properties to check
            bound: BMC bound
        
        Returns:
            Verification report
        """
        # Explore state space
        exploration = self.explorer.explore(initial_state, max_depth=bound)
        
        # Check invariants on visited states
        invariant_results = self.invariants.check_all_states(list(self.explorer.visited))
        
        # BMC for each property
        bmc_results = []
        for prop in properties:
            result = self.bmc.check_property(initial_state, prop)
            bmc_results.append(result)
        
        all_hold = all(r["property_holds"] for r in bmc_results)
        
        return {
            "exploration": exploration,
            "invariants": invariant_results,
            "bmc_results": bmc_results,
            "all_properties_hold": all_hold,
            "states_explored": exploration["states_explored"]
        }
    
    def verifier_summary(self) -> Dict:
        """Get verifier summary."""
        return {
            "invariants_defined": len(self.invariants.invariants),
            "bmc_bound": self.bmc.bound,
            "transitions_defined": len(self.explorer.transitions)
        }
