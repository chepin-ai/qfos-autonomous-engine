"""
Unit tests for residual stress analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from residual_stress_analysis import (StressTensor, XRDSin2Psi,
                                      HoleDrilling,
                                      DepthProfiler,
                                      ResidualStressAnalysis)


class TestXRDSin2Psi(unittest.TestCase):
    """Test XRD."""
    
    def setUp(self):
        self.xrd = XRDSin2Psi(200.0, 0.3, 150.0)
    
    def test_strain(self):
        """Should compute strain."""
        d = [1.0, 1.001, 1.002]
        strains = self.xrd.strain_from_psi(d, [0.0, 15.0, 30.0])
        self.assertEqual(len(strains), 3)
        print(f"  [PASS] Strains: {strains}")
    
    def test_stress_from_slope(self):
        """Should compute stress."""
        s = self.xrd.stress_from_slope(0.001)
        self.assertIsInstance(s, float)
        print(f"  [PASS] Stress: {s:.2f} MPa")
    
    def test_linear_fit(self):
        """Should fit line."""
        sin2 = [0.0, 0.25, 0.5, 0.75]
        d = [1.0, 1.001, 1.002, 1.003]
        a, b = self.xrd.linear_fit(sin2, d)
        self.assertAlmostEqual(b, 0.004, delta=0.001)
        print(f"  [PASS] Fit: a={a:.4f}, b={b:.4f}")


class TestHoleDrilling(unittest.TestCase):
    """Test hole drilling."""
    
    def setUp(self):
        self.hd = HoleDrilling(5.0)
    
    def test_relaxed_strains(self):
        """Should compute relaxed strains."""
        r = self.hd.relaxed_strains([100.0, 200.0, 300.0], [90.0, 185.0, 280.0])
        self.assertEqual(r[0], 10.0)
        print(f"  [PASS] Rel: {r}")
    
    def test_principal_stresses(self):
        """Should compute principal stresses."""
        s1, s2, th = self.hd.principal_stresses(100e-6, 50e-6, -50e-6)
        self.assertIsInstance(s1, float)
        print(f"  [PASS] S1={s1:.2f}, S2={s2:.2f}, th={th:.1f}")


class TestDepthProfiler(unittest.TestCase):
    """Test profiler."""
    
    def setUp(self):
        self.dp = DepthProfiler()
    
    def test_layer_correction(self):
        """Should apply correction."""
        s = self.dp.layer_removal_correction(100.0, 0.5, 10.0)
        self.assertGreater(s, 100.0)
        print(f"  [PASS] Corr: {s:.2f} MPa")
    
    def test_integrate(self):
        """Should integrate stress."""
        force = self.dp.integrate_stress([100.0, 80.0, 60.0], [0.0, 1.0, 2.0])
        self.assertGreater(force, 0)
        print(f"  [PASS] Force: {force:.2f} N/mm")


class TestResidualStressAnalysis(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.rsa = ResidualStressAnalysis()
    
    def test_summary(self):
        """Should summarize."""
        s = self.rsa.stress_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
