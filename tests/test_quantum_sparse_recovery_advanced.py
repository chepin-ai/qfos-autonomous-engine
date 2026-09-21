"""
Unit tests for quantum sparse recovery advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_sparse_recovery_advanced import (SparseSignal, QuantumCompressedSensing,
                                              SparseVectorRecovery,
                                              QuantumInspiredMatchingPursuit,
                                              RIPVerification,
                                              QuantumSparseRecoveryAdvanced)


class TestQuantumCompressedSensing(unittest.TestCase):
    """Test CS."""
    
    def setUp(self):
        self.qcs = QuantumCompressedSensing()
    
    def test_bound(self):
        """Should compute measurement bound."""
        m = self.qcs.measurement_bound(5, 100)
        self.assertGreater(m, 0)
        print(f"  [PASS] M: {m}")
    
    def test_error(self):
        """Should compute error bound."""
        e = self.qcs.recovery_error_bound(0.1, 0.2)
        self.assertGreater(e, 0)
        print(f"  [PASS] E: {e:.4f}")


class TestSparseVectorRecovery(unittest.TestCase):
    """Test sparse."""
    
    def setUp(self):
        self.svr = SparseVectorRecovery()
    
    def test_threshold(self):
        """Should threshold."""
        t = self.svr.hard_thresholding([0.1, 0.9, 0.5], 1)
        self.assertEqual(sum(1 for v in t if v != 0), 1)
        print(f"  [PASS] HT: {t}")
    
    def test_support(self):
        """Should compute recovery rate."""
        r = self.svr.support_recovery_rate([0, 2], [0, 1])
        self.assertEqual(r, 0.5)
        print(f"  [PASS] SR: {r:.2f}")


class TestQuantumInspiredMatchingPursuit(unittest.TestCase):
    """Test MP."""
    
    def setUp(self):
        self.qimp = QuantumInspiredMatchingPursuit()
    
    def test_correlation(self):
        """Should compute correlation."""
        c = self.qimp.correlation([1.0, 2.0], [0.5, 1.0])
        self.assertEqual(c, 2.5)
        print(f"  [PASS] Corr: {c:.2f}")
    
    def test_residual(self):
        """Should update residual."""
        r = self.qimp.update_residual([1.0, 1.0], [0.5, 0.5], 2.0)
        self.assertEqual(r, [0.0, 0.0])
        print(f"  [PASS] Res: {r}")


class TestRIPVerification(unittest.TestCase):
    """Test RIP."""
    
    def setUp(self):
        self.rip = RIPVerification()
    
    def test_ratio(self):
        """Should compute ratio."""
        m = [[1.0, 0.0], [0.0, 1.0]]
        r = self.rip.sparse_norm_ratio(m, [1.0, 0.0])
        self.assertEqual(r, 1.0)
        print(f"  [PASS] R: {r:.2f}")
    
    def test_check(self):
        """Should check RIP."""
        m = [[1.0, 0.0], [0.0, 1.0]]
        b = self.rip.check_rip(m, 1, num_tests=10)
        self.assertTrue(b)
        print(f"  [PASS] RIP: {b}")


class TestQuantumSparseRecoveryAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qsra = QuantumSparseRecoveryAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qsra.recovery_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
