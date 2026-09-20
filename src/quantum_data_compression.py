"""
Quantum Data Compression Module
Quantum autoencoder for data compression, state compression circuits,
fidelity-preserving encoding, and quantum principal component analysis.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class QuantumCompressor:
    """
    Quantum circuit for compressing n-qubit states to k-qubit states.
    """
    
    def __init__(self, num_qubits: int = 4, compressed_qubits: int = 2):
        """
        Args:
            num_qubits: Original qubits
            compressed_qubits: Target qubits
        """
        self.n = num_qubits
        self.k = compressed_qubits
        self.params = [random.uniform(0, 2.0 * math.pi)
                       for _ in range(num_qubits * 3)]
    
    def compress(self, state: List[complex]) -> List[complex]:
        """
        Compress quantum state.
        
        Args:
            state: Original state
        
        Returns:
            Compressed state
        """
        dim = 2 ** self.n
        new_state = state[:]
        
        # Apply parameterized unitary
        for q in range(self.n):
            rx = self.params[q * 3]
            for i in range(dim):
                if (i >> q) & 1:
                    new_state[i] *= complex(math.cos(rx), math.sin(rx))
        
        # Entangle and compress: trace out last n-k qubits
        compressed_dim = 2 ** self.k
        compressed = [complex(0.0, 0.0)] * compressed_dim
        
        for i in range(dim):
            # Map to compressed index
            compressed_idx = i & (compressed_dim - 1)
            compressed[compressed_idx] += new_state[i]
        
        # Normalize
        norm = sum(abs(z)**2 for z in compressed) ** 0.5
        if norm > 0:
            compressed = [z / norm for z in compressed]
        
        return compressed
    
    def decompress(self, compressed: List[complex]) -> List[complex]:
        """
        Decompress quantum state.
        
        Args:
            compressed: Compressed state
        
        Returns:
            Reconstructed state
        """
        dim = 2 ** self.n
        reconstructed = [complex(0.0, 0.0)] * dim
        compressed_dim = 2 ** self.k
        
        for i in range(dim):
            idx = i & (compressed_dim - 1)
            if idx < len(compressed):
                reconstructed[i] = compressed[idx] / math.sqrt(dim / compressed_dim)
        
        # Normalize
        norm = sum(abs(z)**2 for z in reconstructed) ** 0.5
        if norm > 0:
            reconstructed = [z / norm for z in reconstructed]
        
        return reconstructed


class QuantumAutoencoder:
    """
    Quantum autoencoder for classical data compression.
    """
    
    def __init__(self, input_dim: int = 4, latent_dim: int = 2):
        """
        Args:
            input_dim: Input dimension
            latent_dim: Latent dimension
        """
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.num_qubits = max(input_dim, latent_dim)
        self.compressor = QuantumCompressor(self.num_qubits, latent_dim)
    
    def encode_classical(self, data: List[float]) -> List[complex]:
        """
        Encode classical data to quantum state.
        
        Args:
            data: Data
        
        Returns:
            Quantum state
        """
        dim = 2 ** self.num_qubits
        state = [complex(0.0, 0.0)] * dim
        
        # Amplitude encoding
        for i, val in enumerate(data[:self.input_dim]):
            if i < dim:
                state[i] = complex(val, 0.0)
        
        # Normalize
        norm = sum(abs(z)**2 for z in state) ** 0.5
        if norm > 0:
            state = [z / norm for z in state]
        
        return state
    
    def decode_classical(self, state: List[complex]) -> List[float]:
        """
        Decode quantum state to classical data.
        
        Args:
            state: Quantum state
        
        Returns:
            Data
        """
        return [abs(z) for z in state[:self.input_dim]]
    
    def forward(self, data: List[float]) -> Tuple[List[float], List[complex]]:
        """
        Encode-decode cycle.
        
        Args:
            data: Input
        
        Returns:
            (reconstructed, latent)
        """
        state = self.encode_classical(data)
        latent = self.compressor.compress(state)
        reconstructed_state = self.compressor.decompress(latent)
        reconstructed = self.decode_classical(reconstructed_state)
        return reconstructed, latent
    
    def reconstruction_error(self, original: List[float],
                            reconstructed: List[float]) -> float:
        """
        Compute MSE.
        
        Args:
            original: Original
            reconstructed: Reconstructed
        
        Returns:
            MSE
        """
        n = min(len(original), len(reconstructed))
        if n == 0:
            return 0.0
        return sum((a - b) ** 2 for a, b in zip(original[:n], reconstructed[:n])) / n


class QuantumPCA:
    """
    Quantum principal component analysis.
    """
    
    def __init__(self, num_qubits: int = 4, num_components: int = 2):
        """
        Args:
            num_qubits: Qubits
            num_components: Components
        """
        self.n = num_qubits
        self.components = num_components
        self.eigenvalues: List[float] = []
        self.eigenvectors: List[List[float]] = []
    
    def covariance(self, data: List[List[float]]) -> List[List[float]]:
        """
        Compute covariance matrix.
        
        Args:
            data: Data matrix
        
        Returns:
            Covariance
        """
        n = len(data)
        dim = len(data[0]) if data else 0
        
        # Mean
        mean = [sum(row[i] for row in data) / n for i in range(dim)]
        
        # Covariance
        cov = [[0.0] * dim for _ in range(dim)]
        for row in data:
            for i in range(dim):
                for j in range(dim):
                    cov[i][j] += (row[i] - mean[i]) * (row[j] - mean[j])
        
        for i in range(dim):
            for j in range(dim):
                cov[i][j] /= max(n - 1, 1)
        
        return cov
    
    def power_iteration(self, matrix: List[List[float]],
                       num_iter: int = 20) -> Tuple[float, List[float]]:
        """
        Power iteration for dominant eigenvalue/vector.
        
        Args:
            matrix: Matrix
            num_iter: Iterations
        
        Returns:
            (eigenvalue, eigenvector)
        """
        dim = len(matrix)
        vec = [random.random() for _ in range(dim)]
        
        # Normalize
        norm = sum(v**2 for v in vec) ** 0.5
        vec = [v / norm for v in vec]
        
        for _ in range(num_iter):
            # Matrix-vector multiplication
            new_vec = [sum(matrix[i][j] * vec[j] for j in range(dim))
                       for i in range(dim)]
            
            # Normalize
            norm = sum(v**2 for v in new_vec) ** 0.5
            if norm > 0:
                vec = [v / norm for v in new_vec]
        
        # Rayleigh quotient
        Av = [sum(matrix[i][j] * vec[j] for j in range(dim))
              for i in range(dim)]
        eigenvalue = sum(vec[i] * Av[i] for i in range(dim))
        
        return eigenvalue, vec
    
    def fit(self, data: List[List[float]]):
        """
        Fit QPCA.
        
        Args:
            data: Data
        """
        cov = self.covariance(data)
        
        self.eigenvalues = []
        self.eigenvectors = []
        
        for _ in range(self.components):
            val, vec = self.power_iteration(cov)
            self.eigenvalues.append(val)
            self.eigenvectors.append(vec)
            
            # Deflate
            for i in range(len(cov)):
                for j in range(len(cov)):
                    cov[i][j] -= val * vec[i] * vec[j]
    
    def transform(self, data: List[float]) -> List[float]:
        """
        Project data.
        
        Args:
            data: Data
        
        Returns:
            Projected
        """
        return [sum(data[i] * vec[i] for i in range(min(len(data), len(vec))))
                for vec in self.eigenvectors]


class QuantumDataCompression:
    """
    Unified quantum data compression controller.
    """
    
    def __init__(self):
        self.autoencoder: Optional[QuantumAutoencoder] = None
        self.qpca: Optional[QuantumPCA] = None
        self.results: List[Dict] = []
    
    def build_autoencoder(self, input_dim: int = 4, latent_dim: int = 2):
        """
        Build autoencoder.
        
        Args:
            input_dim: Input
            latent_dim: Latent
        """
        self.autoencoder = QuantumAutoencoder(input_dim, latent_dim)
    
    def compress_data(self, data: List[float]) -> Dict:
        """
        Compress data.
        
        Args:
            data: Data
        
        Returns:
            Result
        """
        if self.autoencoder is None:
            self.build_autoencoder(len(data), max(1, len(data) // 2))
        
        reconstructed, latent = self.autoencoder.forward(data)
        error = self.autoencoder.reconstruction_error(data, reconstructed)
        
        result = {
            "original_dim": len(data),
            "latent_dim": len(latent),
            "reconstruction_error": error,
            "compression_ratio": len(data) / max(len(latent), 1)
        }
        self.results.append(result)
        return result
    
    def fit_qpca(self, data: List[List[float]], num_components: int = 2):
        """
        Fit QPCA.
        
        Args:
            data: Data
            num_components: Components
        """
        dim = len(data[0]) if data else 0
        self.qpca = QuantumPCA(dim, num_components)
        self.qpca.fit(data)
    
    def compression_summary(self) -> Dict:
        """Get summary."""
        return {
            "autoencoder": self.autoencoder is not None,
            "qpca": self.qpca is not None,
            "compressions": len(self.results),
            "avg_error": sum(r["reconstruction_error"] for r in self.results) / max(len(self.results), 1)
        }
