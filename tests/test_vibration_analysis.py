"""
Unit tests for vibration analysis module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vibration_analysis import (VibrationSample, TimeDomainAnalyzer,
                                FrequencyDomainAnalyzer,
                                ModalAnalyzer,
                                ShockResponseAnalyzer,
                                VibrationSeverity,
                                VibrationAnalysis)


class TestTimeDomainAnalyzer(unittest.TestCase):
    """Test time domain."""
    
    def setUp(self):
        self.tda = TimeDomainAnalyzer()
        self.samples = [1.0, -1.0, 1.0, -1.0]
    
    def test_rms(self):
        """Should compute RMS."""
        r = self.tda.rms(self.samples)
        self.assertEqual(r, 1.0)
        print(f"  [PASS] RMS: {r}")
    
    def test_peak(self):
        """Should compute peak."""
        p = self.tda.peak(self.samples)
        self.assertEqual(p, 1.0)
        print(f"  [PASS] Peak: {p}")
    
    def test_crest(self):
        """Should compute crest factor."""
        c = self.tda.crest_factor(self.samples)
        self.assertEqual(c, 1.0)
        print(f"  [PASS] Crest: {c}")
    
    def test_kurtosis(self):
        """Should compute kurtosis."""
        k = self.tda.kurtosis([0.0, 1.0, -1.0, 2.0, -2.0])
        self.assertGreater(k, 0)
        print(f"  [PASS] Kurt: {k:.4f}")


class TestFrequencyDomainAnalyzer(unittest.TestCase):
    """Test frequency domain."""
    
    def setUp(self):
        self.fda = FrequencyDomainAnalyzer(1000.0)
    
    def test_dft(self):
        """Should compute DFT."""
        s = [1.0, 0.0, -1.0, 0.0]
        d = self.fda.dft(s)
        self.assertEqual(len(d), 4)
        print("  [PASS] DFT")
    
    def test_spectrum(self):
        """Should compute spectrum."""
        s = [1.0, 0.0, -1.0, 0.0]
        m = self.fda.magnitude_spectrum(s)
        self.assertGreater(len(m), 0)
        print(f"  [PASS] Spec: {len(m)} bins")
    
    def test_dominant(self):
        """Should find dominant freq."""
        t = [i / 1000.0 for i in range(100)]
        s = [math.sin(2 * math.pi * 50.0 * ti) for ti in t]
        f = self.fda.dominant_frequency(s)
        self.assertGreater(f, 0)
        print(f"  [PASS] DomF: {f:.1f} Hz")


class TestModalAnalyzer(unittest.TestCase):
    """Test modal."""
    
    def setUp(self):
        self.ma = ModalAnalyzer()
    
    def test_natural(self):
        """Should compute natural freq."""
        f = self.ma.natural_frequency(10000.0, 1.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] Nat: {f:.2f} Hz")
    
    def test_damping(self):
        """Should compute damping."""
        d = self.ma.damping_ratio(100.0, 99.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Damp: {d:.4f}")
    
    def test_add_mode(self):
        """Should add mode."""
        self.ma.add_mode(100.0, 0.01, [1.0, 0.5])
        self.assertEqual(len(self.ma.modes), 1)
        print("  [PASS] Mode")


class TestShockResponseAnalyzer(unittest.TestCase):
    """Test shock."""
    
    def setUp(self):
        self.sra = ShockResponseAnalyzer()
    
    def test_srs(self):
        """Should compute SRS."""
        pulse = [0.0, 100.0, 0.0]
        freqs = [10.0, 100.0]
        srs = self.sra.shock_spectrum(pulse, freqs, 1000.0)
        self.assertEqual(len(srs), 2)
        print(f"  [PASS] SRS: {srs}")


class TestVibrationSeverity(unittest.TestCase):
    """Test severity."""
    
    def setUp(self):
        self.vs = VibrationSeverity()
    
    def test_assess(self):
        """Should assess."""
        a = self.vs.assess_iso(0.5)
        self.assertEqual(a, "satisfactory")
        print(f"  [PASS] Sev: {a}")
    
    def test_velocity(self):
        """Should convert."""
        v = self.vs.velocity_from_acceleration(9.8, 60.0)
        self.assertGreater(v, 0)
        print(f"  [PASS] Vel: {v:.2f} mm/s")


class TestVibrationAnalysis(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.va = VibrationAnalysis(1000.0)
    
    def test_record(self):
        """Should record."""
        self.va.record([1.0, -1.0, 1.0, -1.0])
        self.assertEqual(len(self.va.samples), 4)
        print("  [PASS] Rec")
    
    def test_analyze(self):
        """Should analyze."""
        t = [i / 1000.0 for i in range(100)]
        s = [math.sin(2 * math.pi * 60.0 * ti) for ti in t]
        self.va.record(s)
        r = self.va.analyze()
        self.assertIn("severity", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.va.va_summary()
        self.assertIn("fs_Hz", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
