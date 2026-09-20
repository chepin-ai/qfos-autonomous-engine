"""
Unit tests for mass spectrometry module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mass_spectrometry import (MassPeak, SpectrumAcquisition,
                               PeakIdentifier,
                               IsotopePattern,
                               MassCalibrator,
                               FragmentationAnalyzer,
                               MassSpectrometry)


class TestSpectrumAcquisition(unittest.TestCase):
    """Test acquisition."""
    
    def setUp(self):
        self.sa = SpectrumAcquisition(10000.0, (10.0, 2000.0))
    
    def test_resolve(self):
        """Should resolve."""
        w = self.sa.resolve_peak(100.0)
        self.assertEqual(w, 0.01)
        print(f"  [PASS] Res: {w}")
    
    def test_scan(self):
        """Should scan."""
        peaks = [MassPeak(50.0, 100.0), MassPeak(3000.0, 50.0)]
        r = self.sa.scan(peaks)
        self.assertEqual(len(r), 1)
        print(f"  [PASS] Scan: {len(r)}")


class TestPeakIdentifier(unittest.TestCase):
    """Test identifier."""
    
    def setUp(self):
        self.pi = PeakIdentifier(10.0)
    
    def test_match(self):
        """Should match."""
        m = self.pi.match(100.0005, 100.0)
        self.assertTrue(m)
        print("  [PASS] Match")
    
    def test_no_match(self):
        """Should not match."""
        m = self.pi.match(100.1, 100.0)
        self.assertFalse(m)
        print("  [PASS] NoMatch")
    
    def test_identify(self):
        """Should identify."""
        lib = {"ethanol": 46.041}
        c = self.pi.identify(46.041, lib)
        self.assertEqual(c, "ethanol")
        print(f"  [PASS] ID: {c}")


class TestIsotopePattern(unittest.TestCase):
    """Test isotope."""
    
    def setUp(self):
        self.ip = IsotopePattern()
    
    def test_mono(self):
        """Should compute monoisotopic mass."""
        m = self.ip.monoisotopic_mass({"C": 2, "H": 6, "O": 1})
        self.assertAlmostEqual(m, 46.041, places=2)
        print(f"  [PASS] Mono: {m:.3f}")
    
    def test_peaks(self):
        """Should compute isotope peaks."""
        peaks = self.ip.isotope_peaks({"C": 6}, 3)
        self.assertGreater(len(peaks), 0)
        print(f"  [PASS] Iso: {len(peaks)} peaks")


class TestMassCalibrator(unittest.TestCase):
    """Test calibrator."""
    
    def setUp(self):
        self.mc = MassCalibrator()
    
    def test_calibrate(self):
        """Should calibrate."""
        self.mc.add_calibrant(100.01, 100.0)
        self.mc.add_calibrant(200.02, 200.0)
        mz = self.mc.apply(150.015)
        self.assertAlmostEqual(mz, 150.0, places=1)
        print(f"  [PASS] Cal: {mz:.3f}")
    
    def test_linear(self):
        """Should compute linear fit."""
        self.mc.add_calibrant(100.0, 100.0)
        self.mc.add_calibrant(200.0, 200.0)
        s, i = self.mc.linear_calibration()
        self.assertAlmostEqual(s, 1.0, places=5)
        self.assertAlmostEqual(i, 0.0, places=5)
        print(f"  [PASS] Fit: s={s:.4f}, i={i:.4f}")


class TestFragmentationAnalyzer(unittest.TestCase):
    """Test fragmentation."""
    
    def setUp(self):
        self.fa = FragmentationAnalyzer()
        self.fa.add_fragment("ethanol", [45.0, 31.0, 29.0])
    
    def test_score(self):
        """Should score."""
        s = self.fa.score_match([45.0, 31.0], "ethanol")
        self.assertGreater(s, 0)
        print(f"  [PASS] Scr: {s:.2f}")
    
    def test_no_match(self):
        """Should return 0."""
        s = self.fa.score_match([1000.0], "ethanol")
        self.assertEqual(s, 0.0)
        print("  [PASS] NoScr")


class TestMassSpectrometry(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ms = MassSpectrometry()
    
    def test_load(self):
        """Should load."""
        peaks = [MassPeak(46.0, 100.0), MassPeak(100.0, 50.0)]
        self.ms.load_spectrum(peaks)
        self.assertEqual(len(self.ms.spectrum), 2)
        print("  [PASS] Load")
    
    def test_analyze(self):
        """Should analyze."""
        peaks = [MassPeak(46.041, 100.0)]
        self.ms.load_spectrum(peaks)
        r = self.ms.analyze({"ethanol": 46.041})
        self.assertIn("identified", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ms.ms_summary()
        self.assertIn("peaks", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
