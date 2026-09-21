"""
Quantum Simulation Module
State vector simulation, density matrix evolution,
Hamiltonian simulation, and time evolution for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumState:
    """Quantum state vector."""
    amplitudes: List[complex]
    
    def norm(self) -> float:
        """Compute norm."""
        return math.sqrt(sum(abs(a) ** 2 for a in self.amplitudes))
    
    def normalize(self):
        """Normalize state."""
        n = self.norm()
        if n > 0:
            self.amplitudes = [a / n for a in self.amplitudes]


class StateVectorSimulator:
    """
    State vector quantum simulator.
    """
    
    def __init__(self, num_qubits: int = 2):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.state = QuantumState([complex(1.0) if i == 0 else complex(0.0)
                                    for i in range(self.dim)])
    
    def apply_gate(self, gate_matrix: List[List[complex]],
                  target_qubits: List[int]):
        """
        Apply gate to state.
        
        Args:
            gate_matrix: Gate matrix
            target_qubits: Target qubits
        """
        # Simplified: apply full matrix
        new_amps = [complex(0.0) for _ in range(self.dim)]
        for i in range(self.dim):
            for j in range(self.dim):
                new_amps[i] += gate_matrix[i][j] * self.state.amplitudes[j]
        self.state.amplitudes = new_amps
    
    def measure(self, qubit: int) -> int:
        """
        Measure qubit.
        
        Args:
            qubit: Qubit to measure
        
        Returns:
            Measurement outcome (0 or 1)
        """
        prob_0 = 0.0
        for i in range(self.dim):
            if (i >> qubit) & 1 == 0:
                prob_0 += abs(self.state.amplitudes[i]) ** 2
        
        # Collapse
        if prob_0 > 0.5:
            new_amps = [self.state.amplitudes[i] if (i >> qubit) & 1 == 0 else complex(0.0)
                       for i in range(self.dim)]
            self.state.amplitudes = new_amps
            self.state.normalize()
            return 0
        else:
            new_amps = [self.state.amplitudes[i] if (i >> qubit) & 1 == 1 else complex(0.0)
                       for i in range(self.dim)]
            self.state.amplitudes = new_amps
            self.state.normalize()
            return 1
    
    def expectation(self, observable: List[List[complex]]) -> float:
        """
        Compute expectation value.
        
        Args:
            observable: Observable matrix
        
        Returns:
            Expectation value
        """
        result = 0.0
        for i in range(self.dim):
            for j in range(self.dim):
                result += (self.state.amplitudes[i].conjugate() *
                          observable[i][j] * self.state.amplitudes[j]).real
        return result


class DensityMatrixSimulator:
    """
    Density matrix simulator.
    """
    
    def __init__(self, num_qubits: int = 2):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.rho: List[List[complex]] = []
        self._init_pure_state(0)
    
    def _init_pure_state(self, basis_state: int):
        """Initialize pure state."""
        self.rho = [[complex(1.0) if i == basis_state and j == basis_state else complex(0.0)
                     for j in range(self.dim)] for i in range(self.dim)]
    
    def apply_unitary(self, U: List[List[complex]]):
        """
        Apply unitary: rho -> U rho U^
        
        Args:
            U: Unitary matrix
        """
        # U rho U^
        temp = [[sum(U[i][k] * self.rho[k][j] for k in range(self.dim))
                for j in range(self.dim)] for i in range(self.dim)]
        
        self.rho = [[sum(temp[i][k] * U[j][k].conjugate() for k in range(self.dim))
                    for j in range(self.dim)] for i in range(self.dim)]
    
    def trace(self) -> float:
        """
        Compute trace.
        
        Returns:
            Trace
        """
        return sum(self.rho[i][i].real for i in range(self.dim))
    
    def purity(self) -> float:
        """
        Compute purity Tr(rho^2).
        
        Returns:
            Purity
        """
        result = 0.0
        for i in range(self.dim):
            for j in range(self.dim):
                result += abs(self.rho[i][j]) ** 2
        return result
    
    def von_neumann_entropy(self) -> float:
        """
        Compute von Neumann entropy.
        
        Returns:
            Entropy
        """
        # Diagonalize and compute eigenvalues
        # Simplified: compute from diagonal elements
        entropy = 0.0
        for i in range(self.dim):
            p = self.rho[i][i].real
            if p > 0:
                entropy -= p * math.log(p)
        return entropy


class HamiltonianSimulator:
    """
    Hamiltonian time evolution simulator.
    """
    
    def __init__(self):
        pass
    
    def time_evolve(self, state: QuantumState,
                   H: List[List[complex]],
                   dt: float,
                   num_steps: int) -> QuantumState:
        """
        Time evolve state under Hamiltonian.
        
        Args:
            state: Initial state
            H: Hamiltonian
            dt: Time step
            num_steps: Number of steps
        
        Returns:
            Evolved state
        """
        dim = len(state.amplitudes)
        current = QuantumState(state.amplitudes[:])
        
        for _ in range(num_steps):
            # Simple Euler: |psi(t+dt)> = |psi(t)> - i H |psi(t)> dt
            new_amps = []
            for i in range(dim):
                val = current.amplitudes[i]
                for j in range(dim):
                    val -= complex(0.0, 1.0) * H[i][j] * current.amplitudes[j] * dt
                new_amps.append(val)
            current.amplitudes = new_amps
            current.normalize()
        
        return current
    
    def energy(self, state: QuantumState,
              H: List[List[complex]]) -> float:
        """
        Compute energy expectation.
        
        Args:
            state: State
            H: Hamiltonian
        
        Returns:
            Energy
        """
        dim = len(state.amplitudes)
        result = 0.0
        for i in range(dim):
            for j in range(dim):
                result += (state.amplitudes[i].conjugate() *
                          H[i][j] * state.amplitudes[j]).real
        return result


class QuantumSimulation:
    """
    Unified quantum simulation controller.
    """
    
    def __init__(self, num_qubits: int = 2):
        self.state_vec = StateVectorSimulator(num_qubits)
        self.density = DensityMatrixSimulator(num_qubits)
        self.hamiltonian = HamiltonianSimulator()
    
    def qs_summary(self) -> Dict:
        """Get summary."""
        return {
            "simulators": ["state_vector", "density_matrix", "hamiltonian"],
            "num_qubits": self.state_vec.num_qubits,
            "dimension": self.state_vec.dim
        }
