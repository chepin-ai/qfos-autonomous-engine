"""
Quantum Boltzmann Machine Module
Quantum-inspired Boltzmann sampling, visible/hidden unit training,
and probabilistic inference for autonomous pattern recognition.
"""

import math
import random
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass


class BoltzmannDistribution:
    """
    Boltzmann probability distribution.
    """
    
    def __init__(self, temperature: float = 1.0):
        """
        Args:
            temperature: System temperature
        """
        self.T = temperature
    
    def probability(self, energy: float) -> float:
        """
        Compute Boltzmann probability.
        
        Args:
            energy: State energy
        
        Returns:
            Probability weight
        """
        if self.T <= 0:
            return 1.0 if energy == 0 else 0.0
        return math.exp(-energy / self.T)
    
    def sample(self, energies: List[float]) -> int:
        """
        Sample from energy distribution.
        
        Args:
            energies: State energies
        
        Returns:
            Selected state index
        """
        weights = [self.probability(E) for E in energies]
        total = sum(weights)
        if total <= 0:
            return random.randint(0, len(energies) - 1)
        
        r = random.random() * total
        cumsum = 0.0
        for i, w in enumerate(weights):
            cumsum += w
            if r <= cumsum:
                return i
        return len(energies) - 1


class RestrictedBoltzmannMachine:
    """
    Restricted Boltzmann Machine (RBM).
    """
    
    def __init__(self, num_visible: int, num_hidden: int):
        """
        Args:
            num_visible: Visible units
            num_hidden: Hidden units
        """
        self.nv = num_visible
        self.nh = num_hidden
        # Weights: W[i][j] from visible i to hidden j
        self.W: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                      for _ in range(num_hidden)]
                                     for _ in range(num_visible)]
        self.b_visible: List[float] = [0.0] * num_visible
        self.b_hidden: List[float] = [0.0] * num_hidden
    
    def sigmoid(self, x: float) -> float:
        """Sigmoid activation."""
        return 1.0 / (1.0 + math.exp(-x))
    
    def hidden_probabilities(self, visible: List[int]) -> List[float]:
        """
        Compute hidden unit activation probabilities.
        
        Args:
            visible: Visible unit states
        
        Returns:
            Hidden probabilities
        """
        probs = []
        for j in range(self.nh):
            activation = self.b_hidden[j]
            for i in range(self.nv):
                activation += visible[i] * self.W[i][j]
            probs.append(self.sigmoid(activation))
        return probs
    
    def visible_probabilities(self, hidden: List[int]) -> List[float]:
        """
        Compute visible unit reconstruction probabilities.
        
        Args:
            hidden: Hidden unit states
        
        Returns:
            Visible probabilities
        """
        probs = []
        for i in range(self.nv):
            activation = self.b_visible[i]
            for j in range(self.nh):
                activation += hidden[j] * self.W[i][j]
            probs.append(self.sigmoid(activation))
        return probs
    
    def sample_hidden(self, visible: List[int]) -> List[int]:
        """
        Sample hidden units.
        
        Args:
            visible: Visible states
        
        Returns:
            Sampled hidden states
        """
        probs = self.hidden_probabilities(visible)
        return [1 if random.random() < p else 0 for p in probs]
    
    def sample_visible(self, hidden: List[int]) -> List[int]:
        """
        Sample visible units.
        
        Args:
            hidden: Hidden states
        
        Returns:
            Sampled visible states
        """
        probs = self.visible_probabilities(hidden)
        return [1 if random.random() < p else 0 for p in probs]
    
    def contrastive_divergence(self, data: List[int],
                              lr: float = 0.1,
                              k: int = 1):
        """
        CD-k training step.
        
        Args:
            data: Training data (visible states)
            lr: Learning rate
            k: Gibbs sampling steps
        """
        # Positive phase
        h0_probs = self.hidden_probabilities(data)
        h0 = [1 if random.random() < p else 0 for p in h0_probs]
        
        # Negative phase: k-step Gibbs
        vk = data[:]
        hk = h0[:]
        for _ in range(k):
            vk_probs = self.visible_probabilities(hk)
            vk = [1 if random.random() < p else 0 for p in vk_probs]
            hk_probs = self.hidden_probabilities(vk)
            hk = [1 if random.random() < p else 0 for p in hk_probs]
        
        # Update weights
        for i in range(self.nv):
            for j in range(self.nh):
                self.W[i][j] += lr * (data[i] * h0_probs[j] - vk[i] * hk_probs[j])
        
        # Update biases
        for i in range(self.nv):
            self.b_visible[i] += lr * (data[i] - vk[i])
        for j in range(self.nh):
            self.b_hidden[j] += lr * (h0_probs[j] - hk_probs[j])


