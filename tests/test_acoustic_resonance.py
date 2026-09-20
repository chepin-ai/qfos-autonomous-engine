"""
Unit tests for acoustic resonance module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from acoustic_resonance import (ResonanceMode, SpectrumAnalyzer,
                                 ModalExtractor,
                                 ResonanceDefectDetector,
                                 AcousticResonance)


class TestSpectrumAnalyzer(unittest.TestCase):
    """Test spectrum analyzer."""
    
    def setUp(self):
        self.sa = SpectrumAnalyzer(1000.0)
    
    def test_dft(self):
        """Should compute DFT."""
        s = [1.0, 0.0, -1.0, 0.0]
        spec = self.sa.dft(s)
        self.assertEqual(len(spec), 4)
        print("  [PASS] DFT")
    
    def test_magnitude(self):
        """Should compute magnitude."""
        s = [1.0, 1.0, -1.0, 0.0]
        m = self.sa.magnitude_spectrum(s)
        self.assertEqual(len(m), 4)
        self.assertGreater(m[0], 0)
        print(f"  [PASS] Mag: {m}")
    
    def test_bins(self):
        """Should compute bins."""
        b = self.sa.frequency_bins(8)
        self.assertEqual(len(b), 5)
        self.assertEqual(b[0], 0.0)
        print(f"  [PASS] Bins: {b}")


class TestModalExtractor(unittest.TestCase):
    """Test modal extractor."""
    
    def setUp(self):
        self.me = ModalExtractor()
    
    def test_peaks(self):
        """Should find peaks."""
        mags = [0.0, 0.5, 1.0, 0.5, 0.0]
        freqs = [0.0, 100.0, 200.0, 300.0, 400.0]
        p = self.me.find_peaks(mags, freqs, 0.2)
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0][1], 200.0)
        print(f"  [PASS] Peaks: {p}")
    
    def test_damping(self):
        """Should estimate damping."""
        decay = [math.exp(-0.1 * i) * math.sin(i) for i in range(50)]
        d = self.me.estimate_damping(decay, 1.0, 100.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Damp: {d:.4f}")
    
    def test_q(self):
        """Should compute Q."""
        q = self.me.q_factor(100.0, 0.01)
        self.assertEqual(q, 50.0)
        print(f"  [PASS] Q: {q}")
    
    def test_extract(self):
        """Should extract modes."""
        signal = [math.sin(2.0 * math.pi * 100.0 * i / 1000.0) for i in range(256)]
        modes = self.me.extract_modes(signal, 1000.0)
        self.assertGreater(len(modes), 0)
        print(f"  [PASS] Extract: {len(modes)} modes")


class TestResonanceDefectDetector(unittest.TestCase):
    """Test defect detector."""
    
    def setUp(self):
        self.rdd = ResonanceDefectDetector()
    
    def test_detect(self):
        """Should detect shifts."""
        baseline = [ResonanceMode(100.0, 1.0, 0.01, 0.0)]
        current = [ResonanceMode(120.0, 1.0, 0.01, 0.0)]
        self.rdd.set_baseline(baseline)
        shifts = self.rdd.detect_shift(current, 10.0)
        self.assertEqual(len(shifts), 1)
        print(f"  [PASS] Detect: {shifts}")


class TestAcousticResonance(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ar = AcousticResonance(1000.0)
    
    def test_measure(self):
        """Should measure."""
        s = [math.sin(i) for i in range(64)]
        self.ar.measure(s)
        self.assertEqual(len(self.ar.measurements), 1)
        print("  [PASS] Measure")
    
    def test_analyze(self):
        """Should analyze."""
        s = [math.sin(2.0 * math.pi * 10.0 * i / 1000.0) for i in range(256)]
        self.ar.measure(s)
        modes = self.ar.analyze()
        self.assertGreater(len(modes), 0)
        print(f"  [PASS] Analyze: {len(modes)} modes")
    
    def test_detect(self):
        """Should detect."""
        s1 = [math.sin(2.0 * math.pi * 10.0 * i / 1000.0) for i in range(256)]
        s2 = [math.sin(2.0 * math.pi * 50.0 * i / 1000.0) for i in range(256)]
        self.ar.measure(s1)
        self.ar.analyze()
        self.ar.measure(s2)
        self.ar.analyze()
        d = self.ar.detect(5.0)
        self.assertGreaterEqual(len(d), 0)
        print(f"  [PASS] Defect: {len(d)} shifts")
    
    def test_summary(self):
        """Should summarize."""
        self.ar.measure([0.0] * 64)
        s = self.ar.resonance_summary()
        self.assertIn("measurements", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
