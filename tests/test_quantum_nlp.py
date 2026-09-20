"""
Unit tests for quantum NLP module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_nlp import (QuantumWordEmbedding, QuantumWordEncoder,
                         QuantumSentenceEncoder,
                         QuantumTextAttention,
                         QuantumTextClassifier,
                         QuantumNLP)


class TestQuantumWordEncoder(unittest.TestCase):
    """Test word encoder."""
    
    def setUp(self):
        self.we = QuantumWordEncoder(4)
    
    def test_encode(self):
        """Should encode word."""
        e = self.we.encode_word("test")
        self.assertEqual(len(e.amplitudes), 4)
        print("  [PASS] Enc")
    
    def test_similarity(self):
        """Should compute similarity."""
        s = self.we.word_similarity("hello", "hello")
        self.assertAlmostEqual(s, 1.0, places=5)
        print(f"  [PASS] Sim: {s:.4f}")


class TestQuantumSentenceEncoder(unittest.TestCase):
    """Test sentence encoder."""
    
    def setUp(self):
        self.se = QuantumSentenceEncoder(4)
    
    def test_encode(self):
        """Should encode sentence."""
        a = self.se.encode_sentence("hello world")
        self.assertEqual(len(a), 4)
        print("  [PASS] Sent")


class TestQuantumTextAttention(unittest.TestCase):
    """Test attention."""
    
    def setUp(self):
        self.attn = QuantumTextAttention(4)
    
    def test_weights(self):
        """Should compute weights."""
        q = [1.0, 0.0, 0.0, 0.0]
        k = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
        w = self.attn.attention_weights(q, k)
        self.assertAlmostEqual(sum(w), 1.0, places=5)
        print(f"  [PASS] Wt: {w}")
    
    def test_attend(self):
        """Should attend."""
        q = [1.0, 0.0, 0.0, 0.0]
        k = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
        v = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
        o = self.attn.attend(q, k, v)
        self.assertEqual(len(o), 4)
        print("  [PASS] Attn")


class TestQuantumTextClassifier(unittest.TestCase):
    """Test classifier."""
    
    def setUp(self):
        self.clf = QuantumTextClassifier(4, 2)
    
    def test_classify(self):
        """Should classify."""
        self.clf.initialize()
        c = self.clf.classify([1.0, 0.0, 0.0, 0.0])
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Cls: {c}")


class TestQuantumNLP(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qnlp = QuantumNLP(4, 2)
    
    def test_encode_doc(self):
        """Should encode document."""
        e = self.qnlp.encode_document(["hello world", "test sentence"])
        self.assertEqual(len(e), 2)
        print("  [PASS] Doc")
    
    def test_classify(self):
        """Should classify text."""
        c = self.qnlp.classify_text("hello world")
        self.assertIn(c, [0, 1])
        print(f"  [PASS] Cls: {c}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qnlp.qnlp_summary()
        self.assertIn("vocab_size", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
