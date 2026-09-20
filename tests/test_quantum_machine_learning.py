"""
Unit tests for quantum machine learning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_machine_learning import (QuantumFeature, QuantumKernel,
                                      QuantumSVM,
                                      QuantumPCA,
                                      QuantumClustering,
                                      QuantumMachineLearning)


class TestQuantumKernel(unittest.TestCase):
    """Test kernel."""
    
    def setUp(self):
        self.qk = QuantumKernel(4)
    
    def test_encode(self):
        """Should encode."""
        a = self.qk.encode_classical([1.0, 0.0, 0.0, 0.0])
        self.assertEqual(len(a), 4)
        print("  [PASS] Enc")
    
    def test_kernel(self):
        """Should compute kernel."""
        k = self.qk.kernel([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(k, 1.0, places=5)
        print(f"  [PASS] Kern: {k:.4f}")
    
    def test_matrix(self):
        """Should compute matrix."""
        data = [[1.0, 0.0], [0.0, 1.0]]
        m = self.qk.kernel_matrix(data)
        self.assertEqual(len(m), 2)
        print("  [PASS] Mat")


class TestQuantumSVM(unittest.TestCase):
    """Test SVM."""
    
    def setUp(self):
        self.svm = QuantumSVM(2)
    
    def test_train(self):
        """Should train."""
        X = [[1.0, 0.0], [0.0, 1.0]]
        y = [1, -1]
        self.svm.train(X, y, 5)
        self.assertGreater(len(self.svm.alphas), 0)
        print("  [PASS] Train")
    
    def test_predict(self):
        """Should predict."""
        X = [[1.0, 0.0], [0.0, 1.0]]
        y = [1, -1]
        self.svm.train(X, y, 5)
        p = self.svm.predict([1.0, 0.0])
        self.assertIn(p, [1, -1])
        print(f"  [PASS] Pred: {p}")


class TestQuantumPCA(unittest.TestCase):
    """Test PCA."""
    
    def setUp(self):
        self.pca = QuantumPCA(2)
    
    def test_covariance(self):
        """Should compute covariance."""
        data = [[1.0, 2.0], [2.0, 4.0]]
        c = self.pca.covariance_matrix(data)
        self.assertEqual(len(c), 2)
        print("  [PASS] Cov")
    
    def test_fit(self):
        """Should fit."""
        data = [[1.0, 0.0], [0.0, 1.0]]
        self.pca.fit(data)
        self.assertEqual(len(self.pca.components), 2)
        print("  [PASS] Fit")
    
    def test_transform(self):
        """Should transform."""
        data = [[1.0, 0.0], [0.0, 1.0]]
        self.pca.fit(data)
        t = self.pca.transform([1.0, 2.0])
        self.assertEqual(len(t), 2)
        print(f"  [PASS] Trans: {t}")


class TestQuantumClustering(unittest.TestCase):
    """Test clustering."""
    
    def setUp(self):
        self.qc = QuantumClustering(2)
    
    def test_distance(self):
        """Should compute distance."""
        d = self.qc.quantum_distance([0.0, 0.0], [3.0, 4.0])
        self.assertEqual(d, 5.0)
        print(f"  [PASS] Dist: {d}")
    
    def test_assign(self):
        """Should assign."""
        self.qc.centroids = [[0.0, 0.0], [10.0, 10.0]]
        a = self.qc.assign_clusters([[1.0, 1.0], [9.0, 9.0]])
        self.assertEqual(a, [0, 1])
        print(f"  [PASS] Asgn: {a}")
    
    def test_fit(self):
        """Should fit."""
        data = [[0.0, 0.0], [1.0, 1.0], [10.0, 10.0], [11.0, 11.0]]
        self.qc.fit(data, 5)
        self.assertEqual(len(self.qc.centroids), 2)
        print("  [PASS] FitClust")


class TestQuantumMachineLearning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qml = QuantumMachineLearning(2)
    
    def test_classify(self):
        """Should classify."""
        X = [[1.0, 0.0], [0.0, 1.0]]
        y = [1, -1]
        p = self.qml.classify(X, y, [[1.0, 0.0]])
        self.assertEqual(len(p), 1)
        print(f"  [PASS] Cls: {p}")
    
    def test_reduce(self):
        """Should reduce."""
        data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        r = self.qml.reduce_dimensions(data, 2)
        self.assertEqual(len(r), 2)
        print("  [PASS] Red")
    
    def test_cluster(self):
        """Should cluster."""
        data = [[0.0, 0.0], [1.0, 1.0], [10.0, 10.0]]
        a = self.qml.cluster(data, 2)
        self.assertEqual(len(a), 3)
        print(f"  [PASS] Clust: {a}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qml.qml_summary()
        self.assertIn("algorithms", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
