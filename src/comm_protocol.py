"""
Communication Protocol Module
CCSDS-style telemetry/telecommand packet handling,
frame synchronization, and data link layer functions.
"""

import struct
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import zlib


class PacketType(Enum):
    """CCSDS packet type."""
    TELEMETRY = 0    # Type 0 = TM
    TELECOMMAND = 1  # Type 1 = TC


class SequenceFlag(Enum):
    """CCSDS sequence flags."""
    CONTINUATION = 0
    FIRST = 1
    LAST = 2
    UNSEGMENTED = 3


@dataclass
class CCSDSPacket:
    """CCSDS Space Packet."""
    version: int = 0
    packet_type: PacketType = PacketType.TELEMETRY
    secondary_header: bool = False
    apid: int = 0  # Application Process ID (0-2047)
    sequence_flags: SequenceFlag = SequenceFlag.UNSEGMENTED
    sequence_count: int = 0
    packet_data_length: int = 0
    payload: bytes = b''
    
    PACKET_PRIMARY_HEADER_SIZE = 6
    MAX_PACKET_SIZE = 65542
    MAX_PAYLOAD_SIZE = 65536
    
    def to_bytes(self) -> bytes:
        """Serialize packet to bytes."""
        if len(self.payload) > self.MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload exceeds maximum size: {len(self.payload)}")
        
        # Packet ID field (2 bytes)
        packet_id = (
            (self.version & 0x07) << 13 |
            (self.packet_type.value & 0x01) << 12 |
            (1 if self.secondary_header else 0) << 11 |
            (self.apid & 0x07FF)
        )
        
        # Packet Sequence Control (2 bytes)
        seq_ctrl = (
            (self.sequence_flags.value & 0x03) << 14 |
            (self.sequence_count & 0x3FFF)
        )
        
        # Packet Data Length (2 bytes) = payload length - 1
        data_length = len(self.payload) - 1
        
        header = struct.pack('>HHH', packet_id, seq_ctrl, data_length)
        return header + self.payload
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'CCSDSPacket':
        """Deserialize packet from bytes."""
        if len(data) < cls.PACKET_PRIMARY_HEADER_SIZE:
            raise ValueError("Data too short for CCSDS header")
        
        packet_id, seq_ctrl, data_length = struct.unpack('>HHH', data[:6])
        
        version = (packet_id >> 13) & 0x07
        packet_type = PacketType((packet_id >> 12) & 0x01)
        secondary_header = bool((packet_id >> 11) & 0x01)
        apid = packet_id & 0x07FF
        
        sequence_flags = SequenceFlag((seq_ctrl >> 14) & 0x03)
        sequence_count = seq_ctrl & 0x3FFF
        
        payload = data[6:6 + data_length + 1]
        
        return cls(
            version=version,
            packet_type=packet_type,
            secondary_header=secondary_header,
            apid=apid,
            sequence_flags=sequence_flags,
            sequence_count=sequence_count,
            packet_data_length=data_length,
            payload=payload
        )
    
    def is_valid(self) -> bool:
        """Check packet validity."""
        return (0 <= self.apid <= 2047 and
                0 <= self.sequence_count <= 16383 and
                len(self.payload) <= self.MAX_PAYLOAD_SIZE)


class FrameBuilder:
    """Build CCSDS Transfer Frames."""
    
    def __init__(self, spacecraft_id: int = 0,
                 virtual_channel_id: int = 0):
        self.scid = spacecraft_id & 0x03FF
        self.vcid = virtual_channel_id & 0x3F
        self.frame_counter = 0
    
    def build_frame(self, packets: List[CCSDSPacket],
                    frame_size: int = 1115) -> bytes:
        """
        Build a transfer frame from packets.
        
        Args:
            packets: List of CCSDS packets
            frame_size: Frame size in bytes
        
        Returns:
            Transfer frame bytes
        """
        # Primary header (5 bytes for TM, 4 for TC)
        # Simplified: just concatenate packets with headers
        frame_data = b''
        for packet in packets:
            packet_bytes = packet.to_bytes()
            if len(frame_data) + len(packet_bytes) + 2 <= frame_size:
                frame_data += packet_bytes
            else:
                break
        
        # Pad to frame size
        if len(frame_data) < frame_size:
            frame_data += b'\x00' * (frame_size - len(frame_data))
        
        return frame_data[:frame_size]
    
    def add_crc(self, frame: bytes) -> bytes:
        """Add CRC-16 to frame."""
        crc = zlib.crc32(frame) & 0xFFFF
        return frame + struct.pack('>H', crc)


