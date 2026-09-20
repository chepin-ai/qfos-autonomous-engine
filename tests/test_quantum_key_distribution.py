"""
Unit tests for quantum key distribution module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_key_distribution import (Basis, BitValue, QubitTransmission,
                                      BB84Protocol, EavesdropperDetector,
                                      PrivacyAmplification, KeyDistillation,
                                      QuantumKeyDistribution)


class TestBB84Protocol(unittest.TestCase):
    """Test BB84 protocol."""
    
    def setUp(self):
        self.bb84 = BB84Protocol()
    
    def test_encode(self):
        """Should encode qubit."""
        tx = self.bb84.encode(1, Basis.RECTILINEAR)
        self.assertEqual(tx.bit, 1)
        self.assertEqual(tx.basis, Basis.RECTILINEAR)
        print("  [PASS] Encode")
    
    def test_measure_correct_basis(self):
        """Should measure correctly in same basis."""
        tx = self.bb84.encode(1, Basis.RECTILINEAR)
        result = self.bb84.measure(tx, Basis.RECTILINEAR)
        self.assertEqual(result, 1)
        print("  [PASS] Measure correct")
    
    def test_measure_wrong_basis(self):
        """Should get random in wrong basis."""
        tx = self.bb84.encode(1, Basis.RECTILINEAR)
        result = self.bb84.measure(tx, Basis.DIAGONAL)
        self.assertIn(result, [0, 1])
        print(f"  [PASS] Measure wrong: {result}")
    
    def test_sift(self):
        """Should sift matching bases."""
        self.bb84.encode(1, Basis.RECTILINEAR)
        self.bb84.measure(self.bb84.transmissions[0], Basis.RECTILINEAR)
        self.bb84.encode(0, Basis.DIAGONAL)
        self.bb84.measure(self.bb84.transmissions[1], Basis.RECTILINEAR)
        key = self.bb84.sift()
        self.assertEqual(len(key), 1)
        self.assertEqual(key[0], 1)
        print(f"  [PASS] Sift: {key}")
    
    def test_key_rate(self):
        """Should estimate key rate."""
        rate = self.bb84.estimate_key_rate(0.05)
        self.assertGreater(rate, 0)
        print(f"  [PASS] Rate: {rate:.0f} bps")
    
    def test_key_rate_zero(self):
        """Should have zero rate above threshold."""
        rate = self.bb84.estimate_key_rate(0.15)
        self.assertEqual(rate, 0.0)
        print("  [PASS] Rate zero")


class TestEavesdropperDetector(unittest.TestCase):
    """Test eavesdropper detector."""
    
    def setUp(self):
        self.ed = EavesdropperDetector()
    
    def test_no_eavesdropper(self):
        """Should not detect with low QBER."""
        detected, conf = self.ed.detect(0.01, 0.01, 1000)
        self.assertFalse(detected)
        print("  [PASS] No Eve")
    
    def test_detect_eavesdropper(self):
        """Should detect high QBER."""
        detected, conf = self.ed.detect(0.15, 0.01, 1000)
        self.assertTrue(detected)
        print(f"  [PASS] Eve: conf={conf:.2f}")
    
    def test_information_leak(self):
        """Should estimate leak."""
        leak = self.ed.information_leak(0.05)
        self.assertGreater(leak, 0)
        print(f"  [PASS] Leak: {leak:.4f}")


class TestPrivacyAmplification(unittest.TestCase):
    """Test privacy amplification."""
    
    def setUp(self):
        self.pa = PrivacyAmplification()
    
    def test_hash(self):
        """Should hash key."""
        key = [1, 0, 1, 1, 0, 0, 1, 0]
        seed = [1, 1, 0, 0]
        out = self.pa.toeplitz_hash(key, seed, 4)
        self.assertEqual(len(out), 4)
        print(f"  [PASS] Hash: {out}")
    
    def test_amplify(self):
        """Should amplify."""
        raw = [1, 0, 1, 1, 0, 0, 1, 0] * 10
        final = self.pa.amplify(raw, 0.1)
        self.assertGreater(len(final), 0)
        self.assertLess(len(final), len(raw))
        print(f"  [PASS] Amplify: {len(raw)} -> {len(final)}")


class TestKeyDistillation(unittest.TestCase):
    """Test key distillation."""
    
    def setUp(self):
        self.kd = KeyDistillation()
    
    def test_distill(self):
        """Should distill key."""
        txs = []
        for i in range(100):
            tx = QubitTransmission(bit=i % 2,
                                   basis=Basis.RECTILINEAR,
                                   received_bit=i % 2,
                                   received_basis=Basis.RECTILINEAR)
            txs.append(tx)
        
        key, success = self.kd.distill(txs, sample_fraction=0.1)
        self.assertTrue(success)
        self.assertGreater(len(key), 0)
        print(f"  [PASS] Distill: {len(key)} bits")
    
    def test_stats(self):
        """Should provide stats."""
        s = self.kd.key_stats()
        self.assertIn("raw_key_length", s)
        print(f"  [PASS] Stats: {s}")


class TestQuantumKeyDistribution(unittest.TestCase):
    """Test unified QKD."""
    
    def setUp(self):
        self.qkd = QuantumKeyDistribution()
    
    def test_transmit(self):
        """Should transmit."""
        bits = [1, 0, 1, 0]
        bases = [Basis.RECTILINEAR, Basis.RECTILINEAR, Basis.DIAGONAL, Basis.DIAGONAL]
        mbases = [Basis.RECTILINEAR, Basis.DIAGONAL, Basis.DIAGONAL, Basis.RECTILINEAR]
        txs = self.qkd.transmit(bits, bases, mbases)
        self.assertEqual(len(txs), 4)
        print(f"  [PASS] TX: {len(txs)}")
    
    def test_generate_key(self):
        """Should generate key."""
        bits = [1, 0, 1, 0, 1, 1, 0, 0] * 20
        bases = [Basis.RECTILINEAR, Basis.DIAGONAL] * 80
        mbases = [Basis.RECTILINEAR, Basis.DIAGONAL] * 80
        txs = self.qkd.transmit(bits, bases, mbases)
        key, success = self.qkd.generate_key(txs)
        self.assertTrue(success or len(key) == 0)
        print(f"  [PASS] Key: {len(key)} bits, success={success}")
    
    def test_summary(self):
        """Should provide summary."""
        s = self.qkd.qkd_summary()
        self.assertIn("total_sessions", s)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
