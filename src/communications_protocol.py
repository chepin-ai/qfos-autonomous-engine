"""
Communications Protocol Module
Packet routing, link layer, and error handling
for spacecraft data communication.
"""

import time
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class PacketType(Enum):
    """Packet type enumeration."""
    DATA = 0
    ACK = 1
    NACK = 2
    HEARTBEAT = 3
    COMMAND = 4
    TELEMETRY = 5


@dataclass
class Packet:
    """A communication packet."""
    source: str
    destination: str
    packet_type: PacketType
    sequence: int
    payload: bytes
    timestamp: float = 0.0
    ttl: int = 10
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class LinkState:
    """State of a communication link."""
    node_a: str
    node_b: str
    is_up: bool = True
    latency_ms: float = 0.0
    packet_loss: float = 0.0
    bandwidth_bps: float = 1e6
    last_heartbeat: float = 0.0


class LinkLayer:
    """
    Link layer protocol handler.
    """
    
    def __init__(self):
        self.links: Dict[Tuple[str, str], LinkState] = {}
        self.seq_counter = 0
    
    def add_link(self, node_a: str, node_b: str,
                bandwidth: float = 1e6, latency: float = 0.0):
        """Add communication link."""
        key = self._link_key(node_a, node_b)
        self.links[key] = LinkState(
            node_a=node_a, node_b=node_b,
            bandwidth_bps=bandwidth, latency_ms=latency
        )
    
    def _link_key(self, a: str, b: str) -> Tuple[str, str]:
        """Canonical link key."""
        return tuple(sorted([a, b]))
    
    def send(self, packet: Packet) -> bool:
        """
        Send packet over link.
        
        Args:
            packet: Packet to send
        
        Returns:
            True if successful
        """
        key = self._link_key(packet.source, packet.destination)
        if key not in self.links:
            return False
        
        link = self.links[key]
        if not link.is_up:
            return False
        
        # Simulate packet loss
        import random
        if random.random() < link.packet_loss:
            return False
        
        link.last_heartbeat = time.time()
        return True
    
    def get_link(self, node_a: str, node_b: str) -> Optional[LinkState]:
        """Get link state."""
        key = self._link_key(node_a, node_b)
        return self.links.get(key)
    
    def set_link_state(self, node_a: str, node_b: str, is_up: bool):
        """Set link up/down state."""
        key = self._link_key(node_a, node_b)
        if key in self.links:
            self.links[key].is_up = is_up
    
    def next_sequence(self) -> int:
        """Get next sequence number."""
        self.seq_counter += 1
        return self.seq_counter


class PacketRouter:
    """
    Packet router with shortest-path routing.
    """
    
    def __init__(self):
        self.nodes: set = set()
        self.neighbors: Dict[str, List[str]] = {}
        self.routes: Dict[Tuple[str, str], List[str]] = {}
    
    def add_node(self, node: str):
        """Add network node."""
        self.nodes.add(node)
        if node not in self.neighbors:
            self.neighbors[node] = []
    
    def add_connection(self, node_a: str, node_b: str):
        """Add bidirectional connection."""
        self.add_node(node_a)
        self.add_node(node_b)
        if node_b not in self.neighbors[node_a]:
            self.neighbors[node_a].append(node_b)
        if node_a not in self.neighbors[node_b]:
            self.neighbors[node_b].append(node_a)
        self._recompute_routes()
    
    def _recompute_routes(self):
        """Recompute all shortest-path routes."""
        self.routes = {}
        for source in self.nodes:
            for dest in self.nodes:
                if source != dest:
                    path = self._bfs(source, dest)
                    if path:
                        self.routes[(source, dest)] = path
    
    def _bfs(self, start: str, goal: str) -> Optional[List[str]]:
        """Breadth-first search for shortest path."""
        from collections import deque
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            node, path = queue.popleft()
            if node == goal:
                return path
            
            for neighbor in self.neighbors.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def route(self, packet: Packet) -> Optional[List[str]]:
        """
        Get route for packet.
        
        Args:
            packet: Packet to route
        
        Returns:
            Route path or None
        """
        key = (packet.source, packet.destination)
        return self.routes.get(key)
    
    def get_hop_count(self, source: str, dest: str) -> int:
        """Get hop count between nodes."""
        route = self.routes.get((source, dest))
        return len(route) - 1 if route else -1


