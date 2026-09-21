"""
Quantum Amplitude Amplification Module
Grover's algorithm, amplitude amplification, oracle construction,
diffusion operator, and search probability for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Search result."""
    target_index: int
    probability: float
    iterations: int


class OracleConstructor:
    """
    Construct quantum oracles.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
    
    def create_oracle(self, marked_indices: List[int]) -> List[List[float]]:
        """
        Create phase oracle.
        
        Args:
            marked_indices: Marked state indices
        
        Returns:
            Oracle matrix
        """
        oracle = [[1.0 if i == j else 0.0 for j in range(self.dim)]
                  for i in range(self.dim)]
        
        for idx in marked_indices:
            if 0 <= idx < self.dim:
                oracle[idx][idx] = -1.0
        
        return oracle
    
    def apply_oracle(self, state: List[complex],
                    marked_indices: List[int]) -> List[complex]:
        """
        Apply oracle to state.
        
        Args:
            state: State vector
            marked_indices: Marked indices
        
        Returns:
            New state
        """
        new_state = state[:]
        for idx in marked_indices:
            if 0 <= idx < len(new_state):
                new_state[idx] = -new_state[idx]
        return new_state


class DiffusionOperator:
    """
    Grover diffusion operator.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
    
    def create_diffusion(self) -> List[List[float]]:
        """
        Create diffusion matrix.
        
        Returns:
            Diffusion matrix
        """
        # D = 2|s><s| - I
        s = 1.0 / math.sqrt(self.dim)
        diffusion = [[0.0] * self.dim for _ in range(self.dim)]
        
        for i in range(self.dim):
            for j in range(self.dim):
                diffusion[i][j] = 2.0 * s * s
                if i == j:
                    diffusion[i][j] -= 1.0
        
        return diffusion
    
    def apply_diffusion(self, state: List[complex]) -> List[complex]:
        """
        Apply diffusion to state.
        
        Args:
            state: State vector
        
        Returns:
            New state
        """
        # Simplified: reflect about average
        avg = sum(state) / len(state)
        new_state = [2.0 * avg - s for s in state]
        return new_state


class GroverSearch:
    """
    Grover's search algorithm.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
        self.oracle = OracleConstructor(num_qubits)
        self.diffusion = DiffusionOperator(num_qubits)
    
    def optimal_iterations(self, num_marked: int) -> int:
        """
        Compute optimal number of iterations.
        
        Args:
            num_marked: Number of marked items
        
        Returns:
            Optimal iterations
        """
        if num_marked <= 0 or num_marked >= self.dim:
            return 0
        theta = math.asin(math.sqrt(num_marked / self.dim))
        return int(round(math.pi / (4.0 * theta)))
    
    def search(self, marked_indices: List[int],
              iterations: Optional[int] = None) -> SearchResult:
        """
        Perform Grover search.
        
        Args:
            marked_indices: Marked indices
            iterations: Number of iterations
        
        Returns:
            Search result
        """
        # Initialize uniform superposition
        state = [1.0 / math.sqrt(self.dim)] * self.dim
        
        if iterations is None:
            iterations = self.optimal_iterations(len(marked_indices))
        
        for _ in range(iterations):
            state = self.oracle.apply_oracle(state, marked_indices)
            state = self.diffusion.apply_diffusion(state)
        
        # Find most probable marked state
        probabilities = [abs(x) ** 2 for x in state]
        max_idx = max(range(self.dim), key=lambda i: probabilities[i])
        
        return SearchResult(
            target_index=max_idx,
            probability=probabilities[max_idx],
            iterations=iterations
        )
    
    def success_probability(self, num_marked: int,
                           iterations: int) -> float:
        """
        Compute success probability.
        
        Args:
            num_marked: Number of marked items
            iterations: Iterations
        
        Returns:
            Probability
        """
        if num_marked <= 0:
            return 0.0
        theta = math.asin(math.sqrt(num_marked / self.dim))
        return math.sin((2.0 * iterations + 1.0) * theta) ** 2


class AmplitudeAmplification:
    """
    General amplitude amplification.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
    
    def amplify(self, state: List[complex],
               marked_indices: List[int],
               iterations: int = 1) -> List[complex]:
        """
        Amplify amplitudes of marked states.
        
        Args:
            state: Initial state
            marked_indices: Marked indices
            iterations: Iterations
        
        Returns:
            Amplified state
        """
        oracle = OracleConstructor(self.n)
        diffusion = DiffusionOperator(self.n)
        
        current = state[:]
        for _ in range(iterations):
            current = oracle.apply_oracle(current, marked_indices)
            current = diffusion.apply_diffusion(current)
        
        return current


class QuantumAmplitudeAmplification:
    """
    Unified quantum amplitude amplification controller.
    """
    
    def __init__(self, num_qubits: int = 3):
        self.n = num_qubits
        self.grover = GroverSearch(num_qubits)
        self.amplification = AmplitudeAmplification(num_qubits)
    
    def search(self, marked_indices: List[int]) -> SearchResult:
        """
        Search for marked items.
        
        Args:
            marked_indices: Marked indices
        
        Returns:
            Result
        """
        return self.grover.search(marked_indices)
    
    def qaa_summary(self) -> Dict:
        """Get summary."""
        return {
            "qubits": self.n,
            "search_space": self.grover.dim,
            "methods": ["grover_search", "amplitude_amplification", "oracle"],
            "speedup": f"O(sqrt(N)) vs O(N)"
        }
