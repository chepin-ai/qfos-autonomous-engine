"""
Data Relay Module
Store-and-forward relay, priority queuing, latency optimization,
and delay-tolerant networking (DTN) bundle protocol simulation.
"""

import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    """Bundle priority levels."""
    CRITICAL = 0
    PRIORITY = 1
    STANDARD = 2
    BULK = 3


class BundleStatus(Enum):
    """Bundle lifecycle status."""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    EXPIRED = "expired"
    DROPPED = "dropped"


@dataclass
class Bundle:
    """A DTN bundle."""
    bundle_id: str
    source: str
    destination: str
    payload_bytes: int
    priority: Priority = Priority.STANDARD
    created_timestamp: float = field(default_factory=time.time)
    expiry_timestamp: float = 0.0
    status: BundleStatus = BundleStatus.PENDING
    custody: bool = False
    ack_requested: bool = False
    fragment_offset: int = 0
    fragment_length: int = 0
    route: List[str] = field(default_factory=list)
    current_hop: int = 0
    transmission_count: int = 0
    max_transmissions: int = 3
    custody_chain: List[str] = field(default_factory=list)


@dataclass
class Contact:
    """A scheduled contact window between nodes."""
    node_a: str
    node_b: str
    start_time: float
    end_time: float
    data_rate_bps: float
    total_capacity_bits: float = 0.0
    used_capacity_bits: float = 0.0


