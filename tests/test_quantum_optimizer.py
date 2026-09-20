"""
Unit tests for quantum optimizer module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_optimizer import (QuantumParticle, QuantumParticleSwarm,
                               QuantumAnnealingOptimizer,
                               QuantumOptimizer)


class TestQuantumParticle(unittest.TestCase):
    """Test quantum particle."""
    
    def setUp(self):
        self.p = QuantumParticle(2, [(-5.0, 5.0), (-5.0, 5.0)])
    
    def test_init(self):
        """Should init within bounds."""
        self.assertEqual(len(self.p.position), 2)
        self.assertTrue(all(-5 <= x <= 5 for x in self.p.position))
        print(f"  [PASS] Pos: {self.p.position}")
    
    def test_update(self):
        """Should update position."""
        old = self.p.position[:]
        self.p.update_position([0.0, 0.0], 0.5)
        self.assertEqual(len(self.p.position), 2)
        print(f"  [PASS] Update")
    
    def test_evaluate(self):
        """Should evaluate."""
        def obj(x): return sum(xi**2 for xi in x)
        f = self.p.evaluate(obj)
        self.assertGreaterEqual(f, 0)
        print(f"  [PASS] Fit: {f:.4f}")


class TestQuantumParticleSwarm(unittest.TestCase):
    """Test QPSO."""
    
    def setUp(self):
        self.qpso = QuantumParticleSwarm(2, [(-5.0, 5.0), (-5.0, 5.0)], 10)
    
    def test_mbest(self):
        """Should compute mean best."""
        mb = self.qpso.mean_best()
        self.assertEqual(len(mb), 2)
        print(f"  [PASS] MB: {mb}")
    
    def test_optimize(self):
        """Should optimize."""
        def obj(x): return sum(xi**2 for xi in x)
        best, fit = self.qpso.optimize(obj, 20)
        self.assertEqual(len(best), 2)
        self.assertLess(fit, 10.0)
        print(f"  [PASS] QPSO: best={best} fit={fit:.4f}")


class TestQuantumAnnealingOptimizer(unittest.TestCase):
    """Test QA optimizer."""
    
    def setUp(self):
        self.qa = QuantumAnnealingOptimizer(2, [(-5.0, 5.0), (-5.0, 5.0)])
    
    def test_tunnel(self):
        """Should compute tunnel probability."""
        p = self.qa.tunnel_probability(1.0, 1.0)
        self.assertGreater(p, 0)
        self.assertLess(p, 1.0)
        print(f"  [PASS] Tunnel: {p:.4f}")
    
    def test_neighbor(self):
        """Should generate neighbor."""
        n = self.qa.neighbor([0.0, 0.0])
        self.assertEqual(len(n), 2)
        print(f"  [PASS] Neighbor: {n}")
    
    def test_optimize(self):
        """Should optimize."""
        def obj(x): return sum(xi**2 for xi in x)
        best, fit = self.qa.optimize(obj, 100)
        self.assertEqual(len(best), 2)
        self.assertLess(fit, 10.0)
        print(f"  [PASS] QA: best={best} fit={fit:.4f}")


class TestQuantumOptimizer(unittest.TestCase):
    """Test unified optimizer."""
    
    def setUp(self):
        self.qo = QuantumOptimizer()
    
    def test_qpso(self):
        """Should run QPSO."""
        def obj(x): return sum(xi**2 for xi in x)
        r = self.qo.qpso_optimize(obj, 2, [(-5.0, 5.0), (-5.0, 5.0)], 10, 20)
        self.assertIn("best_fitness", r)
        print(f"  [PASS] QPSO: {r['best_fitness']:.4f}")
    
    def test_qa(self):
        """Should run QA."""
        def obj(x): return sum(xi**2 for xi in x)
        r = self.qo.qa_optimize(obj, 2, [(-5.0, 5.0), (-5.0, 5.0)], 100)
        self.assertIn("best_fitness", r)
        print(f"  [PASS] QA: {r['best_fitness']:.4f}")
    
    def test_optimize(self):
        """Should dispatch."""
        def obj(x): return sum(xi**2 for xi in x)
        r = self.qo.optimize(obj, 2, [(-5.0, 5.0), (-5.0, 5.0)], "QPSO")
        self.assertEqual(r["method"], "QPSO")
        print("  [PASS] Dispatch")
    
    def test_summary(self):
        """Should summarize."""
        def obj(x): return sum(xi**2 for xi in x)
        self.qo.optimize(obj, 2, [(-5.0, 5.0), (-5.0, 5.0)])
        s = self.qo.optimizer_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
