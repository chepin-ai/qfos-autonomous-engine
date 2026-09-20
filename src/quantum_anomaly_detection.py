"""
Quantum Anomaly Detection Module
Quantum state fidelity, variational anomaly classifier, quantum
principal component analysis, and threshold-based detection.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class QuantumStateEncoder:
    """
    Encode classical data to quantum states.
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Args:
            num_qubits: Qubits
        """
        self.n = num_qubits
    
    def encode(self, data: List[float]) -> List[complex]:
        """
        Encode data to quantum state.
        
        Args:
            data: Data point
        
        Returns:
            Quantum state
        """
        dim = 2 ** self.n
        state = [complex(0, 0)] * dim
        
        # Amplitude encoding
        for i, val in enumerate(data[:dim]):
            state[i] = complex(val, 0)
        
        # Normalize
        norm = sum(abs(z)**2 for z in state) ** 0.5
        if norm > 0:
            state = [z / norm for z in state]
        
        return state


class QuantumFidelity:
    """
    Compute quantum state fidelity.
    """
    
    def __init__(self):
        pass
    
    def fidelity(self, state1: List[complex],
                state2: List[complex]) -> float:
        """
        Compute fidelity.
        
        Args:
            state1: State 1
            state2: State 2
        
        Returns:
            Fidelity
        """
        overlap = sum(s1.conjugate() * s2 for s1, s2 in zip(state1, state2))
        return abs(overlap) ** 2
    
    def average_fidelity(self, test_state: List[complex],
                        reference_states: List[List[complex]]) -> float:
        """
        Compute average fidelity with reference states.
        
        Args:
            test_state: Test state
            reference_states: Reference states
        
        Returns:
            Average fidelity
        """
        if not reference_states:
            return 0.0
        
        fidelities = [self.fidelity(test_state, ref) for ref in reference_states]
        return sum(fidelities) / len(fidelities)


class QuantumPCA:
    """
    Quantum principal component analysis.
    """
    
    def __init__(self, num_components: int = 2):
        """
        Args:
            num_components: Components
        """
        self.k = num_components
    
    def covariance(self, data: List[List[float]]) -> List[List[float]]:
        """
        Compute covariance matrix.
        
        Args:
            data: Dataset
        
        Returns:
            Covariance matrix
        """
        n = len(data)
        dim = len(data[0]) if data else 0
        
        means = [sum(d[i] for d in data) / n for i in range(dim)]
        
        cov = [[0.0] * dim for _ in range(dim)]
        for i in range(dim):
            for j in range(dim):
                cov[i][j] = sum((d[i] - means[i]) * (d[j] - means[j])
                               for d in data) / n
        
        return cov
    
    def transform(self, data: List[List[float]]) -> List[List[float]]:
        """
        Transform data to principal components.
        
        Args:
            data: Dataset
        
        Returns:
            Transformed data
        """
        cov = self.covariance(data)
        dim = len(cov)
        
        # Simplified: use first k dimensions as PCs
        transformed = []
        for point in data:
            t = point[:self.k]
            if len(t) < self.k:
                t = t + [0.0] * (self.k - len(t))
            transformed.append(t)
        
        return transformed


class VariationalAnomalyClassifier:
    """
    Variational quantum anomaly classifier.
    """
    
    def __init__(self, threshold: float = 0.5):
        """
        Args:
            threshold: Anomaly threshold
        """
        self.threshold = threshold
        self.encoder = QuantumStateEncoder()
        self.fidelity = QuantumFidelity()
        self.normal_states: List[List[complex]] = []
    
    def train(self, normal_data: List[List[float]]):
        """
        Train on normal data.
        
        Args:
            normal_data: Normal data
        """
        self.normal_states = [self.encoder.encode(d) for d in normal_data]
    
    def predict(self, data: List[float]) -> Tuple[int, float]:
        """
        Predict anomaly.
        
        Args:
            data: Data point
        
        Returns:
            (is_anomaly, score)
        """
        state = self.encoder.encode(data)
        avg_fid = self.fidelity.average_fidelity(state, self.normal_states)
        
        # Low fidelity = anomaly
        score = 1.0 - avg_fid
        is_anomaly = 1 if score > self.threshold else 0
        
        return (is_anomaly, score)


class QuantumAnomalyDetection:
    """
    Unified quantum anomaly detection controller.
    """
    
    def __init__(self):
        self.encoder = QuantumStateEncoder()
        self.fidelity = QuantumFidelity()
        self.qpca = QuantumPCA()
        self.classifier = VariationalAnomalyClassifier()
        self.results: List[Dict] = []
    
    def fit(self, normal_data: List[List[float]]):
        """
        Fit on normal data.
        
        Args:
            normal_data: Normal data
        """
        # Reduce dimensions
        reduced = self.qpca.transform(normal_data)
        self.classifier.train(reduced)
    
    def detect(self, test_data: List[List[float]]) -> List[Tuple[int, float]]:
        """
        Detect anomalies.
        
        Args:
            test_data: Test data
        
        Returns:
            Predictions
        """
        reduced = self.qpca.transform(test_data)
        predictions = []
        
        for point in reduced:
            pred = self.classifier.predict(point)
            predictions.append(pred)
            self.results.append({
                "is_anomaly": pred[0],
                "score": pred[1]
            })
        
        return predictions
    
    def qad_summary(self) -> Dict:
        """Get summary."""
        anomalies = sum(1 for r in self.results if r["is_anomaly"] == 1)
        return {
            "total_tests": len(self.results),
            "anomalies": anomalies,
            "normal": len(self.results) - anomalies,
            "threshold": self.classifier.threshold
        }
