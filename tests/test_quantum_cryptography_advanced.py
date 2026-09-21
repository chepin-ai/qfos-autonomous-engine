"""
Unit tests for quantum cryptography advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_cryptography_advanced import (QuantumKey, BB84Protocol,
                                           E91Protocol,
                                           QuantumRandomNumberGenerator,
                                           DeviceIndependentQKD,
                                           QuantumCryptographyAdvanced)


class TestBB84Protocol(unittest.TestCase):
    """Test BB84."""
    
    def setUp(self):
        self.bb84 = BB84Protocol()
    
    def test_bases(self):
        """Should generate bases."""
        b = self.bb84.generate_bases(10)
        self.assertEqual(len(b), 10)
        print(f"  [PASS] Bases: {len(b)}")
    
    def test_sift(self):
        """Should sift key."""
        ab = [0, 0, 1, 1]
        bb = [0, 1, 1, 0]
        bits = [1, 0, 1, 0]
        k = self.bb84.sift_key(ab, bb, bits)
        self.assertEqual(len(k), 2)
        print(f"  [PASS] Key: {k}")
    
    def test_qber(self):
        """Should compute QBER."""
        q = self.bb84.error_rate([1, 0, 1, 0], [1, 0, 0, 0])
        self.assertEqual(q, 0.25)
        print(f"  [PASS] QBER: {q:.2f}")


class TestE91Protocol(unittest.TestCase):
    """Test E91."""
    
    def setUp(self):
        self.e91 = E91Protocol()
    
    def test_bell(self):
        """Should measure Bell."""
        a, b = self.e91.bell_measurement(0, 0)
        self.assertEqual(a, b)
        print(f"  [PASS] Bell: ({a}, {b})")
    
    def test_chsh(self):
        """Should compute CHSH."""
        s = self.e91.chsh_parameter([0.7, -0.7, 0.7, 0.7])
        self.assertGreater(s, 0)
        print(f"  [PASS] S: {s:.2f}")


class TestQuantumRandomNumberGenerator(unittest.TestCase):
    """Test QRNG."""
    
    def setUp(self):
        self.qrng = QuantumRandomNumberGenerator()
    
    def test_bits(self):
        """Should generate bits."""
        b = self.qrng.generate_bits(8)
        self.assertEqual(len(b), 8)
        print(f"  [PASS] Bits: {b}")
    
    def test_entropy(self):
        """Should estimate entropy."""
        e = self.qrng.entropy_estimate([0, 1, 0, 1, 0, 1])
        self.assertGreater(e, 0)
        print(f"  [PASS] H: {e:.2f}")


class TestDeviceIndependentQKD(unittest.TestCase):
    """Test DI-QKD."""
    
    def setUp(self):
        self.diqkd = DeviceIndependentQKD()
    
    def test_rate(self):
        """Should compute key rate."""
        r = self.diqkd.secure_key_rate(0.05)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rate: {r:.4f}")


class TestQuantumCryptographyAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qca = QuantumCryptographyAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qca.crypto_summary()
        self.assertIn("protocols", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
