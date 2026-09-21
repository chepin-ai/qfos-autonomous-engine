"""
Unit tests for quantum tensor networks module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_tensor_networks import (Tensor, MatrixProductState,
                                     TensorContractor,
                                     EntanglementEntropy,
                                     MatrixProductOperator,
                                     QuantumTensorNetworks)


class TestMatrixProductState(unittest.TestCase):
    """Test MPS."""
    
    def setUp(self):
        self.mps = MatrixProductState(4, 2, 2)
    
    def test_bonds(self):
        """Should get bond dims."""
        b = self.mps.bond_dimensions()
        self.assertGreater(len(b), 0)
        print(f"  [PASS] Bonds: {b}")
    
    def test_norm(self):
        """Should compute norm."""
        n = self.mps.norm()
        self.assertGreater(n, 0)
        print(f"  [PASS] Norm: {n:.4f}")
    
    def test_normalize(self):
        """Should normalize."""
        self.mps.normalize()
        n = self.mps.norm()
        self.assertAlmostEqual(n, 1.0, places=5)
        print(f"  [PASS] Norm1: {n:.4f}")


class TestTensorContractor(unittest.TestCase):
    """Test contractor."""
    
    def setUp(self):
        self.tc = TensorContractor()
    
    def test_contract(self):
        """Should contract."""
        a = [1.0, 0.0, 0.0, 1.0]
        b = [1.0, 0.0, 0.0, 1.0]
        r, s = self.tc.contract_indices(a, b, (2, 2), (2, 2), 1, 0)
        self.assertEqual(len(r), 4)
        print(f"  [PASS] Contr: shape={s}")
    
    def test_trace(self):
        """Should compute trace."""
        m = [[1.0, 0.0], [0.0, 2.0]]
        t = self.tc.trace(m)
        self.assertEqual(t, 3.0)
        print(f"  [PASS] Tr: {t}")


class TestEntanglementEntropy(unittest.TestCase):
    """Test entropy."""
    
    def setUp(self):
        self.ee = EntanglementEntropy()
    
    def test_vn(self):
        """Should compute von Neumann."""
        s = [1.0 / math.sqrt(2), 1.0 / math.sqrt(2)]
        e = self.ee.von_neumann(s)
        self.assertGreater(e, 0)
        print(f"  [PASS] VN: {e:.4f}")
    
    def test_renyi(self):
        """Should compute Renyi."""
        s = [1.0, 0.0]
        e = self.ee.renyi(s, 2.0)
        self.assertEqual(e, 0.0)
        print(f"  [PASS] R2: {e}")


class TestMatrixProductOperator(unittest.TestCase):
    """Test MPO."""
    
    def setUp(self):
        self.mpo = MatrixProductOperator(4, 2, 2)
    
    def test_apply(self):
        """Should apply to MPS."""
        mps = MatrixProductState(4, 2, 2)
        r = self.mpo.apply_to_mps(mps)
        self.assertEqual(r.num_sites, 4)
        print("  [PASS] MPO")


class TestQuantumTensorNetworks(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qtn = QuantumTensorNetworks(4)
    
    def test_entropy(self):
        """Should compute entropy."""
        s = [1.0 / math.sqrt(2), 1.0 / math.sqrt(2)]
        e = self.qtn.compute_entropy(s)
        self.assertIn("von_neumann", e)
        print(f"  [PASS] Ent: {e}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qtn.qtn_summary()
        self.assertIn("num_sites", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
