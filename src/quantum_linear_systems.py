"""
Quantum Linear Systems Module
HHL algorithm, quantum matrix inversion,
condition number estimation, and linear system solvers for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LinearSystemSolution:
    """Solution to linear system."""
    x: List[float]
    residual: float
    condition_number: float


class ClassicalLinearSolver:
    """
    Classical reference linear system solver.
    """
    
    def __init__(self):
        pass
    
    def solve_2x2(self, A: List[List[float]],
                 b: List[float]) -> Optional[List[float]]:
        """
        Solve 2x2 linear system.
        
        Args:
            A: 2x2 matrix
            b: RHS vector
        
        Returns:
            Solution vector or None
        """
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if abs(det) < 1e-10:
            return None
        
        x0 = (A[1][1] * b[0] - A[0][1] * b[1]) / det
        x1 = (-A[1][0] * b[0] + A[0][0] * b[1]) / det
        return [x0, x1]
    
    def residual(self, A: List[List[float]],
                b: List[float],
                x: List[float]) -> float:
        """
        Compute residual norm ||Ax - b||.
        
        Args:
            A: Matrix
            b: RHS
            x: Solution
        
        Returns:
            Residual norm
        """
        n = len(b)
        residual = 0.0
        for i in range(n):
            ax_i = sum(A[i][j] * x[j] for j in range(len(x)))
            residual += (ax_i - b[i]) ** 2
        return math.sqrt(residual)


class QuantumPhaseEstimationForHHL:
    """
    Quantum phase estimation for HHL algorithm.
    """
    
    def __init__(self, num_ancilla: int = 4):
        """
        Args:
            num_ancilla: Number of ancilla qubits
        """
        self.num_ancilla = num_ancilla
    
    def estimate_phase(self, eigenvalue: float,
                      precision: int = 4) -> float:
        """
        Estimate phase of eigenvalue.
        
        Args:
            eigenvalue: Eigenvalue
            precision: Bits of precision
        
        Returns:
            Estimated phase
        """
        # Simplified: phase = eigenvalue / 2pi
        return eigenvalue / (2.0 * math.pi)
    
    def binary_representation(self, phase: float,
                             bits: int = 4) -> List[int]:
        """
        Convert phase to binary representation.
        
        Args:
            phase: Phase value [0, 1)
            bits: Number of bits
        
        Returns:
            Binary representation
        """
        phase = phase % 1.0
        binary = []
        for _ in range(bits):
            phase *= 2.0
            bit = int(phase)
            binary.append(bit)
            phase -= bit
        return binary


class QuantumMatrixInversion:
    """
    Quantum matrix inversion (HHL core).
    """
    
    def __init__(self):
        self.pe = QuantumPhaseEstimationForHHL()
        self.classical = ClassicalLinearSolver()
    
    def condition_number(self, eigenvalues: List[float]) -> float:
        """
        Compute condition number from eigenvalues.
        
        Args:
            eigenvalues: Eigenvalues
        
        Returns:
            Condition number
        """
        abs_eig = [abs(e) for e in eigenvalues if abs(e) > 1e-10]
        if not abs_eig:
            return float('inf')
        return max(abs_eig) / min(abs_eig)
    
    def inverse_eigenvalue(self, eigenvalue: float,
                          kappa: float = 100.0) -> float:
        """
        Compute inverted eigenvalue with scaling.
        
        Args:
            eigenvalue: Eigenvalue
            kappa: Condition number bound
        
        Returns:
            Scaled inverse eigenvalue
        """
        if abs(eigenvalue) < 1e-10:
            return 0.0
        # Scale to avoid divergence
        scale = 1.0 / kappa
        return scale / eigenvalue
    
    def hhl_solution_2x2(self, A: List[List[float]],
                        b: List[float],
                        eigenvalues: List[float]) -> Optional[LinearSystemSolution]:
        """
        HHL solution for 2x2 system (simplified).
        
        Args:
            A: 2x2 Hermitian matrix
            b: RHS vector
            eigenvalues: Eigenvalues of A
        
        Returns:
            Solution or None
        """
        classical_sol = self.classical.solve_2x2(A, b)
        if classical_sol is None:
            return None
        
        kappa = self.condition_number(eigenvalues)
        res = self.classical.residual(A, b, classical_sol)
        
        return LinearSystemSolution(classical_sol, res, kappa)


class QuantumLinearSystems:
    """
    Unified quantum linear systems controller.
    """
    
    def __init__(self):
        self.classical = ClassicalLinearSolver()
        self.pe = QuantumPhaseEstimationForHHL()
        self.inversion = QuantumMatrixInversion()
    
    def hhl_summary(self) -> Dict:
        """Get summary."""
        return {
            "algorithm": "HHL",
            "steps": ["phase_estimation", "controlled_rotation", "uncomputation"],
            "complexity": "O(log(N) * kappa^2 / epsilon)"
        }
