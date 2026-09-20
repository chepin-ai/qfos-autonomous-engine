"""
Unit tests for quantum NLP module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_natural_language_processing import (QuantumTokenizer,
                                                  QuantumSentenceEmbedding,
                                                  QuantumTextClassifier,
                                                  QuantumSemanticSimilarity,
                                                  QuantumNLP)


class TestQuantumTokenizer(unittest.TestCase):
    """Test tokenizer."""
    
    def setUp(self):
        self.tok = QuantumTokenizer()
    
    def test_tokenize(self):
        """Should tokenize."""
        t = self.tok.tokenize("hello")
        self.assertGreater(len(t), 0)
        print(f"  [PASS] Tok: {t}")
    
    def test_encode(self):
        """Should encode."""
        e = self.tok.encode("hi", 8)
        self.assertEqual(len(e), 8)
        print(f"  [PASS] Enc: {e}")


class TestQuantumSentenceEmbedding(unittest.TestCase):
    """Test embedding."""
    
    def setUp(self):
        self.emb = QuantumSentenceEmbedding(8)
    
    def test_embed(self):
        """Should embed."""
        e = self.emb.embed([1, 2, 3, 4])
        self.assertEqual(len(e), 8)
        norm = sum(x**2 for x in e) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Emb: norm={norm:.4f}")


class TestQuantumTextClassifier(unittest.TestCase):
    """Test classifier."""
    
    def setUp(self):
        self.clf = QuantumTextClassifier(2)
    
    def test_predict(self):
        """Should predict."""
        p = self.clf.predict([0.5, -0.5, 0.0, 0.0])
        self.assertIn(p, [0, 1])
        print(f"  [PASS] Pred: {p}")
    
    def test_classify(self):
        """Should classify text."""
        tok = QuantumTokenizer()
        emb = QuantumSentenceEmbedding()
        c = self.clf.classify("test", tok, emb)
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Clf: {c}")


class TestQuantumSemanticSimilarity(unittest.TestCase):
    """Test similarity."""
    
    def setUp(self):
        self.sim = QuantumSemanticSimilarity()
    
    def test_cosine(self):
        """Should compute cosine."""
        s = self.sim.cosine_similarity([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(s, 1.0, places=5)
        print(f"  [PASS] Cos: {s:.4f}")
    
    def test_kernel(self):
        """Should compute kernel."""
        s = self.sim.quantum_kernel_similarity([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(s, 1.0, places=5)
        print(f"  [PASS] Kern: {s:.4f}")
    
    def test_compare(self):
        """Should compare texts."""
        tok = QuantumTokenizer()
        emb = QuantumSentenceEmbedding()
        r = self.sim.compare("hello", "hello", tok, emb)
        self.assertIn("cosine", r)
        print(f"  [PASS] Cmp: {r}")


class TestQuantumNLP(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qnlp = QuantumNLP()
    
    def test_encode(self):
        """Should encode."""
        e = self.qnlp.encode_text("hello world")
        self.assertEqual(len(e), 8)
        print("  [PASS] Enc")
    
    def test_classify(self):
        """Should classify."""
        c = self.qnlp.classify("positive text")
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Clf: {c}")
    
    def test_compare(self):
        """Should compare."""
        r = self.qnlp.compare("hello", "world")
        self.assertIn("cosine", r)
        print(f"  [PASS] Cmp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qnlp.qnlp_summary()
        self.assertIn("vocab_size", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
