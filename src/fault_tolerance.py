"""
Fault Tolerance Module
Byzantine fault tolerance, consensus voting, and failover
for spacecraft distributed systems.
"""

import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter


class NodeState(Enum):
    """State of a distributed node."""
    HEALTHY = "healthy"
    SUSPECTED = "suspected"
    FAULTY = "faulty"
    RECOVERING = "recovering"


@dataclass
class Vote:
    """A consensus vote."""
    voter_id: str
    value: Any
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class ConsensusResult:
    """Result of consensus voting."""
    value: Any
    votes_for: int
    votes_against: int
    total_votes: int
    is_decided: bool
    quorum_reached: bool


class ByzantineNode:
    """
    A node in the Byzantine fault-tolerant network.
    """
    
    def __init__(self, node_id: str):
        """
        Args:
            node_id: Unique node identifier
        """
        self.node_id = node_id
        self.state = NodeState.HEALTHY
        self.peers: List[str] = []
        self.votes_cast: Dict[str, Vote] = {}
        self.votes_received: Dict[str, List[Vote]] = {}
    
    def add_peer(self, peer_id: str):
        """Add peer node."""
        if peer_id not in self.peers and peer_id != self.node_id:
            self.peers.append(peer_id)
    
    def cast_vote(self, proposal_id: str, value: Any) -> Vote:
        """
        Cast vote on proposal.
        
        Args:
            proposal_id: Proposal identifier
            value: Vote value
        
        Returns:
            Vote object
        """
        vote = Vote(voter_id=self.node_id, value=value)
        self.votes_cast[proposal_id] = vote
        return vote
    
    def receive_vote(self, proposal_id: str, vote: Vote):
        """Receive vote from peer."""
        if proposal_id not in self.votes_received:
            self.votes_received[proposal_id] = []
        self.votes_received[proposal_id].append(vote)
    
    def get_votes(self, proposal_id: str) -> List[Vote]:
        """Get all votes for proposal."""
        return self.votes_received.get(proposal_id, [])
    
    def mark_suspected(self):
        """Mark node as suspected faulty."""
        self.state = NodeState.SUSPECTED
    
    def mark_faulty(self):
        """Mark node as faulty."""
        self.state = NodeState.FAULTY
    
    def mark_healthy(self):
        """Mark node as healthy."""
        self.state = NodeState.HEALTHY


class ConsensusEngine:
    """
    Byzantine fault-tolerant consensus engine.
    
    Requires 3f+1 nodes to tolerate f Byzantine faults.
    """
    
    def __init__(self, quorum_ratio: float = 0.67):
        """
        Args:
            quorum_ratio: Fraction needed for quorum (default 2/3)
        """
        self.quorum_ratio = quorum_ratio
        self.nodes: Dict[str, ByzantineNode] = {}
        self.proposals: Dict[str, Dict] = {}
    
    def add_node(self, node: ByzantineNode):
        """Add node to consensus group."""
        self.nodes[node.node_id] = node
    
    def propose(self, proposal_id: str, proposed_value: Any) -> bool:
        """
        Submit proposal for consensus.
        
        Args:
            proposal_id: Proposal identifier
            proposed_value: Value to agree on
        
        Returns:
            True if proposal accepted
        """
        if proposal_id in self.proposals:
            return False
        
        self.proposals[proposal_id] = {
            "value": proposed_value,
            "votes": {},
            "phase": "voting",
            "start_time": time.time()
        }
        return True
    
    def vote(self, node_id: str, proposal_id: str, value: Any) -> bool:
        """
        Cast vote from node.
        
        Args:
            node_id: Voting node
            proposal_id: Proposal ID
            value: Vote value
        
        Returns:
            True if vote recorded
        """
        if node_id not in self.nodes:
            return False
        if proposal_id not in self.proposals:
            return False
        if self.nodes[node_id].state == NodeState.FAULTY:
            return False
        
        vote = self.nodes[node_id].cast_vote(proposal_id, value)
        
        # Distribute to all peers
        for peer_id, peer in self.nodes.items():
            if peer_id != node_id:
                peer.receive_vote(proposal_id, vote)
        
        self.proposals[proposal_id]["votes"][node_id] = vote
        return True
    
    def tally(self, proposal_id: str) -> ConsensusResult:
        """
        Tally votes for proposal.
        
        Args:
            proposal_id: Proposal ID
        
        Returns:
            Consensus result
        """
        if proposal_id not in self.proposals:
            return ConsensusResult(None, 0, 0, 0, False, False)
        
        healthy_nodes = [n for n in self.nodes.values()
                        if n.state != NodeState.FAULTY]
        total_healthy = len(healthy_nodes)
        
        votes = list(self.proposals[proposal_id]["votes"].values())
        values = [v.value for v in votes]
        
        if not values:
            return ConsensusResult(None, 0, 0, 0, False, False)
        
        counter = Counter(values)
        most_common = counter.most_common(1)[0]
        winner_value = most_common[0]
        winner_count = most_common[1]
        
        quorum_needed = max(1, int(total_healthy * self.quorum_ratio))
        quorum_reached = winner_count >= quorum_needed
        
        return ConsensusResult(
            value=winner_value,
            votes_for=winner_count,
            votes_against=sum(counter.values()) - winner_count,
            total_votes=len(votes),
            is_decided=quorum_reached,
            quorum_reached=quorum_reached
        )
    
    def max_faulty_tolerated(self) -> int:
        """Maximum Byzantine faults tolerated."""
        n = len(self.nodes)
        return (n - 1) // 3


