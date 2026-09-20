"""
Quantum Neural Network Module
Parameterized quantum circuits as neural networks, quantum layers,
backpropagation-free training, and classification for autonomous AI.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class QuantumLayer:
    """
    Single quantum layer with parameterized rotations.
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Args:
            num_qubits: Qubits
        """
        self.n = num_qubits
        self.params = [random.uniform(0, 2.0 * math.pi) for _ in range(num_qubits * 3)]
    
    def apply(self, state: List[complex]) -> List[complex]:
        """
        Apply layer to state.
        
        Args:
            state: Input state
        
        Returns:
            Output state
        """
        dim = len(state)
        new_state = state[:]
        
        # Rotation gates (RX, RY, RZ) for each qubit
        for q in range(self.n):
            rx = self.params[q * 3]
            ry = self.params[q * 3 + 1]
            rz = self.params[q * 3 + 2]
            
            for i in range(dim):
                if (i >> q) & 1:
                    # Apply combined rotation
                    phase = rx + ry + rz
                    new_state[i] *= complex(math.cos(phase), math.sin(phase))
        
        # Entangling: CNOT-like between adjacent qubits
        for q in range(self.n - 1):
            for i in range(dim):
                if (i >> q) & 1:
                    flipped = i ^ (1 << (q + 1))
                    if flipped < dim:
                        new_state[i], new_state[flipped] = new_state[flipped], new_state[i]
        
        # Normalize
        norm = sum(abs(z)**2 for z in new_state) ** 0.5
        if norm > 0:
            new_state = [z / norm for z in new_state]
        
        return new_state


class QuantumNeuralNetwork:
    """
    Multi-layer quantum neural network.
    """
    
    def __init__(self, num_qubits: int = 4, num_layers: int = 3):
        """
        Args:
            num_qubits: Qubits
            num_layers: Layers
        """
        self.n = num_qubits
        self.layers = [QuantumLayer(num_qubits) for _ in range(num_layers)]
    
    def encode(self, features: List[float]) -> List[complex]:
        """
        Encode classical features into quantum state.
        
        Args:
            features: Features
        
        Returns:
            Quantum state
        """
        dim = 2 ** self.n
        state = [complex(0.0, 0.0)] * dim
        state[0] = complex(1.0, 0.0)
        
        # Angle encoding
        for i, f in enumerate(features[:self.n]):
            angle = f * math.pi
            for j in range(dim):
                if (j >> i) & 1:
                    state[j] = complex(state[j].real * math.cos(angle),
                                      state[j].imag + math.sin(angle))
        
        # Normalize
        norm = sum(abs(z)**2 for z in state) ** 0.5
        if norm > 0:
            state = [z / norm for z in state]
        
        return state
    
    def forward(self, features: List[float]) -> List[complex]:
        """
        Forward pass.
        
        Args:
            features: Input features
        
        Returns:
            Output state
        """
        state = self.encode(features)
        for layer in self.layers:
            state = layer.apply(state)
        return state
    
    def measure(self, state: List[complex]) -> List[float]:
        """
        Measure output probabilities.
        
        Args:
            state: State
        
        Returns:
            Probabilities
        """
        return [abs(z)**2 for z in state]
    
    def classify(self, features: List[float],
                num_classes: int = 2) -> int:
        """
        Classify input.
        
        Args:
            features: Features
            num_classes: Classes
        
        Returns:
            Class
        """
        state = self.forward(features)
        probs = self.measure(state)
        
        # Aggregate into classes
        class_probs = [0.0] * num_classes
        for i, p in enumerate(probs):
            class_probs[i % num_classes] += p
        
        return max(range(num_classes), key=lambda i: class_probs[i])


class QuantumTrainer:
    """
    Train QNN via parameter shift rule.
    """
    
    def __init__(self, qnn: QuantumNeuralNetwork, lr: float = 0.1):
        """
        Args:
            qnn: QNN
            lr: Learning rate
        """
        self.qnn = qnn
        self.lr = lr
        self.loss_history: List[float] = []
    
    def compute_loss(self, features: List[float],
                    label: int, num_classes: int = 2) -> float:
        """
        Compute cross-entropy-like loss.
        
        Args:
            features: Features
            label: True label
            num_classes: Classes
        
        Returns:
            Loss
        """
        state = self.qnn.forward(features)
        probs = self.qnn.measure(state)
        
        class_probs = [0.0] * num_classes
        for i, p in enumerate(probs):
            class_probs[i % num_classes] += p
        
        # Negative log probability
        p = max(class_probs[label], 1e-10)
        return -math.log(p)
    
    def parameter_shift(self, features: List[float],
                       label: int,
                       layer_idx: int,
                       param_idx: int,
                       shift: float = math.pi / 2) -> float:
        """
        Compute gradient via parameter shift.
        
        Args:
            features: Features
            label: Label
            layer_idx: Layer
            param_idx: Parameter
            shift: Shift amount
        
        Returns:
            Gradient
        """
        layer = self.qnn.layers[layer_idx]
        
        # Forward shift
        layer.params[param_idx] += shift
        loss_plus = self.compute_loss(features, label)
        
        # Backward shift
        layer.params[param_idx] -= 2.0 * shift
        loss_minus = self.compute_loss(features, label)
        
        # Restore
        layer.params[param_idx] += shift
        
        return (loss_plus - loss_minus) / (2.0 * math.sin(shift))
    
    def train_step(self, features: List[float], label: int):
        """
        Single training step.
        
        Args:
            features: Features
            label: Label
        """
        loss = self.compute_loss(features, label)
        self.loss_history.append(loss)
        
        # Update all parameters
        for li, layer in enumerate(self.qnn.layers):
            for pi in range(len(layer.params)):
                grad = self.parameter_shift(features, label, li, pi)
                layer.params[pi] -= self.lr * grad
    
    def train(self, data: List[Tuple[List[float], int]],
             epochs: int = 20) -> Dict:
        """
        Train on dataset.
        
        Args:
            data: (features, label) pairs
            epochs: Epochs
        
        Returns:
            Result
        """
        for epoch in range(epochs):
            random.shuffle(data)
            for features, label in data:
                self.train_step(features, label)
        
        return {
            "final_loss": self.loss_history[-1] if self.loss_history else 0.0,
            "epochs": epochs
        }


class QuantumNeuralNetworkController:
    """
    Unified QNN controller.
    """
    
    def __init__(self):
        self.qnn: Optional[QuantumNeuralNetwork] = None
        self.trainer: Optional[QuantumTrainer] = None
        self.results: List[Dict] = []
    
    def build(self, num_qubits: int = 4, num_layers: int = 3):
        """
        Build QNN.
        
        Args:
            num_qubits: Qubits
            num_layers: Layers
        """
        self.qnn = QuantumNeuralNetwork(num_qubits, num_layers)
        self.trainer = QuantumTrainer(self.qnn)
    
    def train(self, data: List[Tuple[List[float], int]],
             epochs: int = 20) -> Dict:
        """
        Train.
        
        Args:
            data: Data
            epochs: Epochs
        
        Returns:
            Result
        """
        if self.trainer is None:
            self.build()
        
        result = self.trainer.train(data, epochs)
        self.results.append(result)
        return result
    
    def predict(self, features: List[float],
               num_classes: int = 2) -> int:
        """
        Predict class.
        
        Args:
            features: Features
            num_classes: Classes
        
        Returns:
            Class
        """
        if self.qnn is None:
            return 0
        return self.qnn.classify(features, num_classes)
    
    def qnn_summary(self) -> Dict:
        """Get summary."""
        return {
            "qubits": self.qnn.n if self.qnn else 0,
            "layers": len(self.qnn.layers) if self.qnn else 0,
            "training_runs": len(self.results),
            "final_loss": self.trainer.loss_history[-1] if self.trainer and self.trainer.loss_history else 0.0
        }
