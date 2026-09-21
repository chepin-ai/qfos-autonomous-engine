"""
Unit tests for quantum topology advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_topology_advanced import (BraidWord, BraidGroup,
                                       AnyonBraiding,
                                       TopologicalProtection,
                                       BraidGroupRepresentation,
                                       QuantumTopologyAdvanced)


class TestBraidGroup(unittest.TestCase):
    """Test braid."""
    
    def setUp(self):
        self.bg = BraidGroup(3)
    
    def test_commute(self):
        """Should check commutation."""
        self.assertTrue(self.bg.braid_relation(1, 3))
        print("  [PASS] Commute")
    
    def test_yang_baxter(self):
        """Should apply relation."""
        r = self.bg.yang_baxter(1)
        self.assertEqual(r, [2, 1, 2])
        print(f"  [PASS] YB: {r}")
    
    def test_length(self):
        """Should compute length."""
        b = BraidWord([1, 2, 1], 3)
        l = self.bg.braid_length(b)
        self.assertEqual(l, 3)
        print(f"  [PASS] Len: {l}")


class TestAnyonBraiding(unittest.TestCase):
    """Test anyon."""
    
    def setUp(self):
        self.ab = AnyonBraiding()
    
    def test_phase(self):
        """Should compute phase."""
        p = self.ab.exchange_phase(0.5, 2)
        self.assertEqual(p, 1.0)
        print(f"  [PASS] Phase: {p:.2f}")
    
    def test_fusion(self):
        """Should compute fusion."""
        f = self.ab.fusion_outcome(0.5, 0.5)
        self.assertEqual(len(f), 2)
        print(f"  [PASS] Fusion: {f}")
    
    def test_matrix(self):
        """Should compute element."""
        m = self.ab.braiding_matrix_element(1, 3)
        self.assertIsInstance(m, complex)
        print(f"  [PASS] Mat: {m}")


class TestTopologicalProtection(unittest.TestCase):
    """Test protection."""
    
    def setUp(self):
        self.tp = TopologicalProtection()
    
    def test_gap(self):
        """Should compute gap."""
        g = self.tp.energy_gap(1e-6)
        self.assertGreater(g, 0)
        print(f"  [PASS] Gap: {g:.4f}")
    
    def test_suppression(self):
        """Should compute suppression."""
        s = self.tp.logical_error_suppression(0.01, 1.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] Supp: {s:.6f}")


class TestBraidGroupRepresentation(unittest.TestCase):
    """Test representation."""
    
    def setUp(self):
        self.br = BraidGroupRepresentation()
    
    def test_jones(self):
        """Should compute Jones."""
        b = BraidWord([1, 2], 3)
        j = self.br.jones_representation(b)
        self.assertIsInstance(j, complex)
        print(f"  [PASS] Jones: {j}")
    
    def test_trace(self):
        """Should compute trace."""
        b = BraidWord([1, 2], 3)
        t = self.br.trace(b)
        self.assertGreater(t, 0)
        print(f"  [PASS] Tr: {t:.3f}")


class TestQuantumTopologyAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qta = QuantumTopologyAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qta.topology_summary()
        self.assertIn("concepts", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
