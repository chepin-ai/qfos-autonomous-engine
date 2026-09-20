"""
Unit tests for quantum tensor network module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_tensor_network import (Tensor, TensorContraction,
                                    MatrixProductState, PEPS,
                                    QuantumTensorNetwork)


class TestTensor(unittest.TestCase):
    """Test tensor."""
    
    def test_init(self):
        """Should init."""
        t = Tensor((2, 3))
        self.assertEqual(t.shape, (2, 3))
        self.assertEqual(t.size(), 6)
        print("  [PASS] Init")
    
    def test_get_set(self):
        """Should get/set."""
        t = Tensor((2, 2))
        t.set((0, 1), 5.0)
        self.assertEqual(t.get((0, 1)), 5.0)
        print("  [PASS] GetSet")


class TestTensorContraction(unittest.TestCase):
    """Test tensor contraction."""
    
    def setUp(self):
        self.tc = TensorContraction()
    
    def test_contract(self):
        """Should contract."""
        A = Tensor((2, 3))
        B = Tensor((3, 4))
        C = self.tc.contract(A, B, [1], [0])
        self.assertEqual(C.shape, (2, 4))
        print(f"  [PASS] Contract: {C.shape}")
    
    def test_trace(self):
        """Should trace."""
        A = Tensor((2, 2))
        A.set((0, 0), 1.0)
        A.set((1, 1), 2.0)
        C = self.tc.trace(A, 0, 1)
        self.assertEqual(C.size(), 1)
        print(f"  [PASS] Trace: {C.get((0,)):.1f}")


class TestMatrixProductState(unittest.TestCase):
    """Test MPS."""
    
    def setUp(self):
        self.mps = MatrixProductState(4, 2, 2)
    
    def test_shape(self):
        """Should have correct shapes."""
        self.assertEqual(len(self.mps.tensors), 4)
        self.assertEqual(self.mps.tensors[0].shape, (2, 2))
        self.assertEqual(self.mps.tensors[-1].shape, (2, 2))
        print("  [PASS] Shape")
    
    def test_norm(self):
        """Should compute norm."""
        n = self.mps.norm()
        self.assertGreater(n, 0)
        print(f"  [PASS] Norm: {n:.4f}")
    
    def test_expectation(self):
        """Should compute expectation."""
        op = [[1.0, 0.0], [0.0, -1.0]]
        e = self.mps.local_expectation(0, op)
        print(f"  [PASS] Exp: {e:.4f}")
    
    def test_canonicalize(self):
        """Should canonicalize."""
        self.mps.canonicalize_left(0)
        print("  [PASS] Canon")


class TestPEPS(unittest.TestCase):
    """Test PEPS."""
    
    def setUp(self):
        self.peps = PEPS(3, 3, 2, 2)
    
    def test_shape(self):
        """Should have correct grid."""
        self.assertEqual(len(self.peps.tensors), 3)
        self.assertEqual(len(self.peps.tensors[0]), 3)
        print("  [PASS] Grid")
    
    def test_expectation(self):
        """Should compute expectation."""
        op = [[1.0, 0.0], [0.0, -1.0]]
        e = self.peps.local_expectation(1, 1, op)
        print(f"  [PASS] Exp: {e:.4f}")


class TestQuantumTensorNetwork(unittest.TestCase):
    """Test unified tensor network."""
    
    def setUp(self):
        self.qtn = QuantumTensorNetwork()
    
    def test_build_mps(self):
        """Should build MPS."""
        self.qtn.build_mps(4, 2, 2)
        self.assertIsNotNone(self.qtn.mps)
        print("  [PASS] BuildMPS")
    
    def test_build_peps(self):
        """Should build PEPS."""
        self.qtn.build_peps(3, 3, 2, 2)
        self.assertIsNotNone(self.qtn.peps)
        print("  [PASS] BuildPEPS")
    
    def test_contract(self):
        """Should contract tensors."""
        A = Tensor((2, 3))
        B = Tensor((3, 2))
        C = self.qtn.tensor_contract(A, B, [1], [0])
        self.assertEqual(C.shape, (2, 2))
        print(f"  [PASS] Contract: {C.shape}")
    
    def test_summary(self):
        """Should summarize."""
        self.qtn.build_mps(4, 2, 2)
        s = self.qtn.network_summary()
        self.assertEqual(s["mps_sites"], 4)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
