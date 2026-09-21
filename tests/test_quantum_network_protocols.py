"""
Unit tests for quantum network protocols module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_network_protocols import (QuantumNode, EntanglementLink,
                                       EntanglementDistributor,
                                       QuantumRepeater,
                                       QuantumRouter,
                                       QuantumNetworkStack,
                                       QuantumNetworkProtocols)


class TestEntanglementDistributor(unittest.TestCase):
    """Test distributor."""
    
    def setUp(self):
        self.ed = EntanglementDistributor(0.2)
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.ed.link_fidelity(10.0)
        self.assertGreater(f, 0)
        self.assertLessEqual(f, 0.99)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_success_prob(self):
        """Should compute probability."""
        p = self.ed.success_probability(10.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] Prob: {p:.4f}")


class TestQuantumRepeater(unittest.TestCase):
    """Test repeater."""
    
    def setUp(self):
        self.qr = QuantumRepeater()
    
    def test_store(self):
        """Should store pair."""
        self.qr.store_pair("p1", "n1", 0.9)
        self.assertIn("p1", self.qr.entanglement_pairs)
        print("  [PASS] Store")
    
    def test_swap(self):
        """Should swap."""
        f = self.qr.entanglement_swap(("n1", 0.9), ("n2", 0.8))
        self.assertAlmostEqual(f, 0.72, delta=0.01)
        print(f"  [PASS] Swap: {f:.2f}")
    
    def test_purify(self):
        """Should purify."""
        f = self.qr.purify(0.9, 0.85)
        self.assertGreater(f, 0.9)
        print(f"  [PASS] Pur: {f:.4f}")


class TestQuantumRouter(unittest.TestCase):
    """Test router."""
    
    def setUp(self):
        self.r = QuantumRouter()
        self.r.add_node(QuantumNode("n1", (0.0, 0.0), neighbors=["n2", "n3"]))
        self.r.add_node(QuantumNode("n2", (10.0, 0.0), neighbors=["n1", "n3"]))
        self.r.add_node(QuantumNode("n3", (5.0, 10.0), neighbors=["n1", "n2", "n4"]))
        self.r.add_node(QuantumNode("n4", (15.0, 10.0), neighbors=["n3"]))
        self.r.add_link(EntanglementLink("n1", "n2", 0.9, 1e3))
        self.r.add_link(EntanglementLink("n2", "n3", 0.85, 1e3))
        self.r.add_link(EntanglementLink("n3", "n4", 0.8, 1e3))
    
    def test_shortest_path(self):
        """Should find path."""
        p = self.r.shortest_path("n1", "n4")
        self.assertIn("n1", p)
        self.assertIn("n4", p)
        self.assertGreaterEqual(len(p), 2)
        print(f"  [PASS] Path: {p}")
    
    def test_path_fidelity(self):
        """Should compute fidelity."""
        p = self.r.shortest_path("n1", "n4")
        f = self.r.path_fidelity(p)
        self.assertAlmostEqual(f, 0.8, delta=0.01)
        print(f"  [PASS] PFid: {f:.2f}")


class TestQuantumNetworkStack(unittest.TestCase):
    """Test stack."""
    
    def setUp(self):
        self.ns = QuantumNetworkStack()
        self.ns.router.add_node(QuantumNode("a", (0.0, 0.0), neighbors=["b"]))
        self.ns.router.add_node(QuantumNode("b", (10.0, 0.0), neighbors=["a"]))
        self.ns.router.add_link(EntanglementLink("a", "b", 0.9, 1e3))
    
    def test_connection(self):
        """Should establish connection."""
        c = self.ns.establish_connection("a", "b")
        self.assertEqual(c["status"], "established")
        print(f"  [PASS] Conn: {c}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ns.network_summary()
        self.assertIn("nodes", s)
        print(f"  [PASS] Sum: {s}")


class TestQuantumNetworkProtocols(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qnp = QuantumNetworkProtocols()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qnp.qnp_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
