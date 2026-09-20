"""
Unit tests for quantum adiabatic optimization module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_adiabatic_optimization import (Hamiltonian,
                                            GroundStateSolver,
                                            AdiabaticEvolution,
                                            QuantumAdiabaticOptimization)


class TestHamiltonian(unittest.TestCase):
    """Test Hamiltonian."""
    
    def setUp(self):
        self.H = Hamiltonian(3)
    
    def test_initial(self):
        """Should create initial H."""
        H0 = self.H.initial_hamiltonian()
        self.assertEqual(len(H0), 8)
        print("  [PASS] H0")
    
    def test_problem(self):
        """Should create problem H."""
        cost = lambda x: x
        H1 = self.H.problem_hamiltonian(cost)
        self.assertEqual(len(H1), 8)
        print("  [PASS] H1")
    
    def test_interpolate(self):
        """Should interpolate."""
        H0 = self.H.initial_hamiltonian()
        H1 = self.H.problem_hamiltonian(lambda x: x)
        Hs = self.H.interpolate(H0, H1, 0.5)
        self.assertEqual(len(Hs), 8)
        print("  [PASS] H(s)")


class TestGroundStateSolver(unittest.TestCase):
    """Test solver."""
    
    def setUp(self):
        self.solver = GroundStateSolver()
    
    def test_power_iteration(self):
        """Should find ground state."""
        H = [[1.0, 0.0], [0.0, 3.0]]
        e, state = self.solver.power_iteration(H, 30)
        self.assertLess(e, 2.0)
        print(f"  [PASS] GS: E={e:.4f}")
    
    def test_gap(self):
        """Should compute gap."""
        H = [[1.0, 0.0], [0.0, 3.0]]
        gap = self.solver.energy_gap(H)
        self.assertEqual(gap, 2.0)
        print(f"  [PASS] Gap: {gap}")


class TestAdiabaticEvolution(unittest.TestCase):
    """Test evolution."""
    
    def setUp(self):
        self.ev = AdiabaticEvolution(3, 50)
    
    def test_evolve(self):
        """Should evolve."""
        cost = lambda x: x
        r = self.ev.evolve(cost)
        self.assertIn("solution", r)
        print(f"  [PASS] Ev: sol={r['solution']} cost={r['cost']}")


class TestQuantumAdiabaticOptimization(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qao = QuantumAdiabaticOptimization()
    
    def test_setup(self):
        """Should setup."""
        self.qao.setup(3, 50)
        self.assertIsNotNone(self.qao.evolution)
        print("  [PASS] Setup")
    
    def test_optimize(self):
        """Should optimize."""
        cost = lambda x: (x - 3) ** 2
        r = self.qao.optimize(cost)
        self.assertIn("solution", r)
        print(f"  [PASS] Opt: {r['solution']} cost={r['cost']}")
    
    def test_summary(self):
        """Should summarize."""
        self.qao.optimize(lambda x: x)
        s = self.qao.adiabatic_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
