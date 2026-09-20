"""
Unit tests for surface roughness module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from surface_roughness import (RoughnessStandard, ProfilePoint,
                               ProfileFilter, RoughnessParameters,
                               TextureDirection, FlatnessChecker,
                               SurfaceRoughness)


class TestProfileFilter(unittest.TestCase):
    """Test profile filter."""
    
    def test_remove_form(self):
        """Should remove linear trend."""
        pts = [ProfilePoint(0.0, 0.0), ProfilePoint(1.0, 1.0), ProfilePoint(2.0, 2.0)]
        f = ProfileFilter()
        out = f.remove_form(pts)
        self.assertAlmostEqual(out[0].z_um, 0.0, places=5)
        self.assertAlmostEqual(out[1].z_um, 0.0, places=5)
        print("  [PASS] Detrend")
    
    def test_roughness_profile(self):
        """Should extract roughness."""
        pts = [ProfilePoint(i * 0.1, math.sin(i)) for i in range(20)]
        f = ProfileFilter()
        out = f.roughness_profile(pts)
        self.assertEqual(len(out), 20)
        print("  [PASS] Roughness profile")


class TestRoughnessParameters(unittest.TestCase):
    """Test roughness parameters."""
    
    def setUp(self):
        pts = [ProfilePoint(0.0, 1.0), ProfilePoint(0.1, -1.0),
               ProfilePoint(0.2, 1.0), ProfilePoint(0.3, -1.0)]
        self.rp = RoughnessParameters(pts)
    
    def test_ra(self):
        """Should compute Ra."""
        ra = self.rp.ra()
        self.assertAlmostEqual(ra, 1.0)
        print(f"  [PASS] Ra: {ra}")
    
    def test_rq(self):
        """Should compute Rq."""
        rq = self.rp.rq()
        self.assertAlmostEqual(rq, 1.0)
        print(f"  [PASS] Rq: {rq}")
    
    def test_rz(self):
        """Should compute Rz."""
        rz = self.rp.rz()
        self.assertAlmostEqual(rz, 2.0)
        print(f"  [PASS] Rz: {rz}")
    
    def test_rmax(self):
        """Should compute Rmax."""
        rm = self.rp.rmax()
        self.assertAlmostEqual(rm, 2.0)
        print(f"  [PASS] Rmax: {rm}")
    
    def test_skewness(self):
        """Should compute skewness."""
        sk = self.rp.skewness()
        self.assertAlmostEqual(sk, 0.0, places=5)
        print(f"  [PASS] Skew: {sk}")
    
    def test_kurtosis(self):
        """Should compute kurtosis."""
        ku = self.rp.kurtosis()
        self.assertAlmostEqual(ku, 1.0)
        print(f"  [PASS] Kurt: {ku}")


class TestTextureDirection(unittest.TestCase):
    """Test texture direction."""
    
    def setUp(self):
        self.td = TextureDirection()
    
    def test_dominant_direction(self):
        """Should compute direction."""
        pts = [(i, 2 * i) for i in range(10)]
        angle = self.td.dominant_direction(pts)
        self.assertIsInstance(angle, float)
        print(f"  [PASS] Dir: {angle:.1f}°")
    
    def test_isotropic(self):
        """Should detect isotropy."""
        pts = [(i, i) for i in range(10)]
        idx = self.td.isotropic_index(pts)
        self.assertGreaterEqual(idx, 0.0)
        self.assertLessEqual(idx, 1.0)
        print(f"  [PASS] Iso: {idx:.3f}")


class TestFlatnessChecker(unittest.TestCase):
    """Test flatness checker."""
    
    def setUp(self):
        self.fc = FlatnessChecker(tolerance_um=5.0)
    
    def test_flat(self):
        """Should pass flat surface."""
        pts = [ProfilePoint(0.0, 0.0), ProfilePoint(1.0, 0.5), ProfilePoint(2.0, 0.0)]
        ok = self.fc.check_flatness(pts)
        self.assertTrue(ok)
        print("  [PASS] Flat")
    
    def test_not_flat(self):
        """Should fail uneven surface."""
        pts = [ProfilePoint(0.0, 0.0), ProfilePoint(1.0, 20.0), ProfilePoint(2.0, 0.0)]
        ok = self.fc.check_flatness(pts)
        self.assertFalse(ok)
        print("  [PASS] Not flat")


class TestSurfaceRoughness(unittest.TestCase):
    """Test unified surface roughness."""
    
    def setUp(self):
        self.sr = SurfaceRoughness()
    
    def test_measure(self):
        """Should measure."""
        pts = [ProfilePoint(i * 0.1, (-1)**i) for i in range(10)]
        self.sr.measure(pts)
        self.assertIsNotNone(self.sr.parameters)
        print("  [PASS] Measure")
    
    def test_report(self):
        """Should generate report."""
        pts = [ProfilePoint(i * 0.1, (-1)**i) for i in range(10)]
        self.sr.measure(pts)
        r = self.sr.roughness_report()
        self.assertIn("ra_um", r)
        print(f"  [PASS] Report: Ra={r['ra_um']:.3f}")
    
    def test_pass(self):
        """Should pass."""
        pts = [ProfilePoint(i * 0.1, 0.1 * (-1)**i) for i in range(10)]
        self.sr.measure(pts)
        self.assertTrue(self.sr.pass_fail(ra_limit_um=1.0))
        print("  [PASS] Pass")


if __name__ == '__main__':
    unittest.main(verbosity=2)
