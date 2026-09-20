"""
Quantum Reinforcement Learning Module
Quantum policy gradients, variational Q-learning,
quantum advantage estimation, and autonomous action selection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumPolicy:
    """Quantum policy parameters."""
    rotations: List[Tuple[float, float, float]]
    num_qubits: int


class QuantumPolicyNetwork:
    """
    Quantum policy network.
    """
    
    def __init__(self, num_qubits: int, num_actions: int):
        """
        Args:
            num_qubits: Qubits
            num_actions: Actions
        """
        self.n = num_qubits
        self.m = num_actions
        self.policy: Optional[QuantumPolicy] = None
    
    def initialize(self):
        """Initialize random policy."""
        import random
        rotations = [(random.uniform(0, 2*math.pi),
                     random.uniform(0, 2*math.pi),
                     random.uniform(0, 2*math.pi))
                    for _ in range(self.n)]
        self.policy = QuantumPolicy(rotations, self.n)
    
    def action_probabilities(self, state: List[float]) -> List[float]:
        """
        Compute action probabilities.
        
        Args:
            state: State
        
        Returns:
            Probabilities
        """
        if not self.policy:
            self.initialize()
        
        # Simplified: encode state into rotation angles
        probs = []
        for i in range(self.m):
            angle = sum(s * self.policy.rotations[i % self.n][0]
                       for s in state) if state else 0.0
            probs.append(math.cos(angle) ** 2)
        
        # Normalize
        total = sum(probs)
        if total > 0:
            return [p / total for p in probs]
        return [1.0 / self.m] * self.m
    
    def select_action(self, state: List[float]) -> int:
        """
        Select action.
        
        Args:
            state: State
        
        Returns:
            Action index
        """
        probs = self.action_probabilities(state)
        import random
        r = random.random()
        cumsum = 0.0
        for i, p in enumerate(probs):
            cumsum += p
            if r <= cumsum:
                return i
        return len(probs) - 1


class QuantumAdvantageEstimator:
    """
    Quantum advantage estimation.
    """
    
    def __init__(self):
        pass
    
    def compute_advantage(self, rewards: List[float],
                         values: List[float],
                         gamma: float = 0.99,
                         lambda_gae: float = 0.95) -> List[float]:
        """
        Compute GAE advantages.
        
        Args:
            rewards: Rewards
            values: Value estimates
            gamma: Discount
            lambda_gae: GAE lambda
        
        Returns:
            Advantages
        """
        advantages = []
        gae = 0.0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0.0
            else:
                next_value = values[t + 1]
            
            delta = rewards[t] + gamma * next_value - values[t]
            gae = delta + gamma * lambda_gae * gae
            advantages.insert(0, gae)
        
        return advantages


class VariationalQLearning:
    """
    Variational quantum Q-learning.
    """
    
    def __init__(self, num_qubits: int, num_actions: int):
        """
        Args:
            num_qubits: Qubits
            num_actions: Actions
        """
        self.n = num_qubits
        self.m = num_actions
        self.q_values: Dict[Tuple[int, int], float] = {}
        self.learning_rate = 0.1
        self.epsilon = 0.1
    
    def q_value(self, state_idx: int, action: int) -> float:
        """
        Get Q-value.
        
        Args:
            state_idx: State index
            action: Action
        
        Returns:
            Q-value
        """
        return self.q_values.get((state_idx, action), 0.0)
    
    def update(self, state_idx: int, action: int,
              reward: float, next_state_idx: int,
              gamma: float = 0.99):
        """
        Update Q-value.
        
        Args:
            state_idx: State
            action: Action
            reward: Reward
            next_state_idx: Next state
            gamma: Discount
        """
        current = self.q_value(state_idx, action)
        
        # Max Q for next state
        next_qs = [self.q_value(next_state_idx, a) for a in range(self.m)]
        max_next = max(next_qs) if next_qs else 0.0
        
        # Q-learning update
        new_q = current + self.learning_rate * (reward + gamma * max_next - current)
        self.q_values[(state_idx, action)] = new_q
    
    def select_action(self, state_idx: int) -> int:
        """
        Select action (epsilon-greedy).
        
        Args:
            state_idx: State
        
        Returns:
            Action
        """
        import random
        if random.random() < self.epsilon:
            return random.randint(0, self.m - 1)
        
        qs = [self.q_value(state_idx, a) for a in range(self.m)]
        return qs.index(max(qs))


class QuantumReinforcementLearning:
    """
    Unified quantum RL controller.
    """
    
    def __init__(self, num_qubits: int = 4, num_actions: int = 4):
        self.policy = QuantumPolicyNetwork(num_qubits, num_actions)
        self.advantage = QuantumAdvantageEstimator()
        self.qlearner = VariationalQLearning(num_qubits, num_actions)
        self.episodes: List[Dict] = []
    
    def train_episode(self, states: List[List[float]],
                     actions: List[int],
                     rewards: List[float]) -> Dict:
        """
        Train on episode.
        
        Args:
            states: States
            actions: Actions
            rewards: Rewards
        
        Returns:
            Results
        """
        total_reward = sum(rewards)
        
        # Update Q-values
        for t in range(len(states) - 1):
            self.qlearner.update(t, actions[t], rewards[t], t + 1)
        
        result = {
            "total_reward": total_reward,
            "steps": len(states)
        }
        self.episodes.append(result)
        return result
    
    def qrl_summary(self) -> Dict:
        """Get summary."""
        avg_reward = sum(e["total_reward"] for e in self.episodes) / len(self.episodes) if self.episodes else 0.0
        return {
            "episodes": len(self.episodes),
            "avg_reward": avg_reward,
            "q_entries": len(self.qlearner.q_values)
        }
