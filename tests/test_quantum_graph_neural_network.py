"""
Unit tests for quantum graph neural network module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_graph_neural_network import (GraphNode, GraphEdge, Graph,
                                          MessagePassing, QuantumGraphLayer,
                                          NodeClassifier, GraphLevelPredictor,
                                          QuantumGraphNeuralNetwork)


def make_test_graph():
    """Create a simple test graph."""
    g = Graph()
    g.add_node(GraphNode(0, [1.0, 0.0, 0.0]))
    g.add_node(GraphNode(1, [0.0, 1.0, 0.0]))
    g.add_node(GraphNode(2, [0.0, 0.0, 1.0]))
    g.add_edge(GraphEdge(0, 1))
    g.add_edge(GraphEdge(1, 2))
    g.add_edge(GraphEdge(2, 0))
    return g


class TestGraph(unittest.TestCase):
    """Test graph."""
    
    def setUp(self):
        self.g = make_test_graph()
    
    def test_nodes(self):
        """Should count nodes."""
        self.assertEqual(self.g.num_nodes(), 3)
        print("  [PASS] Nodes")
    
    def test_edges(self):
        """Should count edges."""
        self.assertEqual(self.g.num_edges(), 3)
        print("  [PASS] Edges")
    
    def test_neighbors(self):
        """Should find neighbors."""
        n = self.g.neighbors(0)
        self.assertIn(1, n)
        print(f"  [PASS] Neigh: {n}")
    
    def test_degree(self):
        """Should compute degree."""
        self.assertEqual(self.g.degree(0), 1)
        print("  [PASS] Deg")


class TestMessagePassing(unittest.TestCase):
    """Test message passing."""
    
    def setUp(self):
        self.mp = MessagePassing(3, 4)
        self.g = make_test_graph()
    
    def test_forward(self):
        """Should forward pass."""
        features = {0: [1.0, 0.0, 0.0], 1: [0.0, 1.0, 0.0], 2: [0.0, 0.0, 1.0]}
        out = self.mp.forward(self.g, features)
        self.assertEqual(len(out), 3)
        self.assertEqual(len(out[0]), 4)
        print("  [PASS] Forward")
    
    def test_aggregate(self):
        """Should aggregate."""
        msgs = [[1.0, 2.0], [3.0, 4.0]]
        agg = self.mp.aggregate(msgs, "mean")
        self.assertAlmostEqual(agg[0], 2.0)
        print(f"  [PASS] Agg: {agg}")


class TestQuantumGraphLayer(unittest.TestCase):
    """Test quantum graph layer."""
    
    def setUp(self):
        self.qgl = QuantumGraphLayer(3, 4)
        self.g = make_test_graph()
    
    def test_quantum_map(self):
        """Should quantum map features."""
        qf = self.qgl.quantum_feature_map([1.0, 0.0, 0.0])
        self.assertEqual(len(qf), 3)
        print("  [PASS] QMap")
    
    def test_forward(self):
        """Should forward pass."""
        features = {0: [1.0, 0.0, 0.0], 1: [0.0, 1.0, 0.0], 2: [0.0, 0.0, 1.0]}
        out = self.qgl.forward(self.g, features)
        self.assertEqual(len(out), 3)
        print("  [PASS] QForward")


class TestNodeClassifier(unittest.TestCase):
    """Test node classifier."""
    
    def setUp(self):
        self.nc = NodeClassifier(4, 2)
    
    def test_classify(self):
        """Should classify."""
        c = self.nc.classify([1.0, 0.0, 0.0, 0.0])
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Class: {c}")
    
    def test_scores(self):
        """Should compute scores."""
        s = self.nc.class_scores([1.0, 0.0, 0.0, 0.0])
        self.assertEqual(len(s), 2)
        print(f"  [PASS] Scores: {s}")


class TestGraphLevelPredictor(unittest.TestCase):
    """Test graph predictor."""
    
    def setUp(self):
        self.gp = GraphLevelPredictor(4, 2)
    
    def test_pool(self):
        """Should pool."""
        feats = {0: [1.0, 2.0, 3.0, 4.0], 1: [1.0, 2.0, 3.0, 4.0]}
        p = self.gp.global_mean_pool(feats)
        self.assertAlmostEqual(p[0], 1.0)
        print("  [PASS] Pool")
    
    def test_predict(self):
        """Should predict."""
        feats = {0: [1.0, 0.0, 0.0, 0.0], 1: [0.0, 1.0, 0.0, 0.0]}
        pred = self.gp.predict(feats)
        self.assertEqual(len(pred), 2)
        print(f"  [PASS] Pred: {pred}")


class TestQuantumGraphNeuralNetwork(unittest.TestCase):
    """Test unified QGNN."""
    
    def setUp(self):
        self.qgnn = QuantumGraphNeuralNetwork()
    
    def test_build(self):
        """Should build."""
        self.qgnn.build(3, 4, 2)
        self.assertIsNotNone(self.qgnn.mp_layer)
        print("  [PASS] Build")
    
    def test_load(self):
        """Should load graph."""
        self.qgnn.build(3, 4, 2)
        self.qgnn.load_graph(make_test_graph())
        self.assertEqual(self.qgnn.graph.num_nodes(), 3)
        print("  [PASS] Load")
    
    def test_classify(self):
        """Should classify nodes."""
        self.qgnn.build(3, 4, 2)
        self.qgnn.load_graph(make_test_graph())
        preds = self.qgnn.classify_nodes()
        self.assertEqual(len(preds), 3)
        print(f"  [PASS] Class: {preds}")
    
    def test_graph_pred(self):
        """Should predict graph."""
        self.qgnn.build(3, 4, 2)
        self.qgnn.load_graph(make_test_graph())
        pred = self.qgnn.graph_prediction()
        self.assertEqual(len(pred), 2)
        print(f"  [PASS] Graph: {pred}")
    
    def test_summary(self):
        """Should summarize."""
        self.qgnn.build(3, 4, 2)
        self.qgnn.load_graph(make_test_graph())
        s = self.qgnn.qgnn_summary()
        self.assertEqual(s["nodes"], 3)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
