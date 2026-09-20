"""
Unit tests for neutron radiography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from neutron_radiography import (MaterialProperties,
                                  NeutronAttenuationCalculator,
                                  ContrastEnhancer,
                                  ScatteringCorrector,
                                  NeutronDefectDetector,
                                  NeutronRadiography)


class TestNeutronAttenuationCalculator(unittest.TestCase):
    """Test attenuation."""
    
    def setUp(self):
        self.nac = NeutronAttenuationCalculator()
        self.nac.register_material(MaterialProperties("water", 3.45, 1.0))
    
    def test_attenuation(self):
        """Should compute attenuation."""
        a = self.nac.attenuation("water", 0.1)
        self.assertLess(a, 1.0)
        print(f"  [PASS] Att: {a:.4f}")
    
    def test_transmitted(self):
        """Should compute transmitted flux."""
        t = self.nac.transmitted_flux(1000.0, "water", 0.1)
        self.assertLess(t, 1000.0)
        print(f"  [PASS] Flux: {t:.2f}")


class TestContrastEnhancer(unittest.TestCase):
    """Test enhancer."""
    
    def setUp(self):
        self.ce = ContrastEnhancer()
    
    def test_normalize(self):
        """Should normalize."""
        img = [0.0, 0.5, 1.0]
        n = self.ce.normalize(img)
        self.assertEqual(n[0], 0.0)
        self.assertEqual(n[-1], 1.0)
        print(f"  [PASS] Norm: {n}")
    
    def test_histogram(self):
        """Should equalize."""
        img = [0.0, 0.25, 0.5, 0.75, 1.0]
        e = self.ce.histogram_equalize(img)
        self.assertEqual(len(e), 5)
        print("  [PASS] Hist")


class TestScatteringCorrector(unittest.TestCase):
    """Test corrector."""
    
    def setUp(self):
        self.sc = ScatteringCorrector(0.1)
    
    def test_correct(self):
        """Should correct."""
        img = [1.1, 1.1, 1.1]
        c = self.sc.correct(img)
        self.assertAlmostEqual(c[0], 1.0, places=1)
        print(f"  [PASS] Corr: {c}")


class TestNeutronDefectDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.ndd = NeutronDefectDetector(0.3)
    
    def test_detect(self):
        """Should detect defects."""
        img = [1.0] * 8 + [2.0, 2.0]
        d = self.ndd.detect(img, 5, 2)
        self.assertGreater(len(d), 0)
        print(f"  [PASS] Def: {len(d)}")
    
    def test_no_defect(self):
        """Should not detect uniform."""
        img = [1.0] * 10
        d = self.ndd.detect(img, 5, 2)
        self.assertEqual(len(d), 0)
        print("  [PASS] NoDef")


class TestNeutronRadiography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.nr = NeutronRadiography()
    
    def test_register(self):
        """Should register material."""
        self.nr.register_material("water", 3.45, 1.0)
        self.assertEqual(len(self.nr.attenuation.materials), 1)
        print("  [PASS] Reg")
    
    def test_capture(self):
        """Should capture."""
        self.nr.capture([0.5, 0.6, 0.7])
        self.assertEqual(len(self.nr.image), 3)
        print("  [PASS] Cap")
    
    def test_process(self):
        """Should process."""
        self.nr.capture([0.5, 0.6, 0.7])
        p = self.nr.process()
        self.assertEqual(len(p), 3)
        print("  [PASS] Proc")
    
    def test_inspect(self):
        """Should inspect."""
        img = [1.0] * 8 + [2.0, 2.0]
        self.nr.capture(img)
        r = self.nr.inspect(5, 2)
        self.assertIn("defects", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.nr.nr_summary()
        self.assertIn("image_size", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
