"""
Unit tests for shear wave module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shear_wave import (ShearWaveProbe, SnellLawConverter,
                         ShearWavePath, WeldDefectDetector,
                         ShearWaveSystem)


class TestSnellLawConverter(unittest.TestCase):
    """Test Snell's law."""
    
    def setUp(self):
        self.sc = SnellLawConverter()
    
    def test_long_angle(self):
        """Should compute longitudinal angle."""
        a = self.sc.longitudinal_angle(45.0)
        self.assertGreater(a, 45.0)
        print(f"  [PASS] Long: {a:.2f}")
    
    def test_shear_angle(self):
        """Should compute shear angle."""
        a = self.sc.shear_angle(45.0)
        self.assertLess(a, 45.0)
        print(f"  [PASS] Shear: {a:.2f}")
    
    def test_critical(self):
        """Should compute critical angle."""
        c = self.sc.critical_angle()
        self.assertGreater(c, 0)
        print(f"  [PASS] Crit: {c:.2f}")


class TestShearWavePath(unittest.TestCase):
    """Test path."""
    
    def setUp(self):
        self.p = ShearWavePath(ShearWaveProbe(45.0, 5.0, 10.0))
    
    def test_skip(self):
        """Should compute skip distance."""
        d = self.p.skip_distance(10.0)
        self.assertAlmostEqual(d, 20.0, places=5)
        print(f"  [PASS] Skip: {d}")
    
    def test_sound_path(self):
        """Should compute sound path."""
        sp = self.p.sound_path(10.0)
        self.assertGreater(sp, 0)
        print(f"  [PASS] SP: {sp:.4f}")
    
    def test_depth(self):
        """Should compute depth."""
        d = self.p.depth_from_path(28.28)
        self.assertGreater(d, 0)
        print(f"  [PASS] Depth: {d:.4f}")
    
    def test_surface(self):
        """Should compute surface distance."""
        d = self.p.surface_distance(28.28)
        self.assertGreater(d, 0)
        print(f"  [PASS] Surf: {d:.4f}")


class TestWeldDefectDetector(unittest.TestCase):
    """Test defect detector."""
    
    def setUp(self):
        self.wd = WeldDefectDetector()
    
    def test_locate(self):
        """Should locate."""
        loc = self.wd.locate_defect(0.0, 28.28, 45.0, 10.0)
        self.assertIn("x_mm", loc)
        self.assertIn("depth_mm", loc)
        print(f"  [PASS] Locate: {loc}")
    
    def test_classify(self):
        """Should classify."""
        c = self.wd.classify_defect([0.0, 1.0, 0.0])
        self.assertIn(c, ["porosity", "crack", "lack_of_fusion", "none"])
        print(f"  [PASS] Class: {c}")


class TestShearWaveSystem(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sw = ShearWaveSystem(45.0, 5.0)
    
    def test_scan(self):
        """Should scan."""
        self.sw.scan(0.0, [5.0, 10.0], 10.0)
        self.assertEqual(len(self.sw.measurements), 2)
        print("  [PASS] Scan")
    
    def test_analyze(self):
        """Should analyze."""
        p = [[0.0, 1.0, 0.0], [0.0, 1.0, 1.0, 0.0]]
        c = self.sw.analyze_defects(p)
        self.assertEqual(len(c), 2)
        print(f"  [PASS] Analyze: {c}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.sw.shear_wave_summary()
        self.assertIn("angle_deg", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
