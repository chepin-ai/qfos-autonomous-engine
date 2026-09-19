"""
Neural Compute Module
Lightweight neural network inference engine for
onboard spacecraft AI with minimal compute footprint.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Tensor:
    """Multi-dimensional array for neural computation."""
    data: List[float]
    shape: Tuple[int, ...]
    
    def __post_init__(self):
        expected = 1
        for dim in self.shape:
            expected *= dim
        if len(self.data) != expected:
            raise ValueError(f"Data size {len(self.data)} doesn't match shape {self.shape}")
    
    def reshape(self, new_shape: Tuple[int, ...]) -> "Tensor":
        """Reshape tensor."""
        new_size = 1
        for dim in new_shape:
            new_size *= dim
        if new_size != len(self.data):
            raise ValueError("Shape mismatch")
        return Tensor(self.data[:], new_shape)


def relu(x: float) -> float:
    """ReLU activation."""
    return max(0.0, x)


def sigmoid(x: float) -> float:
    """Sigmoid activation."""
    if x < -10:
        return 0.0
    if x > 10:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def tanh(x: float) -> float:
    """Tanh activation."""
    return math.tanh(x)


class DenseLayer:
    """
    Fully connected dense layer.
    
    y = activation(x @ W + b)
    """
    
    def __init__(self, input_size: int, output_size: int,
                 activation: str = "relu",
                 weights: Optional[List[float]] = None,
                 bias: Optional[List[float]] = None):
        """
        Args:
            input_size: Input dimension
            output_size: Output dimension
            activation: "relu", "sigmoid", "tanh", "linear"
            weights: Flat weight matrix [input_size * output_size]
            bias: Bias vector [output_size]
        """
        self.input_size = input_size
        self.output_size = output_size
        
        # Activation function
        if activation == "relu":
            self.activation = relu
        elif activation == "sigmoid":
            self.activation = sigmoid
        elif activation == "tanh":
            self.activation = tanh
        else:
            self.activation = lambda x: x
        
        # Initialize weights
        if weights is not None:
            self.weights = weights[:]
        else:
            # Xavier initialization
            scale = math.sqrt(2.0 / (input_size + output_size))
            self.weights = [scale * (2.0 * (i % 100) / 100.0 - 1.0)
                           for i in range(input_size * output_size)]
        
        if bias is not None:
            self.bias = bias[:]
        else:
            self.bias = [0.0] * output_size
    
    def forward(self, inputs: List[float]) -> List[float]:
        """
        Forward pass.
        
        Args:
            inputs: Input vector [input_size]
        
        Returns:
            Output vector [output_size]
        """
        if len(inputs) != self.input_size:
            raise ValueError(f"Expected {self.input_size} inputs, got {len(inputs)}")
        
        outputs = []
        for j in range(self.output_size):
            # Compute dot product
            neuron_sum = self.bias[j]
            for i in range(self.input_size):
                neuron_sum += inputs[i] * self.weights[i * self.output_size + j]
            outputs.append(self.activation(neuron_sum))
        
        return outputs
    
    def quantize_weights(self, bits: int = 8) -> Dict:
        """
        Quantize weights to lower precision.
        
        Args:
            bits: Quantization bits
        
        Returns:
            Quantized weights dict
        """
        levels = 2 ** bits - 1
        max_val = max(abs(w) for w in self.weights) or 1.0
        scale = levels / (2.0 * max_val)
        
        quantized = [max(-levels // 2, min(levels // 2, int(w * scale))) for w in self.weights]
        
        return {
            "weights": quantized,
            "scale": scale,
            "bits": bits,
            "original_max": max_val
        }


class NeuralNetwork:
    """
    Simple feedforward neural network.
    """
    
    def __init__(self):
        self.layers: List[DenseLayer] = []
        self.input_shape: Tuple[int, ...] = ()
    
    def add_layer(self, layer: DenseLayer):
        """Add a layer."""
        if not self.layers:
            self.input_shape = (layer.input_size,)
        self.layers.append(layer)
    
    def predict(self, inputs: List[float]) -> List[float]:
        """
        Run inference.
        
        Args:
            inputs: Input vector
        
        Returns:
            Output vector
        """
        current = inputs[:]
        for layer in self.layers:
            current = layer.forward(current)
        return current
    
    def classify(self, inputs: List[float]) -> int:
        """
        Classification: return index of max output.
        
        Args:
            inputs: Input vector
        
        Returns:
            Class index
        """
        outputs = self.predict(inputs)
        return max(range(len(outputs)), key=lambda i: outputs[i])
    
    def get_model_size(self) -> Dict:
        """Get model size info."""
        total_params = 0
        for layer in self.layers:
            total_params += len(layer.weights) + len(layer.bias)
        
        return {
            "layers": len(self.layers),
            "total_parameters": total_params,
            "memory_kb": total_params * 4 / 1024  # float32
        }
    
    @staticmethod
    def create_classifier(input_size: int, num_classes: int,
                         hidden_sizes: Optional[List[int]] = None) -> "NeuralNetwork":
        """
        Create a classification network.
        
        Args:
            input_size: Input dimension
            num_classes: Number of output classes
            hidden_sizes: Hidden layer sizes
        
        Returns:
            NeuralNetwork
        """
        net = NeuralNetwork()
        hidden_sizes = hidden_sizes or [64, 32]
        
        prev_size = input_size
        for hidden_size in hidden_sizes:
            net.add_layer(DenseLayer(prev_size, hidden_size, "relu"))
            prev_size = hidden_size
        
        net.add_layer(DenseLayer(prev_size, num_classes, "linear"))
        
        return net


class InferenceEngine:
    """
    Optimized inference engine with batching and caching.
    """
    
    def __init__(self):
        self.models: Dict[str, NeuralNetwork] = {}
        self.cache: Dict[str, Tuple[List[float], List[float]]] = {}
        self.cache_size = 100
        self.inference_count = 0
    
    def load_model(self, model_id: str, model: NeuralNetwork):
        """Load a model."""
        self.models[model_id] = model
    
    def infer(self, model_id: str, inputs: List[float],
             use_cache: bool = True) -> Optional[List[float]]:
        """
        Run inference with optional caching.
        
        Args:
            model_id: Model identifier
            inputs: Input vector
            use_cache: Use result cache
        
        Returns:
            Output vector or None
        """
        if model_id not in self.models:
            return None
        
        # Check cache
        cache_key = f"{model_id}:{hash(tuple(inputs))}"
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key][1]
        
        # Run inference
        result = self.models[model_id].predict(inputs)
        self.inference_count += 1
        
        # Update cache
        if use_cache:
            if len(self.cache) >= self.cache_size:
                self.cache.pop(next(iter(self.cache)))
            self.cache[cache_key] = (inputs[:], result[:])
        
        return result
    
    def batch_infer(self, model_id: str,
                   batch_inputs: List[List[float]]) -> List[Optional[List[float]]]:
        """
        Batch inference.
        
        Args:
            model_id: Model identifier
            batch_inputs: List of input vectors
        
        Returns:
            List of output vectors
        """
        return [self.infer(model_id, inputs, use_cache=False)
                for inputs in batch_inputs]
    
    def engine_stats(self) -> Dict:
        """Get engine statistics."""
        return {
            "loaded_models": len(self.models),
            "inference_count": self.inference_count,
            "cache_entries": len(self.cache),
            "cache_hit_rate": "N/A"  # Would track in production
        }
