"""
Quantum Deutsch-Jozsa Module
Oracle construction, Deutsch-Jozsa algorithm,
and function property determination for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class FunctionType(Enum):
    """Types of boolean functions."""
    CONSTANT = "constant"
    BALANCED = "balanced"


class QuantumOracle:
    """
    Quantum oracle for Deutsch-Jozsa algorithm.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of input qubits
        """
        self.n = num_qubits
        self.function: Optional[Callable[[int], int]] = None
    
    def set_constant(self, value: int = 0):
        """
        Set constant function f(x) = value.
        
        Args:
            value: 0 or 1
        """
        self.function = lambda x: value & 1
    
    def set_balanced(self, mask: int = 1):
        """
        Set balanced function f(x) = parity(x & mask).
        
        Args:
            mask: Bit mask
        """
        self.function = lambda x: bin(x & mask).count("1") & 1
    
    def evaluate(self, x: int) -> int:
        """
        Evaluate oracle function.
        
        Args:
            x: Input integer
        
        Returns:
            f(x) (0 or 1)
        """
        if self.function is None:
            return 0
        return self.function(x) & 1
    
    def apply(self, state: List[complex]) -> List[complex]:
        """
        Apply oracle to quantum state.
        
        Args:
            state: Input statevector
        
        Returns:
            Output statevector
        """
        dim = 2**self.n
        new_state = list(state)
        
        for i in range(len(state)):
            # Last qubit is ancilla
            x = i & (dim - 1)
            ancilla = (i >> self.n) & 1
            
            if self.function and self.function(x) == 1:
                # Flip ancilla phase
                new_state[i] = -state[i]
        
        return new_state
    
    def check_type(self) -> FunctionType:
        """
        Determine function type classically.
        
        Returns:
            CONSTANT or BALANCED
        """
        if self.function is None:
            return FunctionType.CONSTANT
        
        outputs = [self.function(x) for x in range(2**self.n)]
        ones = sum(outputs)
        
        if ones == 0 or ones == len(outputs):
            return FunctionType.CONSTANT
        return FunctionType.BALANCED


class HadamardTransform:
    """
    Hadamard gate operations.
    """
    
    @staticmethod
    def apply(state: List[complex], num_qubits: int) -> List[complex]:
        """
        Apply H tensor power n to state.
        
        Args:
            state: Input state
            num_qubits: Number of qubits
        
        Returns:
            Transformed state
        """
        dim = 2**num_qubits
        new_state = [0.0j] * dim
        
        for i in range(dim):
            for j in range(dim):
                sign = 1.0
                for k in range(num_qubits):
                    ik = (i >> k) & 1
                    jk = (j >> k) & 1
                    if ik == 1 and jk == 1:
                        sign *= -1.0
                new_state[i] += state[j] * sign / math.sqrt(dim)
        
        return new_state
    
    @staticmethod
    def single(state: List[complex], qubit: int) -> List[complex]:
        """
        Apply H to single qubit.
        
        Args:
            state: Statevector
            qubit: Target qubit
        
        Returns:
            Transformed state
        """
        new_state = list(state)
        dim = len(state)
        
        for i in range(dim):
            if (i >> qubit) & 1 == 0:
                j = i | (1 << qubit)
                a = state[i]
                b = state[j]
                new_state[i] = (a + b) / math.sqrt(2.0)
                new_state[j] = (a - b) / math.sqrt(2.0)
        
        return new_state


class DeutschJozsa:
    """
    Deutsch-Jozsa algorithm.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of input qubits
        """
        self.n = num_qubits
        self.oracle = QuantumOracle(num_qubits)
        self.result: Optional[FunctionType] = None
    
    def run(self, oracle_func: Optional[Callable[[int], int]] = None) -> FunctionType:
        """
        Run Deutsch-Jozsa algorithm.
        
        Args:
            oracle_func: Oracle function
        
        Returns:
            Determined function type
        """
        if oracle_func:
            self.oracle.function = oracle_func
        
        # Initialize |0...0>|1>
        dim = 2**(self.n + 1)
        state = [0.0j] * dim
        state[1 << self.n] = 1.0  # |0...0>|1>
        
        # Apply H to all qubits
        for q in range(self.n + 1):
            state = HadamardTransform.single(state, q)
        
        # Apply oracle
        state = self.oracle.apply(state)
        
        # Apply H to input qubits
        for q in range(self.n):
            state = HadamardTransform.single(state, q)
        
        # Measure input qubits
        # If all zeros -> constant, else balanced
        prob_zero = 0.0
        for i in range(0, dim, 2):
            if (i >> self.n) == 0:  # ancilla = 0
                prob_zero += abs(state[i])**2
        
        # Check if |0...0> has high probability (sum over ancilla states)
        prob_all_zero = sum(abs(state[i])**2 for i in range(0, len(state), 2**self.n))
        
        if prob_all_zero > 0.5:
            self.result = FunctionType.CONSTANT
        else:
            self.result = FunctionType.BALANCED
        
        return self.result
    
    def verify(self) -> bool:
        """
        Verify result against classical check.
        
        Returns:
            True if correct
        """
        if self.result is None:
            return False
        
        classical = self.oracle.check_type()
        return self.result == classical


class QuantumDeutschJozsa:
    """
    Unified Deutsch-Jozsa controller.
    """
    
    def __init__(self):
        self.dj: Optional[DeutschJozsa] = None
        self.history: List[Dict] = []
    
    def setup(self, num_qubits: int):
        """
        Setup DJ algorithm.
        
        Args:
            num_qubits: Number of input qubits
        """
        self.dj = DeutschJozsa(num_qubits)
    
    def solve(self, oracle_func: Callable[[int], int]) -> Dict:
        """
        Solve DJ problem.
        
        Args:
            oracle_func: Oracle function
        
        Returns:
            Results
        """
        if self.dj is None:
            return {"status": "not_setup"}
        
        result = self.dj.run(oracle_func)
        verified = self.dj.verify()
        
        entry = {
            "n_qubits": self.dj.n,
            "result": result.value,
            "verified": verified
        }
        self.history.append(entry)
        return entry
    
    def deutsch_jozsa_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.history),
            "correct": sum(1 for h in self.history if h["verified"])
        }
