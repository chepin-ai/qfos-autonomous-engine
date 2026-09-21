"""
Unit tests for quantum self-testing advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_self_testing_advanced import (BellTestResult, BellInequalityViolation,
                                           MeasurementSelfTesting,
                                           NonlocalCorrelation,
                                           DeviceIndependentCertification,
                                           QuantumSelfTestingAdvanced)


class TestBellInequalityViolation(unittest.TestCase):
    """Test Bell."""
    
    def setUp(self):
        self.biv = BellInequalityViolation()
    
    def test_correlator(self):
        """Should compute CHSH."""
        results = [
            BellTestResult(0, 0, 0, 0), BellTestResult(0, 1, 0, 1),
            BellTestResult(1, 0, 0, 0), BellTestResult(1, 1, 0, 1)
        ]
        s = self.biv.chsh_correlator(results)
        self.assertGreater(abs(s), 0)
        print(f"  [PASS] S: {s:.2f}")
    
    def test_is_quantum(self):
        """Should detect quantum."""
        q = self.biv.is_quantum(2.5)
        self.assertTrue(q)
        print(f"  [PASS] Q: {q}")
    
    def test_tsirelson(self):
        """Should return bound."""
        t = self.biv.tsirelson_bound()
        self.assertAlmostEqual(t, 2.828, delta=0.01)
        print(f"  [PASS] T: {t:.3f}")


class TestMeasurementSelfTesting(unittest.TestCase):
    """Test measurement."""
    
    def setUp(self):
        self.mst = MeasurementSelfTesting()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.mst.measurement_fidelity(0.8, 1.0)
        self.assertEqual(f, 0.8)
        print(f"  [PASS] F: {f:.2f}")
    
    def test_bound(self):
        """Should compute lower bound."""
        b = self.mst.state_fidelity_lower_bound(2.5)
        self.assertGreater(b, 0)
        print(f"  [PASS] LB: {b:.3f}")


class TestNonlocalCorrelation(unittest.TestCase):
    """Test nonlocal."""
    
    def setUp(self):
        self.nc = NonlocalCorrelation()
    
    def test_mi(self):
        """Should compute MI."""
        p = [[0.25, 0.25], [0.25, 0.25]]
        m = self.nc.mutual_information(p)
        self.assertEqual(m, 0.0)
        print(f"  [PASS] MI: {m:.2f}")
    
    def test_local(self):
        """Should return bound."""
        b = self.nc.local_bound()
        self.assertEqual(b, 2.0)
        print(f"  [PASS] LB: {b:.1f}")


class TestDeviceIndependentCertification(unittest.TestCase):
    """Test DI."""
    
    def setUp(self):
        self.dic = DeviceIndependentCertification()
    
    def test_randomness(self):
        """Should compute randomness."""
        r = self.dic.certifiable_randomness(2.5)
        self.assertGreater(r, 0)
        print(f"  [PASS] R: {r:.3f}")
    
    def test_security(self):
        """Should compute security."""
        s = self.dic.security_parameter(1000, 2.5)
        self.assertGreaterEqual(s, 0)
        print(f"  [PASS] Eps: {s:.4f}")


class TestQuantumSelfTestingAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qsta = QuantumSelfTestingAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qsta.self_test_summary()
        self.assertIn("protocols", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
