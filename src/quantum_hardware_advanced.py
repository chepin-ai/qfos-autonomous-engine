"""
Quantum Hardware Advanced Module
Superconducting qubits, transmon Hamiltonian,
coupling strengths, and gate calibration for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QubitParams:
    """Superconducting qubit parameters."""
    frequency_GHz: float
    anharmonicity_MHz: float
    T1_us: float
    T2_us: float


class TransmonQubit:
    """
    Transmon qubit physics.
    """
    
    def __init__(self, EJ_GHz: float = 15.0,
                 EC_GHz: float = 0.3):
        """
        Args:
            EJ_GHz: Josephson energy
            EC_GHz: Charging energy
        """
        self.EJ = EJ_GHz
        self.EC = EC_GHz
    
    def qubit_frequency(self) -> float:
        """
        Compute transmon frequency.
        
        Returns:
            Frequency (GHz)
        """
        return math.sqrt(8.0 * self.EJ * self.EC) - self.EC
    
    def anharmonicity(self) -> float:
        """
        Compute anharmonicity.
        
        Returns:
            Anharmonicity (GHz)
        """
        return -self.EC
    
    def charge_dispersion(self, n_g: float = 0.0) -> float:
        """
        Compute charge dispersion.
        
        Args:
            n_g: Gate charge
        
        Returns:
            Dispersion (GHz)
        """
        ratio = self.EJ / self.EC
        return math.exp(-math.sqrt(8.0 * ratio)) * self.EC * math.cos(2.0 * math.pi * n_g)


class CouplingStrength:
    """
    Qubit-qubit coupling analysis.
    """
    
    def __init__(self):
        pass
    
    def capacitive_coupling(self, C_coupling_fF: float,
                           C_qubit_fF: float = 100.0) -> float:
        """
        Compute capacitive coupling strength.
        
        Args:
            C_coupling_fF: Coupling capacitance
            C_qubit_fF: Qubit capacitance
        
        Returns:
            g / 2pi (MHz)
        """
        if C_qubit_fF <= 0:
            return 0.0
        # Simplified: g ~ C_c / C_q * frequency
        return 5.0 * C_coupling_fF / C_qubit_fF
    
    def swap_time(self, coupling_MHz: float) -> float:
        """
        Compute iSWAP gate time.
        
        Args:
            coupling_MHz: Coupling strength
        
        Returns:
            Swap time (ns)
        """
        if coupling_MHz <= 0:
            return 0.0
        return 1e3 / (2.0 * coupling_MHz)


class GateCalibration:
    """
    Single-qubit gate calibration.
    """
    
    def __init__(self):
        pass
    
    def rabi_frequency(self, drive_amplitude: float,
                      coupling_strength_MHz: float = 100.0) -> float:
        """
        Compute Rabi frequency.
        
        Args:
            drive_amplitude: Normalized drive amplitude
            coupling_strength_MHz: Qubit-drive coupling
        
        Returns:
            Rabi frequency (MHz)
        """
        return drive_amplitude * coupling_strength_MHz
    
    def pi_pulse_duration(self, rabi_MHz: float) -> float:
        """
        Compute pi pulse duration.
        
        Args:
            rabi_MHz: Rabi frequency
        
        Returns:
            Pi pulse duration (ns)
        """
        if rabi_MHz <= 0:
            return 0.0
        return 500.0 / rabi_MHz  # 0.5 / (rabi/1e3) in ns
    
    def gate_fidelity(self, coherence_time_us: float,
                     gate_time_ns: float) -> float:
        """
        Estimate gate fidelity from coherence.
        
        Args:
            coherence_time_us: T2 time
            gate_time_ns: Gate duration
        
        Returns:
            Fidelity
        """
        if coherence_time_us <= 0:
            return 0.0
        # Simplified: exponential decay
        return math.exp(-gate_time_ns / (coherence_time_us * 1e3))


class ReadoutResonator:
    """
    Dispersive readout resonator.
    """
    
    def __init__(self, frequency_GHz: float = 7.0,
                 kappa_MHz: float = 1.0):
        """
        Args:
            frequency_GHz: Resonator frequency
            kappa_MHz: Linewidth
        """
        self.freq = frequency_GHz
        self.kappa = kappa_MHz
    
    def dispersive_shift(self, g_MHz: float,
                        delta_MHz: float) -> float:
        """
        Compute dispersive shift.
        
        Args:
            g_MHz: Coupling
            delta_MHz: Qubit-resonator detuning
        
        Returns:
            Chi (MHz)
        """
        if delta_MHz == 0:
            return 0.0
        return g_MHz**2 / delta_MHz
    
    def measurement_time(self, snr_threshold: float = 5.0) -> float:
        """
        Estimate measurement time.
        
        Args:
            snr_threshold: SNR threshold
        
        Returns:
            Time (ns)
        """
        if self.kappa <= 0:
            return 0.0
        return snr_threshold * 1e3 / self.kappa


class QuantumHardwareAdvanced:
    """
    Unified advanced quantum hardware controller.
    """
    
    def __init__(self):
        self.transmon = TransmonQubit()
        self.coupling = CouplingStrength()
        self.calibration = GateCalibration()
        self.readout = ReadoutResonator()
    
    def hardware_summary(self) -> Dict:
        """Get summary."""
        return {
            "components": ["transmon", "coupling", "calibration", "readout"],
            "metrics": ["T1", "T2", "gate_fidelity", "readout_fidelity"]
        }
