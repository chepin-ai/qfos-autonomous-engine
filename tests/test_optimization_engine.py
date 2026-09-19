"""
Unit tests for optimization engine module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from optimization_engine import (ParetoFrontier, GeneticOptimizer, ConstrainedOptimizer,
                                 OptimizationEngine, Objective, Solution)


class TestParetoFrontier(unittest.TestCase):
    """Test Pareto frontier."""
    
    def setUp(self):
        self.pf = ParetoFrontier([
            Objective("cost", minimize=True),
            Objective("time", minimize=True)
        ])
    
    def test_add_non_dominated(self):
        """Should add non-dominated solution."""
        s = Solution(values={"x": 1}, objectives={"cost": 10, "time": 5})
        self.assertTrue(self.pf.add(s))
        self.assertEqual(self.pf.size(), 1)
        print("  [PASS] Add: non-dominated")
    
    def test_dominates(self):
        """Should detect dominance."""
        s1 = Solution(values={"x": 1}, objectives={"cost": 10, "time": 5})
        s2 = Solution(values={"x": 2}, objectives={"cost": 15, "time": 8})
        self.pf.add(s1)
        self.assertTrue(self.pf.dominates(s1, s2))
        print("  [PASS] Dominates: detected")
    
    def test_add_dominated(self):
        """Should reject dominated solution."""
        s1 = Solution(values={"x": 1}, objectives={"cost": 10, "time": 5})
        s2 = Solution(values={"x": 2}, objectives={"cost": 15, "time": 8})
        self.pf.add(s1)
        self.assertFalse(self.pf.add(s2))
        print("  [PASS] Add: rejected dominated")
    
    def test_multiple_non_dominated(self):
        """Should keep multiple non-dominated solutions."""
        s1 = Solution(values={"x": 1}, objectives={"cost": 10, "time": 20})
        s2 = Solution(values={"x": 2}, objectives={"cost": 20, "time": 10})
        self.pf.add(s1)
        self.pf.add(s2)
        self.assertEqual(self.pf.size(), 2)
        print(f"  [PASS] Frontier: {self.pf.size()} solutions")


class TestGeneticOptimizer(unittest.TestCase):
    """Test genetic optimizer."""
    
    def setUp(self):
        self.opt = GeneticOptimizer(population_size=20, seed=42)
    
    def test_initialize(self):
        """Should initialize population."""
        self.opt.initialize({"x": (0, 10)})
        self.assertEqual(len(self.opt.population), 20)
        print("  [PASS] Init: 20 individuals")
    
    def test_evolve(self):
        """Should evolve population."""
        self.opt.initialize({"x": (0, 10)})
        pop = self.opt.evolve({"x": (0, 10)}, {"obj": lambda v: v["x"] ** 2}, generations=10)
        self.assertEqual(len(pop), 20)
        print("  [PASS] Evolve: 10 generations")
    
    def test_crossover(self):
        """Should produce children."""
        a = Solution(values={"x": 1})
        b = Solution(values={"x": 5})
        c1, c2 = self.opt.crossover(a, b)
        self.assertIn(c1.values["x"], [1, 5])
        print("  [PASS] Crossover: valid")
    
    def test_mutate(self):
        """Should mutate."""
        s = Solution(values={"x": 5})
        self.opt.mutate(s, {"x": (0, 10)})
        self.assertGreaterEqual(s.values["x"], 0)
        self.assertLessEqual(s.values["x"], 10)
        print("  [PASS] Mutate: in bounds")


class TestConstrainedOptimizer(unittest.TestCase):
    """Test constrained optimizer."""
    
    def setUp(self):
        self.co = ConstrainedOptimizer()
        self.co.add_constraint(lambda v: v["x"] - 5)  # x <= 5
    
    def test_feasible(self):
        """Should detect feasible."""
        self.assertTrue(self.co.is_feasible({"x": 3}))
        print("  [PASS] Feasible: True")
    
    def test_infeasible(self):
        """Should detect infeasible."""
        self.assertFalse(self.co.is_feasible({"x": 10}))
        print("  [PASS] Feasible: False")
    
    def test_penalized(self):
        """Should penalize violations."""
        obj = lambda v: v["x"]
        p1 = self.co.penalized_objective(obj, {"x": 3})
        p2 = self.co.penalized_objective(obj, {"x": 10})
        self.assertLess(p1, p2)
        print(f"  [PASS] Penalty: feasible={p1:.0f} < infeasible={p2:.0f}")


class TestOptimizationEngine(unittest.TestCase):
    """Test optimization engine."""
    
    def setUp(self):
        self.oe = OptimizationEngine()
    
    def test_multiobjective(self):
        """Should optimize multi-objective."""
        frontier = self.oe.optimize_multiobjective(
            {"x": (0, 10)},
            [Objective("f1", minimize=True), Objective("f2", minimize=True)],
            {"f1": lambda v: v["x"], "f2": lambda v: (10 - v["x"]) ** 2},
            generations=20
        )
        self.assertGreater(len(frontier), 0)
        print(f"  [PASS] Multi-obj: {len(frontier)} frontier points")
    
    def test_constrained(self):
        """Should optimize constrained."""
        result = self.oe.optimize_constrained(
            {"x": (0, 10)},
            lambda v: v["x"] ** 2,
            [lambda v: v["x"] - 5],
            generations=30
        )
        self.assertIsNotNone(result)
        self.assertLessEqual(result.values["x"], 5.5)
        print(f"  [PASS] Constrained: x={result.values['x']:.2f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.oe.optimize_multiobjective(
            {"x": (0, 10)},
            [Objective("f1", minimize=True)],
            {"f1": lambda v: v["x"]},
            generations=5
        )
        summary = self.oe.engine_summary()
        self.assertIn("pareto_size", summary)
        print(f"  [PASS] Summary: {summary}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
