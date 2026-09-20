"""
Unit tests for digital radiography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from digital_radiography import (DRImage, FlatFieldCorrector,
                                  BadPixelDetector, DQEAnalyzer,
                                  ExposureIndexCalculator,
                                  DigitalRadiography)


class TestFlatFieldCorrector(unittest.TestCase):
    """Test flat field correction."""
    
    def setUp(self):
        self.ffc = FlatFieldCorrector()
    
    def test_correct(self):
        """Should correct."""
        self.ffc.set_flat_field([[2.0]*3 for _ in range(3)])
        self.ffc.set_dark_field([[0.5]*3 for _ in range(3)])
        img = [[1.5]*3 for _ in range(3)]
        c = self.ffc.correct(img)
        self.assertEqual(len(c), 3)
        self.assertAlmostEqual(c[0][0], 0.6667, places=3)
        print("  [PASS] Correct")


class TestBadPixelDetector(unittest.TestCase):
    """Test bad pixel detector."""
    
    def setUp(self):
        self.bpd = BadPixelDetector()
    
    def test_find(self):
        """Should find bad pixels."""
        self.bpd.threshold_sigma = 2.0
        img = [[1.0]*5 for _ in range(5)]
        img[2][2] = 100.0
        bad = self.bpd.find_bad_pixels(img)
        self.assertGreater(len(bad), 0)
        print(f"  [PASS] Find: {len(bad)} bad")
    
    def test_interpolate(self):
        """Should interpolate."""
        img = [[1.0]*3 for _ in range(3)]
        img[1][1] = 100.0
        c = self.bpd.interpolate_bad_pixels(img, [(1, 1)])
        self.assertLess(c[1][1], 100.0)
        print("  [PASS] Interp")


class TestDQEAnalyzer(unittest.TestCase):
    """Test DQE analyzer."""
    
    def setUp(self):
        self.dqe = DQEAnalyzer()
    
    def test_snr(self):
        """Should compute SNR."""
        s = self.dqe.snr([2.0]*10, [1.0]*10)
        self.assertGreater(s, 0)
        print(f"  [PASS] SNR: {s:.4f}")
    
    def test_dqe(self):
        """Should compute DQE."""
        d = self.dqe.dqe(10.0, 20.0)
        self.assertEqual(d, 0.25)
        print(f"  [PASS] DQE: {d}")
    
    def test_estimate(self):
        """Should estimate from ROIs."""
        img = [[1.0]*5 for _ in range(5)]
        for y in range(2, 4):
            for x in range(2, 4):
                img[y][x] = 2.0
        r = self.dqe.estimate_from_rois(img, (2, 2, 2, 2), (0, 0, 2, 2))
        self.assertIn("dqe", r)
        print(f"  [PASS] Est: {r}")


class TestExposureIndexCalculator(unittest.TestCase):
    """Test EI."""
    
    def setUp(self):
        self.ei = ExposureIndexCalculator()
    
    def test_ei(self):
        """Should compute EI."""
        v = self.ei.ei(100.0, 5.0)
        self.assertEqual(v, 2000.0)
        print(f"  [PASS] EI: {v}")
    
    def test_dev(self):
        """Should compute deviation."""
        d = self.ei.deviation(2000.0)
        self.assertEqual(d, 1900.0)
        print(f"  [PASS] Dev: {d}")


class TestDigitalRadiography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.dr = DigitalRadiography()
    
    def test_acquire(self):
        """Should acquire."""
        self.dr.acquire([[1.0]*5 for _ in range(5)])
        self.assertEqual(len(self.dr.images), 1)
        print("  [PASS] Acquire")
    
    def test_process(self):
        """Should process."""
        self.dr.flat_field.set_flat_field([[2.0]*5 for _ in range(5)])
        self.dr.flat_field.set_dark_field([[0.5]*5 for _ in range(5)])
        self.dr.acquire([[1.5]*5 for _ in range(5)])
        c = self.dr.process()
        self.assertEqual(len(c), 5)
        print("  [PASS] Process")
    
    def test_quality(self):
        """Should analyze quality."""
        self.dr.acquire([[1.0]*5 for _ in range(5)])
        q = self.dr.analyze_quality((2, 2, 2, 2), (0, 0, 2, 2))
        self.assertIn("dqe", q)
        print(f"  [PASS] Qual: {q}")
    
    def test_summary(self):
        """Should summarize."""
        self.dr.acquire([[1.0]*3 for _ in range(3)])
        s = self.dr.dr_summary()
        self.assertIn("images", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
