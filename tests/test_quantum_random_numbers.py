"""
Unit tests for quantum random number generation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_random_numbers import (RandomBitstring, HadamardQRNG,
                                    EntropyExtractor,
                                    RandomnessTester,
                                    QuantumRandomNumbers)


class TestHadamardQRNG(unittest.TestCase):
    """Test QRNG."""
    
    def setUp(self):
        self.qrng = HadamardQRNG(4)
    
    def test_generate_bits(self):
        """Should generate bits."""
        b = self.qrng.generate_bits(16)
        self.assertEqual(len(b), 16)
        self.assertTrue(all(c in "01" for c in b))
        print(f"  [PASS] Bits: {b[:8]}...")
    
    def test_generate_integers(self):
        """Should generate integers."""
        ints = self.qrng.generate_integers(5, 100)
        self.assertEqual(len(ints), 5)
        self.assertTrue(all(0 <= i < 100 for i in ints))
        print(f"  [PASS] Ints: {ints}")


class TestEntropyExtractor(unittest.TestCase):
    """Test extractor."""
    
    def setUp(self):
        self.ee = EntropyExtractor()
    
    def test_von_neumann(self):
        """Should extract."""
        raw = "01101001"
        e = self.ee.von_neumann_extractor(raw)
        self.assertTrue(all(c in "01" for c in e))
        print(f"  [PASS] VN: {e}")
    
    def test_parity(self):
        """Should extract parity."""
        raw = "1111"
        e = self.ee.parity_extractor(raw, 4)
        self.assertEqual(len(e), 1)
        print(f"  [PASS] Par: {e}")
    
    def test_entropy(self):
        """Should estimate entropy."""
        e = self.ee.estimate_entropy("01" * 50)
        self.assertGreater(e, 0.9)
        print(f"  [PASS] Ent: {e:.4f}")


class TestRandomnessTester(unittest.TestCase):
    """Test tester."""
    
    def setUp(self):
        self.rt = RandomnessTester()
    
    def test_frequency(self):
        """Should compute frequency test."""
        p = self.rt.frequency_test("01" * 50)
        self.assertGreater(p, 0.0)
        print(f"  [PASS] Freq: {p:.4f}")
    
    def test_runs(self):
        """Should compute runs."""
        r, e = self.rt.runs_test("010101")
        self.assertEqual(r, 6)
        print(f"  [PASS] Runs: {r}, exp: {e:.1f}")
    
    def test_longest_run(self):
        """Should find longest run."""
        lr = self.rt.longest_run_test("0011100")
        self.assertEqual(lr, 3)
        print(f"  [PASS] LR: {lr}")


class TestQuantumRandomNumbers(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qrn = QuantumRandomNumbers(4)
    
    def test_generate(self):
        """Should generate."""
        r = self.qrn.generate(16)
        self.assertEqual(len(r.bits), 16)
        print(f"  [PASS] Gen: {len(r.bits)} bits")
    
    def test_test_randomness(self):
        """Should test."""
        r = self.qrn.test_randomness("01" * 50)
        self.assertIn("frequency_pvalue", r)
        print(f"  [PASS] Tst: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qrn.qrn_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
