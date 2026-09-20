"""
Unit tests for neutron radiography module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from neutron_radiography import (NeutronType, NeutronImage,
                                  AttenuationCalculator,
                                  NeutronContrastAnalyzer,
                                  NeutronScatterCorrector,
                                  NeutronRadiography)


class TestAttenuationCalculator(unittest.TestCase):
    """Test attenuation."""
    
    def setUp(self):
        self.ac = AttenuationCalculator()
    
    def test_attenuation(self):
        """Should compute attenuation."""
        t = self.ac.attenuation("water", 1.0)
        self.assertGreater(t, 0)
        self.assertLess(t, 1.0)
        print(f"  [PASS] Att: {t:.4f}")
    
    def test_thickness(self):
        """Should estimate thickness."""
        thick = self.ac.thickness_from_attenuation("water", 0.03)
        self.assertGreater(thick, 0)
        print(f"  [PASS] Thick: {thick:.4f} cm")
    
    def test_add_material(self):
        """Should add material."""
        self.ac.add_material("custom", 2.0)
        t = self.ac.attenuation("custom", 1.0)
        self.assertAlmostEqual(t, math.exp(-2.0), places=5)
        print("  [PASS] AddMat")


class TestNeutronContrastAnalyzer(unittest.TestCase):
    """Test contrast."""
    
    def setUp(self):
        self.ca = NeutronContrastAnalyzer()
    
    def test_contrast(self):
        """Should compute contrast."""
        c = self.ca.contrast(800.0, 1000.0)
        self.assertEqual(c, 0.2)
        print(f"  [PASS] Contrast: {c}")
    
    def test_snr(self):
        """Should compute SNR."""
        snr = self.ca.signal_to_noise(100.0, 10.0)
        self.assertEqual(snr, 10.0)
        print(f"  [PASS] SNR: {snr}")
    
    def test_defect_map(self):
        """Should detect defects."""
        img = NeutronImage(0.1, 60.0, 1e6, [[1.0]*5 for _ in range(5)])
        img.data[2][2] = 0.5
        dm = self.ca.defect_map(img, 0.1)
        self.assertTrue(any(any(row) for row in dm))
        print("  [PASS] DefectMap")


class TestNeutronScatterCorrector(unittest.TestCase):
    """Test scatter correction."""
    
    def setUp(self):
        self.sc = NeutronScatterCorrector()
    
    def test_correct(self):
        """Should correct scatter."""
        img = NeutronImage(0.1, 60.0, 1e6, [[1.0]*3 for _ in range(3)])
        c = self.sc.correct(img)
        self.assertAlmostEqual(c.data[0][0], 0.85, places=5)
        print("  [PASS] Scatter")
    
    def test_dark(self):
        """Should subtract dark."""
        img = NeutronImage(0.1, 60.0, 1e6, [[1.0]*3 for _ in range(3)])
        dark = NeutronImage(0.1, 60.0, 1e6, [[0.2]*3 for _ in range(3)])
        c = self.sc.dark_current_subtract(img, dark)
        self.assertAlmostEqual(c.data[0][0], 0.8, places=5)
        print("  [PASS] Dark")


class TestNeutronRadiography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.nr = NeutronRadiography()
    
    def test_capture(self):
        """Should capture."""
        self.nr.capture([[1.0]*5 for _ in range(5)])
        self.assertEqual(len(self.nr.images), 1)
        print("  [PASS] Capture")
    
    def test_detect(self):
        """Should detect."""
        d = [[1.0]*5 for _ in range(5)]
        d[2][2] = 0.3
        self.nr.capture(d)
        defects = self.nr.detect_defects(0.1)
        self.assertGreater(len(defects), 0)
        print(f"  [PASS] Detect: {len(defects)} defects")
    
    def test_thickness(self):
        """Should estimate thickness."""
        self.nr.capture([[math.exp(-3.45)]*5 for _ in range(5)])
        t = self.nr.estimate_thickness("water", (0, 0, 5, 5))
        self.assertGreater(t, 0)
        print(f"  [PASS] Thick: {t:.4f} cm")
    
    def test_summary(self):
        """Should summarize."""
        self.nr.capture([[1.0]*3 for _ in range(3)])
        s = self.nr.radiography_summary()
        self.assertIn("images", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
