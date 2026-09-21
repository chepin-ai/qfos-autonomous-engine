"""
Unit tests for quantum communication advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_communication_advanced import (BellPair, QuantumRepeater,
                                            EntanglementSwapping,
                                            QuantumNetwork,
                                            QuantumMemory,
                                            QuantumCommunicationAdvanced)


class TestQuantumRepeater(unittest.TestCase):
    """Test repeater."""
    
    def setUp(self):
        self.qr = QuantumRepeater()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.qr.segment_fidelity(50.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] F: {f:.4f}")
    
    def test_repeaters(self):
        """Should compute repeaters."""
        n = self.qr.num_repeaters(500.0)
        self.assertGreater(n, 0)
        print(f"  [PASS] N: {n}")
    
    def test_e2e(self):
        """Should compute end-to-end."""
        f = self.qr.end_to_end_fidelity(300.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] E2E: {f:.4f}")


class TestEntanglementSwapping(unittest.TestCase):
    """Test swapping."""
    
    def setUp(self):
        self.es = EntanglementSwapping()
    
    def test_swap(self):
        """Should swap fidelity."""
        f = self.es.swap_fidelity(0.9, 0.85)
        self.assertGreater(f, 0)
        print(f"  [PASS] F: {f:.4f}")
    
    def test_success(self):
        """Should compute success."""
        p = self.es.success_probability(0.8)
        self.assertAlmostEqual(p, 0.64, delta=0.01)
        print(f"  [PASS] P: {p:.2f}")


class TestQuantumNetwork(unittest.TestCase):
    """Test network."""
    
    def setUp(self):
        self.qn = QuantumNetwork()
    
    def test_diameter(self):
        """Should compute diameter."""
        d = self.qn.network_diameter(["A", "B", "C"], [("A", "B"), ("B", "C")])
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d}")
    
    def test_path(self):
        """Should compute path fidelity."""
        f = self.qn.path_fidelity(3, 0.9)
        self.assertGreater(f, 0)
        print(f"  [PASS] F: {f:.4f}")


class TestQuantumMemory(unittest.TestCase):
    """Test memory."""
    
    def setUp(self):
        self.qm = QuantumMemory()
    
    def test_storage(self):
        """Should compute storage fidelity."""
        f = self.qm.storage_fidelity(100.0)
        self.assertGreater(f, 0.5)
        print(f"  [PASS] F: {f:.4f}")
    
    def test_efficiency(self):
        """Should compute efficiency."""
        e = self.qm.memory_efficiency(80, 100)
        self.assertEqual(e, 0.8)
        print(f"  [PASS] Eff: {e:.2f}")


class TestQuantumCommunicationAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qca = QuantumCommunicationAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qca.communication_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
