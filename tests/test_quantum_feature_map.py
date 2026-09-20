"""
Unit tests for quantum feature map module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_feature_map import (PauliFeatureMap, ZZFeatureMap,
                                 QuantumKernelMatrix,
                                 QuantumFeatureEncoder,
                                 QuantumFeatureMap)


class TestPauliFeatureMap(unittest.TestCase):
    """Test Pauli feature map."""
    
    def setUp(self):
        self.fm = PauliFeatureMap(4, reps=2)
    
    def test_encode(self):
        """Should encode features."""
        phi = self.fm.encode([0.5, 0.0, -0.5, 1.0])
        self.assertGreater(len(phi), 0)
        print(f"  [PASS] Encode: len={len(phi)}")
    
    def test_kernel(self):
        """Should compute kernel."""
        k = self.fm.kernel([0.5, 0.0], [0.5, 0.0])
        self.assertAlmostEqual(k, 1.0, places=5)
        print(f"  [PASS] SelfK: {k}")
    
    def test_kernel_symmetry(self):
        """Should be symmetric."""
        k1 = self.fm.kernel([0.5, 0.0], [0.0, 0.5])
        k2 = self.fm.kernel([0.0, 0.5], [0.5, 0.0])
        self.assertAlmostEqual(k1, k2, places=5)
        print(f"  [PASS] Sym: {k1:.4f}")


class TestZZFeatureMap(unittest.TestCase):
    """Test ZZ feature map."""
    
    def setUp(self):
        self.fm = ZZFeatureMap(3, reps=1)
    
    def test_encode(self):
        """Should encode with ZZ."""
        phi = self.fm.encode([0.5, 0.0, -0.5])
        self.assertGreater(len(phi), 0)
        print(f"  [PASS] ZZ len={len(phi)}")
    
    def test_kernel(self):
        """Should compute ZZ kernel."""
        k = self.fm.kernel([0.5, 0.0], [0.5, 0.0])
        self.assertAlmostEqual(k, 1.0, places=5)
        print(f"  [PASS] ZZK: {k}")


class TestQuantumKernelMatrix(unittest.TestCase):
    """Test kernel matrix."""
    
    def setUp(self):
        self.km = QuantumKernelMatrix(PauliFeatureMap(2, reps=1))
    
    def test_compute(self):
        """Should compute matrix."""
        X = [[0.5, 0.0], [0.0, 0.5]]
        K = self.km.compute(X)
        self.assertEqual(len(K), 2)
        self.assertEqual(len(K[0]), 2)
        self.assertAlmostEqual(K[0][0], 1.0, places=5)
        print(f"  [PASS] K: {K}")
    
    def test_center(self):
        """Should center matrix."""
        K = [[1.0, 0.5], [0.5, 1.0]]
        C = self.km.center(K)
        self.assertEqual(len(C), 2)
        print(f"  [PASS] Center: {C}")


class TestQuantumFeatureEncoder(unittest.TestCase):
    """Test feature encoder."""
    
    def setUp(self):
        self.enc = QuantumFeatureEncoder("pauli", 4)
    
    def test_transform(self):
        """Should transform."""
        phi = self.enc.transform([0.5, 0.0, -0.5, 1.0])
        self.assertGreater(len(phi), 0)
        print("  [PASS] Transform")
    
    def test_similarity(self):
        """Should compute similarity."""
        s = self.enc.similarity([0.5, 0.0], [0.5, 0.0])
        self.assertAlmostEqual(s, 1.0, places=5)
        print(f"  [PASS] Sim: {s}")
    
    def test_kernel_matrix(self):
        """Should compute kernel matrix."""
        X = [[0.5, 0.0], [0.0, 0.5]]
        K = self.enc.kernel_matrix_for(X)
        self.assertEqual(len(K), 2)
        print(f"  [PASS] KMat: {K}")


class TestQuantumFeatureMap(unittest.TestCase):
    """Test unified feature map."""
    
    def setUp(self):
        self.qfm = QuantumFeatureMap()
    
    def test_build(self):
        """Should build."""
        self.qfm.build("zz", 3)
        self.assertIsNotNone(self.qfm.encoder)
        print("  [PASS] Build")
    
    def test_encode(self):
        """Should encode dataset."""
        self.qfm.build("pauli", 2)
        self.qfm.encode_dataset([[0.5, 0.0], [0.0, 0.5]])
        self.assertEqual(len(self.qfm.encoded_data), 2)
        print("  [PASS] Encode")
    
    def test_kernel(self):
        """Should compute kernel."""
        self.qfm.build("pauli", 2)
        K = self.qfm.compute_kernel([[0.5, 0.0], [0.0, 0.5]])
        self.assertEqual(len(K), 2)
        print(f"  [PASS] Kernel")
    
    def test_summary(self):
        """Should summarize."""
        self.qfm.build("pauli", 2)
        s = self.qfm.feature_map_summary()
        self.assertIn("feature_map", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
