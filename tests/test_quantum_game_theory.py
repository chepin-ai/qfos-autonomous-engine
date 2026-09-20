"""
Unit tests for quantum game theory module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_game_theory import (QuantumStrategy, PayoffMatrix,
                                  NashEquilibriumFinder,
                                  QuantumPrisonerDilemma,
                                  CooperativeGameAnalyzer,
                                  QuantumGameTheory)


class TestPayoffMatrix(unittest.TestCase):
    """Test payoff."""
    
    def setUp(self):
        self.pm = PayoffMatrix(2, 2)
        self.pm.set_payoff(0, 0, 3.0, 3.0)
        self.pm.set_payoff(0, 1, 0.0, 5.0)
        self.pm.set_payoff(1, 0, 5.0, 0.0)
        self.pm.set_payoff(1, 1, 1.0, 1.0)
    
    def test_get(self):
        """Should get payoff."""
        p = self.pm.get_payoff(0, 0)
        self.assertEqual(p, (3.0, 3.0))
        print(f"  [PASS] Get: {p}")
    
    def test_expected(self):
        """Should compute expected."""
        exp = self.pm.expected_payoff([0.5, 0.5], [0.5, 0.5])
        self.assertEqual(len(exp), 2)
        print(f"  [PASS] Exp: {exp}")


class TestNashEquilibriumFinder(unittest.TestCase):
    """Test Nash."""
    
    def setUp(self):
        self.nef = NashEquilibriumFinder()
    
    def test_find(self):
        """Should find Nash equilibria."""
        pm = PayoffMatrix(2, 2)
        pm.set_payoff(0, 0, 3.0, 3.0)
        pm.set_payoff(0, 1, 0.0, 5.0)
        pm.set_payoff(1, 0, 5.0, 0.0)
        pm.set_payoff(1, 1, 1.0, 1.0)
        
        eq = self.nef.find_pure_strategy_nash(pm)
        self.assertEqual(len(eq), 1)
        self.assertEqual(eq[0], (1, 1))
        print(f"  [PASS] Nash: {eq}")


class TestQuantumPrisonerDilemma(unittest.TestCase):
    """Test QPD."""
    
    def setUp(self):
        self.qpd = QuantumPrisonerDilemma()
    
    def test_quantum_payoff(self):
        """Should compute quantum payoff."""
        row = [complex(1, 0), complex(0, 0)]
        col = [complex(1, 0), complex(0, 0)]
        p = self.qpd.quantum_payoff(row, col)
        self.assertEqual(p, (3.0, 3.0))
        print(f"  [PASS] QPay: {p}")


class TestCooperativeGameAnalyzer(unittest.TestCase):
    """Test cooperative."""
    
    def setUp(self):
        self.cga = CooperativeGameAnalyzer()
    
    def test_shapley(self):
        """Should compute Shapley value."""
        values = {
            (): 0.0,
            (0,): 1.0,
            (1,): 2.0,
            (0, 1): 4.0
        }
        sv = self.cga.shapley_value(0, values, 2)
        self.assertGreater(sv, 0)
        print(f"  [PASS] SV: {sv:.4f}")


class TestQuantumGameTheory(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgt = QuantumGameTheory()
    
    def test_add(self):
        """Should add strategy."""
        self.qgt.add_strategy("coop", [complex(1, 0), complex(0, 0)])
        self.assertEqual(len(self.qgt.strategies), 1)
        print("  [PASS] Add")
    
    def test_analyze(self):
        """Should analyze game."""
        pm = PayoffMatrix(2, 2)
        pm.set_payoff(0, 0, 3.0, 3.0)
        pm.set_payoff(0, 1, 0.0, 5.0)
        pm.set_payoff(1, 0, 5.0, 0.0)
        pm.set_payoff(1, 1, 1.0, 1.0)
        
        r = self.qgt.analyze_game(pm)
        self.assertIn("pure_nash", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qgt.qgt_summary()
        self.assertIn("strategies", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
