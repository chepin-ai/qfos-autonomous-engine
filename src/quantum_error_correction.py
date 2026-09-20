"""
Quantum Error Correction Module
Bit-flip code, phase-flip code, Shor code, Steane code,
and syndrome measurement for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QubitState:
    """Logical qubit state."""
    physical_qubits: List[int]  # 0 or 1
    error_type: str  # "none", "bit", "phase"


class BitFlipCode:
    """
    3-qubit bit-flip error correction code.
    """
    
    def __init__(self):
        pass
    
    def encode(self, logical_bit: int) -> List[int]:
        """
        Encode logical bit.
        
        Args:
            logical_bit: 0 or 1
        
        Returns:
            3 physical qubits
        """
        return [logical_bit] * 3
    
    def apply_error(self, codeword: List[int],
                   error_position: Optional[int] = None) -> List[int]:
        """
        Apply bit-flip error.
        
        Args:
            codeword: Codeword
            error_position: Position to flip
        
        Returns:
            Corrupted codeword
        """
        corrupted = codeword.copy()
        if error_position is not None and 0 <= error_position < len(corrupted):
            corrupted[error_position] = 1 - corrupted[error_position]
        return corrupted
    
    def syndrome(self, codeword: List[int]) -> Tuple[int, int]:
        """
        Compute syndrome.
        
        Args:
            codeword: Codeword
        
        Returns:
            (z1, z2) syndrome bits
        """
        if len(codeword) < 3:
            return (0, 0)
        z1 = codeword[0] ^ codeword[1]
        z2 = codeword[1] ^ codeword[2]
        return (z1, z2)
    
    def correct(self, codeword: List[int]) -> List[int]:
        """
        Correct single bit-flip error.
        
        Args:
            codeword: Corrupted codeword
        
        Returns:
            Corrected codeword
        """
        if len(codeword) < 3:
            return codeword
        
        z1, z2 = self.syndrome(codeword)
        corrected = codeword.copy()
        
        if z1 == 0 and z2 == 0:
            pass  # No error
        elif z1 == 1 and z2 == 1:
            corrected[1] = 1 - corrected[1]  # Error on qubit 1
        elif z1 == 1 and z2 == 0:
            corrected[0] = 1 - corrected[0]  # Error on qubit 0
        elif z1 == 0 and z2 == 1:
            corrected[2] = 1 - corrected[2]  # Error on qubit 2
        
        return corrected
    
    def decode(self, codeword: List[int]) -> int:
        """
        Decode to logical bit.
        
        Args:
            codeword: Codeword
        
        Returns:
            Logical bit
        """
        if not codeword:
            return 0
        # Majority vote
        return 1 if sum(codeword) >= len(codeword) / 2 else 0


class PhaseFlipCode:
    """
    3-qubit phase-flip error correction code.
    """
    
    def __init__(self):
        pass
    
    def encode(self, logical_bit: int) -> List[str]:
        """
        Encode logical bit in phase basis.
        
        Args:
            logical_bit: 0 or 1
        
        Returns:
            Phase states
        """
        if logical_bit == 0:
            return ["+", "+", "+"]
        else:
            return ["-", "-", "-"]
    
    def apply_phase_error(self, codeword: List[str],
                         position: int) -> List[str]:
        """
        Apply phase flip.
        
        Args:
            codeword: Codeword
            position: Position
        
        Returns:
            Corrupted codeword
        """
        corrupted = codeword.copy()
        if 0 <= position < len(corrupted):
            corrupted[position] = "-" if corrupted[position] == "+" else "+"
        return corrupted
    
    def measure_phase_syndrome(self, codeword: List[str]) -> Tuple[int, int]:
        """
        Measure phase syndrome.
        
        Args:
            codeword: Codeword
        
        Returns:
            Syndrome
        """
        if len(codeword) < 3:
            return (0, 0)
        # Convert to bit representation: + -> 0, - -> 1
        bits = [0 if s == "+" else 1 for s in codeword]
        z1 = bits[0] ^ bits[1]
        z2 = bits[1] ^ bits[2]
        return (z1, z2)
    
    def correct(self, codeword: List[str]) -> List[str]:
        """
        Correct phase error.
        
        Args:
            codeword: Corrupted codeword
        
        Returns:
            Corrected codeword
        """
        z1, z2 = self.measure_phase_syndrome(codeword)
        corrected = codeword.copy()
        
        if z1 == 1 and z2 == 1:
            corrected[1] = "-" if corrected[1] == "+" else "+"
        elif z1 == 1 and z2 == 0:
            corrected[0] = "-" if corrected[0] == "+" else "+"
        elif z1 == 0 and z2 == 1:
            corrected[2] = "-" if corrected[2] == "+" else "+"
        
        return corrected


class ShorCode:
    """
    9-qubit Shor code.
    """
    
    def __init__(self):
        self.bit_flip = BitFlipCode()
        self.phase_flip = PhaseFlipCode()
    
    def encode(self, logical_bit: int) -> List[List[int]]:
        """
        Encode with Shor code.
        
        Args:
            logical_bit: 0 or 1
        
        Returns:
            9 physical qubits in 3 blocks
        """
        # First phase flip encoding
        phase_encoded = self.phase_flip.encode(logical_bit)
        
        # Then bit flip encoding for each
        blocks = []
        for phase in phase_encoded:
            bit_val = 0 if phase == "+" else 1
            blocks.append(self.bit_flip.encode(bit_val))
        
        return blocks
    
    def decode(self, blocks: List[List[int]]) -> int:
        """
        Decode Shor code.
        
        Args:
            blocks: 3 blocks of 3 qubits
        
        Returns:
            Logical bit
        """
        if len(blocks) < 3:
            return 0
        
        # Correct each block
        corrected_blocks = [self.bit_flip.correct(b) for b in blocks]
        
        # Decode phase
        phase_bits = [self.bit_flip.decode(b) for b in corrected_blocks]
        # Convert back to phase states
        phase_states = ["+" if b == 0 else "-" for b in phase_bits]
        corrected_phase = self.phase_flip.correct(phase_states)
        
        # Final decode
        final_bits = [0 if s == "+" else 1 for s in corrected_phase]
        return 1 if sum(final_bits) >= 2 else 0


class SteaneCode:
    """
    7-qubit Steane code.
    """
    
    def __init__(self):
        self.stabilizers = [
            [0, 1, 2, 3],  # XXXXIII
            [0, 1, 4, 5],  # XXIIXXI
            [0, 2, 4, 6],  # XIXIXIX
        ]
    
    def compute_syndrome(self, codeword: List[int]) -> List[int]:
        """
        Compute Steane syndrome.
        
        Args:
            codeword: 7 qubits
        
        Returns:
            Syndrome bits
        """
        if len(codeword) < 7:
            return [0, 0, 0]
        
        syndrome = []
        for stab in self.stabilizers:
            parity = sum(codeword[i] for i in stab) % 2
            syndrome.append(parity)
        
        return syndrome
    
    def correct(self, codeword: List[int]) -> List[int]:
        """
        Correct single error.
        
        Args:
            codeword: Corrupted codeword
        
        Returns:
            Corrected codeword
        """
        if len(codeword) < 7:
            return codeword
        
        syndrome = self.compute_syndrome(codeword)
        corrected = codeword.copy()
        
        # Syndrome to error position mapping (simplified)
        syndromes = {
            (1, 1, 1): 0, (1, 1, 0): 1, (1, 0, 1): 2, (1, 0, 0): 3,
            (0, 1, 1): 4, (0, 1, 0): 5, (0, 0, 1): 6
        }
        
        pos = syndromes.get(tuple(syndrome))
        if pos is not None:
            corrected[pos] = 1 - corrected[pos]
        
        return corrected


class QuantumErrorCorrection:
    """
    Unified quantum error correction controller.
    """
    
    def __init__(self):
        self.bit_flip = BitFlipCode()
        self.phase_flip = PhaseFlipCode()
        self.shor = ShorCode()
        self.steane = SteaneCode()
    
    def protect_bit(self, bit: int, code: str = "bit_flip") -> List:
        """
        Protect bit with QEC.
        
        Args:
            bit: Logical bit
            code: Code type
        
        Returns:
            Encoded codeword
        """
        if code == "bit_flip":
            return self.bit_flip.encode(bit)
        elif code == "phase_flip":
            return self.phase_flip.encode(bit)
        elif code == "shor":
            return self.shor.encode(bit)
        return [bit]
    
    def recover(self, codeword: List, code: str = "bit_flip") -> int:
        """
        Recover logical bit.
        
        Args:
            codeword: Corrupted codeword
            code: Code type
        
        Returns:
            Logical bit
        """
        if code == "bit_flip":
            corrected = self.bit_flip.correct(codeword)
            return self.bit_flip.decode(corrected)
        elif code == "phase_flip":
            corrected = self.phase_flip.correct(codeword)
            return 0 if corrected.count("+") >= 2 else 1
        elif code == "shor":
            return self.shor.decode(codeword)
        return codeword[0] if codeword else 0
    
    def qec_summary(self) -> Dict:
        """Get summary."""
        return {
            "codes": ["bit_flip", "phase_flip", "shor", "steane"],
            "correctable_errors": "single bit/phase flip"
        }
