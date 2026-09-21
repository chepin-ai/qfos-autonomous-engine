"""
Quantum Walks Advanced Module
Continuous-time quantum walks, multi-particle walks,
quantum walk search, and hitting times for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WalkState:
    """Quantum walk state."""
    position: int
    amplitude: complex


class ContinuousTimeQuantumWalk:
    """
    Continuous-time quantum walk on a graph.
    """
    
    def __init__(self, num_nodes: int = 10,
                 gamma: float = 1.0):
        """
        Args:
            num_nodes: Number of nodes
            gamma: Transition rate
        """
        self.N = num_nodes
        self.gamma = gamma
    
    def adjacency_line(self) -> List[List[float]]:
        """
        Create adjacency matrix for line graph.
        
        Returns:
            Adjacency matrix
        """
        A = [[0.0 for _ in range(self.N)] for _ in range(self.N)]
        for i in range(self.N - 1):
            A[i][i + 1] = 1.0
            A[i + 1][i] = 1.0
        return A
    
    def hamiltonian(self, adjacency: List[List[float]]) -> List[List[float]]:
        """
        Compute Hamiltonian H = -gamma * A.
        
        Args:
            adjacency: Adjacency matrix
        
        Returns:
            Hamiltonian
        """
        return [[-self.gamma * adjacency[i][j] for j in range(self.N)]
                for i in range(self.N)]
    
    def propagate(self, initial_state: List[complex],
                  time: float) -> List[complex]:
        """
        Propagate state under Hamiltonian (simplified).
        
        Args:
            initial_state: Initial state
            time: Evolution time
        
        Returns:
            Final state
        """
        # Simplified: random walk approximation
        result = [0.0j for _ in range(self.N)]
        for i in range(self.N):
            spread = int(time * self.gamma)
            for j in range(max(0, i - spread), min(self.N, i + spread + 1)):
                phase = self.gamma * time * (j - i)
                result[j] += initial_state[i] * complex(math.cos(phase), math.sin(phase)) / (spread + 1)
        
        # Normalize
        norm = sum(abs(r) ** 2 for r in result)
        if norm > 0:
            result = [r / math.sqrt(norm) for r in result]
        return result
    
    def variance(self, probabilities: List[float]) -> float:
        """
        Compute position variance.
        
        Args:
            probabilities: Position probabilities
        
        Returns:
            Variance
        """
        mean = sum(i * p for i, p in enumerate(probabilities))
        return sum(p * (i - mean) ** 2 for i, p in enumerate(probabilities))


class MultiParticleQuantumWalk:
    """
    Multi-particle quantum walk.
    """
    
    def __init__(self, num_positions: int = 5,
                 num_particles: int = 2):
        """
        Args:
            num_positions: Number of positions
            num_particles: Number of particles
        """
        self.positions = num_positions
        self.particles = num_particles
    
    def state_space_size(self) -> int:
        """
        Compute state space size.
        
        Returns:
            State space dimension
        """
        return self.positions ** self.particles
    
    def joint_probability(self, positions: List[int],
                         probabilities: List[float]) -> float:
        """
        Compute joint probability for particle positions.
        
        Args:
            positions: Particle positions
            probabilities: Single-particle probabilities
        
        Returns:
            Joint probability
        """
        prob = 1.0
        for p in positions:
            if p < len(probabilities):
                prob *= probabilities[p]
        return prob


class QuantumWalkSearch:
    """
    Quantum walk search algorithm.
    """
    
    def __init__(self, num_nodes: int = 100):
        """
        Args:
            num_nodes: Number of nodes
        """
        self.N = num_nodes
    
    def optimal_steps(self, num_marked: int = 1) -> int:
        """
        Compute optimal number of steps.
        
        Args:
            num_marked: Number of marked items
        
        Returns:
            Optimal steps
        """
        if num_marked == 0:
            return 0
        return int(round(math.pi / 2.0 * math.sqrt(self.N / num_marked)))
    
    def success_probability(self, steps: int,
                           num_marked: int = 1) -> float:
        """
        Estimate success probability.
        
        Args:
            steps: Number of steps
            num_marked: Number of marked items
        
        Returns:
            Success probability
        """
        if num_marked == 0:
            return 0.0
        theta = math.sqrt(num_marked / self.N)
        return math.sin((2.0 * steps + 1.0) * theta) ** 2


class HittingTimeAnalysis:
    """
    Hitting time analysis for quantum walks.
    """
    
    def __init__(self):
        pass
    
    def classical_hitting_time(self, graph_size: int,
                              target_degree: int = 1) -> float:
        """
        Estimate classical hitting time.
        
        Args:
            graph_size: Graph size
            target_degree: Target node degree
        
        Returns:
            Hitting time
        """
        if target_degree <= 0:
            return float('inf')
        return graph_size ** 2 / target_degree
    
    def quantum_hitting_time(self, graph_size: int) -> float:
        """
        Estimate quantum hitting time.
        
        Args:
            graph_size: Graph size
        
        Returns:
            Quantum hitting time
        """
        return math.sqrt(graph_size)


class QuantumWalksAdvanced:
    """
    Unified advanced quantum walks controller.
    """
    
    def __init__(self):
        self.ctqw = ContinuousTimeQuantumWalk()
        self.multi = MultiParticleQuantumWalk()
        self.search = QuantumWalkSearch()
        self.hitting = HittingTimeAnalysis()
    
    def walks_summary(self) -> Dict:
        """Get summary."""
        return {
            "types": ["continuous_time", "multi_particle", "search"],
            "advantages": ["quadratic_speedup", "localization", "hitting_time"]
        }
