"""
Unit tests for computer vision module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from computer_vision import (ImagePoint, ImageFilter,
                             HoughTransform,
                             FeatureExtractor,
                             ObjectDetector,
                             ComputerVision)


class TestImageFilter(unittest.TestCase):
    """Test filter."""
    
    def setUp(self):
        self.f = ImageFilter()
    
    def test_gaussian_kernel(self):
        """Should generate kernel."""
        k = self.f.gaussian_kernel(3, 1.0)
        self.assertEqual(len(k), 3)
        total = sum(sum(row) for row in k)
        self.assertAlmostEqual(total, 1.0, places=5)
        print("  [PASS] Gauss")
    
    def test_convolve(self):
        """Should convolve."""
        img = [[0.0, 0.0, 0.0],
               [0.0, 1.0, 0.0],
               [0.0, 0.0, 0.0]]
        k = [[0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0]]
        r = self.f.convolve(img, k)
        self.assertAlmostEqual(r[1][1], 1.0)
        print("  [PASS] Conv")
    
    def test_sobel(self):
        """Should detect edges."""
        img = [[0.0, 0.0, 0.0],
               [255.0, 255.0, 255.0],
               [0.0, 0.0, 0.0]]
        e = self.f.sobel_edge(img)
        max_edge = max(max(row) for row in e)
        self.assertGreater(max_edge, 0)
        print("  [PASS] Sobel")


class TestHoughTransform(unittest.TestCase):
    """Test Hough."""
    
    def setUp(self):
        self.h = HoughTransform(90, 50)
    
    def test_detect_lines(self):
        """Should detect lines."""
        edge = [[0.0] * 10 for _ in range(10)]
        for i in range(10):
            edge[5][i] = 255.0
        lines = self.h.detect_lines(edge, 100.0)
        self.assertIsInstance(lines, list)
        print(f"  [PASS] Hough: {len(lines)} lines")


class TestFeatureExtractor(unittest.TestCase):
    """Test features."""
    
    def setUp(self):
        self.fe = FeatureExtractor()
    
    def test_histogram(self):
        """Should compute histogram."""
        edge = [[0.0] * 5 for _ in range(5)]
        edge[2][2] = 255.0
        h = self.fe.gradient_histogram(edge, 4)
        self.assertEqual(len(h), 4)
        self.assertAlmostEqual(sum(h), 1.0, places=5)
        print(f"  [PASS] Hist: {h}")
    
    def test_corners(self):
        """Should find corners."""
        edge = [[0.0] * 5 for _ in range(5)]
        edge[2][2] = 255.0
        c = self.fe.corners_from_edges(edge, 100.0)
        self.assertIsInstance(c, list)
        print(f"  [PASS] Corn: {len(c)}")


class TestObjectDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.od = ObjectDetector()
    
    def test_bboxes(self):
        """Should find boxes."""
        img = [[0.0] * 10 for _ in range(10)]
        for y in range(2, 5):
            for x in range(2, 5):
                img[y][x] = 255.0
        boxes = self.od.bounding_boxes(img, 128.0)
        self.assertGreater(len(boxes), 0)
        print(f"  [PASS] BBox: {len(boxes)}")


class TestComputerVision(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.cv = ComputerVision()
    
    def test_summary(self):
        """Should summarize."""
        s = self.cv.cv_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
