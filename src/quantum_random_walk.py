"""
Quantum Random Walk Module
Discrete-time quantum walk on a line and graph,
with coin operations and position evolution.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class CoinOperator:
    """
    Quantum coin operator for random walks.
    """
    
    def __init__(self, coin_type: str = "hadamard"):
        """
        Args:
            coin_type: "hadamard" or "grover" or "fourier"
        """
        self.type = coin_type
    
    def hadamard(self) -> List[List[complex]]:
        """Hadamard coin."""
        s = 1.0 / math.sqrt(2.0)
        return [[complex(s, 0.0), complex(s, 0.0)],
                [complex(s, 0.0), complex(-s, 0.0)]]
    
    def apply(self, state: List[complex]) -> List[complex]:
        """
        Apply coin to state.
        
        Args:
            state: 2D coin state
        
        Returns:
            New state
        """
        coin = self.hadamard()
        return [sum(coin[i][j] * state[j] for j in range(2)) for i in range(2)]


class ShiftOperator:
    """
    Shift operator for quantum walk.
    """
    
    def __init__(self, num_positions: int = 101):
        """
        Args:
            num_positions: Number of positions
        """
        self.n = num_positions
        self.center = num_positions // 2
    
    def step(self, position_probs: List[float],
            coin_state: List[complex]) -> List[float]:
        """
        Apply one quantum walk step.
        
        Args:
            position_probs: Current position distribution
            coin_state: Coin state
        
        Returns:
            New position distribution
        """
        new_probs = [0.0] * self.n
        
        for pos in range(1, self.n - 1):
            # Right shift (coin |0>)
            amp_r = position_probs[pos] * abs(coin_state[0]) ** 2
            new_probs[pos + 1] += amp_r
            
            # Left shift (coin |1>)
            amp_l = position_probs[pos] * abs(coin_state[1]) ** 2
            new_probs[pos - 1] += amp_l
        
        # Normalize
        total = sum(new_probs)
        if total > 0:
            new_probs = [p / total for p in new_probs]
        
        return new_probs


class QuantumWalkLine:
    """
    Quantum walk on a 1D line.
    """
    
    def __init__(self, num_positions: int = 101):
        """
        Args:
            num_positions: Number of positions
        """
        self.n = num_positions
        self.center = num_positions // 2
        self.coin = CoinOperator()
        self.shift = ShiftOperator(num_positions)
        self.position_probs = [0.0] * num_positions
        self.position_probs[self.center] = 1.0
        self.coin_state = [complex(1.0 / math.sqrt(2.0), 0.0),
                          complex(1.0 / math.sqrt(2.0), 0.0)]
        self.history: List[List[float]] = []
    
    def walk(self, steps: int = 50) -> List[float]:
        """
        Run quantum walk.
        
        Args:
            steps: Steps
        
        Returns:
            Final distribution
        """
        for _ in range(steps):
            # Coin flip
            self.coin_state = self.coin.apply(self.coin_state)
            
            # Shift
            self.position_probs = self.shift.step(self.position_probs, self.coin_state)
            
            # Record
            self.history.append(self.position_probs[:])
        
        return self.position_probs
    
    def mean_position(self) -> float:
        """
        Compute mean position.
        
        Returns:
            Mean
        """
        return sum((i - self.center) * p for i, p in enumerate(self.position_probs))
    
    def variance(self) -> float:
        """
        Compute position variance.
        
        Returns:
            Variance
        """
        mean = self.mean_position()
        return sum(((i - self.center) - mean) ** 2 * p
                   for i, p in enumerate(self.position_probs))
    
    def spread(self) -> float:
        """
        Compute standard deviation.
        
        Returns:
            Spread
        """
        return math.sqrt(self.variance())


class QuantumWalkGraph:
    """
    Quantum walk on a graph.
    """
    
    def __init__(self, num_nodes: int = 10):
        """
        Args:
            num_nodes: Number of nodes
        """
        self.n = num_nodes
        self.adjacency: List[List[int]] = [[] for _ in range(num_nodes)]
        self.node_probs = [0.0] * num_nodes
        self.node_probs[0] = 1.0
    
    def add_edge(self, u: int, v: int):
        """
        Add undirected edge.
        
        Args:
            u: Node u
            v: Node v
        """
        if v not in self.adjacency[u]:
            self.adjacency[u].append(v)
        if u not in self.adjacency[v]:
            self.adjacency[v].append(u)
    
    def degree(self, node: int) -> int:
        """
        Get node degree.
        
        Args:
            node: Node
        
        Returns:
            Degree
        """
        return len(self.adjacency[node])
    
    def step(self):
        """
        Apply one quantum walk step on graph.
        """
        new_probs = [0.0] * self.n
        
        for node in range(self.n):
            if self.node_probs[node] == 0:
                continue
            
            neighbors = self.adjacency[node]
            if not neighbors:
                new_probs[node] += self.node_probs[node]
                continue
            
            # Grover coin: equal superposition to neighbors
            amp = self.node_probs[node] / len(neighbors)
            for neighbor in neighbors:
                new_probs[neighbor] += amp
        
        self.node_probs = new_probs
    
    def walk(self, steps: int = 10) -> List[float]:
        """
        Run quantum walk on graph.
        
        Args:
            steps: Steps
        
        Returns:
            Final distribution
        """
        for _ in range(steps):
            self.step()
        return self.node_probs


class QuantumRandomWalk:
    """
    Unified quantum random walk controller.
    """
    
    def __init__(self):
        self.line_walk: Optional[QuantumWalkLine] = None
        self.graph_walk: Optional[QuantumWalkGraph] = None
        self.results: List[Dict] = []
    
    def line(self, num_positions: int = 101):
        """
        Setup line walk.
        
        Args:
            num_positions: Positions
        """
        self.line_walk = QuantumWalkLine(num_positions)
    
    def graph(self, num_nodes: int = 10):
        """
        Setup graph walk.
        
        Args:
            num_nodes: Nodes
        """
        self.graph_walk = QuantumWalkGraph(num_nodes)
    
    def run_line(self, steps: int = 50) -> Dict:
        """
        Run line walk.
        
        Args:
            steps: Steps
        
        Returns:
            Result
        """
        if self.line_walk is None:
            self.line(101)
        
        dist = self.line_walk.walk(steps)
        
        result = {
            "type": "line",
            "steps": steps,
            "mean_position": self.line_walk.mean_position(),
            "spread": self.line_walk.spread(),
            "final_distribution": dist
        }
        self.results.append(result)
        return result
    
    def run_graph(self, steps: int = 10) -> Dict:
        """
        Run graph walk.
        
        Args:
            steps: Steps
        
        Returns:
            Result
        """
        if self.graph_walk is None:
            self.graph(10)
        
        dist = self.graph_walk.walk(steps)
        
        result = {
            "type": "graph",
            "steps": steps,
            "final_distribution": dist
        }
        self.results.append(result)
        return result
    
    def walk_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.results),
            "line_runs": sum(1 for r in self.results if r.get("type") == "line"),
            "graph_runs": sum(1 for r in self.results if r.get("type") == "graph")
        }
