"""
Unit tests for quantum swarm intelligence module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_swarm_intelligence import (Particle, QuantumParticle,
                                        SwarmOptimizer,
                                        SwarmDiversityTracker,
                                        QuantumSwarmIntelligence)


class TestQuantumParticle(unittest.TestCase):
    """Test quantum particle."""
    
    def setUp(self):
        self.qp = QuantumParticle(2)
    
    def test_update(self):
        """Should update position."""
        self.qp.best_position = [1.0, 1.0]
        gb = [0.0, 0.0]
        self.qp.quantum_update(gb, 0.5)
        self.assertEqual(len(self.qp.position), 2)
        print(f"  [PASS] QUpd: {self.qp.position}")


class TestSwarmOptimizer(unittest.TestCase):
    """Test PSO."""
    
    def setUp(self):
        self.so = SwarmOptimizer(10, 2)
    
    def test_init(self):
        """Should initialize."""
        self.assertEqual(len(self.so.particles), 10)
        print("  [PASS] Init")
    
    def test_step(self):
        """Should optimize step."""
        def f(x):
            return sum(v**2 for v in x)
        
        best = self.so.optimize_step(f)
        self.assertGreaterEqual(best, 0)
        print(f"  [PASS] Step: {best:.4f}")
    
    def test_convergence(self):
        """Should converge."""
        def f(x):
            return sum(v**2 for v in x)
        
        for _ in range(50):
            self.so.optimize_step(f)
        
        self.assertLess(self.so.global_best_fitness, 10.0)
        print(f"  [PASS] Conv: {self.so.global_best_fitness:.6f}")


class TestSwarmDiversityTracker(unittest.TestCase):
    """Test diversity."""
    
    def setUp(self):
        self.sdt = SwarmDiversityTracker()
    
    def test_diversity(self):
        """Should compute diversity."""
        particles = [Particle([0.0, 0.0], [0.0, 0.0], [0.0, 0.0], 0.0),
                     Particle([1.0, 1.0], [0.0, 0.0], [0.0, 0.0], 0.0)]
        d = self.sdt.diversity(particles)
        self.assertGreater(d, 0)
        print(f"  [PASS] Div: {d:.4f}")
    
    def test_converged(self):
        """Should detect convergence."""
        particles = [Particle([0.0, 0.0], [0.0, 0.0], [0.0, 0.0], 0.0),
                     Particle([0.001, 0.001], [0.0, 0.0], [0.0, 0.0], 0.0)]
        c = self.sdt.is_converged(particles, 0.01)
        self.assertTrue(c)
        print("  [PASS] Conv")


class TestQuantumSwarmIntelligence(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qsi = QuantumSwarmIntelligence(10, 2)
    
    def test_optimize(self):
        """Should optimize."""
        def f(x):
            return sum(v**2 for v in x)
        
        r = self.qsi.optimize(f, 50)
        self.assertIn("best_fitness", r)
        print(f"  [PASS] Opt: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qsi.qsi_summary()
        self.assertIn("particles", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
