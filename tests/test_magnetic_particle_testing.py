"""
Unit tests for magnetic particle testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from magnetic_particle_testing import (MTIndication, Magnetizer,
                                       IndicationAnalyzer,
                                       ParticleConcentration,
                                       SensitivityVerifier,
                                       MagneticParticleTesting)


class TestMagnetizer(unittest.TestCase):
    """Test magnetizer."""
    
    def setUp(self):
        self.m = Magnetizer()
    
    def test_longitudinal(self):
        """Should compute field."""
        H = self.m.longitudinal_magnetization(1000.0, 5, 0.5)
        self.assertEqual(H, 10000.0)
        print(f"  [PASS] H: {H:.0f} A/m")
    
    def test_circular(self):
        """Should compute circular field."""
        H = self.m.circular_magnetization(1000.0, 0.05)
        self.assertGreater(H, 0)
        print(f"  [PASS] Hc: {H:.0f} A/m")
    
    def test_required_current(self):
        """Should compute current."""
        I = self.m.required_current(0.0254, "ASTM")
        self.assertAlmostEqual(I, 350.0, delta=0.01)
        print(f"  [PASS] I: {I:.0f} A")
    
    def test_flux_density(self):
        """Should compute B."""
        B = self.m.flux_density(10000.0)
        self.assertGreater(B, 0)
        print(f"  [PASS] B: {B:.4f} T")


class TestIndicationAnalyzer(unittest.TestCase):
    """Test indication."""
    
    def setUp(self):
        self.ia = IndicationAnalyzer()
    
    def test_area(self):
        """Should compute area."""
        a = self.ia.indication_area(5.0, 2.0)
        self.assertEqual(a, 10.0)
        print(f"  [PASS] A: {a:.1f} mm2")
    
    def test_severity(self):
        """Should rate severity."""
        s = self.ia.severity_rating(2.0)
        self.assertEqual(s, "moderate")
        print(f"  [PASS] Sev: {s}")
    
    def test_false_call(self):
        """Should estimate false call."""
        p = self.ia.false_call_probability(0.5, 0.8)
        self.assertGreater(p, 0)
        print(f"  [PASS] FP: {p:.1f}")


class TestParticleConcentration(unittest.TestCase):
    """Test concentration."""
    
    def setUp(self):
        self.pc = ParticleConcentration()
    
    def test_concentration(self):
        """Should compute concentration."""
        c = self.pc.concentration_from_settling(0.2, 100.0)
        self.assertEqual(c, 0.2)
        print(f"  [PASS] C: {c:.2f} ml/100ml")
    
    def test_acceptable(self):
        """Should check acceptability."""
        self.assertTrue(self.pc.is_acceptable(0.2))
        self.assertFalse(self.pc.is_acceptable(0.5))
        print("  [PASS] Acc")


class TestSensitivityVerifier(unittest.TestCase):
    """Test sensitivity."""
    
    def setUp(self):
        self.sv = SensitivityVerifier()
    
    def test_pie(self):
        """Should compute pie sensitivity."""
        s = self.sv.pie_gauge_sensitivity(6)
        self.assertEqual(s, 0.75)
        print(f"  [PASS] Pie: {s:.2f}")
    
    def test_ketos(self):
        """Should compute Ketos sensitivity."""
        s = self.sv.ketos_ring_sensitivity(9)
        self.assertEqual(s, 0.75)
        print(f"  [PASS] Ket: {s:.2f}")


class TestMagneticParticleTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mpt = MagneticParticleTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.mpt.mpt_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
