"""
Unit tests for quantum simulation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_simulation import (QuantumState, StateVectorSimulator,
                                DensityMatrixSimulator,
                                HamiltonianSimulator,
                                QuantumSimulation)


class TestStateVectorSimulator(unittest.TestCase):
    """Test state vector."""
    
    def setUp(self):
        self.sv = StateVectorSimulator(2)
    
    def test_initial_state(self):
        """Should start in |00>."""
        self.assertEqual(abs(self.sv.state.amplitudes[0]), 1.0)
        print("  [PASS] |00>")
    
    def test_measure(self):
        """Should measure."""
        m = self.sv.measure(0)
        self.assertIn(m, [0, 1])
        print(f"  [PASS] M: {m}")
    
    def test_expectation(self):
        """Should compute expectation."""
        z = [[1.0, 0.0, 0.0, 0.0],
             [0.0, -1.0, 0.0, 0.0],
             [0.0, 0.0, -1.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]]
        e = self.sv.expectation(z)
        self.assertEqual(e, 1.0)
        print(f"  [PASS] Exp: {e}")


class TestDensityMatrixSimulator(unittest.TestCase):
    """Test density matrix."""
    
    def setUp(self):
        self.dm = DensityMatrixSimulator(2)
    
    def test_trace(self):
        """Should have trace 1."""
        t = self.dm.trace()
        self.assertAlmostEqual(t, 1.0)
        print(f"  [PASS] Tr: {t}")
    
    def test_purity(self):
        """Should compute purity."""
        p = self.dm.purity()
        self.assertAlmostEqual(p, 1.0)
        print(f"  [PASS] Pur: {p}")


class TestHamiltonianSimulator(unittest.TestCase):
    """Test Hamiltonian."""
    
    def setUp(self):
        self.hs = HamiltonianSimulator()
    
    def test_energy(self):
        """Should compute energy."""
        state = QuantumState([complex(1.0, 0.0), complex(0.0)])
        H = [[1.0, 0.0], [0.0, -1.0]]
        e = self.hs.energy(state, H)
        self.assertEqual(e, 1.0)
        print(f"  [PASS] E: {e}")
    
    def test_time_evolve(self):
        """Should evolve."""
        state = QuantumState([complex(1.0, 0.0), complex(0.0)])
        H = [[1.0, 0.0], [0.0, -1.0]]
        ev = self.hs.time_evolve(state, H, 0.01, 10)
        self.assertAlmostEqual(ev.norm(), 1.0, places=5)
        print("  [PASS] Ev")


class TestQuantumSimulation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qs = QuantumSimulation(2)
    
    def test_summary(self):
        """Should summarize."""
        s = self.qs.qs_summary()
        self.assertIn("simulators", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
