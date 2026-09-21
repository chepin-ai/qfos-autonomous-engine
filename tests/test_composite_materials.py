"""
Unit tests for composite materials module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from composite_materials import (PlyProperties, RuleOfMixtures,
                                 LaminateAnalysis,
                                 FailureCriteria,
                                 CompositeMaterials)


class TestRuleOfMixtures(unittest.TestCase):
    """Test ROM."""
    
    def setUp(self):
        self.rom = RuleOfMixtures()
    
    def test_longitudinal(self):
        """Should compute E1."""
        e = self.rom.longitudinal_modulus(200.0, 3.0, 0.6)
        self.assertAlmostEqual(e, 121.2, delta=0.1)
        print(f"  [PASS] E1: {e:.1f} GPa")
    
    def test_transverse(self):
        """Should compute E2."""
        e = self.rom.transverse_modulus(200.0, 3.0, 0.6)
        self.assertGreater(e, 0)
        print(f"  [PASS] E2: {e:.1f} GPa")
    
    def test_shear(self):
        """Should compute G12."""
        g = self.rom.shear_modulus(30.0, 1.0, 0.6)
        self.assertGreater(g, 0)
        print(f"  [PASS] G12: {g:.1f} GPa")
    
    def test_vf(self):
        """Should compute Vf."""
        vf = self.rom.fiber_volume_fraction(60.0, 40.0, 1.8, 1.2)
        self.assertGreater(vf, 0)
        self.assertLess(vf, 1.0)
        print(f"  [PASS] Vf: {vf:.3f}")


class TestLaminateAnalysis(unittest.TestCase):
    """Test laminate."""
    
    def setUp(self):
        self.la = LaminateAnalysis()
        self.la.add_ply(PlyProperties(150.0, 10.0, 5.0, 0.3, 0.125, 0.0))
        self.la.add_ply(PlyProperties(150.0, 10.0, 5.0, 0.3, 0.125, 90.0))
    
    def test_thickness(self):
        """Should compute thickness."""
        t = self.la.total_thickness()
        self.assertEqual(t, 0.25)
        print(f"  [PASS] t: {t:.3f} mm")
    
    def test_constants(self):
        """Should compute constants."""
        c = self.la.engineering_constants()
        self.assertIn("Ex", c)
        self.assertGreater(c["Ex"], 0)
        print(f"  [PASS] Ex: {c['Ex']:.1f}")
    
    def test_abd(self):
        """Should compute ABD."""
        A, B, D = self.la.abd_matrix()
        self.assertEqual(len(A), 3)
        print("  [PASS] ABD")


class TestFailureCriteria(unittest.TestCase):
    """Test failure."""
    
    def setUp(self):
        self.fc = FailureCriteria()
    
    def test_tsai_hill(self):
        """Should compute Tsai-Hill."""
        f = self.fc.tsai_hill(500.0, 30.0, 20.0, 1500.0, 1200.0, 50.0, 150.0, 80.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] TH: {f:.4f}")
    
    def test_max_stress(self):
        """Should compute max stress."""
        f = self.fc.maximum_stress(500.0, 30.0, 20.0, 1500.0, 1200.0, 50.0, 150.0, 80.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] MS: {f:.4f}")


class TestCompositeMaterials(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.cm = CompositeMaterials()
    
    def test_summary(self):
        """Should summarize."""
        s = self.cm.cm_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
