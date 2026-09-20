"""
Quantum Graph Neural Network Module
Quantum-inspired graph neural networks, message passing,
node classification, and graph-level prediction for autonomous learning.
"""

import math
import random
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass


@dataclass
class GraphNode:
    """A node in the graph."""
    id: int
    features: List[float]
    label: Optional[int] = None


@dataclass
class GraphEdge:
    """An edge in the graph."""
    source: int
    target: int
    weight: float = 1.0


class Graph:
    """
    Simple graph data structure.
    """
    
    def __init__(self):
        self.nodes: Dict[int, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.adjacency: Dict[int, List[int]] = {}
    
    def add_node(self, node: GraphNode):
        """Add node."""
        self.nodes[node.id] = node
        if node.id not in self.adjacency:
            self.adjacency[node.id] = []
    
    def add_edge(self, edge: GraphEdge):
        """Add edge."""
        self.edges.append(edge)
        if edge.source not in self.adjacency:
            self.adjacency[edge.source] = []
        self.adjacency[edge.source].append(edge.target)
    
    def neighbors(self, node_id: int) -> List[int]:
        """
        Get neighbor nodes.
        
        Args:
            node_id: Node ID
        
        Returns:
            Neighbor IDs
        """
        return self.adjacency.get(node_id, [])
    
    def degree(self, node_id: int) -> int:
        """
        Get node degree.
        
        Args:
            node_id: Node ID
        
        Returns:
            Degree
        """
        return len(self.neighbors(node_id))
    
    def num_nodes(self) -> int:
        """Get number of nodes."""
        return len(self.nodes)
    
    def num_edges(self) -> int:
        """Get number of edges."""
        return len(self.edges)


class MessagePassing:
    """
    Classical message passing layer.
    """
    
    def __init__(self, feature_dim: int, hidden_dim: int):
        """
        Args:
            feature_dim: Input feature dimension
            hidden_dim: Hidden dimension
        """
        self.in_dim = feature_dim
        self.out_dim = hidden_dim
        # Message weights: out_dim x in_dim
        self.W_msg: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                          for _ in range(feature_dim)]
                                         for _ in range(hidden_dim)]
        # Update weights: out_dim x out_dim
        self.W_update: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                             for _ in range(hidden_dim)]
                                            for _ in range(hidden_dim)]
    
    def matvec(self, W: List[List[float]], x: List[float]) -> List[float]:
        """
        Matrix-vector multiplication.
        
        Args:
            W: Matrix
            x: Vector
        
        Returns:
            Result
        """
        result = []
        for row in W:
            val = sum(row[i] * x[i] for i in range(min(len(row), len(x))))
            result.append(val)
        return result
    
    def relu(self, x: List[float]) -> List[float]:
        """ReLU activation."""
        return [max(0.0, v) for v in x]
    
    def aggregate(self, messages: List[List[float]],
                 method: str = "mean") -> List[float]:
        """
        Aggregate messages.
        
        Args:
            messages: List of message vectors
            method: "mean", "sum", or "max"
        
        Returns:
            Aggregated vector
        """
        if not messages:
            return [0.0] * self.out_dim
        
        dim = min(self.out_dim, len(messages[0]))
        if method == "sum":
            return [sum(m[i] for m in messages) for i in range(dim)] + [0.0] * (self.out_dim - dim)
        elif method == "max":
            return [max(m[i] for m in messages) for i in range(dim)] + [0.0] * (self.out_dim - dim)
        else:  # mean
            return [sum(m[i] for m in messages) / len(messages) for i in range(dim)] + [0.0] * (self.out_dim - dim)
    
    def forward(self, graph: Graph,
               node_features: Dict[int, List[float]]) -> Dict[int, List[float]]:
        """
        Message passing forward pass.
        
        Args:
            graph: Graph
            node_features: Node features
        
        Returns:
            Updated features
        """
        new_features = {}
        
        for node_id in graph.nodes:
            # Collect messages from neighbors
            messages = []
            for neighbor_id in graph.neighbors(node_id):
                neighbor_feat = node_features.get(neighbor_id, [0.0] * self.in_dim)
                msg = self.matvec(self.W_msg, neighbor_feat)
                messages.append(msg)
            
            # Aggregate
            aggregated = self.aggregate(messages, "mean")
            
            # Update
            own_feat = node_features.get(node_id, [0.0] * self.in_dim)
            own_transformed = self.matvec(self.W_msg, own_feat)
            combined = [aggregated[i] + own_transformed[i] for i in range(self.out_dim)]
            updated = self.matvec(self.W_update, combined)
            new_features[node_id] = self.relu(updated)
        
        return new_features


