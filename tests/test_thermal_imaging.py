"""
Unit tests for thermal imaging module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermal_imaging import (ThermalPixel, InfraredCamera,
                             HotSpotDetector,
                             TemperatureGradientMapper,
                             EmissivityCorrector,
                             ThermalPatternAnalyzer,
                             ThermalImaging)


class TestInfraredCamera(unittest.TestCase):
    """Test camera."""
    
    def setUp(self):
        self.cam = InfraredCamera((64, 48), (7.5, 14.0), 50.0)
    
    def test_capture(self):
        """Should capture."""
        img = self.cam.capture(20.0, [(32, 24, 50.0)])
        self.assertEqual(len(img), 48)
        self.assertEqual(len(img[0]), 64)
        print("  [PASS] Cap")
    
    def test_min_max(self):
        """Should find min/max."""
        img = self.cam.capture(20.0)
        mn, mx = self.cam.min_max_temp(img)
        self.assertLess(mn, mx)
        print(f"  [PASS] MM: {mn:.2f} - {mx:.2f}")


class TestHotSpotDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.hd = HotSpotDetector(5.0)
    
    def test_detect(self):
        """Should detect."""
        img = [[20.0] * 10 for _ in range(10)]
        img[5][5] = 30.0
        spots = self.hd.detect(img, 20.0)
        self.assertGreater(len(spots), 0)
        print(f"  [PASS] HS: {len(spots)} spots")


class TestTemperatureGradientMapper(unittest.TestCase):
    """Test gradient."""
    
    def setUp(self):
        self.tgm = TemperatureGradientMapper()
    
    def test_magnitude(self):
        """Should compute gradient."""
        img = [[20.0, 22.0], [20.0, 22.0]]
        g = self.tgm.gradient_magnitude(img)
        self.assertEqual(len(g), 2)
        print("  [PASS] Grad")
    
    def test_max(self):
        """Should find max gradient."""
        img = [[20.0, 25.0], [20.0, 25.0]]
        m = self.tgm.max_gradient(img)
        self.assertGreater(m, 0)
        print(f"  [PASS] MaxG: {m:.4f}")


class TestEmissivityCorrector(unittest.TestCase):
    """Test emissivity."""
    
    def setUp(self):
        self.ec = EmissivityCorrector()
    
    def test_correct(self):
        """Should correct."""
        t = self.ec.correct_temperature(25.0, 0.95, 20.0)
        self.assertGreater(t, 25.0)
        print(f"  [PASS] Corr: {t:.2f} C")
    
    def test_estimate(self):
        """Should estimate."""
        e = self.ec.estimate_emissivity(100.0, 95.0, 20.0)
        self.assertGreaterEqual(e, 0.0)
        self.assertLessEqual(e, 1.0)
        print(f"  [PASS] Est: {e:.4f}")


class TestThermalPatternAnalyzer(unittest.TestCase):
    """Test pattern."""
    
    def setUp(self):
        self.tpa = ThermalPatternAnalyzer()
    
    def test_uniformity(self):
        """Should compute uniformity."""
        img = [[20.0, 20.1], [20.0, 20.1]]
        u = self.tpa.thermal_uniformity(img)
        self.assertGreaterEqual(u, 0)
        print(f"  [PASS] Uni: {u:.6f}")
    
    def test_histogram(self):
        """Should compute histogram."""
        img = [[20.0, 25.0], [22.0, 28.0]]
        h = self.tpa.thermal_histogram(img, 4)
        self.assertIn("counts", h)
        print(f"  [PASS] Hist: {h['counts']}")


class TestThermalImaging(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ti = ThermalImaging()
    
    def test_inspect(self):
        """Should inspect."""
        self.ti.inspect(20.0, [(160, 120, 60.0)])
        self.assertTrue(len(self.ti.image) > 0)
        print("  [PASS] Insp")
    
    def test_analyze(self):
        """Should analyze."""
        self.ti.inspect(20.0, [(160, 120, 60.0)])
        r = self.ti.analyze()
        self.assertIn("hot_spots", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ti.ti_summary()
        self.assertIn("resolution", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
