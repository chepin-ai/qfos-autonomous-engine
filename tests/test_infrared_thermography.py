"""
Unit tests for infrared thermography module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrared_thermography import (ThermalMode, ThermalPixel,
                                    EmissivityCorrector,
                                    ThermalContrastAnalyzer,
                                    LockInThermography,
                                    InfraredThermography)


class TestEmissivityCorrector(unittest.TestCase):
    """Test emissivity corrector."""
    
    def setUp(self):
        self.ec = EmissivityCorrector()
    
    def test_correct(self):
        """Should correct temperature."""
        t = self.ec.correct_temperature(50.0, 0.9)
        self.assertGreater(t, 50.0)
        print(f"  [PASS] Correct: {t:.2f} C")
    
    def test_estimate(self):
        """Should estimate emissivity."""
        eps = self.ec.estimate_emissivity(100.0, 80.0, 25.0)
        self.assertGreater(eps, 0)
        print(f"  [PASS] Est eps: {eps:.4f}")


class TestThermalContrastAnalyzer(unittest.TestCase):
    """Test contrast analyzer."""
    
    def setUp(self):
        self.tc = ThermalContrastAnalyzer()
    
    def test_contrast(self):
        """Should compute contrast."""
        c = self.tc.contrast(30.0, 25.0)
        self.assertEqual(c, 5.0)
        print(f"  [PASS] Contrast: {c}")
    
    def test_ratio(self):
        """Should compute ratio."""
        r = self.tc.contrast_ratio(30.0, 25.0)
        self.assertEqual(r, 0.2)
        print(f"  [PASS] Ratio: {r}")
    
    def test_defect_map(self):
        """Should detect defects."""
        img = [[25.0, 25.0, 25.0], [25.0, 35.0, 25.0], [25.0, 25.0, 25.0]]
        dm = self.tc.defect_map(img, 5.0)
        self.assertTrue(any(any(row) for row in dm))
        print("  [PASS] DefectMap")


class TestLockInThermography(unittest.TestCase):
    """Test lock-in thermography."""
    
    def setUp(self):
        self.li = LockInThermography(0.1)
    
    def test_demodulate(self):
        """Should demodulate."""
        signal = [(t * 0.1, math.sin(2.0 * math.pi * 0.1 * t * 0.1))
                  for t in range(100)]
        x, y = self.li.demodulate(signal)
        self.assertGreater(abs(x), 0)
        print(f"  [PASS] Demod: X={x:.4f} Y={y:.4f}")
    
    def test_amplitude(self):
        """Should compute amplitude."""
        a = self.li.amplitude(1.0, 1.0)
        self.assertAlmostEqual(a, math.sqrt(2), places=5)
        print(f"  [PASS] Amp: {a:.4f}")
    
    def test_phase(self):
        """Should compute phase."""
        p = self.li.phase(1.0, 1.0)
        self.assertAlmostEqual(p, math.pi / 4, places=5)
        print(f"  [PASS] Phase: {p:.4f}")
    
    def test_diffusion(self):
        """Should compute diffusion length."""
        d = self.li.thermal_diffusion_length_mm(10.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Diff: {d:.4f} mm")


class TestInfraredThermography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.irt = InfraredThermography()
    
    def test_capture(self):
        """Should capture."""
        img = [[25.0] * 5 for _ in range(5)]
        self.irt.capture(img)
        self.assertEqual(len(self.irt.thermal_images), 1)
        print("  [PASS] Capture")
    
    def test_detect(self):
        """Should detect."""
        img = [[25.0] * 5 for _ in range(5)]
        img[2][2] = 35.0
        self.irt.capture(img)
        d = self.irt.detect_defects(5.0)
        self.assertGreater(len(d), 0)
        print(f"  [PASS] Detect: {len(d)} defects")
    
    def test_summary(self):
        """Should summarize."""
        self.irt.capture([[25.0] * 3 for _ in range(3)])
        s = self.irt.thermography_summary()
        self.assertIn("images", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
