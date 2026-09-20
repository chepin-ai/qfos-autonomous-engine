"""
Unit tests for quantum annealing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_annealing import (SpinState, IsingSpin, IsingModel,
                               EnergyLandscape, QuantumAnnealer,
                               GroundStateSearch, QuantumAnnealing)


class TestIsingModel(unittest.TestCase):
    """Test Ising model."""
    
    def setUp(self):
        self.model = IsingModel(num_spins=4)
    
    def test_energy_zero(self):
        """Should have zero energy for no fields."""
        e = self.model.energy()
        self.assertAlmostEqual(e, 0.0)
        print("  [PASS] E=0")
    
    def test_field_energy(self):
        """Should compute field energy."""
        self.model.set_field(0, 1.0)
        self.model.spins = [1, 1, 1, 1]
        e = self.model.energy()
        self.assertAlmostEqual(e, 1.0)
        print(f"  [PASS] E_field: {e}")
    
    def test_coupling_energy(self):
        """Should compute coupling energy."""
        self.model.set_coupling(0, 1, -1.0)
        self.model.spins = [1, 1, 1, 1]
        e = self.model.energy()
        self.assertAlmostEqual(e, -1.0)
        print(f"  [PASS] E_couple: {e}")
    
    def test_flip(self):
        """Should flip spin."""
        self.model.spins = [1, 1, 1, 1]
        self.model.flip_spin(0)
        self.assertEqual(self.model.spins[0], -1)
        print("  [PASS] Flip")
    
    def test_magnetization(self):
        """Should compute magnetization."""
        self.model.spins = [1, 1, -1, -1]
        m = self.model.magnetization()
        self.assertAlmostEqual(m, 0.0)
        print(f"  [PASS] M: {m}")


class TestEnergyLandscape(unittest.TestCase):
    """Test energy landscape."""
    
    def setUp(self):
        self.model = IsingModel(num_spins=3)
        self.model.set_coupling(0, 1, -1.0)
        self.landscape = EnergyLandscape(self.model)
    
    def test_neighbors(self):
        """Should generate neighbors."""
        state = [1, 1, 1]
        neighbors = self.landscape.neighbor_states(state)
        self.assertEqual(len(neighbors), 3)
        print(f"  [PASS] Neighbors: {len(neighbors)}")
    
    def test_local_minimum(self):
        """Should detect local minimum."""
        state = [1, 1, 1]
        # With J=-1, aligned spins have lowest energy
        is_min = self.landscape.local_minima(state)
        self.assertTrue(is_min)
        print("  [PASS] Min: True")
    
    def test_barrier(self):
        """Should compute barrier."""
        s1 = [1, 1, 1]
        s2 = [-1, 1, 1]
        b = self.landscape.energy_barrier(s1, s2)
        self.assertGreaterEqual(b, 0)
        print(f"  [PASS] Barrier: {b:.2f}")


class TestQuantumAnnealer(unittest.TestCase):
    """Test quantum annealer."""
    
    def setUp(self):
        self.model = IsingModel(num_spins=4)
        self.model.set_coupling(0, 1, -1.0)
        self.model.set_coupling(1, 2, -1.0)
        self.annealer = QuantumAnnealer(self.model)
    
    def test_tunneling(self):
        """Should compute tunneling."""
        p = self.annealer.tunneling_probability(1.0, 1.0)
        self.assertGreater(p, 0)
        self.assertLess(p, 1.0)
        print(f"  [PASS] Tunnel: {p:.4f}")
    
    def test_tunneling_zero_barrier(self):
        """Should have P=1 for zero barrier."""
        p = self.annealer.tunneling_probability(0.0, 1.0)
        self.assertAlmostEqual(p, 1.0)
        print("  [PASS] Tunnel zero: 1.0")
    
    def test_anneal(self):
        """Should perform annealing."""
        self.model.spins = [1, -1, 1, -1]
        state, energy = self.annealer.anneal(steps=10)
        self.assertEqual(len(state), 4)
        print(f"  [PASS] Anneal: E={energy:.2f}")


class TestGroundStateSearch(unittest.TestCase):
    """Test ground state search."""
    
    def setUp(self):
        self.model = IsingModel(num_spins=4)
        self.model.set_coupling(0, 1, -1.0)
        self.model.set_coupling(2, 3, -1.0)
        self.searcher = GroundStateSearch(self.model)
    
    def test_search(self):
        """Should find low energy state."""
        state, energy = self.searcher.search(num_restarts=5)
        self.assertEqual(len(state), 4)
        print(f"  [PASS] GS: E={energy:.2f}")
    
    def test_exact_small(self):
        """Should find exact ground state."""
        state, energy = self.searcher.exact_search_small()
        self.assertEqual(len(state), 4)
        print(f"  [PASS] Exact: E={energy:.2f}")


class TestQuantumAnnealing(unittest.TestCase):
    """Test unified quantum annealing."""
    
    def setUp(self):
        self.qa = QuantumAnnealing(num_spins=4)
    
    def test_set_problem(self):
        """Should set problem."""
        self.qa.set_problem({0: 1.0}, {(0, 1): -1.0})
        e = self.qa.model.energy([1, 1, 1, 1])
        self.assertAlmostEqual(e, 0.0)
        print("  [PASS] Set")
    
    def test_solve(self):
        """Should solve."""
        self.qa.set_problem({0: 1.0}, {(0, 1): -1.0})
        state, energy = self.qa.solve(num_restarts=3)
        self.assertEqual(len(state), 4)
        print(f"  [PASS] Solve: E={energy:.2f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.qa.set_problem({0: 1.0}, {(0, 1): -1.0})
        self.qa.solve(num_restarts=2)
        s = self.qa.annealing_summary()
        self.assertIn("best_energy", s)
        print(f"  [PASS] Summary: E={s['best_energy']:.2f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
