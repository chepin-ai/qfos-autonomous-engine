"""
Quantum Cryptography Module
BB84 protocol, quantum key distribution, quantum random number generation,
quantum secure direct communication, and quantum authentication.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumKey:
    """Quantum key."""
    bits: List[int]
    basis: List[str]
    length: int


class BB84Protocol:
    """
    BB84 quantum key distribution protocol.
    """
    
    def __init__(self):
        self.alice_bits: List[int] = []
        self.alice_basis: List[str] = []
        self.bob_basis: List[str] = []
        self.bob_results: List[int] = []
    
    def generate_bits(self, n: int) -> List[int]:
        """
        Generate random bits.
        
        Args:
            n: Number of bits
        
        Returns:
            Random bits
        """
        return [random.randint(0, 1) for _ in range(n)]
    
    def generate_basis(self, n: int) -> List[str]:
        """
        Generate random basis (rectilinear or diagonal).
        
        Args:
            n: Number
        
        Returns:
            Basis choices
        """
        return [random.choice(["+", "X"]) for _ in range(n)]
    
    def prepare_qubits(self, bits: List[int],
                      basis: List[str]) -> List[str]:
        """
        Prepare quantum states.
        
        Args:
            bits: Bits
            basis: Basis
        
        Returns:
            State descriptions
        """
        states = []
        for b, base in zip(bits, basis):
            if base == "+":
                states.append("|0>" if b == 0 else "|1>")
            else:
                states.append("|+>" if b == 0 else "|->")
        return states
    
    def measure_qubits(self, states: List[str],
                      basis: List[str]) -> List[int]:
        """
        Measure qubits.
        
        Args:
            states: States
            basis: Measurement basis
        
        Returns:
            Measurement results
        """
        results = []
        for state, base in zip(states, basis):
            if base == "+":
                if state in ["|0>", "|+>"]:
                    results.append(0)
                elif state in ["|1>", "|->"]:
                    results.append(1)
                else:
                    results.append(random.randint(0, 1))
            else:
                if state in ["|0>", "|->"]:
                    results.append(0)
                elif state in ["|1>", "|+>"]:
                    results.append(1)
                else:
                    results.append(random.randint(0, 1))
        return results
    
    def sift_key(self, alice_basis: List[str],
                bob_basis: List[str],
                bob_results: List[int]) -> List[int]:
        """
        Sift key by matching basis.
        
        Args:
            alice_basis: Alice's basis
            bob_basis: Bob's basis
            bob_results: Bob's results
        
        Returns:
            Sifted key
        """
        key = []
        for ab, bb, br in zip(alice_basis, bob_basis, bob_results):
            if ab == bb:
                key.append(br)
        return key
    
    def run_protocol(self, n: int = 100) -> QuantumKey:
        """
        Run full BB84 protocol.
        
        Args:
            n: Number of qubits
        
        Returns:
            Quantum key
        """
        self.alice_bits = self.generate_bits(n)
        self.alice_basis = self.generate_basis(n)
        self.bob_basis = self.generate_basis(n)
        
        states = self.prepare_qubits(self.alice_bits, self.alice_basis)
        self.bob_results = self.measure_qubits(states, self.bob_basis)
        
        key_bits = self.sift_key(self.alice_basis, self.bob_basis,
                                self.bob_results)
        
        return QuantumKey(
            bits=key_bits,
            basis=[b for b, ab in zip(self.bob_basis, self.alice_basis)
                   if b == ab],
            length=len(key_bits)
        )


class QuantumRandomNumberGenerator:
    """
    Quantum-inspired random number generator.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Args:
            seed: Random seed
        """
        if seed is not None:
            random.seed(seed)
    
    def random_bit(self) -> int:
        """
        Generate random bit.
        
        Returns:
            0 or 1
        """
        return random.randint(0, 1)
    
    def random_bits(self, n: int) -> List[int]:
        """
        Generate random bits.
        
        Args:
            n: Number of bits
        
        Returns:
            Bits
        """
        return [self.random_bit() for _ in range(n)]
    
    def random_float(self) -> float:
        """
        Generate random float [0, 1).
        
        Returns:
            Float
        """
        return random.random()


class QuantumSecureCommunication:
    """
    Quantum secure direct communication.
    """
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.key: Optional[QuantumKey] = None
    
    def establish_key(self, length: int = 128) -> QuantumKey:
        """
        Establish quantum key.
        
        Args:
            length: Key length
        
        Returns:
            Quantum key
        """
        # Need more qubits due to sifting
        n = length * 4
        self.key = self.bb84.run_protocol(n)
        return self.key
    
    def encrypt_message(self, message: str) -> List[int]:
        """
        Encrypt message with quantum key.
        
        Args:
            message: Message
        
        Returns:
            Ciphertext
        """
        if self.key is None or not self.key.bits:
            return []
        
        # Convert message to bits
        message_bits = []
        for char in message:
            for i in range(8):
                message_bits.append((ord(char) >> (7 - i)) & 1)
        
        # XOR with key
        ciphertext = []
        for i, bit in enumerate(message_bits):
            key_bit = self.key.bits[i % len(self.key.bits)]
            ciphertext.append(bit ^ key_bit)
        
        return ciphertext
    
    def decrypt_message(self, ciphertext: List[int]) -> str:
        """
        Decrypt message.
        
        Args:
            ciphertext: Ciphertext
        
        Returns:
            Message
        """
        if self.key is None or not self.key.bits:
            return ""
        
        # XOR with key
        plaintext_bits = []
        for i, bit in enumerate(ciphertext):
            key_bit = self.key.bits[i % len(self.key.bits)]
            plaintext_bits.append(bit ^ key_bit)
        
        # Convert bits to string
        chars = []
        for i in range(0, len(plaintext_bits), 8):
            byte = plaintext_bits[i:i+8]
            if len(byte) == 8:
                val = sum(b << (7 - j) for j, b in enumerate(byte))
                chars.append(chr(val))
        
        return "".join(chars)


class QuantumAuthentication:
    """
    Quantum authentication protocol.
    """
    
    def __init__(self):
        self.shared_key: Optional[QuantumKey] = None
    
    def generate_challenge(self, length: int = 64) -> List[int]:
        """
        Generate authentication challenge.
        
        Args:
            length: Challenge length
        
        Returns:
            Challenge bits
        """
        return [random.randint(0, 1) for _ in range(length)]
    
    def respond(self, challenge: List[int],
               key: QuantumKey) -> List[int]:
        """
        Generate response to challenge.
        
        Args:
            challenge: Challenge
            key: Shared key
        
        Returns:
            Response
        """
        response = []
        for i, c in enumerate(challenge):
            key_bit = key.bits[i % len(key.bits)]
            response.append(c ^ key_bit)
        return response
    
    def verify(self, challenge: List[int],
              response: List[int],
              key: QuantumKey) -> bool:
        """
        Verify response.
        
        Args:
            challenge: Challenge
            response: Response
            key: Shared key
        
        Returns:
            True if valid
        """
        expected = self.respond(challenge, key)
        return response == expected


class QuantumCryptography:
    """
    Unified quantum cryptography controller.
    """
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.qrng = QuantumRandomNumberGenerator()
        self.communication = QuantumSecureCommunication()
        self.authentication = QuantumAuthentication()
    
    def generate_secure_key(self, length: int = 128) -> QuantumKey:
        """
        Generate secure quantum key.
        
        Args:
            length: Key length
        
        Returns:
            Quantum key
        """
        return self.communication.establish_key(length)
    
    def secure_transmit(self, message: str) -> Tuple[List[int], QuantumKey]:
        """
        Securely transmit message.
        
        Args:
            message: Message
        
        Returns:
            (ciphertext, key)
        """
        key = self.generate_secure_key(len(message) * 8)
        self.communication.key = key
        ciphertext = self.communication.encrypt_message(message)
        return (ciphertext, key)
    
    def qcrypto_summary(self) -> Dict:
        """Get summary."""
        return {
            "protocols": ["BB84", "QRNG", "QSDC", "QAuth"],
            "key_length": self.communication.key.length if self.communication.key else 0
        }
