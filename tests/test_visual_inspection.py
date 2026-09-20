"""
Unit tests for visual inspection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visual_inspection import (DefectType, VisualDefect,
                               EdgeDetector, BlobAnalyzer,
                               PatternMatcher, LightingCompensator,
                               VisualInspection)


class TestEdgeDetector(unittest.TestCase):
    """Test edge detector."""
    
    def setUp(self):
        self.ed = EdgeDetector()
        self.image = [[100.0] * 10 for _ in range(10)]
        self.image[5][5] = 200.0
    
    def test_gradient(self):
        """Should compute gradient."""
        img = [[float(i + j) for i in range(10)] for j in range(10)]
        dx, dy = self.ed.gradient(img, 5, 5)
        self.assertNotEqual(dx, 0)
        print(f"  [PASS] Grad: dx={dx:.1f} dy={dy:.1f}")
    
    def test_detect(self):
        """Should detect edges."""
        edges = self.ed.detect_edges(self.image)
        self.assertEqual(len(edges), 10)
        print(f"  [PASS] Edges: {self.ed.edge_count(edges)} pixels")
    
    def test_magnitude(self):
        """Should compute magnitude."""
        m = self.ed.magnitude(3.0, 4.0)
        self.assertEqual(m, 5.0)
        print(f"  [PASS] Mag: {m}")


class TestBlobAnalyzer(unittest.TestCase):
    """Test blob analyzer."""
    
    def setUp(self):
        self.ba = BlobAnalyzer()
        self.image = [[10.0] * 10 for _ in range(10)]
        for y in range(3, 6):
            for x in range(3, 6):
                self.image[y][x] = 100.0
    
    def test_detect(self):
        """Should detect blobs."""
        blobs = self.ba.detect_blobs(self.image)
        self.assertGreater(len(blobs), 0)
        print(f"  [PASS] Blobs: {len(blobs)}")
    
    def test_circularity(self):
        """Should compute circularity."""
        blob = {"width": 3, "height": 3, "area": 9}
        c = self.ba.blob_circularity(blob)
        self.assertGreater(c, 0)
        print(f"  [PASS] Circ: {c:.4f}")


class TestPatternMatcher(unittest.TestCase):
    """Test pattern matcher."""
    
    def setUp(self):
        self.pm = PatternMatcher()
        self.pm.add_template("square", [[20.0, 30.0], [25.0, 35.0]])
    
    def test_ncc(self):
        """Should compute NCC."""
        image = [
            [10.0, 20.0, 30.0, 40.0, 50.0],
            [15.0, 25.0, 35.0, 45.0, 55.0],
            [20.0, 30.0, 40.0, 50.0, 60.0],
            [25.0, 35.0, 45.0, 55.0, 65.0],
            [30.0, 40.0, 50.0, 60.0, 70.0]
        ]
        ncc = self.pm.normalized_cross_correlation(image, [[20.0, 30.0], [25.0, 35.0]], 0, 0)
        self.assertGreater(ncc, 0)
        print(f"  [PASS] NCC: {ncc:.4f}")
    
    def test_match(self):
        """Should match patterns."""
        image = [
            [10.0, 20.0, 30.0, 40.0, 50.0],
            [15.0, 25.0, 35.0, 45.0, 55.0],
            [20.0, 30.0, 40.0, 50.0, 60.0],
            [25.0, 35.0, 45.0, 55.0, 65.0],
            [30.0, 40.0, 50.0, 60.0, 70.0]
        ]
        matches = self.pm.match(image, 0.5)
        self.assertGreater(len(matches), 0)
        print(f"  [PASS] Matches: {len(matches)}")


class TestLightingCompensator(unittest.TestCase):
    """Test lighting compensator."""
    
    def setUp(self):
        self.lc = LightingCompensator()
    
    def test_equalize(self):
        """Should equalize."""
        image = [[50.0] * 5 for _ in range(5)]
        eq = self.lc.histogram_equalization(image)
        self.assertEqual(len(eq), 5)
        print("  [PASS] Eq")
    
    def test_mean(self):
        """Should compute mean."""
        image = [[100.0] * 5 for _ in range(5)]
        m = self.lc.mean_intensity(image)
        self.assertEqual(m, 100.0)
        print(f"  [PASS] Mean: {m}")


class TestVisualInspection(unittest.TestCase):
    """Test unified visual inspection."""
    
    def setUp(self):
        self.vi = VisualInspection()
    
    def test_inspect(self):
        """Should inspect."""
        image = [[50.0] * 10 for _ in range(10)]
        image[5][5] = 200.0
        r = self.vi.inspect(image)
        self.assertIn("edge_pixels", r)
        print(f"  [PASS] Insp: edges={r['edge_pixels']}")
    
    def test_add_pattern(self):
        """Should add pattern."""
        self.vi.add_pattern("test", [[255.0, 255.0], [255.0, 255.0]])
        self.assertEqual(len(self.vi.pattern_matcher.templates), 1)
        print("  [PASS] AddPat")
    
    def test_summary(self):
        """Should summarize."""
        image = [[50.0] * 10 for _ in range(10)]
        self.vi.inspect(image)
        s = self.vi.inspection_summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
