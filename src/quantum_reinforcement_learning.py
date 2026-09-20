"""
Quantum Reinforcement Learning Module
Quantum policy gradients, quantum Q-learning, and
variational quantum circuits for autonomous decision making.
"""

import math
import random
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass


class QuantumPolicy:
    """
    Quantum policy represented by a variational circuit.
    """
    
    def __init__(self, num_qubits: int = 4, num_actions: int = 2):
        """
        Args:
            num_qubits: Circuit qubits
            num_actions: Number of actions
        """
        self.n = num_qubits
        self.actions = num_actions
        self.params: List[float] = [0.0] * (num_qubits * 2)
        self._init_params()
    
    def _init_params(self):
        """Initialize parameters randomly."""
        self.params = [random.uniform(-math.pi, math.pi)
                       for _ in range(len(self.params))]
    
    def action_probabilities(self, state: int) -> List[float]:
        """
        Compute action probabilities.
        
        Args:
            state: Current state
        
        Returns:
            Probability distribution over actions
        """
        # Simulate parameterized quantum circuit output
        probs = []
        for a in range(self.actions):
            val = math.sin(self.params[a % len(self.params)] + state * 0.1)
            probs.append(max(0.0, val + 1.0))
        
        total = sum(probs)
        if total > 0:
            return [p / total for p in probs]
        return [1.0 / self.actions] * self.actions
    
    def select_action(self, state: int) -> int:
        """
        Select action via sampling.
        
        Args:
            state: Current state
        
        Returns:
            Selected action
        """
        probs = self.action_probabilities(state)
        r = random.random()
        cumsum = 0.0
        for i, p in enumerate(probs):
            cumsum += p
            if r <= cumsum:
                return i
        return self.actions - 1
    
    def update(self, gradients: List[float], lr: float = 0.01):
        """
        Update parameters.
        
        Args:
            gradients: Parameter gradients
            lr: Learning rate
        """
        for i in range(min(len(self.params), len(gradients))):
            self.params[i] -= lr * gradients[i]


class QuantumQFunction:
    """
    Quantum Q-function approximator.
    """
    
    def __init__(self, num_states: int, num_actions: int):
        """
        Args:
            num_states: Number of states
            num_actions: Number of actions
        """
        self.num_states = num_states
        self.num_actions = num_actions
        self.q_table: Dict[Tuple[int, int], float] = {}
    
    def get(self, state: int, action: int) -> float:
        """
        Get Q-value.
        
        Args:
            state: State
            action: Action
        
        Returns:
            Q-value
        """
        return self.q_table.get((state, action), 0.0)
    
    def set(self, state: int, action: int, value: float):
        """Set Q-value."""
        self.q_table[(state, action)] = value
    
    def best_action(self, state: int) -> int:
        """
        Get best action.
        
        Args:
            state: State
        
        Returns:
            Best action
        """
        q_vals = [self.get(state, a) for a in range(self.num_actions)]
        return q_vals.index(max(q_vals))
    
    def max_q(self, state: int) -> float:
        """
        Get max Q-value.
        
        Args:
            state: State
        
        Returns:
            Max Q
        """
        return max(self.get(state, a) for a in range(self.num_actions))


class QuantumPolicyGradient:
    """
    Quantum policy gradient optimizer.
    """
    
    def __init__(self, policy: QuantumPolicy,
                 learning_rate: float = 0.01):
        """
        Args:
            policy: Quantum policy
            learning_rate: Learning rate
        """
        self.policy = policy
        self.lr = learning_rate
        self.trajectory: List[Tuple[int, int, float]] = []
    
    def record(self, state: int, action: int, reward: float):
        """Record trajectory step."""
        self.trajectory.append((state, action, reward))
    
    def compute_gradients(self) -> List[float]:
        """
        Compute parameter gradients from trajectory.
        
        Returns:
            Gradients
        """
        grads = [0.0] * len(self.policy.params)
        
        for state, action, reward in self.trajectory:
            probs = self.policy.action_probabilities(state)
            # Policy gradient: d log(pi(a|s)) / d theta
            for i in range(len(grads)):
                # Simplified gradient
                grad = math.cos(self.policy.params[i] + state * 0.1)
                if action == i % self.policy.actions:
                    grads[i] += reward * grad / (probs[action] + 1e-8)
        
        return grads
    
    def update(self):
        """Update policy."""
        grads = self.compute_gradients()
        self.policy.update(grads, self.lr)
        self.trajectory = []


class QuantumQLearning:
    """
    Quantum Q-learning agent.
    """
    
    def __init__(self, num_states: int, num_actions: int,
                 alpha: float = 0.1, gamma: float = 0.9,
                 epsilon: float = 0.1):
        """
        Args:
            num_states: Number of states
            num_actions: Number of actions
            alpha: Learning rate
            gamma: Discount factor
            epsilon: Exploration rate
        """
        self.q = QuantumQFunction(num_states, num_actions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def select_action(self, state: int) -> int:
        """
        Epsilon-greedy action selection.
        
        Args:
            state: State
        
        Returns:
            Action
        """
        if random.random() < self.epsilon:
            return random.randint(0, self.q.num_actions - 1)
        return self.q.best_action(state)
    
    def update(self, state: int, action: int,
              reward: float, next_state: int):
        """
        Q-learning update.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
        """
        current_q = self.q.get(state, action)
        max_next = self.q.max_q(next_state)
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next - current_q)
        self.q.set(state, action, new_q)


class QuantumReinforcementLearning:
    """
    Unified quantum reinforcement learning controller.
    """
    
    def __init__(self):
        self.policy_grad: Optional[QuantumPolicyGradient] = None
        self.q_learning: Optional[QuantumQLearning] = None
        self.episode_rewards: List[float] = []
    
    def setup_policy_gradient(self, num_qubits: int = 4,
                              num_actions: int = 2):
        """
        Setup policy gradient.
        
        Args:
            num_qubits: Qubits
            num_actions: Actions
        """
        policy = QuantumPolicy(num_qubits, num_actions)
        self.policy_grad = QuantumPolicyGradient(policy)
    
    def setup_q_learning(self, num_states: int, num_actions: int):
        """
        Setup Q-learning.
        
        Args:
            num_states: States
            num_actions: Actions
        """
        self.q_learning = QuantumQLearning(num_states, num_actions)
    
    def run_episode(self, env_steps: int = 10) -> float:
        """
        Run a single episode.
        
        Args:
            env_steps: Number of steps
        
        Returns:
            Total reward
        """
        total_reward = 0.0
        
        if self.q_learning is not None:
            state = 0
            for _ in range(env_steps):
                action = self.q_learning.select_action(state)
                reward = random.uniform(-1.0, 1.0)
                next_state = (state + action) % self.q_learning.q.num_states
                self.q_learning.update(state, action, reward, next_state)
                total_reward += reward
                state = next_state
        
        self.episode_rewards.append(total_reward)
        return total_reward
    
    def average_reward(self, window: int = 10) -> float:
        """
        Compute average reward.
        
        Args:
            window: Window size
        
        Returns:
            Average
        """
        recent = self.episode_rewards[-window:]
        if not recent:
            return 0.0
        return sum(recent) / len(recent)
    
    def rl_summary(self) -> Dict:
        """Get RL summary."""
        return {
            "episodes": len(self.episode_rewards),
            "avg_reward": self.average_reward(),
            "best_reward": max(self.episode_rewards) if self.episode_rewards else 0.0
        }
