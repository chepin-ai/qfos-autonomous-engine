"""
Unit tests for quantum graph kernel advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_graph_kernel_advanced import (GraphNode, QuantumWalkGraphKernel,
                                           SpectralGraphKernel,
                                           QuantumGraphNeuralNetworkKernel,
                                           GraphIsomorphismTesting,
                                           QuantumGraphKernelAdvanced)


class TestQuantumWalkGraphKernel(unittest.TestCase):
    """Test QW."""
    
    def setUp(self):
        self.qwgk = QuantumWalkGraphKernel()
    
    def test_adjacency(self):
        """Should build adjacency."""
        a = self.qwgk.adjacency_matrix([(0, 1), (1, 2)], 3)
        self.assertEqual(a[0][1], 1.0)
        print(f"  [PASS] A: {len(a)}x{len(a)}")
    
    def test_kernel(self):
        """Should compute kernel."""
        a1 = [[0.0, 1.0], [1.0, 0.0]]
        k = self.qwgk.quantum_walk_kernel(a1, a1)
        self.assertGreater(k, 0)
        print(f"  [PASS] Kqw: {k:.4f}")


class TestSpectralGraphKernel(unittest.TestCase):
    """Test spectral."""
    
    def setUp(self):
        self.sg = SpectralGraphKernel()
    
    def test_degree(self):
        """Should compute degree."""
        a = [[0.0, 1.0], [1.0, 0.0]]
        d = self.sg.degree_matrix(a)
        self.assertEqual(d[0][0], 1.0)
        print(f"  [PASS] D: {d}")
    
    def test_laplacian(self):
        """Should compute Laplacian."""
        a = [[0.0, 1.0], [1.0, 0.0]]
        l = self.sg.graph_laplacian(a)
        self.assertEqual(l[0][0], 1.0)
        print(f"  [PASS] L: {l}")
    
    def test_spectral(self):
        """Should compute spectral kernel."""
        a = [[0.0, 1.0], [1.0, 0.0]]
        k = self.sg.spectral_kernel(a, a)
        self.assertEqual(k, 1.0)
        print(f"  [PASS] Kspec: {k:.4f}")


class TestQuantumGraphNeuralNetworkKernel(unittest.TestCase):
    """Test GNN."""
    
    def setUp(self):
        self.qgnnk = QuantumGraphNeuralNetworkKernel()
    
    def test_node(self):
        """Should compute node kernel."""
        k = self.qgnnk.node_embedding_kernel([[1.0, 0.0]], [[1.0, 0.0]])
        self.assertAlmostEqual(k, 1.0, delta=1e-10)
        print(f"  [PASS] Knode: {k:.4f}")
    
    def test_graph(self):
        """Should compute graph kernel."""
        k = self.qgnnk.graph_readout_kernel([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(k, 1.0, delta=1e-10)
        print(f"  [PASS] Kgraph: {k:.4f}")


class TestGraphIsomorphismTesting(unittest.TestCase):
    """Test iso."""
    
    def setUp(self):
        self.git = GraphIsomorphismTesting()
    
    def test_degree(self):
        """Should compute degrees."""
        a = [[0.0, 1.0], [1.0, 0.0]]
        d = self.git.degree_sequence(a)
        self.assertEqual(d, [1, 1])
        print(f"  [PASS] Deg: {d}")
    
    def test_iso(self):
        """Should check iso."""
        a = [[0.0, 1.0], [1.0, 0.0]]
        b = self.git.isomorphic_check(a, a)
        self.assertTrue(b)
        print(f"  [PASS] Iso: {b}")


class TestQuantumGraphKernelAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgka = QuantumGraphKernelAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qgka.graph_kernel_summary()
        self.assertIn("kernels", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
