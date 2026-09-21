"""
Unit tests for quantum error correction codes module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_correction_codes import (Syndrome, SteaneCode,
                                            ShorCode,
                                            SurfaceCode,
                                            QuantumErrorCorrectionCodes)


class TestSteaneCode(unittest.TestCase):
    """Test Steane."""
    
    def setUp(self):
        self.sc = SteaneCode()
    
    def test_encode_zero(self):
        """Should encode |0>."""
        s = self.sc.encode_logical_zero()
        self.assertEqual(len(s), 7)
        self.assertEqual(sum(s), 0)
        print("  [PASS] |0>")
    
    def test_encode_one(self):
        """Should encode |1>."""
        s = self.sc.encode_logical_one()
        self.assertEqual(len(s), 7)
        self.assertEqual(sum(s), 7)
        print("  [PASS] |1>")
    
    def test_syndrome_zero(self):
        """Should measure zero syndrome."""
        s = self.sc.encode_logical_zero()
        sx = self.sc.measure_x_syndrome(s)
        self.assertEqual(sum(sx), 0)
        print(f"  [PASS] SX: {sx}")
    
    def test_correct(self):
        """Should correct error."""
        s = self.sc.encode_logical_zero()
        s[3] ^= 1  # Introduce error
        sx = self.sc.measure_x_syndrome(s)
        c = self.sc.correct_x_error(s, sx)
        self.assertEqual(sum(c), 0)
        print("  [PASS] Corr")


class TestShorCode(unittest.TestCase):
    """Test Shor."""
    
    def setUp(self):
        self.sh = ShorCode()
    
    def test_encode_zero(self):
        """Should encode |0>."""
        s = self.sh.encode_logical_zero()
        self.assertEqual(len(s), 9)
        print("  [PASS] |0>")
    
    def test_encode_one(self):
        """Should encode |1>."""
        s = self.sh.encode_logical_one()
        self.assertEqual(len(s), 9)
        print("  [PASS] |1>")
    
    def test_syndrome(self):
        """Should measure syndrome."""
        s = self.sh.encode_logical_zero()
        sp = self.sh.measure_phase_syndrome(s)
        self.assertEqual(sum(sp), 0)
        print(f"  [PASS] SP: {sp}")


class TestSurfaceCode(unittest.TestCase):
    """Test surface."""
    
    def setUp(self):
        self.su = SurfaceCode(3)
    
    def test_size(self):
        """Should have size."""
        self.assertEqual(self.su.lattice_size(), 3)
        print("  [PASS] Sz")
    
    def test_stabilizers(self):
        """Should have stabilizers."""
        n = self.su.num_stabilizers()
        self.assertGreater(n, 0)
        print(f"  [PASS] Stab: {n}")
    
    def test_logical_error(self):
        """Should estimate error rate."""
        le = self.su.logical_error_rate(0.01)
        self.assertLess(le, 0.01)
        print(f"  [PASS] LE: {le:.2e}")


class TestQuantumErrorCorrectionCodes(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qecc = QuantumErrorCorrectionCodes()
    
    def test_protect(self):
        """Should protect."""
        p = self.qecc.protect_state([0], "steane")
        self.assertEqual(p["code"], "steane")
        print(f"  [PASS] Prot: {p['n']}, {p['k']}, {p['d']}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qecc.qecc_summary()
        self.assertIn("codes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
