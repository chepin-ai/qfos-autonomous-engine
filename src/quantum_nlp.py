"""
Quantum Natural Language Processing Module
Quantum word embeddings, quantum attention for text,
sentence encoding, and quantum classification.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumWordEmbedding:
    """Quantum word embedding."""
    word: str
    amplitudes: List[complex]


class QuantumWordEncoder:
    """
    Encode words into quantum states.
    """
    
    def __init__(self, dim: int = 8):
        """
        Args:
            dim: Embedding dimension
        """
        self.dim = dim
        self.vocabulary: Dict[str, QuantumWordEmbedding] = {}
    
    def encode_word(self, word: str) -> QuantumWordEmbedding:
        """
        Encode a word.
        
        Args:
            word: Word
        
        Returns:
            Embedding
        """
        if word in self.vocabulary:
            return self.vocabulary[word]
        
        # Simple hash-based encoding
        amplitudes = []
        hash_val = hash(word) % (2 ** 31)
        for i in range(self.dim):
            angle = (hash_val + i * 7919) % 360
            amplitudes.append(complex(math.cos(math.radians(angle)),
                                     math.sin(math.radians(angle))))
        
        # Normalize
        norm = math.sqrt(sum(abs(a)**2 for a in amplitudes))
        if norm > 0:
            amplitudes = [a / norm for a in amplitudes]
        
        embedding = QuantumWordEmbedding(word, amplitudes)
        self.vocabulary[word] = embedding
        return embedding
    
    def word_similarity(self, word1: str, word2: str) -> float:
        """
        Compute word similarity.
        
        Args:
            word1: Word 1
            word2: Word 2
        
        Returns:
            Similarity
        """
        e1 = self.encode_word(word1)
        e2 = self.encode_word(word2)
        
        overlap = sum(e1.amplitudes[i].conjugate() * e2.amplitudes[i]
                     for i in range(min(len(e1.amplitudes), len(e2.amplitudes))))
        return abs(overlap) ** 2


class QuantumSentenceEncoder:
    """
    Encode sentences into quantum states.
    """
    
    def __init__(self, dim: int = 8):
        """
        Args:
            dim: Dimension
        """
        self.dim = dim
        self.word_encoder = QuantumWordEncoder(dim)
    
    def encode_sentence(self, sentence: str) -> List[complex]:
        """
        Encode sentence.
        
        Args:
            sentence: Sentence
        
        Returns:
            Amplitudes
        """
        words = sentence.lower().split()
        if not words:
            return [0.0] * self.dim
        
        # Average word embeddings
        amplitudes = [0.0] * self.dim
        for word in words:
            emb = self.word_encoder.encode_word(word)
            for i in range(min(self.dim, len(emb.amplitudes))):
                amplitudes[i] += emb.amplitudes[i]
        
        for i in range(self.dim):
            amplitudes[i] /= len(words)
        
        # Normalize
        norm = math.sqrt(sum(abs(a)**2 for a in amplitudes))
        if norm > 0:
            amplitudes = [a / norm for a in amplitudes]
        
        return amplitudes


class QuantumTextAttention:
    """
    Quantum attention for text.
    """
    
    def __init__(self, dim: int = 8):
        """
        Args:
            dim: Dimension
        """
        self.dim = dim
    
    def attention_weights(self, query: List[complex],
                         keys: List[List[complex]]) -> List[float]:
        """
        Compute attention weights.
        
        Args:
            query: Query
            keys: Keys
        
        Returns:
            Weights
        """
        scores = []
        for key in keys:
            score = sum(query[i].conjugate() * key[i]
                       for i in range(min(len(query), len(key))))
            scores.append(abs(score) ** 2)
        
        total = sum(scores)
        if total > 0:
            return [s / total for s in scores]
        return [1.0 / len(keys)] * len(keys)
    
    def attend(self, query: List[complex],
              keys: List[List[complex]],
              values: List[List[complex]]) -> List[complex]:
        """
        Apply attention.
        
        Args:
            query: Query
            keys: Keys
            values: Values
        
        Returns:
            Attended output
        """
        weights = self.attention_weights(query, keys)
        
        output = [0.0] * self.dim
        for w, val in zip(weights, values):
            for i in range(min(self.dim, len(val))):
                output[i] += w * val[i]
        
        return output


class QuantumTextClassifier:
    """
    Quantum text classifier.
    """
    
    def __init__(self, dim: int = 8, num_classes: int = 2):
        """
        Args:
            dim: Dimension
            num_classes: Classes
        """
        self.dim = dim
        self.classes = num_classes
        self.weights: List[List[float]] = []
    
    def initialize(self):
        """Initialize weights."""
        import random
        self.weights = [[random.uniform(-1.0, 1.0) for _ in range(self.dim)]
                       for _ in range(self.classes)]
    
    def classify(self, sentence_amplitudes: List[complex]) -> int:
        """
        Classify sentence.
        
        Args:
            sentence_amplitudes: Sentence encoding
        
        Returns:
            Class index
        """
        if not self.weights:
            self.initialize()
        
        scores = []
        for w in self.weights:
            score = sum(w[i] * abs(sentence_amplitudes[i])
                       for i in range(min(len(w), len(sentence_amplitudes))))
            scores.append(score)
        
        return scores.index(max(scores))


class QuantumNLP:
    """
    Unified quantum NLP controller.
    """
    
    def __init__(self, dim: int = 8, num_classes: int = 2):
        self.word_encoder = QuantumWordEncoder(dim)
        self.sentence_encoder = QuantumSentenceEncoder(dim)
        self.attention = QuantumTextAttention(dim)
        self.classifier = QuantumTextClassifier(dim, num_classes)
    
    def encode_document(self, sentences: List[str]) -> List[List[complex]]:
        """
        Encode document.
        
        Args:
            sentences: Sentences
        
        Returns:
            Encoded sentences
        """
        return [self.sentence_encoder.encode_sentence(s) for s in sentences]
    
    def classify_text(self, text: str) -> int:
        """
        Classify text.
        
        Args:
            text: Text
        
        Returns:
            Class
        """
        sentences = text.split(".")
        encodings = self.encode_document([s.strip() for s in sentences if s.strip()])
        
        if not encodings:
            return 0
        
        # Use first sentence as query, attend over all
        query = encodings[0]
        attended = self.attention.attend(query, encodings, encodings)
        
        return self.classifier.classify(attended)
    
    def qnlp_summary(self) -> Dict:
        """Get summary."""
        return {
            "vocab_size": len(self.word_encoder.vocabulary),
            "dim": self.word_encoder.dim,
            "classes": self.classifier.classes
        }
