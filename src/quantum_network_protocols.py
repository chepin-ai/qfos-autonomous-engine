"""
Quantum Network Protocols Module
Quantum internet, entanglement distribution,
quantum routing, repeater chains, and network stack for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field


@dataclass
class QuantumNode:
    """Node in quantum network."""
    id: str
    position: Tuple[float, float]
    memory_qubits: int = 1
    neighbors: List[str] = field(default_factory=list)


@dataclass
class EntanglementLink:
    """Entanglement link between nodes."""
    node_a: str
    node_b: str
    fidelity: float
    generation_rate_Hz: float


class EntanglementDistributor:
    """
    Distribute entanglement across network.
    """
    
    def __init__(self, attenuation_dB_km: float = 0.2):
        """
        Args:
            attenuation_dB_km: Fiber attenuation
        """
        self.attenuation = attenuation_dB_km
    
    def link_fidelity(self, distance_km: float,
                     initial_fidelity: float = 0.99) -> float:
        """
        Compute link fidelity after transmission.
        
        Args:
            distance_km: Distance
            initial_fidelity: Initial fidelity
        
        Returns:
            Fidelity
        """
        # Simplified: fidelity degrades with distance
        loss = self.attenuation * distance_km
        return initial_fidelity * (10.0 ** (-loss / 10.0))
    
    def success_probability(self, distance_km: float) -> float:
        """
        Compute entanglement generation success probability.
        
        Args:
            distance_km: Distance
        
        Returns:
            Success probability
        """
        loss_dB = self.attenuation * distance_km
        return 10.0 ** (-loss_dB / 10.0)
    
    def generate_link(self, node_a: QuantumNode,
                     node_b: QuantumNode) -> Optional[EntanglementLink]:
        """
        Generate entanglement link between nodes.
        
        Args:
            node_a: Node A
            node_b: Node B
        
        Returns:
            Link or None
        """
        dx = node_a.position[0] - node_b.position[0]
        dy = node_a.position[1] - node_b.position[1]
        dist = math.sqrt(dx ** 2 + dy ** 2)
        
        fid = self.link_fidelity(dist)
        prob = self.success_probability(dist)
        rate = 1e6 * prob  # 1 MHz source rate
        
        if random.random() < prob:
            return EntanglementLink(node_a.id, node_b.id, fid, rate)
        return None


class QuantumRepeater:
    """
    Quantum repeater for extending entanglement range.
    """
    
    def __init__(self):
        self.entanglement_pairs: Dict[str, Tuple[str, float]] = {}
    
    def store_pair(self, pair_id: str, node_id: str,
                  fidelity: float):
        """
        Store entangled pair.
        
        Args:
            pair_id: Pair ID
            node_id: Node ID
            fidelity: Fidelity
        """
        self.entanglement_pairs[pair_id] = (node_id, fidelity)
    
    def entanglement_swap(self, pair_a: Tuple[str, float],
                         pair_b: Tuple[str, float]) -> float:
        """
        Perform entanglement swapping.
        
        Args:
            pair_a: (node_id, fidelity)
            pair_b: (node_id, fidelity)
        
        Returns:
            Resulting fidelity
        """
        fid_a = pair_a[1]
        fid_b = pair_b[1]
        # Fidelity after swapping
        return fid_a * fid_b
    
    def purify(self, fidelity1: float,
              fidelity2: float) -> float:
        """
        Entanglement purification.
        
        Args:
            fidelity1: Fidelity of first pair
            fidelity2: Fidelity of second pair
        
        Returns:
            Purified fidelity
        """
        # Simplified DEJMPS-like purification
        return (fidelity1 * fidelity2) / (fidelity1 * fidelity2 + (1.0 - fidelity1) * (1.0 - fidelity2))


class QuantumRouter:
    """
    Quantum network routing.
    """
    
    def __init__(self):
        self.nodes: Dict[str, QuantumNode] = {}
        self.links: Dict[Tuple[str, str], EntanglementLink] = {}
    
    def add_node(self, node: QuantumNode):
        """
        Add node to network.
        
        Args:
            node: Node
        """
        self.nodes[node.id] = node
    
    def add_link(self, link: EntanglementLink):
        """
        Add link to network.
        
        Args:
            link: Link
        """
        self.links[(link.node_a, link.node_b)] = link
        self.links[(link.node_b, link.node_a)] = link
    
    def shortest_path(self, source: str,
                     target: str) -> List[str]:
        """
        Find shortest path between nodes.
        
        Args:
            source: Source node
            target: Target node
        
        Returns:
            Path
        """
        if source not in self.nodes or target not in self.nodes:
            return []
        
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            if current == target:
                return path
            
            node = self.nodes[current]
            for neighbor in node.neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def path_fidelity(self, path: List[str]) -> float:
        """
        Compute end-to-end fidelity for path.
        
        Args:
            path: Node path
        
        Returns:
            Fidelity
        """
        if len(path) < 2:
            return 0.0
        
        min_fid = 1.0
        for i in range(len(path) - 1):
            key = (path[i], path[i + 1])
            if key in self.links:
                min_fid = min(min_fid, self.links[key].fidelity)
        
        return min_fid


class QuantumNetworkStack:
    """
    Quantum network protocol stack.
    """
    
    def __init__(self):
        self.distributor = EntanglementDistributor()
        self.repeater = QuantumRepeater()
        self.router = QuantumRouter()
    
    def establish_connection(self, source: str,
                            target: str) -> Dict:
        """
        Establish quantum connection.
        
        Args:
            source: Source node
            target: Target node
        
        Returns:
            Connection info
        """
        path = self.router.shortest_path(source, target)
        if not path:
            return {"status": "failed", "reason": "no_path"}
        
        fidelity = self.router.path_fidelity(path)
        
        return {
            "status": "established",
            "path": path,
            "hops": len(path) - 1,
            "fidelity": fidelity
        }
    
    def network_summary(self) -> Dict:
        """Get summary."""
        return {
            "nodes": len(self.router.nodes),
            "links": len(self.router.links) // 2,
            "protocols": ["entanglement_distribution", "repeater", "routing"]
        }


class QuantumNetworkProtocols:
    """
    Unified quantum network protocols controller.
    """
    
    def __init__(self):
        self.stack = QuantumNetworkStack()
    
    def qnp_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["entanglement_distribution", "repeater", "routing", "purification"],
            "layers": ["physical", "link", "network"]
        }
