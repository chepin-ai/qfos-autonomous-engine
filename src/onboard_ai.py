"""
Onboard AI Module
Mission-time neural model execution, quantization,
and resource-aware inference scheduling.
"""

import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from neural_compute import NeuralNetwork, InferenceEngine, DenseLayer


@dataclass
class InferenceTask:
    """A task for onboard AI inference."""
    task_id: str
    model_id: str
    inputs: List[float]
    priority: int = 1
    deadline_ms: Optional[float] = None
    submitted_at: float = field(default_factory=time.time)


@dataclass
class ModelProfile:
    """Performance profile of a neural model."""
    model_id: str
    input_size: int
    output_size: int
    parameters: int
    inference_time_ms: float = 0.0
    memory_kb: float = 0.0
    accuracy: float = 0.0


class ModelQuantizer:
    """
    Quantize neural models for onboard execution.
    
    Reduces memory and compute requirements.
    """
    
    def __init__(self, target_bits: int = 8):
        """
        Args:
            target_bits: Target quantization bits
        """
        self.target_bits = target_bits
    
    def quantize_model(self, model: NeuralNetwork) -> Dict:
        """
        Quantize all layers in a model.
        
        Args:
            model: Model to quantize
        
        Returns:
            Quantization report
        """
        reports = []
        total_params_before = 0
        total_params_after = 0
        
        for i, layer in enumerate(model.layers):
            before = len(layer.weights) * 4  # float32 = 4 bytes
            q = layer.quantize_weights(self.target_bits)
            after = len(q["weights"]) * self.target_bits / 8
            
            reports.append({
                "layer": i,
                "bits": self.target_bits,
                "size_before_bytes": before,
                "size_after_bytes": after,
                "compression_ratio": before / max(after, 1)
            })
            
            total_params_before += before
            total_params_after += after
        
        return {
            "layers": reports,
            "total_size_before_bytes": total_params_before,
            "total_size_after_bytes": total_params_after,
            "overall_compression": total_params_before / max(total_params_after, 1)
        }
    
    def estimate_accuracy_loss(self, original_bits: int = 32) -> float:
        """
        Estimate accuracy loss from quantization.
        
        Args:
            original_bits: Original precision
        
        Returns:
            Estimated accuracy loss
        """
        # Simple heuristic: more bits = less loss
        bit_diff = original_bits - self.target_bits
        if bit_diff <= 8:
            return 0.01 * bit_diff
        elif bit_diff <= 16:
            return 0.02 * bit_diff
        else:
            return 0.05 * bit_diff


class InferenceScheduler:
    """
    Resource-aware inference scheduler.
    
    Schedules inference tasks based on priority,
    deadline, and available compute.
    """
    
    def __init__(self, max_concurrent: int = 4,
                 max_memory_mb: float = 100.0):
        """
        Args:
            max_concurrent: Max concurrent inferences
            max_memory_mb: Max memory budget
        """
        self.max_concurrent = max_concurrent
        self.max_memory_mb = max_memory_mb
        self.task_queue: List[InferenceTask] = []
        self.running: Dict[str, InferenceTask] = {}
        self.completed: List[Dict] = []
        self.engine = InferenceEngine()
    
    def submit(self, task: InferenceTask):
        """Submit an inference task."""
        self.task_queue.append(task)
        # Sort by priority then deadline
        self.task_queue.sort(key=lambda t: (t.priority, t.deadline_ms or float('inf')))
    
    def schedule(self) -> List[Dict]:
        """
        Schedule pending tasks.
        
        Returns:
            List of execution results
        """
        results = []
        
        while self.task_queue and len(self.running) < self.max_concurrent:
            task = self.task_queue.pop(0)
            
            # Check if model loaded
            if task.model_id not in self.engine.models:
                # Skip for now, requeue
                self.task_queue.append(task)
                break
            
            # Execute
            start_time = time.time()
            result = self.engine.infer(task.model_id, task.inputs)
            elapsed_ms = (time.time() - start_time) * 1000
            
            exec_result = {
                "task_id": task.task_id,
                "model_id": task.model_id,
                "result": result,
                "latency_ms": elapsed_ms,
                "deadline_met": task.deadline_ms is None or elapsed_ms <= task.deadline_ms
            }
            
            self.completed.append(exec_result)
            results.append(exec_result)
        
        return results
    
    def load_model_for_inference(self, model_id: str, model: NeuralNetwork):
        """Load model into inference engine."""
        self.engine.load_model(model_id, model)
    
    def get_scheduler_stats(self) -> Dict:
        """Get scheduler statistics."""
        total = len(self.completed)
        met = sum(1 for r in self.completed if r["deadline_met"])
        avg_latency = sum(r["latency_ms"] for r in self.completed) / max(1, total)
        
        return {
            "queued": len(self.task_queue),
            "completed": total,
            "deadlines_met": met,
            "deadline_miss_rate": round((total - met) / max(1, total), 2),
            "avg_latency_ms": round(avg_latency, 2),
            "models_loaded": len(self.engine.models)
        }


