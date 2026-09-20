"""
Unit tests for quantum graph neural networks module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_graph_neural_networks import (QuantumNode, QuantumEdge, QuantumGraph,
                                           QuantumGraphConvolution,
                                           QuantumMessagePassing,
                                           QuantumGraphPooling,
                                           QuantumGraphClassifier,
                                           QuantumGraphNeuralNetworks)


class TestQuantumGraph(unittest.TestCase):
    """Test graph."""
    
    def setUp(self):
        self.g = QuantumGraph()
    
    def test_add_node(self):
        """Should add node."""
        self.g.add_node(QuantumNode(0, [1.0, 0.0]))
        self.assertIn(0, self.g.nodes)
        print("  [PASS] Node")
    
    def test_add_edge(self):
        """Should add edge."""
        self.g.add_node(QuantumNode(0, [1.0, 0.0]))
        self.g.add_node(QuantumNode(1, [0.0, 1.0]))
        self.g.add_edge(QuantumEdge(0, 1, 1.0))
        self.assertEqual(len(self.g.edges), 1)
        print("  [PASS] Edge")


class TestQuantumGraphConvolution(unittest.TestCase):
    """Test convolution."""
    
    def setUp(self):
        self.conv = QuantumGraphConvolution(2)
    
    def test_aggregate(self):
        """Should aggregate."""
        g = QuantumGraph()
        g.add_node(QuantumNode(0, [1.0, 0.0]))
        g.add_node(QuantumNode(1, [0.0, 1.0]))
        g.add_edge(QuantumEdge(0, 1, 1.0))
        agg = self.conv.aggregate(g, 0)
        self.assertEqual(len(agg), 2)
        print(f"  [PASS] Agg: {agg}")
    
    def test_convolve(self):
        """Should convolve."""
        g = QuantumGraph()
        g.add_node(QuantumNode(0, [1.0, 0.0]))
        g.add_node(QuantumNode(1, [0.0, 1.0]))
        g.add_edge(QuantumEdge(0, 1, 1.0))
        result = self.conv.convolve(g)
        self.assertEqual(len(result.nodes), 2)
        print("  [PASS] Conv")


class TestQuantumMessagePassing(unittest.TestCase):
    """Test message passing."""
    
    def setUp(self):
        self.mp = QuantumMessagePassing(2, 2)
    
    def test_pass(self):
        """Should pass messages."""
        g = QuantumGraph()
        g.add_node(QuantumNode(0, [1.0, 0.0]))
        g.add_node(QuantumNode(1, [0.0, 1.0]))
        g.add_edge(QuantumEdge(0, 1, 1.0))
        result = self.mp.pass_messages(g)
        self.assertEqual(len(result.nodes), 2)
        print("  [PASS] MP")


class TestQuantumGraphPooling(unittest.TestCase):
    """Test pooling."""
    
    def setUp(self):
        self.pool = QuantumGraphPooling()
    
    def test_mean(self):
        """Should mean pool."""
        g = QuantumGraph()
        g.add_node(QuantumNode(0, [1.0, 0.0]))
        g.add_node(QuantumNode(1, [0.0, 1.0]))
        p = self.pool.mean_pool(g)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Mean: {p}")
    
    def test_max(self):
        """Should max pool."""
        g = QuantumGraph()
        g.add_node(QuantumNode(0, [1.0, 0.0]))
        g.add_node(QuantumNode(1, [0.0, 0.5]))
        p = self.pool.max_pool(g)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Max: {p}")


class TestQuantumGraphClassifier(unittest.TestCase):
    """Test classifier."""
    
    def setUp(self):
        self.clf = QuantumGraphClassifier(2, 2)
    
    def test_classify(self):
        """Should classify."""
        self.clf.initialize()
        c = self.clf.classify([1.0, 0.0])
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Cls: {c}")


class TestQuantumGraphNeuralNetworks(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgnn = QuantumGraphNeuralNetworks(2, 2)
    
    def test_process(self):
        """Should process graph."""
        g = QuantumGraph()
        g.add_node(QuantumNode(0, [1.0, 0.0]))
        g.add_node(QuantumNode(1, [0.0, 1.0]))
        g.add_edge(QuantumEdge(0, 1, 1.0))
        r = self.qgnn.process(g)
        self.assertIn("class", r)
        print(f"  [PASS] Proc: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qgnn.qgnn_summary()
        self.assertIn("dim", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
