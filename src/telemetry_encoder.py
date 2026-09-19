"""
Telemetry Encoder Module
Frame packing, error correction, and protocol encoding
for spacecraft telemetry downlink.
"""

import struct
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field


@dataclass
class TelemetryFrame:
    """A telemetry frame."""
    frame_id: int
    timestamp: float
    data: bytes
    sequence: int = 0
    is_valid: bool = True


@dataclass
class EncodedPacket:
    """An encoded telemetry packet."""
    header: bytes
    payload: bytes
    checksum: int
    length: int


class ReedSolomonEncoder:
    """
    Simplified Reed-Solomon error correction encoder.
    
    Uses a simplified RS(255, 223) style approach with
    XOR-based parity for demonstration.
    """
    
    def __init__(self, nsym: int = 32):
        """
        Args:
            nsym: Number of parity symbols
        """
        self.nsym = nsym
    
    def encode(self, data: bytes) -> bytes:
        """
        Encode data with parity symbols.
        
        Args:
            data: Input data
        
        Returns:
            Data + parity
        """
        if not data:
            return data
        
        # Compute parity as XOR checksums over interleaved bytes
        parity = bytearray(self.nsym)
        
        for i, byte in enumerate(data):
            parity[i % self.nsym] ^= byte
        
        return data + bytes(parity)
    
    def decode(self, data: bytes) -> Tuple[bytes, bool]:
        """
        Decode and verify data.
        
        Args:
            data: Encoded data
        
        Returns:
            (decoded_data, is_valid)
        """
        if len(data) < self.nsym:
            return data, False
        
        payload = data[:-self.nsym]
        received_parity = data[-self.nsym:]
        
        # Recompute parity
        computed_parity = bytearray(self.nsym)
        for i, byte in enumerate(payload):
            computed_parity[i % self.nsym] ^= byte
        
        is_valid = bytes(computed_parity) == received_parity
        return payload, is_valid
    
    def can_correct(self, data: bytes, errors: int) -> bool:
        """Check if errors can be corrected."""
        return errors <= self.nsym // 2


class FramePacker:
    """
    Pack telemetry data into frames.
    """
    
    def __init__(self, max_frame_size: int = 1024):
        """
        Args:
            max_frame_size: Maximum frame size in bytes
        """
        self.max_frame_size = max_frame_size
        self.sequence_counter = 0
    
    def pack(self, data: bytes, timestamp: float = 0.0) -> List[TelemetryFrame]:
        """
        Pack data into frames.
        
        Args:
            data: Data to pack
            timestamp: Frame timestamp
        
        Returns:
            List of frames
        """
        if not data:
            return []
        
        # Header size: frame_id (4) + timestamp (8) + sequence (4) + length (4) = 20 bytes
        header_size = 20
        payload_size = self.max_frame_size - header_size
        
        frames = []
        offset = 0
        frame_id = 0
        
        while offset < len(data):
            chunk = data[offset:offset + payload_size]
            frame = TelemetryFrame(
                frame_id=frame_id,
                timestamp=timestamp,
                data=chunk,
                sequence=self.sequence_counter
            )
            frames.append(frame)
            offset += payload_size
            frame_id += 1
            self.sequence_counter += 1
        
        return frames
    
    def unpack(self, frames: List[TelemetryFrame]) -> bytes:
        """
        Unpack frames into data.
        
        Args:
            frames: Frames to unpack
        
        Returns:
            Combined data
        """
        data = bytearray()
        for frame in sorted(frames, key=lambda f: f.frame_id):
            data.extend(frame.data)
        return bytes(data)
    
    def frame_to_bytes(self, frame: TelemetryFrame) -> bytes:
        """Convert frame to bytes."""
        header = struct.pack('>I', frame.frame_id)  # 4 bytes
        header += struct.pack('>d', frame.timestamp)  # 8 bytes
        header += struct.pack('>I', frame.sequence)  # 4 bytes
        header += struct.pack('>I', len(frame.data))  # 4 bytes
        return header + frame.data
    
    def bytes_to_frame(self, data: bytes) -> Optional[TelemetryFrame]:
        """Convert bytes to frame."""
        if len(data) < 20:
            return None
        
        frame_id = struct.unpack('>I', data[0:4])[0]
        timestamp = struct.unpack('>d', data[4:12])[0]
        sequence = struct.unpack('>I', data[12:16])[0]
        length = struct.unpack('>I', data[16:20])[0]
        
        if len(data) < 20 + length:
            return None
        
        return TelemetryFrame(
            frame_id=frame_id,
            timestamp=timestamp,
            data=data[20:20+length],
            sequence=sequence
        )


