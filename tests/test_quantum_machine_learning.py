"""
Unit tests for quantum machine learning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_machine_learning import (QuantumFeature, QuantumFeatureMap,
                                      QuantumKernel,
                                      QSVM,
                                      QuantumNeuralNetwork,
                                      QuantumClassifier,
                                      QuantumMachineLearning)


class TestQuantumFeatureMap(unittest.TestCase):
    """Test feature map."""
    
    def setUp(self):
        self.fm = QuantumFeatureMap(2, 2)
    
    def test_encode(self):
        """Should encode."""
        s = self.fm.encode([0.5, 0.5])
        self.assertEqual(len(s), 4)
        print(f"  [PASS] Enc: {len(s)} amps")
    
    def test_num_features(self):
        """Should count features."""
        n = self.fm.num_features()
        self.assertEqual(n, 2)
        print(f"  [PASS] Nf: {n}")


class TestQuantumKernel(unittest.TestCase):
    """Test kernel."""
    
    def setUp(self):
        self.fm = QuantumFeatureMap(2)
        self.k = QuantumKernel(self.fm)
    
    def test_compute(self):
        """Should compute kernel."""
        v = self.k.compute([0.0, 0.0], [0.0, 0.0])
        self.assertAlmostEqual(v, 1.0, delta=0.1)
        print(f"  [PASS] K: {v:.4f}")
    
    def test_matrix(self):
        """Should compute matrix."""
        m = self.k.kernel_matrix([[0.0, 0.0], [0.5, 0.5]])
        self.assertEqual(len(m), 2)
        self.assertEqual(len(m[0]), 2)
        print(f"  [PASS] Mat: {len(m)}x{len(m[0])}")


class TestQSVM(unittest.TestCase):
    """Test QSVM."""
    
    def setUp(self):
        self.fm = QuantumFeatureMap(2)
        self.k = QuantumKernel(self.fm)
        self.svm = QSVM(self.k)
    
    def test_train_predict(self):
        """Should train and predict."""
        self.svm.train([[0.0, 0.0], [0.5, 0.5]], [1, -1])
        p = self.svm.predict([0.1, 0.1])
        self.assertIn(p, [1, -1])
        print(f"  [PASS] SVM: {p}")


class TestQuantumNeuralNetwork(unittest.TestCase):
    """Test QNN."""
    
    def setUp(self):
        self.qnn = QuantumNeuralNetwork(2, 2)
    
    def test_forward(self):
        """Should forward."""
        self.qnn.set_parameters([0.1, 0.2, 0.3, 0.4])
        o = self.qnn.forward([1.0, 0.5])
        self.assertIsNotNone(o)
        print(f"  [PASS] Out: {o:.4f}")
    
    def test_num_params(self):
        """Should count params."""
        n = self.qnn.num_parameters()
        self.assertEqual(n, 4)
        print(f"  [PASS] Np: {n}")


class TestQuantumMachineLearning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qml = QuantumMachineLearning(2)
    
    def test_summary(self):
        """Should summarize."""
        s = self.qml.qml_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
