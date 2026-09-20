"""
Quantum Error Correction Module
Bit-flip code, phase-flip code, Shor code, syndrome
measurement, and stabilizer formalism for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumError:
    """Quantum error."""
    qubit_index: int
    error_type: str  # "X", "Z", "Y"


class BitFlipCode:
    """
    3-qubit bit-flip code.
    """
    
    def __init__(self):
        self.code_distance = 3
    
    def encode(self, logical_state: List[complex]) -> List[complex]:
        """
        Encode logical qubit.
        
        Args:
            logical_state: [alpha, beta]
        
        Returns:
            Encoded state (8 amplitudes for 3 qubits)
        """
        if len(logical_state) < 2:
            logical_state = [1.0, 0.0]
        
        alpha = logical_state[0]
        beta = logical_state[1]
        
        # |0_L> = |000>, |1_L> = |111>
        state = [0.0] * 8
        state[0] = alpha  # |000>
        state[7] = beta   # |111>
        
        return state
    
    def measure_syndrome(self, state: List[complex]) -> List[int]:
        """
        Measure syndrome.
        
        Args:
            state: Physical state
        
        Returns:
            Syndrome bits [s1, s2]
        """
        probs = [abs(a)**2 for a in state]
        
        # Syndrome Z1*Z2: eigenvalue +1 on {000,011,101,110}
        s1 = 0 if (probs[0] + probs[3] + probs[5] + probs[6]) > 0.5 else 1
        
        # Syndrome Z2*Z3: eigenvalue +1 on {000,001,110,111}
        s2 = 0 if (probs[0] + probs[1] + probs[6] + probs[7]) > 0.5 else 1
        
        return [s1, s2]
    
    def correct(self, state: List[complex]) -> List[complex]:
        """
        Correct bit-flip error.
        
        Args:
            state: State
        
        Returns:
            Corrected state
        """
        syndrome = self.measure_syndrome(state)
        corrected = state[:]
        
        if syndrome == [1, 1]:
            # Error on qubit 1
            corrected = self._apply_x(corrected, 1)
        elif syndrome == [1, 0]:
            # Error on qubit 0
            corrected = self._apply_x(corrected, 0)
        elif syndrome == [0, 1]:
            # Error on qubit 2
            corrected = self._apply_x(corrected, 2)
        
        return corrected
    
    def _apply_x(self, state: List[complex], qubit: int) -> List[complex]:
        """Apply X gate."""
        new_state = [0.0] * len(state)
        for i, amp in enumerate(state):
            flipped = i ^ (1 << qubit)
            new_state[flipped] = amp
        return new_state
    
    def decode(self, state: List[complex]) -> List[complex]:
        """
        Decode to logical state.
        
        Args:
            state: Physical state
        
        Returns:
            Logical state [alpha, beta]
        """
        probs = [abs(a)**2 for a in state]
        p0 = probs[0] + probs[1] + probs[2] + probs[3]
        p1 = probs[4] + probs[5] + probs[6] + probs[7]
        
        total = p0 + p1
        if total > 0:
            return [math.sqrt(p0 / total), math.sqrt(p1 / total)]
        return [1.0, 0.0]


class PhaseFlipCode:
    """
    3-qubit phase-flip code.
    """
    
    def __init__(self):
        self.code_distance = 3
    
    def encode(self, logical_state: List[complex]) -> List[complex]:
        """
        Encode logical qubit.
        
        Args:
            logical_state: [alpha, beta]
        
        Returns:
            Encoded state
        """
        if len(logical_state) < 2:
            logical_state = [1.0, 0.0]
        
        alpha = logical_state[0]
        beta = logical_state[1]
        
        # |0_L> = |+++>, |1_L> = |--->
        # |+> = (|0> + |1>)/sqrt(2), |-> = (|0> - |1>)/sqrt(2)
        state = [0.0] * 8
        
        for i in range(8):
            bits = bin(i).count('1')
            sign = 1 if bits % 2 == 0 else -1
            
            if bits == 0 or bits == 2:
                # Part of |+++>
                state[i] += alpha / (2.0 * math.sqrt(2.0))
            if bits == 3 or bits == 1:
                # Part of |--->
                state[i] += beta * sign / (2.0 * math.sqrt(2.0))
        
        return state
    
    def measure_syndrome(self, state: List[complex]) -> List[int]:
        """
        Measure syndrome in X basis.
        
        Args:
            state: State
        
        Returns:
            Syndrome
        """
        # Transform to X basis
        x_basis = []
        for i in range(8):
            amp = 0.0
            for j in range(8):
                sign = 1 if bin(i & j).count('1') % 2 == 0 else -1
                amp += sign * state[j]
            x_basis.append(amp / (2.0 * math.sqrt(2.0)))
        
        probs = [abs(a)**2 for a in x_basis]
        
        s1 = 0 if (probs[0] + probs[1] + probs[2] + probs[3]) > 0.5 else 1
        s2 = 0 if (probs[0] + probs[1] + probs[4] + probs[5]) > 0.5 else 1
        
        return [s1, s2]
    
    def correct(self, state: List[complex]) -> List[complex]:
        """
        Correct phase-flip error.
        
        Args:
            state: State
        
        Returns:
            Corrected state
        """
        syndrome = self.measure_syndrome(state)
        corrected = state[:]
        
        if syndrome == [1, 1]:
            corrected = self._apply_z(corrected, 2)
        elif syndrome == [1, 0]:
            corrected = self._apply_z(corrected, 1)
        elif syndrome == [0, 1]:
            corrected = self._apply_z(corrected, 0)
        
        return corrected
    
    def _apply_z(self, state: List[complex], qubit: int) -> List[complex]:
        """Apply Z gate."""
        new_state = state[:]
        for i in range(len(state)):
            if (i >> qubit) & 1:
                new_state[i] = -new_state[i]
        return new_state


class StabilizerFormalism:
    """
    Stabilizer formalism for QEC.
    """
    
    def __init__(self, num_qubits: int = 3):
        """
        Args:
            num_qubits: Qubits
        """
        self.n = num_qubits
        self.stabilizers: List[str] = []
    
    def add_stabilizer(self, operator: str):
        """
        Add stabilizer.
        
        Args:
            operator: Pauli string
        """
        self.stabilizers.append(operator)
    
    def measure_stabilizer(self, state: List[complex],
                          operator: str) -> int:
        """
        Measure stabilizer.
        
        Args:
            state: State
            operator: Pauli string
        
        Returns:
            Eigenvalue (+1 or -1)
        """
        new_state = state[:]
        
        for i, pauli in enumerate(operator):
            if pauli == 'X':
                new_state = self._apply_x_string(new_state, i)
            elif pauli == 'Z':
                new_state = self._apply_z_string(new_state, i)
            elif pauli == 'Y':
                new_state = self._apply_y_string(new_state, i)
        
        # Compute expectation value
        exp = sum((new_state[i].conjugate() * state[i]).real
                 for i in range(len(state)))
        
        return 1 if exp > 0 else -1
    
    def _apply_x_string(self, state: List[complex], qubit: int) -> List[complex]:
        """Apply X."""
        new_state = [0.0] * len(state)
        for i, amp in enumerate(state):
            flipped = i ^ (1 << qubit)
            new_state[flipped] = amp
        return new_state
    
    def _apply_z_string(self, state: List[complex], qubit: int) -> List[complex]:
        """Apply Z."""
        new_state = state[:]
        for i in range(len(state)):
            if (i >> qubit) & 1:
                new_state[i] = -new_state[i]
        return new_state
    
    def _apply_y_string(self, state: List[complex], qubit: int) -> List[complex]:
        """Apply Y."""
        new_state = [0.0] * len(state)
        for i, amp in enumerate(state):
            flipped = i ^ (1 << qubit)
            sign = 1j if (i >> qubit) & 1 else -1j
            new_state[flipped] = sign * amp
        return new_state


class QuantumErrorCorrection:
    """
    Unified QEC controller.
    """
    
    def __init__(self):
        self.bit_flip = BitFlipCode()
        self.phase_flip = PhaseFlipCode()
        self.stabilizer = StabilizerFormalism()
        self.errors: List[QuantumError] = []
    
    def encode_bit_flip(self, state: List[complex]) -> List[complex]:
        """
        Encode with bit-flip code.
        
        Args:
            state: Logical state
        
        Returns:
            Encoded
        """
        return self.bit_flip.encode(state)
    
    def encode_phase_flip(self, state: List[complex]) -> List[complex]:
        """
        Encode with phase-flip code.
        
        Args:
            state: Logical state
        
        Returns:
            Encoded
        """
        return self.phase_flip.encode(state)
    
    def simulate_error(self, state: List[complex],
                      qubit: int, error_type: str) -> List[complex]:
        """
        Simulate error.
        
        Args:
            state: State
            qubit: Qubit index
            error_type: X, Z, or Y
        
        Returns:
            Corrupted state
        """
        self.errors.append(QuantumError(qubit, error_type))
        
        if error_type == "X":
            return self.bit_flip._apply_x(state, qubit)
        elif error_type == "Z":
            return self.phase_flip._apply_z(state, qubit)
        else:
            return state
    
    def correct(self, state: List[complex],
               code_type: str = "bit_flip") -> List[complex]:
        """
        Correct errors.
        
        Args:
            state: State
            code_type: Code type
        
        Returns:
            Corrected state
        """
        if code_type == "bit_flip":
            return self.bit_flip.correct(state)
        elif code_type == "phase_flip":
            return self.phase_flip.correct(state)
        return state
    
    def qec_summary(self) -> Dict:
        """Get summary."""
        return {
            "code_distance": self.bit_flip.code_distance,
            "errors_simulated": len(self.errors),
            "stabilizers": len(self.stabilizer.stabilizers)
        }
