"""
Quantum Generative Modeling Module
Quantum circuit Born machine, Born rule sampling, MMD loss,
and quantum generative adversarial training for autonomous quantum ML.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


class QCBMCircuit:
    """
    Quantum Circuit Born Machine circuit.
    """
    
    def __init__(self, num_qubits: int = 4, num_layers: int = 2):
        """
        Args:
            num_qubits: Qubits
            num_layers: Layers
        """
        self.n = num_qubits
        self.layers = num_layers
        self.params: List[List[float]] = []
        self._randomize_params()
    
    def _randomize_params(self):
        """Randomize parameters."""
        self.params = []
        for _ in range(self.layers):
            layer = [random.uniform(0, 2 * math.pi) for _ in range(self.n * 2)]
            self.params.append(layer)
    
    def apply_layer(self, state: List[complex],
                   params: List[float]) -> List[complex]:
        """
        Apply one layer.
        
        Args:
            state: State
            params: Parameters
        
        Returns:
            New state
        """
        dim = len(state)
        new_state = state[:]
        
        # Single qubit rotations
        for q in range(self.n):
            theta = params[q * 2]
            phi = params[q * 2 + 1]
            
            for i in range(dim):
                if (i >> q) & 1:
                    new_state[i] *= complex(math.cos(theta), math.sin(theta))
                else:
                    new_state[i] *= complex(math.cos(phi), math.sin(phi))
        
        # Entangling (simplified CNOT-like)
        for q in range(self.n - 1):
            for i in range(dim):
                if ((i >> q) & 1) and not ((i >> (q + 1)) & 1):
                    j = i | (1 << (q + 1))
                    new_state[i], new_state[j] = new_state[j], new_state[i]
        
        # Normalize
        norm = sum(abs(z)**2 for z in new_state) ** 0.5
        if norm > 0:
            new_state = [z / norm for z in new_state]
        
        return new_state
    
    def run(self) -> List[complex]:
        """
        Run circuit.
        
        Returns:
            Final state
        """
        dim = 2 ** self.n
        state = [complex(0, 0)] * dim
        state[0] = complex(1, 0)
        
        for layer_params in self.params:
            state = self.apply_layer(state, layer_params)
        
        return state
    
    def probabilities(self) -> List[float]:
        """
        Get measurement probabilities.
        
        Returns:
            Probabilities
        """
        state = self.run()
        return [abs(z)**2 for z in state]
    
    def sample(self, num_samples: int = 100) -> List[int]:
        """
        Sample from Born distribution.
        
        Args:
            num_samples: Samples
        
        Returns:
            Sampled bitstrings (as integers)
        """
        probs = self.probabilities()
        return random.choices(range(len(probs)), weights=probs, k=num_samples)


class MMDLoss:
    """
    Maximum Mean Discrepancy loss.
    """
    
    def __init__(self, sigma: float = 1.0):
        """
        Args:
            sigma: Kernel bandwidth
        """
        self.sigma = sigma
    
    def gaussian_kernel(self, x: int, y: int) -> float:
        """
        Gaussian kernel on binary strings.
        
        Args:
            x: Bitstring 1
            y: Bitstring 2
        
        Returns:
            Kernel value
        """
        diff = bin(x ^ y).count('1')
        return math.exp(-diff / (2.0 * self.sigma**2))
    
    def mmd(self, p: List[float], q: List[float]) -> float:
        """
        Compute MMD.
        
        Args:
            p: Distribution 1
            q: Distribution 2
        
        Returns:
            MMD
        """
        n = len(p)
        
        # E[k(X, X')]
        term1 = sum(p[i] * p[j] * self.gaussian_kernel(i, j)
                    for i in range(n) for j in range(n))
        
        # E[k(Y, Y')]
        term2 = sum(q[i] * q[j] * self.gaussian_kernel(i, j)
                    for i in range(n) for j in range(n))
        
        # E[k(X, Y)]
        term3 = sum(p[i] * q[j] * self.gaussian_kernel(i, j)
                    for i in range(n) for j in range(n))
        
        return term1 + term2 - 2.0 * term3


class QuantumBornMachineTrainer:
    """
    QCBM trainer.
    """
    
    def __init__(self, circuit: QCBMCircuit,
                 target_dist: List[float],
                 learning_rate: float = 0.1):
        """
        Args:
            circuit: QCBM circuit
            target_dist: Target distribution
            learning_rate: Learning rate
        """
        self.circuit = circuit
        self.target = target_dist
        self.lr = learning_rate
        self.loss_history: List[float] = []
        self.mmd = MMDLoss()
    
    def compute_gradient(self, layer_idx: int, param_idx: int) -> float:
        """
        Compute gradient via parameter shift.
        
        Args:
            layer_idx: Layer index
            param_idx: Parameter index
        
        Returns:
            Gradient
        """
        shift = math.pi / 2.0
        
        # Forward shift
        original = self.circuit.params[layer_idx][param_idx]
        self.circuit.params[layer_idx][param_idx] = original + shift
        loss_plus = self.mmd.mmd(self.circuit.probabilities(), self.target)
        
        # Backward shift
        self.circuit.params[layer_idx][param_idx] = original - shift
        loss_minus = self.mmd.mmd(self.circuit.probabilities(), self.target)
        
        # Restore
        self.circuit.params[layer_idx][param_idx] = original
        
        return (loss_plus - loss_minus) / 2.0
    
    def train_step(self):
        """One training step."""
        for l in range(len(self.circuit.params)):
            for p in range(len(self.circuit.params[l])):
                grad = self.compute_gradient(l, p)
                self.circuit.params[l][p] -= self.lr * grad
    
    def train(self, epochs: int = 10):
        """
        Train.
        
        Args:
            epochs: Epochs
        """
        for _ in range(epochs):
            self.train_step()
            loss = self.mmd.mmd(self.circuit.probabilities(), self.target)
            self.loss_history.append(loss)


class QuantumGenerativeModeling:
    """
    Unified quantum generative modeling controller.
    """
    
    def __init__(self):
        self.circuit: Optional[QCBMCircuit] = None
        self.trainer: Optional[QuantumBornMachineTrainer] = None
        self.samples: List[int] = []
        self.results: List[Dict] = []
    
    def create_circuit(self, num_qubits: int = 4,
                      num_layers: int = 2):
        """
        Create circuit.
        
        Args:
            num_qubits: Qubits
            num_layers: Layers
        """
        self.circuit = QCBMCircuit(num_qubits, num_layers)
    
    def train(self, target_dist: List[float],
             epochs: int = 10,
             learning_rate: float = 0.1) -> Dict:
        """
        Train model.
        
        Args:
            target_dist: Target
            epochs: Epochs
            learning_rate: Learning rate
        
        Returns:
            Result
        """
        if self.circuit is None:
            self.create_circuit()
        
        # Normalize target to match circuit dimension
        dim = 2 ** self.circuit.n
        if len(target_dist) != dim:
            if len(target_dist) < dim:
                target_dist = target_dist + [0.0] * (dim - len(target_dist))
            else:
                target_dist = target_dist[:dim]
            total = sum(target_dist)
            if total > 0:
                target_dist = [v / total for v in target_dist]
        
        self.trainer = QuantumBornMachineTrainer(
            self.circuit, target_dist, learning_rate
        )
        self.trainer.train(epochs)
        
        final_loss = self.trainer.loss_history[-1] if self.trainer.loss_history else 0.0
        result = {
            "final_loss": final_loss,
            "epochs": epochs,
            "initial_loss": self.trainer.loss_history[0] if self.trainer.loss_history else 0.0
        }
        self.results.append(result)
        return result
    
    def generate(self, num_samples: int = 100) -> List[int]:
        """
        Generate samples.
        
        Args:
            num_samples: Samples
        
        Returns:
            Samples
        """
        if self.circuit is None:
            self.create_circuit()
        
        self.samples = self.circuit.sample(num_samples)
        return self.samples
    
    def qgm_summary(self) -> Dict:
        """Get summary."""
        return {
            "qubits": self.circuit.n if self.circuit else 0,
            "layers": self.circuit.layers if self.circuit else 0,
            "training_runs": len(self.results),
            "samples": len(self.samples)
        }
