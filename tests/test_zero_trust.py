"""
Unit tests for zero trust module.
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zero_trust import ZeroTrustController, DeviceIdentity, AccessPolicy, TrustLevel, AttestationEngine, PolicyEngine


class TestAttestationEngine(unittest.TestCase):
    """Test attestation engine."""
    
    def setUp(self):
        self.ae = AttestationEngine()
    
    def test_generate_challenge(self):
        """Should generate challenge."""
        challenge = self.ae.generate_challenge("dev1")
        self.assertIsNotNone(challenge)
        self.assertEqual(len(challenge), 64)
        print("  [PASS] Challenge: generated")
    
    def test_verify_response(self):
        """Should verify response."""
        import hashlib
        challenge = self.ae.generate_challenge("dev1")
        expected = hashlib.sha256(challenge.encode()).hexdigest()
        response = hashlib.sha256((challenge + expected).encode()).hexdigest()
        valid = self.ae.verify_response("dev1", response, expected)
        self.assertTrue(valid)
        print("  [PASS] Verify: valid")
    
    def test_score(self):
        """Should compute attestation score."""
        score = self.ae.get_attestation_score("dev1")
        self.assertEqual(score, 0.0)
        print(f"  [PASS] Score: {score}")


class TestPolicyEngine(unittest.TestCase):
    """Test policy engine."""
    
    def setUp(self):
        self.pe = PolicyEngine()
        self.pe.add_policy(AccessPolicy("propulsion", TrustLevel.TRUSTED, ["control"]))
    
    def test_grant(self):
        """Should grant access."""
        device = DeviceIdentity("dev1", "hash1", trust_level=TrustLevel.TRUSTED,
                               capabilities=["control"])
        result = self.pe.evaluate(device, "propulsion")
        self.assertTrue(result["granted"])
        print("  [PASS] Grant: OK")
    
    def test_deny_trust(self):
        """Should deny for low trust."""
        device = DeviceIdentity("dev1", "hash1", trust_level=TrustLevel.UNVERIFIED)
        result = self.pe.evaluate(device, "propulsion")
        self.assertFalse(result["granted"])
        self.assertEqual(result["reason"], "insufficient_trust")
        print("  [PASS] Deny trust: OK")
    
    def test_deny_capability(self):
        """Should deny for missing capability."""
        device = DeviceIdentity("dev1", "hash1", trust_level=TrustLevel.TRUSTED,
                               capabilities=["read"])
        result = self.pe.evaluate(device, "propulsion")
        self.assertFalse(result["granted"])
        self.assertEqual(result["reason"], "missing_capabilities")
        print("  [PASS] Deny cap: OK")
    
    def test_stats(self):
        """Should provide stats."""
        device = DeviceIdentity("dev1", "hash1", trust_level=TrustLevel.TRUSTED,
                               capabilities=["control"])
        self.pe.evaluate(device, "propulsion")
        stats = self.pe.get_access_stats()
        self.assertEqual(stats["total_requests"], 1)
        print(f"  [PASS] Stats: {stats['total_requests']} requests")


class TestZeroTrustController(unittest.TestCase):
    """Test zero-trust controller."""
    
    def setUp(self):
        self.zt = ZeroTrustController()
        self.zt.register_device("sc_main", "abc123", ["control", "telemetry"])
        self.zt.policy.add_policy(AccessPolicy("engines", TrustLevel.VERIFIED, ["control"]))
    
    def test_register(self):
        """Should register device."""
        self.assertIn("sc_main", self.zt.devices)
        print("  [PASS] Register: OK")
    
    def test_request_access_unknown(self):
        """Should reject unknown device."""
        result = self.zt.request_access("unknown", "engines")
        self.assertFalse(result["granted"])
        self.assertEqual(result["reason"], "unknown_device")
        print("  [PASS] Unknown: rejected")
    
    def test_request_access_granted(self):
        """Should grant valid access."""
        # Simulate attestation history for high trust
        self.zt.attestation.attestation_history["sc_main"] = [time.time()] * 10
        self.zt.devices["sc_main"].trust_level = TrustLevel.TRUSTED
        result = self.zt.request_access("sc_main", "engines")
        self.assertTrue(result["granted"])
        print("  [PASS] Access: granted")
    
    def test_device_status(self):
        """Should get device status."""
        status = self.zt.get_device_status("sc_main")
        self.assertIsNotNone(status)
        self.assertEqual(status["device_id"], "sc_main")
        print(f"  [PASS] Status: {status['trust_level']}")
    
    def test_network_summary(self):
        """Should provide network summary."""
        summary = self.zt.network_summary()
        self.assertEqual(summary["devices"], 1)
        print(f"  [PASS] Network: {summary['devices']} devices")


if __name__ == '__main__':
    unittest.main(verbosity=2)
