"""
Quantum Differential Privacy Module
Quantum noise addition, privacy accounting, quantum mechanism
composition, and adaptive budget allocation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PrivacyBudget:
    """Privacy budget state."""
    epsilon: float
    delta: float
    consumed_epsilon: float = 0.0
    consumed_delta: float = 0.0


class QuantumNoiseGenerator:
    """
    Generate quantum-inspired noise.
    """
    
    def __init__(self):
        pass
    
    def gaussian_noise(self, dimension: int,
                      std: float) -> List[float]:
        """
        Generate Gaussian noise.
        
        Args:
            dimension: Dimension
            std: Standard deviation
        
        Returns:
            Noise vector
        """
        import random
        return [random.gauss(0, std) for _ in range(dimension)]
    
    def laplace_noise(self, dimension: int,
                     scale: float) -> List[float]:
        """
        Generate Laplace noise.
        
        Args:
            dimension: Dimension
            scale: Scale
        
        Returns:
            Noise vector
        """
        import random
        return [self._laplace_random(0, scale) for _ in range(dimension)]
    
    def _laplace_random(self, mu: float, b: float) -> float:
        """Generate Laplace random variable."""
        import random
        u = random.random() - 0.5
        return mu - b * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))
    
    def quantum_coherent_noise(self, dimension: int,
                               amplitude: float) -> List[complex]:
        """
        Generate quantum coherent state noise.
        
        Args:
            dimension: Dimension
            amplitude: Amplitude
        
        Returns:
            Complex noise
        """
        import random
        noise = []
        for _ in range(dimension):
            phase = random.uniform(0, 2.0 * math.pi)
            noise.append(amplitude * complex(math.cos(phase), math.sin(phase)))
        return noise


class PrivacyAccountant:
    """
    Track privacy budget consumption.
    """
    
    def __init__(self, budget: PrivacyBudget):
        """
        Args:
            budget: Privacy budget
        """
        self.budget = budget
    
    def compose_gaussian(self, sigma: float,
                        sensitivity: float = 1.0,
                        num_queries: int = 1) -> float:
        """
        Compose Gaussian mechanism.
        
        Args:
            sigma: Noise std
            sensitivity: Sensitivity
            num_queries: Number of queries
        
        Returns:
            Consumed epsilon
        """
        if sigma <= 0:
            return float('inf')
        
        # Simplified moment accountant
        epsilon_per_query = sensitivity / sigma
        total_epsilon = epsilon_per_query * math.sqrt(num_queries)
        
        self.budget.consumed_epsilon += total_epsilon
        self.budget.consumed_delta += num_queries * self.budget.delta
        
        return total_epsilon
    
    def remaining_budget(self) -> Tuple[float, float]:
        """
        Get remaining budget.
        
        Returns:
            (epsilon, delta)
        """
        eps = max(0.0, self.budget.epsilon - self.budget.consumed_epsilon)
        delta = max(0.0, self.budget.delta - self.budget.consumed_delta)
        return eps, delta
    
    def is_exhausted(self) -> bool:
        """
        Check if budget exhausted.
        
        Returns:
            True if exhausted
        """
        eps, delta = self.remaining_budget()
        return eps <= 0 or delta <= 0


class QuantumMechanismComposer:
    """
    Compose quantum DP mechanisms.
    """
    
    def __init__(self):
        pass
    
    def compose(self, epsilons: List[float],
               deltas: List[float]) -> Tuple[float, float]:
        """
        Compose multiple mechanisms.
        
        Args:
            epsilons: Epsilon values
            deltas: Delta values
        
        Returns:
            (total_epsilon, total_delta)
        """
        # Advanced composition
        total_eps = sum(epsilons)
        total_delta = sum(deltas)
        
        # Apply sqrt k composition
        k = len(epsilons)
        if k > 1:
            total_eps = math.sqrt(k) * max(epsilons) if epsilons else 0.0
        
        return total_eps, total_delta
    
    def adaptive_budget(self, queries: List[Dict],
                       total_epsilon: float,
                       total_delta: float) -> List[float]:
        """
        Adaptively allocate budget.
        
        Args:
            queries: Query importance weights
            total_epsilon: Total epsilon
            total_delta: Total delta
        
        Returns:
            Allocated epsilons
        """
        weights = [q.get("weight", 1.0) for q in queries]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return [total_epsilon / len(queries)] * len(queries)
        
        return [total_epsilon * w / total_weight for w in weights]


class QuantumDifferentialPrivacy:
    """
    Unified quantum DP controller.
    """
    
    def __init__(self, epsilon: float = 1.0,
                 delta: float = 1e-5):
        """
        Args:
            epsilon: Privacy budget
            delta: Failure probability
        """
        self.noise_gen = QuantumNoiseGenerator()
        self.budget = PrivacyBudget(epsilon, delta)
        self.accountant = PrivacyAccountant(self.budget)
        self.composer = QuantumMechanismComposer()
        self.history: List[Dict] = []
    
    def add_noise(self, params: List[float],
                 mechanism: str = "gaussian",
                 sensitivity: float = 1.0) -> List[float]:
        """
        Add DP noise.
        
        Args:
            params: Parameters
            mechanism: Noise type
            sensitivity: Sensitivity
        
        Returns:
            Noisy parameters
        """
        dim = len(params)
        
        if mechanism == "gaussian":
            sigma = sensitivity * math.sqrt(2.0 * math.log(1.25 / self.budget.delta)) / self.budget.epsilon
            noise = self.noise_gen.gaussian_noise(dim, sigma)
            self.accountant.compose_gaussian(sigma, sensitivity)
        elif mechanism == "laplace":
            scale = sensitivity / self.budget.epsilon
            noise = self.noise_gen.laplace_noise(dim, scale)
        else:
            noise = [0.0] * dim
        
        result = [p + n for p, n in zip(params, noise)]
        
        self.history.append({
            "mechanism": mechanism,
            "consumed_eps": self.accountant.budget.consumed_epsilon
        })
        
        return result
    
    def remaining(self) -> Tuple[float, float]:
        """Get remaining budget."""
        return self.accountant.remaining_budget()
    
    def qdp_summary(self) -> Dict:
        """Get summary."""
        eps, delta = self.remaining()
        return {
            "initial_epsilon": self.budget.epsilon,
            "consumed_epsilon": self.budget.consumed_epsilon,
            "remaining_epsilon": eps,
            "remaining_delta": delta,
            "queries": len(self.history)
        }