class ProtocolEncoder:
    """
    Encode/decode telemetry protocol packets.
    """
    
    def __init__(self):
        self.packer = FramePacker()
        self.rs = ReedSolomonEncoder()
    
    def encode_packet(self, data: bytes,
                     timestamp: float = 0.0) -> List[EncodedPacket]:
        """
        Encode data into protocol packets.
        
        Args:
            data: Input data
            timestamp: Packet timestamp
        
        Returns:
            List of encoded packets
        """
        # Add Reed-Solomon parity
        encoded_data = self.rs.encode(data)
        
        # Pack into frames
        frames = self.packer.pack(encoded_data, timestamp)
        
        packets = []
        for frame in frames:
            frame_bytes = self.packer.frame_to_bytes(frame)
            checksum = self._checksum(frame_bytes)
            
            packet = EncodedPacket(
                header=frame_bytes[:20],
                payload=frame_bytes[20:],
                checksum=checksum,
                length=len(frame_bytes)
            )
            packets.append(packet)
        
        return packets
    
    def decode_packet(self, packets: List[EncodedPacket]) -> Tuple[bytes, bool]:
        """
        Decode packets back to data.
        
        Args:
            packets: Encoded packets
        
        Returns:
            (data, is_valid)
        """
        frames = []
        for packet in packets:
            frame_bytes = packet.header + packet.payload
            
            # Verify checksum
            if self._checksum(frame_bytes) != packet.checksum:
                continue
            
            frame = self.packer.bytes_to_frame(frame_bytes)
            if frame:
                frames.append(frame)
        
        if not frames:
            return b'', False
        
        encoded_data = self.packer.unpack(frames)
        data, is_valid = self.rs.decode(encoded_data)
        
        return data, is_valid
    
    def _checksum(self, data: bytes) -> int:
        """Compute simple checksum."""
        return sum(data) & 0xFFFF
    
    def packet_to_bytes(self, packet: EncodedPacket) -> bytes:
        """Convert packet to bytes."""
        header = packet.header
        payload = packet.payload
        trailer = struct.pack('>H', packet.checksum)
        trailer += struct.pack('>H', packet.length)
        return header + payload + trailer
    
    def bytes_to_packet(self, data: bytes) -> Optional[EncodedPacket]:
        """Convert bytes to packet."""
        if len(data) < 24:
            return None
        
        # Find length from trailer
        length = struct.unpack('>H', data[-2:])[0]
        if len(data) != length + 4:
            return None
        
        checksum = struct.unpack('>H', data[-4:-2])[0]
        payload_len = length - 20
        
        if payload_len < 0 or len(data) < 24 + payload_len:
            return None
        
        return EncodedPacket(
            header=data[:20],
            payload=data[20:20+payload_len],
            checksum=checksum,
            length=length
        )


class TelemetryEncoder:
    """
    Unified telemetry encoding controller.
    """
    
    def __init__(self):
        self.protocol = ProtocolEncoder()
        self.stats = {"frames_sent": 0, "bytes_sent": 0, "errors": 0}
    
    def encode(self, data: Union[bytes, str, Dict],
               timestamp: float = 0.0) -> List[EncodedPacket]:
        """
        Encode telemetry data.
        
        Args:
            data: Data to encode
            timestamp: Timestamp
        
        Returns:
            Encoded packets
        """
        if isinstance(data, str):
            raw = data.encode('utf-8')
        elif isinstance(data, dict):
            raw = str(data).encode('utf-8')
        else:
            raw = data
        
        packets = self.protocol.encode_packet(raw, timestamp)
        self.stats["frames_sent"] += len(packets)
        self.stats["bytes_sent"] += sum(p.length for p in packets)
        
        return packets
    
    def decode(self, packets: List[EncodedPacket]) -> Tuple[Union[str, bytes], bool]:
        """
        Decode telemetry data.
        
        Args:
            packets: Encoded packets
        
        Returns:
            (data, is_valid)
        """
        data, is_valid = self.protocol.decode_packet(packets)
        if not is_valid:
            self.stats["errors"] += 1
        
        # Try to decode as string
        try:
            return data.decode('utf-8'), is_valid
        except (UnicodeDecodeError, AttributeError):
            return data, is_valid
    
    def encoder_summary(self) -> Dict:
        """Get encoder summary."""
        return {
            "frames_sent": self.stats["frames_sent"],
            "bytes_sent": self.stats["bytes_sent"],
            "errors": self.stats["errors"],
            "error_rate": self.stats["errors"] / max(1, self.stats["frames_sent"])
        }
