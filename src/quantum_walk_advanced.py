"""
Quantum Walk Advanced Module
Discrete-time quantum walk, continuous-time quantum walk,
hitting time, and spatial search for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WalkState:
    """Quantum walk state."""
    position: int
    coin_state: int
    amplitude: complex


class DiscreteTimeQuantumWalk:
    """
    Discrete-time quantum walk on line/graph.
    """
    
    def __init__(self, num_positions: int = 8):
        """
        Args:
            num_positions: Number of positions
        """
        self.N = num_positions
    
    def coin_operator(self, coin_state: int,
                     coin_type: str = "hadamard") -> List[complex]:
        """
        Apply coin operator.
        
        Args:
            coin_state: 0 or 1
            coin_type: Coin type
        
        Returns:
            New coin amplitudes
        """
        if coin_type == "hadamard":
            h = 1.0 / math.sqrt(2.0)
            if coin_state == 0:
                return [complex(h, 0), complex(h, 0)]
            else:
                return [complex(h, 0), complex(-h, 0)]
        return [complex(1.0, 0), complex(0.0, 0)]
    
    def shift_operator(self, position: int,
                      coin_state: int) -> int:
        """
        Apply shift operator.
        
        Args:
            position: Current position
            coin_state: Coin state (0=left, 1=right)
        
        Returns:
            New position
        """
        if coin_state == 0:
            return max(0, position - 1)
        return min(self.N - 1, position + 1)
    
    def step(self, state: WalkState) -> List[WalkState]:
        """
        One step of quantum walk.
        
        Args:
            state: Current state
        
        Returns:
            Resulting states
        """
        coin_amps = self.coin_operator(state.coin_state)
        results = []
        for c, amp in enumerate(coin_amps):
            new_pos = self.shift_operator(state.position, c)
            results.append(WalkState(new_pos, c, state.amplitude * amp))
        return results


class ContinuousTimeQuantumWalk:
    """
    Continuous-time quantum walk.
    """
    
    def __init__(self, num_nodes: int = 8):
        """
        Args:
            num_nodes: Number of nodes
        """
        self.N = num_nodes
    
    def adjacency_line(self) -> List[List[float]]:
        """
        Generate line graph adjacency matrix.
        
        Returns:
            Adjacency matrix
        """
        A = [[0.0] * self.N for _ in range(self.N)]
        for i in range(self.N - 1):
            A[i][i+1] = 1.0
            A[i+1][i] = 1.0
        return A
    
    def evolution_probability(self, time: float,
                             start_node: int,
                             target_node: int) -> float:
        """
        Compute transition probability (simplified approximation).
        
        Args:
            time: Evolution time
            start_node: Start node
            target_node: Target node
        
        Returns:
            Probability
        """
        # Simplified: Gaussian spreading
        dx = target_node - start_node
        sigma = time / math.sqrt(self.N)
        if sigma <= 0:
            return 1.0 if dx == 0 else 0.0
        return math.exp(-dx**2 / (2.0 * sigma**2)) / (math.sqrt(2.0 * math.pi) * sigma)


class HittingTime:
    """
    Quantum walk hitting time analysis.
    """
    
    def __init__(self):
        pass
    
    def expected_hitting_time(self, graph_size: int,
                             target_probability: float = 0.5) -> float:
        """
        Estimate hitting time (simplified).
        
        Args:
            graph_size: Graph size
            target_probability: Target probability
        
        Returns:
            Hitting time
        """
        if target_probability <= 0 or target_probability >= 1:
            return float('inf')
        # Simplified: O(sqrt(N)) for quantum walk
        return math.sqrt(graph_size) / target_probability
    
    def quantum_speedup(self, classical_hitting_time: float,
                       quantum_hitting_time: float) -> float:
        """
        Compute quantum speedup ratio.
        
        Args:
            classical_hitting_time: Classical time
            quantum_hitting_time: Quantum time
        
        Returns:
            Speedup factor
        """
        if quantum_hitting_time <= 0:
            return 0.0
        return classical_hitting_time / quantum_hitting_time


class SpatialSearch:
    """
    Quantum spatial search algorithms.
    """
    
    def __init__(self):
        pass
    
    def search_complexity(self, database_size: int) -> float:
        """
        Compute quantum spatial search complexity.
        
        Args:
            database_size: Database size
        
        Returns:
            Query complexity
        """
        if database_size <= 0:
            return 0.0
        return math.sqrt(database_size)
    
    def success_probability(self, oracle_marked: int,
                           total_elements: int,
                           iterations: int) -> float:
        """
        Compute success probability after iterations.
        
        Args:
            oracle_marked: Number of marked elements
            total_elements: Total elements
            iterations: Number of iterations
        
        Returns:
            Success probability
        """
        if total_elements <= 0:
            return 0.0
        theta = math.asin(math.sqrt(oracle_marked / total_elements))
        return math.sin((2.0 * iterations + 1.0) * theta)**2


class QuantumWalkAdvanced:
    """
    Unified quantum walk controller.
    """
    
    def __init__(self):
        self.discrete = DiscreteTimeQuantumWalk()
        self.continuous = ContinuousTimeQuantumWalk()
        self.hitting = HittingTime()
        self.search = SpatialSearch()
    
    def walk_summary(self) -> Dict:
        """Get summary."""
        return {
            "types": ["discrete_time", "continuous_time"],
            "applications": ["hitting_time", "spatial_search", "transport"]
        }
