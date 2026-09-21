"""
Unit tests for quantum ML kernels module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_ml_kernels import (KernelMatrix, QuantumFeatureMap,
                                QuantumKernel,
                                QuantumKernelSVM,
                                QuantumKernelPCA,
                                QuantumMLKernels)


class TestQuantumFeatureMap(unittest.TestCase):
    """Test feature map."""
    
    def setUp(self):
        self.fm = QuantumFeatureMap(2, 2)
    
    def test_encode(self):
        """Should encode."""
        phi = self.fm.encode([0.5, 0.3])
        self.assertEqual(len(phi), 4)
        norm = sum(abs(a) ** 2 for a in phi)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print("  [PASS] Enc")
    
    def test_dimension(self):
        """Should have dimension."""
        d = self.fm.feature_dimension()
        self.assertEqual(d, 4)
        print(f"  [PASS] Dim: {d}")


class TestQuantumKernel(unittest.TestCase):
    """Test kernel."""
    
    def setUp(self):
        self.k = QuantumKernel(QuantumFeatureMap(2))
    
    def test_kernel(self):
        """Should compute kernel."""
        k = self.k.kernel([0.5, 0.3], [0.5, 0.3])
        self.assertAlmostEqual(k, 1.0, delta=0.01)
        print(f"  [PASS] K: {k:.3f}")
    
    def test_kernel_matrix(self):
        """Should compute matrix."""
        X = [[0.1, 0.2], [0.3, 0.4]]
        K = self.k.kernel_matrix(X)
        self.assertEqual(K.size, 2)
        self.assertAlmostEqual(K.matrix[0][0], 1.0, delta=0.1)
        print("  [PASS] Kmat")


class TestQuantumKernelSVM(unittest.TestCase):
    """Test SVM."""
    
    def setUp(self):
        self.svm = QuantumKernelSVM(QuantumKernel(QuantumFeatureMap(2)))
    
    def test_train_predict(self):
        """Should train and predict."""
        X = [[0.1, 0.1], [0.9, 0.9], [0.2, 0.1], [0.8, 0.8]]
        y = [1, -1, 1, -1]
        self.svm.train(X, y)
        pred = self.svm.predict([0.15, 0.15])
        print(f"  [PASS] Pred: {pred}")


class TestQuantumKernelPCA(unittest.TestCase):
    """Test PCA."""
    
    def setUp(self):
        self.pca = QuantumKernelPCA(QuantumKernel(QuantumFeatureMap(2)), 2)
    
    def test_transform(self):
        """Should transform."""
        X = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        T = self.pca.fit_transform(X)
        self.assertEqual(len(T), 3)
        print(f"  [PASS] PCA: {len(T)} samples")


class TestQuantumMLKernels(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qml = QuantumMLKernels(2)
    
    def test_summary(self):
        """Should summarize."""
        s = self.qml.qml_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
