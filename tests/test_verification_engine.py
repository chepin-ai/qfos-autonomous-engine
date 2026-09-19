"""
Unit tests for verification engine module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from verification_engine import PropertyVerifier, TemporalProperty, PropertyStatus, TraceGenerator, ContractVerifier


class TestPropertyVerifier(unittest.TestCase):
    """Test property verifier."""
    
    def setUp(self):
        self.vf = PropertyVerifier()
        self.vf.add_property(TemporalProperty(
            "pos_bounded", "Position within bounds", "invariant",
            lambda s: abs(s["x"]) < 100
        ))
        self.vf.add_property(TemporalProperty(
            "reaches_goal", "Eventually reaches goal", "liveness",
            lambda s: s.get("reached", False)
        ))
    
    def test_invariant_pass(self):
        """Should pass invariant."""
        trace = [{"x": 10}, {"x": 20}, {"x": 30}]
        result = self.vf.verify("pos_bounded", trace)
        self.assertEqual(result.status, PropertyStatus.PASS)
        print("  [PASS] Invariant: pass")
    
    def test_invariant_fail(self):
        """Should fail invariant."""
        trace = [{"x": 10}, {"x": 200}]
        result = self.vf.verify("pos_bounded", trace)
        self.assertEqual(result.status, PropertyStatus.FAIL)
        self.assertIsNotNone(result.counterexample)
        print("  [PASS] Invariant: fail")
    
    def test_liveness_pass(self):
        """Should pass liveness."""
        trace = [{"reached": False}, {"reached": True}]
        result = self.vf.verify("reaches_goal", trace)
        self.assertEqual(result.status, PropertyStatus.PASS)
        print("  [PASS] Liveness: pass")
    
    def test_liveness_fail(self):
        """Should fail liveness."""
        trace = [{"reached": False}, {"reached": False}]
        result = self.vf.verify("reaches_goal", trace)
        self.assertEqual(result.status, PropertyStatus.FAIL)
        print("  [PASS] Liveness: fail")
    
    def test_verify_all(self):
        """Should verify all properties."""
        trace = [{"x": 10, "reached": True}]
        results = self.vf.verify_all(trace)
        self.assertEqual(len(results), 2)
        print(f"  [PASS] All: {len(results)} properties")
    
    def test_summary(self):
        """Should provide summary."""
        trace = [{"x": 10}]
        self.vf.verify("pos_bounded", trace)
        summary = self.vf.get_summary()
        self.assertEqual(summary["total_checked"], 1)
        print(f"  [PASS] Summary: {summary['passed']}/{summary['total_checked']}")


class TestTraceGenerator(unittest.TestCase):
    """Test trace generator."""
    
    def setUp(self):
        self.tg = TraceGenerator()
        self.tg.add_transition(lambda s: {"x": s["x"] + 1})
    
    def test_generate(self):
        """Should generate trace."""
        trace = self.tg.generate_trace({"x": 0}, steps=5)
        self.assertEqual(len(trace), 6)
        print(f"  [PASS] Trace: {len(trace)} states")


class TestContractVerifier(unittest.TestCase):
    """Test contract verifier."""
    
    def setUp(self):
        self.cv = ContractVerifier()
        self.cv.add_contract("divide",
                             precondition=lambda a, b: b != 0,
                             postcondition=lambda r, a, b: r * b == a)
    
    def test_precondition_pass(self):
        """Should pass precondition."""
        valid = self.cv.verify_precondition("divide", 10, 2)
        self.assertTrue(valid)
        print("  [PASS] Pre: pass")
    
    def test_precondition_fail(self):
        """Should fail precondition."""
        valid = self.cv.verify_precondition("divide", 10, 0)
        self.assertFalse(valid)
        print("  [PASS] Pre: fail")
    
    def test_postcondition_pass(self):
        """Should pass postcondition."""
        valid = self.cv.verify_postcondition("divide", 5, 10, 2)
        self.assertTrue(valid)
        print("  [PASS] Post: pass")
    
    def test_wrap(self):
        """Should wrap function."""
        def divide(a, b): return a / b
        wrapped = self.cv.wrap("divide", divide)
        result = wrapped(10, 2)
        self.assertEqual(result, 5.0)
        print(f"  [PASS] Wrap: {result}")
    
    def test_wrap_pre_violation(self):
        """Should catch precondition violation."""
        def divide(a, b): return a / b
        wrapped = self.cv.wrap("divide", divide)
        with self.assertRaises(ValueError):
            wrapped(10, 0)
        print("  [PASS] Wrap pre: caught")


if __name__ == '__main__':
    unittest.main(verbosity=2)
