"""
Unit tests for X-ray inspection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xray_inspection import (DefectTypeXRay, XRayPixel,
                             AbsorptionCalculator, DensityEstimator,
                             ContrastAnalyzer, XRayDefectDetector,
                             XRayInspection)


class TestAbsorptionCalculator(unittest.TestCase):
    """Test absorption calculator."""
    
    def setUp(self):
        self.ac = AbsorptionCalculator()
    
    def test_transmission(self):
        """Should compute transmission."""
        T = self.ac.transmission("steel", 10.0)
        self.assertGreater(T, 0)
        self.assertLess(T, 1.0)
        print(f"  [PASS] T: {T:.4f}")
    
    def test_absorbance(self):
        """Should compute absorbance."""
        A = self.ac.absorbance("steel", 10.0)
        self.assertGreater(A, 0)
        print(f"  [PASS] A: {A:.4f}")
    
    def test_materials(self):
        """Should have materials."""
        self.assertIn("steel", self.ac.attenuation)
        self.assertIn("air", self.ac.densities)
        print("  [PASS] Mats")


class TestDensityEstimator(unittest.TestCase):
    """Test density estimator."""
    
    def setUp(self):
        self.de = DensityEstimator()
    
    def test_estimate_default(self):
        """Should estimate with default."""
        d = self.de.estimate(0.5)
        self.assertGreater(d, 0)
        print(f"  [PASS] Est: {d:.2f}")
    
    def test_calibrate(self):
        """Should calibrate."""
        self.de.calibrate(7.85, 0.3)
        self.de.calibrate(2.70, 0.8)
        d = self.de.estimate(0.5)
        self.assertGreater(d, 2.70)
        self.assertLess(d, 7.85)
        print(f"  [PASS] Cal: {d:.2f}")


class TestContrastAnalyzer(unittest.TestCase):
    """Test contrast analyzer."""
    
    def setUp(self):
        self.ca = ContrastAnalyzer()
    
    def test_contrast(self):
        """Should compute contrast."""
        c = self.ca.contrast(0.8, 0.6)
        self.assertAlmostEqual(c, 0.2 / 1.4, places=5)
        print(f"  [PASS] C: {c:.4f}")
    
    def test_snr(self):
        """Should compute SNR."""
        snr = self.ca.signal_to_noise(1.0, 0.1)
        self.assertAlmostEqual(snr, 10.0)
        print(f"  [PASS] SNR: {snr}")
    
    def test_detectability(self):
        """Should estimate detectability."""
        d = self.ca.detectability(1.0, "steel")
        self.assertGreater(d, 0)
        print(f"  [PASS] Det: {d:.4f}")


class TestXRayDefectDetector(unittest.TestCase):
    """Test defect detector."""
    
    def setUp(self):
        self.xdd = XRayDefectDetector()
    
    def test_detect(self):
        """Should detect defects."""
        pixels = [XRayPixel(i, 0, 0.5) for i in range(10)]
        pixels[5].intensity = 0.9
        defects = self.xdd.detect(pixels)
        self.assertGreater(len(defects), 0)
        print(f"  [PASS] Defects: {len(defects)}")
    
    def test_porosity(self):
        """Should estimate porosity."""
        pixels = [XRayPixel(i, 0, 0.5) for i in range(100)]
        p = self.xdd.porosity_fraction(pixels)
        self.assertGreaterEqual(p, 0)
        self.assertLessEqual(p, 1.0)
        print(f"  [PASS] Por: {p:.4f}")


class TestXRayInspection(unittest.TestCase):
    """Test unified X-ray inspection."""
    
    def setUp(self):
        self.xi = XRayInspection()
    
    def test_inspect(self):
        """Should inspect."""
        pixels = [XRayPixel(i, 0, 0.3 + i * 0.01) for i in range(20)]
        r = self.xi.inspect(pixels, "steel")
        self.assertIn("porosity_fraction", r)
        print(f"  [PASS] Insp: por={r['porosity_fraction']:.4f}")
    
    def test_thickness(self):
        """Should estimate thickness."""
        t = self.xi.thickness_from_transmission(0.5, "steel")
        self.assertGreater(t, 0)
        print(f"  [PASS] Thick: {t:.3f}mm")
    
    def test_summary(self):
        """Should summarize."""
        pixels = [XRayPixel(i, 0, 0.5) for i in range(10)]
        self.xi.inspect(pixels)
        s = self.xi.inspection_summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
