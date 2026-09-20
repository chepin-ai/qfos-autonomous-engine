"""
Quantum Feature Map Module
Quantum-inspired feature encoding, kernel mapping,
and Hilbert space embedding for autonomous machine learning.
"""

import math
import random
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass


class PauliFeatureMap:
    """
    Pauli feature map for quantum encoding.
    """
    
    def __init__(self, feature_dim: int, reps: int = 2):
        """
        Args:
            feature_dim: Input feature dimension
            reps: Repetitions
        """
        self.feature_dim = feature_dim
        self.reps = reps
    
    def encode(self, features: List[float]) -> List[complex]:
        """
        Encode features into quantum amplitudes.
        
        Args:
            features: Input features
        
        Returns:
            Complex amplitudes
        """
        dim = min(len(features), self.feature_dim)
        amplitudes = []
        
        for rep in range(self.reps):
            for i in range(dim):
                x = features[i]
                # Pauli rotation: e^{i * x * Z}
                phase = x * math.pi * (rep + 1)
                amplitude = complex(math.cos(phase), math.sin(phase))
                amplitudes.append(amplitude)
        
        return amplitudes
    
    def kernel(self, x: List[float], y: List[float]) -> float:
        """
        Compute quantum kernel K(x, y) = |<phi(x)|phi(y)>|^2.
        
        Args:
            x: First feature
            y: Second feature
        
        Returns:
            Kernel value
        """
        phi_x = self.encode(x)
        phi_y = self.encode(y)
        
        # Inner product
        inner = sum(phi_x[i].conjugate() * phi_y[i] for i in range(min(len(phi_x), len(phi_y))))
        
        # Normalization
        norm_x = sum(abs(z)**2 for z in phi_x)
        norm_y = sum(abs(z)**2 for z in phi_y)
        if norm_x <= 0 or norm_y <= 0:
            return 0.0
        
        return abs(inner) ** 2 / (norm_x * norm_y)


class ZZFeatureMap:
    """
    ZZ interaction feature map.
    """
    
    def __init__(self, feature_dim: int, reps: int = 1):
        """
        Args:
            feature_dim: Input dimension
            reps: Repetitions
        """
        self.feature_dim = feature_dim
        self.reps = reps
    
    def encode(self, features: List[float]) -> List[complex]:
        """
        Encode with ZZ interactions.
        
        Args:
            features: Input
        
        Returns:
            Amplitudes
        """
        dim = min(len(features), self.feature_dim)
        amplitudes = []
        
        for rep in range(self.reps):
            # Single qubit rotations
            for i in range(dim):
                phase = features[i] * math.pi
                amplitudes.append(complex(math.cos(phase), math.sin(phase)))
            
            # ZZ interactions
            for i in range(dim):
                for j in range(i + 1, dim):
                    zz_phase = (math.pi - features[i]) * (math.pi - features[j])
                    amplitudes.append(complex(math.cos(zz_phase), math.sin(zz_phase)))
        
        return amplitudes
    
    def kernel(self, x: List[float], y: List[float]) -> float:
        """
        Compute ZZ kernel.
        
        Args:
            x: First
            y: Second
        
        Returns:
            Kernel value
        """
        phi_x = self.encode(x)
        phi_y = self.encode(y)
        inner = sum(phi_x[i].conjugate() * phi_y[i] for i in range(min(len(phi_x), len(phi_y))))
        
        norm_x = sum(abs(z)**2 for z in phi_x)
        norm_y = sum(abs(z)**2 for z in phi_y)
        if norm_x <= 0 or norm_y <= 0:
            return 0.0
        
        return abs(inner) ** 2 / (norm_x * norm_y)


class QuantumKernelMatrix:
    """
    Compute quantum kernel matrix for dataset.
    """
    
    def __init__(self, feature_map: PauliFeatureMap):
        """
        Args:
            feature_map: Feature map
        """
        self.feature_map = feature_map
    
    def compute(self, X: List[List[float]]) -> List[List[float]]:
        """
        Compute kernel matrix K[i,j] = K(x_i, x_j).
        
        Args:
            X: Dataset
        
        Returns:
            Kernel matrix
        """
        n = len(X)
        K = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i, n):
                k = self.feature_map.kernel(X[i], X[j])
                K[i][j] = k
                K[j][i] = k
        
        return K
    
    def center(self, K: List[List[float]]) -> List[List[float]]:
        """
        Center kernel matrix.
        
        Args:
            K: Kernel matrix
        
        Returns:
            Centered matrix
        """
        n = len(K)
        if n == 0:
            return K
        
        row_means = [sum(row) / n for row in K]
        total_mean = sum(row_means) / n
        
        centered = []
        for i in range(n):
            row = []
            for j in range(n):
                row.append(K[i][j] - row_means[i] - row_means[j] + total_mean)
            centered.append(row)
        
        return centered


class QuantumFeatureEncoder:
    """
    Encode classical features into quantum Hilbert space.
    """
    
    def __init__(self, feature_map: str = "pauli", feature_dim: int = 4):
        """
        Args:
            feature_map: "pauli" or "zz"
            feature_dim: Dimension
        """
        if feature_map.lower() == "zz":
            self.mapper = ZZFeatureMap(feature_dim)
        else:
            self.mapper = PauliFeatureMap(feature_dim)
        self.kernel_matrix = QuantumKernelMatrix(self.mapper)
    
    def transform(self, features: List[float]) -> List[complex]:
        """
        Transform features.
        
        Args:
            features: Input
        
        Returns:
            Quantum state
        """
        return self.mapper.encode(features)
    
    def similarity(self, x: List[float], y: List[float]) -> float:
        """
        Compute similarity.
        
        Args:
            x: First
            y: Second
        
        Returns:
            Similarity
        """
        return self.mapper.kernel(x, y)
    
    def kernel_matrix_for(self, X: List[List[float]]) -> List[List[float]]:
        """
        Compute kernel matrix.
        
        Args:
            X: Dataset
        
        Returns:
            Kernel matrix
        """
        return self.kernel_matrix.compute(X)


class QuantumFeatureMap:
    """
    Unified quantum feature map controller.
    """
    
    def __init__(self):
        self.encoder: Optional[QuantumFeatureEncoder] = None
        self.encoded_data: List[List[complex]] = []
    
    def build(self, feature_map: str = "pauli", feature_dim: int = 4):
        """
        Build feature map.
        
        Args:
            feature_map: Type
            feature_dim: Dimension
        """
        self.encoder = QuantumFeatureEncoder(feature_map, feature_dim)
    
    def encode_dataset(self, dataset: List[List[float]]):
        """
        Encode dataset.
        
        Args:
            dataset: Data
        """
        self.encoded_data = [self.encoder.transform(x) for x in dataset]
    
    def compute_kernel(self, dataset: List[List[float]]) -> List[List[float]]:
        """
        Compute kernel matrix.
        
        Args:
            dataset: Data
        
        Returns:
            Kernel matrix
        """
        return self.encoder.kernel_matrix_for(dataset)
    
    def feature_map_summary(self) -> Dict:
        """Get summary."""
        return {
            "feature_map": type(self.encoder.mapper).__name__ if self.encoder else "none",
            "feature_dim": self.encoder.mapper.feature_dim if self.encoder else 0,
            "encoded_samples": len(self.encoded_data)
        }
