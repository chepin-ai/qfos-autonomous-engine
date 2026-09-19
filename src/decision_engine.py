"""
Decision Engine Module
MDP-based autonomous decision making, policy evaluation,
and value iteration for spacecraft control.
"""

from typing import Dict, List, Tuple, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class State:
    """A state in the MDP."""
    name: str
    features: Dict[str, float] = field(default_factory=dict)


@dataclass
class Action:
    """An action in the MDP."""
    name: str
    cost: float = 0.0


@dataclass
class Transition:
    """A state transition."""
    from_state: str
    action: str
    to_state: str
    probability: float
    reward: float = 0.0


class MDP:
    """
    Markov Decision Process.
    """
    
    def __init__(self, gamma: float = 0.95):
        """
        Args:
            gamma: Discount factor
        """
        self.gamma = gamma
        self.states: Dict[str, State] = {}
        self.actions: Dict[str, Action] = {}
        self.transitions: List[Transition] = []
        self.transition_map: Dict[Tuple[str, str], List[Tuple[str, float, float]]] = defaultdict(list)
    
    def add_state(self, state: State):
        """Add state."""
        self.states[state.name] = state
    
    def add_action(self, action: Action):
        """Add action."""
        self.actions[action.name] = action
    
    def add_transition(self, trans: Transition):
        """Add transition."""
        self.transitions.append(trans)
        self.transition_map[(trans.from_state, trans.action)].append(
            (trans.to_state, trans.probability, trans.reward)
        )
    
    def get_transitions(self, state: str, action: str) -> List[Tuple[str, float, float]]:
        """Get transitions for state-action pair."""
        return self.transition_map.get((state, action), [])
    
    def get_available_actions(self, state: str) -> List[str]:
        """Get available actions at state."""
        actions = []
        for (s, a) in self.transition_map:
            if s == state and a not in actions:
                actions.append(a)
        return actions


class ValueIteration:
    """
    Value iteration for MDP.
    """
    
    def __init__(self, mdp: MDP, theta: float = 1e-6):
        """
        Args:
            mdp: MDP to solve
            theta: Convergence threshold
        """
        self.mdp = mdp
        self.theta = theta
        self.values: Dict[str, float] = {}
        self.policy: Dict[str, str] = {}
    
    def solve(self, max_iterations: int = 1000) -> Dict[str, float]:
        """
        Run value iteration.
        
        Args:
            max_iterations: Maximum iterations
        
        Returns:
            Value function
        """
        # Initialize values
        for s in self.mdp.states:
            self.values[s] = 0.0
        
        for _ in range(max_iterations):
            delta = 0.0
            
            for s in self.mdp.states:
                v = self.values[s]
                actions = self.mdp.get_available_actions(s)
                
                if not actions:
                    continue
                
                # Compute best action value
                best_value = float('-inf')
                for a in actions:
                    action_value = 0.0
                    for s_next, prob, reward in self.mdp.get_transitions(s, a):
                        action_value += prob * (reward + self.mdp.gamma * self.values.get(s_next, 0.0))
                    best_value = max(best_value, action_value)
                
                self.values[s] = best_value
                delta = max(delta, abs(v - best_value))
            
            if delta < self.theta:
                break
        
        # Extract policy
        for s in self.mdp.states:
            actions = self.mdp.get_available_actions(s)
            if actions:
                best_action = None
                best_value = float('-inf')
                for a in actions:
                    action_value = 0.0
                    for s_next, prob, reward in self.mdp.get_transitions(s, a):
                        action_value += prob * (reward + self.mdp.gamma * self.values.get(s_next, 0.0))
                    if action_value > best_value:
                        best_value = action_value
                        best_action = a
                self.policy[s] = best_action
        
        return self.values
    
    def get_policy(self) -> Dict[str, str]:
        """Get computed policy."""
        return self.policy.copy()
    
    def evaluate_state(self, state: str) -> float:
        """Evaluate state value."""
        return self.values.get(state, 0.0)


class PolicyEvaluator:
    """
    Evaluate a policy's expected return.
    """
    
    def __init__(self, mdp: MDP):
        """
        Args:
            mdp: MDP
        """
        self.mdp = mdp
    
    def evaluate(self, policy: Dict[str, str],
                max_iterations: int = 1000,
                theta: float = 1e-6) -> Dict[str, float]:
        """
        Evaluate policy.
        
        Args:
            policy: State -> action mapping
            max_iterations: Maximum iterations
            theta: Convergence threshold
        
        Returns:
            Value function
        """
        values = {s: 0.0 for s in self.mdp.states}
        
        for _ in range(max_iterations):
            delta = 0.0
            
            for s in self.mdp.states:
                v = values[s]
                a = policy.get(s)
                
                if a is None:
                    continue
                
                new_value = 0.0
                for s_next, prob, reward in self.mdp.get_transitions(s, a):
                    new_value += prob * (reward + self.mdp.gamma * values.get(s_next, 0.0))
                
                values[s] = new_value
                delta = max(delta, abs(v - new_value))
            
            if delta < theta:
                break
        
        return values


class DecisionEngine:
    """
    Unified autonomous decision engine.
    """
    
    def __init__(self):
        self.mdp = MDP()
        self.value_iteration: Optional[ValueIteration] = None
        self.evaluator = PolicyEvaluator(self.mdp)
    
    def define_mdp(self, states: List[State], actions: List[Action],
                  transitions: List[Transition]):
        """
        Define the decision MDP.
        
        Args:
            states: States
            actions: Actions
            transitions: Transitions
        """
        for s in states:
            self.mdp.add_state(s)
        for a in actions:
            self.mdp.add_action(a)
        for t in transitions:
            self.mdp.add_transition(t)
    
    def compute_optimal_policy(self) -> Dict[str, str]:
        """
        Compute optimal policy via value iteration.
        
        Returns:
            Policy
        """
        self.value_iteration = ValueIteration(self.mdp)
        self.value_iteration.solve()
        return self.value_iteration.get_policy()
    
    def decide(self, state: str) -> Optional[str]:
        """
        Make decision at state.
        
        Args:
            state: Current state
        
        Returns:
            Best action
        """
        if self.value_iteration is None:
            self.compute_optimal_policy()
        
        return self.value_iteration.get_policy().get(state)
    
    def evaluate_policy(self, policy: Dict[str, str]) -> Dict[str, float]:
        """
        Evaluate a policy.
        
        Args:
            policy: Policy to evaluate
        
        Returns:
            Value function
        """
        return self.evaluator.evaluate(policy)
    
    def engine_summary(self) -> Dict:
        """Get engine summary."""
        return {
            "states": len(self.mdp.states),
            "actions": len(self.mdp.actions),
            "transitions": len(self.mdp.transitions),
            "policy_computed": self.value_iteration is not None
        }
