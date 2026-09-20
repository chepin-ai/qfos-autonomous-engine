"""
Unit tests for quantum cryptography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_cryptography import (QuantumKey, QuantumRandomNumberGenerator,
                                  BB84Protocol,
                                  EavesdropperDetector,
                                  QuantumKeyDistiller,
                                  QuantumCryptography)


class TestQuantumRandomNumberGenerator(unittest.TestCase):
    """Test QRNG."""
    
    def setUp(self):
        self.qrng = QuantumRandomNumberGenerator()
    
    def test_bits(self):
        """Should generate bits."""
        b = self.qrng.generate_bits(10)
        self.assertEqual(len(b), 10)
        self.assertTrue(all(v in [0, 1] for v in b))
        print(f"  [PASS] Bits: {b}")
    
    def test_bases(self):
        """Should generate bases."""
        bases = self.qrng.generate_bases(10)
        self.assertEqual(len(bases), 10)
        self.assertTrue(all(v in ["Z", "X"] for v in bases))
        print(f"  [PASS] Bases: {bases}")


class TestBB84Protocol(unittest.TestCase):
    """Test BB84."""
    
    def setUp(self):
        self.bb84 = BB84Protocol()
    
    def test_prepare(self):
        """Should prepare."""
        self.bb84.alice_prepare(10)
        self.assertEqual(len(self.bb84.alice_bits), 10)
        print("  [PASS] Prep")
    
    def test_measure(self):
        """Should measure."""
        self.bb84.alice_prepare(10)
        self.bb84.bob_measure(10)
        self.assertEqual(len(self.bb84.bob_results), 10)
        print("  [PASS] Meas")
    
    def test_sift(self):
        """Should sift key."""
        self.bb84.alice_prepare(100)
        self.bb84.bob_measure(100)
        k = self.bb84.sift_key()
        self.assertGreater(len(k), 0)
        print(f"  [PASS] Sift: {len(k)}")
    
    def test_error(self):
        """Should compute error rate."""
        self.bb84.alice_prepare(100)
        self.bb84.bob_measure(100)
        self.bb84.sift_key()
        e = self.bb84.error_rate()
        self.assertGreaterEqual(e, 0.0)
        print(f"  [PASS] Err: {e:.4f}")


class TestEavesdropperDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.ed = EavesdropperDetector()
    
    def test_detect(self):
        """Should detect eavesdropper."""
        self.assertTrue(self.ed.detect(0.15))
        self.assertFalse(self.ed.detect(0.05))
        print("  [PASS] Det")
    
    def test_leakage(self):
        """Should estimate leakage."""
        l = self.ed.information_leakage(0.1)
        self.assertGreater(l, 0)
        print(f"  [PASS] Leak: {l:.4f}")


class TestQuantumKeyDistiller(unittest.TestCase):
    """Test distiller."""
    
    def setUp(self):
        self.qkd = QuantumKeyDistiller()
    
    def test_amplify(self):
        """Should amplify."""
        key = [1, 0, 1, 0, 1, 0, 1, 0]
        d = self.qkd.privacy_amplification(key, 4)
        self.assertEqual(len(d), 4)
        print(f"  [PASS] Amp: {d}")


class TestQuantumCryptography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumCryptography()
    
    def test_distribute(self):
        """Should distribute key."""
        r = self.qc.distribute_key(100)
        self.assertIn("raw_key_length", r)
        print(f"  [PASS] Dist: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qc.qcrypto_summary()
        self.assertIn("final_key_length", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
