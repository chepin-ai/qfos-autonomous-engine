"""
Unit tests for vibration analysis module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vibration_analysis import (BearingFaultType, VibrationAnalyzer,
                                BearingDiagnoser, EnvelopeAnalyzer,
                                VibrationAnalysis)


class TestVibrationAnalyzer(unittest.TestCase):
    """Test vibration analyzer."""
    
    def setUp(self):
        self.va = VibrationAnalyzer(1000.0)
        self.signal = [math.sin(2.0 * math.pi * 10.0 * i / 1000.0) for i in range(1000)]
    
    def test_rms(self):
        """Should compute RMS."""
        rms = self.va.rms(self.signal)
        self.assertGreater(rms, 0)
        print(f"  [PASS] RMS: {rms:.4f}")
    
    def test_peak(self):
        """Should compute peak."""
        p = self.va.peak(self.signal)
        self.assertGreater(p, 0)
        print(f"  [PASS] Peak: {p:.4f}")
    
    def test_peak_to_peak(self):
        """Should compute P-P."""
        pp = self.va.peak_to_peak(self.signal)
        self.assertGreater(pp, 0)
        print(f"  [PASS] P-P: {pp:.4f}")
    
    def test_crest(self):
        """Should compute crest factor."""
        cf = self.va.crest_factor(self.signal)
        self.assertGreater(cf, 0)
        print(f"  [PASS] Crest: {cf:.4f}")
    
    def test_kurtosis(self):
        """Should compute kurtosis."""
        k = self.va.kurtosis(self.signal)
        print(f"  [PASS] Kurt: {k:.4f}")
    
    def test_dft(self):
        """Should compute DFT."""
        spec = self.va.dft([1.0, 0.0, -1.0, 0.0])
        self.assertEqual(len(spec), 4)
        print(f"  [PASS] DFT: {len(spec)}")
    
    def test_spectrum(self):
        """Should compute magnitude spectrum."""
        mag = self.va.magnitude_spectrum(self.signal[:256])
        self.assertGreater(len(mag), 0)
        print(f"  [PASS] Spec: len={len(mag)}")
    
    def test_dominant(self):
        """Should find dominant frequency."""
        freq, mag = self.va.dominant_frequency(self.signal[:256])
        self.assertGreater(freq, 0)
        print(f"  [PASS] Dom: {freq:.1f}Hz")


class TestBearingDiagnoser(unittest.TestCase):
    """Test bearing diagnoser."""
    
    def setUp(self):
        self.bd = BearingDiagnoser(1800.0, 8, 10.0, 50.0, 0.0)
    
    def test_bpf_outer(self):
        """Should compute BPFO."""
        f = self.bd.bpf_outer()
        self.assertGreater(f, 0)
        print(f"  [PASS] BPFO: {f:.1f}Hz")
    
    def test_bpf_inner(self):
        """Should compute BPFI."""
        f = self.bd.bpf_inner()
        self.assertGreater(f, 0)
        print(f"  [PASS] BPFI: {f:.1f}Hz")
    
    def test_bsf(self):
        """Should compute BSF."""
        f = self.bd.bsf()
        self.assertGreater(f, 0)
        print(f"  [PASS] BSF: {f:.1f}Hz")
    
    def test_ftf(self):
        """Should compute FTF."""
        f = self.bd.ftf()
        self.assertGreater(f, 0)
        print(f"  [PASS] FTF: {f:.1f}Hz")
    
    def test_detect(self):
        """Should detect faults."""
        spectrum = [0.1] * 100
        faults = self.bd.detect_fault(spectrum, 1.0)
        self.assertIn("outer_race", faults)
        print(f"  [PASS] Faults: {faults}")


class TestEnvelopeAnalyzer(unittest.TestCase):
    """Test envelope analyzer."""
    
    def setUp(self):
        self.ea = EnvelopeAnalyzer(1000.0)
        self.signal = [math.sin(2.0 * math.pi * 10.0 * i / 1000.0) for i in range(256)]
    
    def test_envelope(self):
        """Should compute envelope."""
        env = self.ea.hilbert_envelope(self.signal)
        self.assertEqual(len(env), len(self.signal))
        print(f"  [PASS] Env: len={len(env)}")
    
    def test_envelope_spectrum(self):
        """Should compute envelope spectrum."""
        es = self.ea.envelope_spectrum(self.signal)
        self.assertGreater(len(es), 0)
        print(f"  [PASS] ES: len={len(es)}")


class TestVibrationAnalysis(unittest.TestCase):
    """Test unified vibration analysis."""
    
    def setUp(self):
        self.va = VibrationAnalysis(1000.0)
        self.signal = [math.sin(2.0 * math.pi * 10.0 * i / 1000.0) for i in range(256)]
    
    def test_analyze(self):
        """Should analyze."""
        r = self.va.analyze(self.signal)
        self.assertIn("rms", r)
        print(f"  [PASS] Anal: RMS={r['rms']:.4f}")
    
    def test_trend(self):
        """Should extract trend."""
        self.va.analyze(self.signal)
        self.va.analyze([x * 1.5 for x in self.signal])
        t = self.va.trend_analysis("rms")
        self.assertEqual(len(t), 2)
        print(f"  [PASS] Trend: {t}")
    
    def test_summary(self):
        """Should summarize."""
        self.va.analyze(self.signal)
        s = self.va.analysis_summary()
        self.assertIn("analyses", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
