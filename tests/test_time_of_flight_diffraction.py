"""
Unit tests for time-of-flight diffraction module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from time_of_flight_diffraction import (TOFDProbe, AScanProcessor,
                                        DiffractionAnalyzer,
                                        ScanConverter, TOFDSystem)


class TestAScanProcessor(unittest.TestCase):
    """Test A-scan processor."""
    
    def setUp(self):
        self.asp = AScanProcessor(100.0)
    
    def test_envelope(self):
        """Should compute envelope."""
        s = [1.0, -2.0, 3.0, -1.0]
        e = self.asp.envelope(s)
        self.assertEqual(e, [1.0, 2.0, 3.0, 1.0])
        print(f"  [PASS] Env: {e}")
    
    def test_peaks(self):
        """Should find peaks."""
        s = [0.0, 0.5, 1.0, 0.5, 0.0]
        p = self.asp.find_peaks(s, 0.2)
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0][0], 2)
        print(f"  [PASS] Peaks: {p}")
    
    def test_time_to_depth(self):
        """Should convert time."""
        d = self.asp.time_to_depth(10.0, 5.9)
        self.assertEqual(d, 29.5)
        print(f"  [PASS] Depth: {d}")


class TestDiffractionAnalyzer(unittest.TestCase):
    """Test diffraction analyzer."""
    
    def setUp(self):
        self.da = DiffractionAnalyzer(TOFDProbe(20.0, 5.0, 60.0))
    
    def test_tip_depth(self):
        """Should compute tip depth."""
        d = self.da.tip_depth(10.0)
        self.assertGreaterEqual(d, 0.0)
        print(f"  [PASS] Tip: {d:.4f} mm")
    
    def test_lateral(self):
        """Should compute lateral wave."""
        t = self.da.lateral_wave_time()
        self.assertGreater(t, 0)
        print(f"  [PASS] Lateral: {t:.4f} us")
    
    def test_backwall(self):
        """Should compute backwall."""
        t = self.da.backwall_time(10.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] BW: {t:.4f} us")
    
    def test_classify(self):
        """Should classify."""
        c = self.da.classify_indication(5.0, 10.0)
        self.assertIn(c, ["lateral_wave", "backwall", "defect", "unknown"])
        print(f"  [PASS] Class: {c}")


class TestScanConverter(unittest.TestCase):
    """Test scan converter."""
    
    def setUp(self):
        self.sc = ScanConverter()
    
    def test_d_scan(self):
        """Should build D-scan."""
        scans = [[1.0, 2.0, 1.0], [1.0, 3.0, 1.0]]
        d = self.sc.build_d_scan(scans)
        self.assertEqual(len(d), 3)
        print("  [PASS] D-scan")
    
    def test_b_scan(self):
        """Should build B-scan."""
        scans = [[1.0, 2.0], [1.0, 3.0]]
        b = self.sc.build_b_scan(scans, [0.0, 10.0])
        self.assertEqual(len(b), 2)
        print("  [PASS] B-scan")


class TestTOFDSystem(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.tofd = TOFDSystem(20.0, 5.0, 60.0)
    
    def test_record(self):
        """Should record."""
        self.tofd.record_a_scan([0.0, 1.0, 2.0, 1.0, 0.0])
        self.assertEqual(len(self.tofd.a_scans), 1)
        print("  [PASS] Record")
    
    def test_analyze(self):
        """Should analyze."""
        self.tofd.record_a_scan([0.0, 0.5, 1.0, 0.5, 0.0])
        ind = self.tofd.analyze(10.0)
        self.assertGreaterEqual(len(ind), 0)
        print(f"  [PASS] Analyze: {len(ind)} indications")
    
    def test_d_scan(self):
        """Should generate D-scan."""
        self.tofd.record_a_scan([1.0, 2.0, 1.0])
        self.tofd.record_a_scan([1.0, 3.0, 1.0])
        d = self.tofd.generate_d_scan()
        self.assertEqual(len(d), 3)
        print("  [PASS] GenD")
    
    def test_summary(self):
        """Should summarize."""
        self.tofd.record_a_scan([1.0, 2.0, 1.0])
        s = self.tofd.tofd_summary()
        self.assertIn("scans", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
