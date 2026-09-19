"""
Unit tests for telemetry encoder module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telemetry_encoder import (TelemetryFrame, EncodedPacket,
                               ReedSolomonEncoder, FramePacker,
                               ProtocolEncoder, TelemetryEncoder)


class TestReedSolomonEncoder(unittest.TestCase):
    """Test Reed-Solomon encoder."""
    
    def setUp(self):
        self.rs = ReedSolomonEncoder(nsym=16)
    
    def test_encode(self):
        """Should encode with parity."""
        data = b"Hello, Telemetry!"
        encoded = self.rs.encode(data)
        self.assertEqual(len(encoded), len(data) + 16)
        print(f"  [PASS] Encode: {len(data)} -> {len(encoded)} bytes")
    
    def test_decode_valid(self):
        """Should decode valid data."""
        data = b"Test data"
        encoded = self.rs.encode(data)
        decoded, is_valid = self.rs.decode(encoded)
        self.assertTrue(is_valid)
        self.assertEqual(decoded, data)
        print("  [PASS] Decode valid: ok")
    
    def test_decode_invalid(self):
        """Should detect corruption."""
        data = b"Test data"
        encoded = bytearray(self.rs.encode(data))
        encoded[0] ^= 0xFF  # Corrupt first byte
        decoded, is_valid = self.rs.decode(bytes(encoded))
        self.assertFalse(is_valid)
        print("  [PASS] Decode invalid: detected")
    
    def test_can_correct(self):
        """Should report correction capability."""
        self.assertTrue(self.rs.can_correct(b"test", 8))
        self.assertFalse(self.rs.can_correct(b"test", 20))
        print("  [PASS] Can correct: 8 yes, 20 no")


class TestFramePacker(unittest.TestCase):
    """Test frame packer."""
    
    def setUp(self):
        self.packer = FramePacker(max_frame_size=64)
    
    def test_pack(self):
        """Should pack data into frames."""
        data = b"A" * 200
        frames = self.packer.pack(data, timestamp=1000.0)
        self.assertGreater(len(frames), 1)
        print(f"  [PASS] Pack: {len(frames)} frames")
    
    def test_unpack(self):
        """Should unpack frames."""
        data = b"Hello World! " * 20
        frames = self.packer.pack(data)
        unpacked = self.packer.unpack(frames)
        self.assertEqual(unpacked, data)
        print("  [PASS] Unpack: correct")
    
    def test_frame_to_bytes(self):
        """Should convert frame to bytes."""
        frame = TelemetryFrame(frame_id=1, timestamp=0.0, data=b"test")
        frame_bytes = self.packer.frame_to_bytes(frame)
        self.assertEqual(len(frame_bytes), 24)
        print(f"  [PASS] To bytes: {len(frame_bytes)} bytes")
    
    def test_bytes_to_frame(self):
        """Should convert bytes to frame."""
        frame = TelemetryFrame(frame_id=42, timestamp=123.45, data=b"payload")
        frame_bytes = self.packer.frame_to_bytes(frame)
        recovered = self.packer.bytes_to_frame(frame_bytes)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered.frame_id, 42)
        self.assertEqual(recovered.data, b"payload")
        print("  [PASS] From bytes: id=42, data correct")


class TestProtocolEncoder(unittest.TestCase):
    """Test protocol encoder."""
    
    def setUp(self):
        self.enc = ProtocolEncoder()
    
    def test_encode_decode(self):
        """Should encode and decode."""
        data = b"Telemetry test data"
        packets = self.enc.encode_packet(data)
        self.assertGreater(len(packets), 0)
        
        decoded, is_valid = self.enc.decode_packet(packets)
        self.assertTrue(is_valid)
        self.assertEqual(decoded, data)
        print("  [PASS] Encode/decode: ok")
    
    def test_checksum(self):
        """Should compute checksum."""
        data = b"test"
        cs1 = self.enc._checksum(data)
        cs2 = self.enc._checksum(data)
        self.assertEqual(cs1, cs2)
        print(f"  [PASS] Checksum: {cs1}")
    
    def test_packet_to_bytes(self):
        """Should convert packet to bytes."""
        packets = self.enc.encode_packet(b"x")
        packet = packets[0]
        packet_bytes = self.enc.packet_to_bytes(packet)
        self.assertGreater(len(packet_bytes), 0)
        print(f"  [PASS] Packet bytes: {len(packet_bytes)}")


class TestTelemetryEncoder(unittest.TestCase):
    """Test unified telemetry encoder."""
    
    def setUp(self):
        self.te = TelemetryEncoder()
    
    def test_encode_string(self):
        """Should encode string."""
        packets = self.te.encode("Hello", timestamp=0.0)
        self.assertGreater(len(packets), 0)
        print(f"  [PASS] Encode string: {len(packets)} packets")
    
    def test_encode_dict(self):
        """Should encode dict."""
        packets = self.te.encode({"temp": 25.0, "pressure": 101.3})
        self.assertGreater(len(packets), 0)
        print(f"  [PASS] Encode dict: {len(packets)} packets")
    
    def test_decode(self):
        """Should decode packets."""
        packets = self.te.encode("Test message")
        decoded, is_valid = self.te.decode(packets)
        self.assertTrue(is_valid)
        self.assertIn("Test", decoded)
        print(f"  [PASS] Decode: '{decoded[:20]}...'")
    
    def test_summary(self):
        """Should provide summary."""
        self.te.encode("Data")
        summary = self.te.encoder_summary()
        self.assertIn("frames_sent", summary)
        self.assertIn("bytes_sent", summary)
        print(f"  [PASS] Summary: {summary['frames_sent']} frames")


if __name__ == '__main__':
    unittest.main(verbosity=2)
