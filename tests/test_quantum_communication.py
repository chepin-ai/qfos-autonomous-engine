"""
Unit tests for quantum communication module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_communication import (QuantumChannel, QuantumRepeater,
                                   EntanglementSwapper,
                                   QuantumMemory,
                                   QuantumRouter,
                                   QuantumCommunication)


class TestQuantumRepeater(unittest.TestCase):
    """Test repeater."""
    
    def setUp(self):
        self.qr = QuantumRepeater(0.99)
    
    def test_rate(self):
        """Should compute rate."""
        r = self.qr.entanglement_generation_rate(10.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rate: {r:.6f}")
    
    def test_purify(self):
        """Should purify."""
        f = self.qr.purify(0.9)
        self.assertGreater(f, 0.9)
        print(f"  [PASS] Pur: {f:.4f}")
    
    def test_chain(self):
        """Should compute chain fidelity."""
        f = self.qr.repeater_chain_fidelity(0.99, 2)
        self.assertAlmostEqual(f, 0.9801, places=4)
        print(f"  [PASS] ChF: {f:.4f}")


class TestEntanglementSwapper(unittest.TestCase):
    """Test swapper."""
    
    def setUp(self):
        self.es = EntanglementSwapper()
    
    def test_bsm(self):
        """Should perform BSM."""
        bsm = self.es.bell_state_measurement(0, 1)
        self.assertEqual(len(bsm), 2)
        print(f"  [PASS] BSM: {bsm}")
    
    def test_swap(self):
        """Should swap."""
        pair = self.es.swap((0, 1), (1, 2))
        self.assertEqual(pair[0], 0)
        self.assertEqual(pair[1], 2)
        print(f"  [PASS] Swap: {pair}")


class TestQuantumMemory(unittest.TestCase):
    """Test memory."""
    
    def setUp(self):
        self.qm = QuantumMemory(1.0)
    
    def test_store(self):
        """Should store."""
        self.qm.store([1.0, 0.0], 0.1)
        self.assertEqual(len(self.qm.stored_states), 1)
        print("  [PASS] Store")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.qm.fidelity_after_storage(0.5)
        self.assertAlmostEqual(f, 0.6065, places=3)
        print(f"  [PASS] MemF: {f:.4f}")
    
    def test_retrieve(self):
        """Should retrieve."""
        self.qm.store([0.0, 1.0])
        s = self.qm.retrieve(0)
        self.assertIsNotNone(s)
        print("  [PASS] Retr")
    
    def test_retrieve_none(self):
        """Should return None."""
        s = self.qm.retrieve(10)
        self.assertIsNone(s)
        print("  [PASS] RetN")


class TestQuantumRouter(unittest.TestCase):
    """Test router."""
    
    def setUp(self):
        self.router = QuantumRouter()
        self.router.add_node("A")
        self.router.add_node("B")
        self.router.add_node("C")
        self.router.add_channel(QuantumChannel("A", "B", 10.0, 0.2))
        self.router.add_channel(QuantumChannel("B", "C", 10.0, 0.2))
    
    def test_path(self):
        """Should find path."""
        p = self.router.shortest_path("A", "C")
        self.assertEqual(p, ["A", "B", "C"])
        print(f"  [PASS] Path: {p}")
    
    def test_same(self):
        """Should handle same node."""
        p = self.router.shortest_path("A", "A")
        self.assertEqual(p, ["A"])
        print("  [PASS] Same")
    
    def test_no_path(self):
        """Should return empty."""
        p = self.router.shortest_path("A", "Z")
        self.assertEqual(p, [])
        print("  [PASS] NoPath")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.router.path_fidelity(["A", "B", "C"])
        self.assertGreater(f, 0)
        print(f"  [PASS] PFid: {f:.4f}")


class TestQuantumCommunication(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumCommunication()
    
    def test_link(self):
        """Should establish link."""
        f = self.qc.establish_link("A", "B", 10.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] Link: {f:.6f}")
    
    def test_route(self):
        """Should route."""
        self.qc.router.add_node("A")
        self.qc.router.add_node("B")
        self.qc.router.add_channel(QuantumChannel("A", "B", 10.0, 0.2))
        p, f = self.qc.route_entanglement("A", "B")
        self.assertEqual(p, ["A", "B"])
        print(f"  [PASS] Rte: {p} F={f:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qc.qcomm_summary()
        self.assertIn("nodes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
