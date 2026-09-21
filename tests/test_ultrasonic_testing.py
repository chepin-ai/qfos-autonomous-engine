"""
Unit tests for ultrasonic testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ultrasonic_testing import (UTSignal, PulseEcho,
                                TOFDAnalyzer,
                                PhasedArray,
                                AttenuationAnalyzer,
                                UltrasonicTesting)


class TestPulseEcho(unittest.TestCase):
    """Test pulse-echo."""
    
    def setUp(self):
        self.pe = PulseEcho(5.9)
    
    def test_thickness(self):
        """Should compute thickness."""
        t = self.pe.thickness_from_tof(10.0)
        self.assertAlmostEqual(t, 29.5, delta=0.1)
        print(f"  [PASS] t: {t:.1f} mm")
    
    def test_tof(self):
        """Should compute TOF."""
        tof = self.pe.tof_from_thickness(29.5)
        self.assertAlmostEqual(tof, 10.0, delta=0.1)
        print(f"  [PASS] TOF: {tof:.1f} us")
    
    def test_flaw_depth(self):
        """Should compute depth."""
        d = self.pe.flaw_depth(6.0)
        self.assertAlmostEqual(d, 17.7, delta=0.1)
        print(f"  [PASS] Depth: {d:.1f} mm")
    
    def test_near_field(self):
        """Should compute near field."""
        nf = self.pe.near_field_distance(10.0, 1.0)
        self.assertAlmostEqual(nf, 25.0, delta=0.1)
        print(f"  [PASS] NF: {nf:.1f} mm")
    
    def test_wavelength(self):
        """Should compute wavelength."""
        wl = self.pe.wavelength(5.0)
        self.assertAlmostEqual(wl, 1.18, delta=0.01)
        print(f"  [PASS] WL: {wl:.2f} mm")


class TestTOFDAnalyzer(unittest.TestCase):
    """Test TOFD."""
    
    def setUp(self):
        self.tofd = TOFDAnalyzer(5.9, 50.0)
    
    def test_lateral(self):
        """Should compute lateral wave."""
        t = self.tofd.lateral_wave_tof()
        self.assertGreater(t, 0)
        print(f"  [PASS] LW: {t:.2f} us")
    
    def test_backwall(self):
        """Should compute backwall."""
        t = self.tofd.backwall_tof(20.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] BW: {t:.2f} us")
    
    def test_flaw_tof(self):
        """Should compute flaw TOF."""
        t = self.tofd.flaw_tof(10.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Fl: {t:.2f} us")
    
    def test_flaw_height(self):
        """Should compute height."""
        h = self.tofd.flaw_height(10.0, 12.0)
        self.assertAlmostEqual(h, 5.9, delta=0.1)
        print(f"  [PASS] FH: {h:.1f} mm")


class TestPhasedArray(unittest.TestCase):
    """Test phased array."""
    
    def setUp(self):
        self.pa = PhasedArray(16, 1.0, 5.9)
    
    def test_steering(self):
        """Should compute angle."""
        a = self.pa.steering_angle(0.1)
        self.assertTrue(-90 <= a <= 90)
        print(f"  [PASS] Ang: {a:.1f} deg")
    
    def test_aperture(self):
        """Should compute aperture."""
        a = self.pa.aperture_size()
        self.assertEqual(a, 16.0)
        print(f"  [PASS] Ap: {a:.1f} mm")
    
    def test_focal(self):
        """Should compute focal distance."""
        f = self.pa.focal_distance([0.0, 0.1, 0.2, 0.1, 0.0])
        self.assertGreater(f, 0)
        print(f"  [PASS] Foc: {f:.1f} mm")


class TestAttenuationAnalyzer(unittest.TestCase):
    """Test attenuation."""
    
    def setUp(self):
        self.aa = AttenuationAnalyzer()
    
    def test_coefficient(self):
        """Should compute coefficient."""
        c = self.aa.attenuation_coefficient(10.0, 5.0, 100.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] Att: {c:.4f} dB/mm")
    
    def test_corrected(self):
        """Should correct amplitude."""
        a = self.aa.corrected_amplitude(5.0, 0.01, 100.0)
        self.assertGreater(a, 5.0)
        print(f"  [PASS] Cor: {a:.2f}")


class TestUltrasonicTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ut = UltrasonicTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ut.ut_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