class ProtocolStack:
    """
    CCSDS Protocol Stack.
    
    Handles packetization, frame building, and
    data extraction.
    """
    
    def __init__(self, spacecraft_id: int = 0):
        self.scid = spacecraft_id
        self.frame_builder = FrameBuilder(spacecraft_id)
        self.packet_sequence: Dict[int, int] = {}  # APID -> count
    
    def create_telemetry_packet(self, apid: int,
                                 payload: bytes,
                                 secondary_header: bool = False) -> CCSDSPacket:
        """
        Create a telemetry packet.
        
        Args:
            apid: Application ID
            payload: Payload data
            secondary_header: Has secondary header
        
        Returns:
            CCSDS packet
        """
        seq_count = self.packet_sequence.get(apid, 0)
        self.packet_sequence[apid] = (seq_count + 1) & 0x3FFF
        
        return CCSDSPacket(
            version=0,
            packet_type=PacketType.TELEMETRY,
            secondary_header=secondary_header,
            apid=apid,
            sequence_flags=SequenceFlag.UNSEGMENTED,
            sequence_count=seq_count,
            payload=payload
        )
    
    def create_telecommand_packet(self, apid: int,
                                   payload: bytes) -> CCSDSPacket:
        """Create a telecommand packet."""
        return CCSDSPacket(
            version=0,
            packet_type=PacketType.TELECOMMAND,
            apid=apid,
            sequence_flags=SequenceFlag.UNSEGMENTED,
            payload=payload
        )
    
    def parse_frame(self, frame: bytes) -> List[CCSDSPacket]:
        """
        Parse packets from transfer frame.
        
        Args:
            frame: Raw frame bytes
        
        Returns:
            List of packets
        """
        packets = []
        offset = 0
        
        while offset + 6 <= len(frame):
            # Peek at packet length
            if offset + 6 > len(frame):
                break
            
            _, _, data_length = struct.unpack('>HHH', frame[offset:offset+6])
            packet_size = 6 + data_length + 1
            
            if offset + packet_size > len(frame):
                break
            
            try:
                packet = CCSDSPacket.from_bytes(frame[offset:offset+packet_size])
                if packet.is_valid():
                    packets.append(packet)
            except (ValueError, struct.error):
                pass
            
            offset += packet_size
        
        return packets
    
    def packetize_large_data(self, apid: int,
                              data: bytes,
                              max_payload: int = 1000) -> List[CCSDSPacket]:
        """
        Segment large data into multiple packets.
        
        Args:
            apid: Application ID
            data: Large data buffer
            max_payload: Maximum payload per packet
        
        Returns:
            List of segmented packets
        """
        packets = []
        offset = 0
        seq_count = self.packet_sequence.get(apid, 0)
        
        while offset < len(data):
            chunk = data[offset:offset + max_payload]
            
            if offset == 0 and offset + max_payload >= len(data):
                flags = SequenceFlag.UNSEGMENTED
            elif offset == 0:
                flags = SequenceFlag.FIRST
            elif offset + max_payload >= len(data):
                flags = SequenceFlag.LAST
            else:
                flags = SequenceFlag.CONTINUATION
            
            packet = CCSDSPacket(
                version=0,
                packet_type=PacketType.TELEMETRY,
                apid=apid,
                sequence_flags=flags,
                sequence_count=seq_count,
                payload=chunk
            )
            packets.append(packet)
            
            seq_count = (seq_count + 1) & 0x3FFF
            offset += max_payload
        
        self.packet_sequence[apid] = seq_count
        return packets
    
    def get_throughput_estimate(self, frame_size_bytes: int = 1115,
                                 frame_rate_hz: float = 1.0) -> Dict:
        """
        Estimate communication throughput.
        
        Args:
            frame_size_bytes: Frame size
            frame_rate_hz: Frames per second
        
        Returns:
            Throughput estimate
        """
        bits_per_frame = frame_size_bytes * 8
        bits_per_second = bits_per_frame * frame_rate_hz
        
        # Assuming 1/6 overhead for headers/idle
        efficiency = 5.0 / 6.0
        useful_bps = bits_per_second * efficiency
        
        return {
            "raw_bps": round(bits_per_second, 1),
            "useful_bps": round(useful_bps, 1),
            "raw_kbps": round(bits_per_second / 1000.0, 3),
            "useful_kbps": round(useful_bps / 1000.0, 3),
            "frames_per_second": frame_rate_hz,
            "efficiency": round(efficiency, 3)
        }
