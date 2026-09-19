"""
Unit tests for constraint solver module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from constraint_solver import CSPSolver, SATEncoder, ConstraintSolver, Variable, Constraint


class TestCSPSolver(unittest.TestCase):
    """Test CSP solver."""
    
    def setUp(self):
        self.solver = CSPSolver()
        self.solver.add_variable("A", [1, 2, 3])
        self.solver.add_variable("B", [1, 2, 3])
        self.solver.add_constraint("A", "B", lambda a, b: a != b)
    
    def test_solve(self):
        """Should solve CSP."""
        sol = self.solver.solve()
        self.assertIsNotNone(sol)
        self.assertNotEqual(sol["A"], sol["B"])
        print(f"  [PASS] Solve: A={sol['A']}, B={sol['B']}")
    
    def test_consistent(self):
        """Should check consistency."""
        self.assertTrue(self.solver.is_consistent("A", 1, {"B": 2}))
        self.assertFalse(self.solver.is_consistent("A", 1, {"B": 1}))
        print("  [PASS] Consistent: correct")
    
    def test_arc_consistency(self):
        """Should enforce arc consistency."""
        result = self.solver.arc_consistency()
        self.assertTrue(result)
        print("  [PASS] AC-3: consistent")
    
    def test_no_solution(self):
        """Should detect no solution."""
        s = CSPSolver()
        s.add_variable("X", [1])
        s.add_variable("Y", [1])
        s.add_constraint("X", "Y", lambda x, y: x != y)
        sol = s.solve()
        self.assertIsNone(sol)
        print("  [PASS] No solution: detected")


class TestSATEncoder(unittest.TestCase):
    """Test SAT encoder."""
    
    def setUp(self):
        self.enc = SATEncoder()
    
    def test_encode_variable(self):
        """Should encode variable."""
        v1 = self.enc.encode_variable("X", 1)
        v2 = self.enc.encode_variable("X", 1)
        self.assertEqual(v1, v2)
        print(f"  [PASS] Encode: var_id={v1}")
    
    def test_exactly_one(self):
        """Should encode exactly-one."""
        self.enc.encode_exactly_one("X", [1, 2, 3])
        formula = self.enc.get_formula()
        self.assertGreater(formula["num_clauses"], 0)
        print(f"  [PASS] Exactly-one: {formula['num_clauses']} clauses")
    
    def test_binary_constraint(self):
        """Should encode binary constraint."""
        self.enc.encode_binary_constraint("A", 1, "B", 2, allowed=True)
        formula = self.enc.get_formula()
        self.assertEqual(formula["num_clauses"], 1)
        print("  [PASS] Binary: 1 clause")
    
    def test_decode(self):
        """Should decode solution."""
        self.enc.encode_exactly_one("X", [1, 2])
        sat_sol = {self.enc.encode_variable("X", 1): True,
                   self.enc.encode_variable("X", 2): False}
        csp_sol = self.enc.decode_solution(sat_sol)
        self.assertEqual(csp_sol["X"], 1)
        print(f"  [PASS] Decode: X={csp_sol['X']}")


class TestConstraintSolver(unittest.TestCase):
    """Test unified constraint solver."""
    
    def test_solve_csp(self):
        """Should solve CSP via unified API."""
        solver = ConstraintSolver()
        sol = solver.solve_csp(
            {"A": [1, 2, 3], "B": [1, 2, 3]},
            [("A", "B", lambda a, b: a != b)]
        )
        self.assertIsNotNone(sol)
        self.assertNotEqual(sol["A"], sol["B"])
        print(f"  [PASS] Unified: A={sol['A']}, B={sol['B']}")
    
    def test_summary(self):
        """Should provide summary."""
        solver = ConstraintSolver()
        solver.solve_csp(
            {"A": [1, 2], "B": [1, 2]},
            [("A", "B", lambda a, b: a != b)]
        )
        summary = solver.solver_summary()
        self.assertEqual(summary["variables"], 2)
        print(f"  [PASS] Summary: {summary['variables']} vars")


if __name__ == '__main__':
    unittest.main(verbosity=2)
