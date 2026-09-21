"""
Quantum Metrology Module
Phase estimation, quantum sensing,
Fisher information, quantum Cramer-Rao bound, and parameter estimation for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EstimationResult:
    """Parameter estimation result."""
    estimated_value: float
    uncertainty: float
    fisher_information: float


class PhaseEstimator:
    """
    Quantum phase estimation.
    """
    
    def __init__(self, num_qubits: int = 3):
        """
        Args:
            num_qubits: Number of qubits in estimation register
        """
        self.num_qubits = num_qubits
    
    def estimate_phase(self, true_phase: float,
                      num_measurements: int = 100) -> EstimationResult:
        """
        Estimate phase using quantum measurements.
        
        Args:
            true_phase: True phase value
            num_measurements: Number of measurements
        
        Returns:
            Estimation result
        """
        # Simulate phase estimation
        # Measurement probabilities: P(0) = cos^2(phase/2), P(1) = sin^2(phase/2)
        p0 = math.cos(true_phase / 2.0) ** 2
        
        counts_0 = sum(1 for _ in range(num_measurements)
                      if __import__('random').random() < p0)
        p0_est = counts_0 / num_measurements
        
        # Estimate phase from p0
        p0_est = max(0.001, min(0.999, p0_est))
        estimated_phase = 2.0 * math.acos(math.sqrt(p0_est))
        
        # Fisher information for phase estimation
        FI = num_measurements  # Simplified: scales with N
        
        # Uncertainty from quantum Cramer-Rao bound
        uncertainty = 1.0 / math.sqrt(FI)
        
        return EstimationResult(estimated_phase, uncertainty, FI)
    
    def precision_scaling(self, num_qubits: int) -> float:
        """
        Compute Heisenberg scaling precision.
        
        Args:
            num_qubits: Number of qubits
        
        Returns:
            Precision (1/N)
        """
        return 1.0 / (2.0 ** num_qubits)


class QuantumFisherInformation:
    """
    Quantum Fisher information calculations.
    """
    
    def __init__(self):
        pass
    
    def qfi_pure_state(self, state_derivative: List[complex],
                      state: List[complex]) -> float:
        """
        Compute QFI for pure states.
        
        Args:
            state_derivative: d|psi>/dtheta
            state: |psi>
        
        Returns:
            Quantum Fisher information
        """
        # F_Q = 4 * (<dpsi|dpsi> - |<dpsi|psi>|^2)
        norm_dpsi = sum(abs(d) ** 2 for d in state_derivative)
        overlap = sum((d.conjugate() * s).real
                     for d, s in zip(state_derivative, state))
        
        return 4.0 * (norm_dpsi - overlap ** 2)
    
    def qfi_ghz_state(self, num_qubits: int) -> float:
        """
        QFI for GHZ state.
        
        Args:
            num_qubits: Number of qubits
        
        Returns:
            QFI
        """
        return float(num_qubits ** 2)
    
    def qfi_product_state(self, num_qubits: int) -> float:
        """
        QFI for product state (standard quantum limit).
        
        Args:
            num_qubits: Number of qubits
        
        Returns:
            QFI
        """
        return float(num_qubits)


class QuantumSensor:
    """
    Quantum sensing and parameter estimation.
    """
    
    def __init__(self):
        pass
    
    def frequency_estimation(self, measurement_time_s: float,
                            signal_to_noise_dB: float) -> float:
        """
        Estimate frequency resolution.
        
        Args:
            measurement_time_s: Measurement time
            signal_to_noise_dB: SNR in dB
        
        Returns:
            Frequency uncertainty in Hz
        """
        if measurement_time_s <= 0:
            return float('inf')
        snr_linear = 10.0 ** (signal_to_noise_dB / 10.0)
        return 1.0 / (2.0 * math.pi * measurement_time_s * math.sqrt(snr_linear))
    
    def magnetic_field_sensitivity(self, gyromagnetic_ratio_MHz_T: float,
                                  coherence_time_s: float,
                                  num_ions: int = 1) -> float:
        """
        Compute magnetic field sensitivity.
        
        Args:
            gyromagnetic_ratio_MHz_T: Gyromagnetic ratio
            coherence_time_s: Coherence time
            num_ions: Number of ions
        
        Returns:
            Sensitivity in T/sqrt(Hz)
        """
        if coherence_time_s <= 0 or gyromagnetic_ratio_MHz_T <= 0:
            return float('inf')
        gamma = gyromagnetic_ratio_MHz_T * 2.0 * math.pi * 1e6
        return 1.0 / (gamma * math.sqrt(num_ions * coherence_time_s))
    
    def gravimetry_sensitivity(self, atom_interrogation_time_s: float,
                              wavevector_m: float = 1.0e10) -> float:
        """
        Atom interferometer gravity sensitivity.
        
        Args:
            atom_interrogation_time_s: Interrogation time
            wavevector_m: Wavevector
        
        Returns:
            Sensitivity in m/s^2/sqrt(Hz)
        """
        if atom_interrogation_time_s <= 0:
            return float('inf')
        return 1.0 / (wavevector_m * atom_interrogation_time_s ** 2)


class QuantumMetrology:
    """
    Unified quantum metrology controller.
    """
    
    def __init__(self):
        self.phase = PhaseEstimator()
        self.qfi = QuantumFisherInformation()
        self.sensor = QuantumSensor()
    
    def metrology_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["phase_estimation", "fisher_information", "quantum_sensing"],
            "sensors": ["frequency", "magnetic_field", "gravimetry"],
            "scaling": ["heisenberg", "standard_quantum_limit"]
        }