class QuantumGraphLayer:
    """
    Quantum-inspired graph layer with superposition.
    """
    
    def __init__(self, feature_dim: int, num_basis: int = 4):
        """
        Args:
            feature_dim: Feature dimension
            num_basis: Number of quantum basis states
        """
        self.dim = feature_dim
        self.basis = num_basis
        # Quantum amplitudes for each feature component
        self.amplitudes: List[List[float]] = [
            [random.uniform(-1.0, 1.0) for _ in range(num_basis)]
            for _ in range(feature_dim)
        ]
    
    def quantum_feature_map(self, features: List[float]) -> List[float]:
        """
        Map features to quantum-enhanced representation.
        
        Args:
            features: Input features
        
        Returns:
            Quantum features
        """
        result = []
        for i in range(min(len(features), self.dim)):
            # Superposition of basis states
            val = features[i]
            quantum_val = sum(a * math.sin(val * (j + 1)) for j, a in enumerate(self.amplitudes[i]))
            result.append(quantum_val)
        return result
    
    def forward(self, graph: Graph,
               node_features: Dict[int, List[float]]) -> Dict[int, List[float]]:
        """
        Quantum graph forward pass.
        
        Args:
            graph: Graph
            node_features: Node features
        
        Returns:
            Updated features
        """
        new_features = {}
        
        for node_id in graph.nodes:
            # Quantum-enhanced self features
            self_quantum = self.quantum_feature_map(
                node_features.get(node_id, [0.0] * self.dim)
            )
            
            # Aggregate neighbor quantum features
            neighbor_sum = [0.0] * self.dim
            count = 0
            for neighbor_id in graph.neighbors(node_id):
                neighbor_feat = node_features.get(neighbor_id, [0.0] * self.dim)
                neighbor_quantum = self.quantum_feature_map(neighbor_feat)
                for i in range(self.dim):
                    neighbor_sum[i] += neighbor_quantum[i]
                count += 1
            
            # Combine
            if count > 0:
                for i in range(self.dim):
                    neighbor_sum[i] /= count
                    self_quantum[i] = (self_quantum[i] + neighbor_sum[i]) / 2.0
            
            new_features[node_id] = self_quantum
        
        return new_features


class NodeClassifier:
    """
    Node classification head.
    """
    
    def __init__(self, feature_dim: int, num_classes: int):
        """
        Args:
            feature_dim: Feature dimension
            num_classes: Number of classes
        """
        self.dim = feature_dim
        self.classes = num_classes
        self.W: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                      for _ in range(num_classes)]
                                     for _ in range(feature_dim)]
        self.b: List[float] = [0.0] * num_classes
    
    def classify(self, features: List[float]) -> int:
        """
        Classify node.
        
        Args:
            features: Node features
        
        Returns:
            Predicted class
        """
        scores = []
        for c in range(self.classes):
            score = self.b[c]
            for i in range(min(len(features), self.dim)):
                score += features[i] * self.W[i][c]
            scores.append(score)
        
        return scores.index(max(scores))
    
    def class_scores(self, features: List[float]) -> List[float]:
        """
        Get class scores.
        
        Args:
            features: Node features
        
        Returns:
            Scores
        """
        scores = []
        for c in range(self.classes):
            score = self.b[c]
            for i in range(min(len(features), self.dim)):
                score += features[i] * self.W[i][c]
            scores.append(score)
        return scores


