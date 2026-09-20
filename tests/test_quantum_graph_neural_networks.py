"""
Unit tests for quantum graph neural networks module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_graph_neural_networks import (GraphNode, QuantumGraphConvolution,
                                            QuantumMessagePassing,
                                            QuantumGraphAttention,
                                            QuantumGraphNeuralNetworks)


class TestQuantumGraphConvolution(unittest.TestCase):
    """Test graph convolution."""
    
    def setUp(self):
        self.conv = QuantumGraphConvolution(4, 4)
    
    def test_aggregate(self):
        """Should aggregate."""
        nodes = {
            0: GraphNode(0, [1.0, 0.0, 0.0, 0.0], [1]),
            1: GraphNode(1, [0.0, 1.0, 0.0, 0.0], [0])
        }
        agg = self.conv.aggregate(nodes[0], nodes)
        self.assertEqual(len(agg), 4)
        print(f"  [PASS] Agg: {agg}")
    
    def test_transform(self):
        """Should transform."""
        out = self.conv.transform([1.0, 0.0, 0.0, 0.0])
        self.assertEqual(len(out), 4)
        print(f"  [PASS] Trans: {out}")
    
    def test_forward(self):
        """Should forward."""
        nodes = {
            0: GraphNode(0, [1.0, 0.0, 0.0, 0.0], [1]),
            1: GraphNode(1, [0.0, 1.0, 0.0, 0.0], [0])
        }
        out = self.conv.forward(nodes[0], nodes)
        self.assertEqual(len(out), 4)
        print("  [PASS] Forward")


class TestQuantumMessagePassing(unittest.TestCase):
    """Test message passing."""
    
    def setUp(self):
        self.mp = QuantumMessagePassing(4)
    
    def test_message(self):
        """Should compute message."""
        s = GraphNode(0, [1.0, 0.5, 0.0, 0.0], [])
        r = GraphNode(1, [0.5, 1.0, 0.0, 0.0], [])
        m = self.mp.message(s, r)
        self.assertEqual(len(m), 4)
        print(f"  [PASS] Msg: {m}")
    
    def test_update(self):
        """Should update."""
        n = GraphNode(0, [1.0, 0.0, 0.0, 0.0], [])
        u = self.mp.update(n, [[0.5, 0.5, 0.0, 0.0]])
        self.assertEqual(len(u), 4)
        print(f"  [PASS] Upd: {u}")
    
    def test_pass(self):
        """Should pass messages."""
        nodes = {
            0: GraphNode(0, [1.0, 0.0, 0.0, 0.0], [1]),
            1: GraphNode(1, [0.0, 1.0, 0.0, 0.0], [0])
        }
        updated = self.mp.pass_messages(nodes)
        self.assertIn(0, updated)
        self.assertIn(1, updated)
        print("  [PASS] Pass")


class TestQuantumGraphAttention(unittest.TestCase):
    """Test graph attention."""
    
    def setUp(self):
        self.attn = QuantumGraphAttention(4)
    
    def test_score(self):
        """Should compute attention score."""
        s = self.attn.attention_score([1.0, 0.0, 0.0, 0.0],
                                       [0.5, 0.5, 0.0, 0.0])
        self.assertGreaterEqual(s, 0.0)
        print(f"  [PASS] Score: {s:.4f}")
    
    def test_attend(self):
        """Should attend."""
        nodes = {
            0: GraphNode(0, [1.0, 0.0, 0.0, 0.0], [1]),
            1: GraphNode(1, [0.0, 1.0, 0.0, 0.0], [0])
        }
        out = self.attn.attend(nodes[0], nodes)
        self.assertEqual(len(out), 4)
        print("  [PASS] Attend")


class TestQuantumGraphNeuralNetworks(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgnn = QuantumGraphNeuralNetworks()
    
    def test_build(self):
        """Should build graph."""
        edges = [(0, 1), (1, 2)]
        features = {0: [1.0, 0.0, 0.0, 0.0],
                    1: [0.0, 1.0, 0.0, 0.0],
                    2: [0.0, 0.0, 1.0, 0.0]}
        self.qgnn.build_graph(edges, features)
        self.assertEqual(len(self.qgnn.nodes), 3)
        print("  [PASS] Build")
    
    def test_embed(self):
        """Should embed."""
        edges = [(0, 1), (1, 2)]
        features = {0: [1.0, 0.0, 0.0, 0.0],
                    1: [0.0, 1.0, 0.0, 0.0],
                    2: [0.0, 0.0, 1.0, 0.0]}
        self.qgnn.build_graph(edges, features)
        emb = self.qgnn.embed(2)
        self.assertEqual(len(emb), 3)
        print("  [PASS] Embed")
    
    def test_predict(self):
        """Should predict."""
        edges = [(0, 1)]
        features = {0: [1.0, 0.0, 0.0, 0.0],
                    1: [0.0, -1.0, 0.0, 0.0]}
        self.qgnn.build_graph(edges, features)
        self.qgnn.embed(1)
        p = self.qgnn.predict(0)
        self.assertIn(p, [0, 1])
        print(f"  [PASS] Pred: {p}")
    
    def test_summary(self):
        """Should summarize."""
        edges = [(0, 1)]
        features = {0: [1.0, 0.0, 0.0, 0.0],
                    1: [0.0, 1.0, 0.0, 0.0]}
        self.qgnn.build_graph(edges, features)
        s = self.qgnn.qgnn_summary()
        self.assertIn("nodes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
