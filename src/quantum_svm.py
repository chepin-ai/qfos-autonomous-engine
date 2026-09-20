"""
Quantum SVM Module
Quantum kernel support vector machine and variational quantum classifier
for autonomous pattern recognition and classification.
"""

import math
import random
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass


class QuantumKernelSVM:
    """
    Quantum kernel SVM classifier.
    """
    
    def __init__(self, C: float = 1.0):
        """
        Args:
            C: Regularization
        """
        self.C = C
        self.alpha: List[float] = []
        self.support_vectors: List[List[float]] = []
        self.support_labels: List[int] = []
        self.kernel_func: Optional[Callable] = None
        self.bias = 0.0
    
    def set_kernel(self, kernel: Callable[[List[float], List[float]], float]):
        """
        Set kernel function.
        
        Args:
            kernel: Kernel function
        """
        self.kernel_func = kernel
    
    def train(self, X: List[List[float]], y: List[int]):
        """
        Simplified SMO training.
        
        Args:
            X: Training data
            y: Labels (-1 or 1)
        """
        n = len(X)
        self.alpha = [0.0] * n
        
        for _ in range(100):  # Simplified iterations
            for i in range(n):
                # Compute error
                prediction = sum(self.alpha[j] * y[j] * self.kernel_func(X[j], X[i])
                                for j in range(n)) + self.bias
                error = prediction - y[i]
                
                # Update alpha
                if (y[i] * error < -0.001 and self.alpha[i] < self.C) or \
                   (y[i] * error > 0.001 and self.alpha[i] > 0):
                    j = random.randint(0, n - 1)
                    while j == i:
                        j = random.randint(0, n - 1)
                    
                    pred_j = sum(self.alpha[k] * y[k] * self.kernel_func(X[k], X[j])
                                for k in range(n)) + self.bias
                    error_j = pred_j - y[j]
                    
                    alpha_i_old = self.alpha[i]
                    alpha_j_old = self.alpha[j]
                    
                    # Compute bounds
                    if y[i] != y[j]:
                        L = max(0.0, self.alpha[j] - self.alpha[i])
                        H = min(self.C, self.C + self.alpha[j] - self.alpha[i])
                    else:
                        L = max(0.0, self.alpha[i] + self.alpha[j] - self.C)
                        H = min(self.C, self.alpha[i] + self.alpha[j])
                    
                    if L == H:
                        continue
                    
                    eta = 2.0 * self.kernel_func(X[i], X[j]) - \
                          self.kernel_func(X[i], X[i]) - \
                          self.kernel_func(X[j], X[j])
                    
                    if eta >= 0:
                        continue
                    
                    self.alpha[j] -= y[j] * (error - error_j) / eta
                    self.alpha[j] = max(L, min(H, self.alpha[j]))
                    
                    if abs(self.alpha[j] - alpha_j_old) < 1e-5:
                        continue
                    
                    self.alpha[i] += y[i] * y[j] * (alpha_j_old - self.alpha[j])
                    
                    # Update bias
                    b1 = self.bias - error - y[i] * (self.alpha[i] - alpha_i_old) * \
                         self.kernel_func(X[i], X[i]) - y[j] * (self.alpha[j] - alpha_j_old) * \
                         self.kernel_func(X[i], X[j])
                    b2 = self.bias - error_j - y[i] * (self.alpha[i] - alpha_i_old) * \
                         self.kernel_func(X[i], X[j]) - y[j] * (self.alpha[j] - alpha_j_old) * \
                         self.kernel_func(X[j], X[j])
                    
                    if 0 < self.alpha[i] < self.C:
                        self.bias = b1
                    elif 0 < self.alpha[j] < self.C:
                        self.bias = b2
                    else:
                        self.bias = (b1 + b2) / 2.0
        
        # Extract support vectors
        for i in range(n):
            if self.alpha[i] > 1e-5:
                self.support_vectors.append(X[i])
                self.support_labels.append(y[i])
    
    def predict(self, x: List[float]) -> int:
        """
        Predict label.
        
        Args:
            x: Input
        
        Returns:
            Label (-1 or 1)
        """
        if not self.support_vectors:
            return 0
        
        val = sum(self.alpha[i] * self.support_labels[i] * self.kernel_func(self.support_vectors[i], x)
                 for i in range(len(self.support_vectors))) + self.bias
        return 1 if val >= 0 else -1
    
    def predict_batch(self, X: List[List[float]]) -> List[int]:
        """
        Predict batch.
        
        Args:
            X: Inputs
        
        Returns:
            Labels
        """
        return [self.predict(x) for x in X]


