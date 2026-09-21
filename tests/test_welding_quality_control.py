"""
Unit tests for welding quality control module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from welding_quality_control import (WeldBead, WeldBeadGeometry,
                                     HeatAffectedZone,
                                     WeldDefectDetection,
                                     WeldMechanicalProperties,
                                     WeldingQualityControl)


class TestWeldBeadGeometry(unittest.TestCase):
    """Test bead."""
    
    def setUp(self):
        self.wbg = WeldBeadGeometry()
    
    def test_aspect(self):
        """Should compute aspect ratio."""
        bead = WeldBead(10.0, 5.0, 3.0, 2.0)
        r = self.wbg.aspect_ratio(bead)
        self.assertEqual(r, 2.0)
        print(f"  [PASS] AR: {r:.1f}")
    
    def test_dilution(self):
        """Should compute dilution."""
        bead = WeldBead(10.0, 5.0, 3.0, 2.0)
        d = self.wbg.dilution(bead, 15.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Dil: {d:.3f}")
    
    def test_throat(self):
        """Should compute throat."""
        bead = WeldBead(10.0, 5.0, 3.0, 2.0)
        t = self.wbg.throat_thickness(bead, 45.0)
        self.assertAlmostEqual(t, 5.0 * math.sin(math.radians(45.0)), delta=0.01)
        print(f"  [PASS] Th: {t:.2f}")


class TestHeatAffectedZone(unittest.TestCase):
    """Test HAZ."""
    
    def setUp(self):
        self.haz = HeatAffectedZone()
    
    def test_width(self):
        """Should compute HAZ width."""
        w = self.haz.haz_width(1000.0, 20.0)
        self.assertGreater(w, 0)
        print(f"  [PASS] W: {w:.2f} mm")
    
    def test_cooling(self):
        """Should compute cooling time."""
        t = self.haz.cooling_time_t8_5(1000.0, 10.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] t8/5: {t:.1f} s")


class TestWeldDefectDetection(unittest.TestCase):
    """Test defects."""
    
    def setUp(self):
        self.wdd = WeldDefectDetection()
    
    def test_porosity(self):
        """Should compute porosity."""
        p = self.wdd.porosity_fraction(2.0, 100.0)
        self.assertEqual(p, 0.02)
        print(f"  [PASS] Por: {p:.3f}")
    
    def test_crack(self):
        """Should check crack."""
        ok = self.wdd.crack_acceptance(0.5, 10.0)
        self.assertTrue(ok)
        print("  [PASS] Crack OK")
    
    def test_undercut(self):
        """Should check undercut."""
        ok = self.wdd.undercut_depth_acceptance(0.3, 10.0)
        self.assertTrue(ok)
        print("  [PASS] Undercut OK")


class TestWeldMechanicalProperties(unittest.TestCase):
    """Test mechanical."""
    
    def setUp(self):
        self.wmp = WeldMechanicalProperties()
    
    def test_hardness(self):
        """Should estimate hardness."""
        h = self.wmp.hardness_haz(200.0, 0.4, 10.0)
        self.assertGreater(h, 200.0)
        print(f"  [PASS] HV: {h:.1f}")
    
    def test_tensile(self):
        """Should estimate UTS."""
        u = self.wmp.tensile_strength_estimate(500.0, 0.3)
        self.assertGreater(u, 0)
        print(f"  [PASS] UTS: {u:.1f} MPa")


class TestWeldingQualityControl(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.wqc = WeldingQualityControl()
    
    def test_summary(self):
        """Should summarize."""
        s = self.wqc.welding_summary()
        self.assertIn("metrics", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
