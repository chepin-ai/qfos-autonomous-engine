"""
Quantum Oracle Module
Boolean function oracles, phase oracles,
Grover oracle construction, and quantum query complexity for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class OracleResult:
    """Oracle evaluation result."""
    input_state: int
    output: int
    phase: float


class BooleanOracle:
    """
    Boolean function oracle.
    """
    
    def __init__(self, func: Callable[[int], int],
                 num_qubits: int = 3):
        """
        Args:
            func: Boolean function f(x) -> 0 or 1
            num_qubits: Number of input qubits
        """
        self.func = func
        self.n = num_qubits
    
    def evaluate(self, x: int) -> int:
        """
        Evaluate oracle on input x.
        
        Args:
            x: Input integer
        
        Returns:
            f(x)
        """
        return self.func(x)
    
    def truth_table(self) -> Dict[int, int]:
        """
        Generate truth table.
        
        Returns:
            Truth table dictionary
        """
        return {x: self.func(x) for x in range(2 ** self.n)}
    
    def is_constant(self) -> bool:
        """
        Check if function is constant.
        
        Returns:
            Whether constant
        """
        outputs = [self.func(x) for x in range(2 ** self.n)]
        return all(o == outputs[0] for o in outputs)
    
    def is_balanced(self) -> bool:
        """
        Check if function is balanced.
        
        Returns:
            Whether balanced
        """
        outputs = [self.func(x) for x in range(2 ** self.n)]
        return sum(outputs) == len(outputs) // 2


class PhaseOracle:
    """
    Phase oracle (marks solutions with phase flip).
    """
    
    def __init__(self, marked_states: List[int]):
        """
        Args:
            marked_states: States to mark
        """
        self.marked = set(marked_states)
    
    def apply_phase(self, x: int) -> float:
        """
        Apply phase to state x.
        
        Args:
            x: State
        
        Returns:
            Phase factor (+1 or -1)
        """
        return -1.0 if x in self.marked else 1.0
    
    def num_marked(self, total_states: int) -> int:
        """
        Count marked states.
        
        Args:
            total_states: Total number of states
        
        Returns:
            Number of marked states
        """
        return len([x for x in range(total_states) if x in self.marked])
    
    def optimal_iterations(self, total_states: int) -> int:
        """
        Compute optimal Grover iterations.
        
        Args:
            total_states: Total states
        
        Returns:
            Optimal iterations
        """
        M = self.num_marked(total_states)
        N = total_states
        if M == 0 or N == 0:
            return 0
        theta = math.asin(math.sqrt(M / N))
        if theta == 0:
            return 0
        return int(round(math.pi / (4.0 * theta)))


class GroverOracle:
    """
    Grover search oracle.
    """
    
    def __init__(self, marked_states: List[int]):
        """
        Args:
            marked_states: Target states
        """
        self.phase_oracle = PhaseOracle(marked_states)
    
    def diffusion_operator(self, state: List[float]) -> List[float]:
        """
        Apply diffusion (inversion about average).
        
        Args:
            state: Quantum state amplitudes
        
        Returns:
            Diffused state
        """
        n = len(state)
        avg = sum(state) / n
        return [2.0 * avg - s for s in state]
    
    def grover_iteration(self, state: List[float]) -> List[float]:
        """
        One Grover iteration.
        
        Args:
            state: Current state
        
        Returns:
            State after one iteration
        """
        # Phase oracle
        marked = list(self.phase_oracle.marked)
        for m in marked:
            if m < len(state):
                state[m] = -state[m]
        
        # Diffusion
        return self.diffusion_operator(state)


class QuantumQueryComplexity:
    """
    Quantum query complexity analysis.
    """
    
    def __init__(self):
        pass
    
    def deutsch_jozsa_queries(self, num_qubits: int) -> int:
        """
        Query complexity for Deutsch-Jozsa.
        
        Args:
            num_qubits: Number of qubits
        
        Returns:
            Queries (always 1)
        """
        return 1
    
    def grover_queries(self, N: int,
                      M: int = 1) -> float:
        """
        Query complexity for Grover search.
        
        Args:
            N: Search space
            M: Number of solutions
        
        Returns:
            Queries
        """
        if M == 0 or N == 0:
            return 0.0
        return math.sqrt(N / M) * math.pi / 4.0
    
    def simon_queries(self, num_qubits: int) -> int:
        """
        Query complexity for Simon's algorithm.
        
        Args:
            num_qubits: Number of qubits
        
        Returns:
            Linear in n (vs exponential classically)
        """
        return num_qubits


class QuantumOracle:
    """
    Unified quantum oracle controller.
    """
    
    def __init__(self):
        self.phase = PhaseOracle([])
        self.grover = GroverOracle([])
        self.complexity = QuantumQueryComplexity()
    
    def oracle_summary(self) -> Dict:
        """Get summary."""
        return {
            "types": ["boolean", "phase", "grover"],
            "algorithms": ["Deutsch-Jozsa", "Grover", "Simon"],
            "speedups": ["exponential", "quadratic", "exponential"]
        }
