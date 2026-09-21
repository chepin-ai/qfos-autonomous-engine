"""
Unit tests for acoustic emission module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from acoustic_emission import (AEHit, HitDetector,
                               SourceLocator,
                               KaiserEffect,
                               AmplitudeAnalyzer,
                               AcousticEmission)


class TestHitDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.hd = HitDetector(40.0, 50.0)
    
    def test_detect(self):
        """Should detect hits."""
        t = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
        a = [30.0, 35.0, 50.0, 55.0, 35.0, 30.0]
        hits = self.hd.detect_hits(t, a)
        self.assertGreater(len(hits), 0)
        print(f"  [PASS] Hits: {len(hits)}")
    
    def test_count_rate(self):
        """Should compute rate."""
        hits = [AEHit(0.0, 60.0, 100.0, 10.0, 1.0, 5)]
        r = self.hd.count_rate(hits, 1.0)
        self.assertEqual(r, 1.0)
        print(f"  [PASS] Rate: {r:.1f} hits/s")


class TestSourceLocator(unittest.TestCase):
    """Test locator."""
    
    def setUp(self):
        self.sl = SourceLocator(5000.0)
    
    def test_locate(self):
        """Should locate source."""
        sensors = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        times = [0.0, 200.0, 223.6]
        src = self.sl.time_difference_location(sensors, times)
        self.assertIsNotNone(src)
        print(f"  [PASS] Src: ({src[0]:.2f}, {src[1]:.2f})")
    
    def test_hyperbola(self):
        """Should compute hyperbola."""
        pts = self.sl.delta_t_source((0.0, 0.0), (1.0, 0.0), 100.0)
        self.assertGreater(len(pts), 0)
        print(f"  [PASS] Hyp: {len(pts)} pts")


class TestKaiserEffect(unittest.TestCase):
    """Test Kaiser."""
    
    def setUp(self):
        self.ke = KaiserEffect()
    
    def test_felicity(self):
        """Should compute ratio."""
        fr = self.ke.felicity_ratio(100.0, 90.0)
        self.assertAlmostEqual(fr, 0.9, delta=0.01)
        print(f"  [PASS] FR: {fr:.2f}")
    
    def test_violation(self):
        """Should detect violation."""
        self.assertTrue(self.ke.is_kaiser_violation(0.9))
        self.assertFalse(self.ke.is_kaiser_violation(0.97))
        print("  [PASS] Viol")


class TestAmplitudeAnalyzer(unittest.TestCase):
    """Test amplitude."""
    
    def setUp(self):
        self.aa = AmplitudeAnalyzer()
    
    def test_b_value(self):
        """Should compute b-value."""
        amps = [40.0, 45.0, 50.0, 55.0, 60.0]
        b = self.aa.b_value(amps)
        self.assertIsInstance(b, float)
        print(f"  [PASS] b: {b:.2f}")
    
    def test_asl(self):
        """Should compute ASL."""
        asl = self.aa.average_signal_level([40.0, 50.0, 60.0])
        self.assertEqual(asl, 50.0)
        print(f"  [PASS] ASL: {asl:.1f} dB")


class TestAcousticEmission(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ae = AcousticEmission()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ae.ae_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
