"""
Unit tests for communications protocol module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from communications_protocol import (PacketType, Packet, LinkState,
                                     LinkLayer, PacketRouter,
                                     ErrorHandler, CommunicationsProtocol)


class TestPacket(unittest.TestCase):
    """Test packet."""
    
    def test_creation(self):
        """Should create packet."""
        p = Packet("A", "B", PacketType.DATA, 1, b"test")
        self.assertEqual(p.source, "A")
        self.assertEqual(p.destination, "B")
        print("  [PASS] Create: A->B")


class TestLinkLayer(unittest.TestCase):
    """Test link layer."""
    
    def setUp(self):
        self.ll = LinkLayer()
        self.ll.add_link("A", "B", bandwidth=1e6, latency=10.0)
    
    def test_add_link(self):
        """Should add link."""
        self.assertEqual(len(self.ll.links), 1)
        print("  [PASS] Add link: 1")
    
    def test_send(self):
        """Should send packet."""
        p = Packet("A", "B", PacketType.DATA, 1, b"test")
        result = self.ll.send(p)
        self.assertTrue(result)
        print("  [PASS] Send: ok")
    
    def test_send_no_link(self):
        """Should fail without link."""
        p = Packet("A", "C", PacketType.DATA, 1, b"test")
        result = self.ll.send(p)
        self.assertFalse(result)
        print("  [PASS] No link: fail")
    
    def test_set_state(self):
        """Should set link state."""
        self.ll.set_link_state("A", "B", False)
        link = self.ll.get_link("A", "B")
        self.assertFalse(link.is_up)
        print("  [PASS] State: down")
    
    def test_sequence(self):
        """Should increment sequence."""
        s1 = self.ll.next_sequence()
        s2 = self.ll.next_sequence()
        self.assertEqual(s2, s1 + 1)
        print(f"  [PASS] Seq: {s1}, {s2}")


class TestPacketRouter(unittest.TestCase):
    """Test packet router."""
    
    def setUp(self):
        self.r = PacketRouter()
        self.r.add_connection("A", "B")
        self.r.add_connection("B", "C")
        self.r.add_connection("A", "C")
    
    def test_add_node(self):
        """Should add node."""
        self.assertIn("A", self.r.nodes)
        print("  [PASS] Nodes: A, B, C")
    
    def test_route(self):
        """Should find route."""
        p = Packet("A", "C", PacketType.DATA, 1, b"test")
        route = self.r.route(p)
        self.assertIsNotNone(route)
        self.assertEqual(route[0], "A")
        self.assertEqual(route[-1], "C")
        print(f"  [PASS] Route: {' -> '.join(route)}")
    
    def test_hop_count(self):
        """Should count hops."""
        hops = self.r.get_hop_count("A", "C")
        self.assertEqual(hops, 1)  # Direct connection
        print(f"  [PASS] Hops: {hops}")


class TestErrorHandler(unittest.TestCase):
    """Test error handler."""
    
    def setUp(self):
        self.eh = ErrorHandler(max_retries=2, timeout=1.0)
    
    def test_send_success(self):
        """Should succeed on first try."""
        p = Packet("A", "B", PacketType.DATA, 1, b"test")
        result = self.eh.send_with_retry(p, lambda x: True)
        self.assertTrue(result)
        print("  [PASS] Send success: ok")
    
    def test_send_fail(self):
        """Should fail after retries."""
        p = Packet("A", "B", PacketType.DATA, 2, b"test")
        result = self.eh.send_with_retry(p, lambda x: False)
        self.assertFalse(result)
        print("  [PASS] Send fail: timeout")
    
    def test_handle_ack(self):
        """Should handle ACK."""
        p = Packet("A", "B", PacketType.DATA, 3, b"test")
        self.eh.send_with_retry(p, lambda x: True)
        self.eh.handle_ack(3)
        self.assertEqual(self.eh.stats["acked"], 1)
        print("  [PASS] ACK: 1")
    
    def test_handle_nack(self):
        """Should handle NACK."""
        self.eh.handle_nack(99)
        self.assertEqual(self.eh.stats["nacked"], 1)
        print("  [PASS] NACK: 1")
    
    def test_stats(self):
        """Should provide stats."""
        stats = self.eh.error_stats()
        self.assertIn("success_rate", stats)
        print(f"  [PASS] Stats: {stats['sent']} sent")


class TestCommunicationsProtocol(unittest.TestCase):
    """Test unified communications protocol."""
    
    def setUp(self):
        self.cp = CommunicationsProtocol()
        self.cp.connect("SC", "GS", bandwidth=1e6)
    
    def test_connect(self):
        """Should connect nodes."""
        summary = self.cp.protocol_summary()
        self.assertEqual(summary["nodes"], 2)
        print(f"  [PASS] Connect: {summary['nodes']} nodes")
    
    def test_send_packet(self):
        """Should send packet."""
        result = self.cp.send_packet("SC", "GS", b"telemetry")
        self.assertTrue(result)
        print("  [PASS] Send: ok")
    
    def test_receive(self):
        """Should receive packet."""
        p = Packet("GS", "SC", PacketType.COMMAND, 1, b"cmd")
        self.cp.receive_packet(p)
        self.assertEqual(len(self.cp.received_packets), 1)
        print("  [PASS] Receive: 1 packet")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.cp.protocol_summary()
        self.assertIn("links", summary)
        print(f"  [PASS] Summary: {summary['links']} links")


if __name__ == '__main__':
    unittest.main(verbosity=2)
