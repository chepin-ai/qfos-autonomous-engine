"""
Quantum Cryptography Module
Quantum key distribution, BB84 protocol, quantum random
number generation, and eavesdropper detection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumKey:
    """Quantum key."""
    bits: List[int]
    bases: List[str]


class QuantumRandomNumberGenerator:
    """
    Generate quantum random numbers.
    """
    
    def __init__(self):
        pass
    
    def generate_bits(self, n: int) -> List[int]:
        """
        Generate random bits.
        
        Args:
            n: Number of bits
        
        Returns:
            Random bits
        """
        import random
        return [random.randint(0, 1) for _ in range(n)]
    
    def generate_bases(self, n: int) -> List[str]:
        """
        Generate random bases (Z or X).
        
        Args:
            n: Number of bases
        
        Returns:
            Random bases
        """
        import random
        return ["Z" if random.random() < 0.5 else "X" for _ in range(n)]


class BB84Protocol:
    """
    BB84 quantum key distribution.
    """
    
    def __init__(self):
        self.rng = QuantumRandomNumberGenerator()
        self.alice_bits: List[int] = []
        self.alice_bases: List[str] = []
        self.bob_bases: List[str] = []
        self.bob_results: List[int] = []
        self.key: List[int] = []
    
    def alice_prepare(self, n: int):
        """
        Alice prepares quantum states.
        
        Args:
            n: Number of qubits
        """
        self.alice_bits = self.rng.generate_bits(n)
        self.alice_bases = self.rng.generate_bases(n)
    
    def bob_measure(self, n: int):
        """
        Bob measures.
        
        Args:
            n: Number of measurements
        """
        self.bob_bases = self.rng.generate_bases(n)
        # Simulate measurement
        self.bob_results = []
        for i in range(n):
            if self.bob_bases[i] == self.alice_bases[i]:
                # Correct basis - get correct bit
                self.bob_results.append(self.alice_bits[i])
            else:
                # Wrong basis - random result
                import random
                self.bob_results.append(random.randint(0, 1))
    
    def sift_key(self) -> List[int]:
        """
        Sift key from matching bases.
        
        Returns:
            Sifted key
        """
        self.key = []
        for i in range(len(self.alice_bits)):
            if self.alice_bases[i] == self.bob_bases[i]:
                self.key.append(self.alice_bits[i])
        return self.key
    
    def error_rate(self, sample_size: int = 20) -> float:
        """
        Compute error rate.
        
        Args:
            sample_size: Sample size
        
        Returns:
            Error rate
        """
        if len(self.key) < sample_size:
            return 0.0
        
        # Compare a subset
        sample = self.key[:sample_size]
        # In real protocol, compare with Alice's copy
        # Here we simulate some errors
        import random
        errors = sum(random.random() < 0.05 for _ in sample)
        return errors / sample_size


class EavesdropperDetector:
    """
    Detect eavesdropping.
    """
    
    def __init__(self, threshold: float = 0.11):
        """
        Args:
            threshold: Error rate threshold
        """
        self.threshold = threshold
    
    def detect(self, error_rate: float) -> bool:
        """
        Detect eavesdropper.
        
        Args:
            error_rate: Error rate
        
        Returns:
            True if eavesdropping detected
        """
        return error_rate > self.threshold
    
    def information_leakage(self, error_rate: float) -> float:
        """
        Estimate information leakage.
        
        Args:
            error_rate: Error rate
        
        Returns:
            Leakage fraction
        """
        # Simplified: leakage proportional to error rate
        return min(1.0, error_rate * 4.0)


class QuantumKeyDistiller:
    """
    Distill quantum key.
    """
    
    def __init__(self):
        pass
    
    def privacy_amplification(self, raw_key: List[int],
                             final_length: int) -> List[int]:
        """
        Privacy amplification.
        
        Args:
            raw_key: Raw key
            final_length: Final length
        
        Returns:
            Final key
        """
        if not raw_key:
            return []
        
        # Simple hash: XOR groups of bits
        group_size = max(1, len(raw_key) // final_length)
        distilled = []
        
        for i in range(final_length):
            start = i * group_size
            end = min(start + group_size, len(raw_key))
            group = raw_key[start:end]
            
            # XOR all bits in group
            bit = 0
            for b in group:
                bit ^= b
            distilled.append(bit)
        
        return distilled


class QuantumCryptography:
    """
    Unified quantum cryptography controller.
    """
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.detector = EavesdropperDetector()
        self.distiller = QuantumKeyDistiller()
        self.final_key: List[int] = []
    
    def distribute_key(self, n_qubits: int = 100) -> Dict:
        """
        Distribute key.
        
        Args:
            n_qubits: Number of qubits
        
        Returns:
            Results
        """
        self.bb84.alice_prepare(n_qubits)
        self.bb84.bob_measure(n_qubits)
        
        raw_key = self.bb84.sift_key()
        error = self.bb84.error_rate()
        
        # Check for eavesdropping
        is_eavesdropped = self.detector.detect(error)
        
        if not is_eavesdropped and len(raw_key) > 0:
            final_length = max(1, len(raw_key) // 2)
            self.final_key = self.distiller.privacy_amplification(raw_key, final_length)
        else:
            self.final_key = []
        
        return {
            "raw_key_length": len(raw_key),
            "error_rate": error,
            "eavesdropped": is_eavesdropped,
            "final_key_length": len(self.final_key)
        }
    
    def qcrypto_summary(self) -> Dict:
        """Get summary."""
        return {
            "final_key_length": len(self.final_key),
            "threshold": self.detector.threshold
        }
