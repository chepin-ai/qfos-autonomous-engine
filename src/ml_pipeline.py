"""
Machine Learning Pipeline Module
Online learning, parameter adaptation, and performance
optimization from mission telemetry data.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class TrainingSample:
    """A training sample for online learning."""
    features: List[float]
    label: float
    weight: float = 1.0
    timestamp: float = 0.0


class OnlineRegressor:
    """
    Online linear regressor with gradient descent.
    
    Adapts weights incrementally as new data arrives.
    """
    
    def __init__(self, num_features: int,
                 learning_rate: float = 0.01,
                 regularization: float = 0.001):
        """
        Args:
            num_features: Number of input features
            learning_rate: Gradient descent step size
            regularization: L2 regularization strength
        """
        self.num_features = num_features
        self.lr = learning_rate
        self.reg = regularization
        self.weights = [0.0] * num_features
        self.bias = 0.0
        self.samples_seen = 0
    
    def predict(self, features: List[float]) -> float:
        """
        Predict output for features.
        
        Args:
            features: Input features
        
        Returns:
            Predicted value
        """
        if len(features) != self.num_features:
            return 0.0
        
        return sum(w * f for w, f in zip(self.weights, features)) + self.bias
    
    def update(self, features: List[float], label: float):
        """
        Update model with one sample.
        
        Args:
            features: Input features
            label: True output
        """
        if len(features) != self.num_features:
            return
        
        prediction = self.predict(features)
        error = prediction - label
        
        # Gradient descent
        for i in range(self.num_features):
            grad = error * features[i] + self.reg * self.weights[i]
            self.weights[i] -= self.lr * grad
        
        self.bias -= self.lr * error
        self.samples_seen += 1
    
    def train_batch(self, samples: List[TrainingSample],
                    epochs: int = 1):
        """
        Train on a batch of samples.
        
        Args:
            samples: Training samples
            epochs: Number of passes
        """
        for _ in range(epochs):
            for sample in samples:
                self.update(sample.features, sample.label)
    
    def evaluate(self, samples: List[TrainingSample]) -> Dict:
        """
        Evaluate model on samples.
        
        Args:
            samples: Test samples
        
        Returns:
            Metrics dict
        """
        if not samples:
            return {"mse": 0.0, "mae": 0.0, "samples": 0}
        
        errors = []
        for sample in samples:
            pred = self.predict(sample.features)
            errors.append(pred - sample.label)
        
        mse = sum(e**2 for e in errors) / len(errors)
        mae = sum(abs(e) for e in errors) / len(errors)
        
        return {
            "mse": round(mse, 6),
            "mae": round(mae, 6),
            "rmse": round(math.sqrt(mse), 6),
            "samples": len(samples)
        }


class KalmanFilterEstimator:
    """
    Kalman filter for state estimation from noisy measurements.
    
    Used for adaptive parameter estimation.
    """
    
    def __init__(self, state_dim: int = 1,
                 process_noise: float = 0.01,
                 measurement_noise: float = 1.0):
        """
        Args:
            state_dim: State dimension
            process_noise: Process noise covariance
            measurement_noise: Measurement noise covariance
        """
        self.state_dim = state_dim
        self.state = [0.0] * state_dim
        self.covariance = [1.0] * state_dim
        self.Q = process_noise
        self.R = measurement_noise
    
    def predict(self):
        """Prediction step."""
        # State prediction: x = x (identity transition)
        # Covariance prediction: P = P + Q
        for i in range(self.state_dim):
            self.covariance[i] += self.Q
    
    def update(self, measurement: float, state_idx: int = 0):
        """
        Update step with measurement.
        
        Args:
            measurement: Measured value
            state_idx: Which state element
        """
        if state_idx >= self.state_dim:
            return
        
        # Kalman gain
        P = self.covariance[state_idx]
        K = P / (P + self.R)
        
        # State update
        innovation = measurement - self.state[state_idx]
        self.state[state_idx] += K * innovation
        
        # Covariance update
        self.covariance[state_idx] = (1.0 - K) * P
    
    def get_state(self, state_idx: int = 0) -> float:
        """Get current state estimate."""
        if state_idx < self.state_dim:
            return self.state[state_idx]
        return 0.0


class PerformanceOptimizer:
    """
    Performance optimizer using hill-climbing.
    
    Adapts control parameters to maximize a performance metric.
    """
    
    def __init__(self, param_bounds: List[Tuple[float, float]],
                 step_size: float = 0.1,
                 convergence_threshold: float = 0.001):
        """
        Args:
            param_bounds: List of (min, max) for each parameter
            step_size: Exploration step size
            convergence_threshold: Convergence criterion
        """
        self.bounds = param_bounds
        self.step_size = step_size
        self.convergence = convergence_threshold
        self.current_params = [(b[0] + b[1]) / 2.0 for b in param_bounds]
        self.best_score = -float('inf')
        self.iteration = 0
    
    def optimize_step(self, evaluate: Callable[[List[float]], float]) -> Dict:
        """
        One optimization step.
        
        Args:
            evaluate: Function that scores parameter set
        
        Returns:
            Step result
        """
        self.iteration += 1
        
        # Evaluate current
        current_score = evaluate(self.current_params)
        
        # Try perturbations
        best_local = current_score
        best_params = self.current_params[:]
        
        for i in range(len(self.current_params)):
            for direction in [-1, 1]:
                test_params = self.current_params[:]
                step = self.step_size * (self.bounds[i][1] - self.bounds[i][0])
                test_params[i] += direction * step
                test_params[i] = max(self.bounds[i][0],
                                    min(self.bounds[i][1], test_params[i]))
                
                score = evaluate(test_params)
                if score > best_local:
                    best_local = score
                    best_params = test_params[:]
        
        # Update
        improved = best_local > current_score
        if improved:
            self.current_params = best_params
        
        # Update best score
        if best_local > self.best_score:
            self.best_score = best_local
        
        converged = abs(best_local - current_score) < self.convergence
        
        return {
            "iteration": self.iteration,
            "params": [round(p, 6) for p in self.current_params],
            "score": round(current_score, 6),
            "best_score": round(self.best_score, 6),
            "improved": improved,
            "converged": converged
        }
    
    def optimize(self, evaluate: Callable[[List[float]], float],
                max_iterations: int = 100) -> Dict:
        """
        Run optimization to convergence.
        
        Args:
            evaluate: Scoring function
            max_iterations: Maximum iterations
        
        Returns:
            Final result
        """
        for _ in range(max_iterations):
            result = self.optimize_step(evaluate)
            if result["converged"]:
                break
        
        return {
            "final_params": [round(p, 6) for p in self.current_params],
            "best_score": round(self.best_score, 6),
            "iterations": self.iteration
        }


class MLPipeline:
    """
    Integrated machine learning pipeline.
    
    Combines online regression, state estimation,
    and parameter optimization.
    """
    
    def __init__(self):
        self.regressors: Dict[str, OnlineRegressor] = {}
        self.estimators: Dict[str, KalmanFilterEstimator] = {}
        self.optimizers: Dict[str, PerformanceOptimizer] = {}
        self.performance_log: List[Dict] = []
    
    def add_regressor(self, name: str, num_features: int,
                     learning_rate: float = 0.01):
        """Add an online regressor."""
        self.regressors[name] = OnlineRegressor(num_features, learning_rate)
    
    def add_estimator(self, name: str, state_dim: int = 1):
        """Add a Kalman filter estimator."""
        self.estimators[name] = KalmanFilterEstimator(state_dim)
    
    def add_optimizer(self, name: str, param_bounds: List[Tuple[float, float]]):
        """Add a performance optimizer."""
        self.optimizers[name] = PerformanceOptimizer(param_bounds)
    
    def predict(self, regressor_name: str, features: List[float]) -> float:
        """Make prediction."""
        if regressor_name in self.regressors:
            return self.regressors[regressor_name].predict(features)
        return 0.0
    
    def adapt(self, regressor_name: str, features: List[float],
              label: float):
        """Adapt regressor with new data."""
        if regressor_name in self.regressors:
            self.regressors[regressor_name].update(features, label)
    
    def estimate(self, estimator_name: str, measurement: float,
                state_idx: int = 0) -> float:
        """Update and get state estimate."""
        if estimator_name in self.estimators:
            est = self.estimators[estimator_name]
            est.predict()
            est.update(measurement, state_idx)
            return est.get_state(state_idx)
        return measurement
    
    def optimize(self, optimizer_name: str,
                evaluate: Callable[[List[float]], float],
                max_iterations: int = 50) -> Dict:
        """Run optimizer."""
        if optimizer_name in self.optimizers:
            result = self.optimizers[optimizer_name].optimize(evaluate, max_iterations)
            self.performance_log.append(result)
            return result
        return {}
    
    def pipeline_summary(self) -> Dict:
        """Get pipeline summary."""
        return {
            "regressors": len(self.regressors),
            "estimators": len(self.estimators),
            "optimizers": len(self.optimizers),
            "optimizations_run": len(self.performance_log),
            "regressor_samples": {name: r.samples_seen
                                 for name, r in self.regressors.items()}
        }
