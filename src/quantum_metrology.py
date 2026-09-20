"""
Quantum Metrology Module
Quantum-enhanced parameter estimation, phase sensing, Ramsey
interferometry, and quantum Fisher information for autonomous
high-precision measurement.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class QuantumPhaseSensor:
    """
    Quantum phase estimation via interferometry.
    """
    
    def __init__(self, num_qubits: int = 2):
        """
        Args:
            num_qubits: Qubits
        """
        self.n = num_qubits
    
    def prepare_ghz(self) -> List[complex]:
        """
        Prepare GHZ state.
        
        Returns:
            GHZ state
        """
        dim = 2 ** self.n
        state = [complex(0.0, 0.0)] * dim
        state[0] = complex(1.0 / math.sqrt(2), 0.0)
        state[dim - 1] = complex(1.0 / math.sqrt(2), 0.0)
        return state
    
    def apply_phase(self, state: List[complex],
                   phi: float) -> List[complex]:
        """
        Apply phase to state.
        
        Args:
            state: State
            phi: Phase
        
        Returns:
            State with phase
        """
        return [z * complex(math.cos(phi), math.sin(phi)) for z in state]
    
    def measure(self, state: List[complex]) -> float:
        """
        Measure expectation of Pauli-X.
        
        Args:
            state: State
        
        Returns:
            Expectation value
        """
        # <X> = Re(<0|X|psi>) simplified
        return sum(abs(z) ** 2 * (1 if i % 2 == 0 else -1)
                   for i, z in enumerate(state))
    
    def estimate_phase(self, state: List[complex]) -> float:
        """
        Estimate phase from measurement.
        
        Args:
            state: State
        
        Returns:
            Estimated phase
        """
        expectation = self.measure(state)
        # cos(n*phi) ~ expectation
        if abs(expectation) > 1.0:
            expectation = 1.0 if expectation > 0 else -1.0
        return math.acos(expectation) / self.n


class RamseyInterferometer:
    """
    Ramsey interferometry for frequency estimation.
    """
    
    def __init__(self):
        self.pi_half_pulse = math.pi / 2
        self.wait_time = 1.0
    
    def ramsey_sequence(self, detuning: float,
                       wait_time: float = 1.0) -> float:
        """
        Simulate Ramsey sequence.
        
        Args:
            detuning: Frequency detuning
            wait_time: Wait time
        
        Returns:
            Probability of |1>
        """
        # P(1) = 0.5 * (1 - cos(detuning * wait_time))
        return 0.5 * (1.0 - math.cos(detuning * wait_time))
    
    def estimate_detuning(self, probability: float,
                         wait_time: float = 1.0) -> float:
        """
        Estimate detuning.
        
        Args:
            probability: P(1)
            wait_time: Wait time
        
        Returns:
            Detuning
        """
        if wait_time <= 0:
            return 0.0
        
        cos_term = 1.0 - 2.0 * probability
        if abs(cos_term) > 1.0:
            cos_term = 1.0 if cos_term > 0 else -1.0
        
        return math.acos(cos_term) / wait_time
    
    def sensitivity(self, wait_time: float,
                   num_measurements: int = 1) -> float:
        """
        Compute sensitivity.
        
        Args:
            wait_time: Wait time
            num_measurements: Measurements
        
        Returns:
            Sensitivity
        """
        if wait_time <= 0 or num_measurements <= 0:
            return float('inf')
        return 1.0 / (wait_time * math.sqrt(num_measurements))


class QuantumFisherInfo:
    """
    Quantum Fisher information calculations.
    """
    
    def __init__(self):
        pass
    
    def pure_state_qfi(self, state_derivative: List[complex],
                      state: List[complex]) -> float:
        """
        QFI for pure state.
        
        Args:
            state_derivative: d|psi>/dtheta
            state: |psi>
        
        Returns:
            QFI
        """
        # F = 4 * (<dpsi|dpsi> - |<dpsi|psi>|^2)
        dpsi_dpsi = sum(abs(z)**2 for z in state_derivative)
        dpsi_psi = sum(z1.conjugate() * z2
                       for z1, z2 in zip(state_derivative, state))
        
        return 4.0 * (dpsi_dpsi - abs(dpsi_psi)**2)
    
    def ghz_qfi(self, num_qubits: int) -> float:
        """
        QFI for GHZ state.
        
        Args:
            num_qubits: Qubits
        
        Returns:
            QFI
        """
        return float(num_qubits ** 2)
    
    def coherent_state_qfi(self, num_qubits: int) -> float:
        """
        QFI for coherent (separable) state.
        
        Args:
            num_qubits: Qubits
        
        Returns:
            QFI
        """
        return float(num_qubits)
    
    def quantum_advantage(self, num_qubits: int) -> float:
        """
        Compute quantum advantage.
        
        Args:
            num_qubits: Qubits
        
        Returns:
            Advantage ratio
        """
        if num_qubits <= 0:
            return 1.0
        return self.ghz_qfi(num_qubits) / self.coherent_state_qfi(num_qubits)


class QuantumMetrology:
    """
    Unified quantum metrology controller.
    """
    
    def __init__(self):
        self.phase_sensor: Optional[QuantumPhaseSensor] = None
        self.ramsey = RamseyInterferometer()
        self.qfi = QuantumFisherInfo()
        self.results: List[Dict] = []
    
    def setup_phase_sensor(self, num_qubits: int = 2):
        """
        Setup phase sensor.
        
        Args:
            num_qubits: Qubits
        """
        self.phase_sensor = QuantumPhaseSensor(num_qubits)
    
    def measure_phase(self, true_phase: float) -> Dict:
        """
        Measure phase.
        
        Args:
            true_phase: True phase
        
        Returns:
            Result
        """
        if self.phase_sensor is None:
            self.setup_phase_sensor()
        
        state = self.phase_sensor.prepare_ghz()
        state = self.phase_sensor.apply_phase(state, true_phase)
        estimated = self.phase_sensor.estimate_phase(state)
        
        result = {
            "true_phase": true_phase,
            "estimated_phase": estimated,
            "error": abs(estimated - true_phase)
        }
        self.results.append(result)
        return result
    
    def ramsey_measurement(self, detuning: float,
                          wait_time: float = 1.0) -> Dict:
        """
        Perform Ramsey measurement.
        
        Args:
            detuning: Detuning
            wait_time: Wait time
        
        Returns:
            Result
        """
        prob = self.ramsey.ramsey_sequence(detuning, wait_time)
        estimated = self.ramsey.estimate_detuning(prob, wait_time)
        sensitivity = self.ramsey.sensitivity(wait_time)
        
        return {
            "detuning": detuning,
            "probability": prob,
            "estimated_detuning": estimated,
            "sensitivity": sensitivity
        }
    
    def compute_qfi(self, num_qubits: int) -> Dict:
        """
        Compute QFI metrics.
        
        Args:
            num_qubits: Qubits
        
        Returns:
            Metrics
        """
        return {
            "ghz_qfi": self.qfi.ghz_qfi(num_qubits),
            "coherent_qfi": self.qfi.coherent_state_qfi(num_qubits),
            "advantage": self.qfi.quantum_advantage(num_qubits)
        }
    
    def metrology_summary(self) -> Dict:
        """Get summary."""
        return {
            "measurements": len(self.results),
            "avg_error": sum(r["error"] for r in self.results) / max(len(self.results), 1),
            "qfi_available": True
        }
