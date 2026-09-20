"""
Unit tests for quantum hidden subgroup module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_hidden_subgroup import (GroupOperation, HiddenSubgroupProblem,
                                     PeriodFinding, SubgroupCharacterizer,
                                     QuantumHiddenSubgroup)


class TestHiddenSubgroupProblem(unittest.TestCase):
    """Test HSP."""
    
    def test_constant_function(self):
        """Should find trivial subgroup."""
        hsp = HiddenSubgroupProblem(8)
        hsp.set_function(lambda x: 0)
        r = hsp.find_period_classical()
        self.assertEqual(r, 1)
        print(f"  [PASS] Trivial: r={r}")
    
    def test_periodic_function(self):
        """Should find period."""
        hsp = HiddenSubgroupProblem(12)
        hsp.set_function(lambda x: x % 3)
        r = hsp.find_period_classical()
        self.assertEqual(r, 3)
        print(f"  [PASS] Period: r={r}")
    
    def test_generators(self):
        """Should find generators."""
        hsp = HiddenSubgroupProblem(12)
        hsp.set_function(lambda x: x % 4)
        gens = hsp.generators()
        self.assertIn(4, gens)
        print(f"  [PASS] Gen: {gens}")


class TestPeriodFinding(unittest.TestCase):
    """Test period finding."""
    
    def setUp(self):
        self.pf = PeriodFinding(15)
    
    def test_quantum_period(self):
        """Should find period."""
        r = self.pf.quantum_period(2)
        self.assertGreater(r, 0)
        print(f"  [PASS] Q period: {r}")
    
    def test_verify(self):
        """Should verify period."""
        r = self.pf.quantum_period(2)
        self.assertTrue(self.pf.verify_period(2, r))
        print("  [PASS] Verify")


class TestSubgroupCharacterizer(unittest.TestCase):
    """Test subgroup characterizer."""
    
    def setUp(self):
        self.sc = SubgroupCharacterizer(12)
    
    def test_is_subgroup(self):
        """Should validate subgroup."""
        self.assertTrue(self.sc.is_subgroup({0, 3, 6, 9}))
        print("  [PASS] Is subgroup")
    
    def test_not_subgroup(self):
        """Should reject non-subgroup."""
        self.assertFalse(self.sc.is_subgroup({0, 2, 5}))
        print("  [PASS] Not subgroup")
    
    def test_index(self):
        """Should compute index."""
        idx = self.sc.index(4)
        self.assertEqual(idx, 3)
        print(f"  [PASS] Index: {idx}")
    
    def test_cosets(self):
        """Should compute cosets."""
        cosets = self.sc.cosets([3])
        self.assertEqual(len(cosets), 3)
        print(f"  [PASS] Cosets: {len(cosets)}")


class TestQuantumHiddenSubgroup(unittest.TestCase):
    """Test unified HSP controller."""
    
    def setUp(self):
        self.qhs = QuantumHiddenSubgroup()
    
    def test_setup(self):
        """Should setup."""
        self.qhs.setup(8, lambda x: x % 2)
        self.assertIsNotNone(self.qhs.hsp)
        print("  [PASS] Setup")
    
    def test_solve(self):
        """Should solve."""
        self.qhs.setup(8, lambda x: x % 2)
        r = self.qhs.solve()
        self.assertIn("generators", r)
        print(f"  [PASS] Solve: {r['generators']}")
    
    def test_summary(self):
        """Should provide summary."""
        self.qhs.setup(8, lambda x: 0)
        self.qhs.solve()
        s = self.qhs.hidden_subgroup_summary()
        self.assertEqual(s["runs"], 1)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
