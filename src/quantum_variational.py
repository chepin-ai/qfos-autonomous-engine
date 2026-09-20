"""
Quantum Variational Module
Variational Quantum Eigensolver (VQE), ansatz circuits,
and parameter optimization for autonomous quantum simulation.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class AnsatzType(Enum):
    """Types of variational ansatzes."""
    RY = "ry"
    RYRZ = "ryrz"
    UCCSD = "uccsd"
    HARDWARE = "hardware_efficient"


@dataclass
class VariationalParameter:
    """A variational circuit parameter."""
    name: str
    value: float
    bounds: Tuple[float, float] = (-math.pi, math.pi)


class PauliHamiltonian:
    """
    Hamiltonian as sum of Pauli strings.
    """
    
    def __init__(self):
        self.terms: List[Tuple[str, float]] = []
    
    def add_term(self, pauli_string: str, coefficient: float):
        """
        Add Pauli term.
        
        Args:
            pauli_string: Pauli string (e.g., "ZI")
            coefficient: Weight
        """
        self.terms.append((pauli_string, coefficient))
    
    def expectation(self, bitstring: str) -> float:
        """
        Compute expectation for a bitstring.
        
        Args:
            bitstring: Measurement outcome
        
        Returns:
            Energy contribution
        """
        energy = 0.0
        for pauli, coef in self.terms:
            sign = 1.0
            for i, p in enumerate(reversed(pauli)):
                if p != 'I' and i < len(bitstring):
                    bit = int(bitstring[i])
                    if p == 'Z':
                        sign *= 1.0 if bit == 0 else -1.0
                    elif p == 'X':
                        # For diagonal expectation, X average is 0
                        sign = 0.0
                        break
                    elif p == 'Y':
                        sign = 0.0
                        break
            energy += coef * sign
        return energy
    
    def num_qubits(self) -> int:
        """
        Get number of qubits.
        
        Returns:
            Qubit count
        """
        if not self.terms:
            return 0
        return len(self.terms[0][0])


class VariationalAnsatz:
    """
    Parameterized quantum circuit ansatz.
    """
    
    def __init__(self, num_qubits: int, ansatz_type: AnsatzType = AnsatzType.RY):
        """
        Args:
            num_qubits: Number of qubits
            ansatz_type: Ansatz type
        """
        self.num_qubits = num_qubits
        self.ansatz_type = ansatz_type
        self.parameters: List[VariationalParameter] = []
        self._build()
    
    def _build(self):
        """Build parameter list."""
        if self.ansatz_type == AnsatzType.RY:
            for i in range(self.num_qubits):
                self.parameters.append(VariationalParameter(f"ry_{i}", 0.0))
        elif self.ansatz_type == AnsatzType.RYRZ:
            for i in range(self.num_qubits):
                self.parameters.append(VariationalParameter(f"ry_{i}", 0.0))
                self.parameters.append(VariationalParameter(f"rz_{i}", 0.0))
        elif self.ansatz_type == AnsatzType.HARDWARE:
            layers = 2
            for l in range(layers):
                for i in range(self.num_qubits):
                    self.parameters.append(VariationalParameter(f"ry_{l}_{i}", 0.0))
                    self.parameters.append(VariationalParameter(f"rz_{l}_{i}", 0.0))
    
    def set_parameters(self, values: List[float]):
        """
        Set parameter values.
        
        Args:
            values: Parameter values
        """
        for i, v in enumerate(values):
            if i < len(self.parameters):
                self.parameters[i].value = v
    
    def num_parameters(self) -> int:
        """
        Get parameter count.
        
        Returns:
            Number of parameters
        """
        return len(self.parameters)
    
    def statevector(self) -> List[complex]:
        """
        Compute statevector (simplified RY ansatz).
        
        Returns:
            State amplitudes
        """
        # Start with |0...0>
        dim = 2**self.num_qubits
        state = [0.0j] * dim
        state[0] = 1.0
        
        # Apply RY rotations
        for i, param in enumerate(self.parameters):
            if i >= self.num_qubits:
                break
            
            theta = param.value
            new_state = [0.0j] * dim
            
            for b in range(dim):
                bit = (b >> i) & 1
                cos = math.cos(theta / 2.0)
                sin = math.sin(theta / 2.0)
                
                if bit == 0:
                    new_state[b] += state[b] * cos
                    new_state[b | (1 << i)] += state[b] * sin
                else:
                    new_state[b & ~(1 << i)] += state[b] * (-sin)
                    new_state[b] += state[b] * cos
            
            state = new_state
        
        # Normalize
        norm = math.sqrt(sum(abs(a)**2 for a in state))
        if norm > 0:
            state = [a / norm for a in state]
        
        return state


class ParameterOptimizer:
    """
    Classical parameter optimizer.
    """
    
    def __init__(self, learning_rate: float = 0.1,
                 max_iterations: int = 100):
        """
        Args:
            learning_rate: Step size
            max_iterations: Max iterations
        """
        self.lr = learning_rate
        self.max_iter = max_iterations
    
    def gradient_descent(self, energy_func, params: List[float]) -> Tuple[List[float], float]:
        """
        Simple gradient descent.
        
        Args:
            energy_func: Function(params) -> energy
            params: Initial parameters
        
        Returns:
            Optimized parameters and energy
        """
        current = list(params)
        best_energy = energy_func(current)
        best_params = list(current)
        
        for _ in range(self.max_iter):
            # Numerical gradient
            grad = []
            eps = 1e-4
            
            for i in range(len(current)):
                p_plus = list(current)
                p_minus = list(current)
                p_plus[i] += eps
                p_minus[i] -= eps
                
                g = (energy_func(p_plus) - energy_func(p_minus)) / (2.0 * eps)
                grad.append(g)
            
            # Update
            for i in range(len(current)):
                current[i] -= self.lr * grad[i]
            
            energy = energy_func(current)
            if energy < best_energy:
                best_energy = energy
                best_params = list(current)
        
        return best_params, best_energy
    
    def nelder_mead(self, energy_func, params: List[float]) -> Tuple[List[float], float]:
        """
        Simplified Nelder-Mead optimization.
        
        Args:
            energy_func: Energy function
            params: Initial parameters
        
        Returns:
            Optimized parameters and energy
        """
        current = list(params)
        best_energy = energy_func(current)
        
        for _ in range(self.max_iter):
            # Simple random walk
            trial = [p + random.uniform(-self.lr, self.lr) for p in current]
            energy = energy_func(trial)
            
            if energy < best_energy:
                best_energy = energy
                current = trial
        
        return current, best_energy


class VQE:
    """
    Variational Quantum Eigensolver.
    """
    
    def __init__(self, hamiltonian: PauliHamiltonian,
                 ansatz: VariationalAnsatz):
        """
        Args:
            hamiltonian: Problem Hamiltonian
            ansatz: Variational ansatz
        """
        self.hamiltonian = hamiltonian
        self.ansatz = ansatz
        self.optimizer = ParameterOptimizer()
        self.energy_history: List[float] = []
    
    def energy(self, parameters: List[float]) -> float:
        """
        Compute energy for parameters.
        
        Args:
            parameters: Circuit parameters
        
        Returns:
            Energy expectation
        """
        self.ansatz.set_parameters(parameters)
        state = self.ansatz.statevector()
        
        # Compute <psi|H|psi>
        energy = 0.0
        for pauli, coef in self.hamiltonian.terms:
            # For Z-only terms, compute expectation directly
            if all(p in 'IZ' for p in pauli):
                exp = 0.0
                for b in range(len(state)):
                    sign = 1.0
                    for i, p in enumerate(reversed(pauli)):
                        if p == 'Z':
                            bit = (b >> i) & 1
                            sign *= 1.0 if bit == 0 else -1.0
                    exp += abs(state[b])**2 * sign
                energy += coef * exp
            else:
                # Non-diagonal terms: simplified (average to 0 for random)
                energy += coef * 0.0
        
        return energy
    
    def run(self, initial_params: Optional[List[float]] = None,
            method: str = "gradient") -> Dict:
        """
        Run VQE.
        
        Args:
            initial_params: Starting parameters
            method: "gradient" or "nelder_mead"
        
        Returns:
            Results dict
        """
        n = self.ansatz.num_parameters()
        if initial_params is None:
            initial_params = [random.uniform(-math.pi, math.pi) for _ in range(n)]
        
        if method == "gradient":
            params, energy = self.optimizer.gradient_descent(self.energy, initial_params)
        else:
            params, energy = self.optimizer.nelder_mead(self.energy, initial_params)
        
        self.ansatz.set_parameters(params)
        
        return {
            "optimal_params": params,
            "ground_state_energy": energy,
            "iterations": self.optimizer.max_iter
        }
    
    def ground_state(self) -> List[complex]:
        """
        Get optimized ground state.
        
        Returns:
            Statevector
        """
        return self.ansatz.statevector()


class QuantumVariational:
    """
    Unified quantum variational controller.
    """
    
    def __init__(self):
        self.vqe: Optional[VQE] = None
        self.results: List[Dict] = []
    
    def setup(self, hamiltonian: PauliHamiltonian,
              ansatz_type: AnsatzType = AnsatzType.RY):
        """
        Setup VQE problem.
        
        Args:
            hamiltonian: Hamiltonian
            ansatz_type: Ansatz type
        """
        ansatz = VariationalAnsatz(hamiltonian.num_qubits(), ansatz_type)
        self.vqe = VQE(hamiltonian, ansatz)
    
    def solve(self, method: str = "gradient") -> Dict:
        """
        Solve VQE.
        
        Args:
            method: Optimization method
        
        Returns:
            Results
        """
        if self.vqe is None:
            return {"status": "not_setup"}
        
        result = self.vqe.run(method=method)
        self.results.append(result)
        return result
    
    def variational_summary(self) -> Dict:
        """Get summary."""
        if not self.results:
            return {"status": "no_results"}
        
        energies = [r["ground_state_energy"] for r in self.results]
        return {
            "runs": len(self.results),
            "best_energy": min(energies),
            "avg_energy": sum(energies) / len(energies)
        }
