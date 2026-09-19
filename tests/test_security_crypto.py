"""
Unit tests for security cryptography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from security_crypto import SymmetricCipher, DigitalSignature, KeyManager, SecureChannel


class TestSymmetricCipher(unittest.TestCase):
    """Test symmetric cipher."""
    
    def test_encrypt_decrypt(self):
        """Should encrypt and decrypt."""
        cipher = SymmetricCipher()
        plaintext = "Hello, Spacecraft!"
        ciphertext, mac = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(ciphertext, mac)
        self.assertEqual(decrypted, plaintext)
        print(f"  [PASS] Encrypt/decrypt: OK")
    
    def test_tamper_detection(self):
        """Should detect tampering."""
        cipher = SymmetricCipher()
        ciphertext, mac = cipher.encrypt("secret")
        # Tamper with ciphertext
        tampered = ciphertext[:-1] + bytes([ciphertext[-1] ^ 0xFF])
        decrypted = cipher.decrypt(tampered, mac)
        self.assertIsNone(decrypted)
        print("  [PASS] Tamper: detected")


class TestDigitalSignature(unittest.TestCase):
    """Test digital signature."""
    
    def setUp(self):
        self.signer = DigitalSignature()
        self.kp = self.signer.generate_keypair()
    
    def test_sign_verify(self):
        """Should sign and verify."""
        message = "burn_engines"
        sig = self.signer.sign(message, self.kp.private_key)
        valid = self.signer.verify(message, sig, self.kp.public_key, self.kp.private_key)
        self.assertTrue(valid)
        print("  [PASS] Sign/verify: valid")
    
    def test_verify_wrong_message(self):
        """Should reject wrong message."""
        sig = self.signer.sign("original", self.kp.private_key)
        valid = self.signer.verify("tampered", sig, self.kp.public_key, self.kp.private_key)
        self.assertFalse(valid)
        print("  [PASS] Wrong msg: rejected")


class TestKeyManager(unittest.TestCase):
    """Test key manager."""
    
    def setUp(self):
        self.km = KeyManager()
    
    def test_generate_symmetric(self):
        """Should generate symmetric key."""
        key = self.km.generate_key("sym_1", "symmetric")
        self.assertEqual(key["type"], "symmetric")
        self.assertEqual(key["status"], "active")
        print("  [PASS] Symmetric key: generated")
    
    def test_generate_asymmetric(self):
        """Should generate asymmetric key."""
        key = self.km.generate_key("asym_1", "asymmetric")
        self.assertEqual(key["type"], "asymmetric")
        self.assertIn("public", key["data"])
        print("  [PASS] Asymmetric key: generated")
    
    def test_revoke(self):
        """Should revoke key."""
        self.km.generate_key("k1")
        result = self.km.revoke_key("k1")
        self.assertTrue(result)
        self.assertEqual(self.km.get_key("k1")["status"], "revoked")
        print("  [PASS] Revoke: OK")
    
    def test_rotate(self):
        """Should rotate key."""
        self.km.generate_key("k1")
        new_key = self.km.rotate_key("k1")
        self.assertIsNotNone(new_key)
        print("  [PASS] Rotate: OK")
    
    def test_summary(self):
        """Should provide summary."""
        self.km.generate_key("k1")
        self.km.generate_key("k2")
        summary = self.km.key_summary()
        self.assertEqual(summary["total_keys"], 2)
        print(f"  [PASS] Summary: {summary['total_keys']} keys")


class TestSecureChannel(unittest.TestCase):
    """Test secure channel."""
    
    def setUp(self):
        self.channel = SecureChannel()
    
    def test_send_receive(self):
        """Should send and receive."""
        message = "telemetry_data"
        packet = self.channel.send(message)
        received = self.channel.receive(packet)
        self.assertEqual(received, message)
        print("  [PASS] Send/receive: OK")
    
    def test_stats(self):
        """Should track stats."""
        self.channel.send("msg1")
        self.channel.send("msg2")
        stats = self.channel.channel_stats()
        self.assertEqual(stats["messages_sent"], 2)
        print(f"  [PASS] Stats: {stats['messages_sent']} sent")


if __name__ == '__main__':
    unittest.main(verbosity=2)
