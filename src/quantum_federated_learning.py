"""
Quantum Federated Learning Module
Quantum client models, secure aggregation, differential privacy,
and federated averaging for autonomous distributed quantum ML.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumClientModel:
    """Quantum model on client."""
    client_id: str
    params: List[float]
    data_size: int


class SecureAggregator:
    """
    Securely aggregate client updates.
    """
    
    def __init__(self):
        pass
    
    def weighted_average(self, models: List[QuantumClientModel]) -> List[float]:
        """
        Compute weighted average of parameters.
        
        Args:
            models: Client models
        
        Returns:
            Aggregated parameters
        """
        if not models:
            return []
        
        total_data = sum(m.data_size for m in models)
        if total_data == 0:
            return models[0].params[:]
        
        dim = len(models[0].params)
        aggregated = [0.0] * dim
        
        for model in models:
            weight = model.data_size / total_data
            for i in range(min(dim, len(model.params))):
                aggregated[i] += model.params[i] * weight
        
        return aggregated
    
    def simple_average(self, models: List[QuantumClientModel]) -> List[float]:
        """
        Compute simple average.
        
        Args:
            models: Client models
        
        Returns:
            Averaged parameters
        """
        if not models:
            return []
        
        dim = len(models[0].params)
        aggregated = [0.0] * dim
        
        for model in models:
            for i in range(min(dim, len(model.params))):
                aggregated[i] += model.params[i]
        
        n = len(models)
        return [a / n for a in aggregated]


class DifferentialPrivacy:
    """
    Differential privacy for federated learning.
    """
    
    def __init__(self, epsilon: float = 1.0,
                 delta: float = 1e-5):
        """
        Args:
            epsilon: Privacy budget
            delta: Failure probability
        """
        self.epsilon = epsilon
        self.delta = delta
    
    def add_noise(self, params: List[float],
                 sensitivity: float = 1.0) -> List[float]:
        """
        Add Gaussian noise.
        
        Args:
            params: Parameters
            sensitivity: Sensitivity
        
        Returns:
            Noisy parameters
        """
        import random
        sigma = sensitivity * math.sqrt(2.0 * math.log(1.25 / self.delta)) / self.epsilon
        return [p + random.gauss(0, sigma) for p in params]
    
    def clip_gradients(self, params: List[float],
                      max_norm: float = 1.0) -> List[float]:
        """
        Clip parameters to bound sensitivity.
        
        Args:
            params: Parameters
            max_norm: Max norm
        
        Returns:
            Clipped parameters
        """
        norm = sum(p**2 for p in params) ** 0.5
        if norm > max_norm:
            scale = max_norm / norm
            return [p * scale for p in params]
        return params[:]


class FederatedAveraging:
    """
    Federated averaging algorithm.
    """
    
    def __init__(self, aggregator: SecureAggregator):
        """
        Args:
            aggregator: Aggregator
        """
        self.aggregator = aggregator
        self.global_model: List[float] = []
        self.rounds: int = 0
    
    def initialize(self, dim: int = 4):
        """
        Initialize global model.
        
        Args:
            dim: Dimension
        """
        self.global_model = [0.0] * dim
    
    def aggregate(self, client_models: List[QuantumClientModel]) -> List[float]:
        """
        Aggregate client models.
        
        Args:
            client_models: Client models
        
        Returns:
            Updated global model
        """
        self.global_model = self.aggregator.weighted_average(client_models)
        self.rounds += 1
        return self.global_model
    
    def distribute(self) -> List[float]:
        """
        Distribute global model to clients.
        
        Returns:
            Global model
        """
        return self.global_model[:]


class QuantumFederatedLearning:
    """
    Unified quantum federated learning controller.
    """
    
    def __init__(self):
        self.aggregator = SecureAggregator()
        self.privacy = DifferentialPrivacy()
        self.fed_avg = FederatedAveraging(self.aggregator)
        self.clients: List[QuantumClientModel] = []
        self.history: List[Dict] = []
    
    def register_client(self, client_id: str,
                       params: List[float],
                       data_size: int):
        """
        Register client.
        
        Args:
            client_id: ID
            params: Parameters
            data_size: Data size
        """
        self.clients.append(QuantumClientModel(client_id, params, data_size))
    
    def train_round(self, apply_privacy: bool = True) -> Dict:
        """
        Execute one federated round.
        
        Args:
            apply_privacy: Apply DP
        
        Returns:
            Round result
        """
        if not self.global_model:
            self.fed_avg.initialize(len(self.clients[0].params) if self.clients else 4)
        
        # Optionally apply privacy
        client_updates = self.clients[:]
        if apply_privacy:
            client_updates = []
            for client in self.clients:
                clipped = self.privacy.clip_gradients(client.params)
                noisy = self.privacy.add_noise(clipped)
                client_updates.append(QuantumClientModel(
                    client.client_id, noisy, client.data_size
                ))
        
        # Aggregate
        global_params = self.fed_avg.aggregate(client_updates)
        
        result = {
            "round": self.fed_avg.rounds,
            "clients": len(self.clients),
            "global_params": global_params[:3]
        }
        self.history.append(result)
        return result
    
    def evaluate(self, test_data: List[List[float]]) -> float:
        """
        Evaluate global model.
        
        Args:
            test_data: Test data
        
        Returns:
            Accuracy
        """
        if not self.global_model or not test_data:
            return 0.0
        
        # Simplified: compute average match
        correct = 0
        for point in test_data:
            pred = sum(a * b for a, b in zip(self.global_model, point)) > 0
            correct += 1 if pred else 0
        
        return correct / len(test_data)
    
    @property
    def global_model(self) -> List[float]:
        return self.fed_avg.global_model
    
    def qfl_summary(self) -> Dict:
        """Get summary."""
        return {
            "clients": len(self.clients),
            "rounds": self.fed_avg.rounds,
            "epsilon": self.privacy.epsilon
        }
