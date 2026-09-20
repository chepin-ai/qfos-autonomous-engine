"""
Unit tests for chromatography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chromatography import (ChromatogramPoint, PeakDetector,
                            RetentionTimeAnalyzer,
                            GasChromatography,
                            LiquidChromatography,
                            Chromatography)


class TestPeakDetector(unittest.TestCase):
    """Test peak detector."""
    
    def setUp(self):
        self.pd = PeakDetector(0.5, 3)
    
    def test_detect(self):
        """Should detect peaks."""
        data = [ChromatogramPoint(0.0, 0.0),
                ChromatogramPoint(1.0, 0.0),
                ChromatogramPoint(2.0, 2.0),
                ChromatogramPoint(3.0, 2.0),
                ChromatogramPoint(4.0, 2.0),
                ChromatogramPoint(5.0, 0.0)]
        peaks = self.pd.detect_peaks(data)
        self.assertEqual(len(peaks), 1)
        print(f"  [PASS] Det: {len(peaks)} peaks")
    
    def test_no_peaks(self):
        """Should detect no peaks."""
        data = [ChromatogramPoint(0.0, 0.0),
                ChromatogramPoint(1.0, 0.1)]
        peaks = self.pd.detect_peaks(data)
        self.assertEqual(len(peaks), 0)
        print("  [PASS] NoPeak")


class TestRetentionTimeAnalyzer(unittest.TestCase):
    """Test RT analyzer."""
    
    def setUp(self):
        self.rta = RetentionTimeAnalyzer()
        self.rta.add_reference("ethanol", 2.5)
        self.rta.add_reference("methanol", 1.8)
    
    def test_identify(self):
        """Should identify."""
        c = self.rta.identify(2.5, 0.3)
        self.assertEqual(c, "ethanol")
        print(f"  [PASS] ID: {c}")
    
    def test_not_found(self):
        """Should not identify."""
        c = self.rta.identify(10.0, 0.1)
        self.assertIsNone(c)
        print("  [PASS] NF")
    
    def test_resolution(self):
        """Should compute resolution."""
        r = self.rta.resolution(2.0, 3.0, 0.5, 0.5)
        self.assertEqual(r, 2.0)
        print(f"  [PASS] Res: {r}")


class TestGasChromatography(unittest.TestCase):
    """Test GC."""
    
    def setUp(self):
        self.gc = GasChromatography(30.0, "helium")
    
    def test_retention_factor(self):
        """Should compute k."""
        k = self.gc.retention_factor(5.0, 2.0)
        self.assertEqual(k, 1.5)
        print(f"  [PASS] k: {k}")
    
    def test_selectivity(self):
        """Should compute alpha."""
        a = self.gc.selectivity_factor(4.0, 6.0, 2.0)
        self.assertEqual(a, 2.0)
        print(f"  [PASS] Alpha: {a}")
    
    def test_plates(self):
        """Should compute N."""
        n = self.gc.theoretical_plates(10.0, 1.0)
        self.assertEqual(n, 1600.0)
        print(f"  [PASS] N: {n}")
    
    def test_plate_height(self):
        """Should compute H."""
        h = self.gc.plate_height(10.0, 1.0)
        self.assertEqual(h, 18.75)
        print(f"  [PASS] H: {h} mm")


class TestLiquidChromatography(unittest.TestCase):
    """Test LC."""
    
    def setUp(self):
        self.lc = LiquidChromatography(1.0)
    
    def test_void(self):
        """Should compute void volume."""
        v = self.lc.void_volume(10.0)
        self.assertEqual(v, 6.0)
        print(f"  [PASS] V0: {v} ml")
    
    def test_dead_time(self):
        """Should compute dead time."""
        t = self.lc.dead_time(10.0)
        self.assertEqual(t, 6.0)
        print(f"  [PASS] t0: {t} min")


class TestChromatography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.chrom = Chromatography()
    
    def test_load(self):
        """Should load."""
        data = [ChromatogramPoint(0.0, 0.0),
                ChromatogramPoint(2.0, 2.0)]
        self.chrom.load_data(data)
        self.assertEqual(len(self.chrom.chromatogram), 2)
        print("  [PASS] Load")
    
    def test_analyze(self):
        """Should analyze."""
        data = [ChromatogramPoint(0.0, 0.0),
                ChromatogramPoint(1.0, 0.0),
                ChromatogramPoint(2.0, 2.0),
                ChromatogramPoint(3.0, 1.0),
                ChromatogramPoint(4.0, 0.0)]
        self.chrom.load_data(data)
        r = self.chrom.analyze()
        self.assertIn("peaks", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.chrom.chrom_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
