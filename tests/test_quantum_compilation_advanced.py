"""
Unit tests for quantum compilation advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_compilation_advanced import (Gate, GateDecomposition,
                                          CircuitOptimization,
                                          QubitRouting,
                                          LayoutSynthesis,
                                          QuantumCompilationAdvanced)


class TestGateDecomposition(unittest.TestCase):
    """Test decomposition."""
    
    def setUp(self):
        self.gd = GateDecomposition()
    
    def test_toffoli(self):
        """Should decompose Toffoli."""
        g = self.gd.toffoli_decomposition(0, 1, 2)
        self.assertGreater(len(g), 0)
        print(f"  [PASS] Toff: {len(g)} gates")
    
    def test_rotation(self):
        """Should decompose rotation."""
        g = self.gd.controlled_rotation(0, 1, 0.5)
        self.assertEqual(len(g), 1)
        print(f"  [PASS] CR: {g[0].name}")


class TestCircuitOptimization(unittest.TestCase):
    """Test optimization."""
    
    def setUp(self):
        self.co = CircuitOptimization()
    
    def test_cancel(self):
        """Should cancel CNOTs."""
        gates = [Gate("CNOT", [0, 1], []), Gate("CNOT", [0, 1], [])]
        o = self.co.cancel_adjacent_cnots(gates)
        self.assertEqual(len(o), 0)
        print(f"  [PASS] Cancel: {len(o)}")
    
    def test_merge(self):
        """Should merge rotations."""
        gates = [Gate("RZ", [0], [0.1]), Gate("RZ", [0], [0.2])]
        o = self.co.merge_rotations(gates)
        self.assertEqual(len(o), 1)
        print(f"  [PASS] Merge: {o[0].params}")
    
    def test_count(self):
        """Should count gates."""
        c = self.co.gate_count([Gate("X", [0], []), Gate("H", [0], [])])
        self.assertEqual(c, 2)
        print(f"  [PASS] Count: {c}")


class TestQubitRouting(unittest.TestCase):
    """Test routing."""
    
    def setUp(self):
        self.qr = QubitRouting()
    
    def test_swap(self):
        """Should insert SWAP."""
        s = self.qr.swap_insertion((0, 2), [(0, 1), (1, 2)])
        self.assertEqual(len(s), 1)
        print(f"  [PASS] Swap: {s}")
    
    def test_depth(self):
        """Should compute depth."""
        d = self.qr.routing_depth(2)
        self.assertEqual(d, 16)
        print(f"  [PASS] Depth: {d}")


class TestLayoutSynthesis(unittest.TestCase):
    """Test layout."""
    
    def setUp(self):
        self.ls = LayoutSynthesis()
    
    def test_trivial(self):
        """Should create layout."""
        l = self.ls.trivial_layout(3, 5)
        self.assertEqual(l, [0, 1, 2])
        print(f"  [PASS] Lay: {l}")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.ls.layout_fidelity([0, 1, 2], [(0, 1)], [(0, 1), (1, 2)])
        self.assertEqual(f, 1.0)
        print(f"  [PASS] Fid: {f:.2f}")


class TestQuantumCompilationAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qca = QuantumCompilationAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qca.compilation_summary()
        self.assertIn("stages", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
