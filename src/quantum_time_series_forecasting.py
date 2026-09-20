"""
Quantum Time Series Forecasting Module
Quantum recurrent network, quantum Fourier forecasting, trend
extraction, and prediction confidence for autonomous forecasting.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class QuantumRecurrentCell:
    """
    Quantum-inspired recurrent cell.
    """
    
    def __init__(self, hidden_dim: int = 4):
        """
        Args:
            hidden_dim: Hidden dimension
        """
        self.hidden_dim = hidden_dim
        self.state = [0.0] * hidden_dim
        self.weights = [[0.1 for _ in range(hidden_dim)] for _ in range(hidden_dim)]
    
    def step(self, input_val: float) -> List[float]:
        """
        Process one time step.
        
        Args:
            input_val: Input
        
        Returns:
            New hidden state
        """
        new_state = []
        for i in range(self.hidden_dim):
            # Quantum-inspired rotation
            angle = input_val * math.pi + sum(
                self.state[j] * self.weights[j][i]
                for j in range(self.hidden_dim)
            )
            new_state.append(math.sin(angle))
        
        self.state = new_state
        return self.state
    
    def output(self) -> float:
        """
        Compute output.
        
        Returns:
            Output value
        """
        return sum(self.state) / max(len(self.state), 1)


class QuantumFourierForecaster:
    """
    Quantum Fourier forecasting.
    """
    
    def __init__(self, num_freqs: int = 4):
        """
        Args:
            num_freqs: Frequencies
        """
        self.num_freqs = num_freqs
    
    def dft(self, series: List[float]) -> List[complex]:
        """
        Discrete Fourier transform.
        
        Args:
            series: Time series
        
        Returns:
            Spectrum
        """
        N = len(series)
        spectrum = []
        for k in range(min(self.num_freqs, N)):
            s = complex(0, 0)
            for n in range(N):
                angle = -2.0 * math.pi * k * n / N
                s += series[n] * complex(math.cos(angle), math.sin(angle))
            spectrum.append(s)
        return spectrum
    
    def predict(self, series: List[float],
               horizon: int = 1) -> List[float]:
        """
        Predict future values.
        
        Args:
            series: Time series
            horizon: Prediction horizon
        
        Returns:
            Predictions
        """
        N = len(series)
        spectrum = self.dft(series)
        
        predictions = []
        for h in range(1, horizon + 1):
            val = 0.0
            for k, coeff in enumerate(spectrum):
                angle = 2.0 * math.pi * k * (N + h - 1) / N
                val += (coeff.real * math.cos(angle) -
                        coeff.imag * math.sin(angle))
            predictions.append(val / N)
        
        return predictions


class TrendExtractor:
    """
    Extract trend from time series.
    """
    
    def __init__(self):
        pass
    
    def linear_trend(self, series: List[float]) -> Tuple[float, float]:
        """
        Fit linear trend.
        
        Args:
            series: Series
        
        Returns:
            (slope, intercept)
        """
        n = len(series)
        if n < 2:
            return (0.0, series[0] if series else 0.0)
        
        x_mean = sum(range(n)) / n
        y_mean = sum(series) / n
        
        num = sum((i - x_mean) * (series[i] - y_mean) for i in range(n))
        den = sum((i - x_mean) ** 2 for i in range(n))
        
        if den == 0:
            return (0.0, y_mean)
        
        slope = num / den
        intercept = y_mean - slope * x_mean
        
        return (slope, intercept)
    
    def detrend(self, series: List[float]) -> List[float]:
        """
        Remove linear trend.
        
        Args:
            series: Series
        
        Returns:
            Detrended series
        """
        slope, intercept = self.linear_trend(series)
        return [series[i] - (slope * i + intercept) for i in range(len(series))]


class PredictionConfidence:
    """
    Compute prediction confidence intervals.
    """
    
    def __init__(self):
        pass
    
    def interval(self, predictions: List[float],
                historical_errors: List[float],
                confidence: float = 0.95) -> List[Tuple[float, float]]:
        """
        Compute confidence intervals.
        
        Args:
            predictions: Predictions
            historical_errors: Historical errors
            confidence: Confidence level
        
        Returns:
            (lower, upper) intervals
        """
        if not historical_errors:
            return [(p, p) for p in predictions]
        
        std = (sum(e**2 for e in historical_errors) / len(historical_errors)) ** 0.5
        
        # Simplified: 2 sigma for 95%
        margin = 2.0 * std
        
        return [(p - margin, p + margin) for p in predictions]


class QuantumTimeSeriesForecasting:
    """
    Unified quantum time series forecasting controller.
    """
    
    def __init__(self):
        self.recurrent = QuantumRecurrentCell()
        self.fourier = QuantumFourierForecaster()
        self.trend = TrendExtractor()
        self.confidence = PredictionConfidence()
        self.history: List[float] = []
        self.predictions: List[float] = []
    
    def add_history(self, value: float):
        """
        Add historical value.
        
        Args:
            value: Value
        """
        self.history.append(value)
        self.recurrent.step(value)
    
    def forecast_recurrent(self, horizon: int = 1) -> List[float]:
        """
        Forecast using recurrent model.
        
        Args:
            horizon: Horizon
        
        Returns:
            Predictions
        """
        predictions = []
        state = self.recurrent.state[:]
        
        for _ in range(horizon):
            pred = sum(state) / max(len(state), 1)
            predictions.append(pred)
            # Update state
            state = self.recurrent.step(pred)
        
        self.predictions = predictions
        return predictions
    
    def forecast_fourier(self, horizon: int = 1) -> List[float]:
        """
        Forecast using Fourier model.
        
        Args:
            horizon: Horizon
        
        Returns:
            Predictions
        """
        if len(self.history) < 2:
            return [0.0] * horizon
        
        return self.fourier.predict(self.history, horizon)
    
    def forecast_combined(self, horizon: int = 1) -> List[float]:
        """
        Combined forecast.
        
        Args:
            horizon: Horizon
        
        Returns:
            Predictions
        """
        rec = self.forecast_recurrent(horizon)
        fou = self.forecast_fourier(horizon)
        
        return [(r + f) / 2.0 for r, f in zip(rec, fou)]
    
    def qtsf_summary(self) -> Dict:
        """Get summary."""
        return {
            "history_length": len(self.history),
            "predictions": len(self.predictions),
            "hidden_dim": self.recurrent.hidden_dim
        }
