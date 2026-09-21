"""
Unit tests for quantum network protocols advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_network_protocols_advanced import (EntanglementLink, EntanglementPurification,
                                                QuantumTeleportationNetwork,
                                                QuantumKeyDistributionNetwork,
                                                QuantumInternetStack,
                                                QuantumNetworkProtocolsAdvanced)


class TestEntanglementPurification(unittest.TestCase):
    """Test purification."""
    
    def setUp(self):
        self.ep = EntanglementPurification()
    
    def test_deutsch(self):
        """Should purify."""
        f = self.ep.deutsch_purification_fidelity(0.8)
        self.assertGreater(f, 0.8)
        print(f"  [PASS] Fout: {f:.4f}")
    
    def test_prob(self):
        """Should compute prob."""
        p = self.ep.success_probability(0.8)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.4f}")


class TestQuantumTeleportationNetwork(unittest.TestCase):
    """Test teleportation."""
    
    def setUp(self):
        self.qtn = QuantumTeleportationNetwork()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.qtn.teleportation_fidelity(0.9)
        self.assertEqual(f, 0.9)
        print(f"  [PASS] Ftel: {f:.2f}")
    
    def test_cost(self):
        """Should compute cost."""
        c = self.qtn.classical_communication_cost(1)
        self.assertEqual(c, 2)
        print(f"  [PASS] Bits: {c}")


class TestQuantumKeyDistributionNetwork(unittest.TestCase):
    """Test QKD."""
    
    def setUp(self):
        self.qkd = QuantumKeyDistributionNetwork()
    
    def test_bb84(self):
        """Should compute key rate."""
        r = self.qkd.bb84_key_rate(0.05)
        self.assertGreater(r, 0)
        print(f"  [PASS] R: {r:.1f}")
    
    def test_decoy(self):
        """Should compute decoy rate."""
        r = self.qkd.decoy_state_key_rate(0.2, 0.01, 0.05)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rdec: {r:.4f}")


class TestQuantumInternetStack(unittest.TestCase):
    """Test stack."""
    
    def setUp(self):
        self.qis = QuantumInternetStack()
    
    def test_rate(self):
        """Should compute rate."""
        r = self.qis.entanglement_generation_rate(0.5, 1e-3, 1e-4)
        self.assertGreater(r, 0)
        print(f"  [PASS] Re: {r:.4f}")
    
    def test_latency(self):
        """Should compute latency."""
        l = self.qis.network_latency(3)
        self.assertEqual(l, 33.0)
        print(f"  [PASS] Lat: {l:.1f}")


class TestQuantumNetworkProtocolsAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qnpa = QuantumNetworkProtocolsAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qnpa.network_summary()
        self.assertIn("protocols", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
