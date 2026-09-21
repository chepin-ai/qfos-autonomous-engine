"""
Unit tests for quantum walks advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_walks_advanced import (WalkState, ContinuousTimeQuantumWalk,
                                    MultiParticleQuantumWalk,
                                    QuantumWalkSearch,
                                    HittingTimeAnalysis,
                                    QuantumWalksAdvanced)


class TestContinuousTimeQuantumWalk(unittest.TestCase):
    """Test CTQW."""
    
    def setUp(self):
        self.ctqw = ContinuousTimeQuantumWalk(5, 1.0)
    
    def test_adjacency(self):
        """Should create adjacency."""
        A = self.ctqw.adjacency_line()
        self.assertEqual(A[0][1], 1.0)
        print("  [PASS] Adj")
    
    def test_hamiltonian(self):
        """Should compute H."""
        A = self.ctqw.adjacency_line()
        H = self.ctqw.hamiltonian(A)
        self.assertEqual(H[0][1], -1.0)
        print("  [PASS] H")
    
    def test_propagate(self):
        """Should propagate."""
        s0 = [1.0, 0.0, 0.0, 0.0, 0.0]
        s = self.ctqw.propagate(s0, 1.0)
        self.assertEqual(len(s), 5)
        print("  [PASS] Prop")
    
    def test_variance(self):
        """Should compute variance."""
        p = [0.2, 0.3, 0.3, 0.1, 0.1]
        v = self.ctqw.variance(p)
        self.assertGreater(v, 0)
        print(f"  [PASS] Var: {v:.3f}")


class TestMultiParticleQuantumWalk(unittest.TestCase):
    """Test multi-particle."""
    
    def setUp(self):
        self.mp = MultiParticleQuantumWalk(4, 2)
    
    def test_size(self):
        """Should compute size."""
        s = self.mp.state_space_size()
        self.assertEqual(s, 16)
        print(f"  [PASS] Size: {s}")
    
    def test_joint(self):
        """Should compute joint prob."""
        p = [0.25, 0.25, 0.25, 0.25]
        j = self.mp.joint_probability([0, 1], p)
        self.assertEqual(j, 0.0625)
        print(f"  [PASS] Joint: {j:.4f}")


class TestQuantumWalkSearch(unittest.TestCase):
    """Test search."""
    
    def setUp(self):
        self.qws = QuantumWalkSearch(100)
    
    def test_steps(self):
        """Should compute steps."""
        s = self.qws.optimal_steps(1)
        self.assertGreater(s, 0)
        print(f"  [PASS] Steps: {s}")
    
    def test_probability(self):
        """Should compute prob."""
        p = self.qws.success_probability(8, 1)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.3f}")


class TestHittingTimeAnalysis(unittest.TestCase):
    """Test hitting."""
    
    def setUp(self):
        self.ht = HittingTimeAnalysis()
    
    def test_classical(self):
        """Should compute classical."""
        t = self.ht.classical_hitting_time(10)
        self.assertGreater(t, 0)
        print(f"  [PASS] Tc: {t:.1f}")
    
    def test_quantum(self):
        """Should compute quantum."""
        t = self.ht.quantum_hitting_time(10)
        self.assertGreater(t, 0)
        print(f"  [PASS] Tq: {t:.3f}")


class TestQuantumWalksAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qwa = QuantumWalksAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qwa.walks_summary()
        self.assertIn("types", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
