"""
Quantum Order Finding Module
Modular exponentiation, period finding, and order estimation
for autonomous quantum factoring and cryptography.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ModularArithmetic:
    """
    Classical modular arithmetic operations.
    """
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """
        Compute greatest common divisor.
        
        Args:
            a, b: Integers
        
        Returns:
            GCD
        """
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def mod_exp(base: int, exp: int, mod: int) -> int:
        """
        Compute base^exp mod mod.
        
        Args:
            base: Base
            exp: Exponent
            mod: Modulus
        
        Returns:
            Result
        """
        if mod == 1:
            return 0
        result = 1
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp >>= 1
        return result
    
    @staticmethod
    def order(a: int, N: int) -> int:
        """
        Find multiplicative order of a mod N classically.
        
        Args:
            a: Base
            N: Modulus
        
        Returns:
            Order r where a^r = 1 mod N
        """
        if ModularArithmetic.gcd(a, N) != 1:
            return 0
        
        r = 1
        current = a % N
        while current != 1:
            current = (current * a) % N
            r += 1
            if r > N:
                return 0
        return r


class PhaseEstimator:
    """
    Quantum phase estimation for order finding.
    """
    
    def __init__(self, num_precision_qubits: int = 8):
        """
        Args:
            num_precision_qubits: Number of precision qubits
        """
        self.precision = num_precision_qubits
    
    def estimate_phase(self, a: int, N: int) -> float:
        """
        Estimate phase fraction j/r.
        
        Args:
            a: Base
            N: Modulus
        
        Returns:
            Estimated phase [0, 1)
        """
        # Classical simulation of QPE for order finding
        # The eigenvalue phase is j/r for some random j
        r = ModularArithmetic.order(a, N)
        if r == 0:
            return 0.0
        
        # Random j coprime to r
        import random
        j = random.randint(1, r - 1)
        while ModularArithmetic.gcd(j, r) != 1 and r > 1:
            j = random.randint(1, r - 1)
        
        phase = j / r
        
        # Add quantization noise based on precision
        delta = 1.0 / (2**self.precision)
        phase += random.uniform(-delta, delta)
        phase = phase % 1.0
        
        return phase
    
    def continued_fraction(self, phase: float,
                          max_denominator: int) -> Tuple[int, int]:
        """
        Compute continued fraction convergent.
        
        Args:
            phase: Phase estimate
            max_denominator: Maximum denominator
        
        Returns:
            (numerator, denominator)
        """
        if phase <= 0:
            return 0, 1
        
        # Simple continued fraction
        x = phase
        a0 = int(x)
        x = x - a0
        
        if x < 1e-10:
            return a0, 1
        
        # First convergent
        a1 = int(1.0 / x)
        num = a0 * a1 + 1
        den = a1
        
        if den > max_denominator:
            return a0, 1
        
        return num, den


class OrderFinder:
    """
    Order finding using classical + quantum methods.
    """
    
    def __init__(self):
        self.pe = PhaseEstimator()
        self.results: List[Dict] = []
    
    def classical_order(self, a: int, N: int) -> int:
        """
        Find order classically.
        
        Args:
            a: Base
            N: Modulus
        
        Returns:
            Order r
        """
        return ModularArithmetic.order(a, N)
    
    def quantum_order(self, a: int, N: int) -> int:
        """
        Find order using quantum phase estimation.
        
        Args:
            a: Base
            N: Modulus
        
        Returns:
            Estimated order
        """
        if ModularArithmetic.gcd(a, N) != 1:
            return 0
        
        phase = self.pe.estimate_phase(a, N)
        num, den = self.pe.continued_fraction(phase, N)
        
        if den <= 0:
            return 0
        
        # Verify: a^r = 1 mod N
        if ModularArithmetic.mod_exp(a, den, N) == 1:
            return den
        
        # Try multiples
        for k in range(1, 10):
            r = den * k
            if r > N:
                break
            if ModularArithmetic.mod_exp(a, r, N) == 1:
                return r
        
        return den
    
    def find_order(self, a: int, N: int,
                  method: str = "quantum") -> Dict:
        """
        Find order with chosen method.
        
        Args:
            a: Base
            N: Modulus
            method: "classical" or "quantum"
        
        Returns:
            Results dict
        """
        if method == "classical":
            r = self.classical_order(a, N)
        else:
            r = self.quantum_order(a, N)
        
        result = {
            "a": a,
            "N": N,
            "order": r,
            "verified": ModularArithmetic.mod_exp(a, r, N) == 1 if r > 0 else False
        }
        self.results.append(result)
        return result
    
    def factor_from_order(self, a: int, N: int,
                         r: int) -> Optional[Tuple[int, int]]:
        """
        Extract factors from order.
        
        Args:
            a: Base
            N: Modulus
            r: Order
        
        Returns:
            Factors (p, q) or None
        """
        if r <= 0 or r % 2 != 0:
            return None
        
        # Check a^(r/2) +/- 1
        x = ModularArithmetic.mod_exp(a, r // 2, N)
        
        p = ModularArithmetic.gcd(x - 1, N)
        q = ModularArithmetic.gcd(x + 1, N)
        
        if p > 1 and p < N and N % p == 0:
            return p, N // p
        if q > 1 and q < N and N % q == 0:
            return q, N // q
        
        return None


class QuantumOrderFinding:
    """
    Unified quantum order finding controller.
    """
    
    def __init__(self):
        self.finder = OrderFinder()
    
    def solve(self, N: int, method: str = "quantum") -> Dict:
        """
        Attempt to factor N.
        
        Args:
            N: Number to factor
            method: Method
        
        Returns:
            Results
        """
        if N <= 1:
            return {"status": "invalid_input"}
        
        # Random base
        import random
        a = random.randint(2, N - 1)
        
        g = ModularArithmetic.gcd(a, N)
        if g > 1:
            return {
                "N": N,
                "a": a,
                "factors": (g, N // g),
                "method": "gcd"
            }
        
        result = self.finder.find_order(a, N, method)
        r = result["order"]
        
        factors = self.finder.factor_from_order(a, N, r)
        
        return {
            "N": N,
            "a": a,
            "order": r,
            "factors": factors,
            "verified": result["verified"]
        }
    
    def order_finding_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.finder.results),
            "successful": sum(1 for r in self.finder.results if r["verified"])
        }