class ErrorHandler:
    """
    Handle communication errors with retry logic.
    """
    
    def __init__(self, max_retries: int = 3, timeout: float = 5.0):
        """
        Args:
            max_retries: Maximum retry attempts
            timeout: Timeout in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.pending: Dict[int, Dict] = {}
        self.stats = {"sent": 0, "acked": 0, "nacked": 0, "timeouts": 0}
    
    def send_with_retry(self, packet: Packet,
                       send_fn: Callable[[Packet], bool]) -> bool:
        """
        Send packet with automatic retry.
        
        Args:
            packet: Packet to send
            send_fn: Send function
        
        Returns:
            True if successful
        """
        self.stats["sent"] += 1
        
        for attempt in range(self.max_retries):
            if send_fn(packet):
                self.pending[packet.sequence] = {
                    "packet": packet,
                    "attempts": attempt + 1,
                    "time": time.time()
                }
                return True
        
        self.stats["timeouts"] += 1
        return False
    
    def handle_ack(self, sequence: int):
        """Handle ACK packet."""
        if sequence in self.pending:
            del self.pending[sequence]
            self.stats["acked"] += 1
    
    def handle_nack(self, sequence: int):
        """Handle NACK packet."""
        self.stats["nacked"] += 1
        if sequence in self.pending:
            del self.pending[sequence]
    
    def check_timeouts(self) -> List[int]:
        """Check for timed-out packets."""
        now = time.time()
        timed_out = []
        for seq, info in list(self.pending.items()):
            if now - info["time"] > self.timeout:
                timed_out.append(seq)
                del self.pending[seq]
                self.stats["timeouts"] += 1
        return timed_out
    
    def error_stats(self) -> Dict:
        """Get error statistics."""
        total = self.stats["sent"]
        return {
            "sent": total,
            "acked": self.stats["acked"],
            "nacked": self.stats["nacked"],
            "timeouts": self.stats["timeouts"],
            "pending": len(self.pending),
            "success_rate": self.stats["acked"] / max(1, total)
        }


class CommunicationsProtocol:
    """
    Unified communications protocol controller.
    """
    
    def __init__(self):
        self.link_layer = LinkLayer()
        self.router = PacketRouter()
        self.error_handler = ErrorHandler()
        self.received_packets: List[Packet] = []
    
    def connect(self, node_a: str, node_b: str,
               bandwidth: float = 1e6, latency: float = 0.0):
        """
        Connect two nodes.
        
        Args:
            node_a: First node
            node_b: Second node
            bandwidth: Link bandwidth (bps)
            latency: Link latency (ms)
        """
        self.link_layer.add_link(node_a, node_b, bandwidth, latency)
        self.router.add_connection(node_a, node_b)
    
    def send_packet(self, source: str, dest: str,
                   payload: bytes,
                   packet_type: PacketType = PacketType.DATA) -> bool:
        """
        Send packet.
        
        Args:
            source: Source node
            dest: Destination node
            payload: Packet payload
            packet_type: Packet type
        
        Returns:
            True if sent
        """
        route = self.router.route(Packet(source, dest, packet_type, 0, b''))
        if not route:
            return False
        
        packet = Packet(
            source=source,
            destination=dest,
            packet_type=packet_type,
            sequence=self.link_layer.next_sequence(),
            payload=payload
        )
        
        return self.error_handler.send_with_retry(
            packet, self.link_layer.send
        )
    
    def receive_packet(self, packet: Packet):
        """Receive packet."""
        self.received_packets.append(packet)
        
        if packet.packet_type == PacketType.ACK:
            self.error_handler.handle_ack(packet.sequence)
        elif packet.packet_type == PacketType.NACK:
            self.error_handler.handle_nack(packet.sequence)
    
    def protocol_summary(self) -> Dict:
        """Get protocol summary."""
        return {
            "nodes": len(self.router.nodes),
            "links": len(self.link_layer.links),
            "routes": len(self.router.routes),
            "received": len(self.received_packets),
            "errors": self.error_handler.error_stats()
        }
