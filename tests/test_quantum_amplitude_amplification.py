"""
Unit tests for quantum amplitude amplification module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_amplitude_amplification import (SearchResult, OracleConstructor,
                                             DiffusionOperator,
                                             GroverSearch,
                                             AmplitudeAmplification,
                                             QuantumAmplitudeAmplification)


class TestOracleConstructor(unittest.TestCase):
    """Test oracle."""
    
    def setUp(self):
        self.oc = OracleConstructor(3)
    
    def test_create(self):
        """Should create oracle."""
        o = self.oc.create_oracle([2])
        self.assertEqual(o[2][2], -1.0)
        print("  [PASS] Orac")
    
    def test_apply(self):
        """Should apply oracle."""
        s = [1.0] * 8
        r = self.oc.apply_oracle(s, [2])
        self.assertEqual(r[2], -1.0)
        print("  [PASS] Appl")


class TestDiffusionOperator(unittest.TestCase):
    """Test diffusion."""
    
    def setUp(self):
        self.dif = DiffusionOperator(3)
    
    def test_create(self):
        """Should create diffusion."""
        d = self.dif.create_diffusion()
        self.assertEqual(len(d), 8)
        print("  [PASS] Diff")
    
    def test_apply(self):
        """Should apply diffusion."""
        s = [1.0] * 8
        r = self.dif.apply_diffusion(s)
        self.assertEqual(len(r), 8)
        print("  [PASS] Appl")


class TestGroverSearch(unittest.TestCase):
    """Test Grover."""
    
    def setUp(self):
        self.gs = GroverSearch(3)
    
    def test_optimal(self):
        """Should compute optimal iterations."""
        opt = self.gs.optimal_iterations(1)
        self.assertGreater(opt, 0)
        print(f"  [PASS] Opt: {opt}")
    
    def test_search(self):
        """Should search."""
        r = self.gs.search([5])
        self.assertIsNotNone(r)
        print(f"  [PASS] Srch: idx={r.target_index}, P={r.probability:.3f}")
    
    def test_probability(self):
        """Should compute probability."""
        p = self.gs.success_probability(1, 2)
        self.assertGreater(p, 0)
        print(f"  [PASS] Prob: {p:.3f}")


class TestAmplitudeAmplification(unittest.TestCase):
    """Test amplification."""
    
    def setUp(self):
        self.aa = AmplitudeAmplification(3)
    
    def test_amplify(self):
        """Should amplify."""
        s = [1.0 / math.sqrt(8)] * 8
        r = self.aa.amplify(s, [3], 1)
        self.assertEqual(len(r), 8)
        print("  [PASS] Amp")


class TestQuantumAmplitudeAmplification(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qaa = QuantumAmplitudeAmplification(3)
    
    def test_search(self):
        """Should search."""
        r = self.qaa.search([2])
        self.assertIsNotNone(r)
        print(f"  [PASS] QAA: idx={r.target_index}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qaa.qaa_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
