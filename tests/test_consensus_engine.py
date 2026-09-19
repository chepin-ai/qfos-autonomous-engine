"""
Unit tests for consensus engine module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consensus_engine import PBFTConsensus, RaftConsensus, Vote, ConsensusVote


class TestPBFTConsensus(unittest.TestCase):
    """Test PBFT consensus."""
    
    def setUp(self):
        self.node = PBFTConsensus("node_0", total_nodes=4)
    
    def test_propose(self):
        """Should create proposal."""
        prop = self.node.propose("p1", {"action": "burn"})
        self.assertEqual(prop.proposer, "node_0")
        print("  [PASS] Proposed: p1")
    
    def test_fault_tolerance(self):
        """Should compute fault tolerance."""
        self.assertEqual(self.node.fault_tolerance, 1)
        print(f"  [PASS] f = {self.node.fault_tolerance}")
    
    def test_vote(self):
        """Should cast vote."""
        self.node.propose("p1", "value")
        v = self.node.vote("p1", Vote.YES)
        self.assertIsNotNone(v)
        self.assertEqual(v.vote, Vote.YES)
        print("  [PASS] Vote: YES")
    
    def test_check_prepare(self):
        """Should detect prepare quorum."""
        self.node.propose("p1", "value")
        votes = [
            ConsensusVote("p1", "n0", Vote.YES),
            ConsensusVote("p1", "n1", Vote.YES),
            ConsensusVote("p1", "n2", Vote.YES)
        ]
        self.assertTrue(self.node.check_prepare("p1", votes))
        print("  [PASS] Prepare: quorum met")
    
    def test_check_commit(self):
        """Should detect commit quorum."""
        self.node.propose("p1", "value")
        votes = [
            ConsensusVote("p1", "n0", Vote.YES),
            ConsensusVote("p1", "n1", Vote.YES),
            ConsensusVote("p1", "n2", Vote.YES)
        ]
        self.assertTrue(self.node.check_commit("p1", votes))
        print("  [PASS] Commit: quorum met")
    
    def test_decide(self):
        """Should decide on proposal."""
        self.node.propose("p1", "committed_value")
        votes = [
            ConsensusVote("p1", "n0", Vote.YES),
            ConsensusVote("p1", "n1", Vote.YES),
            ConsensusVote("p1", "n2", Vote.YES)
        ]
        result = self.node.decide("p1", votes)
        self.assertEqual(result, "committed_value")
        print(f"  [PASS] Decided: {result}")
    
    def test_get_state(self):
        """Should get consensus state."""
        self.node.propose("p1", "value")
        self.node.vote("p1", Vote.YES)
        state = self.node.get_consensus_state("p1")
        self.assertIn("status", state)
        print(f"  [PASS] State: {state['status']}")
    
    def test_summary(self):
        """Should provide summary."""
        self.node.propose("p1", "v1")
        summary = self.node.consensus_summary()
        self.assertEqual(summary["total_nodes"], 4)
        print(f"  [PASS] Summary: {summary['proposals']} proposals")


class TestRaftConsensus(unittest.TestCase):
    """Test Raft consensus."""
    
    def setUp(self):
        self.node = RaftConsensus("node_0", ["node_0", "node_1", "node_2"])
    
    def test_request_vote(self):
        """Should handle vote request."""
        granted, term = self.node.request_vote(1, "node_1", -1, 0)
        self.assertTrue(granted)
        print("  [PASS] Vote granted")
    
    def test_request_vote_old_term(self):
        """Should reject old term."""
        self.node.term = 5
        granted, term = self.node.request_vote(1, "node_1", -1, 0)
        self.assertFalse(granted)
        print("  [PASS] Old term rejected")
    
    def test_become_candidate(self):
        """Should become candidate."""
        self.node.become_candidate()
        self.assertEqual(self.node.role, "candidate")
        self.assertEqual(self.node.term, 1)
        print("  [PASS] Candidate: term=1")
    
    def test_election_won(self):
        """Should detect election win."""
        self.node.become_candidate()
        self.node.votes_received = {"node_0", "node_1"}
        self.assertTrue(self.node.check_election_won())
        print("  [PASS] Election won")
    
    def test_append_entries(self):
        """Should append entries."""
        success, term = self.node.append_entries(
            1, "leader", -1, 0,
            [{"term": 1, "value": "cmd1"}], -1
        )
        self.assertTrue(success)
        self.assertEqual(len(self.node.log), 1)
        print("  [PASS] Appended: 1 entry")
    
    def test_log_summary(self):
        """Should provide log summary."""
        self.node.append_entries(1, "leader", -1, 0,
                                 [{"term": 1, "value": "cmd"}], -1)
        summary = self.node.get_log_summary()
        self.assertEqual(summary["log_length"], 1)
        print(f"  [PASS] Log: {summary['log_length']} entries")


if __name__ == '__main__':
    unittest.main(verbosity=2)
