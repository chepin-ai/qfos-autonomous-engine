"""
Quantum Boltzmann Machine Module
Quantum-stochastic neural network with thermal sampling, energy-based
learning, and Gibbs sampling for autonomous pattern recognition.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class QBMState:
    """
    State of quantum Boltzmann machine.
    """
    
    def __init__(self, num_visible: int = 4, num_hidden: int = 4):
        """
        Args:
            num_visible: Visible units
            num_hidden: Hidden units
        """
        self.v = num_visible
        self.h = num_hidden
        # Visible and hidden states (spins: +1 or -1)
        self.visible = [1 if random.random() > 0.5 else -1 for _ in range(num_visible)]
        self.hidden = [1 if random.random() > 0.5 else -1 for _ in range(num_hidden)]
    
    def copy(self) -> 'QBMState':
        """Create copy."""
        s = QBMState(self.v, self.h)
        s.visible = self.visible[:]
        s.hidden = self.hidden[:]
        return s


class QuantumBoltzmannMachine:
    """
    Quantum Boltzmann machine.
    """
    
    def __init__(self, num_visible: int = 4, num_hidden: int = 4):
        """
        Args:
            num_visible: Visible units
            num_hidden: Hidden units
        """
        self.v = num_visible
        self.h = num_hidden
        
        # Weights and biases
        self.W: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                       for _ in range(num_hidden)]
                                      for _ in range(num_visible)]
        self.b_v: List[float] = [0.0] * num_visible
        self.b_h: List[float] = [0.0] * num_hidden
        
        # Transverse field strength (quantum)
        self.gamma = 1.0
        self.temperature = 1.0
    
    def energy(self, state: QBMState) -> float:
        """
        Compute energy of state.
        
        Args:
            state: State
        
        Returns:
            Energy
        """
        E = 0.0
        
        # Visible-hidden interactions
        for i in range(self.v):
            for j in range(self.h):
                E -= self.W[i][j] * state.visible[i] * state.hidden[j]
        
        # Visible biases
        for i in range(self.v):
            E -= self.b_v[i] * state.visible[i]
        
        # Hidden biases
        for j in range(self.h):
            E -= self.b_h[j] * state.hidden[j]
        
        # Transverse field (quantum term)
        E += self.gamma * sum(abs(s) for s in state.visible)
        E += self.gamma * sum(abs(s) for s in state.hidden)
        
        return E
    
    def probability(self, state: QBMState) -> float:
        """
        Boltzmann probability.
        
        Args:
            state: State
        
        Returns:
            Probability
        """
        return math.exp(-self.energy(state) / self.temperature)
    
    def sample_hidden(self, visible: List[int]) -> List[int]:
        """
        Sample hidden given visible.
        
        Args:
            visible: Visible state
        
        Returns:
            Hidden state
        """
        hidden = []
        for j in range(self.h):
            activation = self.b_h[j]
            for i in range(self.v):
                activation += self.W[i][j] * visible[i]
            
            # Sigmoid probability
            p = 1.0 / (1.0 + math.exp(-2.0 * activation / self.temperature))
            hidden.append(1 if random.random() < p else -1)
        
        return hidden
    
    def sample_visible(self, hidden: List[int]) -> List[int]:
        """
        Sample visible given hidden.
        
        Args:
            hidden: Hidden state
        
        Returns:
            Visible state
        """
        visible = []
        for i in range(self.v):
            activation = self.b_v[i]
            for j in range(self.h):
                activation += self.W[i][j] * hidden[j]
            
            p = 1.0 / (1.0 + math.exp(-2.0 * activation / self.temperature))
            visible.append(1 if random.random() < p else -1)
        
        return visible
    
    def gibbs_sample(self, state: QBMState, steps: int = 1) -> QBMState:
        """
        Gibbs sampling.
        
        Args:
            state: Initial state
            steps: Steps
        
        Returns:
            New state
        """
        s = state.copy()
        for _ in range(steps):
            s.hidden = self.sample_hidden(s.visible)
            s.visible = self.sample_visible(s.hidden)
        return s
    
    def reconstruct(self, visible: List[int], steps: int = 1) -> List[int]:
        """
        Reconstruct visible state.
        
        Args:
            visible: Input
            steps: Gibbs steps
        
        Returns:
            Reconstructed
        """
        state = QBMState(self.v, self.h)
        state.visible = visible[:]
        state.hidden = self.sample_hidden(visible)
        
        for _ in range(steps):
            state.visible = self.sample_visible(state.hidden)
            state.hidden = self.sample_hidden(state.visible)
        
        return state.visible


class QBMLearner:
    """
    QBM training via contrastive divergence.
    """
    
    def __init__(self, qbm: QuantumBoltzmannMachine, lr: float = 0.01):
        """
        Args:
            qbm: QBM
            lr: Learning rate
        """
        self.qbm = qbm
        self.lr = lr
        self.loss_history: List[float] = []
    
    def train_step(self, data_batch: List[List[int]],
                  k: int = 1) -> float:
        """
        Single CD-k training step.
        
        Args:
            data_batch: Training data
            k: Gibbs steps
        
        Returns:
            Loss
        """
        # Positive phase
        pos_W = [[0.0] * self.qbm.h for _ in range(self.qbm.v)]
        pos_bv = [0.0] * self.qbm.v
        pos_bh = [0.0] * self.qbm.h
        
        for visible in data_batch:
            state = QBMState(self.qbm.v, self.qbm.h)
            state.visible = visible[:]
            state.hidden = self.qbm.sample_hidden(visible)
            
            for i in range(self.qbm.v):
                pos_bv[i] += state.visible[i]
                for j in range(self.qbm.h):
                    pos_W[i][j] += state.visible[i] * state.hidden[j]
            for j in range(self.qbm.h):
                pos_bh[j] += state.hidden[j]
        
        # Negative phase
        neg_W = [[0.0] * self.qbm.h for _ in range(self.qbm.v)]
        neg_bv = [0.0] * self.qbm.v
        neg_bh = [0.0] * self.qbm.h
        
        for visible in data_batch:
            state = QBMState(self.qbm.v, self.qbm.h)
            state.visible = visible[:]
            state.hidden = self.qbm.sample_hidden(visible)
            
            # Gibbs sampling
            state = self.qbm.gibbs_sample(state, k)
            
            for i in range(self.qbm.v):
                neg_bv[i] += state.visible[i]
                for j in range(self.qbm.h):
                    neg_W[i][j] += state.visible[i] * state.hidden[j]
            for j in range(self.qbm.h):
                neg_bh[j] += state.hidden[j]
        
        n = len(data_batch)
        if n == 0:
            return 0.0
        
        # Update weights
        for i in range(self.qbm.v):
            self.qbm.b_v[i] += self.lr * (pos_bv[i] - neg_bv[i]) / n
            for j in range(self.qbm.h):
                self.qbm.W[i][j] += self.lr * (pos_W[i][j] - neg_W[i][j]) / n
        for j in range(self.qbm.h):
            self.qbm.b_h[j] += self.lr * (pos_bh[j] - neg_bh[j]) / n
        
        # Compute loss (reconstruction error)
        loss = 0.0
        for visible in data_batch:
            recon = self.qbm.reconstruct(visible, k)
            loss += sum((a - b) ** 2 for a, b in zip(visible, recon)) / len(visible)
        
        loss /= n
        self.loss_history.append(loss)
        return loss
    
    def train(self, data: List[List[int]],
             epochs: int = 100,
             batch_size: int = 10,
             k: int = 1) -> Dict:
        """
        Full training.
        
        Args:
            data: Training data
            epochs: Epochs
            batch_size: Batch size
            k: CD steps
        
        Returns:
            Result
        """
        for epoch in range(epochs):
            # Shuffle
            random.shuffle(data)
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                self.train_step(batch, k)
        
        return {
            "final_loss": self.loss_history[-1] if self.loss_history else 0.0,
            "epochs": epochs
        }


class QuantumBoltzmannMachineController:
    """
    Unified QBM controller.
    """
    
    def __init__(self):
        self.qbm: Optional[QuantumBoltzmannMachine] = None
        self.learner: Optional[QBMLearner] = None
        self.results: List[Dict] = []
    
    def build(self, num_visible: int = 4, num_hidden: int = 4):
        """
        Build QBM.
        
        Args:
            num_visible: Visible units
            num_hidden: Hidden units
        """
        self.qbm = QuantumBoltzmannMachine(num_visible, num_hidden)
        self.learner = QBMLearner(self.qbm)
    
    def train(self, data: List[List[int]],
             epochs: int = 50) -> Dict:
        """
        Train QBM.
        
        Args:
            data: Training data
            epochs: Epochs
        
        Returns:
            Result
        """
        if self.learner is None:
            self.build(len(data[0]) if data else 4)
        
        result = self.learner.train(data, epochs=epochs)
        self.results.append(result)
        return result
    
    def generate(self, num_samples: int = 10,
                steps: int = 10) -> List[List[int]]:
        """
        Generate samples.
        
        Args:
            num_samples: Number
            steps: Gibbs steps
        
        Returns:
            Samples
        """
        if self.qbm is None:
            return []
        
        samples = []
        for _ in range(num_samples):
            state = QBMState(self.qbm.v, self.qbm.h)
            state = self.qbm.gibbs_sample(state, steps)
            samples.append(state.visible[:])
        
        return samples
    
    def qbm_summary(self) -> Dict:
        """Get summary."""
        return {
            "visible": self.qbm.v if self.qbm else 0,
            "hidden": self.qbm.h if self.qbm else 0,
            "training_runs": len(self.results),
            "final_loss": self.learner.loss_history[-1] if self.learner and self.learner.loss_history else 0.0
        }
