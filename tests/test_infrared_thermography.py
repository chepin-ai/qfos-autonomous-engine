"""
Unit tests for infrared thermography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrared_thermography import (ThermalPixel, EmissivityCorrector,
                                    HotspotDetector,
                                    TemperatureTrendAnalyzer,
                                    InfraredThermography)


class TestEmissivityCorrector(unittest.TestCase):
    """Test corrector."""
    
    def setUp(self):
        self.ec = EmissivityCorrector(25.0)
    
    def test_correct(self):
        """Should correct temp."""
        t = self.ec.correct(100.0, 0.9)
        self.assertGreater(t, 100.0)
        print(f"  [PASS] Corr: {t:.2f}C")
    
    def test_perfect_emissivity(self):
        """Should not change at eps=1."""
        t = self.ec.correct(50.0, 1.0)
        self.assertAlmostEqual(t, 50.0, places=0)
        print(f"  [PASS] Eps1: {t:.2f}C")
    
    def test_image(self):
        """Should correct image."""
        pixels = [ThermalPixel(0, 0, 100.0, 0.9),
                  ThermalPixel(1, 0, 50.0, 0.8)]
        c = self.ec.correct_image(pixels)
        self.assertEqual(len(c), 2)
        print("  [PASS] Img")


class TestHotspotDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.hd = HotspotDetector(5.0)
    
    def test_detect(self):
        """Should detect hotspots."""
        temps = [25.0] * 8 + [50.0, 50.0]
        h = self.hd.detect(temps, 5, 2)
        self.assertGreater(len(h), 0)
        print(f"  [PASS] HS: {len(h)}")
    
    def test_no_hotspot(self):
        """Should not detect if uniform."""
        temps = [25.0] * 10
        h = self.hd.detect(temps, 5, 2)
        self.assertEqual(len(h), 0)
        print("  [PASS] NoHS")


class TestTemperatureTrendAnalyzer(unittest.TestCase):
    """Test trend."""
    
    def setUp(self):
        self.tta = TemperatureTrendAnalyzer()
    
    def test_add(self):
        """Should add measurement."""
        self.tta.add_measurement(0.0, [25.0, 26.0, 27.0])
        self.assertEqual(len(self.tta.history), 1)
        print("  [PASS] Add")
    
    def test_slope(self):
        """Should compute slope."""
        self.tta.add_measurement(0.0, [25.0])
        self.tta.add_measurement(1.0, [30.0])
        s = self.tta.trend_slope()
        self.assertAlmostEqual(s, 5.0, places=5)
        print(f"  [PASS] Slope: {s:.2f}")
    
    def test_overheat(self):
        """Should detect overheating."""
        self.tta.add_measurement(0.0, [25.0])
        self.tta.add_measurement(1.0, [30.0])
        self.assertTrue(self.tta.is_overheating(0.5))
        print("  [PASS] Overheat")


class TestInfraredThermography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ir = InfraredThermography()
    
    def test_capture(self):
        """Should capture."""
        temps = [25.0, 30.0, 35.0, 40.0]
        emiss = [0.9, 0.9, 0.9, 0.9]
        self.ir.capture(temps, emiss, 2, 2)
        self.assertEqual(len(self.ir.pixels), 4)
        print("  [PASS] Cap")
    
    def test_inspect(self):
        """Should inspect."""
        temps = [25.0] * 8 + [60.0, 60.0]
        emiss = [0.95] * 10
        self.ir.capture(temps, emiss, 5, 2)
        r = self.ir.inspect()
        self.assertIn("hotspots", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_trend(self):
        """Should track trend."""
        temps = [25.0, 30.0]
        emiss = [0.9, 0.9]
        self.ir.capture(temps, emiss, 2, 1)
        self.ir.add_timepoint(0.0)
        self.ir.add_timepoint(1.0)
        s = self.ir.ir_summary()
        self.assertIn("trend_slope", s)
        print(f"  [PASS] Trend: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
