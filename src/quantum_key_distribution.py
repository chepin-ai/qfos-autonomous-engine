"""
Quantum Key Distribution Module
BB84 protocol, eavesdropper detection, key rate estimation,
and privacy amplification for autonomous quantum-secure communication.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class Basis(Enum):
    """Measurement basis."""
    RECTILINEAR = "Z"  # 0/1
    DIAGONAL = "X"     # +/−


class BitValue(Enum):
    """Quantum bit value."""
    ZERO = 0
    ONE = 1


@dataclass
class QubitTransmission:
    """A transmitted qubit."""
    bit: int
    basis: Basis
    received_bit: Optional[int] = None
    received_basis: Optional[Basis] = None


class BB84Protocol:
    """
    BB84 quantum key distribution protocol.
    """
    
    def __init__(self, error_threshold: float = 0.11):
        """
        Args:
            error_threshold: Maximum tolerable error rate
        """
        self.error_threshold = error_threshold
        self.transmissions: List[QubitTransmission] = []
        self.sifted_key: List[int] = []
    
    def encode(self, bit: int, basis: Basis) -> QubitTransmission:
        """
        Alice encodes a qubit.
        
        Args:
            bit: Bit value (0 or 1)
            basis: Encoding basis
        
        Returns:
            Transmission record
        """
        tx = QubitTransmission(bit=bit, basis=basis)
        self.transmissions.append(tx)
        return tx
    
    def measure(self, tx: QubitTransmission,
               basis: Basis) -> int:
        """
        Bob measures qubit in chosen basis.
        
        Args:
            tx: Transmission
            basis: Measurement basis
        
        Returns:
            Measured bit
        """
        tx.received_basis = basis
        
        if basis == tx.basis:
            # Correct basis: get original bit
            tx.received_bit = tx.bit
        else:
            # Wrong basis: random outcome
            import random
            tx.received_bit = random.choice([0, 1])
        
        return tx.received_bit
    
    def sift(self) -> List[int]:
        """
        Sift key (keep only matching bases).
        
        Returns:
            Sifted key bits
        """
        self.sifted_key = []
        
        for tx in self.transmissions:
            if tx.received_basis == tx.basis and tx.received_bit is not None:
                self.sifted_key.append(tx.received_bit)
        
        return self.sifted_key
    
    def error_rate(self, sample_indices: List[int]) -> float:
        """
        Compute error rate on sample.
        
        Args:
            sample_indices: Indices to check
        
        Returns:
            Error rate
        """
        if not sample_indices:
            return 0.0
        
        errors = 0
        for i in sample_indices:
            if i < len(self.transmissions):
                tx = self.transmissions[i]
                if tx.received_basis == tx.basis:
                    if tx.received_bit != tx.bit:
                        errors += 1
        
        return errors / len(sample_indices)
    
    def estimate_key_rate(self, qber: float,
                         detection_efficiency: float = 0.1,
                         rep_rate_Hz: float = 1e6) -> float:
        """
        Estimate secure key rate.
        
        Args:
            qber: Quantum bit error rate
            detection_efficiency: Detector efficiency
            rep_rate_Hz: Pulse repetition rate
        
        Returns:
            Secure key rate (bits/s)
        """
        if qber >= self.error_threshold:
            return 0.0
        
        # Simplified: key rate proportional to (1 - H(QBER) - H(QBER))
        # where H is binary entropy
        def h2(p):
            if p <= 0 or p >= 1:
                return 0.0
            return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
        
        # Asymptotic key rate
        rate_fraction = 1.0 - 2.0 * h2(qber)
        
        if rate_fraction <= 0:
            return 0.0
        
        return rep_rate_Hz * detection_efficiency * rate_fraction


class EavesdropperDetector:
    """
    Detect eavesdropping via error rate analysis.
    """
    
    def __init__(self, confidence_level: float = 0.99):
        """
        Args:
            confidence_level: Statistical confidence
        """
        self.confidence = confidence_level
    
    def detect(self, observed_qber: float,
              expected_qber: float,
              sample_size: int) -> Tuple[bool, float]:
        """
        Detect eavesdropping statistically.
        
        Args:
            observed_qber: Observed error rate
            expected_qber: Expected error rate (noise)
            sample_size: Number of samples
        
        Returns:
            (eavesdropper_detected, confidence)
        """
        if sample_size <= 0:
            return (False, 0.0)
        
        # Simplified: if observed QBER significantly exceeds expected
        margin = 3.0 * math.sqrt(expected_qber * (1 - expected_qber) / sample_size)
        
        if observed_qber > expected_qber + margin:
            confidence = min(1.0, (observed_qber - expected_qber) / margin)
            return (True, confidence)
        
        return (False, 0.0)
    
    def information_leak(self, qber: float) -> float:
        """
        Estimate information leaked to eavesdropper.
        
        Args:
            qber: Quantum bit error rate
        
        Returns:
            Leaked fraction
        """
        # For intercept-resend: Eve gets ~50% of key
        # For general attack: I_Eve <= h2(QBER)
        if qber <= 0 or qber >= 1:
            return 0.0
        
        return -(qber * math.log2(qber) + (1 - qber) * math.log2(1 - qber))


class PrivacyAmplification:
    """
    Privacy amplification for key distillation.
    """
    
    def __init__(self):
        self.hash_history: List[str] = []
    
    def toeplitz_hash(self, key_bits: List[int],
                     seed_bits: List[int],
                     output_length: int) -> List[int]:
        """
        Toeplitz matrix hashing.
        
        Args:
            key_bits: Raw key bits
            seed_bits: Random seed
            output_length: Desired output length
        
        Returns:
            Amplified key
        """
        # Simplified: XOR-based compression
        if not key_bits:
            return []
        
        output = []
        for i in range(output_length):
            bit = 0
            for j in range(len(key_bits)):
                seed_idx = (i + j) % max(1, len(seed_bits))
                if seed_bits:
                    bit ^= key_bits[j] & seed_bits[seed_idx]
                else:
                    bit ^= key_bits[j]
            output.append(bit)
        
        return output
    
    def amplify(self, raw_key: List[int],
               leaked_fraction: float) -> List[int]:
        """
        Perform privacy amplification.
        
        Args:
            raw_key: Raw sifted key
            leaked_fraction: Estimated leaked fraction
        
        Returns:
            Final key
        """
        if not raw_key:
            return []
        
        # Compress key by leaked amount
        target_length = max(1, int(len(raw_key) * (1.0 - leaked_fraction)))
        
        # Use simple seed
        seed = [1 if i % 2 == 0 else 0 for i in range(min(16, len(raw_key)))]
        
        return self.toeplitz_hash(raw_key, seed, target_length)


class KeyDistillation:
    """
    Full key distillation pipeline.
    """
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.detector = EavesdropperDetector()
        self.amplifier = PrivacyAmplification()
        self.raw_key: List[int] = []
        self.final_key: List[int] = []
    
    def distill(self, transmissions: List[QubitTransmission],
               sample_fraction: float = 0.2) -> Tuple[List[int], bool]:
        """
        Distill secure key.
        
        Args:
            transmissions: All transmissions
            sample_fraction: Fraction to use for error estimation
        
        Returns:
            (final_key, success)
        """
        self.bb84.transmissions = transmissions
        
        # Sift
        raw = self.bb84.sift()
        self.raw_key = raw
        
        if len(raw) < 10:
            return ([], False)
        
        # Error estimation
        sample_size = max(1, int(len(transmissions) * sample_fraction))
        sample_indices = list(range(0, min(sample_size, len(transmissions))))
        qber = self.bb84.error_rate(sample_indices)
        
        # Detect eavesdropper
        detected, confidence = self.detector.detect(qber, 0.01, sample_size)
        
        if detected and confidence > 0.5:
            return ([], False)
        
        if qber >= self.bb84.error_threshold:
            return ([], False)
        
        # Privacy amplification
        leaked = self.detector.information_leak(qber)
        self.final_key = self.amplifier.amplify(raw, leaked)
        
        return (self.final_key, True)
    
    def key_stats(self) -> Dict:
        """Get key statistics."""
        return {
            "raw_key_length": len(self.raw_key),
            "final_key_length": len(self.final_key),
            "compression_ratio": len(self.final_key) / max(1, len(self.raw_key))
        }


class QuantumKeyDistribution:
    """
    Unified QKD controller.
    """
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.distillation = KeyDistillation()
        self.sessions: List[Dict] = []
    
    def transmit(self, bits: List[int],
                bases: List[Basis],
                measurement_bases: List[Basis]) -> List[QubitTransmission]:
        """
        Simulate QKD transmission.
        
        Args:
            bits: Alice's bits
            bases: Alice's bases
            measurement_bases: Bob's bases
        
        Returns:
            Transmission records
        """
        transmissions = []
        
        for bit, basis, mbasis in zip(bits, bases, measurement_bases):
            tx = self.bb84.encode(bit, basis)
            self.bb84.measure(tx, mbasis)
            transmissions.append(tx)
        
        return transmissions
    
    def generate_key(self, transmissions: List[QubitTransmission]) -> Tuple[List[int], bool]:
        """
        Generate secure key from transmissions.
        
        Args:
            transmissions: Transmission records
        
        Returns:
            (key, success)
        """
        key, success = self.distillation.distill(transmissions)
        
        self.sessions.append({
            "transmissions": len(transmissions),
            "raw_key": len(self.distillation.raw_key),
            "final_key": len(key),
            "success": success
        })
        
        return (key, success)
    
    def qkd_summary(self) -> Dict:
        """Get QKD summary."""
        total = len(self.sessions)
        successful = sum(1 for s in self.sessions if s["success"])
        
        return {
            "total_sessions": total,
            "successful_sessions": successful,
            "total_final_bits": sum(s["final_key"] for s in self.sessions),
            "success_rate": successful / max(1, total)
        }
