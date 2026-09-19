"""
Consensus Engine Module
Distributed consensus algorithms with Byzantine fault
tolerance for federated decision-making.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Vote(Enum):
    """Consensus vote values."""
    YES = 1
    NO = 0
    ABSTAIN = -1


@dataclass
class ConsensusProposal:
    """A proposal for consensus."""
    id: str
    value: Any
    proposer: str
    round_number: int = 0
    timestamp: float = 0.0


@dataclass
class ConsensusVote:
    """A vote on a proposal."""
    proposal_id: str
    voter_id: str
    vote: Vote
    round_number: int = 0


class PBFTConsensus:
    """
    Practical Byzantine Fault Tolerance consensus.
    
    Tolerates up to f faulty nodes out of 3f+1 total nodes.
    Phases: request, pre-prepare, prepare, commit, reply.
    """
    
    def __init__(self, node_id: str, total_nodes: int):
        """
        Args:
            node_id: This node's ID
            total_nodes: Total nodes in network
        """
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.fault_tolerance = (total_nodes - 1) // 3
        self.proposals: Dict[str, ConsensusProposal] = {}
        self.votes: Dict[str, List[ConsensusVote]] = {}
        self.decided: Dict[str, Any] = {}
    
    def propose(self, proposal_id: str, value: Any) -> ConsensusProposal:
        """
        Create a new proposal.
        
        Args:
            proposal_id: Unique proposal ID
            value: Proposal value
        
        Returns:
            Created proposal
        """
        import time
        proposal = ConsensusProposal(
            id=proposal_id,
            value=value,
            proposer=self.node_id,
            round_number=0,
            timestamp=time.time()
        )
        self.proposals[proposal_id] = proposal
        self.votes[proposal_id] = []
        return proposal
    
    def vote(self, proposal_id: str, vote: Vote,
            round_number: int = 0) -> Optional[ConsensusVote]:
        """
        Cast a vote on a proposal.
        
        Args:
            proposal_id: Proposal to vote on
            vote: Vote value
            round_number: Consensus round
        
        Returns:
            Vote or None if proposal unknown
        """
        if proposal_id not in self.proposals:
            return None
        
        v = ConsensusVote(
            proposal_id=proposal_id,
            voter_id=self.node_id,
            vote=vote,
            round_number=round_number
        )
        self.votes[proposal_id].append(v)
        return v
    
    def check_prepare(self, proposal_id: str,
                     received_votes: List[ConsensusVote]) -> bool:
        """
        Check if prepare quorum reached (2f votes).
        
        Args:
            proposal_id: Proposal ID
            received_votes: All received votes
        
        Returns:
            True if prepare quorum met
        """
        if proposal_id not in self.proposals:
            return False
        
        valid = [v for v in received_votes
                if v.proposal_id == proposal_id and v.vote == Vote.YES]
        
        # Need 2f votes (including self)
        return len(valid) >= 2 * self.fault_tolerance
    
    def check_commit(self, proposal_id: str,
                    received_votes: List[ConsensusVote]) -> bool:
        """
        Check if commit quorum reached (2f+1 votes).
        
        Args:
            proposal_id: Proposal ID
            received_votes: All received votes
        
        Returns:
            True if commit quorum met
        """
        if proposal_id not in self.proposals:
            return False
        
        valid = [v for v in received_votes
                if v.proposal_id == proposal_id and v.vote == Vote.YES]
        
        # Need 2f+1 votes for commit
        return len(valid) >= 2 * self.fault_tolerance + 1
    
    def decide(self, proposal_id: str,
               commit_votes: List[ConsensusVote]) -> Optional[Any]:
        """
        Decide on proposal if commit reached.
        
        Args:
            proposal_id: Proposal ID
            commit_votes: Commit-phase votes
        
        Returns:
            Decided value or None
        """
        if not self.check_commit(proposal_id, commit_votes):
            return None
        
        if proposal_id in self.decided:
            return self.decided[proposal_id]
        
        value = self.proposals[proposal_id].value
        self.decided[proposal_id] = value
        return value
    
    def get_consensus_state(self, proposal_id: str) -> Dict:
        """
        Get consensus state for proposal.
        
        Args:
            proposal_id: Proposal ID
        
        Returns:
            State dict
        """
        if proposal_id not in self.proposals:
            return {"status": "unknown"}
        
        votes = self.votes.get(proposal_id, [])
        yes_count = sum(1 for v in votes if v.vote == Vote.YES)
        no_count = sum(1 for v in votes if v.vote == Vote.NO)
        
        status = "pending"
        if proposal_id in self.decided:
            status = "decided"
        elif self.check_prepare(proposal_id, votes):
            status = "prepared"
        
        return {
            "status": status,
            "total_votes": len(votes),
            "yes": yes_count,
            "no": no_count,
            "quorum_needed": 2 * self.fault_tolerance + 1,
            "fault_tolerance": self.fault_tolerance
        }
    
    def consensus_summary(self) -> Dict:
        """Get summary of all consensus rounds."""
        return {
            "total_nodes": self.total_nodes,
            "fault_tolerance": self.fault_tolerance,
            "proposals": len(self.proposals),
            "decided": len(self.decided),
            "pending": len(self.proposals) - len(self.decided)
        }


class RaftConsensus:
    """
    Raft consensus for leader-based log replication.
    
    Simplified version with leader election and log commit.
    """
    
    def __init__(self, node_id: str, node_ids: List[str]):
        """
        Args:
            node_id: This node's ID
            node_ids: All node IDs
        """
        self.node_id = node_id
        self.node_ids = node_ids
        self.term = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict] = []
        self.commit_index = -1
        self.role = "follower"  # follower, candidate, leader
        self.leader_id: Optional[str] = None
        self.votes_received: set = set()
    
    def request_vote(self, term: int, candidate_id: str,
                    last_log_index: int, last_log_term: int) -> Tuple[bool, int]:
        """
        Handle vote request.
        
        Args:
            term: Candidate's term
            candidate_id: Candidate ID
            last_log_index: Candidate's last log index
            last_log_term: Candidate's last log term
        
        Returns:
            (vote_granted, current_term)
        """
        if term < self.term:
            return False, self.term
        
        if term > self.term:
            self.term = term
            self.voted_for = None
            self.role = "follower"
        
        if self.voted_for is None or self.voted_for == candidate_id:
            # Check log is at least as up-to-date
            my_last_index = len(self.log) - 1
            my_last_term = self.log[my_last_index]["term"] if self.log else 0
            
            if last_log_term > my_last_term or \
               (last_log_term == my_last_term and last_log_index >= my_last_index):
                self.voted_for = candidate_id
                return True, self.term
        
        return False, self.term
    
    def become_candidate(self):
        """Transition to candidate state."""
        self.term += 1
        self.role = "candidate"
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
    
    def check_election_won(self) -> bool:
        """Check if election won (majority)."""
        return len(self.votes_received) > len(self.node_ids) // 2
    
    def append_entries(self, term: int, leader_id: str,
                      prev_log_index: int, prev_log_term: int,
                      entries: List[Dict], leader_commit: int) -> Tuple[bool, int]:
        """
        Handle append entries (heartbeat or log replication).
        
        Args:
            term: Leader's term
            leader_id: Leader ID
            prev_log_index: Previous log index
            prev_log_term: Previous log term
            entries: Entries to append
            leader_commit: Leader's commit index
        
        Returns:
            (success, current_term)
        """
        if term < self.term:
            return False, self.term
        
        self.leader_id = leader_id
        self.role = "follower"
        
        if term > self.term:
            self.term = term
            self.voted_for = None
        
        # Check log consistency
        if prev_log_index >= 0:
            if prev_log_index >= len(self.log):
                return False, self.term
            if self.log[prev_log_index]["term"] != prev_log_term:
                return False, self.term
        
        # Append entries
        for i, entry in enumerate(entries):
            idx = prev_log_index + 1 + i
            if idx < len(self.log):
                if self.log[idx]["term"] != entry["term"]:
                    # Conflict: truncate
                    self.log = self.log[:idx]
                    self.log.append(entry)
            else:
                self.log.append(entry)
        
        # Update commit index
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log) - 1)
        
        return True, self.term
    
    def get_log_summary(self) -> Dict:
        """Get log replication summary."""
        return {
            "term": self.term,
            "role": self.role,
            "leader": self.leader_id,
            "log_length": len(self.log),
            "commit_index": self.commit_index,
            "entries_committed": self.commit_index + 1
        }
