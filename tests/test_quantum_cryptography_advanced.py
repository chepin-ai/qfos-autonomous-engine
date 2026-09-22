"""
Unit tests for quantum cryptography advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_cryptography_advanced import (QuantumKey, BB84Protocol,
                                           E91Protocol,
                                           QuantumKeyDistillation,
                                           QuantumRandomNumberGeneration,
                                           QuantumCryptographyAdvanced)


class TestBB84Protocol(unittest.TestCase):
    """Test BB84."""
    
    def setUp(self):
        self.bb84 = BB84Protocol()
    
    def test_prepare(self):
        """Should prepare state."""
        s = self.bb84.prepare_state(0, "Z")
        self.assertEqual(s, "|0>_Z")
        print(f"  [PASS] Prep: {s}")
    
    def test_measure(self):
        """Should measure."""
        m = self.bb84.measure_state("Z", "Z", 0)
        self.assertEqual(m, 0)
        print(f"  [PASS] Meas: {m}")
    
    def test_sift(self):
        """Should sift key."""
        bits = [0, 1, 0, 1]
        a_bases = ["Z", "Z", "X", "X"]
        b_bases = ["Z", "X", "X", "Z"]
        key = self.bb84.sift_key(bits, a_bases, b_bases, bits)
        self.assertEqual(key, [0, 0])
        print(f"  [PASS] Key: {key}")
    
    def test_qber(self):
        """Should compute QBER."""
        q = self.bb84.quantum_bit_error_rate([0, 0, 1, 1], [0, 1, 1, 1])
        self.assertEqual(q, 0.25)
        print(f"  [PASS] QBER: {q:.2f}")


class TestE91Protocol(unittest.TestCase):
    """Test E91."""
    
    def setUp(self):
        self.e91 = E91Protocol()
    
    def test_correlation(self):
        """Should compute correlation."""
        a = [0, 1, 0, 1]
        b = [0, 1, 1, 0]
        c = self.e91.chsh_correlation(a, b)
        self.assertEqual(c, 0.0)
        print(f"  [PASS] Corr: {c:.2f}")
    
    def test_chsh(self):
        """Should compute CHSH."""
        S = self.e91.chsh_parameter([0.7, -0.7, 0.7, 0.7])
        self.assertAlmostEqual(S, 2.8, delta=1e-6)
        print(f"  [PASS] S: {S:.2f}")
    
    def test_entangle(self):
        """Should verify entanglement."""
        v = self.e91.entanglement_verified(2.5)
        self.assertTrue(v)
        print(f"  [PASS] Ent: {v}")


class TestQuantumKeyDistillation(unittest.TestCase):
    """Test distillation."""
    
    def setUp(self):
        self.qkd = QuantumKeyDistillation()
    
    def test_privacy(self):
        """Should amplify privacy."""
        k = self.qkd.privacy_amplification([0, 1, 0, 1])
        self.assertGreater(len(k), 0)
        print(f"  [PASS] Priv: {k}")
    
    def test_reconcile(self):
        """Should reconcile."""
        c1, c2 = self.qkd.error_reconciliation([0, 1, 0], [0, 1, 1])
        self.assertEqual(c1, c2)
        print(f"  [PASS] Rec: {c1}, {c2}")


class TestQuantumRandomNumberGeneration(unittest.TestCase):
    """Test QRNG."""
    
    def setUp(self):
        self.qrng = QuantumRandomNumberGeneration()
    
    def test_bits(self):
        """Should generate bits."""
        b = self.qrng.generate_bits(10, seed=42)
        self.assertEqual(len(b), 10)
        print(f"  [PASS] Bits: {b}")
    
    def test_bases(self):
        """Should generate bases."""
        b = self.qrng.generate_bases(10, seed=42)
        self.assertEqual(len(b), 10)
        print(f"  [PASS] Bases: {b}")
    
    def test_entropy(self):
        """Should compute entropy."""
        e = self.qrng.entropy_estimate([0, 1, 0, 1])
        self.assertEqual(e, 1.0)
        print(f"  [PASS] Ent: {e:.2f}")


class TestQuantumCryptographyAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qca = QuantumCryptographyAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qca.qkd_summary()
        self.assertIn("protocols", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
