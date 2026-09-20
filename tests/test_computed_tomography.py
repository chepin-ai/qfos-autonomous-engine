"""
Unit tests for computed tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from computed_tomography import (CTProjection, RadonTransform,
                                  FilteredBackprojection,
                                  CTArtifactCorrector,
                                  ComputedTomography)


class TestRadonTransform(unittest.TestCase):
    """Test Radon transform."""
    
    def setUp(self):
        self.rt = RadonTransform(32)
    
    def test_line_integral(self):
        """Should compute line integral."""
        img = [[1.0] * 32 for _ in range(32)]
        val = self.rt.line_integral(img, 0.0, 0.0)
        self.assertGreater(val, 0)
        print(f"  [PASS] LineInt: {val:.4f}")
    
    def test_project(self):
        """Should compute projections."""
        img = [[0.0] * 32 for _ in range(32)]
        for y in range(10, 22):
            for x in range(10, 22):
                img[y][x] = 1.0
        proj = self.rt.project(img, [0.0, 90.0], 32)
        self.assertEqual(len(proj), 2)
        self.assertGreater(sum(proj[0.0]), 0)
        print("  [PASS] Project")


class TestFilteredBackprojection(unittest.TestCase):
    """Test FBP."""
    
    def setUp(self):
        self.fbp = FilteredBackprojection(32)
    
    def test_ram_lak(self):
        """Should generate filter."""
        k = self.fbp.ram_lak_filter(16)
        self.assertEqual(len(k), 16)
        self.assertEqual(k[8], 1.0)
        print("  [PASS] RamLak")
    
    def test_convolve(self):
        """Should convolve."""
        s = [1.0, 2.0, 3.0, 4.0]
        k = [0.5, 1.0, 0.5]
        c = self.fbp.convolve(s, k)
        self.assertEqual(len(c), 4)
        print(f"  [PASS] Conv: {c}")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        img = [[0.0] * 32 for _ in range(32)]
        for y in range(10, 22):
            for x in range(10, 22):
                img[y][x] = 1.0
        rt = RadonTransform(32)
        proj = rt.project(img, [i * 3.0 for i in range(60)], 32)
        rec = self.fbp.reconstruct(proj)
        self.assertEqual(len(rec), 32)
        print("  [PASS] Reconstruct")


class TestCTArtifactCorrector(unittest.TestCase):
    """Test artifact correction."""
    
    def setUp(self):
        self.ac = CTArtifactCorrector()
    
    def test_beam_hardening(self):
        """Should correct beam hardening."""
        p = [1.0, 2.0, 3.0]
        c = self.ac.beam_hardening_correction(p)
        self.assertEqual(len(c), 3)
        self.assertGreater(c[1], p[1])
        print(f"  [PASS] BH: {c}")
    
    def test_ring_reduction(self):
        """Should reduce rings."""
        s = [[1.0, 100.0, 1.0], [1.0, 100.0, 1.0]]
        c = self.ac.ring_artifact_reduction(s)
        self.assertEqual(len(c), 2)
        print("  [PASS] RingRed")


class TestComputedTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ct = ComputedTomography(32)
    
    def test_scan(self):
        """Should scan."""
        img = [[0.0] * 32 for _ in range(32)]
        for y in range(10, 22):
            for x in range(10, 22):
                img[y][x] = 1.0
        self.ct.scan(img, [0.0, 45.0, 90.0], 32)
        self.assertEqual(len(self.ct.projections), 3)
        print("  [PASS] Scan")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        img = [[0.0] * 32 for _ in range(32)]
        for y in range(10, 22):
            for x in range(10, 22):
                img[y][x] = 1.0
        self.ct.scan(img, [i * 3.0 for i in range(60)], 32)
        rec = self.ct.reconstruct_fbp()
        self.assertIsNotNone(rec)
        print("  [PASS] Recon")
    
    def test_summary(self):
        """Should summarize."""
        self.ct.scan([[0.0] * 32 for _ in range(32)])
        s = self.ct.ct_summary()
        self.assertIn("projections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