class VariationalQuantumClassifier:
    """
    Variational quantum classifier with parameterized circuits.
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.params: List[float] = [random.uniform(-math.pi, math.pi)
                                    for _ in range(num_qubits * 2)]
        self.history: List[float] = []
    
    def rotation(self, x: float, theta: float) -> float:
        """
        Parameterized rotation.
        
        Args:
            x: Input
            theta: Parameter
        
        Returns:
            Rotated value
        """
        return x * math.cos(theta) + math.sin(theta)
    
    def entangle(self, states: List[float]) -> List[float]:
        """
        Entangling layer.
        
        Args:
            states: Qubit states
        
        Returns:
            Entangled states
        """
        new_states = states[:]
        for i in range(len(states) - 1):
            # CNOT-like interaction
            new_states[i] = states[i] * states[i + 1]
        return new_states
    
    def circuit(self, features: List[float]) -> float:
        """
        Forward pass through variational circuit.
        
        Args:
            features: Input features
        
        Returns:
            Output expectation
        """
        dim = min(len(features), self.n)
        states = features[:dim] + [0.0] * (self.n - dim)
        
        # Layer 1: rotations
        for i in range(self.n):
            states[i] = self.rotation(states[i], self.params[i])
        
        # Entanglement
        states = self.entangle(states)
        
        # Layer 2: rotations
        for i in range(self.n):
            states[i] = self.rotation(states[i], self.params[self.n + i])
        
        # Measurement: sum of squared amplitudes
        return sum(s ** 2 for s in states)
    
    def predict(self, features: List[float]) -> int:
        """
        Predict class.
        
        Args:
            features: Input
        
        Returns:
            Class (0 or 1)
        """
        output = self.circuit(features)
        return 1 if output > 0.5 else 0
    
    def loss(self, features: List[float], label: int) -> float:
        """
        Binary cross-entropy loss.
        
        Args:
            features: Input
            label: Label (0 or 1)
        
        Returns:
            Loss
        """
        output = self.circuit(features)
        # Sigmoid
        pred = 1.0 / (1.0 + math.exp(-output))
        eps = 1e-8
        pred = max(eps, min(1.0 - eps, pred))
        target = float(label)
        return -(target * math.log(pred) + (1.0 - target) * math.log(1.0 - pred))
    
    def train(self, X: List[List[float]], y: List[int],
             epochs: int = 50, lr: float = 0.1):
        """
        Train classifier.
        
        Args:
            X: Training data
            y: Labels
            epochs: Epochs
            lr: Learning rate
        """
        for epoch in range(epochs):
            total_loss = 0.0
            for features, label in zip(X, y):
                # Compute loss
                l = self.loss(features, label)
                total_loss += l
                
                # Simple parameter update (finite differences)
                for i in range(len(self.params)):
                    old = self.params[i]
                    self.params[i] = old + 1e-4
                    l_plus = self.loss(features, label)
                    self.params[i] = old - 1e-4
                    l_minus = self.loss(features, label)
                    grad = (l_plus - l_minus) / (2.0 * 1e-4)
                    self.params[i] = old - lr * grad
            
            self.history.append(total_loss / len(X))


class QuantumSVM:
    """
    Unified quantum SVM controller.
    """
    
    def __init__(self):
        self.svm: Optional[QuantumKernelSVM] = None
        self.vqc: Optional[VariationalQuantumClassifier] = None
        self.kernel_matrix: Optional[List[List[float]]] = None
    
    def build_kernel_svm(self, C: float = 1.0,
                        kernel: Optional[Callable] = None):
        """
        Build quantum kernel SVM.
        
        Args:
            C: Regularization
            kernel: Kernel function
        """
        self.svm = QuantumKernelSVM(C)
        if kernel:
            self.svm.set_kernel(kernel)
        else:
            # Default quantum kernel
            def default_kernel(x, y):
                inner = sum(x[i] * y[i] for i in range(min(len(x), len(y))))
                norm_x = sum(xi ** 2 for xi in x) ** 0.5
                norm_y = sum(yi ** 2 for yi in y) ** 0.5
                if norm_x <= 0 or norm_y <= 0:
                    return 0.0
                return (inner / (norm_x * norm_y)) ** 2
            self.svm.set_kernel(default_kernel)
    
    def build_vqc(self, num_qubits: int = 4):
        """
        Build variational classifier.
        
        Args:
            num_qubits: Qubits
        """
        self.vqc = VariationalQuantumClassifier(num_qubits)
    
    def train_svm(self, X: List[List[float]], y: List[int]):
        """
        Train SVM.
        
        Args:
            X: Data
            y: Labels (-1, 1)
        """
        self.svm.train(X, y)
    
    def train_vqc(self, X: List[List[float]], y: List[int],
                 epochs: int = 50):
        """
        Train VQC.
        
        Args:
            X: Data
            y: Labels (0, 1)
            epochs: Epochs
        """
        self.vqc.train(X, y, epochs)
    
    def predict(self, x: List[float], method: str = "svm") -> int:
        """
        Predict.
        
        Args:
            x: Input
            method: "svm" or "vqc"
        
        Returns:
            Label
        """
        if method.lower() == "vqc" and self.vqc:
            return self.vqc.predict(x)
        if self.svm:
            return self.svm.predict(x)
        return 0
    
    def svm_summary(self) -> Dict:
        """Get SVM summary."""
        return {
            "support_vectors": len(self.svm.support_vectors) if self.svm else 0,
            "bias": self.svm.bias if self.svm else 0.0,
            "C": self.svm.C if self.svm else 0.0
        }
