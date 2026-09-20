"""
Unit tests for visual testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visual_testing import (VisualDefect, ImageEnhancer,
                            VisualDefectDetector,
                            DimensionalMeasurer,
                            VisualTesting)


class TestImageEnhancer(unittest.TestCase):
    """Test enhancer."""
    
    def setUp(self):
        self.ie = ImageEnhancer()
    
    def test_contrast(self):
        """Should stretch contrast."""
        img = [[0.1, 0.2], [0.8, 0.9]]
        e = self.ie.contrast_stretch(img)
        self.assertEqual(len(e), 2)
        print("  [PASS] Cont")
    
    def test_edge(self):
        """Should enhance edges."""
        img = [[0.0, 0.5, 0.0], [0.5, 1.0, 0.5], [0.0, 0.5, 0.0]]
        e = self.ie.edge_enhance(img)
        self.assertEqual(len(e), 3)
        print("  [PASS] Edge")


class TestVisualDefectDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.det = VisualDefectDetector(0.5, 0.2)
    
    def test_detect(self):
        """Should detect defects."""
        img = [
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 1.0, 1.0, 0.5],
            [0.5, 1.0, 1.0, 0.5],
            [0.5, 0.5, 0.5, 0.5]
        ]
        d = self.det.detect(img, 1.0)
        self.assertEqual(len(d), 1)
        print(f"  [PASS] Det: {len(d)}")


class TestDimensionalMeasurer(unittest.TestCase):
    """Test measurer."""
    
    def setUp(self):
        self.dm = DimensionalMeasurer()
    
    def test_length(self):
        """Should measure length."""
        pts = [(0.0, 0.0), (3.0, 4.0)]
        l = self.dm.measure_length(pts)
        self.assertAlmostEqual(l, 5.0, places=5)
        print(f"  [PASS] Len: {l}")
    
    def test_angle(self):
        """Should measure angle."""
        a = self.dm.measure_angle((0.0, 0.0), (0.0, 0.0), (1.0, 0.0))
        self.assertEqual(a, 0.0)
        print(f"  [PASS] Ang: {a}")


class TestVisualTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.vt = VisualTesting()
    
    def test_inspect(self):
        """Should inspect."""
        img = [
            [0.5, 0.5, 0.5, 0.5],
            [0.5, 1.0, 1.0, 0.5],
            [0.5, 1.0, 1.0, 0.5],
            [0.5, 0.5, 0.5, 0.5]
        ]
        r = self.vt.inspect(img, 1.0)
        self.assertIn("defects", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.vt.vt_summary()
        self.assertIn("defects", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
