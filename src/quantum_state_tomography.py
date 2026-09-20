"""
Quantum State Tomography Module
Density matrix estimation, state reconstruction,
and fidelity computation for autonomous quantum characterization.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class DensityMatrix:
    """
    Quantum density matrix representation.
    """
    
    def __init__(self, dim: int):
        """
        Args:
            dim: Hilbert space dimension
        """
        self.dim = dim
        # Initialize as maximally mixed state
        self.matrix: List[List[complex]] = [[complex(1.0 / dim, 0.0) if i == j else complex(0.0, 0.0)
                                             for j in range(dim)]
                                            for i in range(dim)]
    
    def trace(self) -> complex:
        """
        Compute trace.
        
        Returns:
            Trace
        """
        return sum(self.matrix[i][i] for i in range(self.dim))
    
    def purity(self) -> float:
        """
        Compute purity Tr(rho^2).
        
        Returns:
            Purity (1/dim to 1)
        """
        total = 0.0
        for i in range(self.dim):
            for j in range(self.dim):
                total += (self.matrix[i][j] * self.matrix[j][i]).real
        return total
    
    def expectation(self, operator: List[List[complex]]) -> float:
        """
        Compute expectation value Tr(rho * O).
        
        Args:
            operator: Operator matrix
        
        Returns:
            Expectation value
        """
        total = complex(0.0, 0.0)
        for i in range(self.dim):
            for j in range(self.dim):
                total += self.matrix[i][j] * operator[j][i]
        return total.real
    
    def set_pure_state(self, state: List[complex]):
        """
        Set as pure state |psi><psi|.
        
        Args:
            state: State vector
        """
        for i in range(self.dim):
            for j in range(self.dim):
                if i < len(state) and j < len(state):
                    self.matrix[i][j] = state[i] * state[j].conjugate()
                else:
                    self.matrix[i][j] = complex(0.0, 0.0)
    
    def is_physical(self, tolerance: float = 1e-6) -> bool:
        """
        Check if density matrix is physical.
        
        Args:
            tolerance: Tolerance
        
        Returns:
            True if physical
        """
        # Check trace = 1
        tr = self.trace()
        if abs(tr.real - 1.0) > tolerance or abs(tr.imag) > tolerance:
            return False
        
        # Check Hermitian
        for i in range(self.dim):
            for j in range(self.dim):
                if abs(self.matrix[i][j] - self.matrix[j][i].conjugate()) > tolerance:
                    return False
        
        return True


class StateTomography:
    """
    Quantum state tomography using Pauli measurements.
    """
    
    def __init__(self, num_qubits: int = 1):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
        self.measurements: List[Dict] = []
    
    def pauli_x(self) -> List[List[complex]]:
        """Pauli X operator."""
        return [[complex(0.0, 0.0), complex(1.0, 0.0)],
                [complex(1.0, 0.0), complex(0.0, 0.0)]]
    
    def pauli_y(self) -> List[List[complex]]:
        """Pauli Y operator."""
        return [[complex(0.0, 0.0), complex(0.0, -1.0)],
                [complex(0.0, 1.0), complex(0.0, 0.0)]]
    
    def pauli_z(self) -> List[List[complex]]:
        """Pauli Z operator."""
        return [[complex(1.0, 0.0), complex(0.0, 0.0)],
                [complex(0.0, 0.0), complex(-1.0, 0.0)]]
    
    def identity(self) -> List[List[complex]]:
        """Identity operator."""
        return [[complex(1.0, 0.0), complex(0.0, 0.0)],
                [complex(0.0, 0.0), complex(1.0, 0.0)]]
    
    def tensor_product(self, A: List[List[complex]],
                      B: List[List[complex]]) -> List[List[complex]]:
        """
        Compute tensor product A x B.
        
        Args:
            A: First matrix
            B: Second matrix
        
        Returns:
            Tensor product
        """
        a_dim = len(A)
        b_dim = len(B)
        result = []
        for i in range(a_dim):
            for k in range(b_dim):
                row = []
                for j in range(a_dim):
                    for l in range(b_dim):
                        row.append(A[i][j] * B[k][l])
                result.append(row)
        return result
    
    def add_measurement(self, operator: str,
                       expectation: float,
                       shots: int = 1000):
        """
        Add measurement result.
        
        Args:
            operator: Pauli string (e.g., "X", "Z", "XI")
            expectation: Measured expectation
            shots: Number of shots
        """
        self.measurements.append({
            "operator": operator,
            "expectation": expectation,
            "shots": shots
        })
    
    def reconstruct(self) -> DensityMatrix:
        """
        Reconstruct density matrix from measurements.
        
        Returns:
            Reconstructed density matrix
        """
        rho = DensityMatrix(self.dim)
        
        # Initialize to maximally mixed
        for i in range(self.dim):
            for j in range(self.dim):
                rho.matrix[i][j] = complex(1.0 / self.dim if i == j else 0.0, 0.0)
        
        # Simplified: use measurements to update diagonal elements
        for m in self.measurements:
            if m["operator"] == "Z" and self.n == 1:
                # rho_00 = (1 + <Z>) / 2
                # rho_11 = (1 - <Z>) / 2
                rho.matrix[0][0] = complex((1.0 + m["expectation"]) / 2.0, 0.0)
                rho.matrix[1][1] = complex((1.0 - m["expectation"]) / 2.0, 0.0)
            elif m["operator"] == "X" and self.n == 1:
                # Re(<X>) = rho_01 + rho_10
                val = m["expectation"] / 2.0
                rho.matrix[0][1] = complex(val, 0.0)
                rho.matrix[1][0] = complex(val, 0.0)
            elif m["operator"] == "Y" and self.n == 1:
                # Im(<Y>) = rho_10 - rho_01
                val = m["expectation"] / 2.0
                rho.matrix[0][1] = complex(rho.matrix[0][1].real, -val)
                rho.matrix[1][0] = complex(rho.matrix[1][0].real, val)
        
        return rho


class StateFidelity:
    """
    Quantum state fidelity computation.
    """
    
    def fidelity(self, rho1: DensityMatrix, rho2: DensityMatrix) -> float:
        """
        Compute fidelity F(rho1, rho2).
        Simplified using normalized overlap for mixed states.
        
        Args:
            rho1: First state
            rho2: Second state
        
        Returns:
            Fidelity (0 to 1)
        """
        overlap = complex(0.0, 0.0)
        for i in range(rho1.dim):
            for j in range(rho1.dim):
                overlap += rho1.matrix[i][j] * rho2.matrix[j][i]
        
        p1 = rho1.purity()
        p2 = rho2.purity()
        if p1 <= 0 or p2 <= 0:
            return 0.0
        
        # Normalized overlap ensures F(rho, rho) = 1
        return max(0.0, min(1.0, overlap.real / math.sqrt(p1 * p2)))
    
    def trace_distance(self, rho1: DensityMatrix, rho2: DensityMatrix) -> float:
        """
        Compute trace distance T = 0.5 * Tr(|rho1 - rho2|).
        Simplified.
        
        Args:
            rho1: First state
            rho2: Second state
        
        Returns:
            Trace distance
        """
        diff = 0.0
        for i in range(rho1.dim):
            for j in range(rho1.dim):
                d = rho1.matrix[i][j] - rho2.matrix[i][j]
                diff += abs(d)
        
        return 0.5 * diff


class QuantumStateTomography:
    """
    Unified quantum state tomography controller.
    """
    
    def __init__(self):
        self.tomography: Optional[StateTomography] = None
        self.reconstructed: Optional[DensityMatrix] = None
        self.fidelity_calculator = StateFidelity()
        self.history: List[Dict] = []
    
    def setup(self, num_qubits: int = 1):
        """
        Setup tomography.
        
        Args:
            num_qubits: Qubits
        """
        self.tomography = StateTomography(num_qubits)
    
    def measure(self, operator: str, expectation: float, shots: int = 1000):
        """
        Add measurement.
        
        Args:
            operator: Pauli string
            expectation: Expectation
            shots: Shots
        """
        if self.tomography:
            self.tomography.add_measurement(operator, expectation, shots)
    
    def reconstruct(self) -> DensityMatrix:
        """
        Reconstruct state.
        
        Returns:
            Density matrix
        """
        if self.tomography:
            self.reconstructed = self.tomography.reconstruct()
        return self.reconstructed
    
    def fidelity_with(self, target: DensityMatrix) -> float:
        """
        Compute fidelity with target.
        
        Args:
            target: Target state
        
        Returns:
            Fidelity
        """
        if self.reconstructed is None:
            return 0.0
        return self.fidelity_calculator.fidelity(self.reconstructed, target)
    
    def tomography_summary(self) -> Dict:
        """Get tomography summary."""
        return {
            "qubits": self.tomography.n if self.tomography else 0,
            "measurements": len(self.tomography.measurements) if self.tomography else 0,
            "reconstructed": self.reconstructed is not None,
            "purity": self.reconstructed.purity() if self.reconstructed else 0.0,
            "physical": self.reconstructed.is_physical() if self.reconstructed else False
        }