class FailoverManager:
    """
    Manage failover between primary and backup components.
    """
    
    def __init__(self):
        self.primaries: Dict[str, str] = {}  # service -> primary node
        self.backups: Dict[str, List[str]] = {}  # service -> backup nodes
        self.active: Dict[str, str] = {}  # service -> currently active node
        self.health_checks: Dict[str, Callable[[], bool]] = {}
    
    def register_service(self, service: str, primary: str,
                        backups: List[str]):
        """Register service with failover config."""
        self.primaries[service] = primary
        self.backups[service] = backups
        self.active[service] = primary
    
    def register_health_check(self, service: str,
                             check_fn: Callable[[], bool]):
        """Register health check function."""
        self.health_checks[service] = check_fn
    
    def check_health(self, service: str) -> bool:
        """Check service health."""
        if service in self.health_checks:
            return self.health_checks[service]()
        return True
    
    def failover(self, service: str) -> Optional[str]:
        """
        Failover service to backup.
        
        Args:
            service: Service name
        
        Returns:
            New active node or None
        """
        if service not in self.backups:
            return None
        
        current = self.active.get(service)
        backups = self.backups[service]
        
        # Try each backup in order
        for backup in backups:
            if backup != current:
                self.active[service] = backup
                return backup
        
        return None
    
    def get_active(self, service: str) -> Optional[str]:
        """Get currently active node for service."""
        return self.active.get(service)
    
    def restore_primary(self, service: str) -> bool:
        """Restore primary if healthy."""
        if service not in self.primaries:
            return False
        
        primary = self.primaries[service]
        if self.check_health(service):
            self.active[service] = primary
            return True
        return False


class FaultTolerance:
    """
    Unified fault tolerance controller.
    """
    
    def __init__(self):
        self.consensus = ConsensusEngine()
        self.failover = FailoverManager()
        self.nodes: Dict[str, ByzantineNode] = {}
    
    def add_node(self, node_id: str):
        """Add node to fault-tolerant group."""
        node = ByzantineNode(node_id)
        self.nodes[node_id] = node
        self.consensus.add_node(node)
    
    def connect_nodes(self, node_a: str, node_b: str):
        """Connect two nodes as peers."""
        if node_a in self.nodes and node_b in self.nodes:
            self.nodes[node_a].add_peer(node_b)
            self.nodes[node_b].add_peer(node_a)
    
    def run_consensus(self, proposal_id: str, proposed_value: Any,
                     votes: Dict[str, Any]) -> ConsensusResult:
        """
        Run full consensus round.
        
        Args:
            proposal_id: Proposal ID
            proposed_value: Proposed value
            votes: Node votes
        
        Returns:
            Consensus result
        """
        self.consensus.propose(proposal_id, proposed_value)
        
        for node_id, value in votes.items():
            self.consensus.vote(node_id, proposal_id, value)
        
        return self.consensus.tally(proposal_id)
    
    def register_failover(self, service: str, primary: str,
                         backups: List[str]):
        """Register failover service."""
        self.failover.register_service(service, primary, backups)
    
    def ft_summary(self) -> Dict:
        """Get fault tolerance summary."""
        return {
            "nodes": len(self.nodes),
            "max_faulty": self.consensus.max_faulty_tolerated(),
            "services": list(self.failover.active.keys()),
            "proposals": len(self.consensus.proposals)
        }
