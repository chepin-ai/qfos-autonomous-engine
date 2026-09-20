"""
Quantum Generative Adversarial Network Module
Quantum-inspired generator, discriminator, and adversarial training
for autonomous data synthesis and pattern generation.
"""

import math
import random
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass


class QuantumGenerator:
    """
    Quantum-inspired generator network.
    """
    
    def __init__(self, noise_dim: int = 8, output_dim: int = 4):
        """
        Args:
            noise_dim: Latent noise dimension
            output_dim: Generated output dimension
        """
        self.noise_dim = noise_dim
        self.output_dim = output_dim
        # Layer 1: noise_dim -> hidden
        self.W1: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                       for _ in range(noise_dim)]
                                      for _ in range(output_dim * 2)]
        # Layer 2: hidden -> output
        self.W2: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                       for _ in range(output_dim * 2)]
                                      for _ in range(output_dim)]
        self.b1: List[float] = [0.0] * (output_dim * 2)
        self.b2: List[float] = [0.0] * output_dim
    
    def sigmoid(self, x: float) -> float:
        """Sigmoid activation."""
        return 1.0 / (1.0 + math.exp(-x))
    
    def tanh(self, x: float) -> float:
        """Tanh activation."""
        return math.tanh(x)
    
    def matvec(self, W: List[List[float]], x: List[float]) -> List[float]:
        """Matrix-vector multiplication."""
        result = []
        for row in W:
            val = sum(row[i] * x[i] for i in range(min(len(row), len(x))))
            result.append(val)
        return result
    
    def generate(self, noise: Optional[List[float]] = None) -> List[float]:
        """
        Generate sample from noise.
        
        Args:
            noise: Latent noise (random if None)
        
        Returns:
            Generated sample
        """
        if noise is None:
            noise = [random.uniform(-1.0, 1.0) for _ in range(self.noise_dim)]
        
        # Layer 1
        h = self.matvec(self.W1, noise)
        h = [self.tanh(h[i] + self.b1[i]) for i in range(len(h))]
        
        # Layer 2
        out = self.matvec(self.W2, h)
        out = [self.tanh(out[i] + self.b2[i]) for i in range(len(out))]
        
        return out
    
    def generate_batch(self, batch_size: int) -> List[List[float]]:
        """
        Generate batch.
        
        Args:
            batch_size: Batch size
        
        Returns:
            Batch of samples
        """
        return [self.generate() for _ in range(batch_size)]


class QuantumDiscriminator:
    """
    Quantum-inspired discriminator network.
    """
    
    def __init__(self, input_dim: int = 4):
        """
        Args:
            input_dim: Input dimension
        """
        self.input_dim = input_dim
        # Layer 1
        self.W1: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                       for _ in range(input_dim)]
                                      for _ in range(input_dim * 2)]
        # Layer 2
        self.W2: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                       for _ in range(input_dim * 2)]
                                      for _ in range(1)]
        self.b1: List[float] = [0.0] * (input_dim * 2)
        self.b2: List[float] = [0.0]
    
    def sigmoid(self, x: float) -> float:
        """Sigmoid activation."""
        return 1.0 / (1.0 + math.exp(-x))
    
    def matvec(self, W: List[List[float]], x: List[float]) -> List[float]:
        """Matrix-vector multiplication."""
        result = []
        for row in W:
            val = sum(row[i] * x[i] for i in range(min(len(row), len(x))))
            result.append(val)
        return result
    
    def discriminate(self, sample: List[float]) -> float:
        """
        Discriminate sample.
        
        Args:
            sample: Input sample
        
        Returns:
            Probability [0, 1] of being real
        """
        # Layer 1
        h = self.matvec(self.W1, sample)
        h = [self.sigmoid(h[i] + self.b1[i]) for i in range(len(h))]
        
        # Layer 2
        out = self.matvec(self.W2, h)
        logit = out[0] + self.b2[0]
        
        return self.sigmoid(logit)
    
    def classify_batch(self, samples: List[List[float]]) -> List[float]:
        """
        Classify batch.
        
        Args:
            samples: Batch
        
        Returns:
            Probabilities
        """
        return [self.discriminate(s) for s in samples]


