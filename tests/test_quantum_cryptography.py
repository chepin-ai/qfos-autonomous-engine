"""
Unit tests for quantum cryptography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_cryptography import (QKDKey, BB84Protocol,
                                  E91Protocol,
                                  PrivacyAmplification,
                                  SecurityAnalyzer,
                                  QuantumCryptography)


class TestBB84Protocol(unittest.TestCase):
    """Test BB84."""
    
    def setUp(self):
        self.bb84 = BB84Protocol()
    
    def test_generate(self):
        """Should generate raw key."""
        bits, bases = self.bb84.generate_raw_key(10)
        self.assertEqual(len(bits), 10)
        self.assertEqual(len(bases), 10)
        print("  [PASS] Gen")
    
    def test_encode(self):
        """Should encode."""
        states = self.bb84.encode([0, 1], ["Z", "X"])
        self.assertEqual(states[0], "|0>")
        self.assertIn(states[1], ["|->", "|+>"])
        print(f"  [PASS] Enc: {states}")
    
    def test_sift(self):
        """Should sift."""
        a_bits = [0, 1, 0, 1]
        a_bases = ["Z", "Z", "X", "X"]
        b_bits = [0, 0, 0, 1]
        b_bases = ["Z", "Z", "X", "X"]
        key, err = self.bb84.sift_key(a_bases, b_bases, a_bits, b_bits)
        self.assertGreater(len(key), 0)
        print(f"  [PASS] Sift: {key}, err={err:.2f}")


class TestE91Protocol(unittest.TestCase):
    """Test E91."""
    
    def setUp(self):
        self.e91 = E91Protocol()
    
    def test_entangled_pair(self):
        """Should generate pair."""
        a, b = self.e91.generate_entangled_pair()
        self.assertEqual(a, b)
        print(f"  [PASS] Ent: {a}, {b}")
    
    def test_chsh(self):
        """Should compute CHSH."""
        a_res = [0, 0, 1, 1]
        b_res = [0, 1, 0, 1]
        a_base = [0, 0, 1, 1]
        b_base = [0, 1, 0, 1]
        s = self.e91.CHSH_test(a_res, b_res, a_base, b_base)
        self.assertGreaterEqual(s, 0.0)
        print(f"  [PASS] CHSH: {s:.2f}")


class TestPrivacyAmplification(unittest.TestCase):
    """Test amplification."""
    
    def setUp(self):
        self.pa = PrivacyAmplification()
    
    def test_xor(self):
        """Should amplify."""
        k = self.pa.xor_amplification("1111", 2)
        self.assertEqual(len(k), 2)
        print(f"  [PASS] XOR: {k}")
    
    def test_hash(self):
        """Should hash."""
        h = self.pa.universal_hash("1010", 42)
        self.assertEqual(len(h), 4)
        print(f"  [PASS] Hash: {h}")


class TestSecurityAnalyzer(unittest.TestCase):
    """Test security."""
    
    def setUp(self):
        self.sa = SecurityAnalyzer()
    
    def test_leakage(self):
        """Should estimate leakage."""
        l = self.sa.information_leakage(0.05)
        self.assertGreater(l, 0)
        print(f"  [PASS] Leak: {l:.2f}")
    
    def test_key_rate(self):
        """Should compute key rate."""
        r = self.sa.secure_key_rate(1000.0, 0.05)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rate: {r:.0f}")


class TestQuantumCryptography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumCryptography()
    
    def test_generate_key(self):
        """Should generate key."""
        k = self.qc.generate_key(20)
        self.assertIsInstance(k.key, str)
        print(f"  [PASS] Key: {len(k.key)} bits")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qc.qc_summary()
        self.assertIn("protocols", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
