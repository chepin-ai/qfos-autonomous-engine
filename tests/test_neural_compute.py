"""
Unit tests for neural compute module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from neural_compute import DenseLayer, NeuralNetwork, InferenceEngine, Tensor


class TestDenseLayer(unittest.TestCase):
    """Test dense layer."""
    
    def test_forward(self):
        """Should compute forward pass."""
        layer = DenseLayer(3, 2, "linear",
                          weights=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                          bias=[0.0, 0.0])
        out = layer.forward([1.0, 0.0, 0.0])
        self.assertEqual(len(out), 2)
        print(f"  [PASS] Forward: {out}")
    
    def test_relu(self):
        """Should apply ReLU."""
        layer = DenseLayer(2, 1, "relu",
                          weights=[-1.0, 1.0],
                          bias=[0.0])
        out = layer.forward([1.0, 1.0])
        self.assertEqual(out[0], 0.0)
        print(f"  [PASS] ReLU: {out[0]}")
    
    def test_sigmoid(self):
        """Should apply sigmoid."""
        layer = DenseLayer(1, 1, "sigmoid",
                          weights=[0.0],
                          bias=[0.0])
        out = layer.forward([0.0])
        self.assertAlmostEqual(out[0], 0.5, delta=0.01)
        print(f"  [PASS] Sigmoid: {out[0]:.3f}")
    
    def test_quantize(self):
        """Should quantize weights."""
        layer = DenseLayer(2, 2, "linear",
                          weights=[0.5, -0.5, 0.3, -0.3],
                          bias=[0.0, 0.0])
        q = layer.quantize_weights(8)
        self.assertIn("weights", q)
        self.assertIn("scale", q)
        print(f"  [PASS] Quantize: {q['bits']} bits")


class TestNeuralNetwork(unittest.TestCase):
    """Test neural network."""
    
    def setUp(self):
        self.net = NeuralNetwork()
        self.net.add_layer(DenseLayer(2, 3, "relu"))
        self.net.add_layer(DenseLayer(3, 1, "linear"))
    
    def test_predict(self):
        """Should predict."""
        out = self.net.predict([1.0, 0.5])
        self.assertEqual(len(out), 1)
        print(f"  [PASS] Predict: {out}")
    
    def test_classify(self):
        """Should classify."""
        net = NeuralNetwork()
        net.add_layer(DenseLayer(2, 3, "linear",
                                weights=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                                bias=[0.0, 0.0, 0.0]))
        cls = net.classify([1.0, 0.0])
        self.assertEqual(cls, 0)
        print(f"  [PASS] Classify: class {cls}")
    
    def test_model_size(self):
        """Should report size."""
        size = self.net.get_model_size()
        self.assertGreater(size["total_parameters"], 0)
        print(f"  [PASS] Size: {size['total_parameters']} params")
    
    def test_create_classifier(self):
        """Should create classifier."""
        net = NeuralNetwork.create_classifier(4, 2, [8])
        self.assertEqual(len(net.layers), 2)
        print(f"  [PASS] Classifier: {len(net.layers)} layers")


class TestInferenceEngine(unittest.TestCase):
    """Test inference engine."""
    
    def setUp(self):
        self.engine = InferenceEngine()
        self.net = NeuralNetwork()
        self.net.add_layer(DenseLayer(2, 1, "linear",
                                     weights=[1.0, 1.0],
                                     bias=[0.0]))
        self.engine.load_model("test", self.net)
    
    def test_infer(self):
        """Should run inference."""
        result = self.engine.infer("test", [1.0, 2.0])
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result[0], 3.0, delta=0.01)
        print(f"  [PASS] Infer: {result[0]:.2f}")
    
    def test_cache(self):
        """Should use cache."""
        r1 = self.engine.infer("test", [1.0, 1.0])
        r2 = self.engine.infer("test", [1.0, 1.0])
        self.assertEqual(r1, r2)
        print("  [PASS] Cache: hit")
    
    def test_batch(self):
        """Should batch infer."""
        results = self.engine.batch_infer("test", [[1.0, 0.0], [0.0, 1.0]])
        self.assertEqual(len(results), 2)
        print(f"  [PASS] Batch: {len(results)} results")
    
    def test_stats(self):
        """Should provide stats."""
        self.engine.infer("test", [1.0, 1.0])
        stats = self.engine.engine_stats()
        self.assertEqual(stats["loaded_models"], 1)
        print(f"  [PASS] Stats: {stats['inference_count']} inferences")


class TestTensor(unittest.TestCase):
    """Test tensor."""
    
    def test_create(self):
        """Should create tensor."""
        t = Tensor([1.0, 2.0, 3.0, 4.0], (2, 2))
        self.assertEqual(t.shape, (2, 2))
        print("  [PASS] Tensor: (2,2)")
    
    def test_reshape(self):
        """Should reshape."""
        t = Tensor([1.0, 2.0, 3.0, 4.0], (2, 2))
        r = t.reshape((4,))
        self.assertEqual(r.shape, (4,))
        print("  [PASS] Reshape: (4,)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
