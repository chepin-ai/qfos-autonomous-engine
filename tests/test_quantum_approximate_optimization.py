"""
Unit tests for quantum approximate optimization (QAOA) module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_approximate_optimization import (MaxCut, QAOACircuit,
                                              ClassicalOptimizer,
                                              QuantumApproximateOptimization)


class TestMaxCut(unittest.TestCase):
    """Test MaxCut."""
    
    def setUp(self):
        self.mc = MaxCut(4)
        self.mc.add_edge(0, 1)
        self.mc.add_edge(1, 2)
        self.mc.add_edge(2, 3)
        self.mc.add_edge(3, 0)
    
    def test_cut_value(self):
        """Should compute cut value."""
        val = self.mc.cut_value([0, 1, 0, 1])
        self.assertEqual(val, 4.0)
        print(f"  [PASS] Cut: {val}")
    
    def test_cost(self):
        """Should compute cost."""
        cost = self.mc.cost_hamiltonian_term(5)  # 0101
        self.assertLess(cost, 0)
        print(f"  [PASS] Cost: {cost}")
    
    def test_max_cut(self):
        """Should compute max possible."""
        m = self.mc.max_possible_cut()
        self.assertEqual(m, 4.0)
        print(f"  [PASS] Max: {m}")


class TestQAOACircuit(unittest.TestCase):
    """Test QAOA circuit."""
    
    def setUp(self):
        mc = MaxCut(3)
        mc.add_edge(0, 1)
        mc.add_edge(1, 2)
        self.circ = QAOACircuit(mc, 1)
    
    def test_mixer(self):
        """Should apply mixer."""
        state = [complex(1.0, 0.0), complex(0.0, 0.0),
                 complex(0.0, 0.0), complex(0.0, 0.0),
                 complex(0.0, 0.0), complex(0.0, 0.0),
                 complex(0.0, 0.0), complex(0.0, 0.0)]
        new_state = self.circ.mixer_hamiltonian(0.5, state)
        self.assertEqual(len(new_state), 8)
        print("  [PASS] Mixer")
    
    def test_expectation(self):
        """Should compute expectation."""
        exp = self.circ.expectation_value()
        self.assertIsNotNone(exp)
        print(f"  [PASS] Exp: {exp:.4f}")
    
    def test_sample(self):
        """Should sample."""
        counts = self.circ.sample(100)
        self.assertGreater(len(counts), 0)
        print(f"  [PASS] Sample: {len(counts)} outcomes")


class TestClassicalOptimizer(unittest.TestCase):
    """Test classical optimizer."""
    
    def setUp(self):
        self.opt = ClassicalOptimizer()
    
    def test_optimize(self):
        """Should optimize."""
        mc = MaxCut(3)
        mc.add_edge(0, 1)
        circ = QAOACircuit(mc, 1)
        initial = circ.expectation_value()
        optimized = self.opt.optimize(circ, 10)
        final = optimized.expectation_value()
        print(f"  [PASS] Opt: {initial:.4f} -> {final:.4f}")


class TestQuantumApproximateOptimization(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qaoa = QuantumApproximateOptimization()
    
    def test_build(self):
        """Should build problem."""
        self.qaoa.build_problem(4, [(0, 1), (1, 2), (2, 3)])
        self.assertIsNotNone(self.qaoa.maxcut)
        print("  [PASS] Build")
    
    def test_solve(self):
        """Should solve."""
        self.qaoa.build_problem(3, [(0, 1), (1, 2)])
        r = self.qaoa.solve(1, 10)
        self.assertIn("best_solution", r)
        print(f"  [PASS] Sol: {r['best_solution']} cost={r['best_cost']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        self.qaoa.build_problem(3, [(0, 1)])
        self.qaoa.solve(1, 5)
        s = self.qaoa.qaoa_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
