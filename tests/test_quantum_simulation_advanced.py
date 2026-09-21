"""
Unit tests for quantum simulation advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_simulation_advanced import (HamiltonianTerm, TrotterSuzuki,
                                         VariationalQuantumSimulator,
                                         QuantumImaginaryTimeEvolution,
                                         LindbladianDynamics,
                                         QuantumSimulationAdvanced)


class TestTrotterSuzuki(unittest.TestCase):
    """Test Trotter."""
    
    def setUp(self):
        self.ts = TrotterSuzuki(2)
    
    def test_steps(self):
        """Should compute steps."""
        n = self.ts.trotter_step_count(1.0, 1e-3, 10.0)
        self.assertGreater(n, 0)
        print(f"  [PASS] Steps: {n}")
    
    def test_first_order(self):
        """Should apply step."""
        s = self.ts.first_order_step([1.0, 0.0], [HamiltonianTerm(1.0, ["Z"], [0])], 0.1)
        self.assertEqual(len(s), 2)
        print(f"  [PASS] State: {s}")


class TestVariationalQuantumSimulator(unittest.TestCase):
    """Test VQS."""
    
    def setUp(self):
        self.vqs = VariationalQuantumSimulator(2)
    
    def test_ansatz(self):
        """Should generate state."""
        s = self.vqs.ansatz_state([0.5, 0.5])
        self.assertEqual(len(s), 4)
        print(f"  [PASS] Dim: {len(s)}")
    
    def test_energy(self):
        """Should compute energy."""
        e = self.vqs.energy_expectation([1.0, 0.0], lambda s: sum(s))
        self.assertIsInstance(e, float)
        print(f"  [PASS] E: {e:.4f}")


class TestQuantumImaginaryTimeEvolution(unittest.TestCase):
    """Test QITE."""
    
    def setUp(self):
        self.qite = QuantumImaginaryTimeEvolution()
    
    def test_propagator(self):
        """Should compute propagator."""
        p = self.qite.imaginary_propagator(1.0, 0.1)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.4f}")
    
    def test_ground(self):
        """Should approximate ground state."""
        e = self.qite.ground_state_approximation([0.0, 1.0, 2.0], [1.0, 1.0, 1.0], 10.0)
        self.assertGreater(e, 0)
        print(f"  [PASS] E0: {e:.4f}")


class TestLindbladianDynamics(unittest.TestCase):
    """Test Lindblad."""
    
    def setUp(self):
        self.ld = LindbladianDynamics()
    
    def test_decay(self):
        """Should compute decay."""
        p = self.ld.decay_probability(1.0, 1.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.4f}")
    
    def test_dephasing(self):
        """Should compute dephasing."""
        f = self.ld.dephasing_factor(1.0, 1.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] F: {f:.4f}")


class TestQuantumSimulationAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qsa = QuantumSimulationAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qsa.simulation_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
