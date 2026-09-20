"""
Unit tests for quantum transformers module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_transformers import (QuantumToken, QuantumSelfAttention,
                                  QuantumMultiHeadAttention,
                                  QuantumPositionalEncoding,
                                  QuantumTransformerBlock,
                                  QuantumTransformers)


class TestQuantumSelfAttention(unittest.TestCase):
    """Test attention."""
    
    def setUp(self):
        self.attn = QuantumSelfAttention(4)
    
    def test_score(self):
        """Should compute score."""
        q = [1.0, 0.0, 0.0, 0.0]
        k = [1.0, 0.0, 0.0, 0.0]
        s = self.attn.attention_score(q, k)
        self.assertAlmostEqual(s, 1.0, places=5)
        print(f"  [PASS] Score: {s:.4f}")
    
    def test_apply(self):
        """Should apply attention."""
        tokens = [QuantumToken([1.0, 0.0, 0.0, 0.0], 0),
                  QuantumToken([0.0, 1.0, 0.0, 0.0], 1)]
        out = self.attn.apply(tokens)
        self.assertEqual(len(out), 2)
        print("  [PASS] Attn")


class TestQuantumMultiHeadAttention(unittest.TestCase):
    """Test multi-head."""
    
    def setUp(self):
        self.mha = QuantumMultiHeadAttention(4, 2)
    
    def test_apply(self):
        """Should apply multi-head."""
        tokens = [QuantumToken([1.0, 0.0, 0.0, 0.0], 0),
                  QuantumToken([0.0, 1.0, 0.0, 0.0], 1)]
        out = self.mha.apply(tokens)
        self.assertEqual(len(out), 2)
        print("  [PASS] MHA")


class TestQuantumPositionalEncoding(unittest.TestCase):
    """Test encoding."""
    
    def setUp(self):
        self.pe = QuantumPositionalEncoding(4)
    
    def test_encode(self):
        """Should encode position."""
        e = self.pe.encode(0)
        self.assertEqual(len(e), 4)
        print("  [PASS] Enc")
    
    def test_add(self):
        """Should add position."""
        tokens = [QuantumToken([1.0, 0.0, 0.0, 0.0], 0)]
        out = self.pe.add_position(tokens)
        self.assertEqual(len(out), 1)
        print("  [PASS] Add")


class TestQuantumTransformerBlock(unittest.TestCase):
    """Test block."""
    
    def setUp(self):
        self.block = QuantumTransformerBlock(4, 2)
    
    def test_forward(self):
        """Should forward."""
        tokens = [QuantumToken([1.0, 0.0, 0.0, 0.0], 0),
                  QuantumToken([0.0, 1.0, 0.0, 0.0], 1)]
        out = self.block.forward(tokens)
        self.assertEqual(len(out), 2)
        print("  [PASS] Fwd")


class TestQuantumTransformers(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qt = QuantumTransformers(4, 2, 2)
    
    def test_encode(self):
        """Should encode."""
        tokens = [QuantumToken([1.0, 0.0, 0.0, 0.0], 0),
                  QuantumToken([0.0, 1.0, 0.0, 0.0], 1)]
        out = self.qt.encode(tokens)
        self.assertEqual(len(out), 2)
        print("  [PASS] Enc")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qt.qt_summary()
        self.assertIn("layers", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
