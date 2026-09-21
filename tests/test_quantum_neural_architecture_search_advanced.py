"""
Unit tests for quantum neural architecture search advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_neural_architecture_search_advanced import (ArchitectureConfig,
                                                         QuantumCellSearch,
                                                         QuantumLayerSearch,
                                                         QuantumTopologySearch,
                                                         QuantumHyperparameterOptimization,
                                                         QuantumNeuralArchitectureSearchAdvanced)


class TestQuantumCellSearch(unittest.TestCase):
    """Test cell."""
    
    def setUp(self):
        self.qcs = QuantumCellSearch()
    
    def test_score(self):
        """Should score cell."""
        s = self.qcs.cell_score(["rx", "ry"], 4, 4)
        self.assertGreater(s, 0)
        print(f"  [PASS] Score: {s:.4f}")
    
    def test_random(self):
        """Should generate random."""
        c = self.qcs.random_cell(4)
        self.assertEqual(len(c), 4)
        print(f"  [PASS] Cell: {c}")


class TestQuantumLayerSearch(unittest.TestCase):
    """Test layer."""
    
    def setUp(self):
        self.qls = QuantumLayerSearch()
    
    def test_complexity(self):
        """Should compute complexity."""
        c = self.qls.layer_complexity(4, 8, 16)
        self.assertGreater(c, 0)
        print(f"  [PASS] C: {c:.2f}")
    
    def test_search(self):
        """Should search size."""
        s = self.qls.search_layer_size(50.0, 4)
        self.assertGreaterEqual(s, 4)
        print(f"  [PASS] Size: {s}")


class TestQuantumTopologySearch(unittest.TestCase):
    """Test topology."""
    
    def setUp(self):
        self.qts = QuantumTopologySearch()
    
    def test_depth(self):
        """Should compute depth."""
        d = self.qts.topology_depth(4, 10)
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d}")
    
    def test_efficiency(self):
        """Should compute efficiency."""
        e = self.qts.topology_efficiency(4, 10, 5)
        self.assertGreater(e, 0)
        print(f"  [PASS] E: {e:.4f}")


class TestQuantumHyperparameterOptimization(unittest.TestCase):
    """Test hyperopt."""
    
    def setUp(self):
        self.qho = QuantumHyperparameterOptimization()
    
    def test_grid(self):
        """Should grid search."""
        p, s = self.qho.grid_search({"lr": [0.01, 0.1]}, lambda x: x["lr"])
        self.assertEqual(p["lr"], 0.1)
        print(f"  [PASS] Grid: {p}, S: {s:.4f}")
    
    def test_random(self):
        """Should random search."""
        p, s = self.qho.random_search({"lr": (0.01, 0.1)}, lambda x: x["lr"], 5)
        self.assertIn("lr", p)
        print(f"  [PASS] Rand: {p}")


class TestQuantumNeuralArchitectureSearchAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qnas = QuantumNeuralArchitectureSearchAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qnas.nas_summary()
        self.assertIn("search_spaces", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
