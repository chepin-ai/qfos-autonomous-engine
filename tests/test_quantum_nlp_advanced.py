"""
Unit tests for quantum NLP advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_nlp_advanced import (QuantumWord, QuantumWordEmbeddings,
                                  QuantumSentenceClassification,
                                  QuantumSemanticSimilarity,
                                  QuantumLanguageModeling,
                                  QuantumNLPAdvanced)


class TestQuantumWordEmbeddings(unittest.TestCase):
    """Test embeddings."""
    
    def setUp(self):
        self.qwe = QuantumWordEmbeddings()
    
    def test_encode(self):
        """Should encode word."""
        v = self.qwe.encode_word("test")
        self.assertEqual(len(v), 8)
        norm = sum(x**2 for x in v) ** 0.5
        self.assertAlmostEqual(norm, 1.0, delta=1e-6)
        print(f"  [PASS] Enc: {len(v)}D, norm={norm:.4f}")
    
    def test_sim(self):
        """Should compute similarity."""
        s = self.qwe.word_similarity("hello", "hello")
        self.assertAlmostEqual(s, 1.0, delta=1e-6)
        print(f"  [PASS] Sim: {s:.4f}")


class TestQuantumSentenceClassification(unittest.TestCase):
    """Test classify."""
    
    def setUp(self):
        self.qsc = QuantumSentenceClassification()
        self.qwe = QuantumWordEmbeddings()
    
    def test_train(self):
        """Should train."""
        self.qsc.train(0, ["good product", "nice item"], self.qwe)
        self.assertIn(0, self.qsc.class_vectors)
        print(f"  [PASS] Train: {len(self.qsc.class_vectors)} classes")
    
    def test_classify(self):
        """Should classify."""
        self.qsc.train(0, ["good product"], self.qwe)
        self.qsc.train(1, ["bad product"], self.qwe)
        c = self.qsc.classify("good", self.qwe)
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Cls: {c}")


class TestQuantumSemanticSimilarity(unittest.TestCase):
    """Test similarity."""
    
    def setUp(self):
        self.qss = QuantumSemanticSimilarity()
        self.qwe = QuantumWordEmbeddings()
    
    def test_embed(self):
        """Should embed sentence."""
        v = self.qss.sentence_embedding("hello world", self.qwe)
        self.assertEqual(len(v), 8)
        print(f"  [PASS] SE: {len(v)}D")
    
    def test_similarity(self):
        """Should compute similarity."""
        s = self.qss.similarity("hello world", "hello world", self.qwe)
        self.assertAlmostEqual(s, 1.0, delta=1e-6)
        print(f"  [PASS] Sim: {s:.4f}")


class TestQuantumLanguageModeling(unittest.TestCase):
    """Test LM."""
    
    def setUp(self):
        self.qlm = QuantumLanguageModeling()
    
    def test_prob(self):
        """Should compute probability."""
        p = self.qlm.ngram_probability(["hello", "world", "test"])
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.4f}")
    
    def test_perplexity(self):
        """Should compute perplexity."""
        pp = self.qlm.perplexity(["hello", "world", "test"])
        self.assertGreater(pp, 0)
        print(f"  [PASS] PP: {pp:.2f}")


class TestQuantumNLPAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qnlp = QuantumNLPAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qnlp.nlp_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
