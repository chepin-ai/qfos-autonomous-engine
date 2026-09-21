"""
Unit tests for quantum sensing advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_sensing_advanced import (SqueezingParams, QuantumMetrology,
                                      SqueezingEnhancedSensing,
                                      QuantumIllumination,
                                      EntanglementAssistedSensing,
                                      QuantumSensingAdvanced)


class TestQuantumMetrology(unittest.TestCase):
    """Test metrology."""
    
    def setUp(self):
        self.qm = QuantumMetrology()
    
    def test_sql(self):
        """Should compute SQL."""
        s = self.qm.standard_quantum_limit(100)
        self.assertEqual(s, 0.1)
        print(f"  [PASS] SQL: {s:.3f}")
    
    def test_hl(self):
        """Should compute HL."""
        h = self.qm.heisenberg_limit(100)
        self.assertEqual(h, 0.01)
        print(f"  [PASS] HL: {h:.3f}")
    
    def test_fisher(self):
        """Should compute Fisher."""
        f = self.qm.fisher_information(1.0, 0.5)
        self.assertGreater(f, 0)
        print(f"  [PASS] F: {f:.2f}")


class TestSqueezingEnhancedSensing(unittest.TestCase):
    """Test squeezing."""
    
    def setUp(self):
        self.ses = SqueezingEnhancedSensing()
    
    def test_factor(self):
        """Should compute factor."""
        f = self.ses.squeezing_factor(1.0)
        self.assertLess(f, 1.0)
        print(f"  [PASS] Sq: {f:.4f}")
    
    def test_anti(self):
        """Should compute anti."""
        f = self.ses.anti_squeezing_factor(1.0)
        self.assertGreater(f, 1.0)
        print(f"  [PASS] Anti: {f:.4f}")
    
    def test_variance(self):
        """Should compute variance."""
        v = self.ses.squeezed_state_variance(1.0)
        self.assertLess(v, 0.25)
        print(f"  [PASS] Var: {v:.4f}")


class TestQuantumIllumination(unittest.TestCase):
    """Test illumination."""
    
    def setUp(self):
        self.qi = QuantumIllumination()
    
    def test_gain(self):
        """Should compute gain."""
        g = self.qi.quantum_illumination_gain(1.0, 0.1, 10.0)
        self.assertGreater(g, 0)
        print(f"  [PASS] Gain: {g:.4f}")
    
    def test_exponent(self):
        """Should compute exponent."""
        e = self.qi.error_exponent(1.0, 0.1, 10.0)
        self.assertGreater(e, 0)
        print(f"  [PASS] Exp: {e:.5f}")


class TestEntanglementAssistedSensing(unittest.TestCase):
    """Test entanglement."""
    
    def setUp(self):
        self.eas = EntanglementAssistedSensing()
    
    def test_precision(self):
        """Should compute precision."""
        p = self.eas.entanglement_enhanced_precision(100)
        self.assertGreater(p, 0)
        print(f"  [PASS] Prec: {p:.4f}")
    
    def test_violation(self):
        """Should compute violation."""
        v = self.eas.bell_inequality_violation(0.9)
        self.assertGreater(v, 0)
        print(f"  [PASS] Vio: {v:.4f}")


class TestQuantumSensingAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qsa = QuantumSensingAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qsa.sensing_summary()
        self.assertIn("protocols", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
