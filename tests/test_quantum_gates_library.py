"""
Unit tests for quantum gates library module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_gates_library import (Gate, SingleQubitGates,
                                   TwoQubitGates,
                                   GateDecomposer,
                                   GateComposer,
                                   QuantumGatesLibrary)


class TestSingleQubitGates(unittest.TestCase):
    """Test single-qubit gates."""
    
    def setUp(self):
        self.g = SingleQubitGates()
    
    def test_identity(self):
        """Should be identity."""
        I = self.g.I()
        self.assertEqual(I.matrix[0][0], 1.0)
        print("  [PASS] I")
    
    def test_pauli_x(self):
        """Should be X."""
        X = self.g.X()
        self.assertEqual(X.matrix[0][1], 1.0)
        print("  [PASS] X")
    
    def test_hadamard(self):
        """Should be H."""
        H = self.g.H()
        s = 1.0 / (2.0 ** 0.5)
        self.assertAlmostEqual(H.matrix[0][0].real, s, places=5)
        print("  [PASS] H")
    
    def test_rotation(self):
        """Should be rotation."""
        Rx = self.g.Rx(math.pi)
        self.assertAlmostEqual(Rx.matrix[0][0].real, 0.0, places=5)
        print("  [PASS] Rx")


class TestTwoQubitGates(unittest.TestCase):
    """Test two-qubit gates."""
    
    def setUp(self):
        self.g = TwoQubitGates()
    
    def test_cnot(self):
        """Should be CNOT."""
        C = self.g.CNOT()
        self.assertEqual(len(C.matrix), 4)
        print("  [PASS] CNOT")
    
    def test_cz(self):
        """Should be CZ."""
        C = self.g.CZ()
        self.assertEqual(C.matrix[3][3], -1.0)
        print("  [PASS] CZ")
    
    def test_swap(self):
        """Should be SWAP."""
        S = self.g.SWAP()
        self.assertEqual(S.matrix[1][2], 1.0)
        print("  [PASS] SWAP")


class TestGateDecomposer(unittest.TestCase):
    """Test decomposer."""
    
    def setUp(self):
        self.d = GateDecomposer()
    
    def test_decompose(self):
        """Should decompose."""
        gates = self.d.decompose_rx_ry_rz([[1.0, 0.0], [0.0, 1.0]])
        self.assertEqual(len(gates), 3)
        print(f"  [PASS] Dec: {len(gates)} gates")


class TestGateComposer(unittest.TestCase):
    """Test composer."""
    
    def setUp(self):
        self.c = GateComposer()
    
    def test_bell(self):
        """Should create Bell circuit."""
        gates = self.c.bell_state_circuit()
        self.assertEqual(len(gates), 2)
        print(f"  [PASS] Bell: {len(gates)} gates")
    
    def test_ghz(self):
        """Should create GHZ circuit."""
        gates = self.c.ghz_circuit(3)
        self.assertEqual(len(gates), 3)
        print(f"  [PASS] GHZ: {len(gates)} gates")
    
    def test_qft(self):
        """Should create QFT circuit."""
        gates = self.c.qft_circuit(2)
        self.assertGreater(len(gates), 0)
        print(f"  [PASS] QFT: {len(gates)} gates")


class TestQuantumGatesLibrary(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgl = QuantumGatesLibrary()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qgl.gate_summary()
        self.assertIn("single_qubit", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