class OnboardAI:
    """
    Unified onboard AI controller.
    
    Manages models, quantization, and inference scheduling.
    """
    
    def __init__(self):
        self.models: Dict[str, NeuralNetwork] = {}
        self.profiles: Dict[str, ModelProfile] = {}
        self.quantizer = ModelQuantizer()
        self.scheduler = InferenceScheduler()
    
    def register_model(self, model_id: str, model: NeuralNetwork,
                      profile: Optional[ModelProfile] = None):
        """
        Register a model for onboard use.
        
        Args:
            model_id: Model identifier
            model: Neural network
            profile: Performance profile
        """
        self.models[model_id] = model
        
        if profile is None:
            size_info = model.get_model_size()
            profile = ModelProfile(
                model_id=model_id,
                input_size=model.input_shape[0] if model.input_shape else 0,
                output_size=model.layers[-1].output_size if model.layers else 0,
                parameters=size_info["total_parameters"],
                memory_kb=size_info["memory_kb"]
            )
        
        self.profiles[model_id] = profile
        self.scheduler.load_model_for_inference(model_id, model)
    
    def run_inference(self, model_id: str, inputs: List[float],
                     priority: int = 1,
                     deadline_ms: Optional[float] = None) -> Optional[Dict]:
        """
        Run inference on a model.
        
        Args:
            model_id: Model to use
            inputs: Input data
            priority: Task priority
            deadline_ms: Deadline in milliseconds
        
        Returns:
            Result dict or None
        """
        if model_id not in self.models:
            return None
        
        task = InferenceTask(
            task_id=f"inf_{int(time.time() * 1000)}",
            model_id=model_id,
            inputs=inputs,
            priority=priority,
            deadline_ms=deadline_ms
        )
        
        self.scheduler.submit(task)
        results = self.scheduler.schedule()
        
        return results[0] if results else None
    
    def quantize(self, model_id: str, bits: int = 8) -> Optional[Dict]:
        """
        Quantize a registered model.
        
        Args:
            model_id: Model to quantize
            bits: Target bits
        
        Returns:
            Quantization report or None
        """
        if model_id not in self.models:
            return None
        
        self.quantizer.target_bits = bits
        return self.quantizer.quantize_model(self.models[model_id])
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get model information."""
        if model_id not in self.models:
            return None
        
        profile = self.profiles.get(model_id)
        model = self.models[model_id]
        
        return {
            "model_id": model_id,
            "layers": len(model.layers),
            "parameters": profile.parameters if profile else 0,
            "memory_kb": profile.memory_kb if profile else 0,
            "input_size": profile.input_size if profile else 0,
            "output_size": profile.output_size if profile else 0
        }
    
    def ai_summary(self) -> Dict:
        """Get onboard AI summary."""
        return {
            "registered_models": len(self.models),
            "scheduler_stats": self.scheduler.get_scheduler_stats(),
            "total_parameters": sum(p.parameters for p in self.profiles.values())
        }
