"""
Unit tests for communications protocol module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from comms_protocol import (PacketType, LinkState, Packet,
                            PacketFramer, ARQManager,
                            FlowController, CommsProtocol)


class TestPacketFramer(unittest.TestCase):
    """Test packet framer."""
    
    def setUp(self):
        self.framer = PacketFramer()
    
    def test_frame_deframe(self):
        """Should frame and deframe."""
        packet = Packet(1, PacketType.DATA, b'hello')
        framed = self.framer.frame(packet)
        self.assertGreater(len(framed), 0)
        
        decoded = self.framer.deframe(framed)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.sequence_num, 1)
        self.assertEqual(decoded.payload, b'hello')
        print(f"  [PASS] Frame/Deframe: {decoded.payload}")
    
    def test_deframe_invalid(self):
        """Should reject invalid frame."""
        decoded = self.framer.deframe(b'\x00\x00\x00')
        self.assertIsNone(decoded)
        print("  [PASS] Invalid: None")
    
    def test_crc_error(self):
        """Should detect CRC error."""
        packet = Packet(1, PacketType.DATA, b'test')
        framed = bytearray(self.framer.frame(packet))
        framed[-1] ^= 0xFF  # Corrupt CRC
        decoded = self.framer.deframe(bytes(framed))
        self.assertIsNone(decoded)
        print("  [PASS] CRC: rejected")
    
    def test_frame_size(self):
        """Should compute frame size."""
        size = self.framer.frame_size(10)
        self.assertEqual(size, len(self.framer.sync_word) + 4 + 10 + 1)
        print(f"  [PASS] Size: {size}")


class TestARQManager(unittest.TestCase):
    """Test ARQ manager."""
    
    def setUp(self):
        self.arq = ARQManager(max_retries=3, window_size=4)
    
    def test_send_packet(self):
        """Should send packet."""
        p = self.arq.send_packet(b'data')
        self.assertEqual(p.sequence_num, 0)
        self.assertEqual(len(self.arq.unacked), 1)
        print("  [PASS] Send: seq 0")
    
    def test_receive_ack(self):
        """Should process ACK."""
        self.arq.send_packet(b'data')
        ok = self.arq.receive_ack(0)
        self.assertTrue(ok)
        self.assertEqual(len(self.arq.unacked), 0)
        print("  [PASS] ACK: cleared")
    
    def test_window_limit(self):
        """Should enforce window."""
        for i in range(5):
            self.arq.send_packet(b'data')
        self.assertEqual(len(self.arq.unacked), 5)
        self.assertFalse(self.arq.window_available())
        print("  [PASS] Window: full")
    
    def test_retransmission(self):
        """Should retransmit."""
        self.arq.send_packet(b'data')
        retrans = self.arq.get_retransmissions()
        self.assertEqual(len(retrans), 1)
        print("  [PASS] Retrans: 1")
    
    def test_max_retries(self):
        """Should drop after max retries."""
        self.arq.send_packet(b'data')
        for _ in range(4):
            retrans = self.arq.get_retransmissions()
        self.assertEqual(len(self.arq.unacked), 0)
        print("  [PASS] Max retry: dropped")


class TestFlowController(unittest.TestCase):
    """Test flow controller."""
    
    def setUp(self):
        self.fc = FlowController(max_buffer_size=10)
    
    def test_enqueue(self):
        """Should enqueue packet."""
        p = Packet(0, PacketType.DATA, b'test')
        ok = self.fc.enqueue(p)
        self.assertTrue(ok)
        self.assertEqual(len(self.fc.buffer), 1)
        print("  [PASS] Enqueue: 1")
    
    def test_buffer_full(self):
        """Should reject when full."""
        for i in range(11):
            p = Packet(i, PacketType.DATA, b'test')
            self.fc.enqueue(p)
        ok = self.fc.enqueue(Packet(11, PacketType.DATA, b'test'))
        self.assertFalse(ok)
        print("  [PASS] Full: rejected")
    
    def test_dequeue(self):
        """Should dequeue packet."""
        p = Packet(0, PacketType.DATA, b'test')
        self.fc.enqueue(p)
        out = self.fc.dequeue()
        self.assertIsNotNone(out)
        self.assertEqual(out.sequence_num, 0)
        print("  [PASS] Dequeue: seq 0")
    
    def test_buffer_level(self):
        """Should compute buffer level."""
        for i in range(5):
            self.fc.enqueue(Packet(i, PacketType.DATA, b't'))
        level = self.fc.buffer_level()
        self.assertEqual(level, 0.5)
        print(f"  [PASS] Level: {level}")


class TestCommsProtocol(unittest.TestCase):
    """Test unified protocol."""
    
    def setUp(self):
        self.cp = CommsProtocol()
    
    def test_initial_state(self):
        """Should start disconnected."""
        self.assertEqual(self.cp.link_state, LinkState.DISCONNECTED)
        print("  [PASS] State: disconnected")
    
    def test_connect(self):
        """Should connect."""
        self.cp.connect()
        self.assertEqual(self.cp.link_state, LinkState.CONNECTED)
        print("  [PASS] Connect: ok")
    
    def test_send_not_connected(self):
        """Should not send when disconnected."""
        result = self.cp.send(b'data')
        self.assertEqual(result, b'')
        print("  [PASS] No send: disconnected")
    
    def test_send_receive(self):
        """Should send and receive."""
        self.cp.connect()
        framed = self.cp.send(b'hello')
        self.assertGreater(len(framed), 0)
        
        payload = self.cp.receive(framed)
        self.assertIsNotNone(payload)
        print(f"  [PASS] Send/Recv: {payload}")
    
    def test_summary(self):
        """Should provide summary."""
        self.cp.connect()
        self.cp.send(b'test')
        summary = self.cp.protocol_summary()
        self.assertEqual(summary["packets_tx"], 1)
        print(f"  [PASS] Summary: tx={summary['packets_tx']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
