"""
Unit tests for quantum annealing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_annealing import (SpinConfiguration, IsingModel,
                               AnnealingSchedule,
                               QuantumAnnealer,
                               EnergyLandscape,
                               QuantumAnnealing)


class TestIsingModel(unittest.TestCase):
    """Test Ising model."""
    
    def setUp(self):
        self.im = IsingModel(4)
    
    def test_energy(self):
        """Should compute energy."""
        self.im.set_field(0, 1.0)
        self.im.set_coupling(0, 1, -1.0)
        e = self.im.energy([1, 1, -1, -1])
        self.assertEqual(e, 0.0)
        print(f"  [PASS] E: {e}")
    
    def test_coupling(self):
        """Should set coupling."""
        self.im.set_coupling(1, 2, 0.5)
        self.assertIn((1, 2), self.im.J)
        print("  [PASS] J")


class TestAnnealingSchedule(unittest.TestCase):
    """Test schedule."""
    
    def setUp(self):
        self.asch = AnnealingSchedule(0.0, 1.0, 100)
    
    def test_linear(self):
        """Should generate linear schedule."""
        s = self.asch.linear_schedule()
        self.assertEqual(len(s), 101)
        self.assertAlmostEqual(s[0], 0.0)
        self.assertAlmostEqual(s[-1], 1.0)
        print(f"  [PASS] Lin: {len(s)} steps")
    
    def test_exponential(self):
        """Should generate exponential schedule."""
        s = self.asch.exponential_schedule()
        self.assertEqual(len(s), 101)
        print(f"  [PASS] Exp: {s[-1]:.4f}")


class TestQuantumAnnealer(unittest.TestCase):
    """Test annealer."""
    
    def setUp(self):
        self.model = IsingModel(4)
        self.model.set_field(0, 1.0)
        self.qa = QuantumAnnealer(self.model)
    
    def test_anneal(self):
        """Should anneal."""
        schedule = [0.0, 0.5, 1.0]
        result = self.qa.anneal(schedule, [1, -1, 1, -1])
        self.assertIsNotNone(result.spins)
        print(f"  [PASS] Anneal: E={result.energy:.2f}")


class TestEnergyLandscape(unittest.TestCase):
    """Test landscape."""
    
    def setUp(self):
        self.model = IsingModel(3)
        self.model.set_field(0, 1.0)
        self.el = EnergyLandscape(self.model)
    
    def test_local_minima(self):
        """Should find minima."""
        samples = [[1, 1, 1], [1, -1, 1]]
        m = self.el.local_minima(samples)
        self.assertGreater(len(m), 0)
        print(f"  [PASS] Minima: {len(m)}")
    
    def test_ground(self):
        """Should estimate ground state."""
        e = self.el.ground_state_energy()
        self.assertIsNotNone(e)
        print(f"  [PASS] GS: {e}")


class TestQuantumAnnealing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qa = QuantumAnnealing(4)
    
    def test_solve(self):
        """Should solve."""
        r = self.qa.solve({0: 1.0, 1: -1.0}, {(0, 1): -1.0}, 5)
        self.assertIn("best_energy", r)
        print(f"  [PASS] Sol: E={r['best_energy']:.2f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qa.qa_summary()
        self.assertIn("num_spins", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
