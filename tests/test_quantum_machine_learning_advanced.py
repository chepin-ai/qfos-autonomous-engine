"""
Unit tests for quantum machine learning advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_machine_learning_advanced import (QuantumCircuitParams,
                                               VariationalQuantumCircuit,
                                               QuantumNeuralNetwork,
                                               QuantumAutoencoder,
                                               QuantumClassifier,
                                               QuantumMachineLearningAdvanced)


class TestVariationalQuantumCircuit(unittest.TestCase):
    """Test VQC."""
    
    def setUp(self):
        self.vqc = VariationalQuantumCircuit(3, 2)
    
    def test_init_params(self):
        """Should init params."""
        p = self.vqc.initialize_params()
        self.assertEqual(len(p.theta), 12)
        print(f"  [PASS] Params: {len(p.theta)}")
    
    def test_expectation(self):
        """Should compute expectation."""
        p = QuantumCircuitParams([0.5]*12, [0.5]*12)
        e = self.vqc.expectation_value(p)
        self.assertIsInstance(e, float)
        print(f"  [PASS] Exp: {e:.4f}")
    
    def test_cost(self):
        """Should compute cost."""
        p = QuantumCircuitParams([0.5]*12, [0.5]*12)
        c = self.vqc.cost_function(p, 0.5)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cost: {c:.4f}")


class TestQuantumNeuralNetwork(unittest.TestCase):
    """Test QNN."""
    
    def setUp(self):
        self.qnn = QuantumNeuralNetwork(2, 1)
    
    def test_feature_map(self):
        """Should map features."""
        f = self.qnn.quantum_feature_map([0.5, 0.5])
        self.assertEqual(len(f), 2)
        print(f"  [PASS] FM: {f}")
    
    def test_forward(self):
        """Should forward."""
        out = self.qnn.forward([0.5, 0.5], [[0.1, 0.2, 0.3, 0.4]])
        self.assertIsInstance(out, float)
        print(f"  [PASS] Out: {out:.4f}")


class TestQuantumAutoencoder(unittest.TestCase):
    """Test QAE."""
    
    def setUp(self):
        self.qae = QuantumAutoencoder(4, 2)
    
    def test_ratio(self):
        """Should compute ratio."""
        r = self.qae.compression_ratio()
        self.assertEqual(r, 0.5)
        print(f"  [PASS] Ratio: {r:.2f}")
    
    def test_encode(self):
        """Should encode."""
        e = self.qae.encode([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(len(e), 2)
        print(f"  [PASS] Enc: {e}")
    
    def test_decode(self):
        """Should decode."""
        d = self.qae.decode([1.5, 3.5])
        self.assertEqual(len(d), 4)
        print(f"  [PASS] Dec: {d}")
    
    def test_error(self):
        """Should compute error."""
        err = self.qae.reconstruction_error([1.0, 2.0, 3.0, 4.0], [1.1, 1.9, 3.1, 3.9])
        self.assertGreater(err, 0)
        print(f"  [PASS] Err: {err:.4f}")


class TestQuantumClassifier(unittest.TestCase):
    """Test classifier."""
    
    def setUp(self):
        self.qcl = QuantumClassifier()
    
    def test_classify(self):
        """Should classify."""
        c = self.qcl.classify([1.0, -1.0], [0.5, 0.5])
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Cls: {c}")
    
    def test_accuracy(self):
        """Should compute accuracy."""
        X = [[1.0, 0.0], [0.0, 1.0]]
        y = [1, 0]
        a = self.qcl.accuracy(X, y, [1.0, -1.0])
        self.assertGreater(a, 0)
        print(f"  [PASS] Acc: {a:.2f}")


class TestQuantumMachineLearningAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qml = QuantumMachineLearningAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qml.qml_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
