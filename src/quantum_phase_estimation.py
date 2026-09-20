"""
Quantum Phase Estimation Module
QPE algorithm, eigenvalue estimation, precision analysis,
and controlled-U decomposition for autonomous quantum computation.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class PhaseGate:
    """
    Controlled phase rotation gates.
    """
    
    @staticmethod
    def controlled_phase(k: int) -> complex:
        """
        R_k gate: e^(2*pi*i / 2^k)
        
        Args:
            k: Gate precision parameter
        
        Returns:
            Phase factor
        """
        return complex(math.cos(2 * math.pi / (2**k)),
                      math.sin(2 * math.pi / (2**k)))
    
    @staticmethod
    def inverse_qft_phase(j: int, k: int, n: int) -> complex:
        """
        Phase for inverse QFT.
        
        Args:
            j, k: Qubit indices
            n: Total qubits
        
        Returns:
            Phase factor
        """
        angle = -2.0 * math.pi * (j - k) / (2**(n - k))
        return complex(math.cos(angle), math.sin(angle))


class QuantumFourierTransform:
    """
    Quantum Fourier Transform implementation.
    """
    
    def __init__(self, num_qubits: int = 3):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
    
    def apply(self, amplitudes: List[complex]) -> List[complex]:
        """
        Apply QFT to state amplitudes.
        
        Args:
            amplitudes: Input state
        
        Returns:
            Transformed amplitudes
        """
        N = len(amplitudes)
        if N != 2**self.n:
            # Pad or truncate
            amplitudes = amplitudes[:N] if len(amplitudes) > N else amplitudes + [0j] * (N - len(amplitudes))
        
        output = []
        for k in range(N):
            sum_val = 0j
            for j in range(N):
                angle = 2.0 * math.pi * j * k / N
                sum_val += amplitudes[j] * complex(math.cos(angle), math.sin(angle))
            output.append(sum_val / math.sqrt(N))
        
        return output
    
    def inverse(self, amplitudes: List[complex]) -> List[complex]:
        """
        Apply inverse QFT.
        
        Args:
            amplitudes: Input state
        
        Returns:
            Transformed amplitudes
        """
        N = len(amplitudes)
        output = []
        
        for k in range(N):
            sum_val = 0j
            for j in range(N):
                angle = -2.0 * math.pi * j * k / N
                sum_val += amplitudes[j] * complex(math.cos(angle), math.sin(angle))
            output.append(sum_val / math.sqrt(N))
        
        return output


class PhaseEstimator:
    """
    Quantum phase estimation algorithm.
    """
    
    def __init__(self, num_precision_qubits: int = 3):
        """
        Args:
            num_precision_qubits: Number of precision qubits
        """
        self.t = num_precision_qubits
        self.qft = QuantumFourierTransform(num_precision_qubits)
    
    def controlled_u_sequence(self, phase: float) -> List[complex]:
        """
        Simulate controlled-U^k operations.
        
        Args:
            phase: True phase (in units of 2*pi)
        
        Returns:
            Phase register state amplitudes
        """
        N = 2**self.t
        amplitudes = []
        
        for j in range(N):
            # Phase accumulated: e^(2*pi*i * phase * j)
            angle = 2.0 * math.pi * phase * j
            amplitudes.append(complex(math.cos(angle), math.sin(angle)) / math.sqrt(N))
        
        return amplitudes
    
    def estimate(self, phase: float) -> float:
        """
        Estimate phase using QPE.
        
        Args:
            phase: True phase (0 to 1)
        
        Returns:
            Estimated phase
        """
        # Simulate phase register after controlled-U
        state = self.controlled_u_sequence(phase)
        
        # Apply inverse QFT
        measured = self.qft.inverse(state)
        
        # Measure: find most likely outcome
        max_prob = -1.0
        best_j = 0
        
        for j, amp in enumerate(measured):
            prob = abs(amp)**2
            if prob > max_prob:
                max_prob = prob
                best_j = j
        
        # Convert to phase estimate
        return best_j / (2**self.t)
    
    def precision(self) -> float:
        """
        Get phase estimation precision.
        
        Returns:
            Precision (delta_phi)
        """
        return 1.0 / (2**self.t)
    
    def success_probability(self, phase: float) -> float:
        """
        Compute success probability.
        
        Args:
            phase: True phase
        
        Returns:
            Probability of correct estimation
        """
        # For ideal QPE, success probability depends on how close
        # phase is to a binary fraction
        estimated = self.estimate(phase)
        error = abs(estimated - phase)
        
        # Success if within half precision
        return 1.0 if error <= self.precision() / 2 else 0.0


class EigenvalueEstimator:
    """
    Estimate eigenvalues using QPE.
    """
    
    def __init__(self, num_qubits: int = 3):
        self.qpe = PhaseEstimator(num_qubits)
    
    def estimate_eigenvalue(self, unitary_phase: float,
                           eigenvalue_scale: float = 1.0) -> float:
        """
        Estimate eigenvalue from phase.
        
        Args:
            unitary_phase: Phase of eigenvalue (phi where U|psi> = e^(2*pi*i*phi)|psi>)
            eigenvalue_scale: Scale factor
        
        Returns:
            Estimated eigenvalue
        """
        phase = self.qpe.estimate(unitary_phase)
        return phase * eigenvalue_scale
    
    def energy_estimate(self, phase: float,
                       time_evolution: float = 1.0) -> float:
        """
        Estimate energy from phase (E = -hbar * phi / t).
        
        Args:
            phase: Estimated phase
            time_evolution: Evolution time
        
        Returns:
            Energy estimate
        """
        if time_evolution <= 0:
            return 0.0
        return -2.0 * math.pi * phase / time_evolution


class ControlledUnitary:
    """
    Controlled unitary operation.
    """
    
    def __init__(self, unitary_matrix: Optional[List[List[complex]]] = None):
        """
        Args:
            unitary_matrix: 2x2 unitary matrix
        """
        if unitary_matrix is None:
            # Default: Z-rotation
            unitary_matrix = [[1, 0], [0, -1]]
        self.U = unitary_matrix
    
    def apply_power(self, power: int, state: List[complex]) -> List[complex]:
        """
        Apply U^k to state.
        
        Args:
            power: Power k
            state: Input state
        
        Returns:
            Output state
        """
        # For diagonal U, U^k is just powers of diagonal elements
        result = []
        for i, amp in enumerate(state):
            if i < len(self.U):
                phase = self.U[i][i] ** power
                result.append(amp * phase)
            else:
                result.append(amp)
        
        return result
    
    def phase_from_unitary(self) -> float:
        """
        Extract phase from unitary.
        
        Returns:
            Phase (0 to 1)
        """
        # For diagonal U = diag(e^(2*pi*i*phi), ...)
        if self.U and len(self.U) > 0:
            eigenval = self.U[0][0]
            if abs(eigenval) > 0:
                # phi = arg(eigenval) / (2*pi)
                phi = math.atan2(eigenval.imag, eigenval.real) / (2.0 * math.pi)
                return phi % 1.0
        return 0.0


class QuantumPhaseEstimation:
    """
    Unified quantum phase estimation controller.
    """
    
    def __init__(self, num_qubits: int = 3):
        self.qpe = PhaseEstimator(num_qubits)
        self.eigenvalue = EigenvalueEstimator(num_qubits)
        self.qft = QuantumFourierTransform(num_qubits)
        self.history: List[Dict] = []
    
    def estimate(self, true_phase: float) -> Dict:
        """
        Perform phase estimation.
        
        Args:
            true_phase: True phase value
        
        Returns:
            Result dictionary
        """
        estimated = self.qpe.estimate(true_phase)
        precision = self.qpe.precision()
        error = abs(estimated - true_phase)
        
        result = {
            "true_phase": true_phase,
            "estimated_phase": estimated,
            "precision": precision,
            "error": error,
            "success": error <= precision / 2
        }
        
        self.history.append(result)
        return result
    
    def estimate_energy(self, hamiltonian_phase: float,
                       evolution_time: float = 1.0) -> float:
        """
        Estimate energy eigenvalue.
        
        Args:
            hamiltonian_phase: Phase from time evolution
            evolution_time: Time evolution parameter
        
        Returns:
            Energy estimate
        """
        return self.eigenvalue.energy_estimate(hamiltonian_phase, evolution_time)
    
    def qpe_summary(self) -> Dict:
        """Get QPE summary."""
        if not self.history:
            return {"status": "not_run"}
        
        avg_error = sum(h["error"] for h in self.history) / len(self.history)
        success_rate = sum(1 for h in self.history if h["success"]) / len(self.history)
        
        return {
            "runs": len(self.history),
            "precision_qubits": self.qpe.t,
            "precision": self.qpe.precision(),
            "avg_error": avg_error,
            "success_rate": success_rate
        }
