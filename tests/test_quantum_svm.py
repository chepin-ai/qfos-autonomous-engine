"""
Unit tests for quantum SVM module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_svm import (QuantumKernelSVM, VariationalQuantumClassifier,
                         QuantumSVM)


class TestQuantumKernelSVM(unittest.TestCase):
    """Test quantum kernel SVM."""
    
    def setUp(self):
        self.svm = QuantumKernelSVM(C=1.0)
        def kernel(x, y):
            inner = sum(x[i] * y[i] for i in range(min(len(x), len(y))))
            nx = sum(xi ** 2 for xi in x) ** 0.5
            ny = sum(yi ** 2 for yi in y) ** 0.5
            if nx <= 0 or ny <= 0:
                return 0.0
            return (inner / (nx * ny)) ** 2
        self.svm.set_kernel(kernel)
    
    def test_train(self):
        """Should train."""
        X = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
        y = [1, 1, -1, -1]
        self.svm.train(X, y)
        self.assertGreater(len(self.svm.support_vectors), 0)
        print(f"  [PASS] SVs: {len(self.svm.support_vectors)}")
    
    def test_predict(self):
        """Should predict."""
        X = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
        y = [1, 1, -1, -1]
        self.svm.train(X, y)
        pred = self.svm.predict([1.0, 0.0])
        self.assertIn(pred, [-1, 1])
        print(f"  [PASS] Pred: {pred}")
    
    def test_batch(self):
        """Should predict batch."""
        X = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
        y = [1, 1, -1, -1]
        self.svm.train(X, y)
        preds = self.svm.predict_batch([[1.0, 0.0], [-1.0, 0.0]])
        self.assertEqual(len(preds), 2)
        print(f"  [PASS] Batch: {preds}")


class TestVariationalQuantumClassifier(unittest.TestCase):
    """Test VQC."""
    
    def setUp(self):
        self.vqc = VariationalQuantumClassifier(2)
    
    def test_circuit(self):
        """Should compute circuit."""
        out = self.vqc.circuit([0.5, 0.5])
        self.assertIsInstance(out, float)
        print(f"  [PASS] Circ: {out:.4f}")
    
    def test_predict(self):
        """Should predict."""
        pred = self.vqc.predict([0.5, 0.5])
        self.assertIn(pred, [0, 1])
        print(f"  [PASS] Pred: {pred}")
    
    def test_loss(self):
        """Should compute loss."""
        l = self.vqc.loss([0.5, 0.5], 1)
        self.assertGreater(l, 0)
        print(f"  [PASS] Loss: {l:.4f}")
    
    def test_train(self):
        """Should train."""
        X = [[0.5, 0.5], [0.6, 0.4], [0.4, 0.6], [-0.5, -0.5]]
        y = [1, 1, 1, 0]
        self.vqc.train(X, y, epochs=5)
        self.assertEqual(len(self.vqc.history), 5)
        print(f"  [PASS] Train: loss={self.vqc.history[-1]:.4f}")


class TestQuantumSVM(unittest.TestCase):
    """Test unified quantum SVM."""
    
    def setUp(self):
        self.qsvm = QuantumSVM()
    
    def test_build_svm(self):
        """Should build SVM."""
        self.qsvm.build_kernel_svm()
        self.assertIsNotNone(self.qsvm.svm)
        print("  [PASS] BuildSVM")
    
    def test_build_vqc(self):
        """Should build VQC."""
        self.qsvm.build_vqc(2)
        self.assertIsNotNone(self.qsvm.vqc)
        print("  [PASS] BuildVQC")
    
    def test_train_predict_svm(self):
        """Should train and predict SVM."""
        self.qsvm.build_kernel_svm()
        X = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
        y = [1, 1, -1, -1]
        self.qsvm.train_svm(X, y)
        pred = self.qsvm.predict([1.0, 0.0], "svm")
        self.assertIn(pred, [-1, 1])
        print(f"  [PASS] SVM: {pred}")
    
    def test_train_predict_vqc(self):
        """Should train and predict VQC."""
        self.qsvm.build_vqc(2)
        X = [[0.5, 0.5], [0.6, 0.4], [-0.5, -0.5], [-0.6, -0.4]]
        y = [1, 1, 0, 0]
        self.qsvm.train_vqc(X, y, epochs=5)
        pred = self.qsvm.predict([0.5, 0.5], "vqc")
        self.assertIn(pred, [0, 1])
        print(f"  [PASS] VQC: {pred}")
    
    def test_summary(self):
        """Should summarize."""
        self.qsvm.build_kernel_svm()
        X = [[1.0, 0.0], [-1.0, 0.0]]
        y = [1, -1]
        self.qsvm.train_svm(X, y)
        s = self.qsvm.svm_summary()
        self.assertIn("support_vectors", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
