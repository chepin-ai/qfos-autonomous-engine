"""
Unit tests for fault tolerance module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fault_tolerance import (NodeState, Vote, ConsensusResult,
                             ByzantineNode, ConsensusEngine,
                             FailoverManager, FaultTolerance)


class TestByzantineNode(unittest.TestCase):
    """Test Byzantine node."""
    
    def setUp(self):
        self.node = ByzantineNode("node1")
    
    def test_add_peer(self):
        """Should add peer."""
        self.node.add_peer("node2")
        self.assertIn("node2", self.node.peers)
        print("  [PASS] Peer: node2")
    
    def test_cast_vote(self):
        """Should cast vote."""
        vote = self.node.cast_vote("p1", "yes")
        self.assertEqual(vote.voter_id, "node1")
        self.assertEqual(vote.value, "yes")
        print("  [PASS] Vote: yes")
    
    def test_receive_vote(self):
        """Should receive vote."""
        vote = Vote("node2", "no")
        self.node.receive_vote("p1", vote)
        self.assertEqual(len(self.node.get_votes("p1")), 1)
        print("  [PASS] Receive: 1 vote")
    
    def test_mark_faulty(self):
        """Should mark faulty."""
        self.node.mark_faulty()
        self.assertEqual(self.node.state, NodeState.FAULTY)
        print("  [PASS] Faulty: marked")


class TestConsensusEngine(unittest.TestCase):
    """Test consensus engine."""
    
    def setUp(self):
        self.ce = ConsensusEngine(quorum_ratio=0.67)
        for i in range(4):
            self.ce.add_node(ByzantineNode(f"n{i}"))
    
    def test_add_node(self):
        """Should add nodes."""
        self.assertEqual(len(self.ce.nodes), 4)
        print("  [PASS] Nodes: 4")
    
    def test_propose(self):
        """Should propose."""
        result = self.ce.propose("p1", "value_a")
        self.assertTrue(result)
        print("  [PASS] Propose: ok")
    
    def test_vote(self):
        """Should record vote."""
        self.ce.propose("p1", "value_a")
        result = self.ce.vote("n0", "p1", "value_a")
        self.assertTrue(result)
        print("  [PASS] Vote: recorded")
    
    def test_tally_quorum(self):
        """Should reach quorum."""
        self.ce.propose("p1", "value_a")
        self.ce.vote("n0", "p1", "value_a")
        self.ce.vote("n1", "p1", "value_a")
        self.ce.vote("n2", "p1", "value_a")
        result = self.ce.tally("p1")
        self.assertTrue(result.quorum_reached)
        self.assertEqual(result.value, "value_a")
        print(f"  [PASS] Tally: quorum={result.quorum_reached}, val={result.value}")
    
    def test_tally_no_quorum(self):
        """Should not reach quorum."""
        self.ce.propose("p1", "value_a")
        self.ce.vote("n0", "p1", "value_a")
        result = self.ce.tally("p1")
        self.assertFalse(result.quorum_reached)
        print("  [PASS] No quorum: False")
    
    def test_max_faulty(self):
        """Should compute max faults."""
        max_f = self.ce.max_faulty_tolerated()
        self.assertEqual(max_f, 1)  # (4-1)//3 = 1
        print(f"  [PASS] Max faulty: {max_f}")


class TestFailoverManager(unittest.TestCase):
    """Test failover manager."""
    
    def setUp(self):
        self.fm = FailoverManager()
        self.fm.register_service("comms", "primary", ["backup1", "backup2"])
    
    def test_register(self):
        """Should register service."""
        self.assertIn("comms", self.fm.primaries)
        print("  [PASS] Register: comms")
    
    def test_get_active(self):
        """Should get active."""
        active = self.fm.get_active("comms")
        self.assertEqual(active, "primary")
        print(f"  [PASS] Active: {active}")
    
    def test_failover(self):
        """Should failover."""
        new_active = self.fm.failover("comms")
        self.assertIsNotNone(new_active)
        self.assertNotEqual(new_active, "primary")
        print(f"  [PASS] Failover: {new_active}")
    
    def test_check_health(self):
        """Should check health."""
        result = self.fm.check_health("comms")
        self.assertTrue(result)
        print("  [PASS] Health: ok")


class TestFaultTolerance(unittest.TestCase):
    """Test unified fault tolerance."""
    
    def setUp(self):
        self.ft = FaultTolerance()
        for i in range(4):
            self.ft.add_node(f"n{i}")
    
    def test_add_node(self):
        """Should add nodes."""
        self.assertEqual(len(self.ft.nodes), 4)
        print("  [PASS] Nodes: 4")
    
    def test_connect(self):
        """Should connect nodes."""
        self.ft.connect_nodes("n0", "n1")
        self.assertIn("n1", self.ft.nodes["n0"].peers)
        print("  [PASS] Connect: n0-n1")
    
    def test_run_consensus(self):
        """Should run consensus."""
        votes = {"n0": "yes", "n1": "yes", "n2": "yes", "n3": "no"}
        result = self.ft.run_consensus("p1", "yes", votes)
        self.assertTrue(result.quorum_reached)
        print(f"  [PASS] Consensus: {result.value}, quorum={result.quorum_reached}")
    
    def test_register_failover(self):
        """Should register failover."""
        self.ft.register_failover("svc", "p", ["b1", "b2"])
        self.assertIn("svc", self.ft.failover.active)
        print("  [PASS] Failover: registered")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.ft.ft_summary()
        self.assertEqual(summary["nodes"], 4)
        print(f"  [PASS] Summary: {summary['nodes']} nodes")


if __name__ == '__main__':
    unittest.main(verbosity=2)
