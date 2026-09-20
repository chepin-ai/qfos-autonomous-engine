"""
Quantum Bernstein-Vazirani Module
Hidden string determination, BV algorithm,
and linear function characterization for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class BVOracle:
    """
    Oracle for Bernstein-Vazirani: f(x) = s . x (mod 2)
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of input qubits
        """
        self.n = num_qubits
        self.hidden_string: int = 0
    
    def set_hidden_string(self, s: int):
        """
        Set hidden string.
        
        Args:
            s: Hidden bitstring as integer
        """
        self.hidden_string = s & ((1 << self.n) - 1)
    
    def evaluate(self, x: int) -> int:
        """
        Evaluate f(x) = s . x mod 2.
        
        Args:
            x: Input integer
        
        Returns:
            Dot product mod 2
        """
        return bin(self.hidden_string & x).count("1") & 1
    
    def apply(self, state: List[complex]) -> List[complex]:
        """
        Apply phase oracle to quantum state.
        
        Args:
            state: Input statevector
        
        Returns:
            Output statevector
        """
        new_state = list(state)
        dim = len(state)
        
        for i in range(dim):
            x = i & ((1 << self.n) - 1)
            if self.evaluate(x) == 1:
                new_state[i] = -state[i]
        
        return new_state


class BernsteinVazirani:
    """
    Bernstein-Vazirani algorithm.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of input qubits
        """
        self.n = num_qubits
        self.oracle = BVOracle(num_qubits)
        self.result: Optional[int] = None
    
    def _hadamard_single(self, state: List[complex],
                        qubit: int) -> List[complex]:
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
    
    def run(self, hidden_string: Optional[int] = None) -> int:
        """
        Run BV algorithm.
        
        Args:
            hidden_string: Known hidden string (for testing)
        
        Returns:
            Discovered hidden string
        """
        if hidden_string is not None:
            self.oracle.set_hidden_string(hidden_string)
        
        # Initialize |0...0>|1>
        dim = 2**(self.n + 1)
        state = [0.0j] * dim
        state[1 << self.n] = 1.0
        
        # Apply H to all qubits
        for q in range(self.n + 1):
            state = self._hadamard_single(state, q)
        
        # Apply oracle
        state = self.oracle.apply(state)
        
        # Apply H to input qubits
        for q in range(self.n):
            state = self._hadamard_single(state, q)
        
        # Measure input qubits
        # The state should be |s>|->
        self.result = 0
        for q in range(self.n):
            # Check probability of |1> for qubit q
            prob_one = 0.0
            for i in range(dim):
                if (i >> q) & 1 == 1:
                    prob_one += abs(state[i])**2
            
            if prob_one > 0.5:
                self.result |= (1 << q)
        
        return self.result
    
    def verify(self) -> bool:
        """
        Verify result.
        
        Returns:
            True if correct
        """
        if self.result is None:
            return False
        return self.result == self.oracle.hidden_string


class QuantumBernsteinVazirani:
    """
    Unified Bernstein-Vazirani controller.
    """
    
    def __init__(self):
        self.bv: Optional[BernsteinVazirani] = None
        self.history: List[Dict] = []
    
    def setup(self, num_qubits: int):
        """
        Setup BV algorithm.
        
        Args:
            num_qubits: Number of qubits
        """
        self.bv = BernsteinVazirani(num_qubits)
    
    def solve(self, hidden_string: int) -> Dict:
        """
        Solve BV problem.
        
        Args:
            hidden_string: Hidden string to find
        
        Returns:
            Results
        """
        if self.bv is None:
            return {"status": "not_setup"}
        
        result = self.bv.run(hidden_string)
        verified = self.bv.verify()
        
        entry = {
            "n_qubits": self.bv.n,
            "hidden_string": hidden_string,
            "discovered": result,
            "verified": verified
        }
        self.history.append(entry)
        return entry
    
    def bv_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.history),
            "correct": sum(1 for h in self.history if h["verified"])
        }
