"""
Unit tests for spectrophotometry module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from spectrophotometry import (SpectrumPoint, BeerLambertLaw,
                               CalibrationCurve,
                               WavelengthAnalyzer,
                               Spectrophotometry)


class TestBeerLambertLaw(unittest.TestCase):
    """Test Beer-Lambert."""
    
    def setUp(self):
        self.bl = BeerLambertLaw()
    
    def test_absorbance(self):
        """Should compute absorbance."""
        a = self.bl.absorbance(1000.0, 0.01, 1.0)
        self.assertEqual(a, 10.0)
        print(f"  [PASS] A: {a}")
    
    def test_concentration(self):
        """Should compute concentration."""
        c = self.bl.concentration(1.0, 1000.0, 1.0)
        self.assertEqual(c, 0.001)
        print(f"  [PASS] C: {c}")
    
    def test_transmittance(self):
        """Should convert to transmittance."""
        t = self.bl.transmittance(1.0)
        self.assertEqual(t, 0.1)
        print(f"  [PASS] T: {t}")
    
    def test_abs_from_t(self):
        """Should convert from transmittance."""
        a = self.bl.absorbance_from_transmittance(0.1)
        self.assertEqual(a, 1.0)
        print(f"  [PASS] A: {a}")


class TestCalibrationCurve(unittest.TestCase):
    """Test calibration."""
    
    def setUp(self):
        self.cc = CalibrationCurve()
        self.cc.add_standard(0.0, 0.0)
        self.cc.add_standard(1.0, 2.0)
        self.cc.add_standard(2.0, 4.0)
    
    def test_fit(self):
        """Should fit."""
        s, i = self.cc.linear_fit()
        self.assertEqual(s, 2.0)
        self.assertEqual(i, 0.0)
        print(f"  [PASS] Fit: s={s}, i={i}")
    
    def test_r2(self):
        """Should compute R2."""
        r = self.cc.r_squared()
        self.assertEqual(r, 1.0)
        print(f"  [PASS] R2: {r}")
    
    def test_predict(self):
        """Should predict."""
        c = self.cc.predict_concentration(3.0)
        self.assertEqual(c, 1.5)
        print(f"  [PASS] Pred: {c}")


class TestWavelengthAnalyzer(unittest.TestCase):
    """Test wavelength."""
    
    def setUp(self):
        self.wa = WavelengthAnalyzer()
    
    def test_lambda_max(self):
        """Should find lambda max."""
        spec = [SpectrumPoint(400.0, 0.1, 0.8),
                SpectrumPoint(500.0, 1.0, 0.1),
                SpectrumPoint(600.0, 0.2, 0.6)]
        lm = self.wa.lambda_max(spec)
        self.assertEqual(lm, 500.0)
        print(f"  [PASS] lmax: {lm}")
    
    def test_peak_area(self):
        """Should integrate."""
        spec = [SpectrumPoint(400.0, 0.0, 1.0),
                SpectrumPoint(500.0, 1.0, 0.1),
                SpectrumPoint(600.0, 0.0, 1.0)]
        a = self.wa.peak_area(spec, 400.0, 600.0)
        self.assertGreater(a, 0)
        print(f"  [PASS] Area: {a:.1f}")
    
    def test_bandwidth(self):
        """Should compute bandwidth."""
        spec = [SpectrumPoint(490.0, 0.6, 0.25),
                SpectrumPoint(500.0, 1.0, 0.1),
                SpectrumPoint(510.0, 0.6, 0.25)]
        bw = self.wa.bandwidth(spec, 0.5)
        self.assertGreater(bw, 0)
        print(f"  [PASS] BW: {bw:.1f}")


class TestSpectrophotometry(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sp = Spectrophotometry()
    
    def test_analyze(self):
        """Should analyze."""
        spec = [SpectrumPoint(490.0, 0.1, 0.8),
                SpectrumPoint(500.0, 1.0, 0.1),
                SpectrumPoint(510.0, 0.1, 0.8)]
        self.sp.load_spectrum(spec)
        r = self.sp.analyze()
        self.assertIn("lambda_max_nm", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.sp.sp_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
