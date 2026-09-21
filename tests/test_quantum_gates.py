"""
Unit tests for quantum gates module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_gates import (Gate, SingleQubitGates,
                           MultiQubitGates,
                           GateComposer,
                           QuantumGates)


class TestSingleQubitGates(unittest.TestCase):
    """Test single qubit gates."""
    
    def setUp(self):
        self.sg = SingleQubitGates()
    
    def test_x(self):
        """Should get X."""
        g = self.sg.get("X")
        self.assertEqual(g.name, "X")
        self.assertEqual(len(g.matrix), 2)
        print("  [PASS] X")
    
    def test_h(self):
        """Should get H."""
        g = self.sg.get("H")
        self.assertEqual(g.name, "H")
        print("  [PASS] H")
    
    def test_rx(self):
        """Should get RX."""
        g = self.sg.rx(math.pi)
        self.assertEqual(g.name, "RX")
        print("  [PASS] RX")
    
    def test_ry(self):
        """Should get RY."""
        g = self.sg.ry(math.pi / 2)
        self.assertEqual(g.name, "RY")
        print("  [PASS] RY")
    
    def test_rz(self):
        """Should get RZ."""
        g = self.sg.rz(math.pi / 4)
        self.assertEqual(g.name, "RZ")
        print("  [PASS] RZ")
    
    def test_phase(self):
        """Should get phase."""
        g = self.sg.phase(math.pi / 2)
        self.assertEqual(g.name, "P")
        print("  [PASS] P")


class TestMultiQubitGates(unittest.TestCase):
    """Test multi qubit gates."""
    
    def setUp(self):
        self.mg = MultiQubitGates()
    
    def test_cnot(self):
        """Should get CNOT."""
        g = self.mg.cnot()
        self.assertEqual(g.name, "CNOT")
        self.assertEqual(len(g.matrix), 4)
        print("  [PASS] CNOT")
    
    def test_cz(self):
        """Should get CZ."""
        g = self.mg.cz()
        self.assertEqual(g.name, "CZ")
        print("  [PASS] CZ")
    
    def test_swap(self):
        """Should get SWAP."""
        g = self.mg.swap()
        self.assertEqual(g.name, "SWAP")
        print("  [PASS] SWAP")
    
    def test_toffoli(self):
        """Should get Toffoli."""
        g = self.mg.toffoli()
        self.assertEqual(g.name, "Toffoli")
        self.assertEqual(len(g.matrix), 8)
        print("  [PASS] Toffoli")


class TestGateComposer(unittest.TestCase):
    """Test composer."""
    
    def setUp(self):
        self.gc = GateComposer()
    
    def test_apply(self):
        """Should apply gate."""
        g = self.gc.single.get("X")
        s = self.gc.apply(g, [1.0, 0.0])
        self.assertEqual(s[0], 0.0)
        self.assertEqual(s[1], 1.0)
        print("  [PASS] Apply")
    
    def test_tensor(self):
        """Should tensor."""
        g = self.gc.tensor_product(self.gc.single.get("I"),
                                   self.gc.single.get("X"))
        self.assertEqual(g.num_qubits, 2)
        print("  [PASS] Tensor")
    
    def test_controlled(self):
        """Should create controlled."""
        g = self.gc.controlled(self.gc.single.get("X"))
        self.assertEqual(g.num_qubits, 2)
        print("  [PASS] Ctrl")


class TestQuantumGates(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qg = QuantumGates()
    
    def test_add(self):
        """Should add gate."""
        self.qg.add_gate(self.qg.single.get("H"))
        self.assertEqual(len(self.qg.circuit), 1)
        print("  [PASS] Add")
    
    def test_circuit(self):
        """Should apply circuit."""
        self.qg.add_gate(self.qg.single.get("X"))
        s = self.qg.apply_circuit([1.0, 0.0])
        self.assertEqual(s[1], 1.0)
        print("  [PASS] Circ")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qg.qg_summary()
        self.assertIn("single_qubit", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
