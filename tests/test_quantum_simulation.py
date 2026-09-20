"""
Unit tests for quantum simulation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_simulation import (QuantumState, StateVectorSimulator,
                                DensityMatrixSimulator,
                                NoiseModel,
                                CircuitBuilder,
                                QuantumSimulation)


class TestStateVectorSimulator(unittest.TestCase):
    """Test statevector."""
    
    def setUp(self):
        self.sim = StateVectorSimulator(2)
    
    def test_init(self):
        """Should initialize."""
        self.assertEqual(len(self.sim.state.amplitudes), 4)
        print("  [PASS] Init")
    
    def test_x(self):
        """Should apply X."""
        self.sim.apply_x(0)
        self.assertAlmostEqual(abs(self.sim.state.amplitudes[1]), 1.0, places=5)
        print("  [PASS] X")
    
    def test_h(self):
        """Should apply H."""
        self.sim.apply_h(0)
        norm = sum(abs(a)**2 for a in self.sim.state.amplitudes)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print("  [PASS] H")
    
    def test_cnot(self):
        """Should apply CNOT."""
        self.sim.apply_x(0)
        self.sim.apply_cnot(0, 1)
        self.assertAlmostEqual(abs(self.sim.state.amplitudes[3]), 1.0, places=5)
        print("  [PASS] CNOT")
    
    def test_measure(self):
        """Should measure."""
        c = self.sim.measure(100)
        self.assertEqual(sum(c.values()), 100)
        print(f"  [PASS] Meas: {c}")
    
    def test_expectation(self):
        """Should compute expectation."""
        obs = [[1.0, 0.0], [0.0, 2.0]]
        e = self.sim.expectation(obs)
        self.assertEqual(e, 1.0)
        print(f"  [PASS] Exp: {e}")


class TestDensityMatrixSimulator(unittest.TestCase):
    """Test density matrix."""
    
    def setUp(self):
        self.dm = DensityMatrixSimulator(2)
    
    def test_purity(self):
        """Should compute purity."""
        p = self.dm.purity()
        self.assertAlmostEqual(p, 1.0, places=5)
        print(f"  [PASS] Pur: {p}")
    
    def test_entropy(self):
        """Should compute entropy."""
        e = self.dm.von_neumann_entropy()
        self.assertGreaterEqual(e, 0)
        print(f"  [PASS] Ent: {e:.4f}")
    
    def test_depolarize(self):
        """Should apply depolarizing."""
        self.dm.apply_depolarizing(0, 0.1)
        p = self.dm.purity()
        self.assertLess(p, 1.0)
        print(f"  [PASS] Dep: {p:.4f}")


class TestNoiseModel(unittest.TestCase):
    """Test noise."""
    
    def setUp(self):
        self.nm = NoiseModel()
    
    def test_fidelity(self):
        """Should get fidelity."""
        f = self.nm.gate_fidelity("x")
        self.assertGreater(f, 0.99)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_coherence(self):
        """Should compute coherence limit."""
        c = self.nm.coherence_time_limit(1.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] Coh: {c:.6f}")


class TestCircuitBuilder(unittest.TestCase):
    """Test circuit builder."""
    
    def setUp(self):
        self.cb = CircuitBuilder(2)
    
    def test_build(self):
        """Should build and execute."""
        self.cb.h(0)
        self.cb.cnot(0, 1)
        sim = self.cb.execute()
        self.assertEqual(len(sim.state.amplitudes), 4)
        print("  [PASS] Cir")


class TestQuantumSimulation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qs = QuantumSimulation(2)
    
    def test_bell(self):
        """Should create Bell state."""
        sim = self.qs.bell_state()
        c = sim.measure(1000)
        self.assertIn(0, c)
        self.assertIn(3, c)
        print(f"  [PASS] Bell: {c}")
    
    def test_grover(self):
        """Should run Grover."""
        sim = self.qs.grover_search(3, 2)
        self.assertEqual(len(sim.state.amplitudes), 4)
        print("  [PASS] Grv")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qs.qsim_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