class BundleRouter:
    """
    DTN bundle router with store-and-forward.
    
    Manages bundle queueing, routing, and delivery
    over intermittent links.
    """
    
    def __init__(self):
        self.bundles: Dict[str, Bundle] = {}
        self.queues: Dict[str, List[str]] = {}  # node -> list of bundle_ids
        self.contacts: List[Contact] = []
        self.delivered: List[str] = []
        self.dropped: List[str] = []
        self._bundle_counter = 0
    
    def create_bundle(self, source: str, destination: str,
                      payload_bytes: int, priority: Priority = Priority.STANDARD,
                      ttl_hours: float = 24.0) -> Bundle:
        """
        Create a new bundle.
        
        Args:
            source: Source node
            destination: Destination node
            payload_bytes: Payload size
            priority: Bundle priority
            ttl_hours: Time-to-live
        
        Returns:
            Created bundle
        """
        now = time.time()
        self._bundle_counter += 1
        bundle_id = f"{source}_{destination}_{int(now*1000)}_{self._bundle_counter}"
        
        bundle = Bundle(
            bundle_id=bundle_id,
            source=source,
            destination=destination,
            payload_bytes=payload_bytes,
            priority=priority,
            created_timestamp=now,
            expiry_timestamp=now + ttl_hours * 3600.0
        )
        
        self.bundles[bundle_id] = bundle
        
        if source not in self.queues:
            self.queues[source] = []
        self.queues[source].append(bundle_id)
        
        return bundle
    
    def add_contact(self, contact: Contact):
        """Add a contact window."""
        contact.total_capacity_bits = (contact.end_time - contact.start_time) * contact.data_rate_bps
        self.contacts.append(contact)
    
    def get_queue(self, node: str) -> List[Bundle]:
        """
        Get sorted bundle queue for a node.
        
        Sorted by priority then creation time.
        """
        if node not in self.queues:
            return []
        
        bundles = [self.bundles[bid] for bid in self.queues[node]
                  if bid in self.bundles]
        bundles.sort(key=lambda b: (b.priority.value, b.created_timestamp))
        return bundles
    
    def forward_bundle(self, bundle_id: str, from_node: str,
                       to_node: str, route: List[str]) -> bool:
        """
        Forward bundle to next hop.
        
        Args:
            bundle_id: Bundle ID
            from_node: Current node
            to_node: Next hop
            route: Full route
        
        Returns:
            Success
        """
        if bundle_id not in self.bundles:
            return False
        
        bundle = self.bundles[bundle_id]
        bundle.transmission_count += 1
        bundle.route = route
        
        # Move from one queue to another
        if from_node in self.queues and bundle_id in self.queues[from_node]:
            self.queues[from_node].remove(bundle_id)
        
        if to_node not in self.queues:
            self.queues[to_node] = []
        self.queues[to_node].append(bundle_id)
        
        bundle.current_hop += 1
        bundle.status = BundleStatus.IN_TRANSIT
        
        return True
    
    def deliver_bundle(self, bundle_id: str) -> bool:
        """
        Mark bundle as delivered.
        
        Args:
            bundle_id: Bundle ID
        
        Returns:
            Success
        """
        if bundle_id not in self.bundles:
            return False
        
        bundle = self.bundles[bundle_id]
        bundle.status = BundleStatus.DELIVERED
        
        # Remove from queues
        for node, queue in self.queues.items():
            if bundle_id in queue:
                queue.remove(bundle_id)
        
        self.delivered.append(bundle_id)
        return True
    
    def process_expired(self) -> List[str]:
        """
        Process expired bundles.
        
        Returns:
            List of expired bundle IDs
        """
        now = time.time()
        expired = []
        
        for bid, bundle in self.bundles.items():
            if bundle.status in [BundleStatus.PENDING, BundleStatus.IN_TRANSIT]:
                if now > bundle.expiry_timestamp:
                    bundle.status = BundleStatus.EXPIRED
                    expired.append(bid)
                    
                    for queue in self.queues.values():
                        if bid in queue:
                            queue.remove(bid)
        
        return expired
    
    def simulate_contact(self, contact: Contact) -> Dict:
        """
        Simulate data transfer during a contact.
        
        Args:
            contact: Contact window
        
        Returns:
            Transfer results
        """
        available_bits = contact.total_capacity_bits - contact.used_capacity_bits
        transferred = 0
        bundles_sent = 0
        
        queue = self.get_queue(contact.node_a)
        
        for bundle in queue:
            if bundle.destination == contact.node_b:
                # Direct delivery
                bundle_size_bits = bundle.payload_bytes * 8
                
                if transferred + bundle_size_bits <= available_bits:
                    self.deliver_bundle(bundle.bundle_id)
                    transferred += bundle_size_bits
                    bundles_sent += 1
                else:
                    break
            else:
                # Forward to next hop
                bundle_size_bits = bundle.payload_bytes * 8
                
                if transferred + bundle_size_bits <= available_bits:
                    # Simple: forward to contact node
                    self.forward_bundle(bundle.bundle_id, contact.node_a,
                                       contact.node_b, [contact.node_a, contact.node_b])
                    transferred += bundle_size_bits
                    bundles_sent += 1
                else:
                    break
        
        contact.used_capacity_bits += transferred
        
        return {
            "contact": f"{contact.node_a}->{contact.node_b}",
            "duration_s": round(contact.end_time - contact.start_time, 1),
            "transferred_bits": transferred,
            "bundles_sent": bundles_sent,
            "capacity_utilization": round(transferred / contact.total_capacity_bits, 3) if contact.total_capacity_bits > 0 else 0.0
        }
    
    def network_stats(self) -> Dict:
        """Get relay network statistics."""
        pending = sum(1 for b in self.bundles.values() if b.status == BundleStatus.PENDING)
        in_transit = sum(1 for b in self.bundles.values() if b.status == BundleStatus.IN_TRANSIT)
        delivered = len(self.delivered)
        expired = sum(1 for b in self.bundles.values() if b.status == BundleStatus.EXPIRED)
        
        total_bytes = sum(b.payload_bytes for b in self.bundles.values())
        delivered_bytes = sum(self.bundles[bid].payload_bytes for bid in self.delivered
                             if bid in self.bundles)
        
        return {
            "total_bundles": len(self.bundles),
            "pending": pending,
            "in_transit": in_transit,
            "delivered": delivered,
            "expired": expired,
            "delivery_rate": round(delivered / max(1, len(self.bundles)), 3),
            "total_bytes": total_bytes,
            "delivered_bytes": delivered_bytes,
            "throughput_efficiency": round(delivered_bytes / max(1, total_bytes), 3)
        }
    
    def latency_estimate(self, bundle_id: str,
                        route: Optional[List[str]] = None) -> float:
        """
        Estimate delivery latency for a bundle.
        
        Args:
            bundle_id: Bundle ID
            route: Route (uses bundle's route if None)
        
        Returns:
            Estimated latency in seconds
        """
        if bundle_id not in self.bundles:
            return -1.0
        
        bundle = self.bundles[bundle_id]
        r = route or bundle.route
        
        if not r:
            return -1.0
        
        # Sum contact latencies (simplified)
        latency = 0.0
        for i in range(len(r) - 1):
            # Find contact between hops
            for contact in self.contacts:
                if (contact.node_a == r[i] and contact.node_b == r[i+1]) or \
                   (contact.node_a == r[i+1] and contact.node_b == r[i]):
                    latency += (contact.end_time - contact.start_time) * 0.5
                    break
        
        return latency
