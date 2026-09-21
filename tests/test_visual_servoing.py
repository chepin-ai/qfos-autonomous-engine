"""
Unit tests for visual servoing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visual_servoing import (ImageFeature, ImageBasedServoing,
                             PositionBasedServoing,
                             FeatureTracker,
                             CameraRobotCalibration,
                             VisualServoing)


class TestImageBasedServoing(unittest.TestCase):
    """Test IBVS."""
    
    def setUp(self):
        self.ibvs = ImageBasedServoing(500.0, 0.1)
    
    def test_interaction_matrix(self):
        """Should compute L."""
        L = self.ibvs.interaction_matrix(ImageFeature(10.0, 20.0), 1.0)
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L[0]), 6)
        print("  [PASS] L")
    
    def test_error(self):
        """Should compute error."""
        e = self.ibvs.error_vector(ImageFeature(15.0, 25.0), ImageFeature(10.0, 20.0))
        self.assertEqual(e, [5.0, 5.0])
        print(f"  [PASS] e: {e}")
    
    def test_velocity(self):
        """Should compute velocity."""
        v = self.ibvs.camera_velocity(ImageFeature(15.0, 25.0), ImageFeature(10.0, 20.0), 1.0)
        self.assertEqual(len(v), 6)
        print(f"  [PASS] v: {v}")


class TestPositionBasedServoing(unittest.TestCase):
    """Test PBVS."""
    
    def setUp(self):
        self.pbvs = PositionBasedServoing(0.5)
    
    def test_error(self):
        """Should compute error."""
        e = self.pbvs.position_error([1.0, 2.0, 3.0, 0.0, 0.0, 0.0],
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(e[0], 1.0)
        print(f"  [PASS] e: {e}")


class TestFeatureTracker(unittest.TestCase):
    """Test tracker."""
    
    def setUp(self):
        self.ft = FeatureTracker()
    
    def test_centroid(self):
        """Should compute centroid."""
        c = self.ft.centroid([ImageFeature(0.0, 0.0), ImageFeature(10.0, 20.0)])
        self.assertEqual(c.u, 5.0)
        print(f"  [PASS] Cen: ({c.u}, {c.v})")
    
    def test_bbox(self):
        """Should compute bounding box."""
        b = self.ft.bounding_box([ImageFeature(0.0, 5.0), ImageFeature(10.0, 20.0)])
        self.assertEqual(b, (0.0, 5.0, 10.0, 20.0))
        print(f"  [PASS] BBox: {b}")


class TestCameraRobotCalibration(unittest.TestCase):
    """Test calibration."""
    
    def setUp(self):
        self.cal = CameraRobotCalibration()
    
    def test_pixel_to_meter(self):
        """Should convert pixels to meters."""
        m = self.cal.pixel_to_meter(100.0, 2.0, 500.0)
        self.assertEqual(m, 0.4)
        print(f"  [PASS] m: {m:.3f}")
    
    def test_meter_to_pixel(self):
        """Should convert meters to pixels."""
        p = self.cal.meter_to_pixel(0.4, 2.0, 500.0)
        self.assertEqual(p, 100.0)
        print(f"  [PASS] px: {p:.1f}")


class TestVisualServoing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.vs = VisualServoing()
    
    def test_summary(self):
        """Should summarize."""
        s = self.vs.vs_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
