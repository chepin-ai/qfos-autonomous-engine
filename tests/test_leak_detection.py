"""
Unit tests for leak detection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from leak_detection import (LeakMethod, LeakRate,
                            PressureDecayTester,
                            HeliumMassSpectrometer,
                            BubbleTester,
                            AcousticLeakDetector,
                            LeakDetection)


class TestPressureDecayTester(unittest.TestCase):
    """Test pressure decay tester."""
    
    def setUp(self):
        self.pt = PressureDecayTester(0.001)
    
    def test_leak_rate(self):
        """Should compute leak rate."""
        q = self.pt.leak_rate(100000.0, 95000.0, 10.0)
        self.assertGreater(q, 0)
        print(f"  [PASS] Q: {q:.2f}")
    
    def test_decay_constant(self):
        """Should compute decay constant."""
        tau = self.pt.decay_constant(5.0, 100000.0)
        self.assertGreater(tau, 0)
        print(f"  [PASS] Tau: {tau:.1f}s")
    
    def test_time_to_threshold(self):
        """Should compute time."""
        t = self.pt.time_to_threshold(100000.0, 90000.0, 5.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] T: {t:.1f}s")


class TestHeliumMassSpectrometer(unittest.TestCase):
    """Test helium detector."""
    
    def setUp(self):
        self.hd = HeliumMassSpectrometer()
    
    def test_detect(self):
        """Should detect leak."""
        self.assertTrue(self.hd.detect_leak(10.0, 1.0))
        print("  [PASS] Detect")
    
    def test_no_detect(self):
        """Should not detect low signal."""
        self.assertFalse(self.hd.detect_leak(2.0, 1.0))
        print("  [PASS] NoDetect")
    
    def test_rate(self):
        """Should convert signal."""
        r = self.hd.leak_rate_from_signal(100.0, 1e-9)
        self.assertAlmostEqual(r, 1e-7, places=15)
        print(f"  [PASS] Rate: {r}")
    
    def test_sniff(self):
        """Should sniff test."""
        r = self.hd.sniff_test(100.0, 1e-4)
        self.assertGreater(r, 0)
        print(f"  [PASS] Sniff: {r:.2e}")


class TestBubbleTester(unittest.TestCase):
    """Test bubble tester."""
    
    def setUp(self):
        self.bt = BubbleTester()
    
    def test_bubble_rate(self):
        """Should compute from bubble."""
        q = self.bt.bubble_leak_rate(2.0, 1.0)
        self.assertGreater(q, 0)
        print(f"  [PASS] BubbleQ: {q:.2e}")
    
    def test_detected(self):
        """Should detect leak."""
        self.assertTrue(self.bt.leak_detected(10, 60.0))
        print("  [PASS] Detected")
    
    def test_frequency(self):
        """Should compute frequency."""
        f = self.bt.bubble_frequency(1e-5)
        self.assertGreater(f, 0)
        print(f"  [PASS] Freq: {f:.1f}")


class TestAcousticLeakDetector(unittest.TestCase):
    """Test acoustic detector."""
    
    def setUp(self):
        self.ad = AcousticLeakDetector()
    
    def test_turbulence(self):
        """Should detect turbulence."""
        self.assertTrue(self.ad.detect_turbulence(50.0, 50.0))
        print("  [PASS] Turb")
    
    def test_intensity(self):
        """Should compute intensity."""
        i = self.ad.leak_intensity(1.0)
        self.assertGreater(i, 0)
        print(f"  [PASS] Int: {i:.4f}")


class TestLeakDetection(unittest.TestCase):
    """Test unified leak detection."""
    
    def setUp(self):
        self.ld = LeakDetection()
    
    def test_pressure(self):
        """Should test pressure."""
        r = self.ld.test_pressure_decay(100000.0, 95000.0, 10.0)
        self.assertIn("leak_rate_Pa_m3_s", r)
        print(f"  [PASS] Press: {r['leak_rate_Pa_m3_s']:.2f}")
    
    def test_helium(self):
        """Should test helium."""
        r = self.ld.test_helium(10.0)
        self.assertTrue(r["detected"])
        print(f"  [PASS] He: detected={r['detected']}")
    
    def test_bubble(self):
        """Should test bubble."""
        r = self.ld.test_bubble(10, 60.0)
        self.assertTrue(r["detected"])
        print(f"  [PASS] Bubble: detected={r['detected']}")
    
    def test_summary(self):
        """Should summarize."""
        self.ld.test_pressure_decay(100000.0, 95000.0, 10.0)
        s = self.ld.leak_summary()
        self.assertIn("total_tests", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
