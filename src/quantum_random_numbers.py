"""
Quantum Random Number Generation Module
QRNG, entropy extraction, randomness testing,
Hadamard-based generation, and bitstring generation for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RandomBitstring:
    """Random bitstring result."""
    bits: str
    length: int
    entropy_estimate: float


class HadamardQRNG:
    """
    Hadamard-based quantum random number generator.
    """
    
    def __init__(self, num_qubits: int = 8):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.num_qubits = num_qubits
    
    def generate_bits(self, num_bits: int) -> str:
        """
        Generate random bitstring.
        
        Args:
            num_bits: Number of bits
        
        Returns:
            Bitstring
        """
        bits_per_shot = self.num_qubits
        num_shots = (num_bits + bits_per_shot - 1) // bits_per_shot
        
        result = []
        for _ in range(num_shots):
            # Simulate Hadamard superposition measurement
            shot = ""
            for _ in range(bits_per_shot):
                shot += "1" if random.random() < 0.5 else "0"
            result.append(shot)
        
        return "".join(result)[:num_bits]
    
    def generate_integers(self, count: int,
                         max_value: int) -> List[int]:
        """
        Generate random integers.
        
        Args:
            count: Number of integers
            max_value: Maximum value (exclusive)
        
        Returns:
            Random integers
        """
        num_bits = max_value.bit_length()
        result = []
        
        for _ in range(count):
            bits = self.generate_bits(num_bits)
            val = int(bits, 2)
            if val < max_value:
                result.append(val)
            else:
                result.append(val % max_value)
        
        return result


class EntropyExtractor:
    """
    Entropy extraction from raw randomness.
    """
    
    def __init__(self):
        pass
    
    def von_neumann_extractor(self, raw_bits: str) -> str:
        """
        Von Neumann entropy extractor.
        
        Args:
            raw_bits: Raw bitstring
        
        Returns:
            Extracted bits
        """
        result = []
        for i in range(0, len(raw_bits) - 1, 2):
            pair = raw_bits[i:i + 2]
            if pair == "01":
                result.append("0")
            elif pair == "10":
                result.append("1")
        return "".join(result)
    
    def parity_extractor(self, raw_bits: str,
                        block_size: int = 4) -> str:
        """
        Parity-based extractor.
        
        Args:
            raw_bits: Raw bitstring
            block_size: Block size
        
        Returns:
            Extracted bits
        """
        result = []
        for i in range(0, len(raw_bits), block_size):
            block = raw_bits[i:i + block_size]
            parity = sum(int(b) for b in block) % 2
            result.append(str(parity))
        return "".join(result)
    
    def estimate_entropy(self, bitstring: str) -> float:
        """
        Estimate Shannon entropy per bit.
        
        Args:
            bitstring: Bitstring
        
        Returns:
            Entropy in bits
        """
        if not bitstring:
            return 0.0
        
        n = len(bitstring)
        p1 = bitstring.count("1") / n
        p0 = 1.0 - p1
        
        entropy = 0.0
        for p in [p0, p1]:
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy


class RandomnessTester:
    """
    Statistical randomness tests.
    """
    
    def __init__(self):
        pass
    
    def frequency_test(self, bitstring: str) -> float:
        """
        Frequency (monobit) test.
        
        Args:
            bitstring: Bitstring
        
        Returns:
            P-value
        """
        n = len(bitstring)
        if n == 0:
            return 0.0
        
        s = sum(2 * int(b) - 1 for b in bitstring)
        s_obs = abs(s) / math.sqrt(n)
        
        # P-value from erfc approximation
        return math.erfc(s_obs / math.sqrt(2))
    
    def runs_test(self, bitstring: str) -> Tuple[int, float]:
        """
        Runs test.
        
        Args:
            bitstring: Bitstring
        
        Returns:
            (number of runs, expected runs)
        """
        if not bitstring:
            return (0, 0.0)
        
        n = len(bitstring)
        n1 = bitstring.count("1")
        n0 = n - n1
        
        if n0 == 0 or n1 == 0:
            return (1, 0.0)
        
        runs = 1
        for i in range(1, n):
            if bitstring[i] != bitstring[i - 1]:
                runs += 1
        
        expected = (2.0 * n0 * n1) / n + 1.0
        
        return (runs, expected)
    
    def longest_run_test(self, bitstring: str) -> int:
        """
        Find longest run of identical bits.
        
        Args:
            bitstring: Bitstring
        
        Returns:
            Longest run length
        """
        if not bitstring:
            return 0
        
        max_run = 1
        current = 1
        
        for i in range(1, len(bitstring)):
            if bitstring[i] == bitstring[i - 1]:
                current += 1
                max_run = max(max_run, current)
            else:
                current = 1
        
        return max_run


class QuantumRandomNumbers:
    """
    Unified quantum random number generation controller.
    """
    
    def __init__(self, num_qubits: int = 8):
        self.hadamard = HadamardQRNG(num_qubits)
        self.extractor = EntropyExtractor()
        self.tester = RandomnessTester()
    
    def generate(self, num_bits: int,
                extract: bool = False) -> RandomBitstring:
        """
        Generate random bits.
        
        Args:
            num_bits: Number of bits
            extract: Whether to apply entropy extraction
        
        Returns:
            Random bitstring
        """
        raw = self.hadamard.generate_bits(num_bits * 4 if extract else num_bits)
        
        if extract:
            bits = self.extractor.von_neumann_extractor(raw)
            if len(bits) < num_bits:
                bits = self.hadamard.generate_bits(num_bits)
        else:
            bits = raw[:num_bits]
        
        entropy = self.extractor.estimate_entropy(bits)
        
        return RandomBitstring(bits, len(bits), entropy)
    
    def test_randomness(self, bitstring: str) -> Dict:
        """
        Test randomness.
        
        Args:
            bitstring: Bitstring
        
        Returns:
            Test results
        """
        runs, expected = self.tester.runs_test(bitstring)
        
        return {
            "frequency_pvalue": self.tester.frequency_test(bitstring),
            "runs": runs,
            "expected_runs": expected,
            "longest_run": self.tester.longest_run_test(bitstring),
            "entropy": self.extractor.estimate_entropy(bitstring)
        }
    
    def qrn_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["hadamard", "von_neumann", "parity"],
            "tests": ["frequency", "runs", "longest_run"],
            "num_qubits": self.hadamard.num_qubits
        }
