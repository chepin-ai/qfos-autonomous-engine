"""
Quantum Natural Gradient Module
Quantum Fisher information matrix and natural gradient descent
for autonomous variational quantum optimization.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


class QuantumFisherInformation:
    """
    Quantum Fisher Information Matrix (QFIM).
    """
    
    def __init__(self, num_params: int):
        """
        Args:
            num_params: Number of parameters
        """
        self.n = num_params
        self.F: List[List[float]] = [[0.0] * num_params for _ in range(num_params)]
    
    def compute_from_states(self, states: List[List[complex]]) -> List[List[float]]:
        """
        Compute QFIM from parameter-shifted states.
        
        Args:
            states: List of quantum states for each parameter shift
        
        Returns:
            QFIM
        """
        for i in range(self.n):
            for j in range(self.n):
                if i >= len(states) or j >= len(states):
                    self.F[i][j] = 0.0
                    continue
                
                # F_ij = 4 * Re(<d_i psi| d_j psi> - <d_i psi|psi><psi|d_j psi>)
                # Simplified: overlap between shifted states
                overlap = sum(states[i][k].conjugate() * states[j][k]
                             for k in range(min(len(states[i]), len(states[j]))))
                self.F[i][j] = 4.0 * abs(overlap) ** 2
        
        return self.F
    
    def metric_tensor(self, params: List[float],
                     state_fn: Callable[[List[float]], List[complex]]) -> List[List[float]]:
        """
        Compute metric tensor using parameter shift.
        
        Args:
            params: Parameters
            state_fn: Function that returns quantum state given params
        
        Returns:
            Metric tensor
        """
        shift = math.pi / 2.0
        
        for i in range(self.n):
            for j in range(self.n):
                # Parameter shift for i
                params_plus_i = params[:]
                params_plus_i[i] += shift
                state_plus_i = state_fn(params_plus_i)
                
                params_minus_i = params[:]
                params_minus_i[i] -= shift
                state_minus_i = state_fn(params_minus_i)
                
                # Parameter shift for j
                params_plus_j = params[:]
                params_plus_j[j] += shift
                state_plus_j = state_fn(params_plus_j)
                
                params_minus_j = params[:]
                params_minus_j[j] -= shift
                state_minus_j = state_fn(params_minus_j)
                
                # Finite difference for derivative overlap
                di = [(state_plus_i[k] - state_minus_i[k]) / 2.0
                      for k in range(min(len(state_plus_i), len(state_minus_i)))]
                dj = [(state_plus_j[k] - state_minus_j[k]) / 2.0
                      for k in range(min(len(state_plus_j), len(state_minus_j)))]
                
                overlap = sum(di[k].conjugate() * dj[k] for k in range(min(len(di), len(dj))))
                self.F[i][j] = 4.0 * overlap.real
        
        return self.F
    
    def regularize(self, epsilon: float = 1e-4):
        """
        Add regularization to diagonal.
        
        Args:
            epsilon: Regularization
        """
        for i in range(self.n):
            self.F[i][i] += epsilon


class NaturalGradientDescent:
    """
    Natural gradient descent optimizer.
    """
    
    def __init__(self, lr: float = 0.01, damping: float = 1e-4):
        """
        Args:
            lr: Learning rate
            damping: Damping for Fisher matrix
        """
        self.lr = lr
        self.damping = damping
        self.history: List[float] = []
    
    def solve_linear(self, A: List[List[float]], b: List[float]) -> List[float]:
        """
        Solve linear system Ax = b using Jacobi iteration.
        
        Args:
            A: Matrix
            b: Vector
        
        Returns:
            x
        """
        n = len(b)
        x = [0.0] * n
        
        for _ in range(50):
            new_x = []
            for i in range(n):
                sigma = sum(A[i][j] * x[j] for j in range(n) if j != i)
                if abs(A[i][i]) > 1e-10:
                    new_x.append((b[i] - sigma) / A[i][i])
                else:
                    new_x.append(x[i])
            x = new_x
        
        return x
    
    def step(self, params: List[float],
            gradient: List[float],
            fisher: List[List[float]]) -> List[float]:
        """
        Natural gradient step.
        
        Args:
            params: Current parameters
            gradient: Gradient
            fisher: Fisher information matrix
        
        Returns:
            Updated parameters
        """
        # Add damping
        n = len(params)
        F_damped = [row[:] for row in fisher]
        for i in range(n):
            F_damped[i][i] += self.damping
        
        # Solve F * nat_grad = gradient
        nat_grad = self.solve_linear(F_damped, gradient)
        
        # Update
        new_params = [params[i] - self.lr * nat_grad[i] for i in range(n)]
        return new_params


class VariationalQuantumOptimizer:
    """
    Variational quantum optimizer with natural gradient.
    """
    
    def __init__(self, num_params: int, lr: float = 0.01):
        """
        Args:
            num_params: Number of parameters
            lr: Learning rate
        """
        self.n = num_params
        self.params = [random.uniform(-math.pi, math.pi) for _ in range(num_params)]
        self.qfi = QuantumFisherInformation(num_params)
        self.ngd = NaturalGradientDescent(lr)
        self.loss_history: List[float] = []
    
    def rotation_state(self, params: List[float]) -> List[complex]:
        """
        Simple parameterized quantum state.
        
        Args:
            params: Parameters
        
        Returns:
            Quantum state amplitudes
        """
        dim = 2 ** ((len(params) + 1) // 2)
        state = [complex(1.0 / math.sqrt(dim), 0.0)] * dim
        
        for i, p in enumerate(params):
            idx = i % dim
            state[idx] *= complex(math.cos(p), math.sin(p))
        
        # Normalize
        norm = sum(abs(z)**2 for z in state) ** 0.5
        if norm > 0:
            state = [z / norm for z in state]
        
        return state
    
    def compute_gradient(self, loss_fn: Callable[[List[float]], float]) -> List[float]:
        """
        Compute gradient using parameter shift.
        
        Args:
            loss_fn: Loss function
        
        Returns:
            Gradient
        """
        shift = math.pi / 2.0
        grad = []
        
        for i in range(self.n):
            params_plus = self.params[:]
            params_plus[i] += shift
            loss_plus = loss_fn(params_plus)
            
            params_minus = self.params[:]
            params_minus[i] -= shift
            loss_minus = loss_fn(params_minus)
            
            grad.append((loss_plus - loss_minus) / 2.0)
        
        return grad
    
    def optimize(self, loss_fn: Callable[[List[float]], float],
                epochs: int = 50) -> List[float]:
        """
        Optimize using natural gradient.
        
        Args:
            loss_fn: Loss function
            epochs: Epochs
        
        Returns:
            Optimized parameters
        """
        for epoch in range(epochs):
            loss = loss_fn(self.params)
            self.loss_history.append(loss)
            
            gradient = self.compute_gradient(loss_fn)
            
            # Compute Fisher information
            fisher = self.qfi.metric_tensor(self.params, self.rotation_state)
            self.qfi.regularize(self.ngd.damping)
            
            # Natural gradient step
            self.params = self.ngd.step(self.params, gradient, fisher)
        
        return self.params


class QuantumNaturalGradient:
    """
    Unified quantum natural gradient controller.
    """
    
    def __init__(self):
        self.optimizer: Optional[VariationalQuantumOptimizer] = None
        self.results: List[Dict] = []
    
    def build(self, num_params: int, lr: float = 0.01):
        """
        Build optimizer.
        
        Args:
            num_params: Parameters
            lr: Learning rate
        """
        self.optimizer = VariationalQuantumOptimizer(num_params, lr)
    
    def optimize(self, loss_fn: Callable[[List[float]], float],
                epochs: int = 50) -> Dict:
        """
        Run optimization.
        
        Args:
            loss_fn: Loss function
            epochs: Epochs
        
        Returns:
            Result
        """
        params = self.optimizer.optimize(loss_fn, epochs)
        
        result = {
            "final_params": params,
            "final_loss": self.optimizer.loss_history[-1] if self.optimizer.loss_history else 0.0,
            "epochs": epochs,
            "loss_history": self.optimizer.loss_history
        }
        self.results.append(result)
        return result
    
    def qng_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.results),
            "best_loss": min((r["final_loss"] for r in self.results), default=0.0)
        }
