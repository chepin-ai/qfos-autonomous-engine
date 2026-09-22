"""
Quantum Cryptography Advanced Module
BB84 protocol, E91 entanglement-based QKD,
quantum key distillation, and quantum random number generation for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumKey:
    """Quantum key material."""
    bits: List[int]
    basis: List[str]


class BB84Protocol:
    """
    BB84 quantum key distribution protocol.
    """
    
    def __init__(self):
        self.bases = ["Z", "X"]
    
    def prepare_state(self, bit: int, basis: str) -> str:
        """
        Prepare quantum state.
        
        Args:
            bit: 0 or 1
            basis: Z or X
        
        Returns:
            State label
        """
        return f"|{bit}>_{basis}"
    
    def measure_state(self, sent_basis: str,
                     received_basis: str,
                     bit: int) -> int:
        """
        Measure state in chosen basis.
        
        Args:
            sent_basis: Sender basis
            received_basis: Receiver basis
            bit: Sent bit
        
        Returns:
            Measured bit
        """
        if sent_basis == received_basis:
            return bit
        # Random outcome if bases differ
        import random
        return random.randint(0, 1)
    
    def sift_key(self, alice_bits: List[int],
                alice_bases: List[str],
                bob_bases: List[str],
                bob_bits: List[int]) -> List[int]:
        """
        Sift matching basis key.
        
        Args:
            alice_bits: Alice bits
            alice_bases: Alice bases
            bob_bases: Bob bases
            bob_bits: Bob bits
        
        Returns:
            Sifted key
        """
        key = []
        for i in range(min(len(alice_bases), len(bob_bases))):
            if alice_bases[i] == bob_bases[i]:
                key.append(alice_bits[i])
        return key
    
    def quantum_bit_error_rate(self, key1: List[int],
                              key2: List[int]) -> float:
        """
        Compute QBER.
        
        Args:
            key1: Key 1
            key2: Key 2
        
        Returns:
            QBER
        """
        n = min(len(key1), len(key2))
        if n == 0:
            return 0.0
        errors = sum(1 for i in range(n) if key1[i] != key2[i])
        return errors / n


class E91Protocol:
    """
    E91 entanglement-based QKD protocol.
    """
    
    def __init__(self):
        pass
    
    def chsh_correlation(self, measurements_a: List[int],
                        measurements_b: List[int]) -> float:
        """
        Compute CHSH correlation.
        
        Args:
            measurements_a: Alice measurements
            measurements_b: Bob measurements
        
        Returns:
            Correlation
        """
        n = min(len(measurements_a), len(measurements_b))
        if n == 0:
            return 0.0
        same = sum(1 for i in range(n) if measurements_a[i] == measurements_b[i])
        diff = n - same
        return (same - diff) / n
    
    def chsh_parameter(self, correlations: List[float]) -> float:
        """
        Compute CHSH parameter S.
        
        Args:
            correlations: Four correlations
        
        Returns:
            S parameter
        """
        if len(correlations) < 4:
            return 0.0
        return abs(correlations[0] - correlations[1] + correlations[2] + correlations[3])
    
    def entanglement_verified(self, S: float,
                             threshold: float = 2.0) -> bool:
        """
        Check if entanglement is verified.
        
        Args:
            S: CHSH parameter
            threshold: Bell threshold
        
        Returns:
            True if entangled
        """
        return S > threshold


class QuantumKeyDistillation:
    """
    Post-processing for quantum keys.
    """
    
    def __init__(self):
        pass
    
    def privacy_amplification(self, key: List[int],
                             seed: int = 42) -> List[int]:
        """
        Simple privacy amplification.
        
        Args:
            key: Raw key
            seed: Random seed
        
        Returns:
            Distilled key
        """
        if not key:
            return []
        import random
        rng = random.Random(seed)
        # XOR pairs
        distilled = []
        for i in range(0, len(key) - 1, 2):
            distilled.append(key[i] ^ key[i+1])
        if len(key) % 2 == 1:
            distilled.append(key[-1] ^ (rng.randint(0, 1)))
        return distilled
    
    def error_reconciliation(self, key1: List[int],
                            key2: List[int],
                            parity_bits: int = 3) -> Tuple[List[int], List[int]]:
        """
        Simple error reconciliation.
        
        Args:
            key1: Key 1
            key2: Key 2
            parity_bits: Block size
        
        Returns:
            (corrected1, corrected2)
        """
        if not key1 or not key2:
            return (key1, key2)
        corrected1 = list(key1)
        corrected2 = list(key2)
        # Flip mismatched bits in blocks
        for i in range(0, min(len(corrected1), len(corrected2)), parity_bits):
            block_end = min(i + parity_bits, len(corrected1), len(corrected2))
            p1 = sum(corrected1[j] for j in range(i, block_end)) % 2
            p2 = sum(corrected2[j] for j in range(i, block_end)) % 2
            if p1 != p2:
                # Find and correct first mismatch
                for j in range(i, block_end):
                    if corrected1[j] != corrected2[j]:
                        corrected2[j] = corrected1[j]
                        break
        return (corrected1, corrected2)


class QuantumRandomNumberGeneration:
    """
    Quantum random number generation.
    """
    
    def __init__(self):
        pass
    
    def generate_bits(self, n: int,
                     seed: Optional[int] = None) -> List[int]:
        """
        Generate random bits.
        
        Args:
            n: Number of bits
            seed: Optional seed
        
        Returns:
            Random bits
        """
        import random
        rng = random.Random(seed)
        return [rng.randint(0, 1) for _ in range(n)]
    
    def generate_bases(self, n: int,
                      seed: Optional[int] = None) -> List[str]:
        """
        Generate random bases.
        
        Args:
            n: Number of bases
            seed: Optional seed
        
        Returns:
            Random bases (Z or X)
        """
        import random
        rng = random.Random(seed)
        return ["Z" if rng.random() < 0.5 else "X" for _ in range(n)]
    
    def entropy_estimate(self, bits: List[int]) -> float:
        """
        Estimate Shannon entropy.
        
        Args:
            bits: Bit sequence
        
        Returns:
            Entropy per bit
        """
        if not bits:
            return 0.0
        n = len(bits)
        p0 = bits.count(0) / n
        p1 = bits.count(1) / n
        entropy = 0.0
        for p in [p0, p1]:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy


class QuantumCryptographyAdvanced:
    """
    Unified quantum cryptography controller.
    """
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.e91 = E91Protocol()
        self.distillation = QuantumKeyDistillation()
        self.qrng = QuantumRandomNumberGeneration()
    
    def qkd_summary(self) -> Dict:
        """Get summary."""
        return {
            "protocols": ["bb84", "e91"],
            "tools": ["privacy_amplification", "error_reconciliation", "qrng"],
            "applications": ["secure_communication", "randomness"]
        }
