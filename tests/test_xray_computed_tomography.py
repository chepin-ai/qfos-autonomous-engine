"""
Unit tests for X-ray computed tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xray_computed_tomography import (CTProjection, ProjectionAcquirer,
                                      FilteredBackProjection,
                                      ArtifactReducer,
                                      XRayComputedTomography)


class TestProjectionAcquirer(unittest.TestCase):
    """Test acquirer."""
    
    def setUp(self):
        self.pa = ProjectionAcquirer(180, 64)
    
    def test_angles(self):
        """Should generate angles."""
        a = self.pa.generate_angles()
        self.assertEqual(len(a), 180)
        self.assertAlmostEqual(a[0], 0.0, places=5)
        print(f"  [PASS] Ang: {len(a)} angles")
    
    def test_simulate(self):
        """Should simulate projection."""
        phantom = [[0.0] * 8 for _ in range(8)]
        phantom[3][3] = 1.0
        p = self.pa.simulate_projection(0.0, phantom, 8)
        self.assertEqual(len(p), 64)
        print(f"  [PASS] Sim: {len(p)} detectors")


class TestFilteredBackProjection(unittest.TestCase):
    """Test FBP."""
    
    def setUp(self):
        self.fbp = FilteredBackProjection(32)
    
    def test_filter(self):
        """Should apply ramp filter."""
        proj = [0.0, 1.0, 2.0, 1.0, 0.0]
        f = self.fbp.ramp_filter(proj)
        self.assertEqual(len(f), 5)
        print(f"  [PASS] Filt: {f}")
    
    def test_back_project(self):
        """Should back-project."""
        projs = [CTProjection(0.0, [1.0] * 32, 500.0, 250.0),
                 CTProjection(90.0, [1.0] * 32, 500.0, 250.0)]
        img = self.fbp.back_project(projs)
        self.assertEqual(len(img), 32)
        print(f"  [PASS] BP: {len(img)}x{len(img[0])}")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        projs = [CTProjection(0.0, [1.0] * 32, 500.0, 250.0),
                 CTProjection(90.0, [1.0] * 32, 500.0, 250.0)]
        img = self.fbp.reconstruct(projs)
        self.assertEqual(len(img), 32)
        print("  [PASS] Rec")


class TestArtifactReducer(unittest.TestCase):
    """Test reducer."""
    
    def setUp(self):
        self.ar = ArtifactReducer()
    
    def test_ring(self):
        """Should reduce rings."""
        img = [[1.0] * 8 for _ in range(8)]
        r = self.ar.ring_artifact_reduction(img)
        self.assertEqual(len(r), 8)
        print("  [PASS] Ring")
    
    def test_beam(self):
        """Should correct beam hardening."""
        img = [[10.0] * 4 for _ in range(4)]
        c = self.ar.beam_hardening_correction(img)
        self.assertLess(c[0][0], 10.0)
        print(f"  [PASS] Beam: {c[0][0]:.4f}")


class TestXRayComputedTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ct = XRayComputedTomography(32)
    
    def test_scan(self):
        """Should scan."""
        phantom = [[0.0] * 8 for _ in range(8)]
        phantom[3][3] = 1.0
        phantom[4][4] = 1.0
        self.ct.scan(phantom, 90)
        self.assertEqual(len(self.ct.projections), 90)
        print("  [PASS] Scan")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        phantom = [[0.0] * 8 for _ in range(8)]
        phantom[3][3] = 1.0
        self.ct.scan(phantom, 90)
        img = self.ct.reconstruct()
        self.assertEqual(len(img), 32)
        print("  [PASS] Rec")
    
    def test_inspect(self):
        """Should inspect."""
        phantom = [[0.0] * 8 for _ in range(8)]
        phantom[3][3] = 1.0
        self.ct.scan(phantom, 90)
        self.ct.reconstruct()
        r = self.ct.inspect()
        self.assertIn("mean", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ct.ct_summary()
        self.assertIn("image_size", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
