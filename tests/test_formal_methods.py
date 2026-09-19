"""
Unit tests for formal methods module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from formal_methods import State, StateSpaceExplorer, InvariantChecker, BoundedModelChecker, FormalVerifier


class TestState(unittest.TestCase):
    """Test state."""
    
    def test_create(self):
        """Should create state."""
        s = State.from_dict({"x": 1, "y": 2})
        self.assertEqual(s.get("x"), 1)
        print("  [PASS] State: created")
    
    def test_equality(self):
        """Should compare states."""
        s1 = State.from_dict({"x": 1})
        s2 = State.from_dict({"x": 1})
        self.assertEqual(s1, s2)
        print("  [PASS] State: equal")


class TestStateSpaceExplorer(unittest.TestCase):
    """Test state space explorer."""
    
    def setUp(self):
        self.ex = StateSpaceExplorer()
        self.ex.add_transition(lambda s: [State.from_dict({"x": s.get("x") + 1})])
    
    def test_explore(self):
        """Should explore state space."""
        initial = State.from_dict({"x": 0})
        result = self.ex.explore(initial, max_depth=5, max_states=10)
        self.assertGreater(result["states_explored"], 0)
        print(f"  [PASS] Explore: {result['states_explored']} states")
    
    def test_find_reachable(self):
        """Should find reachable state."""
        initial = State.from_dict({"x": 0})
        found = self.ex.find_reachable(initial, lambda s: s.get("x") == 3, max_depth=5)
        self.assertIsNotNone(found)
        self.assertEqual(found.get("x"), 3)
        print(f"  [PASS] Find: x={found.get('x')}")


class TestInvariantChecker(unittest.TestCase):
    """Test invariant checker."""
    
    def setUp(self):
        self.ic = InvariantChecker()
        self.ic.add_invariant("x_positive", lambda s: s.get("x", 0) >= 0)
    
    def test_check_pass(self):
        """Should pass invariant."""
        s = State.from_dict({"x": 5})
        results = self.ic.check(s)
        self.assertTrue(results["x_positive"])
        print("  [PASS] Invariant: pass")
    
    def test_check_fail(self):
        """Should fail invariant."""
        s = State.from_dict({"x": -1})
        results = self.ic.check(s)
        self.assertFalse(results["x_positive"])
        print("  [PASS] Invariant: fail")
    
    def test_check_all(self):
        """Should check all states."""
        states = [State.from_dict({"x": 1}), State.from_dict({"x": 2})]
        summary = self.ic.check_all_states(states)
        self.assertEqual(summary["states_checked"], 2)
        print(f"  [PASS] All states: {summary['states_checked']}")


class TestBoundedModelChecker(unittest.TestCase):
    """Test bounded model checker."""
    
    def setUp(self):
        self.bmc = BoundedModelChecker(bound=5)
        self.bmc.add_transition(lambda s: [State.from_dict({"x": s.get("x") + 1})])
    
    def test_check_property(self):
        """Should check property."""
        initial = State.from_dict({"x": 0})
        result = self.bmc.check_property(initial, lambda s: s.get("x") < 10)
        self.assertTrue(result["property_holds"])
        print("  [PASS] BMC: holds")
    
    def test_check_property_fail(self):
        """Should find counterexample."""
        initial = State.from_dict({"x": 0})
        result = self.bmc.check_property(initial, lambda s: s.get("x") < 3)
        self.assertFalse(result["property_holds"])
        self.assertGreater(result["counterexamples"], 0)
        print(f"  [PASS] BMC: {result['counterexamples']} counterexamples")
    
    def test_reachability(self):
        """Should check reachability."""
        initial = State.from_dict({"x": 0})
        result = self.bmc.check_reachability(initial, lambda s: s.get("x") == 3)
        self.assertTrue(result["reachable"])
        print("  [PASS] Reachable: True")


class TestFormalVerifier(unittest.TestCase):
    """Test formal verifier."""
    
    def setUp(self):
        self.fv = FormalVerifier()
        self.fv.explorer.add_transition(lambda s: [State.from_dict({"x": s.get("x") + 1})])
    
    def test_verify_system(self):
        """Should verify system."""
        initial = State.from_dict({"x": 0})
        report = self.fv.verify_system(initial, [lambda s: s.get("x") < 10], bound=3)
        self.assertIn("exploration", report)
        print(f"  [PASS] Verify: {report['states_explored']} states")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.fv.verifier_summary()
        self.assertEqual(summary["transitions_defined"], 1)
        print(f"  [PASS] Summary: {summary['transitions_defined']} transitions")


if __name__ == '__main__':
    unittest.main(verbosity=2)
