"""
Quantum Error Mitigation Module
Zero-noise extrapolation, probabilistic error cancellation,
and measurement error mitigation for autonomous quantum execution.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


class ZeroNoiseExtrapolation:
    """
    Zero-noise extrapolation for expectation values.
    """
    
    def __init__(self):
        self.scales: List[float] = []
        self.expectations: List[float] = []
    
    def add_point(self, scale: float, expectation: float):
        """
        Add measurement point.
        
        Args:
            scale: Noise scale factor
            expectation: Measured expectation
        """
        self.scales.append(scale)
        self.expectations.append(expectation)
    
    def linear_extrapolate(self) -> float:
        """
        Linear extrapolation to zero noise.
        
        Returns:
            Extrapolated value
        """
        if len(self.scales) < 2:
            return self.expectations[-1] if self.expectations else 0.0
        
        # Fit E = a + b * scale
        n = len(self.scales)
        sx = sum(self.scales)
        sy = sum(self.expectations)
        sxx = sum(s**2 for s in self.scales)
        sxy = sum(self.scales[i] * self.expectations[i] for i in range(n))
        
        denom = n * sxx - sx**2
        if abs(denom) < 1e-10:
            return sy / n
        
        a = (sy * sxx - sx * sxy) / denom
        return a
    
    def richardson_extrapolate(self) -> float:
        """
        Richardson extrapolation.
        
        Returns:
            Extrapolated value
        """
        if len(self.scales) < 2:
            return self.linear_extrapolate()
        
        # Use first two points for simple Richardson
        x0, x1 = self.scales[0], self.scales[1]
        y0, y1 = self.expectations[0], self.expectations[1]
        
        if abs(x1 - x0) < 1e-10:
            return y0
        
        # Extrapolate to x=0
        return y0 - x0 * (y1 - y0) / (x1 - x0)


class ProbabilisticErrorCancellation:
    """
    Probabilistic error cancellation.
    """
    
    def __init__(self):
        self.noise_channels: List[Dict] = []
        self.mitigation_gates: List[Dict] = []
    
    def add_noise_model(self, error_rate: float, gate_type: str = "depolarizing"):
        """
        Add noise model.
        
        Args:
            error_rate: Error rate
            gate_type: Noise type
        """
        self.noise_channels.append({
            "rate": error_rate,
            "type": gate_type
        })
    
    def mitigation_weight(self, num_gates: int,
                         error_rate: float) -> float:
        """
        Compute mitigation weight.
        
        Args:
            num_gates: Number of gates
            error_rate: Error rate
        
        Returns:
            Weight factor
        """
        # Weight grows exponentially with circuit depth
        return (1.0 + error_rate) ** num_gates
    
    def sample_mitigated(self, true_expectation: float,
                        error_rate: float,
                        num_samples: int = 1000) -> float:
        """
        Sample mitigated expectation.
        
        Args:
            true_expectation: True value
            error_rate: Error rate
            num_samples: Samples
        
        Returns:
            Mitigated estimate
        """
        # Simulate noisy measurements
        noisy = []
        for _ in range(num_samples):
            # Add bias
            bias = random.gauss(0, error_rate)
            noisy.append(true_expectation + bias)
        
        # Weighted average (simplified)
        return sum(noisy) / len(noisy)


class MeasurementErrorMitigation:
    """
    Measurement error mitigation via calibration.
    """
    
    def __init__(self, num_qubits: int = 1):
        """
        Args:
            num_qubits: Qubits
        """
        self.n = num_qubits
        self.calibration_matrix: List[List[float]] = []
        self._identity_calibration()
    
    def _identity_calibration(self):
        """Initialize with identity calibration."""
        dim = 2 ** self.n
        self.calibration_matrix = [[1.0 if i == j else 0.0
                                    for j in range(dim)]
                                   for i in range(dim)]
    
    def add_calibration(self, ideal: int, measured: int,
                       probability: float):
        """
        Add calibration point.
        
        Args:
            ideal: Ideal outcome
            measured: Measured outcome
            probability: Probability
        """
        dim = 2 ** self.n
        if ideal < dim and measured < dim:
            self.calibration_matrix[measured][ideal] = probability
    
    def inverse_matrix(self) -> List[List[float]]:
        """
        Compute approximate inverse of calibration matrix.
        Simplified: assume diagonal dominance.
        
        Returns:
            Inverse matrix
        """
        dim = 2 ** self.n
        inv = [[0.0] * dim for _ in range(dim)]
        
        for i in range(dim):
            diag = self.calibration_matrix[i][i]
            if diag > 1e-10:
                inv[i][i] = 1.0 / diag
        
        return inv
    
    def mitigate_counts(self, counts: Dict[int, int]) -> Dict[int, float]:
        """
        Mitigate measurement counts.
        
        Args:
            counts: Raw counts
        
        Returns:
            Mitigated probabilities
        """
        dim = 2 ** self.n
        total = sum(counts.values())
        if total == 0:
            return {}
        
        raw_probs = [counts.get(i, 0) / total for i in range(dim)]
        inv = self.inverse_matrix()
        
        mitigated = []
        for i in range(dim):
            p = sum(inv[i][j] * raw_probs[j] for j in range(dim))
            mitigated.append(max(0.0, p))
        
        # Renormalize
        s = sum(mitigated)
        if s > 0:
            mitigated = [p / s for p in mitigated]
        
        return {i: mitigated[i] for i in range(dim)}


class QuantumErrorMitigation:
    """
    Unified quantum error mitigation controller.
    """
    
    def __init__(self):
        self.zne = ZeroNoiseExtrapolation()
        self.pec = ProbabilisticErrorCancellation()
        self.mem: Optional[MeasurementErrorMitigation] = None
        self.results: List[Dict] = []
    
    def setup_measurement(self, num_qubits: int = 1):
        """
        Setup measurement mitigation.
        
        Args:
            num_qubits: Qubits
        """
        self.mem = MeasurementErrorMitigation(num_qubits)
    
    def extrapolate_zne(self, scales: List[float],
                       expectations: List[float],
                       method: str = "linear") -> float:
        """
        Run ZNE.
        
        Args:
            scales: Noise scales
            expectations: Expectations
            method: "linear" or "richardson"
        
        Returns:
            Extrapolated value
        """
        self.zne = ZeroNoiseExtrapolation()
        for s, e in zip(scales, expectations):
            self.zne.add_point(s, e)
        
        if method == "richardson":
            return self.zne.richardson_extrapolate()
        return self.zne.linear_extrapolate()
    
    def mitigate_counts(self, counts: Dict[int, int]) -> Dict[int, float]:
        """
        Mitigate measurement counts.
        
        Args:
            counts: Raw counts
        
        Returns:
            Mitigated probabilities
        """
        if self.mem is None:
            return {k: v / sum(counts.values()) for k, v in counts.items()}
        return self.mem.mitigate_counts(counts)
    
    def mitigation_summary(self) -> Dict:
        """Get mitigation summary."""
        return {
            "zne_points": len(self.zne.scales),
            "pec_channels": len(self.pec.noise_channels),
            "mem_qubits": self.mem.n if self.mem else 0
        }