class QuantumBoltzmannMachine:
    """
    Quantum Boltzmann Machine with transverse field.
    """
    
    def __init__(self, num_visible: int, num_hidden: int,
                 transverse_field: float = 0.1):
        """
        Args:
            num_visible: Visible units
            num_hidden: Hidden units
            transverse_field: Transverse field strength (Gamma)
        """
        self.rbm = RestrictedBoltzmannMachine(num_visible, num_hidden)
        self.Gamma = transverse_field
        self.quantum_weights: List[List[float]] = [[w for w in row] for row in self.rbm.W]
    
    def quantum_energy(self, visible: List[int],
                      hidden: List[int]) -> float:
        """
        Compute quantum Hamiltonian energy.
        
        Args:
            visible: Visible states
            hidden: Hidden states
        
        Returns:
            Energy
        """
        classical = 0.0
        for i in range(self.rbm.nv):
            for j in range(self.rbm.nh):
                classical -= self.quantum_weights[i][j] * visible[i] * hidden[j]
        for i in range(self.rbm.nv):
            classical -= self.rbm.b_visible[i] * visible[i]
        for j in range(self.rbm.nh):
            classical -= self.rbm.b_hidden[j] * hidden[j]
        
        # Transverse field term (quantum fluctuations)
        quantum_term = -self.Gamma * sum(visible) - self.Gamma * sum(hidden)
        
        return classical + quantum_term
    
    def quantum_sample(self, visible: List[int]) -> Tuple[List[int], float]:
        """
        Sample with quantum effects.
        
        Args:
            visible: Input visible states
        
        Returns:
            (hidden_states, energy)
        """
        # First sample classically
        hidden = self.rbm.sample_hidden(visible)
        
        # Apply quantum perturbation
        for j in range(self.rbm.nh):
            if random.random() < self.Gamma:
                hidden[j] = 1 - hidden[j]
        
        E = self.quantum_energy(visible, hidden)
        return hidden, E
    
    def train_quantum(self, data: List[int], lr: float = 0.1):
        """
        Train with quantum CD.
        
        Args:
            data: Training data
            lr: Learning rate
        """
        self.rbm.contrastive_divergence(data, lr, k=1)
        # Update quantum weights
        self.quantum_weights = [[w for w in row] for row in self.rbm.W]


class QBMInference:
    """
    Inference engine for trained QBM.
    """
    
    def __init__(self, qbm: QuantumBoltzmannMachine):
        """
        Args:
            qbm: Trained QBM
        """
        self.qbm = qbm
    
    def reconstruct(self, partial_visible: List[Optional[int]]) -> List[int]:
        """
        Reconstruct missing visible units.
        
        Args:
            partial_visible: Partial visible state (None for missing)
        
        Returns:
            Reconstructed state
        """
        # Fill missing with random
        visible = [v if v is not None else random.choice([0, 1])
                   for v in partial_visible]
        
        # Sample hidden
        hidden = self.qbm.rbm.sample_hidden(visible)
        
        # Reconstruct visible
        recon_probs = self.qbm.rbm.visible_probabilities(hidden)
        recon = []
        for i, v in enumerate(partial_visible):
            if v is not None:
                recon.append(v)
            else:
                recon.append(1 if random.random() < recon_probs[i] else 0)
        
        return recon
    
    def feature_representation(self, visible: List[int]) -> List[float]:
        """
        Extract hidden features.
        
        Args:
            visible: Input
        
        Returns:
            Hidden probabilities as features
        """
        return self.qbm.rbm.hidden_probabilities(visible)
    
    def free_energy(self, visible: List[int]) -> float:
        """
        Compute free energy.
        
        Args:
            visible: Visible state
        
        Returns:
            Free energy
        """
        hidden_probs = self.qbm.rbm.hidden_probabilities(visible)
        fe = 0.0
        for i in range(self.qbm.rbm.nv):
            fe -= self.qbm.rbm.b_visible[i] * visible[i]
        for j in range(self.qbm.rbm.nh):
            fe -= math.log(1 + math.exp(hidden_probs[j]))
        return fe


class QuantumBoltzmannController:
    """
    Unified QBM controller.
    """
    
    def __init__(self):
        self.qbm: Optional[QuantumBoltzmannMachine] = None
        self.inference: Optional[QBMInference] = None
        self.training_history: List[float] = []
    
    def build(self, num_visible: int, num_hidden: int,
             transverse_field: float = 0.1):
        """
        Build QBM.
        
        Args:
            num_visible: Visible units
            num_hidden: Hidden units
            transverse_field: Transverse field
        """
        self.qbm = QuantumBoltzmannMachine(num_visible, num_hidden, transverse_field)
        self.inference = QBMInference(self.qbm)
    
    def train(self, dataset: List[List[int]],
             epochs: int = 10, lr: float = 0.1):
        """
        Train on dataset.
        
        Args:
            dataset: Training data
            epochs: Training epochs
            lr: Learning rate
        """
        for epoch in range(epochs):
            total_error = 0.0
            for data in dataset:
                old_visible = data[:]
                self.qbm.train_quantum(data, lr)
                # Compute reconstruction error
                hidden = self.qbm.rbm.sample_hidden(data)
                recon_probs = self.qbm.rbm.visible_probabilities(hidden)
                error = sum((data[i] - recon_probs[i])**2 for i in range(len(data)))
                total_error += error
            
            avg_error = total_error / len(dataset) if dataset else 0
            self.training_history.append(avg_error)
    
    def predict(self, input_data: List[Optional[int]]) -> List[int]:
        """
        Predict/reconstruct.
        
        Args:
            input_data: Partial input
        
        Returns:
            Reconstructed output
        """
        if self.inference is None:
            return []
        return self.inference.reconstruct(input_data)
    
    def qbm_summary(self) -> Dict:
        """Get QBM summary."""
        if self.qbm is None:
            return {"status": "not_built"}
        
        return {
            "visible": self.qbm.rbm.nv,
            "hidden": self.qbm.rbm.nh,
            "transverse_field": self.qbm.Gamma,
            "training_epochs": len(self.training_history),
            "final_error": self.training_history[-1] if self.training_history else 0.0
        }
