"""
Quantum Walks Module
Classical random walk, discrete quantum walk, continuous quantum walk,
and quantum walk search for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WalkPosition:
    """Position on a walk."""
    x: int
    probability: float


class ClassicalRandomWalk:
    """
    Classical random walk.
    """
    
    def __init__(self, num_steps: int = 10):
        """
        Args:
            num_steps: Number of steps
        """
        self.steps = num_steps
        self.position = 0
        self.history: List[int] = [0]
    
    def step(self) -> int:
        """
        Take one random step.
        
        Returns:
            New position
        """
        self.position += random.choice([-1, 1])
        self.history.append(self.position)
        return self.position
    
    def walk(self) -> List[int]:
        """
        Perform full walk.
        
        Returns:
            Position history
        """
        for _ in range(self.steps):
            self.step()
        return self.history
    
    def variance(self) -> float:
        """
        Compute position variance.
        
        Returns:
            Variance
        """
        if not self.history:
            return 0.0
        mean = sum(self.history) / len(self.history)
        return sum((x - mean) ** 2 for x in self.history) / len(self.history)
    
    def mean_displacement(self) -> float:
        """
        Compute mean displacement.
        
        Returns:
            Mean displacement
        """
        if not self.history:
            return 0.0
        return sum(self.history) / len(self.history)


class DiscreteQuantumWalk:
    """
    Discrete-time quantum walk.
    """
    
    def __init__(self, num_positions: int = 8):
        """
        Args:
            num_positions: Number of positions
        """
        self.num_positions = num_positions
        self.position_state = [0.0] * num_positions
        self.coin_state = [1.0 / math.sqrt(2), 1.0 / math.sqrt(2)]
        self.position_state[num_positions // 2] = 1.0  # Start at center
    
    def coin_operator(self, state: List[float]) -> List[float]:
        """
        Apply Hadamard coin.
        
        Args:
            state: Coin state
        
        Returns:
            New coin state
        """
        h = 1.0 / math.sqrt(2)
        return [
            h * (state[0] + state[1]),
            h * (state[0] - state[1])
        ]
    
    def shift_operator(self, position_state: List[float],
                      coin_state: List[float]) -> List[float]:
        """
        Apply shift operator.
        
        Args:
            position_state: Position state
            coin_state: Coin state
        
        Returns:
            New position state
        """
        new_state = [0.0] * self.num_positions
        
        for i in range(self.num_positions):
            if coin_state[0] != 0:
                new_pos = (i + 1) % self.num_positions
                new_state[new_pos] += position_state[i] * coin_state[0]
            if coin_state[1] != 0:
                new_pos = (i - 1) % self.num_positions
                new_state[new_pos] += position_state[i] * coin_state[1]
        
        return new_state
    
    def step(self):
        """Take one quantum step."""
        self.coin_state = self.coin_operator(self.coin_state)
        self.position_state = self.shift_operator(self.position_state, self.coin_state)
    
    def walk(self, steps: int) -> List[float]:
        """
        Perform quantum walk.
        
        Args:
            steps: Number of steps
        
        Returns:
            Position probabilities
        """
        for _ in range(steps):
            self.step()
        
        return [abs(x) ** 2 for x in self.position_state]
    
    def variance(self) -> float:
        """
        Compute position variance.
        
        Returns:
            Variance
        """
        probs = [abs(x) ** 2 for x in self.position_state]
        mean = sum(i * p for i, p in enumerate(probs))
        return sum((i - mean) ** 2 * p for i, p in enumerate(probs))


class ContinuousQuantumWalk:
    """
    Continuous-time quantum walk.
    """
    
    def __init__(self, num_nodes: int = 8):
        """
        Args:
            num_nodes: Number of nodes
        """
        self.num_nodes = num_nodes
        self.state = [0.0] * num_nodes
        self.state[num_nodes // 2] = 1.0  # Start at center
    
    def adjacency_matrix(self) -> List[List[float]]:
        """
        Create line graph adjacency matrix.
        
        Returns:
            Adjacency matrix
        """
        A = [[0.0] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes - 1):
            A[i][i + 1] = 1.0
            A[i + 1][i] = 1.0
        return A
    
    def laplacian(self) -> List[List[float]]:
        """
        Create graph Laplacian.
        
        Returns:
            Laplacian matrix
        """
        A = self.adjacency_matrix()
        L = [[0.0] * self.num_nodes for _ in range(self.num_nodes)]
        
        for i in range(self.num_nodes):
            degree = sum(A[i])
            for j in range(self.num_nodes):
                L[i][j] = degree if i == j else -A[i][j]
        
        return L
    
    def evolve(self, time: float) -> List[float]:
        """
        Evolve state for time t.
        
        Args:
            time: Evolution time
        
        Returns:
            Probabilities
        """
        # Simplified: random walk-like diffusion
        # U = exp(-i * H * t)
        # For simplicity, approximate with discrete steps
        probs = [abs(x) ** 2 for x in self.state]
        
        # Simple diffusion approximation
        new_probs = probs[:]
        for _ in range(int(time * 10)):
            temp = new_probs[:]
            for i in range(1, self.num_nodes - 1):
                new_probs[i] = temp[i] + 0.1 * (temp[i - 1] + temp[i + 1] - 2 * temp[i])
        
        return new_probs


class QuantumWalkSearch:
    """
    Search using quantum walks.
    """
    
    def __init__(self, num_positions: int = 8):
        """
        Args:
            num_positions: Number of positions
        """
        self.num_positions = num_positions
        self.walk = DiscreteQuantumWalk(num_positions)
    
    def search(self, marked_positions: List[int],
              steps: int = 5) -> Tuple[int, float]:
        """
        Search for marked positions.
        
        Args:
            marked_positions: Marked positions
            steps: Number of steps
        
        Returns:
            (best_position, probability)
        """
        for _ in range(steps):
            self.walk.step()
        
        probs = [abs(x) ** 2 for x in self.walk.position_state]
        
        # Boost marked positions (oracle-like effect)
        for pos in marked_positions:
            if 0 <= pos < self.num_positions:
                probs[pos] *= 2.0
        
        # Normalize
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        
        best = max(range(self.num_positions), key=lambda i: probs[i])
        return (best, probs[best])


class QuantumWalks:
    """
    Unified quantum walks controller.
    """
    
    def __init__(self, num_positions: int = 8):
        self.classical = ClassicalRandomWalk()
        self.discrete = DiscreteQuantumWalk(num_positions)
        self.continuous = ContinuousQuantumWalk(num_positions)
        self.search = QuantumWalkSearch(num_positions)
    
    def compare_variances(self, steps: int) -> Dict:
        """
        Compare classical vs quantum walk variances.
        
        Args:
            steps: Number of steps
        
        Returns:
            Comparison
        """
        # Classical
        self.classical = ClassicalRandomWalk(steps)
        self.classical.walk()
        classical_var = self.classical.variance()
        
        # Quantum
        self.discrete = DiscreteQuantumWalk(self.discrete.num_positions)
        self.discrete.walk(steps)
        quantum_var = self.discrete.variance()
        
        return {
            "classical_variance": classical_var,
            "quantum_variance": quantum_var,
            "speedup": quantum_var / classical_var if classical_var > 0 else 0.0
        }
    
    def qw_summary(self) -> Dict:
        """Get summary."""
        return {
            "types": ["classical", "discrete", "continuous"],
            "positions": self.discrete.num_positions,
            "methods": ["coin_operator", "shift_operator", "evolution", "search"]
        }
