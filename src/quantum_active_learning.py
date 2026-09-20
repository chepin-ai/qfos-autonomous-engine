"""
Quantum Active Learning Module
Uncertainty sampling, query-by-committee, quantum uncertainty
estimation, and batch selection for autonomous data efficiency.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class UncertaintySampler:
    """
    Uncertainty-based sampling.
    """
    
    def __init__(self):
        pass
    
    def entropy(self, probabilities: List[float]) -> float:
        """
        Compute entropy.
        
        Args:
            probabilities: Probabilities
        
        Returns:
            Entropy
        """
        h = 0.0
        for p in probabilities:
            if p > 0:
                h -= p * math.log2(p)
        return h
    
    def margin(self, probabilities: List[float]) -> float:
        """
        Compute margin (difference between top two).
        
        Args:
            probabilities: Probabilities
        
        Returns:
            Margin
        """
        if len(probabilities) < 2:
            return 0.0
        
        sorted_probs = sorted(probabilities, reverse=True)
        return 1.0 - (sorted_probs[0] - sorted_probs[1])
    
    def least_confident(self, probabilities: List[float]) -> float:
        """
        Compute least confidence.
        
        Args:
            probabilities: Probabilities
        
        Returns:
            Uncertainty
        """
        return 1.0 - max(probabilities) if probabilities else 1.0


class QueryByCommittee:
    """
    Query by committee sampling.
    """
    
    def __init__(self, num_committee: int = 3):
        """
        Args:
            num_committee: Committee size
        """
        self.k = num_committee
        self.committee_votes: List[List[int]] = []
    
    def vote_entropy(self, votes: List[int], num_classes: int = 2) -> float:
        """
        Compute vote entropy.
        
        Args:
            votes: Committee votes
            num_classes: Classes
        
        Returns:
            Entropy
        """
        counts = [0] * num_classes
        for v in votes:
            if 0 <= v < num_classes:
                counts[v] += 1
        
        total = len(votes)
        h = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                h -= p * math.log2(p)
        return h
    
    def disagreement(self, votes: List[int]) -> float:
        """
        Compute disagreement ratio.
        
        Args:
            votes: Votes
        
        Returns:
            Disagreement
        """
        if not votes:
            return 0.0
        
        unique = len(set(votes))
        return unique / len(votes)


class QuantumUncertaintyEstimator:
    """
    Quantum uncertainty estimation.
    """
    
    def __init__(self):
        pass
    
    def quantum_entropy(self, state_amplitudes: List[complex]) -> float:
        """
        Compute von Neumann entropy approximation.
        
        Args:
            state_amplitudes: State amplitudes
        
        Returns:
            Entropy
        """
        probs = [abs(a)**2 for a in state_amplitudes]
        h = 0.0
        for p in probs:
            if p > 1e-10:
                h -= p * math.log2(p)
        return h
    
    def uncertainty_from_superposition(self,
                                       predictions: List[float]) -> float:
        """
        Compute uncertainty from superposition.
        
        Args:
            predictions: Predictions
        
        Returns:
            Uncertainty
        """
        if not predictions:
            return 1.0
        
        mean = sum(predictions) / len(predictions)
        variance = sum((p - mean)**2 for p in predictions) / len(predictions)
        return math.sqrt(variance)


class BatchSelector:
    """
    Batch selection for active learning.
    """
    
    def __init__(self, batch_size: int = 10):
        """
        Args:
            batch_size: Batch size
        """
        self.batch_size = batch_size
    
    def select_uncertainty(self, uncertainties: List[float],
                          indices: List[int]) -> List[int]:
        """
        Select most uncertain samples.
        
        Args:
            uncertainties: Uncertainty values
            indices: Sample indices
        
        Returns:
            Selected indices
        """
        paired = list(zip(uncertainties, indices))
        paired.sort(reverse=True)
        return [idx for _, idx in paired[:self.batch_size]]
    
    def select_diverse(self, embeddings: List[List[float]],
                      indices: List[int]) -> List[int]:
        """
        Select diverse samples.
        
        Args:
            embeddings: Embeddings
            indices: Sample indices
        
        Returns:
            Selected indices
        """
        if len(indices) <= self.batch_size:
            return indices
        
        # Greedy diversity selection
        selected = [indices[0]]
        remaining = set(indices[1:])
        
        while len(selected) < self.batch_size and remaining:
            # Find farthest from selected
            max_min_dist = -1
            best_idx = None
            
            for idx in remaining:
                emb = embeddings[idx]
                min_dist = min(
                    sum((a - b)**2 for a, b in zip(emb, embeddings[s])) ** 0.5
                    for s in selected
                )
                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    best_idx = idx
            
            if best_idx is not None:
                selected.append(best_idx)
                remaining.remove(best_idx)
        
        return selected


class QuantumActiveLearning:
    """
    Unified quantum active learning controller.
    """
    
    def __init__(self):
        self.uncertainty = UncertaintySampler()
        self.committee = QueryByCommittee()
        self.quantum_unc = QuantumUncertaintyEstimator()
        self.selector = BatchSelector()
        self.labeled: List[int] = []
        self.unlabeled: List[int] = []
    
    def initialize_pool(self, total_samples: int,
                       initial_labeled: List[int]):
        """
        Initialize sample pool.
        
        Args:
            total_samples: Total samples
            initial_labeled: Initially labeled indices
        """
        self.labeled = initial_labeled[:]
        self.unlabeled = [i for i in range(total_samples)
                         if i not in self.labeled]
    
    def query_uncertainty(self, probabilities: List[List[float]]) -> List[int]:
        """
        Query by uncertainty.
        
        Args:
            probabilities: Probabilities for unlabeled
        
        Returns:
            Selected indices
        """
        uncertainties = [self.uncertainty.least_confident(p)
                        for p in probabilities]
        return self.selector.select_uncertainty(uncertainties, self.unlabeled)
    
    def query_committee(self, committee_votes: List[List[int]]) -> List[int]:
        """
        Query by committee.
        
        Args:
            committee_votes: Votes for each unlabeled sample
        
        Returns:
            Selected indices
        """
        disagreements = [self.committee.disagreement(votes)
                        for votes in committee_votes]
        return self.selector.select_uncertainty(disagreements, self.unlabeled)
    
    def qal_summary(self) -> Dict:
        """Get summary."""
        return {
            "labeled": len(self.labeled),
            "unlabeled": len(self.unlabeled),
            "batch_size": self.selector.batch_size
        }
