"""
Quantum Reinforcement Learning Advanced Module
Quantum Q-learning, quantum policy gradients,
quantum actor-critic, and quantum reward shaping for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumState:
    """Quantum state representation."""
    amplitudes: List[float]


@dataclass
class QuantumAction:
    """Quantum action representation."""
    index: int
    probability: float


class QuantumQLearning:
    """
    Quantum Q-learning algorithm.
    """
    
    def __init__(self, num_states: int = 10, num_actions: int = 4,
                 learning_rate: float = 0.1, discount: float = 0.9):
        """
        Args:
            num_states: State space size
            num_actions: Action space size
            learning_rate: Alpha
            discount: Gamma
        """
        self.n_states = num_states
        self.n_actions = num_actions
        self.alpha = learning_rate
        self.gamma = discount
        self.q_table: Dict[Tuple[int, int], float] = {}
    
    def get_q(self, state: int, action: int) -> float:
        """
        Get Q-value.
        
        Args:
            state, action: Indices
        
        Returns:
            Q-value
        """
        return self.q_table.get((state, action), 0.0)
    
    def update(self, state: int, action: int, reward: float,
              next_state: int):
        """
        Q-learning update.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
        """
        current_q = self.get_q(state, action)
        # Max Q for next state
        next_q_values = [self.get_q(next_state, a) for a in range(self.n_actions)]
        max_next_q = max(next_q_values) if next_q_values else 0.0
        # Update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q
    
    def epsilon_greedy(self, state: int, epsilon: float = 0.1) -> int:
        """
        Epsilon-greedy action selection.
        
        Args:
            state: Current state
            epsilon: Exploration rate
        
        Returns:
            Action index
        """
        import random
        if random.random() < epsilon:
            return random.randint(0, self.n_actions - 1)
        q_values = [self.get_q(state, a) for a in range(self.n_actions)]
        return q_values.index(max(q_values))


class QuantumPolicyGradient:
    """
    Quantum policy gradient methods.
    """
    
    def __init__(self, num_actions: int = 4):
        """
        Args:
            num_actions: Action space size
        """
        self.n_actions = num_actions
        self.policy_params: List[float] = [0.0] * num_actions
    
    def softmax_policy(self, state_features: List[float]) -> List[float]:
        """
        Compute action probabilities.
        
        Args:
            state_features: State features
        
        Returns:
            Action probabilities
        """
        # Simplified: softmax over policy parameters
        logits = [p + sum(state_features) * 0.1 for p in self.policy_params]
        max_logit = max(logits)
        exp_logits = [math.exp(l - max_logit) for l in logits]
        sum_exp = sum(exp_logits)
        return [e / sum_exp for e in exp_logits]
    
    def policy_gradient_update(self, state_features: List[float],
                              action: int, reward: float,
                              learning_rate: float = 0.01):
        """
        Update policy parameters.
        
        Args:
            state_features: State features
            action: Action taken
            reward: Reward
            learning_rate: Learning rate
        """
        probs = self.softmax_policy(state_features)
        # Gradient ascent: increase probability of good actions
        for a in range(self.n_actions):
            if a == action:
                self.policy_params[a] += learning_rate * reward * (1.0 - probs[a])
            else:
                self.policy_params[a] -= learning_rate * reward * probs[a]


class QuantumActorCritic:
    """
    Quantum actor-critic algorithm.
    """
    
    def __init__(self, num_states: int = 10, num_actions: int = 4):
        """
        Args:
            num_states: State space
            num_actions: Action space
        """
        self.n_states = num_states
        self.n_actions = num_actions
        self.value_function: Dict[int, float] = {}
        self.policy = QuantumPolicyGradient(num_actions)
    
    def get_value(self, state: int) -> float:
        """
        Get state value estimate.
        
        Args:
            state: State index
        
        Returns:
            Value
        """
        return self.value_function.get(state, 0.0)
    
    def update_critic(self, state: int, reward: float,
                     next_state: int,
                     learning_rate: float = 0.1,
                     discount: float = 0.9):
        """
        Update value function (critic).
        
        Args:
            state: Current state
            reward: Reward
            next_state: Next state
            learning_rate: Alpha
            discount: Gamma
        """
        current_v = self.get_value(state)
        next_v = self.get_value(next_state)
        td_error = reward + discount * next_v - current_v
        self.value_function[state] = current_v + learning_rate * td_error
        return td_error
    
    def update_actor(self, state_features: List[float],
                    action: int, td_error: float,
                    learning_rate: float = 0.01):
        """
        Update policy (actor).
        
        Args:
            state_features: State features
            action: Action taken
            td_error: TD error
            learning_rate: Alpha
        """
        self.policy.policy_gradient_update(state_features, action, td_error, learning_rate)


class QuantumRewardShaping:
    """
    Quantum reward shaping for RL.
    """
    
    def __init__(self):
        pass
    
    def potential_based_shaping(self, reward: float,
                               current_potential: float,
                               next_potential: float,
                               discount: float = 0.9) -> float:
        """
        Apply potential-based reward shaping.
        
        Args:
            reward: Original reward
            current_potential: Current state potential
            next_potential: Next state potential
            discount: Discount factor
        
        Returns:
            Shaped reward
        """
        return reward + discount * next_potential - current_potential
    
    def distance_potential(self, current_distance: float,
                          goal_distance: float = 0.0) -> float:
        """
        Compute potential from distance to goal.
        
        Args:
            current_distance: Current distance
            goal_distance: Goal distance
        
        Returns:
            Potential
        """
        return -abs(current_distance - goal_distance)


class QuantumReinforcementLearningAdvanced:
    """
    Unified quantum RL controller.
    """
    
    def __init__(self):
        self.qlearning = QuantumQLearning()
        self.policy_gradient = QuantumPolicyGradient()
        self.actor_critic = QuantumActorCritic()
        self.reward_shaping = QuantumRewardShaping()
    
    def rl_summary(self) -> Dict:
        """Get summary."""
        return {
            "algorithms": ["q_learning", "policy_gradient", "actor_critic"],
            "components": ["reward_shaping"],
            "applications": ["control", "optimization"]
        }
