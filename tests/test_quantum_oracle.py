"""
Unit tests for quantum oracle module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_oracle import (OracleResult, BooleanOracle,
                            PhaseOracle,
                            GroverOracle,
                            QuantumQueryComplexity,
                            QuantumOracle)


class TestBooleanOracle(unittest.TestCase):
    """Test boolean oracle."""
    
    def setUp(self):
        self.bo = BooleanOracle(lambda x: x % 2, 3)
    
    def test_evaluate(self):
        """Should evaluate."""
        self.assertEqual(self.bo.evaluate(3), 1)
        print("  [PASS] Eval")
    
    def test_truth_table(self):
        """Should generate table."""
        tt = self.bo.truth_table()
        self.assertEqual(len(tt), 8)
        print(f"  [PASS] TT: {len(tt)} entries")
    
    def test_constant(self):
        """Should check constant."""
        co = BooleanOracle(lambda x: 0, 2)
        self.assertTrue(co.is_constant())
        print("  [PASS] Const")
    
    def test_balanced(self):
        """Should check balanced."""
        self.assertTrue(self.bo.is_balanced())
        print("  [PASS] Bal")


class TestPhaseOracle(unittest.TestCase):
    """Test phase oracle."""
    
    def setUp(self):
        self.po = PhaseOracle([3, 5])
    
    def test_phase(self):
        """Should apply phase."""
        self.assertEqual(self.po.apply_phase(3), -1.0)
        self.assertEqual(self.po.apply_phase(0), 1.0)
        print("  [PASS] Phase")
    
    def test_marked(self):
        """Should count marked."""
        n = self.po.num_marked(8)
        self.assertEqual(n, 2)
        print(f"  [PASS] M: {n}")
    
    def test_optimal(self):
        """Should compute iterations."""
        it = self.po.optimal_iterations(8)
        self.assertGreater(it, 0)
        print(f"  [PASS] It: {it}")


class TestGroverOracle(unittest.TestCase):
    """Test Grover."""
    
    def setUp(self):
        self.go = GroverOracle([3])
    
    def test_diffusion(self):
        """Should diffuse."""
        s = self.go.diffusion_operator([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(s), 4)
        print(f"  [PASS] Diff: {s}")
    
    def test_iteration(self):
        """Should iterate."""
        s = self.go.grover_iteration([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(s), 4)
        print(f"  [PASS] Iter: {s}")


class TestQuantumQueryComplexity(unittest.TestCase):
    """Test complexity."""
    
    def setUp(self):
        self.qc = QuantumQueryComplexity()
    
    def test_deutsch(self):
        """Should compute DJ queries."""
        q = self.qc.deutsch_jozsa_queries(3)
        self.assertEqual(q, 1)
        print(f"  [PASS] DJ: {q}")
    
    def test_grover(self):
        """Should compute Grover queries."""
        q = self.qc.grover_queries(16, 1)
        self.assertGreater(q, 0)
        print(f"  [PASS] G: {q:.2f}")
    
    def test_simon(self):
        """Should compute Simon queries."""
        q = self.qc.simon_queries(4)
        self.assertEqual(q, 4)
        print(f"  [PASS] S: {q}")


class TestQuantumOracle(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qo = QuantumOracle()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qo.oracle_summary()
        self.assertIn("types", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
