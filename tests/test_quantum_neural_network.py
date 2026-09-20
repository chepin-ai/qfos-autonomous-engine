"""
Unit tests for quantum neural network module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_neural_network import (QuantumLayer, QuantumNeuralNetwork,
                                     QuantumTrainer,
                                     QuantumNeuralNetworkController)


class TestQuantumLayer(unittest.TestCase):
    """Test quantum layer."""
    
    def setUp(self):
        self.layer = QuantumLayer(4)
    
    def test_apply(self):
        """Should apply layer."""
        state = [complex(1.0, 0.0)] + [complex(0.0, 0.0)] * 15
        out = self.layer.apply(state)
        self.assertEqual(len(out), 16)
        norm = sum(abs(z)**2 for z in out)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Apply: norm={norm:.4f}")


class TestQuantumNeuralNetwork(unittest.TestCase):
    """Test QNN."""
    
    def setUp(self):
        self.qnn = QuantumNeuralNetwork(4, 2)
    
    def test_encode(self):
        """Should encode."""
        state = self.qnn.encode([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(state), 16)
        norm = sum(abs(z)**2 for z in state)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Encode: norm={norm:.4f}")
    
    def test_forward(self):
        """Should forward."""
        state = self.qnn.forward([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(state), 16)
        print("  [PASS] Forward")
    
    def test_measure(self):
        """Should measure."""
        state = self.qnn.forward([0.5, 0.5, 0.5, 0.5])
        probs = self.qnn.measure(state)
        self.assertAlmostEqual(sum(probs), 1.0, places=5)
        print(f"  [PASS] Measure: sum={sum(probs):.4f}")
    
    def test_classify(self):
        """Should classify."""
        c = self.qnn.classify([0.5, 0.5, 0.5, 0.5], 2)
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Class: {c}")


class TestQuantumTrainer(unittest.TestCase):
    """Test trainer."""
    
    def setUp(self):
        self.qnn = QuantumNeuralNetwork(4, 2)
        self.trainer = QuantumTrainer(self.qnn)
    
    def test_loss(self):
        """Should compute loss."""
        loss = self.trainer.compute_loss([0.5, 0.5, 0.5, 0.5], 0)
        self.assertGreater(loss, 0)
        print(f"  [PASS] Loss: {loss:.4f}")
    
    def test_train_step(self):
        """Should train step."""
        self.trainer.train_step([0.5, 0.5, 0.5, 0.5], 0)
        self.assertEqual(len(self.trainer.loss_history), 1)
        print("  [PASS] Step")
    
    def test_train(self):
        """Should train."""
        data = [([0.5, 0.5, 0.5, 0.5], 0), ([0.1, 0.1, 0.1, 0.1], 1)]
        r = self.trainer.train(data, 5)
        self.assertIn("final_loss", r)
        print(f"  [PASS] Train: loss={r['final_loss']:.4f}")


class TestQuantumNeuralNetworkController(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ctrl = QuantumNeuralNetworkController()
    
    def test_build(self):
        """Should build."""
        self.ctrl.build(4, 2)
        self.assertIsNotNone(self.ctrl.qnn)
        print("  [PASS] Build")
    
    def test_train(self):
        """Should train."""
        data = [([0.5, 0.5, 0.5, 0.5], 0), ([0.1, 0.1, 0.1, 0.1], 1)]
        r = self.ctrl.train(data, 5)
        self.assertIn("final_loss", r)
        print(f"  [PASS] Train: loss={r['final_loss']:.4f}")
    
    def test_predict(self):
        """Should predict."""
        self.ctrl.build(4, 2)
        p = self.ctrl.predict([0.5, 0.5, 0.5, 0.5], 2)
        self.assertIn(p, [0, 1])
        print(f"  [PASS] Pred: {p}")
    
    def test_summary(self):
        """Should summarize."""
        self.ctrl.build(4, 2)
        s = self.ctrl.qnn_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
