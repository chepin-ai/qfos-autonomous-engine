"""
Unit tests for quantum kernel estimation advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_kernel_estimation_advanced import (KernelResult, QuantumFeatureMapKernel,
                                                KernelMatrixEstimation,
                                                QuantumSupportVectorKernel,
                                                KernelAlignment,
                                                QuantumKernelEstimationAdvanced)


class TestQuantumFeatureMapKernel(unittest.TestCase):
    """Test feature map."""
    
    def setUp(self):
        self.qfk = QuantumFeatureMapKernel()
    
    def test_zz(self):
        """Should compute ZZ kernel."""
        k = self.qfk.zz_feature_map_kernel([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(k, 1.0, delta=1e-10)
        print(f"  [PASS] Kzz: {k:.4f}")
    
    def test_pauli(self):
        """Should compute Pauli kernel."""
        k = self.qfk.pauli_feature_map_kernel([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(k, 1.0, delta=1e-10)
        print(f"  [PASS] Kp: {k:.4f}")


class TestKernelMatrixEstimation(unittest.TestCase):
    """Test matrix."""
    
    def setUp(self):
        self.kme = KernelMatrixEstimation()
    
    def test_matrix(self):
        """Should compute matrix."""
        def kf(a, b):
            return 1.0 if a == b else 0.0
        m = self.kme.kernel_matrix([[1.0], [2.0]], kf)
        self.assertEqual(m[0][0], 1.0)
        print(f"  [PASS] K: {len(m)}x{len(m)}")
    
    def test_condition(self):
        """Should compute condition."""
        c = self.kme.condition_number([[2.0, 0.0], [0.0, 1.0]])
        self.assertEqual(c, 2.0)
        print(f"  [PASS] Cond: {c:.1f}")


class TestQuantumSupportVectorKernel(unittest.TestCase):
    """Test SVM."""
    
    def setUp(self):
        self.qsvk = QuantumSupportVectorKernel()
    
    def test_decision(self):
        """Should compute decision."""
        d = self.qsvk.svm_decision([1.0, 1.0], [1, -1], [0.5, 0.5])
        self.assertEqual(d, 0.0)
        print(f"  [PASS] D: {d:.2f}")
    
    def test_classify(self):
        """Should classify."""
        c = self.qsvk.classify(0.5)
        self.assertEqual(c, 1)
        print(f"  [PASS] Cls: {c}")


class TestKernelAlignment(unittest.TestCase):
    """Test alignment."""
    
    def setUp(self):
        self.ka = KernelAlignment()
    
    def test_alignment(self):
        """Should compute alignment."""
        k = [[1.0, 0.5], [0.5, 1.0]]
        a = self.ka.alignment(k, k)
        self.assertAlmostEqual(a, 1.0, delta=1e-10)
        print(f"  [PASS] A: {a:.4f}")
    
    def test_center(self):
        """Should center."""
        c = self.ka.center_kernel([[1.0, 1.0], [1.0, 1.0]])
        self.assertAlmostEqual(c[0][0], 0.0, delta=1e-10)
        print(f"  [PASS] C: {c}")


class TestQuantumKernelEstimationAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qkea = QuantumKernelEstimationAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qkea.kernel_summary()
        self.assertIn("kernels", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
