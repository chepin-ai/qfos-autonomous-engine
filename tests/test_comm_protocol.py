"""
Unit tests for communication protocol module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from comm_protocol import CCSDSPacket, PacketType, SequenceFlag, ProtocolStack, FrameBuilder


class TestCCSDSPacket(unittest.TestCase):
    """Test CCSDS packet."""
    
    def test_roundtrip(self):
        """Should serialize and deserialize."""
        packet = CCSDSPacket(
            version=0,
            packet_type=PacketType.TELEMETRY,
            apid=123,
            sequence_flags=SequenceFlag.UNSEGMENTED,
            sequence_count=42,
            payload=b'Hello, Space!'
        )
        
        data = packet.to_bytes()
        restored = CCSDSPacket.from_bytes(data)
        
        self.assertEqual(restored.apid, 123)
        self.assertEqual(restored.sequence_count, 42)
        self.assertEqual(restored.payload, b'Hello, Space!')
        print("  [PASS] Packet roundtrip")
    
    def test_validity(self):
        """Should validate packet."""
        packet = CCSDSPacket(apid=100, payload=b'test')
        self.assertTrue(packet.is_valid())
        
        bad = CCSDSPacket(apid=9999, payload=b'test')
        self.assertFalse(bad.is_valid())
        print("  [PASS] Packet validity")
    
    def test_telecommand(self):
        """Should create telecommand packet."""
        packet = CCSDSPacket(
            packet_type=PacketType.TELECOMMAND,
            apid=500,
            payload=b'CMD_EXECUTE'
        )
        self.assertEqual(packet.packet_type, PacketType.TELECOMMAND)
        data = packet.to_bytes()
        restored = CCSDSPacket.from_bytes(data)
        self.assertEqual(restored.packet_type, PacketType.TELECOMMAND)
        print("  [PASS] Telecommand packet")
    
    def test_large_payload(self):
        """Should handle large payloads."""
        payload = b'X' * 1000
        packet = CCSDSPacket(apid=1, payload=payload)
        data = packet.to_bytes()
        restored = CCSDSPacket.from_bytes(data)
        self.assertEqual(len(restored.payload), 1000)
        print("  [PASS] Large payload: 1000 bytes")


class TestProtocolStack(unittest.TestCase):
    """Test protocol stack."""
    
    def setUp(self):
        self.stack = ProtocolStack(spacecraft_id=42)
    
    def test_create_telemetry(self):
        """Should create telemetry packet."""
        packet = self.stack.create_telemetry_packet(
            apid=100, payload=b'TM_DATA'
        )
        self.assertEqual(packet.packet_type, PacketType.TELEMETRY)
        self.assertEqual(packet.apid, 100)
        print("  [PASS] Telemetry creation")
    
    def test_create_telecommand(self):
        """Should create telecommand packet."""
        packet = self.stack.create_telecommand_packet(
            apid=200, payload=b'TC_DATA'
        )
        self.assertEqual(packet.packet_type, PacketType.TELECOMMAND)
        print("  [PASS] Telecommand creation")
    
    def test_sequence_counting(self):
        """Should increment sequence count."""
        p1 = self.stack.create_telemetry_packet(apid=100, payload=b'A')
        p2 = self.stack.create_telemetry_packet(apid=100, payload=b'B')
        self.assertEqual(p2.sequence_count, p1.sequence_count + 1)
        print("  [PASS] Sequence counting")
    
    def test_packetize_large_data(self):
        """Should segment large data."""
        data = b'X' * 2500
        packets = self.stack.packetize_large_data(apid=50, data=data, max_payload=1000)
        self.assertGreater(len(packets), 2)
        self.assertEqual(packets[0].sequence_flags, SequenceFlag.FIRST)
        self.assertEqual(packets[-1].sequence_flags, SequenceFlag.LAST)
        print(f"  [PASS] Segmentation: {len(packets)} packets")
    
    def test_parse_frame(self):
        """Should parse frame into packets."""
        packets = [
            self.stack.create_telemetry_packet(10, b'A'),
            self.stack.create_telemetry_packet(10, b'B'),
        ]
        frame = self.stack.frame_builder.build_frame(packets, frame_size=200)
        parsed = self.stack.parse_frame(frame)
        self.assertGreaterEqual(len(parsed), 1)
        print(f"  [PASS] Frame parse: {len(parsed)} packets")
    
    def test_throughput(self):
        """Should estimate throughput."""
        est = self.stack.get_throughput_estimate(frame_size_bytes=1115, frame_rate_hz=2.0)
        self.assertGreater(est["raw_bps"], 0.0)
        self.assertGreater(est["useful_bps"], 0.0)
        print(f"  [PASS] Throughput: {est['raw_kbps']:.2f} kbps")


class TestFrameBuilder(unittest.TestCase):
    """Test frame builder."""
    
    def test_build_frame(self):
        """Should build frame."""
        fb = FrameBuilder(spacecraft_id=1, virtual_channel_id=0)
        packets = [CCSDSPacket(apid=1, payload=b'test')]
        frame = fb.build_frame(packets, frame_size=100)
        self.assertEqual(len(frame), 100)
        print("  [PASS] Frame size: 100 bytes")
    
    def test_crc(self):
        """Should add CRC."""
        fb = FrameBuilder()
        frame = b'\x00' * 10
        frame_with_crc = fb.add_crc(frame)
        self.assertEqual(len(frame_with_crc), len(frame) + 2)
        print("  [PASS] CRC appended")


if __name__ == '__main__':
    unittest.main(verbosity=2)
