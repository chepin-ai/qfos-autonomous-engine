"""
Communications Network Module
Multi-hop relay network simulation, link routing,
network topology management for deep space comms.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class LinkStatus(Enum):
    """Link status states."""
    ACTIVE = "active"
    DEGRADED = "degraded"
    INTERRUPTED = "interrupted"
    OFFLINE = "offline"


@dataclass
class Node:
    """A network node (spacecraft, relay, ground station)."""
    name: str
    position_m: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    transmit_power_w: float = 50.0
    antenna_gain_db: float = 30.0
    frequency_ghz: float = 8.4
    data_rate_mbps: float = 10.0
    buffer_capacity_mb: float = 1000.0
    buffer_occupied_mb: float = 0.0
    operational: bool = True


@dataclass
class Link:
    """A communication link between two nodes."""
    node_a: str
    node_b: str
    distance_m: float = 0.0
    status: LinkStatus = LinkStatus.ACTIVE
    data_rate_mbps: float = 0.0
    latency_s: float = 0.0
    bit_error_rate: float = 1e-6
    margin_db: float = 3.0


class CommNetwork:
    """
    Deep space communications network.
    
    Manages nodes, links, routing, and topology
    for multi-hop relay operations.
    """
    
    SPEED_OF_LIGHT = 299792458.0  # m/s
    BOLTZMANN = 1.380649e-23
    SYSTEM_TEMP_K = 290.0
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.links: Dict[Tuple[str, str], Link] = {}
        self.routes: Dict[Tuple[str, str], List[str]] = {}
    
    def add_node(self, node: Node):
        """Add a node to the network."""
        self.nodes[node.name] = node
    
    def remove_node(self, name: str):
        """Remove a node and its links."""
        if name in self.nodes:
            del self.nodes[name]
        
        # Remove associated links
        to_remove = []
        for (a, b) in self.links:
            if a == name or b == name:
                to_remove.append((a, b))
        for key in to_remove:
            del self.links[key]
    
    def compute_link(self, node_a: str, node_b: str) -> Optional[Link]:
        """
        Compute link parameters between two nodes.
        
        Args:
            node_a, node_b: Node names
        
        Returns:
            Link or None
        """
        if node_a not in self.nodes or node_b not in self.nodes:
            return None
        
        a = self.nodes[node_a]
        b = self.nodes[node_b]
        
        if not a.operational or not b.operational:
            return None
        
        # Distance
        dx = a.position_m[0] - b.position_m[0]
        dy = a.position_m[1] - b.position_m[1]
        dz = a.position_m[2] - b.position_m[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Free space path loss
        wavelength = self.SPEED_OF_LIGHT / (a.frequency_ghz * 1e9)
        fspl_db = 20.0 * math.log10(4.0 * math.pi * distance / wavelength)
        
        # Link budget
        received_power_db = (10.0 * math.log10(a.transmit_power_w) +
                            a.antenna_gain_db + b.antenna_gain_db - fspl_db)
        
        # Noise floor
        noise_db = 10.0 * math.log10(self.BOLTZMANN * self.SYSTEM_TEMP_K * 1e6)
        snr_db = received_power_db - noise_db
        
        # Data rate from Shannon limit (simplified)
        bandwidth_mhz = 10.0
        capacity_mbps = bandwidth_mhz * math.log2(1.0 + 10.0**(snr_db/10.0))
        data_rate = min(a.data_rate_mbps, capacity_mbps)
        
        # Latency
        latency = distance / self.SPEED_OF_LIGHT
        
        # Status
        if snr_db < 0.0:
            status = LinkStatus.OFFLINE
        elif snr_db < 3.0:
            status = LinkStatus.DEGRADED
        else:
            status = LinkStatus.ACTIVE
        
        return Link(
            node_a=node_a, node_b=node_b,
            distance_m=round(distance, 1),
            status=status,
            data_rate_mbps=round(data_rate, 3),
            latency_s=round(latency, 6),
            bit_error_rate=1e-6 / (1.0 + 10.0**(snr_db/10.0)),
            margin_db=round(snr_db, 2)
        )
    
    def establish_link(self, node_a: str, node_b: str) -> Optional[Link]:
        """
        Establish a bidirectional link.
        
        Args:
            node_a, node_b: Node names
        
        Returns:
            Link or None
        """
        link = self.compute_link(node_a, node_b)
        if link:
            self.links[(node_a, node_b)] = link
            # Bidirectional
            rev = self.compute_link(node_b, node_a)
            if rev:
                self.links[(node_b, node_a)] = rev
        return link
    
    def find_route(self, source: str, destination: str,
                   max_hops: int = 5) -> Optional[List[str]]:
        """
        Find shortest route using BFS.
        
        Args:
            source: Source node
            destination: Destination node
            max_hops: Maximum hops
        
        Returns:
            Route as list of node names or None
        """
        if source not in self.nodes or destination not in self.nodes:
            return None
        
        if source == destination:
            return [source]
        
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_hops:
                continue
            
            # Find neighbors
            for (a, b), link in self.links.items():
                if a == current and link.status in [LinkStatus.ACTIVE, LinkStatus.DEGRADED]:
                    if b not in visited:
                        if b == destination:
                            return path + [b]
                        visited.add(b)
                        queue.append((b, path + [b]))
        
        return None
    
    def compute_route_latency(self, route: List[str]) -> float:
        """
        Compute total route latency.
        
        Args:
            route: List of node names
        
        Returns:
            Total latency in seconds
        """
        total = 0.0
        for i in range(len(route) - 1):
            key = (route[i], route[i+1])
            if key in self.links:
                total += self.links[key].latency_s
        return total
    
    def compute_route_capacity(self, route: List[str]) -> float:
        """
        Compute bottleneck capacity of route.
        
        Args:
            route: List of node names
        
        Returns:
            Minimum data rate along route (Mbps)
        """
        min_rate = float('inf')
        for i in range(len(route) - 1):
            key = (route[i], route[i+1])
            if key in self.links:
                min_rate = min(min_rate, self.links[key].data_rate_mbps)
        return min_rate if min_rate != float('inf') else 0.0
    
    def network_summary(self) -> Dict:
        """Get network summary."""
        active_links = sum(1 for l in self.links.values() if l.status == LinkStatus.ACTIVE)
        degraded_links = sum(1 for l in self.links.values() if l.status == LinkStatus.DEGRADED)
        offline_nodes = sum(1 for n in self.nodes.values() if not n.operational)
        
        return {
            "nodes": len(self.nodes),
            "links": len(self.links) // 2,  # Bidirectional counted once
            "active_links": active_links // 2,
            "degraded_links": degraded_links // 2,
            "offline_nodes": offline_nodes,
            "avg_data_rate_mbps": round(sum(l.data_rate_mbps for l in self.links.values()) / max(1, len(self.links)), 2)
        }
    
    def create_mars_relay_network(self) -> Dict[str, Node]:
        """Create a Mars relay network topology."""
        nodes = {
            "mro": Node("MRO", (0.0, 0.0, 400000.0), transmit_power_w=100.0,
                       antenna_gain_db=46.0, data_rate_mbps=6.0),
            "maven": Node("MAVEN", (200000.0, 0.0, 300000.0), transmit_power_w=35.0,
                         antenna_gain_db=30.0, data_rate_mbps=4.0),
            "msl": Node("MSL", (3396190.0, 0.0, 0.0), transmit_power_w=15.0,
                       antenna_gain_db=15.0, data_rate_mbps=0.5),
            "percy": Node("Perseverance", (3396190.0, 100000.0, 0.0), transmit_power_w=15.0,
                         antenna_gain_db=15.0, data_rate_mbps=0.5),
            "dsn_34": Node("DSN-34", (0.0, 1.5e11, 0.0), transmit_power_w=20000.0,
                          antenna_gain_db=74.0, data_rate_mbps=500.0),
            "dsn_70": Node("DSN-70", (0.0, -1.5e11, 0.0), transmit_power_w=20000.0,
                          antenna_gain_db=79.0, data_rate_mbps=500.0)
        }
        
        for node in nodes.values():
            self.add_node(node)
        
        return nodes
