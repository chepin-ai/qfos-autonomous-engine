"""
Communications Protocol Module
Packet framing, error detection, ARQ, and flow control
for autonomous system data link management.
"""

import struct
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class PacketType(Enum):
    """Protocol packet type."""
    DATA = 0x01
    ACK = 0x02
    NACK = 0x03
    HEARTBEAT = 0x04
    CONTROL = 0x05


class LinkState(Enum):
    """Data link state."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    ERROR = "error"


@dataclass
class Packet:
    """Protocol data packet."""
    sequence_num: int
    packet_type: PacketType
    payload: bytes
    timestamp: float = 0.0


class PacketFramer:
    """
    Frame and deframe packets.
    """
    
    def __init__(self, sync_word: bytes = b'\xAA\x55',
                 max_payload_size: int = 1024):
        """
        Args:
            sync_word: Frame sync pattern
            max_payload_size: Maximum payload bytes
        """
        self.sync_word = sync_word
        self.max_payload = max_payload_size
    
    def _checksum(self, data: bytes) -> int:
        """
        Compute simple XOR checksum.
        
        Args:
            data: Input data
        
        Returns:
            Checksum byte
        """
        cs = 0
        for b in data:
            cs ^= b
        return cs & 0xFF
    
    def frame(self, packet: Packet) -> bytes:
        """
        Frame a packet.
        
        Args:
            packet: Packet to frame
        
        Returns:
            Framed bytes
        """
        payload = packet.payload
        if len(payload) > self.max_payload:
            payload = payload[:self.max_payload]
        
        # Build frame: SYNC | SEQ | TYPE | LEN | PAYLOAD | CRC
        header = struct.pack('>BBH', packet.sequence_num & 0xFF,
                            packet.packet_type.value, len(payload))
        crc_data = header + payload
        crc = self._checksum(crc_data)
        
        return self.sync_word + crc_data + bytes([crc])
    
    def deframe(self, data: bytes) -> Optional[Packet]:
        """
        Deframe a packet.
        
        Args:
            data: Raw bytes
        
        Returns:
            Packet or None
        """
        if len(data) < len(self.sync_word) + 5:
            return None
        
        # Find sync word
        sync_idx = data.find(self.sync_word)
        if sync_idx < 0:
            return None
        
        frame_start = sync_idx + len(self.sync_word)
        if len(data) < frame_start + 4:
            return None
        
        # Parse header
        seq = data[frame_start]
        ptype = data[frame_start + 1]
        plen = struct.unpack('>H', data[frame_start + 2:frame_start + 4])[0]
        
        if plen > self.max_payload:
            return None
        
        if len(data) < frame_start + 4 + plen + 1:
            return None
        
        payload = data[frame_start + 4:frame_start + 4 + plen]
        crc_received = data[frame_start + 4 + plen]
        
        # Verify CRC
        crc_data = bytes([seq, ptype]) + struct.pack('>H', plen) + payload
        crc_calc = self._checksum(crc_data)
        
        if crc_received != crc_calc:
            return None
        
        return Packet(seq, PacketType(ptype), payload)
    
    def frame_size(self, payload_len: int) -> int:
        """Get total frame size for payload."""
        return len(self.sync_word) + 4 + payload_len + 1


class ARQManager:
    """
    Automatic Repeat Request manager.
    """
    
    def __init__(self, max_retries: int = 3,
                 window_size: int = 4):
        """
        Args:
            max_retries: Maximum retransmissions
            window_size: Sliding window size
        """
        self.max_retries = max_retries
        self.window_size = window_size
        self.next_seq = 0
        self.expected_seq = 0
        self.unacked: Dict[int, Tuple[Packet, int]] = {}
        # seq -> (packet, retry_count)
        self.buffer: List[Packet] = []
    
    def send_packet(self, payload: bytes,
                   packet_type: PacketType = PacketType.DATA) -> Packet:
        """
        Prepare packet for transmission.
        
        Args:
            payload: Data payload
            packet_type: Packet type
        
        Returns:
            Packet
        """
        packet = Packet(self.next_seq, packet_type, payload)
        self.next_seq = (self.next_seq + 1) % 256
        
        if packet_type == PacketType.DATA:
            self.unacked[packet.sequence_num] = (packet, 0)
        
        return packet
    
    def receive_ack(self, seq_num: int) -> bool:
        """
        Process ACK.
        
        Args:
            seq_num: Acknowledged sequence
        
        Returns:
            True if valid
        """
        if seq_num in self.unacked:
            del self.unacked[seq_num]
            return True
        return False
    
    def get_retransmissions(self) -> List[Packet]:
        """
        Get packets needing retransmission.
        
        Returns:
            List of packets to retransmit
        """
        retrans = []
        to_remove = []
        
        for seq, (packet, retries) in self.unacked.items():
            if retries >= self.max_retries:
                to_remove.append(seq)
            else:
                self.unacked[seq] = (packet, retries + 1)
                retrans.append(packet)
        
        for seq in to_remove:
            del self.unacked[seq]
        
        return retrans
    
    def receive_packet(self, packet: Packet) -> Optional[Packet]:
        """
        Process received packet.
        
        Args:
            packet: Received packet
        
        Returns:
            ACK packet or None
        """
        if packet.packet_type == PacketType.DATA:
            if packet.sequence_num == self.expected_seq:
                self.buffer.append(packet)
                self.expected_seq = (self.expected_seq + 1) % 256
                # Send ACK
                return Packet(packet.sequence_num, PacketType.ACK, b'')
            else:
                # Out of order
                return Packet(self.expected_seq - 1, PacketType.ACK, b'')
        
        return None
    
    def window_available(self) -> bool:
        """Check if send window has space."""
        return len(self.unacked) < self.window_size


class FlowController:
    """
    Flow control for data link.
    """
    
    def __init__(self, max_buffer_size: int = 100,
                 transmit_rate_Bps: float = 1000.0):
        """
        Args:
            max_buffer_size: Maximum buffer packets
            transmit_rate_Bps: Transmit rate
        """
        self.max_buffer = max_buffer_size
        self.tx_rate = transmit_rate_Bps
        self.buffer: List[Packet] = []
        self.bytes_sent = 0
        self.credits = max_buffer_size
    
    def can_accept(self) -> bool:
        """Check if buffer can accept new data."""
        return len(self.buffer) < self.max_buffer
    
    def enqueue(self, packet: Packet) -> bool:
        """
        Add packet to transmit buffer.
        
        Args:
            packet: Packet to send
        
        Returns:
            True if accepted
        """
        if self.can_accept():
            self.buffer.append(packet)
            return True
        return False
    
    def dequeue(self) -> Optional[Packet]:
        """Get next packet to transmit."""
        if self.buffer:
            packet = self.buffer.pop(0)
            self.bytes_sent += len(packet.payload)
            return packet
        return None
    
    def update_credits(self, credits: int):
        """Update flow control credits."""
        self.credits = credits
    
    def can_send(self) -> bool:
        """Check if allowed to send."""
        return self.credits > 0 and len(self.buffer) > 0
    
    def buffer_level(self) -> float:
        """Get buffer fill level."""
        return len(self.buffer) / self.max_buffer


class CommsProtocol:
    """
    Unified communications protocol controller.
    """
    
    def __init__(self):
        self.framer = PacketFramer()
        self.arq = ARQManager()
        self.flow = FlowController()
        self.link_state = LinkState.DISCONNECTED
        self.packets_tx = 0
        self.packets_rx = 0
        self.packets_dropped = 0
    
    def connect(self):
        """Establish connection."""
        self.link_state = LinkState.CONNECTED
    
    def disconnect(self):
        """Disconnect link."""
        self.link_state = LinkState.DISCONNECTED
    
    def send(self, data: bytes) -> bytes:
        """
        Send data over link.
        
        Args:
            data: Data to send
        
        Returns:
            Framed bytes
        """
        if self.link_state != LinkState.CONNECTED:
            return b''
        
        if not self.arq.window_available():
            self.packets_dropped += 1
            return b''
        
        packet = self.arq.send_packet(data)
        if not self.flow.enqueue(packet):
            self.packets_dropped += 1
            return b''
        
        framed = self.framer.frame(packet)
        self.packets_tx += 1
        return framed
    
    def receive(self, raw_bytes: bytes) -> Optional[bytes]:
        """
        Receive data from link.
        
        Args:
            raw_bytes: Raw received bytes
        
        Returns:
            Payload or None
        """
        packet = self.framer.deframe(raw_bytes)
        if not packet:
            return None
        
        self.packets_rx += 1
        
        if packet.packet_type == PacketType.ACK:
            self.arq.receive_ack(packet.sequence_num)
            return None
        
        ack = self.arq.receive_packet(packet)
        if ack:
            # Would send ACK back
            pass
        
        if packet.packet_type == PacketType.DATA:
            return packet.payload
        
        return None
    
    def retransmit(self) -> List[bytes]:
        """Get retransmission frames."""
        packets = self.arq.get_retransmissions()
        return [self.framer.frame(p) for p in packets]
    
    def protocol_summary(self) -> Dict:
        """Get protocol summary."""
        return {
            "link_state": self.link_state.value,
            "packets_tx": self.packets_tx,
            "packets_rx": self.packets_rx,
            "packets_dropped": self.packets_dropped,
            "unacked": len(self.arq.unacked),
            "buffer_level": self.flow.buffer_level(),
            "window_available": self.arq.window_available()
        }
