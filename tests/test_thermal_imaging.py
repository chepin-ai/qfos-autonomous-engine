"""
Unit tests for thermal imaging module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermal_imaging import (TemperatureUnit, ThermalPixel,
                             TemperatureConverter, HotspotDetector,
                             ThermalGradient, EmissivityCorrector,
                             ThermalImaging)


class TestTemperatureConverter(unittest.TestCase):
    """Test temperature converter."""
    
    def test_c_to_k(self):
        """Should convert C to K."""
        self.assertAlmostEqual(TemperatureConverter.celsius_to_kelvin(0), 273.15)
        print("  [PASS] C->K")
    
    def test_c_to_f(self):
        """Should convert C to F."""
        self.assertAlmostEqual(TemperatureConverter.celsius_to_fahrenheit(100), 212.0)
        print("  [PASS] C->F")
    
    def test_roundtrip(self):
        """Should roundtrip F->C."""
        c = 37.0
        f = TemperatureConverter.celsius_to_fahrenheit(c)
        c2 = TemperatureConverter.fahrenheit_to_celsius(f)
        self.assertAlmostEqual(c, c2)
        print("  [PASS] Round")


class TestHotspotDetector(unittest.TestCase):
    """Test hotspot detector."""
    
    def setUp(self):
        self.hd = HotspotDetector(threshold_delta_K=5.0)
    
    def test_detect(self):
        """Should detect hotspots."""
        pixels = [
            ThermalPixel(0, 0, 20.0),
            ThermalPixel(1, 0, 22.0),
            ThermalPixel(0, 1, 35.0)
        ]
        hs = self.hd.detect(pixels)
        self.assertGreater(len(hs), 0)
        print(f"  [PASS] Hotspots: {len(hs)}")
    
    def test_max_temp(self):
        """Should find max."""
        pixels = [ThermalPixel(0, 0, 20.0), ThermalPixel(1, 0, 50.0)]
        self.assertAlmostEqual(self.hd.max_temperature(pixels), 50.0)
        print("  [PASS] Max")
    
    def test_uniformity(self):
        """Should compute uniformity."""
        pixels = [ThermalPixel(i, 0, 20.0) for i in range(10)]
        u = self.hd.thermal_uniformity(pixels)
        self.assertGreater(u, 0.9)
        print(f"  [PASS] Uni: {u:.3f}")


class TestThermalGradient(unittest.TestCase):
    """Test thermal gradient."""
    
    def setUp(self):
        self.tg = ThermalGradient()
    
    def test_gradient_x(self):
        """Should compute horizontal gradient."""
        pixels = [ThermalPixel(i, 0, float(i)) for i in range(4)]
        gx = self.tg.gradient_x(pixels, 2)
        self.assertGreater(len(gx), 0)
        print(f"  [PASS] GradX")
    
    def test_max_gradient(self):
        """Should find max gradient."""
        pixels = [ThermalPixel(i, 0, float(i * i)) for i in range(4)]
        mg = self.tg.max_gradient(pixels, 2)
        self.assertGreater(mg, 0)
        print(f"  [PASS] MaxGrad: {mg:.2f}")


class TestEmissivityCorrector(unittest.TestCase):
    """Test emissivity corrector."""
    
    def setUp(self):
        self.ec = EmissivityCorrector()
    
    def test_correct(self):
        """Should correct temperature."""
        t = self.ec.correct_temperature(100.0, 0.9)
        self.assertNotEqual(t, 100.0)
        print(f"  [PASS] Correct: {t:.1f}")
    
    def test_low_emissivity(self):
        """Should handle low emissivity."""
        t = self.ec.correct_temperature(100.0, 0.1)
        self.assertGreater(t, 100.0)
        print(f"  [PASS] LowE: {t:.1f}")


class TestThermalImaging(unittest.TestCase):
    """Test unified thermal imaging."""
    
    def setUp(self):
        self.ti = ThermalImaging()
    
    def test_report(self):
        """Should generate report."""
        pixels = [ThermalPixel(i, 0, 20.0 + i) for i in range(10)]
        self.ti.load_pixels(pixels)
        r = self.ti.thermal_report()
        self.assertIn("max_temp_C", r)
        print(f"  [PASS] Report: max={r['max_temp_C']:.1f}")
    
    def test_pass_fail(self):
        """Should pass/fail."""
        pixels = [ThermalPixel(0, 0, 50.0)]
        self.ti.load_pixels(pixels)
        self.assertTrue(self.ti.pass_fail(80.0))
        self.assertFalse(self.ti.pass_fail(30.0))
        print("  [PASS] PassFail")


if __name__ == '__main__':
    unittest.main(verbosity=2)
