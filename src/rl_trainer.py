"""
RL Trainer Module
Q-learning, policy gradient, and experience replay buffer
for autonomous spacecraft reinforcement learning.
"""

import random
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import deque


@dataclass
class Experience:
    """A single experience tuple."""
    state: str
    action: str
    reward: float
    next_state: str
    done: bool = False


class ReplayBuffer:
    """
    Experience replay buffer.
    """
    
    def __init__(self, capacity: int = 10000):
        """
        Args:
            capacity: Maximum buffer size
        """
        self.capacity = capacity
        self.buffer: deque = deque(maxlen=capacity)
    
    def push(self, experience: Experience):
        """Add experience to buffer."""
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch.
        
        Args:
            batch_size: Batch size
        
        Returns:
            List of experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        return random.sample(list(self.buffer), batch_size)
    
    def __len__(self) -> int:
        """Get buffer size."""
        return len(self.buffer)
    
    def is_ready(self, batch_size: int) -> bool:
        """Check if enough data for batch."""
        return len(self.buffer) >= batch_size


class QLearningAgent:
    """
    Q-learning agent with epsilon-greedy exploration.
    """
    
    def __init__(self, actions: List[str],
                 alpha: float = 0.1,
                 gamma: float = 0.95,
                 epsilon: float = 0.1,
                 seed: Optional[int] = None):
        """
        Args:
            actions: Available actions
            alpha: Learning rate
            gamma: Discount factor
            epsilon: Exploration rate
            seed: Random seed
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = random.Random(seed)
        self.q_table: Dict[Tuple[str, str], float] = {}
    
    def get_q(self, state: str, action: str) -> float:
        """Get Q-value."""
        return self.q_table.get((state, action), 0.0)
    
    def choose_action(self, state: str) -> str:
        """
        Choose action using epsilon-greedy.
        
        Args:
            state: Current state
        
        Returns:
            Selected action
        """
        if self.rng.random() < self.epsilon:
            return self.rng.choice(self.actions)
        
        # Greedy
        q_values = [(a, self.get_q(state, a)) for a in self.actions]
        best_action = max(q_values, key=lambda x: x[1])[0]
        return best_action
    
    def learn(self, state: str, action: str,
             reward: float, next_state: str, done: bool = False):
        """
        Update Q-value.
        
        Args:
            state: Current state
            action: Taken action
            reward: Received reward
            next_state: Next state
            done: Episode done
        """
        current_q = self.get_q(state, action)
        
        if done:
            target = reward
        else:
            next_q_values = [self.get_q(next_state, a) for a in self.actions]
            target = reward + self.gamma * max(next_q_values)
        
        self.q_table[(state, action)] = current_q + self.alpha * (target - current_q)
    
    def get_policy(self) -> Dict[str, str]:
        """Get greedy policy."""
        policy = {}
        states = set(s for s, _ in self.q_table)
        
        for state in states:
            q_values = [(a, self.get_q(state, a)) for a in self.actions]
            policy[state] = max(q_values, key=lambda x: x[1])[0]
        
        return policy
    
    def get_value_function(self) -> Dict[str, float]:
        """Get value function."""
        values = {}
        states = set(s for s, _ in self.q_table)
        
        for state in states:
            values[state] = max(self.get_q(state, a) for a in self.actions)
        
        return values


class PolicyGradientAgent:
    """
    Simple policy gradient agent.
    """
    
    def __init__(self, actions: List[str],
                 alpha: float = 0.01,
                 gamma: float = 0.95,
                 seed: Optional[int] = None):
        """
        Args:
            actions: Available actions
            alpha: Learning rate
            gamma: Discount factor
            seed: Random seed
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.rng = random.Random(seed)
        self.policy_params: Dict[Tuple[str, str], float] = {}
        self.trajectory: List[Tuple[str, str, float]] = []
    
    def get_preference(self, state: str, action: str) -> float:
        """Get action preference."""
        return self.policy_params.get((state, action), 0.0)
    
    def choose_action(self, state: str) -> str:
        """
        Choose action using softmax policy.
        
        Args:
            state: Current state
        
        Returns:
            Selected action
        """
        preferences = [self.get_preference(state, a) for a in self.actions]
        max_pref = max(preferences)
        exp_prefs = [pow(2.718281828459045, p - max_pref) for p in preferences]
        total = sum(exp_prefs)
        probs = [e / total for e in exp_prefs]
        
        r = self.rng.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                return self.actions[i]
        
        return self.actions[-1]
    
    def record(self, state: str, action: str, reward: float):
        """Record trajectory step."""
        self.trajectory.append((state, action, reward))
    
    def update(self):
        """Update policy using collected trajectory."""
        if not self.trajectory:
            return
        
        # Compute returns
        returns = []
        G = 0.0
        for _, _, reward in reversed(self.trajectory):
            G = reward + self.gamma * G
            returns.insert(0, G)
        
        # Normalize returns
        mean_g = sum(returns) / len(returns)
        std_g = (sum((g - mean_g) ** 2 for g in returns) / len(returns)) ** 0.5
        if std_g > 0:
            returns = [(g - mean_g) / std_g for g in returns]
        
        # Update preferences
        for i, (state, action, _) in enumerate(self.trajectory):
            G = returns[i]
            
            # Softmax gradient
            preferences = [self.get_preference(state, a) for a in self.actions]
            max_pref = max(preferences)
            exp_prefs = [pow(2.718281828459045, p - max_pref) for p in preferences]
            total = sum(exp_prefs)
            probs = [e / total for e in exp_prefs]
            
            for j, a in enumerate(self.actions):
                indicator = 1.0 if a == action else 0.0
                grad = indicator - probs[j]
                key = (state, a)
                self.policy_params[key] = self.policy_params.get(key, 0.0) + self.alpha * G * grad
        
        self.trajectory.clear()
    
    def get_policy_probs(self, state: str) -> Dict[str, float]:
        """Get action probabilities."""
        preferences = [self.get_preference(state, a) for a in self.actions]
        max_pref = max(preferences)
        exp_prefs = [pow(2.718281828459045, p - max_pref) for p in preferences]
        total = sum(exp_prefs)
        return {a: e / total for a, e in zip(self.actions, exp_prefs)}