class AdversarialTrainer:
    """
    Adversarial training loop.
    """
    
    def __init__(self, generator: QuantumGenerator,
                 discriminator: QuantumDiscriminator,
                 lr: float = 0.01):
        """
        Args:
            generator: Generator
            discriminator: Discriminator
            lr: Learning rate
        """
        self.gen = generator
        self.disc = discriminator
        self.lr = lr
        self.gen_losses: List[float] = []
        self.disc_losses: List[float] = []
    
    def binary_cross_entropy(self, pred: float, target: float) -> float:
        """
        Binary cross-entropy loss.
        
        Args:
            pred: Prediction
            target: Target
        
        Returns:
            Loss
        """
        eps = 1e-8
        pred = max(eps, min(1.0 - eps, pred))
        return -(target * math.log(pred) + (1.0 - target) * math.log(1.0 - pred))
    
    def train_discriminator(self, real_samples: List[List[float]],
                           batch_size: int = 8):
        """
        Train discriminator on real and fake samples.
        
        Args:
            real_samples: Real data
            batch_size: Batch size
        """
        fake_samples = self.gen.generate_batch(batch_size)
        
        disc_loss = 0.0
        # Real samples
        for real in real_samples[:batch_size]:
            pred = self.disc.discriminate(real)
            disc_loss += self.binary_cross_entropy(pred, 1.0)
        
        # Fake samples
        for fake in fake_samples:
            pred = self.disc.discriminate(fake)
            disc_loss += self.binary_cross_entropy(pred, 0.0)
        
        disc_loss /= (len(real_samples[:batch_size]) + len(fake_samples))
        self.disc_losses.append(disc_loss)
    
    def train_generator(self, batch_size: int = 8):
        """
        Train generator to fool discriminator.
        
        Args:
            batch_size: Batch size
        """
        fake_samples = self.gen.generate_batch(batch_size)
        
        gen_loss = 0.0
        for fake in fake_samples:
            pred = self.disc.discriminate(fake)
            # Generator wants discriminator to predict 1 (real)
            gen_loss += self.binary_cross_entropy(pred, 1.0)
        
        gen_loss /= len(fake_samples)
        self.gen_losses.append(gen_loss)
    
    def train_step(self, real_samples: List[List[float]],
                  batch_size: int = 8):
        """
        Single training step.
        
        Args:
            real_samples: Real data
            batch_size: Batch size
        """
        self.train_discriminator(real_samples, batch_size)
        self.train_generator(batch_size)


class QuantumGenerativeAdversarialNetwork:
    """
    Unified QGAN controller.
    """
    
    def __init__(self):
        self.generator: Optional[QuantumGenerator] = None
        self.discriminator: Optional[QuantumDiscriminator] = None
        self.trainer: Optional[AdversarialTrainer] = None
        self.real_data: List[List[float]] = []
    
    def build(self, noise_dim: int = 8, data_dim: int = 4):
        """
        Build QGAN.
        
        Args:
            noise_dim: Noise dimension
            data_dim: Data dimension
        """
        self.generator = QuantumGenerator(noise_dim, data_dim)
        self.discriminator = QuantumDiscriminator(data_dim)
        self.trainer = AdversarialTrainer(self.generator, self.discriminator)
    
    def load_real_data(self, data: List[List[float]]):
        """Load real training data."""
        self.real_data = data
    
    def train(self, epochs: int = 10, batch_size: int = 8):
        """
        Train QGAN.
        
        Args:
            epochs: Epochs
            batch_size: Batch size
        """
        for _ in range(epochs):
            if self.real_data:
                self.trainer.train_step(self.real_data, batch_size)
            else:
                # Generate synthetic real data if none provided
                synthetic = [[random.uniform(-1.0, 1.0) for _ in range(self.generator.output_dim)]
                            for _ in range(batch_size)]
                self.trainer.train_step(synthetic, batch_size)
    
    def generate(self, num_samples: int = 1) -> List[List[float]]:
        """
        Generate samples.
        
        Args:
            num_samples: Number of samples
        
        Returns:
            Generated samples
        """
        return self.generator.generate_batch(num_samples)
    
    def evaluate(self, samples: List[List[float]]) -> List[float]:
        """
        Evaluate samples with discriminator.
        
        Args:
            samples: Samples
        
        Returns:
            Realness scores
        """
        return self.discriminator.classify_batch(samples)
    
    def qgan_summary(self) -> Dict:
        """Get QGAN summary."""
        return {
            "noise_dim": self.generator.noise_dim if self.generator else 0,
            "output_dim": self.generator.output_dim if self.generator else 0,
            "epochs_trained": len(self.trainer.gen_losses) if self.trainer else 0,
            "latest_gen_loss": self.trainer.gen_losses[-1] if self.trainer and self.trainer.gen_losses else 0.0,
            "latest_disc_loss": self.trainer.disc_losses[-1] if self.trainer and self.trainer.disc_losses else 0.0
        }
