"""
Unit tests for resonant acoustic spectroscopy module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from resonant_acoustic_spectroscopy import (ResonancePeak, ResonanceScanner,
                                             QualityFactorEstimator,
                                             ModalDensityAnalyzer,
                                             DefectShiftDetector,
                                             ResonantAcousticSpectroscopy)


class TestResonanceScanner(unittest.TestCase):
    """Test scanner."""
    
    def setUp(self):
        self.rs = ResonanceScanner()
    
    def test_find_peaks(self):
        """Should find peaks."""
        freqs = [100.0, 200.0, 300.0, 400.0, 500.0]
        amps = [0.1, 0.5, 1.0, 0.5, 0.1]
        peaks = self.rs.find_peaks(freqs, amps, 0.3)
        self.assertGreater(len(peaks), 0)
        print(f"  [PASS] Peaks: {len(peaks)}")
    
    def test_bandwidth(self):
        """Should estimate bandwidth."""
        freqs = [100.0, 200.0, 300.0, 400.0, 500.0]
        amps = [0.1, 0.5, 1.0, 0.5, 0.1]
        peaks = self.rs.find_peaks(freqs, amps)
        if peaks:
            self.assertGreaterEqual(peaks[0].bandwidth_Hz, 0)
        print("  [PASS] BW")


class TestQualityFactorEstimator(unittest.TestCase):
    """Test Q factor."""
    
    def setUp(self):
        self.qe = QualityFactorEstimator()
    
    def test_q(self):
        """Should compute Q."""
        peak = ResonancePeak(1000.0, 1.0, 100.0)
        q = self.qe.q_factor(peak)
        self.assertEqual(q, 10.0)
        print(f"  [PASS] Q: {q}")
    
    def test_average(self):
        """Should compute average Q."""
        peaks = [ResonancePeak(1000.0, 1.0, 100.0),
                 ResonancePeak(2000.0, 1.0, 200.0)]
        avg = self.qe.average_q(peaks)
        self.assertEqual(avg, 10.0)
        print(f"  [PASS] AvgQ: {avg}")


class TestModalDensityAnalyzer(unittest.TestCase):
    """Test modal density."""
    
    def setUp(self):
        self.mda = ModalDensityAnalyzer()
    
    def test_density(self):
        """Should compute density."""
        d = self.mda.modal_density([100.0, 200.0, 300.0], 500.0)
        self.assertEqual(d, 0.006)
        print(f"  [PASS] Den: {d}")
    
    def test_uniformity(self):
        """Should compute uniformity."""
        u = self.mda.spacing_uniformity([100.0, 200.0, 300.0])
        self.assertEqual(u, 0.0)
        print(f"  [PASS] Uni: {u}")


class TestDefectShiftDetector(unittest.TestCase):
    """Test shift detector."""
    
    def setUp(self):
        self.dsd = DefectShiftDetector()
    
    def test_detect(self):
        """Should detect shifts."""
        self.dsd.set_baseline([100.0, 200.0, 300.0])
        shifts = self.dsd.detect_shifts([110.0, 200.0, 290.0], 5.0)
        self.assertGreater(len(shifts), 0)
        print(f"  [PASS] Shifts: {len(shifts)}")
    
    def test_correlation(self):
        """Should correlate."""
        c = self.dsd.correlation_with_defect_size([10.0, 5.0], 2.0)
        self.assertEqual(c, 7.5)
        print(f"  [PASS] Corr: {c}")


class TestResonantAcousticSpectroscopy(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ras = ResonantAcousticSpectroscopy()
    
    def test_analyze(self):
        """Should analyze."""
        freqs = [100.0, 200.0, 300.0, 400.0, 500.0]
        amps = [0.1, 0.5, 1.0, 0.5, 0.1]
        r = self.ras.analyze_spectrum(freqs, amps)
        self.assertIn("num_peaks", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_detect(self):
        """Should detect defects."""
        base = [100.0, 200.0, 300.0]
        meas = [115.0, 200.0, 285.0]
        d = self.ras.detect_defects(base, meas, 5.0)
        self.assertGreater(len(d), 0)
        print(f"  [PASS] Def: {len(d)}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ras.ras_summary()
        self.assertIn("peaks", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
