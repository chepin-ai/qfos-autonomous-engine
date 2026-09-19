"""
Unit tests for communications network module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from comm_network import CommNetwork, Node, LinkStatus


class TestCommNetwork(unittest.TestCase):
    """Test communications network."""
    
    def setUp(self):
        self.net = CommNetwork()
        self.net.add_node(Node("A", (0.0, 0.0, 0.0), transmit_power_w=100.0,
                              antenna_gain_db=30.0, data_rate_mbps=10.0))
        self.net.add_node(Node("B", (1000.0, 0.0, 0.0), transmit_power_w=100.0,
                              antenna_gain_db=30.0, data_rate_mbps=10.0))
    
    def test_add_node(self):
        """Should add node."""
        self.assertEqual(len(self.net.nodes), 2)
        print("  [PASS] Nodes: 2 added")
    
    def test_compute_link(self):
        """Should compute link."""
        link = self.net.compute_link("A", "B")
        self.assertIsNotNone(link)
        self.assertEqual(link.node_a, "A")
        self.assertEqual(link.node_b, "B")
        print(f"  [PASS] Link: {link.distance_m:.0f}m, rate={link.data_rate_mbps:.2f}Mbps")
    
    def test_establish_link(self):
        """Should establish link."""
        link = self.net.establish_link("A", "B")
        self.assertIsNotNone(link)
        self.assertIn(("A", "B"), self.net.links)
        print("  [PASS] Link established")
    
    def test_link_status(self):
        """Should determine link status."""
        link = self.net.compute_link("A", "B")
        self.assertIn(link.status, [LinkStatus.ACTIVE, LinkStatus.DEGRADED, LinkStatus.OFFLINE])
        print(f"  [PASS] Status: {link.status.value}")
    
    def test_find_route_direct(self):
        """Should find direct route."""
        self.net.establish_link("A", "B")
        route = self.net.find_route("A", "B")
        self.assertIsNotNone(route)
        self.assertEqual(route, ["A", "B"])
        print("  [PASS] Route: direct")
    
    def test_find_route_multi_hop(self):
        """Should find multi-hop route."""
        self.net.add_node(Node("C", (2000.0, 0.0, 0.0)))
        self.net.establish_link("A", "B")
        self.net.establish_link("B", "C")
        route = self.net.find_route("A", "C")
        self.assertEqual(len(route), 3)
        print(f"  [PASS] Route: {route}")
    
    def test_route_latency(self):
        """Should compute route latency."""
        self.net.establish_link("A", "B")
        route = self.net.find_route("A", "B")
        latency = self.net.compute_route_latency(route)
        self.assertGreater(latency, 0.0)
        print(f"  [PASS] Latency: {latency*1e6:.1f} us")
    
    def test_network_summary(self):
        """Should provide summary."""
        summary = self.net.network_summary()
        self.assertIn("nodes", summary)
        print(f"  [PASS] Summary: {summary['nodes']} nodes")
    
    def test_mars_relay(self):
        """Should create Mars relay."""
        net = CommNetwork()
        nodes = net.create_mars_relay_network()
        self.assertEqual(len(nodes), 6)
        print(f"  [PASS] Mars relay: {len(nodes)} nodes")


if __name__ == '__main__':
    unittest.main(verbosity=2)
