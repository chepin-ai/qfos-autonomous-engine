"""
Unit tests for onboard AI module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from onboard_ai import OnboardAI, ModelQuantizer, InferenceScheduler, InferenceTask, ModelProfile
from neural_compute import NeuralNetwork, DenseLayer


class TestModelQuantizer(unittest.TestCase):
    """Test model quantizer."""
    
    def setUp(self):
        self.net = NeuralNetwork()
        self.net.add_layer(DenseLayer(2, 2, "linear",
                                     weights=[0.5, -0.5, 0.3, -0.3],
                                     bias=[0.0, 0.0]))
        self.quantizer = ModelQuantizer(8)
    
    def test_quantize(self):
        """Should quantize model."""
        report = self.quantizer.quantize_model(self.net)
        self.assertGreater(report["overall_compression"], 1.0)
        print(f"  [PASS] Quantize: {report['overall_compression']:.1f}x compression")
    
    def test_accuracy_loss(self):
        """Should estimate accuracy loss."""
        loss = self.quantizer.estimate_accuracy_loss(32)
        self.assertGreater(loss, 0)
        print(f"  [PASS] Loss: {loss:.3f}")


class TestInferenceScheduler(unittest.TestCase):
    """Test inference scheduler."""
    
    def setUp(self):
        self.sched = InferenceScheduler()
        self.net = NeuralNetwork()
        self.net.add_layer(DenseLayer(2, 1, "linear",
                                     weights=[1.0, 1.0],
                                     bias=[0.0]))
        self.sched.load_model_for_inference("m1", self.net)
    
    def test_submit(self):
        """Should submit task."""
        task = InferenceTask("t1", "m1", [1.0, 0.0])
        self.sched.submit(task)
        self.assertEqual(len(self.sched.task_queue), 1)
        print("  [PASS] Submit: 1 task")
    
    def test_schedule(self):
        """Should schedule and execute."""
        task = InferenceTask("t1", "m1", [1.0, 1.0])
        self.sched.submit(task)
        results = self.sched.schedule()
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0]["result"])
        print(f"  [PASS] Schedule: result={results[0]['result']}")
    
    def test_stats(self):
        """Should provide stats."""
        task = InferenceTask("t1", "m1", [1.0, 1.0])
        self.sched.submit(task)
        self.sched.schedule()
        stats = self.sched.get_scheduler_stats()
        self.assertEqual(stats["completed"], 1)
        print(f"  [PASS] Stats: {stats['completed']} completed")


class TestOnboardAI(unittest.TestCase):
    """Test onboard AI."""
    
    def setUp(self):
        self.ai = OnboardAI()
        self.net = NeuralNetwork()
        self.net.add_layer(DenseLayer(3, 2, "relu"))
        self.net.add_layer(DenseLayer(2, 1, "linear"))
    
    def test_register(self):
        """Should register model."""
        self.ai.register_model("nav", self.net)
        self.assertIn("nav", self.ai.models)
        print("  [PASS] Register: nav")
    
    def test_inference(self):
        """Should run inference."""
        self.ai.register_model("nav", self.net)
        result = self.ai.run_inference("nav", [1.0, 0.5, 0.2])
        self.assertIsNotNone(result)
        self.assertIn("result", result)
        print(f"  [PASS] Inference: {result['result']}")
    
    def test_quantize(self):
        """Should quantize."""
        self.ai.register_model("nav", self.net)
        report = self.ai.quantize("nav", 8)
        self.assertIsNotNone(report)
        print(f"  [PASS] Quantize: {report['overall_compression']:.1f}x")
    
    def test_model_info(self):
        """Should get model info."""
        self.ai.register_model("nav", self.net)
        info = self.ai.get_model_info("nav")
        self.assertEqual(info["model_id"], "nav")
        print(f"  [PASS] Info: {info['layers']} layers")
    
    def test_summary(self):
        """Should provide summary."""
        self.ai.register_model("nav", self.net)
        summary = self.ai.ai_summary()
        self.assertEqual(summary["registered_models"], 1)
        print(f"  [PASS] Summary: {summary['registered_models']} models")


if __name__ == '__main__':
    unittest.main(verbosity=2)
