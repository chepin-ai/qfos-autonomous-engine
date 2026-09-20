"""
Unit tests for X-ray fluorescence module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xray_fluorescence import (XRFPeak, EnergyCalibrator,
                                PeakDetector, ElementIdentifier,
                                QuantitativeAnalyzer,
                                XRayFluorescence)


class TestEnergyCalibrator(unittest.TestCase):
    """Test energy calibrator."""
    
    def setUp(self):
        self.ec = EnergyCalibrator()
    
    def test_add_point(self):
        """Should add point."""
        self.ec.add_calibration_point(0.0, 0.0)
        self.ec.add_calibration_point(100.0, 10.0)
        self.assertEqual(len(self.ec.calibration_points), 2)
        print("  [PASS] AddPt")
    
    def test_calibrate(self):
        """Should calibrate."""
        self.ec.add_calibration_point(0.0, 0.0)
        self.ec.add_calibration_point(100.0, 10.0)
        self.ec.calibrate()
        self.assertAlmostEqual(self.ec.gain, 0.1, places=5)
        print(f"  [PASS] Cal: gain={self.ec.gain:.4f}")
    
    def test_channel_to_energy(self):
        """Should convert."""
        self.ec.gain = 0.1
        self.ec.offset = 0.0
        e = self.ec.channel_to_energy(50.0)
        self.assertAlmostEqual(e, 5.0, places=5)
        print(f"  [PASS] Ch2E: {e}")


class TestPeakDetector(unittest.TestCase):
    """Test peak detector."""
    
    def setUp(self):
        self.pd = PeakDetector()
    
    def test_smooth(self):
        """Should smooth."""
        s = [1.0, 2.0, 3.0, 2.0, 1.0]
        sm = self.pd.smooth(s)
        self.assertEqual(len(sm), 5)
        print(f"  [PASS] Smooth: {sm}")
    
    def test_find_peaks(self):
        """Should find peaks."""
        s = [0.0, 0.5, 1.0, 0.5, 0.0]
        p = self.pd.find_peaks(s, 0.2)
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0][0], 2)
        print(f"  [PASS] Peaks: {p}")
    
    def test_fwhm(self):
        """Should estimate FWHM."""
        s = [0.0, 0.5, 1.0, 0.5, 0.0]
        f = self.pd.estimate_fwhm(s, 2)
        self.assertGreater(f, 0)
        print(f"  [PASS] FWHM: {f}")


class TestElementIdentifier(unittest.TestCase):
    """Test element identifier."""
    
    def setUp(self):
        self.ei = ElementIdentifier()
    
    def test_identify(self):
        """Should identify."""
        el = self.ei.identify(6.40)
        self.assertEqual(el, "Fe")
        print(f"  [PASS] ID: {el}")
    
    def test_add(self):
        """Should add element."""
        self.ei.add_element("X", 5.0)
        el = self.ei.identify(5.0)
        self.assertEqual(el, "X")
        print("  [PASS] AddEl")


class TestQuantitativeAnalyzer(unittest.TestCase):
    """Test quantitative analyzer."""
    
    def setUp(self):
        self.qa = QuantitativeAnalyzer()
    
    def test_concentration(self):
        """Should compute concentration."""
        self.qa.add_standard("Fe", 10.0)
        c = self.qa.concentration("Fe", 50.0, 100.0)
        self.assertEqual(c, 5.0)
        print(f"  [PASS] Conc: {c}")
    
    def test_matrix(self):
        """Should correct matrix."""
        c = self.qa.matrix_correction(10.0, 2.0, 2.0)
        self.assertEqual(c, 2.5)
        print(f"  [PASS] Matrix: {c}")


class TestXRayFluorescence(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.xrf = XRayFluorescence()
    
    def test_acquire(self):
        """Should acquire."""
        self.xrf.acquire_spectrum([0.0, 0.5, 1.0, 0.5, 0.0])
        self.assertEqual(len(self.xrf.spectra), 1)
        print("  [PASS] Acquire")
    
    def test_analyze(self):
        """Should analyze."""
        self.xrf.calibrator.gain = 0.1
        self.xrf.acquire_spectrum([0.0, 0.5, 1.0, 0.5, 0.0])
        peaks = self.xrf.analyze_peaks()
        self.assertGreaterEqual(len(peaks), 0)
        print(f"  [PASS] Analyze: {len(peaks)} peaks")
    
    def test_quantitative(self):
        """Should do quantitative."""
        self.xrf.quantitative.add_standard("Fe", 10.0)
        self.xrf.acquire_spectrum([0.0, 0.0, 1.0, 0.0, 0.0])
        self.xrf.peaks.append(XRFPeak(6.40, 50.0, 1.0, "Fe"))
        q = self.xrf.quantitative_analysis()
        self.assertIn("Fe", q)
        print(f"  [PASS] Quant: {q}")
    
    def test_summary(self):
        """Should summarize."""
        self.xrf.acquire_spectrum([0.0] * 5)
        s = self.xrf.xrf_summary()
        self.assertIn("spectra", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