class RLTrainer:
    """
    Unified RL training controller.
    """
    
    def __init__(self):
        self.q_agent: Optional[QLearningAgent] = None
        self.pg_agent: Optional[PolicyGradientAgent] = None
        self.replay_buffer = ReplayBuffer()
        self.episode_rewards: List[float] = []
    
    def create_q_agent(self, actions: List[str],
                      alpha: float = 0.1,
                      gamma: float = 0.95,
                      epsilon: float = 0.1) -> QLearningAgent:
        """
        Create Q-learning agent.
        
        Args:
            actions: Available actions
            alpha: Learning rate
            gamma: Discount factor
            epsilon: Exploration rate
        
        Returns:
            QLearningAgent
        """
        self.q_agent = QLearningAgent(actions, alpha, gamma, epsilon)
        return self.q_agent
    
    def create_pg_agent(self, actions: List[str],
                       alpha: float = 0.01,
                       gamma: float = 0.95) -> PolicyGradientAgent:
        """
        Create policy gradient agent.
        
        Args:
            actions: Available actions
            alpha: Learning rate
            gamma: Discount factor
        
        Returns:
            PolicyGradientAgent
        """
        self.pg_agent = PolicyGradientAgent(actions, alpha, gamma)
        return self.pg_agent
    
    def train_q_learning(self, env_step_fn: Callable[[str, str], Tuple[str, float, bool]],
                        initial_state: str,
                        episodes: int = 1000,
                        max_steps: int = 100) -> Dict[str, float]:
        """
        Train Q-learning agent.
        
        Args:
            env_step_fn: Function (state, action) -> (next_state, reward, done)
            initial_state: Starting state
            episodes: Number of episodes
            max_steps: Max steps per episode
        
        Returns:
            Value function
        """
        if self.q_agent is None:
            raise ValueError("Q-agent not created")
        
        for _ in range(episodes):
            state = initial_state
            episode_reward = 0.0
            
            for _ in range(max_steps):
                action = self.q_agent.choose_action(state)
                next_state, reward, done = env_step_fn(state, action)
                
                self.q_agent.learn(state, action, reward, next_state, done)
                self.replay_buffer.push(
                    Experience(state, action, reward, next_state, done)
                )
                
                episode_reward += reward
                state = next_state
                
                if done:
                    break
            
            self.episode_rewards.append(episode_reward)
        
        return self.q_agent.get_value_function()
    
    def train_policy_gradient(self, env_step_fn: Callable[[str, str], Tuple[str, float, bool]],
                             initial_state: str,
                             episodes: int = 1000,
                             max_steps: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Train policy gradient agent.
        
        Args:
            env_step_fn: Function (state, action) -> (next_state, reward, done)
            initial_state: Starting state
            episodes: Number of episodes
            max_steps: Max steps per episode
        
        Returns:
            Policy probabilities
        """
        if self.pg_agent is None:
            raise ValueError("PG agent not created")
        
        for _ in range(episodes):
            state = initial_state
            episode_reward = 0.0
            
            for _ in range(max_steps):
                action = self.pg_agent.choose_action(state)
                next_state, reward, done = env_step_fn(state, action)
                
                self.pg_agent.record(state, action, reward)
                
                episode_reward += reward
                state = next_state
                
                if done:
                    break
            
            self.pg_agent.update()
            self.episode_rewards.append(episode_reward)
        
        # Collect policy for all seen states
        policy = {}
        for (s, _) in self.pg_agent.policy_params:
            if s not in policy:
                policy[s] = self.pg_agent.get_policy_probs(s)
        
        return policy
    
    def get_training_stats(self) -> Dict:
        """Get training statistics."""
        if not self.episode_rewards:
            return {"episodes": 0}
        
        return {
            "episodes": len(self.episode_rewards),
            "mean_reward": sum(self.episode_rewards) / len(self.episode_rewards),
            "max_reward": max(self.episode_rewards),
            "min_reward": min(self.episode_rewards),
            "buffer_size": len(self.replay_buffer)
        }
    
    def trainer_summary(self) -> Dict:
        """Get trainer summary."""
        return {
            "q_agent": self.q_agent is not None,
            "pg_agent": self.pg_agent is not None,
            "buffer_size": len(self.replay_buffer),
            "episodes_trained": len(self.episode_rewards)
        }
