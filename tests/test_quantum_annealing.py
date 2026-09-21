"""
Unit tests for quantum annealing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_annealing import (SpinConfiguration, IsingModel,
                               QUBO,
                               SimulatedAnnealing,
                               QuantumAnnealing,
                               QuantumAnnealingController)


class TestIsingModel(unittest.TestCase):
    """Test Ising."""
    
    def setUp(self):
        self.ising = IsingModel(3)
        self.ising.set_coupling(0, 1, -1.0)
        self.ising.set_field(0, 0.5)
    
    def test_energy(self):
        """Should compute energy."""
        spins = [1, 1, -1]
        E = self.ising.energy(spins)
        self.assertIsInstance(E, float)
        print(f"  [PASS] E: {E:.2f}")
    
    def test_ground_state(self):
        """Should find ground state."""
        gs = self.ising.ground_state()
        self.assertIsInstance(gs.energy, float)
        print(f"  [PASS] GS: E={gs.energy:.2f}")


class TestQUBO(unittest.TestCase):
    """Test QUBO."""
    
    def setUp(self):
        self.qubo = QUBO(3)
        self.qubo.set_coefficient(0, 0, -1.0)
        self.qubo.set_coefficient(0, 1, 2.0)
    
    def test_energy(self):
        """Should compute energy."""
        x = [1, 0, 1]
        E = self.qubo.energy(x)
        self.assertIsInstance(E, float)
        print(f"  [PASS] E: {E:.2f}")
    
    def test_to_ising(self):
        """Should convert."""
        ising = self.qubo.to_ising()
        self.assertEqual(ising.num_spins, 3)
        print("  [PASS] Conv")


class TestSimulatedAnnealing(unittest.TestCase):
    """Test SA."""
    
    def setUp(self):
        self.ising = IsingModel(4)
        self.ising.set_coupling(0, 1, -1.0)
        self.ising.set_coupling(1, 2, -1.0)
        self.ising.set_coupling(2, 3, -1.0)
        self.sa = SimulatedAnnealing(self.ising, 5.0, 0.9, 500)
    
    def test_solve(self):
        """Should solve."""
        sol = self.sa.solve()
        self.assertEqual(len(sol.spins), 4)
        print(f"  [PASS] SA: E={sol.energy:.2f}")


class TestQuantumAnnealing(unittest.TestCase):
    """Test QA."""
    
    def setUp(self):
        self.ising = IsingModel(4)
        self.ising.set_coupling(0, 1, -1.0)
        self.qa = QuantumAnnealing(self.ising)
    
    def test_tunnel(self):
        """Should compute tunneling."""
        p = self.qa.tunneling_probability(1.0, 0.5)
        self.assertGreater(p, 0)
        print(f"  [PASS] T: {p:.4f}")
    
    def test_solve(self):
        """Should solve."""
        sol = self.qa.solve()
        self.assertEqual(len(sol.spins), 4)
        print(f"  [PASS] QA: E={sol.energy:.2f}")


class TestQuantumAnnealingController(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qac = QuantumAnnealingController(4)
    
    def test_summary(self):
        """Should summarize."""
        s = self.qac.qa_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
