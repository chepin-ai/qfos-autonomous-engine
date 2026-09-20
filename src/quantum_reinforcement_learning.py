"""
Quantum Reinforcement Learning Module
Quantum policy gradients, variational quantum circuits for RL agents,
action selection, and environment interaction for autonomous control.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


class QuantumPolicy:
    """
    Parameterized quantum policy for RL.
    """
    
    def __init__(self, num_qubits: int = 4, num_actions: int = 2):
        """
        Args:
            num_qubits: Qubits
            num_actions: Action space size
        """
        self.n = num_qubits
        self.actions = num_actions
        self.params = [random.uniform(0, 2.0 * math.pi) for _ in range(num_qubits * 2)]
    
    def rotation_gate(self, angle: float) -> List[List[complex]]:
        """
        RX rotation matrix.
        
        Args:
            angle: Rotation angle
        
        Returns:
            Matrix
        """
        c = math.cos(angle / 2.0)
        s = math.sin(angle / 2.0)
        return [[complex(c, 0.0), complex(0.0, -s)],
                [complex(0.0, -s), complex(c, 0.0)]]
    
    def entangling_gate(self, state: List[complex],
                       qubit_i: int, qubit_j: int) -> List[complex]:
        """
        Apply CNOT-like entangling operation.
        
        Args:
            state: State
            qubit_i: Control
            qubit_j: Target
        
        Returns:
            New state
        """
        dim = len(state)
        new_state = state[:]
        
        for i in range(dim):
            if (i >> qubit_i) & 1:
                flipped = i ^ (1 << qubit_j)
                if flipped < dim:
                    new_state[i], new_state[flipped] = new_state[flipped], new_state[i]
        
        return new_state
    
    def evaluate(self, state_encoding: List[float]) -> List[float]:
        """
        Evaluate policy for state.
        
        Args:
            state_encoding: State features
        
        Returns:
            Action probabilities
        """
        dim = 2 ** self.n
        # Initialize uniform
        quantum_state = [complex(1.0 / math.sqrt(dim), 0.0)] * dim
        
        # Encode state into rotation angles
        for i in range(min(len(state_encoding), self.n)):
            angle = state_encoding[i] * math.pi
            # Apply rotation
            for j in range(dim):
                if (j >> i) & 1:
                    quantum_state[j] *= complex(math.cos(angle), math.sin(angle))
        
        # Apply parameterized gates
        for i in range(self.n):
            if i < len(self.params):
                angle = self.params[i]
                for j in range(dim):
                    if (j >> i) & 1:
                        quantum_state[j] *= complex(math.cos(angle), math.sin(angle))
        
        # Measure: compute probabilities for each action
        probs = []
        for a in range(self.actions):
            # Map action to subset of basis states
            prob = 0.0
            for j in range(dim):
                if j % self.actions == a:
                    prob += abs(quantum_state[j]) ** 2
            probs.append(max(0.0, prob))
        
        # Normalize
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        else:
            probs = [1.0 / self.actions] * self.actions
        
        return probs
    
    def select_action(self, state_encoding: List[float]) -> int:
        """
        Select action from policy.
        
        Args:
            state_encoding: State
        
        Returns:
            Action
        """
        probs = self.evaluate(state_encoding)
        r = random.random()
        cumsum = 0.0
        for i, p in enumerate(probs):
            cumsum += p
            if r <= cumsum:
                return i
        return len(probs) - 1


class QuantumPolicyGradient:
    """
    Policy gradient optimization for quantum RL.
    """
    
    def __init__(self, policy: QuantumPolicy, lr: float = 0.1):
        """
        Args:
            policy: Quantum policy
            lr: Learning rate
        """
        self.policy = policy
        self.lr = lr
        self.rewards: List[float] = []
        self.log_probs: List[float] = []
    
    def store_transition(self, log_prob: float, reward: float):
        """
        Store transition.
        
        Args:
            log_prob: Log probability
            reward: Reward
        """
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
    
    def compute_returns(self, gamma: float = 0.99) -> List[float]:
        """
        Compute discounted returns.
        
        Args:
            gamma: Discount factor
        
        Returns:
            Returns
        """
        returns = []
        R = 0.0
        for r in reversed(self.rewards):
            R = r + gamma * R
            returns.insert(0, R)
        
        # Normalize
        if returns:
            mean = sum(returns) / len(returns)
            std = (sum((r - mean)**2 for r in returns) / len(returns)) ** 0.5
            if std > 1e-10:
                returns = [(r - mean) / std for r in returns]
        
        return returns
    
    def update(self, gamma: float = 0.99):
        """
        Update policy parameters.
        
        Args:
            gamma: Discount factor
        """
        returns = self.compute_returns(gamma)
        
        # Gradient ascent on policy parameters
        for i in range(len(self.policy.params)):
            grad = 0.0
            for log_prob, ret in zip(self.log_probs, returns):
                # Simplified gradient: d(log_prob)/d(param) ~ log_prob
                grad += log_prob * ret
            
            self.policy.params[i] += self.lr * grad / max(len(self.log_probs), 1)
        
        # Clear buffers
        self.rewards = []
        self.log_probs = []


class QuantumRLAgent:
    """
    Quantum RL agent for environment interaction.
    """
    
    def __init__(self, state_dim: int = 2, num_actions: int = 2):
        """
        Args:
            state_dim: State dimension
            num_actions: Actions
        """
        self.state_dim = state_dim
        self.policy = QuantumPolicy(state_dim, num_actions)
        self.optimizer = QuantumPolicyGradient(self.policy)
        self.episode_rewards: List[float] = []
    
    def act(self, state: List[float]) -> int:
        """
        Select action.
        
        Args:
            state: State
        
        Returns:
            Action
        """
        return self.policy.select_action(state)
    
    def step(self, state: List[float], action: int, reward: float):
        """
        Record step.
        
        Args:
            state: State
            action: Action
            reward: Reward
        """
        probs = self.policy.evaluate(state)
        log_prob = math.log(max(probs[action], 1e-10))
        self.optimizer.store_transition(log_prob, reward)
    
    def finish_episode(self):
        """Finish episode and update."""
        total_reward = sum(self.optimizer.rewards)
        self.episode_rewards.append(total_reward)
        self.optimizer.update()
    
    def mean_reward(self, window: int = 10) -> float:
        """
        Mean recent reward.
        
        Args:
            window: Window
        
        Returns:
            Mean
        """
        recent = self.episode_rewards[-window:]
        return sum(recent) / len(recent) if recent else 0.0


class QuantumReinforcementLearning:
    """
    Unified quantum reinforcement learning controller.
    """
    
    def __init__(self):
        self.agent: Optional[QuantumRLAgent] = None
        self.results: List[Dict] = []
    
    def build_agent(self, state_dim: int = 2, num_actions: int = 2):
        """
        Build agent.
        
        Args:
            state_dim: State dimension
            num_actions: Actions
        """
        self.agent = QuantumRLAgent(state_dim, num_actions)
    
    def train(self, environment: Callable[[int], Tuple[List[float], float]],
             episodes: int = 100) -> Dict:
        """
        Train agent.
        
        Args:
            environment: Environment function (action -> state, reward)
            episodes: Episodes
        
        Returns:
            Result
        """
        if self.agent is None:
            self.build_agent()
        
        for _ in range(episodes):
            state = [0.0] * self.agent.state_dim
            done = False
            steps = 0
            max_steps = 50
            
            while not done and steps < max_steps:
                action = self.agent.act(state)
                next_state, reward = environment(action)
                self.agent.step(state, action, reward)
                state = next_state
                steps += 1
                
                if reward > 10.0:
                    done = True
            
            self.agent.finish_episode()
        
        result = {
            "episodes": episodes,
            "mean_reward": self.agent.mean_reward(),
            "final_params": self.agent.policy.params[:5]
        }
        self.results.append(result)
        return result
    
    def qrl_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.results),
            "best_mean_reward": max((r["mean_reward"] for r in self.results), default=0.0)
        }
