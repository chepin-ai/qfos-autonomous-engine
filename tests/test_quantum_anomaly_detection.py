"""
Unit tests for quantum anomaly detection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_anomaly_detection import (QuantumStateEncoder, QuantumFidelity,
                                        QuantumPCA, VariationalAnomalyClassifier,
                                        QuantumAnomalyDetection)


class TestQuantumStateEncoder(unittest.TestCase):
    """Test encoder."""
    
    def setUp(self):
        self.enc = QuantumStateEncoder(3)
    
    def test_encode(self):
        """Should encode."""
        state = self.enc.encode([0.5, 0.5, 0.5, 0.0])
        self.assertEqual(len(state), 8)
        norm = sum(abs(z)**2 for z in state) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Enc: norm={norm:.4f}")


class TestQuantumFidelity(unittest.TestCase):
    """Test fidelity."""
    
    def setUp(self):
        self.fid = QuantumFidelity()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        s1 = [complex(1, 0), complex(0, 0)]
        s2 = [complex(1, 0), complex(0, 0)]
        f = self.fid.fidelity(s1, s2)
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_avg(self):
        """Should compute average."""
        s = [complex(1, 0), complex(0, 0)]
        refs = [[complex(1, 0), complex(0, 0)],
                [complex(0, 0), complex(1, 0)]]
        a = self.fid.average_fidelity(s, refs)
        self.assertAlmostEqual(a, 0.5, places=5)
        print(f"  [PASS] Avg: {a:.4f}")


class TestQuantumPCA(unittest.TestCase):
    """Test QPCA."""
    
    def setUp(self):
        self.qpca = QuantumPCA(2)
    
    def test_covariance(self):
        """Should compute covariance."""
        data = [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]]
        cov = self.qpca.covariance(data)
        self.assertEqual(len(cov), 2)
        print(f"  [PASS] Cov: {cov}")
    
    def test_transform(self):
        """Should transform."""
        data = [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]]
        t = self.qpca.transform(data)
        self.assertEqual(len(t[0]), 2)
        print(f"  [PASS] Trans: {t}")


class TestVariationalAnomalyClassifier(unittest.TestCase):
    """Test classifier."""
    
    def setUp(self):
        self.vac = VariationalAnomalyClassifier(0.3)
    
    def test_train(self):
        """Should train."""
        self.vac.train([[1.0, 0.0], [0.9, 0.1], [1.1, 0.0]])
        self.assertGreater(len(self.vac.normal_states), 0)
        print("  [PASS] Train")
    
    def test_predict(self):
        """Should predict."""
        self.vac.train([[1.0, 0.0], [0.9, 0.1]])
        pred, score = self.vac.predict([5.0, 5.0])
        self.assertIn(pred, [0, 1])
        print(f"  [PASS] Pred: {pred}, score={score:.4f}")


class TestQuantumAnomalyDetection(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qad = QuantumAnomalyDetection()
    
    def test_fit(self):
        """Should fit."""
        self.qad.fit([[1.0, 0.0], [0.9, 0.1], [1.1, 0.0]])
        self.assertGreater(len(self.qad.classifier.normal_states), 0)
        print("  [PASS] Fit")
    
    def test_detect(self):
        """Should detect."""
        self.qad.fit([[1.0, 0.0], [0.9, 0.1]])
        preds = self.qad.detect([[1.0, 0.0], [5.0, 5.0]])
        self.assertEqual(len(preds), 2)
        print(f"  [PASS] Det: {preds}")
    
    def test_summary(self):
        """Should summarize."""
        self.qad.fit([[1.0, 0.0]])
        self.qad.detect([[5.0, 5.0]])
        s = self.qad.qad_summary()
        self.assertIn("anomalies", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
