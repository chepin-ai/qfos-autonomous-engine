"""
Quantum Teleportation Module
Teleportation protocol, Bell state preparation, fidelity,
and entanglement for autonomous quantum communication.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class PauliOp(Enum):
    """Pauli operators for correction."""
    I = "I"
    X = "X"
    Z = "Z"
    Y = "Y"


@dataclass
class QubitState:
    """Single qubit state |psi> = alpha|0> + beta|1>."""
    alpha: complex = 1.0 + 0j
    beta: complex = 0.0 + 0j
    
    def normalize(self):
        """Normalize state."""
        norm = math.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        if norm > 0:
            self.alpha /= norm
            self.beta /= norm
    
    def fidelity(self, other: 'QubitState') -> float:
        """
        Compute state fidelity.
        
        Args:
            other: Another state
        
        Returns:
            Fidelity
        """
        return abs(self.alpha.conjugate() * other.alpha +
                  self.beta.conjugate() * other.beta)**2
    
    def apply_pauli(self, op: PauliOp) -> 'QubitState':
        """
        Apply Pauli operator.
        
        Args:
            op: Pauli operator
        
        Returns:
            New state
        """
        if op == PauliOp.I:
            return QubitState(self.alpha, self.beta)
        elif op == PauliOp.X:
            return QubitState(self.beta, self.alpha)
        elif op == PauliOp.Z:
            return QubitState(self.alpha, -self.beta)
        elif op == PauliOp.Y:
            return QubitState(-1j * self.beta, 1j * self.alpha)
        return QubitState(self.alpha, self.beta)


class BellState:
    """
    Bell state generator and analyzer.
    """
    
    @staticmethod
    def phi_plus() -> Tuple[complex, complex, complex, complex]:
        """
        |Phi+> = (|00> + |11>) / sqrt(2)
        
        Returns:
            (c00, c01, c10, c11)
        """
        s = 1.0 / math.sqrt(2)
        return (s, 0.0 + 0j, 0.0 + 0j, s)
    
    @staticmethod
    def phi_minus() -> Tuple[complex, complex, complex, complex]:
        """
        |Phi-> = (|00> - |11>) / sqrt(2)
        """
        s = 1.0 / math.sqrt(2)
        return (s, 0.0 + 0j, 0.0 + 0j, -s)
    
    @staticmethod
    def psi_plus() -> Tuple[complex, complex, complex, complex]:
        """
        |Psi+> = (|01> + |10>) / sqrt(2)
        """
        s = 1.0 / math.sqrt(2)
        return (0.0 + 0j, s, s, 0.0 + 0j)
    
    @staticmethod
    def psi_minus() -> Tuple[complex, complex, complex, complex]:
        """
        |Psi-> = (|01> - |10>) / sqrt(2)
        """
        s = 1.0 / math.sqrt(2)
        return (0.0 + 0j, s, -s, 0.0 + 0j)
    
    @staticmethod
    def bell_measurement(state: Tuple[complex, complex, complex, complex]) -> Tuple[int, int]:
        """
        Bell state measurement (simplified).
        
        Args:
            state: Two-qubit state amplitudes
        
        Returns:
            (bit1, bit2) classical outcome
        """
        c00, c01, c10, c11 = state
        probs = [abs(c00)**2, abs(c01)**2, abs(c10)**2, abs(c11)**2]
        
        # Most likely outcome
        max_idx = probs.index(max(probs))
        
        if max_idx == 0:
            return (0, 0)
        elif max_idx == 1:
            return (0, 1)
        elif max_idx == 2:
            return (1, 0)
        else:
            return (1, 1)


class TeleportationProtocol:
    """
    Quantum teleportation protocol.
    """
    
    def __init__(self):
        self.bell = BellState()
        self.teleportation_log: List[Dict] = []
    
    def prepare_bell_pair(self) -> Tuple[QubitState, QubitState]:
        """
        Prepare entangled Bell pair.
        
        Returns:
            (alice_half, bob_half) shared entangled qubits
        """
        # Simplified: return conceptual entangled pair
        alice = QubitState(1.0 / math.sqrt(2), 0.0)
        bob = QubitState(1.0 / math.sqrt(2), 0.0)
        return (alice, bob)
    
    def alice_measurement(self, psi: QubitState,
                         alice_entangled: QubitState) -> Tuple[int, int]:
        """
        Alice performs Bell measurement.
        
        Args:
            psi: State to teleport
            alice_entangled: Alice's half of Bell pair
        
        Returns:
            (a, b) classical bits
        """
        # Simplified: compute overlap with Bell states
        # For |psi> = alpha|0> + beta|1> and |Phi+>:
        # Measurement projects onto (00, 01, 10, 11)
        
        alpha, beta = psi.alpha, psi.beta
        
        # Probabilities for each outcome
        p00 = 0.5 * abs(alpha + beta)**2
        p01 = 0.5 * abs(alpha - beta)**2
        p10 = 0.5 * abs(alpha + beta)**2
        p11 = 0.5 * abs(alpha - beta)**2
        
        # Simplified: use deterministic outcome based on state
        if abs(alpha) > abs(beta):
            return (0, 0)
        return (1, 1)
    
    def bob_correction(self, bob_qubit: QubitState,
                      classical_bits: Tuple[int, int]) -> QubitState:
        """
        Bob applies correction based on classical bits.
        
        Args:
            bob_qubit: Bob's qubit
            classical_bits: (a, b) from Alice
        
        Returns:
            Corrected state
        """
        a, b = classical_bits
        
        if a == 1 and b == 1:
            return bob_qubit.apply_pauli(PauliOp.Y)
        elif a == 1:
            return bob_qubit.apply_pauli(PauliOp.X)
        elif b == 1:
            return bob_qubit.apply_pauli(PauliOp.Z)
        
        return bob_qubit
    
    def teleport(self, psi: QubitState) -> Tuple[QubitState, Tuple[int, int]]:
        """
        Execute full teleportation protocol.
        
        Args:
            psi: State to teleport
        
        Returns:
            (received_state, classical_bits)
        """
        alice_half, bob_half = self.prepare_bell_pair()
        bits = self.alice_measurement(psi, alice_half)
        received = self.bob_correction(bob_half, bits)
        
        self.teleportation_log.append({
            "sent": (psi.alpha, psi.beta),
            "received": (received.alpha, received.beta),
            "bits": bits
        })
        
        return (received, bits)


class EntanglementMetrics:
    """
    Compute entanglement measures.
    """
    
    @staticmethod
    def concurrence(c00: complex, c01: complex,
                   c10: complex, c11: complex) -> float:
        """
        Compute concurrence for two-qubit state.
        
        Args:
            c00, c01, c10, c11: State amplitudes
        
        Returns:
            Concurrence (0-1)
        """
        # C = 2 * |c00*c11 - c01*c10|
        return 2.0 * abs(c00 * c11 - c01 * c10)
    
    @staticmethod
    def entanglement_entropy(c00: complex, c01: complex,
                            c10: complex, c11: complex) -> float:
        """
        Compute von Neumann entanglement entropy.
        
        Args:
            c00, c01, c10, c11: State amplitudes
        
        Returns:
            Entropy
        """
        # Reduced density matrix eigenvalues
        a = abs(c00)**2 + abs(c01)**2
        b = abs(c10)**2 + abs(c11)**2
        
        # Eigenvalues of reduced density matrix
        lambda1 = a
        lambda2 = b
        
        # Ensure normalization
        total = lambda1 + lambda2
        if total > 0:
            lambda1 /= total
            lambda2 /= total
        
        entropy = 0.0
        for lam in [lambda1, lambda2]:
            if 0 < lam < 1:
                entropy -= lam * math.log2(lam)
        
        return entropy
    
    @staticmethod
    def is_entangled(c00: complex, c01: complex,
                    c10: complex, c11: complex,
                    threshold: float = 0.01) -> bool:
        """
        Check if state is entangled.
        
        Args:
            c00, c01, c10, c11: State amplitudes
            threshold: Entanglement threshold
        
        Returns:
            True if entangled
        """
        c = EntanglementMetrics.concurrence(c00, c01, c10, c11)
        return c > threshold


class FidelityEstimator:
    """
    Estimate teleportation fidelity.
    """
    
    def __init__(self, noise_model: Optional[Callable] = None):
        self.noise_model = noise_model
    
    def theoretical_fidelity(self, state: QubitState) -> float:
        """
        Theoretical maximum fidelity.
        
        Args:
            state: State to teleport
        
        Returns:
            Maximum fidelity (1.0 for ideal)
        """
        return 1.0
    
    def noisy_fidelity(self, state: QubitState,
                      noise_level: float = 0.01) -> float:
        """
        Estimate fidelity with noise.
        
        Args:
            state: State to teleport
            noise_level: Noise parameter
        
        Returns:
            Expected fidelity
        """
        # Depolarizing: F = 1 - (4/3)*p for Bell state
        return 1.0 - (4.0 / 3.0) * noise_level
    
    def average_fidelity(self, noise_level: float = 0.01) -> float:
        """
        Average fidelity over all input states.
        
        Args:
            noise_level: Noise parameter
        
        Returns:
            Average fidelity
        """
        return (2.0 + (1.0 - (4.0 / 3.0) * noise_level)) / 3.0


class QuantumTeleport:
    """
    Unified quantum teleportation controller.
    """
    
    def __init__(self):
        self.protocol = TeleportationProtocol()
        self.metrics = EntanglementMetrics()
        self.fidelity = FidelityEstimator()
        self.teleported_states = 0
    
    def send(self, state: QubitState) -> Tuple[QubitState, float]:
        """
        Teleport state and measure fidelity.
        
        Args:
            state: State to teleport
        
        Returns:
            (received_state, fidelity)
        """
        received, bits = self.protocol.teleport(state)
        self.teleported_states += 1
        
        fid = state.fidelity(received)
        return (received, fid)
    
    def entanglement_check(self) -> Dict:
        """
        Check entanglement quality.
        
        Returns:
            Entanglement metrics
        """
        c00, c01, c10, c11 = BellState.phi_plus()
        
        return {
            "concurrence": self.metrics.concurrence(c00, c01, c10, c11),
            "entropy": self.metrics.entanglement_entropy(c00, c01, c10, c11),
            "is_entangled": self.metrics.is_entangled(c00, c01, c10, c11)
        }
    
    def protocol_summary(self) -> Dict:
        """Get teleportation summary."""
        return {
            "teleported_states": self.teleported_states,
            "log_entries": len(self.protocol.teleportation_log),
            "theoretical_fidelity": self.fidelity.theoretical_fidelity(QubitState()),
            "entanglement": self.entanglement_check()
        }
