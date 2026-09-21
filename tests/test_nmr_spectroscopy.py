"""
Unit tests for NMR spectroscopy module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nmr_spectroscopy import (NMRPeak, ChemicalShiftCalculator,
                              SpinSystem,
                              SpectralProcessor,
                              TwoDNMR,
                              NMRSpectroscopy)


class TestChemicalShiftCalculator(unittest.TestCase):
    """Test shift calculator."""
    
    def setUp(self):
        self.csc = ChemicalShiftCalculator()
    
    def test_freq(self):
        """Should convert to Hz."""
        f = self.csc.frequency(1.0, 400.0)
        self.assertEqual(f, 400.0)
        print(f"  [PASS] Hz: {f}")
    
    def test_ppm(self):
        """Should convert to ppm."""
        p = self.csc.ppm(400.0, 400.0)
        self.assertEqual(p, 1.0)
        print(f"  [PASS] ppm: {p}")


class TestSpinSystem(unittest.TestCase):
    """Test spin system."""
    
    def setUp(self):
        self.ss = SpinSystem()
        self.ss.add_spin("1H", 3.5, 7.0)
    
    def test_add(self):
        """Should add spin."""
        self.assertEqual(len(self.ss.spins), 1)
        print("  [PASS] Add")
    
    def test_splitting(self):
        """Should split."""
        peaks = self.ss.first_order_splitting(3.5, 7.0, 400.0, 1)
        self.assertEqual(len(peaks), 2)
        print(f"  [PASS] Split: {len(peaks)} lines")
    
    def test_multiplicity(self):
        """Should determine multiplicity."""
        m = self.ss.multiplicity(2)
        self.assertEqual(m, "t")
        print(f"  [PASS] Mult: {m}")


class TestSpectralProcessor(unittest.TestCase):
    """Test processor."""
    
    def setUp(self):
        self.sp = SpectralProcessor()
    
    def test_baseline(self):
        """Should correct baseline."""
        spec = [(0.0, 1.0), (1.0, 2.0), (2.0, 1.0)]
        c = self.sp.baseline_correction(spec)
        self.assertEqual(c[0][1], 0.0)
        print("  [PASS] Base")
    
    def test_integrate(self):
        """Should integrate."""
        spec = [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0)]
        i = self.sp.integrate(spec, 0.0, 2.0)
        self.assertGreater(i, 0)
        print(f"  [PASS] Int: {i:.2f}")
    
    def test_snr(self):
        """Should compute SNR."""
        spec = [(0.0, 0.1), (1.0, 10.0), (2.0, 0.1)]
        snr = self.sp.signal_to_noise(spec, (0.8, 1.2))
        self.assertGreater(snr, 0)
        print(f"  [PASS] SNR: {snr:.2f}")


class TestTwoDNMR(unittest.TestCase):
    """Test 2D NMR."""
    
    def setUp(self):
        self.td = TwoDNMR()
    
    def test_peak(self):
        """Should create peak."""
        p = self.td.correlation_peak(3.5, 7.2, 1.0)
        self.assertEqual(p["f1_ppm"], 3.5)
        print("  [PASS] Peak")
    
    def test_cross(self):
        """Should check correlation."""
        a = NMRPeak(3.5, 1.0)
        b = NMRPeak(3.6, 1.0)
        c = self.td.cross_peak(a, b)
        self.assertTrue(c)
        print("  [PASS] Cross")


class TestNMRSpectroscopy(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.nmr = NMRSpectroscopy(400.0)
    
    def test_add(self):
        """Should add peak."""
        self.nmr.add_peak(NMRPeak(3.5, 1.0, "t", 7.0))
        self.assertEqual(len(self.nmr.spectrum), 1)
        print("  [PASS] Add")
    
    def test_analyze(self):
        """Should analyze."""
        self.nmr.add_peak(NMRPeak(3.5, 1.0))
        r = self.nmr.analyze()
        self.assertIn("peaks", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.nmr.nmr_summary()
        self.assertIn("larmor_mhz", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
