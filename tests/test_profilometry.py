"""
Unit tests for profilometry module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from profilometry import (ProfilePoint, ProfileAcquisition,
                          RoughnessAnalyzer,
                          WavinessAnalyzer,
                          FormErrorEvaluator,
                          Profilometry)


class TestProfileAcquisition(unittest.TestCase):
    """Test acquisition."""
    
    def setUp(self):
        self.pa = ProfileAcquisition(5.0)
    
    def test_generate(self):
        """Should generate profile."""
        p = self.pa.generate_profile(1.0, 1.0)
        self.assertGreater(len(p), 0)
        print(f"  [PASS] Gen: {len(p)} pts")
    
    def test_resample(self):
        """Should resample."""
        p = self.pa.generate_profile(1.0, 1.0)
        r = self.pa.resample(p, 10.0)
        self.assertGreater(len(r), 0)
        print(f"  [PASS] Resamp: {len(r)} pts")


class TestRoughnessAnalyzer(unittest.TestCase):
    """Test roughness."""
    
    def setUp(self):
        self.ra = RoughnessAnalyzer(0.8)
        self.profile = [ProfilePoint(0.0, 1.0), ProfilePoint(0.1, -1.0),
                       ProfilePoint(0.2, 1.0), ProfilePoint(0.3, -1.0)]
    
    def test_ra(self):
        """Should compute Ra."""
        r = self.ra.ra(self.profile)
        self.assertGreater(r, 0)
        print(f"  [PASS] Ra: {r:.4f} um")
    
    def test_rq(self):
        """Should compute Rq."""
        r = self.ra.rq(self.profile)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rq: {r:.4f} um")
    
    def test_rz(self):
        """Should compute Rz."""
        r = self.ra.rz(self.profile)
        self.assertEqual(r, 2.0)
        print(f"  [PASS] Rz: {r} um")
    
    def test_rt(self):
        """Should compute Rt."""
        r = self.ra.rt(self.profile)
        self.assertEqual(r, 2.0)
        print(f"  [PASS] Rt: {r} um")


class TestWavinessAnalyzer(unittest.TestCase):
    """Test waviness."""
    
    def setUp(self):
        self.wa = WavinessAnalyzer(0.8)
        self.profile = [ProfilePoint(float(i)*0.1, math.sin(i)) for i in range(20)]
    
    def test_wa(self):
        """Should compute Wa."""
        w = self.wa.wa(self.profile)
        self.assertGreaterEqual(w, 0)
        print(f"  [PASS] Wa: {w:.4f} um")


class TestFormErrorEvaluator(unittest.TestCase):
    """Test form."""
    
    def setUp(self):
        self.fe = FormErrorEvaluator()
    
    def test_line(self):
        """Should fit line."""
        p = [ProfilePoint(0.0, 0.0), ProfilePoint(1.0, 1.0)]
        m, b = self.fe.least_squares_line(p)
        self.assertAlmostEqual(m, 1.0, places=5)
        print(f"  [PASS] Line: m={m:.4f}")
    
    def test_flatness(self):
        """Should compute flatness."""
        p = [ProfilePoint(0.0, 0.0), ProfilePoint(1.0, 0.0),
             ProfilePoint(0.5, 1.0)]
        f = self.fe.flatness(p)
        self.assertGreater(f, 0)
        print(f"  [PASS] Flat: {f:.4f} um")


class TestProfilometry(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.prof = Profilometry()
    
    def test_measure(self):
        """Should measure."""
        self.prof.measure(1.0, 1.0)
        self.assertGreater(len(self.prof.profile), 0)
        print("  [PASS] Meas")
    
    def test_analyze(self):
        """Should analyze."""
        self.prof.measure(1.0, 1.0)
        r = self.prof.analyze()
        self.assertIn("Ra_um", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        self.prof.measure(1.0, 1.0)
        s = self.prof.prof_summary()
        self.assertIn("points", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
