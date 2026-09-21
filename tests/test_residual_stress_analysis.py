"""
Unit tests for residual stress analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from residual_stress_analysis import (StrainRosette, HoleDrillingMethod,
                                      XrayDiffraction,
                                      Sin2PsiMethod,
                                      StressRelaxation,
                                      ResidualStressAnalysis)


class TestHoleDrillingMethod(unittest.TestCase):
    """Test hole drilling."""
    
    def setUp(self):
        self.hdm = HoleDrillingMethod()
    
    def test_principal(self):
        """Should compute principal stresses."""
        s = StrainRosette(100e-6, 50e-6, -50e-6)
        p = self.hdm.principal_stresses(s)
        self.assertGreater(p[0], p[1])
        print(f"  [PASS] S1={p[0]:.1f}, S2={p[1]:.1f}")
    
    def test_direction(self):
        """Should compute direction."""
        s = StrainRosette(100e-6, 50e-6, -50e-6)
        d = self.hdm.stress_direction(s)
        self.assertIsInstance(d, float)
        print(f"  [PASS] Dir: {d:.1f}")


class TestXrayDiffraction(unittest.TestCase):
    """Test XRD."""
    
    def setUp(self):
        self.xrd = XrayDiffraction()
    
    def test_d_spacing(self):
        """Should compute d-spacing."""
        d = self.xrd.d_spacing(45.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] d: {d:.4f} nm")
    
    def test_strain(self):
        """Should compute strain."""
        e = self.xrd.strain_from_d(0.202, 0.200)
        self.assertAlmostEqual(e, 0.01, delta=1e-10)
        print(f"  [PASS] Strain: {e:.4f}")


class TestSin2PsiMethod(unittest.TestCase):
    """Test sin2psi."""
    
    def setUp(self):
        self.s2p = Sin2PsiMethod()
    
    def test_stress(self):
        """Should compute stress."""
        s = self.s2p.stress_from_slope(1e-4)
        self.assertGreater(s, 0)
        print(f"  [PASS] S: {s:.1f}")
    
    def test_sin2psi(self):
        """Should compute sin2psi."""
        v = self.s2p.sin2psi_values([0.0, 30.0, 45.0])
        self.assertEqual(len(v), 3)
        print(f"  [PASS] sin2: {v}")


class TestStressRelaxation(unittest.TestCase):
    """Test relaxation."""
    
    def setUp(self):
        self.sr = StressRelaxation()
    
    def test_relaxed(self):
        """Should compute relaxed stress."""
        s = self.sr.relaxed_stress(100.0, 50.0)
        self.assertLess(s, 100.0)
        print(f"  [PASS] Srel: {s:.2f}")
    
    def test_rate(self):
        """Should compute rate."""
        r = self.sr.relaxation_rate(100.0, 10.0)
        self.assertEqual(r, -10.0)
        print(f"  [PASS] Rate: {r:.1f}")


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
