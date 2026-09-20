"""
Quantum Diffusion Model Module
Quantum-inspired diffusion process, noise scheduling,
reverse sampling, and probabilistic generation for autonomous synthesis.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class NoiseSchedule:
    """
    Diffusion noise schedule.
    """
    
    def __init__(self, num_steps: int = 100,
                 beta_start: float = 0.0001,
                 beta_end: float = 0.02):
        """
        Args:
            num_steps: Diffusion steps
            beta_start: Starting noise level
            beta_end: Ending noise level
        """
        self.T = num_steps
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.betas = self._compute_betas()
        self.alphas = [1.0 - b for b in self.betas]
        self.alpha_bars = self._compute_alpha_bars()
    
    def _compute_betas(self) -> List[float]:
        """Compute linear beta schedule."""
        return [self.beta_start + (self.beta_end - self.beta_start) * t / self.T
                for t in range(self.T)]
    
    def _compute_alpha_bars(self) -> List[float]:
        """Compute cumulative product of alphas."""
        alpha_bars = []
        prod = 1.0
        for alpha in self.alphas:
            prod *= alpha
            alpha_bars.append(prod)
        return alpha_bars
    
    def alpha_bar(self, t: int) -> float:
        """
        Get alpha_bar at step t.
        
        Args:
            t: Step
        
        Returns:
            alpha_bar
        """
        if t < 0 or t >= self.T:
            return 0.0
        return self.alpha_bars[t]
    
    def signal_to_noise_ratio(self, t: int) -> float:
        """
        Compute SNR at step t.
        
        Args:
            t: Step
        
        Returns:
            SNR in dB
        """
        ab = self.alpha_bar(t)
        if ab <= 0 or ab >= 1.0:
            return 0.0
        return 10.0 * math.log10(ab / (1.0 - ab))


class ForwardDiffusion:
    """
    Forward diffusion process q(x_t | x_0).
    """
    
    def __init__(self, schedule: NoiseSchedule):
        """
        Args:
            schedule: Noise schedule
        """
        self.schedule = schedule
    
    def add_noise(self, x0: List[float], t: int) -> Tuple[List[float], List[float]]:
        """
        Add noise to data at step t.
        
        Args:
            x0: Clean data
            t: Step
        
        Returns:
            (noisy_data, noise)
        """
        alpha_bar = self.schedule.alpha_bar(t)
        noise = [random.gauss(0.0, 1.0) for _ in range(len(x0))]
        xt = [math.sqrt(alpha_bar) * x0[i] + math.sqrt(1.0 - alpha_bar) * noise[i]
              for i in range(len(x0))]
        return xt, noise
    
    def sample_noisy(self, x0: List[float]) -> List[float]:
        """
        Sample fully noised data.
        
        Args:
            x0: Clean data
        
        Returns:
            Noisy data
        """
        xt, _ = self.add_noise(x0, self.schedule.T - 1)
        return xt


class QuantumNoiseKernel:
    """
    Quantum-inspired noise kernel with superposition.
    """
    
    def __init__(self, num_basis: int = 4):
        """
        Args:
            num_basis: Number of quantum basis states
        """
        self.basis = num_basis
        self.amplitudes = [random.uniform(-1.0, 1.0) for _ in range(num_basis)]
    
    def quantum_noise(self, dim: int) -> List[float]:
        """
        Generate quantum-correlated noise.
        
        Args:
            dim: Dimension
        
        Returns:
            Noise vector
        """
        base_noise = [random.gauss(0.0, 1.0) for _ in range(dim)]
        # Apply quantum phase modulation
        quantum_noise = []
        for i in range(dim):
            phase = sum(self.amplitudes[j] * math.sin((i + 1) * (j + 1) * math.pi / self.basis)
                       for j in range(self.basis))
            quantum_noise.append(base_noise[i] * (1.0 + 0.1 * phase))
        return quantum_noise


class ReverseSampler:
    """
    Reverse diffusion sampler p(x_{t-1} | x_t).
    """
    
    def __init__(self, schedule: NoiseSchedule):
        """
        Args:
            schedule: Noise schedule
        """
        self.schedule = schedule
    
    def denoise_step(self, xt: List[float], t: int,
                    predicted_noise: List[float]) -> List[float]:
        """
        Single reverse diffusion step.
        
        Args:
            xt: Noisy data
            t: Current step
            predicted_noise: Predicted noise
        
        Returns:
            Less noisy data
        """
        if t <= 0:
            return xt
        
        alpha = self.schedule.alphas[t]
        alpha_bar = self.schedule.alpha_bar(t)
        alpha_bar_prev = self.schedule.alpha_bar(t - 1) if t > 0 else 1.0
        
        beta = self.schedule.betas[t]
        
        # Compute x_{t-1}
        coeff_x0 = 1.0 / math.sqrt(alpha)
        coeff_noise = (1.0 - alpha) / math.sqrt(1.0 - alpha_bar)
        
        # Predict x_0
        x0_pred = [(xt[i] - math.sqrt(1.0 - alpha_bar) * predicted_noise[i]) / math.sqrt(alpha_bar)
                   for i in range(len(xt))]
        
        # Compute mean
        if alpha_bar_prev > 0:
            mean = [(math.sqrt(alpha_bar_prev) * beta / (1.0 - alpha_bar)) * x0_pred[i] +
                    (math.sqrt(alpha) * (1.0 - alpha_bar_prev) / (1.0 - alpha_bar)) * xt[i]
                    for i in range(len(xt))]
        else:
            mean = x0_pred
        
        # Add noise (except for final step)
        if t > 1:
            sigma = math.sqrt(beta * (1.0 - alpha_bar_prev) / (1.0 - alpha_bar))
            noise = [random.gauss(0.0, sigma) for _ in range(len(xt))]
            return [mean[i] + noise[i] for i in range(len(xt))]
        
        return mean
    
    def simple_denoise(self, xt: List[float], t: int,
                      predicted_noise: List[float]) -> List[float]:
        """
        Simplified denoising step.
        
        Args:
            xt: Noisy data
            t: Step
            predicted_noise: Predicted noise
        
        Returns:
            Denoised data
        """
        alpha_bar = self.schedule.alpha_bar(t)
        if alpha_bar <= 0:
            return xt
        
        # x0 prediction
        x0 = [(xt[i] - math.sqrt(1.0 - alpha_bar) * predicted_noise[i]) / math.sqrt(alpha_bar)
              for i in range(len(xt))]
        return x0


class QuantumDiffusionModel:
    """
    Unified quantum diffusion model controller.
    """
    
    def __init__(self, data_dim: int = 4, num_steps: int = 100):
        """
        Args:
            data_dim: Data dimension
            num_steps: Diffusion steps
        """
        self.dim = data_dim
        self.schedule = NoiseSchedule(num_steps)
        self.forward = ForwardDiffusion(self.schedule)
        self.sampler = ReverseSampler(self.schedule)
        self.quantum_kernel = QuantumNoiseKernel()
        self.training_history: List[float] = []
    
    def predict_noise(self, xt: List[float], t: int) -> List[float]:
        """
        Predict noise (simplified neural approximation).
        
        Args:
            xt: Noisy data
            t: Step
        
        Returns:
            Predicted noise
        """
        # Simplified: use quantum noise as prediction
        qn = self.quantum_kernel.quantum_noise(self.dim)
        # Scale by time embedding
        scale = t / self.schedule.T
        return [scale * qn[i] + (1.0 - scale) * xt[i] * 0.1 for i in range(self.dim)]
    
    def generate(self, num_samples: int = 1) -> List[List[float]]:
        """
        Generate samples via reverse diffusion.
        
        Args:
            num_samples: Number of samples
        
        Returns:
            Generated samples
        """
        samples = []
        for _ in range(num_samples):
            # Start from noise
            xt = [random.gauss(0.0, 1.0) for _ in range(self.dim)]
            
            # Reverse diffusion
            for t in range(self.schedule.T - 1, -1, -1):
                pred_noise = self.predict_noise(xt, t)
                xt = self.sampler.denoise_step(xt, t, pred_noise)
            
            samples.append(xt)
        
        return samples
    
    def diffusion_loss(self, x0: List[float]) -> float:
        """
        Compute diffusion training loss (MSE on noise).
        
        Args:
            x0: Clean data
        
        Returns:
            Loss
        """
        t = random.randint(0, self.schedule.T - 1)
        xt, true_noise = self.forward.add_noise(x0, t)
        pred_noise = self.predict_noise(xt, t)
        
        mse = sum((true_noise[i] - pred_noise[i])**2 for i in range(len(x0))) / len(x0)
        return mse
    
    def train_step(self, dataset: List[List[float]]):
        """
        Single training step.
        
        Args:
            dataset: Training data
        """
        total_loss = 0.0
        for x0 in dataset:
            loss = self.diffusion_loss(x0)
            total_loss += loss
        
        avg_loss = total_loss / len(dataset) if dataset else 0.0
        self.training_history.append(avg_loss)
    
    def diffusion_summary(self) -> Dict:
        """Get diffusion model summary."""
        return {
            "data_dim": self.dim,
            "diffusion_steps": self.schedule.T,
            "training_steps": len(self.training_history),
            "latest_loss": self.training_history[-1] if self.training_history else 0.0,
            "final_snr_dB": self.schedule.signal_to_noise_ratio(0)
        }
