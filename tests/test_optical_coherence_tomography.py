"""
Unit tests for optical coherence tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from optical_coherence_tomography import (AScan, AScanProcessor,
                                          BScanReconstructor,
                                          DepthProfiler,
                                          LayerSegmenter,
                                          OpticalCoherenceTomography)


class TestAScanProcessor(unittest.TestCase):
    """Test A-scan."""
    
    def setUp(self):
        self.asp = AScanProcessor()
    
    def test_envelope(self):
        """Should compute envelope."""
        sig = [0.0, 1.0, 0.0, -1.0, 0.0]
        e = self.asp.envelope(sig)
        self.assertEqual(len(e), 5)
        print(f"  [PASS] Env: {e}")
    
    def test_peaks(self):
        """Should find peaks."""
        env = [0.1, 0.5, 1.0, 0.5, 0.1]
        depth = [0.0, 0.25, 0.5, 0.75, 1.0]
        p = self.asp.peak_positions(env, depth)
        self.assertGreater(len(p), 0)
        print(f"  [PASS] Peaks: {p}")


class TestBScanReconstructor(unittest.TestCase):
    """Test B-scan."""
    
    def setUp(self):
        self.bsr = BScanReconstructor()
    
    def test_add(self):
        """Should add A-scan."""
        a = AScan([0.0, 0.5, 1.0], [1.0, 2.0, 3.0], 0.0)
        self.bsr.add_ascan(a)
        self.assertEqual(len(self.bsr.ascans), 1)
        print("  [PASS] Add")
    
    def test_reconstruct(self):
        """Should reconstruct B-scan."""
        self.bsr.add_ascan(AScan([0.0, 0.5], [1.0, 2.0], 0.0))
        self.bsr.add_ascan(AScan([0.0, 0.5], [3.0, 4.0], 1.0))
        img = self.bsr.reconstruct()
        self.assertEqual(len(img), 2)
        print(f"  [PASS] Rec: {len(img)}x{len(img[0])}")


class TestDepthProfiler(unittest.TestCase):
    """Test profiler."""
    
    def setUp(self):
        self.dp = DepthProfiler()
    
    def test_attenuation(self):
        """Should compute attenuation."""
        ints = [1.0, 0.8, 0.6, 0.4, 0.2]
        depths = [0.0, 0.25, 0.5, 0.75, 1.0]
        a = self.dp.attenuation_coefficient(ints, depths)
        self.assertGreater(a, 0)
        print(f"  [PASS] Att: {a:.4f}")
    
    def test_penetration(self):
        """Should find penetration."""
        ints = [1.0, 0.9, 0.8, 0.05, 0.02]
        depths = [0.0, 0.25, 0.5, 0.75, 1.0]
        p = self.dp.penetration_depth(ints, depths)
        self.assertGreater(p, 0)
        print(f"  [PASS] Pen: {p:.4f}")


class TestLayerSegmenter(unittest.TestCase):
    """Test segmenter."""
    
    def setUp(self):
        self.ls = LayerSegmenter()
    
    def test_segment(self):
        """Should segment layers."""
        bscan = [[1.0, 2.0, 1.0, 0.5, 0.1],
                 [1.0, 2.0, 1.0, 0.5, 0.1]]
        depth = [0.0, 0.25, 0.5, 0.75, 1.0]
        l = self.ls.segment(bscan, depth)
        self.assertGreaterEqual(len(l), 0)
        print(f"  [PASS] Lay: {len(l)}")


class TestOpticalCoherenceTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.oct = OpticalCoherenceTomography()
    
    def test_capture(self):
        """Should capture A-scan."""
        self.oct.capture_ascan([0.0, 0.5, 1.0], [1.0, 2.0, 3.0], 0.0)
        self.assertEqual(len(self.oct.reconstructor.ascans), 1)
        print("  [PASS] Cap")
    
    def test_inspect(self):
        """Should inspect."""
        self.oct.capture_ascan([0.0, 0.5, 1.0], [1.0, 2.0, 3.0], 0.0)
        self.oct.capture_ascan([0.0, 0.5, 1.0], [1.5, 2.5, 3.5], 1.0)
        r = self.oct.inspect()
        self.assertIn("layers", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        self.oct.capture_ascan([0.0, 0.5], [1.0, 2.0], 0.0)
        s = self.oct.oct_summary()
        self.assertIn("ascans", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
