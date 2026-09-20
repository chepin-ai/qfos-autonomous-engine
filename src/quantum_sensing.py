"""
Quantum Sensing Module
Quantum metrology, phase estimation, quantum-enhanced
measurement, and precision bounds for autonomous sensing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumProbe:
    """Quantum probe state."""
    amplitudes: List[complex]
    num_qubits: int


class PhaseEstimator:
    """
    Quantum phase estimation.
    """
    
    def __init__(self):
        pass
    
    def estimate(self, measurements: List[int],
                precision_bits: int = 3) -> float:
        """
        Estimate phase from measurements.
        
        Args:
            measurements: Measurement outcomes
            precision_bits: Precision
        
        Returns:
            Phase estimate
        """
        if not measurements:
            return 0.0
        
        # Convert measurements to phase
        n = len(measurements)
        phase = sum(m * (2 ** i) for i, m in enumerate(reversed(measurements)))
        return 2.0 * math.pi * phase / (2 ** n)
    
    def precision(self, num_qubits: int) -> float:
        """
        Compute phase precision.
        
        Args:
            num_qubits: Qubits
        
        Returns:
            Precision (rad)
        """
        return 2.0 * math.pi / (2 ** num_qubits)


class QuantumMetrology:
    """
    Quantum-enhanced metrology.
    """
    
    def __init__(self):
        pass
    
    def shot_noise_limit(self, n: int) -> float:
        """
        Standard quantum limit (shot noise).
        
        Args:
            n: Number of probes
        
        Returns:
            Variance
        """
        return 1.0 / n if n > 0 else float('inf')
    
    def heisenberg_limit(self, n: int) -> float:
        """
        Heisenberg limit.
        
        Args:
            n: Number of probes
        
        Returns:
            Variance
        """
        return 1.0 / (n ** 2) if n > 0 else float('inf')
    
    def optimal_probe(self, num_qubits: int) -> QuantumProbe:
        """
        Create optimal probe (GHZ state).
        
        Args:
            num_qubits: Qubits
        
        Returns:
            Probe
        """
        dim = 2 ** num_qubits
        amplitudes = [0.0] * dim
        amplitudes[0] = 1.0 / math.sqrt(2.0)
        amplitudes[dim - 1] = 1.0 / math.sqrt(2.0)
        
        return QuantumProbe(amplitudes, num_qubits)


class QuantumEnhancedMeasurement:
    """
    Quantum-enhanced measurement.
    """
    
    def __init__(self):
        pass
    
    def squeezed_state_precision(self, squeezing_db: float,
                                 n: int) -> float:
        """
        Precision with squeezed states.
        
        Args:
            squeezing_db: Squeezing in dB
            n: Probes
        
        Returns:
            Variance
        """
        r = squeezing_db / (20.0 * math.log10(math.e))
        return math.exp(-2.0 * r) / n if n > 0 else float('inf')
    
    def entangled_state_precision(self, n: int) -> float:
        """
        Precision with entangled states.
        
        Args:
            n: Probes
        
        Returns:
            Variance
        """
        return 1.0 / (n ** 2) if n > 0 else float('inf')


class CramerRaoBound:
    """
    Cramer-Rao bound for quantum sensing.
    """
    
    def __init__(self):
        pass
    
    def classical_bound(self, fisher_information: float) -> float:
        """
        Classical Cramer-Rao bound.
        
        Args:
            fisher_information: Fisher information
        
        Returns:
            Bound
        """
        return 1.0 / fisher_information if fisher_information > 0 else float('inf')
    
    def quantum_bound(self, quantum_fisher_information: float) -> float:
        """
        Quantum Cramer-Rao bound.
        
        Args:
            quantum_fisher_information: Quantum Fisher information
        
        Returns:
            Bound
        """
        return 1.0 / quantum_fisher_information if quantum_fisher_information > 0 else float('inf')


class QuantumSensing:
    """
    Unified quantum sensing controller.
    """
    
    def __init__(self):
        self.phase = PhaseEstimator()
        self.metrology = QuantumMetrology()
        self.enhanced = QuantumEnhancedMeasurement()
        self.crb = CramerRaoBound()
        self.measurements: List[int] = []
    
    def add_measurement(self, outcome: int):
        """
        Add measurement.
        
        Args:
            outcome: Outcome
        """
        self.measurements.append(outcome)
    
    def estimate_phase(self) -> float:
        """
        Estimate phase.
        
        Returns:
            Phase
        """
        return self.phase.estimate(self.measurements)
    
    def sensing_precision(self, n_probes: int,
                         use_entanglement: bool = False) -> float:
        """
        Compute sensing precision.
        
        Args:
            n_probes: Probes
            use_entanglement: Use entanglement
        
        Returns:
            Variance
        """
        if use_entanglement:
            return self.metrology.heisenberg_limit(n_probes)
        return self.metrology.shot_noise_limit(n_probes)
    
    def qs_summary(self) -> Dict:
        """Get summary."""
        return {
            "measurements": len(self.measurements),
            "phase_estimate": self.estimate_phase(),
            "shot_noise": self.metrology.shot_noise_limit(len(self.measurements))
        }
