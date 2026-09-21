"""
Quantum Cryptography Module
BB84, E91, quantum key distribution,
entanglement-based crypto, and security analysis for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QKDKey:
    """Quantum key result."""
    key: str
    length: int
    error_rate: float


class BB84Protocol:
    """
    BB84 quantum key distribution protocol.
    """
    
    def __init__(self):
        self.basis_choices: List[str] = []
        self.bit_values: List[int] = []
    
    def generate_raw_key(self, num_bits: int) -> Tuple[List[int], List[str]]:
        """
        Generate raw key with random bases.
        
        Args:
            num_bits: Number of bits
        
        Returns:
            (bits, bases)
        """
        bits = [random.randint(0, 1) for _ in range(num_bits)]
        bases = [random.choice(["Z", "X"]) for _ in range(num_bits)]
        return (bits, bases)
    
    def encode(self, bits: List[int],
              bases: List[str]) -> List[str]:
        """
        Encode bits into quantum states.
        
        Args:
            bits: Bits to encode
            bases: Bases for encoding
        
        Returns:
            State labels
        """
        states = []
        for bit, basis in zip(bits, bases):
            if basis == "Z":
                states.append("|0>" if bit == 0 else "|1>")
            else:
                states.append("|+>" if bit == 0 else "|->")
        return states
    
    def measure(self, states: List[str],
               measure_bases: List[str]) -> List[int]:
        """
        Measure states in given bases.
        
        Args:
            states: Quantum states
            measure_bases: Measurement bases
        
        Returns:
            Measurement results
        """
        results = []
        for state, basis in zip(states, measure_bases):
            if basis == "Z":
                if state in ["|0>", "|+>", "|->"]:
                    # |+> and |-> have 50% chance of 0
                    if state == "|0>":
                        results.append(0)
                    elif state == "|1>":
                        results.append(1)
                    else:
                        results.append(random.randint(0, 1))
                else:
                    results.append(1)
            else:
                if state in ["|+>", "|0>", "|1>"]:
                    if state == "|+>":
                        results.append(0)
                    elif state == "|->":
                        results.append(1)
                    else:
                        results.append(random.randint(0, 1))
                else:
                    results.append(1)
        return results
    
    def sift_key(self, alice_bases: List[str],
                bob_bases: List[str],
                alice_bits: List[int],
                bob_bits: List[int]) -> Tuple[str, float]:
        """
        Sift key by matching bases.
        
        Args:
            alice_bases: Alice's bases
            bob_bases: Bob's bases
            alice_bits: Alice's bits
            bob_bits: Bob's bits
        
        Returns:
            (sifted_key, error_rate)
        """
        matching = []
        errors = 0
        
        for a_base, b_base, a_bit, b_bit in zip(alice_bases, bob_bases, alice_bits, bob_bits):
            if a_base == b_base:
                matching.append(str(a_bit))
                if a_bit != b_bit:
                    errors += 1
        
        key = "".join(matching)
        error_rate = errors / len(matching) if matching else 0.0
        
        return (key, error_rate)


class E91Protocol:
    """
    Ekert 91 entanglement-based QKD.
    """
    
    def __init__(self):
        pass
    
    def generate_entangled_pair(self) -> Tuple[str, str]:
        """
        Generate entangled Bell pair.
        
        Returns:
            (alice_state, bob_state)
        """
        # Simulate |Phi+> = (|00> + |11>) / sqrt(2)
        if random.random() < 0.5:
            return ("|0>", "|0>")
        else:
            return ("|1>", "|1>")
    
    def CHSH_test(self, alice_results: List[int],
                 bob_results: List[int],
                 alice_bases: List[int],
                 bob_bases: List[int]) -> float:
        """
        Compute CHSH correlation.
        
        Args:
            alice_results: Alice's measurements
            bob_results: Bob's measurements
            alice_bases: Alice's base choices
            bob_bases: Bob's base choices
        
        Returns:
            S parameter
        """
        # Simplified CHSH: count correlations for basis combinations
        E = {}
        counts = {}
        
        for a, b, a_base, b_base in zip(alice_results, bob_results, alice_bases, bob_bases):
            key = (a_base, b_base)
            if key not in counts:
                counts[key] = {"same": 0, "diff": 0}
            if a == b:
                counts[key]["same"] += 1
            else:
                counts[key]["diff"] += 1
        
        # Compute S = E(0,0) - E(0,1) + E(1,0) + E(1,1)
        S = 0.0
        for key, c in counts.items():
            total = c["same"] + c["diff"]
            if total > 0:
                E_val = (c["same"] - c["diff"]) / total
                E[key] = E_val
        
        # Simplified S calculation
        S = sum(abs(v) for v in E.values())
        return S


class PrivacyAmplification:
    """
    Privacy amplification for QKD.
    """
    
    def __init__(self):
        pass
    
    def xor_amplification(self, raw_key: str,
                         block_size: int = 2) -> str:
        """
        XOR-based privacy amplification.
        
        Args:
            raw_key: Raw key
            block_size: Block size
        
        Returns:
            Amplified key
        """
        result = []
        for i in range(0, len(raw_key), block_size):
            block = raw_key[i:i + block_size]
            parity = sum(int(b) for b in block) % 2
            result.append(str(parity))
        return "".join(result)
    
    def universal_hash(self, key: str,
                      seed: int = 42) -> str:
        """
        Universal hash function.
        
        Args:
            key: Key
            seed: Seed
        
        Returns:
            Hashed key
        """
        random.seed(seed)
        # XOR with random mask
        mask = "".join(str(random.randint(0, 1)) for _ in range(len(key)))
        return "".join(str(int(a) ^ int(b)) for a, b in zip(key, mask))


class SecurityAnalyzer:
    """
    QKD security analysis.
    """
    
    def __init__(self):
        pass
    
    def information_leakage(self, error_rate: float) -> float:
        """
        Estimate information leakage to eavesdropper.
        
        Args:
            error_rate: QBER
        
        Returns:
            Leaked fraction
        """
        # Simplified: linear approximation
        if error_rate >= 0.25:
            return 1.0
        return error_rate / 0.25
    
    def secure_key_rate(self, raw_rate: float,
                       error_rate: float) -> float:
        """
        Compute secure key rate.
        
        Args:
            raw_rate: Raw key rate
            error_rate: Error rate
        
        Returns:
            Secure key rate
        """
        # Simplified: key rate decreases with error
        if error_rate >= 0.11:
            return 0.0
        return raw_rate * (1.0 - 2.0 * error_rate)


class QuantumCryptography:
    """
    Unified quantum cryptography controller.
    """
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.e91 = E91Protocol()
        self.amplification = PrivacyAmplification()
        self.security = SecurityAnalyzer()
    
    def generate_key(self, num_bits: int = 100) -> QKDKey:
        """
        Generate quantum key.
        
        Args:
            num_bits: Number of bits
        
        Returns:
            QKD key
        """
        alice_bits, alice_bases = self.bb84.generate_raw_key(num_bits)
        states = self.bb84.encode(alice_bits, alice_bases)
        
        bob_bases = [random.choice(["Z", "X"]) for _ in range(num_bits)]
        bob_bits = self.bb84.measure(states, bob_bases)
        
        key, error_rate = self.bb84.sift_key(alice_bases, bob_bases, alice_bits, bob_bits)
        
        return QKDKey(key, len(key), error_rate)
    
    def qc_summary(self) -> Dict:
        """Get summary."""
        return {
            "protocols": ["BB84", "E91"],
            "methods": ["privacy_amplification", "CHSH_test", "security_analysis"],
            "num_qubits": 1
        }
