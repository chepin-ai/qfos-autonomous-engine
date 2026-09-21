"""
Quantum Error Correction Codes Module
Steane code, Shor code, surface code,
stabilizers, syndrome measurement, and logical operations for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class Syndrome:
    """Error syndrome."""
    x_syndrome: List[int]
    z_syndrome: List[int]
    error_location: Optional[int] = None


class SteaneCode:
    """
    Steane [[7,1,3]] quantum error correction code.
    """
    
    def __init__(self):
        # Steane code stabilizers
        self.x_stabilizers = [
            [0, 1, 2, 3],  # XXXXIII
            [0, 1, 4, 5],  # XXIIIXX
            [0, 2, 4, 6],  # XIXIXIX
        ]
        self.z_stabilizers = [
            [0, 1, 2, 3],  # ZZZZIII
            [0, 1, 4, 5],  # ZZIIZZZ
            [0, 2, 4, 6],  # ZIZIZIZ
        ]
        self.n = 7
        self.k = 1
        self.d = 3
    
    def encode_logical_zero(self) -> List[int]:
        """
        Encode |0>_L.
        
        Returns:
            7-bit state (all zeros)
        """
        return [0] * self.n
    
    def encode_logical_one(self) -> List[int]:
        """
        Encode |1>_L.
        
        Returns:
            7-bit state (all ones)
        """
        return [1] * self.n
    
    def measure_x_syndrome(self, state: List[int]) -> List[int]:
        """
        Measure X stabilizer syndrome.
        
        Args:
            state: Physical state
        
        Returns:
            Syndrome bits
        """
        syndrome = []
        for stab in self.x_stabilizers:
            parity = sum(state[i] for i in stab) % 2
            syndrome.append(parity)
        return syndrome
    
    def measure_z_syndrome(self, state: List[int]) -> List[int]:
        """
        Measure Z stabilizer syndrome (simplified).
        
        Args:
            state: Physical state
        
        Returns:
            Syndrome bits
        """
        syndrome = []
        for stab in self.z_stabilizers:
            parity = sum(state[i] for i in stab) % 2
            syndrome.append(parity)
        return syndrome
    
    def correct_x_error(self, state: List[int],
                       syndrome: List[int]) -> List[int]:
        """
        Correct single X error from syndrome.
        
        Args:
            state: State with error
            syndrome: X syndrome
        
        Returns:
            Corrected state
        """
        # Syndrome to error location mapping for Steane code
        syndrome_map = {
            (0, 0, 0): None,
            (1, 1, 1): 0,
            (1, 1, 0): 1,
            (1, 0, 1): 2,
            (1, 0, 0): 3,
            (0, 1, 1): 4,
            (0, 1, 0): 5,
            (0, 0, 1): 6,
        }
        
        loc = syndrome_map.get(tuple(syndrome))
        if loc is not None:
            state = state.copy()
            state[loc] ^= 1
        return state


class ShorCode:
    """
    Shor [[9,1,3]] quantum error correction code.
    """
    
    def __init__(self):
        self.n = 9
        self.k = 1
        self.d = 3
    
    def encode_logical_zero(self) -> List[int]:
        """
        Encode |0>_L.
        
        Returns:
            9-bit state
        """
        # |0>_L = (|000> + |111>)(|000> + |111>)(|000> + |111>)
        # Classical simulation: use all zeros
        return [0] * self.n
    
    def encode_logical_one(self) -> List[int]:
        """
        Encode |1>_L.
        
        Returns:
            9-bit state
        """
        return [1] * self.n
    
    def measure_phase_syndrome(self, state: List[int]) -> List[int]:
        """
        Measure phase syndrome (between blocks).
        
        Args:
            state: State
        
        Returns:
            Syndrome bits
        """
        # Check parity between blocks of 3
        syndrome = []
        for i in range(2):
            block_parity = sum(state[i * 3 + j] for j in range(3)) % 2
            next_block = sum(state[(i + 1) * 3 + j] for j in range(3)) % 2
            syndrome.append(block_parity ^ next_block)
        return syndrome
    
    def measure_bit_syndrome(self, state: List[int]) -> List[int]:
        """
        Measure bit-flip syndrome within blocks.
        
        Args:
            state: State
        
        Returns:
            Syndrome bits
        """
        syndrome = []
        for i in range(3):
            b0 = state[i * 3]
            b1 = state[i * 3 + 1]
            b2 = state[i * 3 + 2]
            syndrome.append(b0 ^ b1)
            syndrome.append(b1 ^ b2)
        return syndrome


class SurfaceCode:
    """
    Surface code (simplified d=3, 9 data qubits).
    """
    
    def __init__(self, distance: int = 3):
        """
        Args:
            distance: Code distance
        """
        self.d = distance
        self.n = distance ** 2 + (distance - 1) ** 2  # Simplified
        self.data_qubits = distance ** 2
    
    def lattice_size(self) -> int:
        """
        Get lattice size.
        
        Returns:
            Lattice dimension
        """
        return self.d
    
    def num_stabilizers(self) -> int:
        """
        Get number of stabilizers.
        
        Returns:
            Number of stabilizers
        """
        return (self.d - 1) ** 2 * 2  # X and Z stabilizers
    
    def logical_error_rate(self, physical_error_rate: float) -> float:
        """
        Estimate logical error rate.
        
        Args:
            physical_error_rate: Physical error rate
        
        Returns:
            Logical error rate
        """
        # Approximate: logical error rate ~ (physical_error_rate)^((d+1)/2)
        exponent = (self.d + 1) // 2
        return physical_error_rate ** exponent


class QuantumErrorCorrectionCodes:
    """
    Unified quantum error correction controller.
    """
    
    def __init__(self):
        self.steane = SteaneCode()
        self.shor = ShorCode()
        self.surface = SurfaceCode()
    
    def protect_state(self, state: List[int],
                     code_type: str = "steane") -> Dict:
        """
        Protect state with error correction.
        
        Args:
            state: Logical state
            code_type: Code type
        
        Returns:
            Protected state info
        """
        if code_type == "steane":
            encoded = self.steane.encode_logical_zero() if state[0] == 0 else self.steane.encode_logical_one()
            syndrome_x = self.steane.measure_x_syndrome(encoded)
            return {
                "code": "steane",
                "encoded": encoded,
                "syndrome_x": syndrome_x,
                "n": self.steane.n,
                "k": self.steane.k,
                "d": self.steane.d
            }
        elif code_type == "shor":
            encoded = self.shor.encode_logical_zero() if state[0] == 0 else self.shor.encode_logical_one()
            return {
                "code": "shor",
                "encoded": encoded,
                "n": self.shor.n,
                "k": self.shor.k,
                "d": self.shor.d
            }
        else:
            return {"code": code_type, "error": "unknown_code"}
    
    def qecc_summary(self) -> Dict:
        """Get summary."""
        return {
            "codes": ["steane", "shor", "surface"],
            "steane": {"n": 7, "k": 1, "d": 3},
            "shor": {"n": 9, "k": 1, "d": 3},
            "surface": {"d": 3}
        }
