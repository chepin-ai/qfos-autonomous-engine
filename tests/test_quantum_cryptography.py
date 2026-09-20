"""
Unit tests for quantum cryptography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_cryptography import (QuantumKey, BB84Protocol,
                                  QuantumRandomNumberGenerator,
                                  QuantumSecureCommunication,
                                  QuantumAuthentication,
                                  QuantumCryptography)


class TestBB84Protocol(unittest.TestCase):
    """Test BB84."""
    
    def setUp(self):
        self.bb84 = BB84Protocol()
    
    def test_bits(self):
        """Should generate bits."""
        b = self.bb84.generate_bits(10)
        self.assertEqual(len(b), 10)
        print("  [PASS] Bits")
    
    def test_basis(self):
        """Should generate basis."""
        b = self.bb84.generate_basis(10)
        self.assertEqual(len(b), 10)
        print("  [PASS] Basis")
    
    def test_prepare(self):
        """Should prepare states."""
        s = self.bb84.prepare_qubits([0, 1], ["+", "X"])
        self.assertEqual(len(s), 2)
        print(f"  [PASS] Prep: {s}")
    
    def test_measure(self):
        """Should measure."""
        s = self.bb84.prepare_qubits([0, 1], ["+", "+"])
        m = self.bb84.measure_qubits(s, ["+", "+"])
        self.assertEqual(m, [0, 1])
        print(f"  [PASS] Meas: {m}")
    
    def test_sift(self):
        """Should sift key."""
        k = self.bb84.sift_key(["+", "X", "+"], ["+", "+", "+"], [0, 1, 0])
        self.assertEqual(len(k), 2)
        print(f"  [PASS] Sift: {k}")
    
    def test_run(self):
        """Should run protocol."""
        k = self.bb84.run_protocol(20)
        self.assertIsInstance(k, QuantumKey)
        self.assertGreater(k.length, 0)
        print(f"  [PASS] Run: {k.length} bits")


class TestQuantumRandomNumberGenerator(unittest.TestCase):
    """Test QRNG."""
    
    def setUp(self):
        self.qrng = QuantumRandomNumberGenerator(42)
    
    def test_bit(self):
        """Should generate bit."""
        b = self.qrng.random_bit()
        self.assertIn(b, [0, 1])
        print(f"  [PASS] Bit: {b}")
    
    def test_bits(self):
        """Should generate bits."""
        b = self.qrng.random_bits(10)
        self.assertEqual(len(b), 10)
        print("  [PASS] Bits")
    
    def test_float(self):
        """Should generate float."""
        f = self.qrng.random_float()
        self.assertGreaterEqual(f, 0.0)
        self.assertLess(f, 1.0)
        print(f"  [PASS] Float: {f:.4f}")


class TestQuantumSecureCommunication(unittest.TestCase):
    """Test QSDC."""
    
    def setUp(self):
        self.qsc = QuantumSecureCommunication()
    
    def test_key(self):
        """Should establish key."""
        k = self.qsc.establish_key(16)
        self.assertGreater(len(k.bits), 0)
        print(f"  [PASS] Key: {len(k.bits)} bits")
    
    def test_encrypt_decrypt(self):
        """Should encrypt/decrypt."""
        self.qsc.establish_key(32)
        msg = "Hi"
        c = self.qsc.encrypt_message(msg)
        d = self.qsc.decrypt_message(c)
        self.assertEqual(d, msg)
        print(f"  [PASS] Enc/Dec: '{d}'")


class TestQuantumAuthentication(unittest.TestCase):
    """Test QAuth."""
    
    def setUp(self):
        self.qa = QuantumAuthentication()
    
    def test_challenge(self):
        """Should generate challenge."""
        c = self.qa.generate_challenge(16)
        self.assertEqual(len(c), 16)
        print("  [PASS] Chal")
    
    def test_verify(self):
        """Should verify."""
        key = QuantumKey([0, 1, 0, 1], ["+", "+", "+", "+"], 4)
        c = [1, 0, 1, 0]
        r = self.qa.respond(c, key)
        v = self.qa.verify(c, r, key)
        self.assertTrue(v)
        print("  [PASS] Ver")


class TestQuantumCryptography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumCryptography()
    
    def test_key(self):
        """Should generate key."""
        k = self.qc.generate_secure_key(16)
        self.assertGreater(len(k.bits), 0)
        print(f"  [PASS] Key: {len(k.bits)} bits")
    
    def test_transmit(self):
        """Should transmit."""
        c, k = self.qc.secure_transmit("X")
        self.assertGreater(len(c), 0)
        print(f"  [PASS] Tx: {len(c)} bits")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qc.qcrypto_summary()
        self.assertIn("protocols", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