class GraphLevelPredictor:
    """
    Graph-level prediction (pooling + MLP).
    """
    
    def __init__(self, feature_dim: int, output_dim: int):
        """
        Args:
            feature_dim: Feature dimension
            output_dim: Output dimension
        """
        self.dim = feature_dim
        self.out = output_dim
        self.W: List[List[float]] = [[random.uniform(-0.1, 0.1)
                                      for _ in range(output_dim)]
                                     for _ in range(feature_dim)]
    
    def global_mean_pool(self, node_features: Dict[int, List[float]]) -> List[float]:
        """
        Global mean pooling.
        
        Args:
            node_features: Node features
        
        Returns:
            Pooled vector
        """
        if not node_features:
            return [0.0] * self.dim
        
        pooled = [0.0] * self.dim
        for features in node_features.values():
            for i in range(min(len(features), self.dim)):
                pooled[i] += features[i]
        
        for i in range(self.dim):
            pooled[i] /= len(node_features)
        return pooled
    
    def predict(self, node_features: Dict[int, List[float]]) -> List[float]:
        """
        Predict graph-level output.
        
        Args:
            node_features: Node features
        
        Returns:
            Output vector
        """
        pooled = self.global_mean_pool(node_features)
        result = []
        for j in range(self.out):
            val = sum(pooled[i] * self.W[i][j] for i in range(self.dim))
            result.append(val)
        return result


class QuantumGraphNeuralNetwork:
    """
    Unified quantum graph neural network controller.
    """
    
    def __init__(self):
        self.graph: Optional[Graph] = None
        self.mp_layer: Optional[MessagePassing] = None
        self.quantum_layer: Optional[QuantumGraphLayer] = None
        self.classifier: Optional[NodeClassifier] = None
        self.predictor: Optional[GraphLevelPredictor] = None
        self.node_features: Dict[int, List[float]] = {}
    
    def build(self, feature_dim: int, hidden_dim: int,
             num_classes: int = 2):
        """
        Build QGNN.
        
        Args:
            feature_dim: Input feature dimension
            hidden_dim: Hidden dimension
            num_classes: Number of classes
        """
        self.mp_layer = MessagePassing(feature_dim, hidden_dim)
        self.quantum_layer = QuantumGraphLayer(hidden_dim)
        self.classifier = NodeClassifier(hidden_dim, num_classes)
        self.predictor = GraphLevelPredictor(hidden_dim, num_classes)
    
    def load_graph(self, graph: Graph):
        """Load graph."""
        self.graph = graph
        self.node_features = {node_id: node.features[:] for node_id, node in graph.nodes.items()}
    
    def forward(self, num_layers: int = 2) -> Dict[int, List[float]]:
        """
        Forward pass.
        
        Args:
            num_layers: Number of message passing layers
        
        Returns:
            Node embeddings
        """
        features = self.node_features
        
        for _ in range(num_layers):
            if self.mp_layer:
                features = self.mp_layer.forward(self.graph, features)
            if self.quantum_layer:
                features = self.quantum_layer.forward(self.graph, features)
        
        return features
    
    def classify_nodes(self) -> Dict[int, int]:
        """
        Classify all nodes.
        
        Returns:
            Node predictions
        """
        embeddings = self.forward()
        return {node_id: self.classifier.classify(emb) for node_id, emb in embeddings.items()}
    
    def graph_prediction(self) -> List[float]:
        """
        Graph-level prediction.
        
        Returns:
            Prediction vector
        """
        embeddings = self.forward()
        return self.predictor.predict(embeddings)
    
    def qgnn_summary(self) -> Dict:
        """Get QGNN summary."""
        return {
            "nodes": self.graph.num_nodes() if self.graph else 0,
            "edges": self.graph.num_edges() if self.graph else 0,
            "features": self.mp_layer.in_dim if self.mp_layer else 0,
            "hidden": self.mp_layer.out_dim if self.mp_layer else 0,
            "classes": self.classifier.classes if self.classifier else 0
        }
