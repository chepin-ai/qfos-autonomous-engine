"""
Quantum Natural Language Processing Advanced Module
Quantum word embeddings, quantum sentence classification,
quantum semantic similarity, and quantum language modeling for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumWord:
    """Quantum word representation."""
    word: str
    amplitude: List[float]


class QuantumWordEmbeddings:
    """
    Quantum word embedding methods.
    """
    
    def __init__(self, embedding_dim: int = 8):
        """
        Args:
            embedding_dim: Dimension
        """
        self.dim = embedding_dim
    
    def encode_word(self, word: str) -> List[float]:
        """
        Encode word as quantum amplitude vector.
        
        Args:
            word: Input word
        
        Returns:
            Amplitude vector
        """
        # Simplified: hash-based encoding
        import hashlib
        h = hashlib.md5(word.encode()).hexdigest()
        vector = []
        for i in range(self.dim):
            val = int(h[i * 2:i * 2 + 2], 16) / 255.0
            vector.append(val * 2.0 - 1.0)  # Scale to [-1, 1]
        # Normalize
        norm = math.sqrt(sum(v**2 for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector
    
    def word_similarity(self, word1: str, word2: str) -> float:
        """
        Compute quantum word similarity.
        
        Args:
            word1, word2: Words
        
        Returns:
            Similarity (-1 to 1)
        """
        v1 = self.encode_word(word1)
        v2 = self.encode_word(word2)
        dot = sum(a * b for a, b in zip(v1, v2))
        return dot


class QuantumSentenceClassification:
    """
    Quantum sentence classification.
    """
    
    def __init__(self):
        self.class_vectors: Dict[int, List[float]] = {}
    
    def train(self, class_id: int, sentences: List[str],
              embeddings: QuantumWordEmbeddings):
        """
        Train class prototype.
        
        Args:
            class_id: Class label
            sentences: Training sentences
            embeddings: Word embeddings
        """
        vectors = []
        for sentence in sentences:
            words = sentence.lower().split()
            if words:
                vec = [0.0] * embeddings.dim
                for word in words:
                    wvec = embeddings.encode_word(word)
                    vec = [a + b for a, b in zip(vec, wvec)]
                vec = [v / len(words) for v in vec]
                vectors.append(vec)
        if vectors:
            prototype = [sum(v[i] for v in vectors) / len(vectors) for i in range(embeddings.dim)]
            self.class_vectors[class_id] = prototype
    
    def classify(self, sentence: str,
                embeddings: QuantumWordEmbeddings) -> int:
        """
        Classify sentence.
        
        Args:
            sentence: Input sentence
            embeddings: Word embeddings
        
        Returns:
            Class label
        """
        words = sentence.lower().split()
        if not words or not self.class_vectors:
            return 0
        vec = [0.0] * embeddings.dim
        for word in words:
            wvec = embeddings.encode_word(word)
            vec = [a + b for a, b in zip(vec, wvec)]
        vec = [v / len(words) for v in vec]
        # Find closest class
        best_class = 0
        best_sim = -1.0
        for class_id, prototype in self.class_vectors.items():
            sim = sum(a * b for a, b in zip(vec, prototype))
            if sim > best_sim:
                best_sim = sim
                best_class = class_id
        return best_class


class QuantumSemanticSimilarity:
    """
    Quantum semantic similarity.
    """
    
    def __init__(self):
        pass
    
    def sentence_embedding(self, sentence: str,
                          embeddings: QuantumWordEmbeddings) -> List[float]:
        """
        Compute sentence embedding.
        
        Args:
            sentence: Input sentence
            embeddings: Word embeddings
        
        Returns:
            Sentence vector
        """
        words = sentence.lower().split()
        if not words:
            return [0.0] * embeddings.dim
        vec = [0.0] * embeddings.dim
        for word in words:
            wvec = embeddings.encode_word(word)
            vec = [a + b for a, b in zip(vec, wvec)]
        return [v / len(words) for v in vec]
    
    def similarity(self, sentence1: str, sentence2: str,
                  embeddings: QuantumWordEmbeddings) -> float:
        """
        Compute sentence similarity.
        
        Args:
            sentence1, sentence2: Sentences
            embeddings: Word embeddings
        
        Returns:
            Similarity score
        """
        v1 = self.sentence_embedding(sentence1, embeddings)
        v2 = self.sentence_embedding(sentence2, embeddings)
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a**2 for a in v1))
        norm2 = math.sqrt(sum(b**2 for b in v2))
        if norm1 <= 0 or norm2 <= 0:
            return 0.0
        return dot / (norm1 * norm2)


class QuantumLanguageModeling:
    """
    Quantum language modeling.
    """
    
    def __init__(self):
        pass
    
    def ngram_probability(self, words: List[str], n: int = 2) -> float:
        """
        Compute n-gram probability (simplified).
        
        Args:
            words: Word sequence
            n: N-gram size
        
        Returns:
            Probability
        """
        if len(words) < n:
            return 1.0
        # Simplified: uniform probability
        return 1.0 / (len(words) - n + 1) if len(words) >= n else 1.0
    
    def perplexity(self, words: List[str], n: int = 2) -> float:
        """
        Compute perplexity.
        
        Args:
            words: Word sequence
            n: N-gram size
        
        Returns:
            Perplexity
        """
        if len(words) < n:
            return 1.0
        prob = self.ngram_probability(words, n)
        if prob <= 0:
            return float('inf')
        return 1.0 / prob


class QuantumNLPAdvanced:
    """
    Unified quantum NLP controller.
    """
    
    def __init__(self):
        self.embeddings = QuantumWordEmbeddings()
        self.classification = QuantumSentenceClassification()
        self.similarity = QuantumSemanticSimilarity()
        self.language_model = QuantumLanguageModeling()
    
    def nlp_summary(self) -> Dict:
        """Get summary."""
        return {
            "components": ["word_embeddings", "classification", "similarity", "language_model"],
            "applications": ["text_classification", "semantic_search"]
        }
