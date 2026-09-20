"""
Unit tests for quantum kernel methods module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_kernel_methods import (QuantumFeatureMap, QuantumKernel,
                                     KernelAlignment, QuantumKernelSVM,
                                     QuantumKernelMethods)


class TestQuantumFeatureMap(unittest.TestCase):
    """Test feature map."""
    
    def setUp(self):
        self.fm = QuantumFeatureMap(4, 2)
    
    def test_encode(self):
        """Should encode."""
        state = self.fm.encode([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(state), 16)
        norm = sum(abs(z)**2 for z in state)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Encode: norm={norm:.4f}")
    
    def test_feature_vector(self):
        """Should get feature vector."""
        fv = self.fm.feature_vector([0.5]*4)
        self.assertEqual(len(fv), 32)
        print(f"  [PASS] FV: len={len(fv)}")


class TestQuantumKernel(unittest.TestCase):
    """Test kernel."""
    
    def setUp(self):
        self.k = QuantumKernel()
    
    def test_kernel(self):
        """Should compute kernel."""
        x1, x2 = [0.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]
        k = self.k.kernel(x1, x2)
        self.assertGreaterEqual(k, 0)
        self.assertLessEqual(k, 1.0)
        print(f"  [PASS] Kernel: {k:.4f}")
    
    def test_kernel_matrix(self):
        """Should compute kernel matrix."""
        data = [[0.0]*4, [1.0]*4]
        K = self.k.kernel_matrix(data)
        self.assertEqual(len(K), 2)
        self.assertAlmostEqual(K[0][0], 1.0, places=3)
        print(f"  [PASS] Kmat: {K}")


class TestKernelAlignment(unittest.TestCase):
    """Test alignment."""
    
    def setUp(self):
        self.ka = KernelAlignment()
    
    def test_frobenius(self):
        """Should compute Frobenius."""
        K = [[1.0, 0.5], [0.5, 1.0]]
        f = self.ka.frobenius_inner(K, K)
        self.assertEqual(f, 2.5)
        print(f"  [PASS] Frob: {f}")
    
    def test_alignment(self):
        """Should compute alignment."""
        K = [[1.0, 1.0], [1.0, 1.0]]
        a = self.ka.alignment(K, [1, -1])
        self.assertIsInstance(a, float)
        print(f"  [PASS] Align: {a:.4f}")


class TestQuantumKernelSVM(unittest.TestCase):
    """Test QK SVM."""
    
    def setUp(self):
        self.svm = QuantumKernelSVM(QuantumKernel())
    
    def test_fit(self):
        """Should fit."""
        X = [[0.0]*4, [1.0]*4]
        y = [-1, 1]
        self.svm.fit(X, y)
        self.assertEqual(len(self.svm.alpha), 2)
        print("  [PASS] Fit")
    
    def test_predict(self):
        """Should predict."""
        X = [[0.0]*4, [1.0]*4]
        y = [-1, 1]
        self.svm.fit(X, y)
        p = self.svm.predict([0.0]*4)
        self.assertIn(p, [-1, 1])
        print(f"  [PASS] Pred: {p}")
    
    def test_score(self):
        """Should score."""
        X = [[0.0]*4, [1.0]*4]
        y = [-1, 1]
        self.svm.fit(X, y)
        s = self.svm.score(X, y)
        self.assertGreaterEqual(s, 0)
        print(f"  [PASS] Score: {s}")


class TestQuantumKernelMethods(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qkm = QuantumKernelMethods()
    
    def test_matrix(self):
        """Should compute matrix."""
        data = [[0.0]*4, [0.5]*4]
        K = self.qkm.compute_kernel_matrix(data)
        self.assertEqual(len(K), 2)
        print("  [PASS] Matrix")
    
    def test_fit(self):
        """Should fit SVM."""
        X = [[0.0]*4, [1.0]*4, [0.1]*4]
        y = [-1, 1, -1]
        r = self.qkm.fit_svm(X, y)
        self.assertIn("accuracy", r)
        print(f"  [PASS] Fit: {r}")
    
    def test_align(self):
        """Should compute alignment."""
        data = [[0.0]*4, [1.0]*4]
        labels = [-1, 1]
        a = self.qkm.evaluate_alignment(data, labels)
        self.assertIsInstance(a, float)
        print(f"  [PASS] Align: {a:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qkm.qkm_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
