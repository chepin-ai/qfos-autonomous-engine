"""
Quantum State Tomography Module
Density matrix reconstruction, fidelity estimation, POVM,
and maximum likelihood for autonomous quantum characterization.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PauliBasis(Enum):
    """Pauli measurement basis."""
    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"


@dataclass
class MeasurementResult:
    """A quantum measurement outcome."""
    basis: PauliBasis
    outcome: int  # +1 or -1
    shots: int = 1


class DensityMatrix:
    """
    Quantum density matrix for single qubit.
    """
    
    def __init__(self):
        # rho = 0.5 * (I + r_x * X + r_y * Y + r_z * Z)
        self.r = [0.0, 0.0, 0.0]  # Bloch vector (x, y, z)
    
    def from_bloch(self, rx: float, ry: float, rz: float):
        """
        Set from Bloch vector.
        
        Args:
            rx, ry, rz: Bloch components
        """
        self.r = [rx, ry, rz]
    
    def matrix_element(self, i: int, j: int) -> complex:
        """
        Get density matrix element.
        
        Args:
            i, j: Matrix indices
        
        Returns:
            rho_ij
        """
        # rho = [[0.5*(1+rz), 0.5*(rx-1j*ry)],
        #        [0.5*(rx+1j*ry), 0.5*(1-rz)]]
        if i == 0 and j == 0:
            return 0.5 * (1.0 + self.r[2])
        elif i == 0 and j == 1:
            return 0.5 * (self.r[0] - 1j * self.r[1])
        elif i == 1 and j == 0:
            return 0.5 * (self.r[0] + 1j * self.r[1])
        elif i == 1 and j == 1:
            return 0.5 * (1.0 - self.r[2])
        return 0.0
    
    def purity(self) -> float:
        """
        Compute purity Tr(rho^2).
        
        Returns:
            Purity (0.5 to 1.0)
        """
        r_sq = sum(ri**2 for ri in self.r)
        return 0.5 * (1.0 + r_sq)
    
    def is_physical(self) -> bool:
        """
        Check if density matrix is physical.
        
        Returns:
            True if valid
        """
        r_sq = sum(ri**2 for ri in self.r)
        return r_sq <= 1.0 + 1e-6
    
    def fidelity(self, other: 'DensityMatrix') -> float:
        """
        Compute fidelity between states.
        
        Args:
            other: Another density matrix
        
        Returns:
            Fidelity
        """
        # F = Tr(sqrt(sqrt(rho) * sigma * sqrt(rho)))^2
        # Simplified for single qubit: F = 0.5 * (1 + r1 . r2)
        dot = sum(a * b for a, b in zip(self.r, other.r))
        return 0.5 * (1.0 + dot)


class StateTomography:
    """
    Quantum state tomography reconstruction.
    """
    
    def __init__(self):
        self.measurements: List[MeasurementResult] = []
    
    def add_measurement(self, result: MeasurementResult):
        """Add measurement result."""
        self.measurements.append(result)
    
    def linear_inversion(self) -> DensityMatrix:
        """
        Reconstruct state via linear inversion.
        
        Returns:
            Reconstructed density matrix
        """
        # Average outcomes per basis
        sums = {b: 0.0 for b in PauliBasis if b != PauliBasis.I}
        counts = {b: 0 for b in PauliBasis if b != PauliBasis.I}
        
        for m in self.measurements:
            if m.basis in sums:
                sums[m.basis] += m.outcome * m.shots
                counts[m.basis] += m.shots
        
        rho = DensityMatrix()
        
        # Bloch vector components from expectation values
        for i, basis in enumerate([PauliBasis.X, PauliBasis.Y, PauliBasis.Z]):
            if counts[basis] > 0:
                rho.r[i] = sums[basis] / counts[basis]
        
        return rho
    
    def maximum_likelihood(self, iterations: int = 100) -> DensityMatrix:
        """
        Maximum likelihood estimation (simplified).
        
        Args:
            iterations: Iteration count
        
        Returns:
            ML-estimated density matrix
        """
        # Start with linear inversion
        rho = self.linear_inversion()
        
        # Ensure physical (project onto Bloch sphere)
        r_sq = sum(ri**2 for ri in rho.r)
        if r_sq > 1.0:
            scale = 1.0 / math.sqrt(r_sq)
            rho.r = [ri * scale for ri in rho.r]
        
        return rho
    
    def estimate_expectation(self, basis: PauliBasis) -> float:
        """
        Estimate expectation value.
        
        Args:
            basis: Pauli basis
        
        Returns:
            Expectation value
        """
        total = 0
        shots = 0
        
        for m in self.measurements:
            if m.basis == basis:
                total += m.outcome * m.shots
                shots += m.shots
        
        if shots == 0:
            return 0.0
        return total / shots


class POVM:
    """
    Positive Operator-Valued Measure.
    """
    
    def __init__(self):
        self.operators: List[List[List[complex]]] = []
    
    def add_operator(self, operator: List[List[complex]]):
        """Add POVM element."""
        self.operators.append(operator)
    
    def probability(self, state: DensityMatrix,
                   operator_index: int) -> float:
        """
        Compute measurement probability.
        
        Args:
            state: Quantum state
            operator_index: POVM element index
        
        Returns:
            Probability
        """
        if operator_index >= len(self.operators):
            return 0.0
        
        E = self.operators[operator_index]
        # p = Tr(rho * E)
        p = 0.0
        for i in range(2):
            for j in range(2):
                p += (state.matrix_element(i, j) * E[j][i]).real
        
        return max(0.0, min(1.0, p))
    
    def completeness(self) -> bool:
        """
        Check POVM completeness (sum E_i = I).
        
        Returns:
            True if complete
        """
        if not self.operators:
            return False
        
        total = [[0j, 0j], [0j, 0j]]
        for E in self.operators:
            for i in range(2):
                for j in range(2):
                    total[i][j] += E[i][j]
        
        # Check if total is identity
        identity = [[1, 0], [0, 1]]
        for i in range(2):
            for j in range(2):
                if abs(total[i][j] - identity[i][j]) > 0.01:
                    return False
        
        return True


class TomographyFidelity:
    """
    Estimate tomography fidelity.
    """
    
    def __init__(self):
        self.true_state: Optional[DensityMatrix] = None
    
    def set_true_state(self, state: DensityMatrix):
        """Set known true state."""
        self.true_state = state
    
    def reconstruction_fidelity(self, estimated: DensityMatrix) -> float:
        """
        Compute reconstruction fidelity.
        
        Args:
            estimated: Estimated state
        
        Returns:
            Fidelity
        """
        if self.true_state is None:
            return estimated.purity()
        return self.true_state.fidelity(estimated)
    
    def statistical_error(self, num_shots: int) -> float:
        """
        Estimate statistical error.
        
        Args:
            num_shots: Number of measurements
        
        Returns:
            Standard error
        """
        if num_shots <= 0:
            return 1.0
        return 1.0 / math.sqrt(num_shots)


class QuantumStateTomography:
    """
    Unified quantum state tomography controller.
    """
    
    def __init__(self):
        self.tomography = StateTomography()
        self.povm = POVM()
        self.fidelity = TomographyFidelity()
        self.reconstructed: Optional[DensityMatrix] = None
    
    def measure(self, basis: PauliBasis, outcome: int, shots: int = 1):
        """
        Record measurement.
        
        Args:
            basis: Measurement basis
            outcome: +1 or -1
            shots: Number of shots
        """
        self.tomography.add_measurement(MeasurementResult(basis, outcome, shots))
    
    def reconstruct(self, method: str = "linear") -> DensityMatrix:
        """
        Reconstruct quantum state.
        
        Args:
            method: "linear" or "ml"
        
        Returns:
            Reconstructed state
        """
        if method == "ml":
            self.reconstructed = self.tomography.maximum_likelihood()
        else:
            self.reconstructed = self.tomography.linear_inversion()
        
        return self.reconstructed
    
    def tomography_summary(self) -> Dict:
        """Get tomography summary."""
        if self.reconstructed is None:
            return {"status": "not_reconstructed"}
        
        return {
            "measurements": len(self.tomography.measurements),
            "purity": self.reconstructed.purity(),
            "physical": self.reconstructed.is_physical(),
            "bloch_vector": self.reconstructed.r,
            "fidelity": self.fidelity.reconstruction_fidelity(self.reconstructed) if self.fidelity.true_state else None
        }
