"""
Quantum Decision Tree Advanced Module
Quantum entropy splitting, quantum information gain,
quantum-inspired tree building, and ensemble quantum forests for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TreeNode:
    """Decision tree node."""
    feature_index: Optional[int]
    threshold: Optional[float]
    left: Optional['TreeNode']
    right: Optional['TreeNode']
    prediction: Optional[int]


class QuantumEntropySplitting:
    """
    Quantum-inspired entropy-based splitting.
    """
    
    def __init__(self):
        pass
    
    def von_neumann_entropy(self, probabilities: List[float]) -> float:
        """
        Compute von Neumann entropy from probabilities.
        
        Args:
            probabilities: State probabilities
        
        Returns:
            Entropy (bits)
        """
        if not probabilities:
            return 0.0
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def quantum_information_gain(self, parent_probs: List[float],
                                left_probs: List[float],
                                right_probs: List[float],
                                left_weight: float = 0.5) -> float:
        """
        Compute quantum information gain.
        
        Args:
            parent_probs: Parent distribution
            left_probs: Left child distribution
            right_probs: Right child distribution
            left_weight: Left weight
        
        Returns:
            Information gain
        """
        parent_entropy = self.von_neumann_entropy(parent_probs)
        left_entropy = self.von_neumann_entropy(left_probs)
        right_entropy = self.von_neumann_entropy(right_probs)
        weighted_child = left_weight * left_entropy + (1.0 - left_weight) * right_entropy
        return parent_entropy - weighted_child


class QuantumInformationGain:
    """
    Quantum information gain for feature selection.
    """
    
    def __init__(self):
        pass
    
    def binary_split_quality(self, feature_values: List[float],
                            labels: List[int],
                            threshold: float) -> float:
        """
        Evaluate split quality at threshold.
        
        Args:
            feature_values: Feature values
            labels: Class labels
            threshold: Split threshold
        
        Returns:
            Gain value
        """
        if not feature_values or not labels:
            return 0.0
        left_labels = [l for f, l in zip(feature_values, labels) if f <= threshold]
        right_labels = [l for f, l in zip(feature_values, labels) if f > threshold]
        if not left_labels or not right_labels:
            return 0.0
        # Compute class distributions
        all_classes = list(set(labels))
        parent_counts = [labels.count(c) / len(labels) for c in all_classes]
        left_counts = [left_labels.count(c) / len(left_labels) for c in all_classes]
        right_counts = [right_labels.count(c) / len(right_labels) for c in all_classes]
        # Compute gain
        qes = QuantumEntropySplitting()
        return qes.quantum_information_gain(parent_counts, left_counts, right_counts,
                                           len(left_labels) / len(labels))
    
    def best_threshold(self, feature_values: List[float],
                      labels: List[int]) -> Tuple[float, float]:
        """
        Find best threshold for feature.
        
        Args:
            feature_values: Feature values
            labels: Class labels
        
        Returns:
            (threshold, gain)
        """
        if not feature_values or not labels:
            return (0.0, 0.0)
        unique_values = sorted(set(feature_values))
        best_gain = -1.0
        best_threshold = unique_values[0]
        for i in range(len(unique_values) - 1):
            threshold = (unique_values[i] + unique_values[i + 1]) / 2.0
            gain = self.binary_split_quality(feature_values, labels, threshold)
            if gain > best_gain:
                best_gain = gain
                best_threshold = threshold
        return (best_threshold, best_gain)


class QuantumInspiredTreeBuilding:
    """
    Build quantum-inspired decision trees.
    """
    
    def __init__(self, max_depth: int = 5):
        """
        Args:
            max_depth: Maximum depth
        """
        self.max_depth = max_depth
    
    def build_leaf(self, labels: List[int]) -> TreeNode:
        """
        Create leaf node.
        
        Args:
            labels: Labels
        
        Returns:
            Leaf node
        """
        if not labels:
            return TreeNode(None, None, None, None, 0)
        prediction = max(set(labels), key=labels.count)
        return TreeNode(None, None, None, None, prediction)
    
    def should_split(self, labels: List[int], depth: int) -> bool:
        """
        Check if node should split.
        
        Args:
            labels: Labels
            depth: Current depth
        
        Returns:
            True if should split
        """
        if depth >= self.max_depth:
            return False
        return len(set(labels)) > 1
    
    def predict(self, node: TreeNode, features: List[float]) -> int:
        """
        Predict class for features.
        
        Args:
            node: Tree root
            features: Feature vector
        
        Returns:
            Prediction
        """
        if node.prediction is not None:
            return node.prediction
        if node.feature_index is not None and node.threshold is not None:
            if features[node.feature_index] <= node.threshold:
                return self.predict(node.left, features)
            else:
                return self.predict(node.right, features)
        return 0


class EnsembleQuantumForest:
    """
    Ensemble of quantum-inspired trees.
    """
    
    def __init__(self, num_trees: int = 10):
        """
        Args:
            num_trees: Number of trees
        """
        self.n_trees = num_trees
        self.trees: List[TreeNode] = []
    
    def majority_vote(self, predictions: List[int]) -> int:
        """
        Majority vote across trees.
        
        Args:
            predictions: Tree predictions
        
        Returns:
            Majority class
        """
        if not predictions:
            return 0
        return max(set(predictions), key=predictions.count)
    
    def forest_predict(self, features: List[float]) -> int:
        """
        Predict using forest.
        
        Args:
            features: Feature vector
        
        Returns:
            Prediction
        """
        if not self.trees:
            return 0
        builder = QuantumInspiredTreeBuilding()
        predictions = [builder.predict(tree, features) for tree in self.trees]
        return self.majority_vote(predictions)


class QuantumDecisionTreeAdvanced:
    """
    Unified quantum decision tree controller.
    """
    
    def __init__(self):
        self.entropy = QuantumEntropySplitting()
        self.gain = QuantumInformationGain()
        self.tree = QuantumInspiredTreeBuilding()
        self.forest = EnsembleQuantumForest()
    
    def decision_tree_summary(self) -> Dict:
        """Get summary."""
        return {
            "components": ["entropy_splitting", "information_gain", "tree_building", "ensemble"],
            "applications": ["classification", "feature_selection"]
        }
