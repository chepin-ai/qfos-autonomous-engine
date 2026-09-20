"""
Quantum Phase Estimation Module
Eigenphase estimation with inverse QFT,
controlled unitary operations, and binary fraction decoding.
"""

import math
import cmath
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class InverseQFT:
    """
    Inverse Quantum Fourier Transform.
    """
    
    def __init__(self, num_qubits: int = 3):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
    
    def apply(self, state: List[complex]) -> List[complex]:
        """
        Apply inverse QFT.
        
        Args:
            state: Input state
        
        Returns:
            Transformed state
        """
        N = 2 ** self.n
        result = [complex(0.0, 0.0)] * N
        
        for k in range(N):
            for j in range(N):
                angle = -2.0 * math.pi * j * k / N
                result[k] += state[j] * complex(math.cos(angle), math.sin(angle))
        
        # Normalize
        norm = sum(abs(z)**2 for z in result) ** 0.5
        if norm > 0:
            result = [z / norm for z in result]
        
        return result


class ControlledUnitary:
    """
    Controlled unitary operation for QPE.
    """
    
    def __init__(self, phase: float):
        """
        Args:
            phase: Phase to estimate
        """
        self.phase = phase
    
    def apply_power(self, power: int) -> List[List[complex]]:
        """
        Generate U^(2^power) matrix.
        
        Args:
            power: Power
        
        Returns:
            Unitary matrix
        """
        angle = self.phase * (2 ** power)
        return [[complex(math.cos(angle), -math.sin(angle)), complex(0.0, 0.0)],
                [complex(0.0, 0.0), complex(math.cos(angle), math.sin(angle))]]
    
    def apply_to_state(self, state: List[complex], power: int) -> List[complex]:
        """
        Apply U^(2^power) to state.
        
        Args:
            state: State
            power: Power
        
        Returns:
            Result
        """
        U = self.apply_power(power)
        return [sum(U[i][j] * state[j] for j in range(len(state))) for i in range(len(U))]


class PhaseEstimator:
    """
    Quantum phase estimation algorithm.
    """
    
    def __init__(self, precision_bits: int = 3):
        """
        Args:
            precision_bits: Number of precision qubits
        """
        self.n = precision_bits
        self.iqft = InverseQFT(precision_bits)
        self.results: List[Dict] = []
    
    def binary_fraction(self, measurement: int) -> float:
        """
        Convert measurement to phase fraction.
        
        Args:
            measurement: Measured integer
        
        Returns:
            Phase estimate
        """
        return measurement / (2 ** self.n)
    
    def estimate(self, phase: float,
                shots: int = 100) -> Dict:
        """
        Estimate phase using QPE.
        
        Args:
            phase: True phase
            shots: Number of shots
        
        Returns:
            Result
        """
        N = 2 ** self.n
        cu = ControlledUnitary(phase)
        
        # Simulate QPE
        counts = [0] * N
        
        for _ in range(shots):
            # Initialize counting register in superposition
            state = [complex(1.0 / math.sqrt(N), 0.0)] * N
            
            # Apply controlled-U operations
            for i in range(self.n):
                power = self.n - 1 - i
                phase_factor = cmath.exp(1j * phase * (2 ** power))
                # Apply phase kickback (simplified)
                for j in range(N):
                    if (j >> i) & 1:
                        state[j] *= phase_factor
            
            # Apply inverse QFT
            state = self.iqft.apply(state)
            
            # Measure
            probs = [abs(z)**2 for z in state]
            measurement = self._sample(probs)
            counts[measurement] += 1
        
        # Find most likely outcome
        max_count = max(counts)
        best_measurement = counts.index(max_count)
        estimated_phase = self.binary_fraction(best_measurement)
        
        # Handle 2*pi periodicity
        estimated_phase = estimated_phase % (2.0 * math.pi)
        
        result = {
            "true_phase": phase,
            "estimated_phase": estimated_phase,
            "measurement": best_measurement,
            "counts": counts,
            "error": abs(phase - estimated_phase),
            "success_probability": max_count / shots
        }
        self.results.append(result)
        return result
    
    def _sample(self, probabilities: List[float]) -> int:
        """
        Sample from probability distribution.
        
        Args:
            probabilities: Probabilities
        
        Returns:
            Sampled index
        """
        import random
        r = random.random()
        cumsum = 0.0
        for i, p in enumerate(probabilities):
            cumsum += p
            if r <= cumsum:
                return i
        return len(probabilities) - 1
    
    def precision(self) -> float:
        """
        Compute theoretical precision.
        
        Returns:
            Precision
        """
        return 2.0 * math.pi / (2 ** self.n)


class QuantumPhaseEstimation:
    """
    Unified quantum phase estimation controller.
    """
    
    def __init__(self):
        self.estimator: Optional[PhaseEstimator] = None
        self.history: List[Dict] = []
    
    def setup(self, precision_bits: int = 3):
        """
        Setup estimator.
        
        Args:
            precision_bits: Precision
        """
        self.estimator = PhaseEstimator(precision_bits)
    
    def estimate(self, phase: float, shots: int = 100) -> Dict:
        """
        Estimate phase.
        
        Args:
            phase: Phase
            shots: Shots
        
        Returns:
            Result
        """
        if self.estimator is None:
            self.setup(3)
        
        result = self.estimator.estimate(phase, shots)
        self.history.append(result)
        return result
    
    def qpe_summary(self) -> Dict:
        """Get summary."""
        if not self.history:
            return {"status": "no_data"}
        
        avg_error = sum(r["error"] for r in self.history) / len(self.history)
        
        return {
            "runs": len(self.history),
            "precision_bits": self.estimator.n if self.estimator else 0,
            "theoretical_precision": self.estimator.precision() if self.estimator else 0.0,
            "average_error": avg_error
        }
