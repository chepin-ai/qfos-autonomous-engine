"""
Unit tests for visual servoing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visual_servoing import (ImageFeature, Point3D,
                             ImageBasedVisualServoing,
                             PositionBasedVisualServoing,
                             FeatureTracking,
                             CameraCalibration,
                             VisualServoing)


class TestImageBasedVisualServoing(unittest.TestCase):
    """Test IBVS."""
    
    def setUp(self):
        self.ibvs = ImageBasedVisualServoing()
    
    def test_interaction(self):
        """Should compute interaction matrix."""
        f = ImageFeature(10.0, 20.0)
        L = self.ibvs.interaction_matrix(f)
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L[0]), 6)
        print(f"  [PASS] L: 2x6")
    
    def test_error(self):
        """Should compute error."""
        c = ImageFeature(10.0, 20.0)
        d = ImageFeature(5.0, 15.0)
        e = self.ibvs.feature_error(c, d)
        self.assertEqual(e, [5.0, 5.0])
        print(f"  [PASS] E: {e}")
    
    def test_velocity(self):
        """Should compute velocity."""
        c = ImageFeature(10.0, 0.0)
        d = ImageFeature(0.0, 0.0)
        v = self.ibvs.camera_velocity(c, d)
        self.assertEqual(len(v), 6)
        print(f"  [PASS] V: {len(v)}D")


class TestPositionBasedVisualServoing(unittest.TestCase):
    """Test PBVS."""
    
    def setUp(self):
        self.pbvs = PositionBasedVisualServoing()
    
    def test_error(self):
        """Should compute pose error."""
        e = self.pbvs.pose_error([1.0, 2.0, 3.0], [0.0, 1.0, 2.0])
        self.assertEqual(e, [1.0, 1.0, 1.0])
        print(f"  [PASS] E: {e}")
    
    def test_command(self):
        """Should compute velocity command."""
        v = self.pbvs.velocity_command([1.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        self.assertEqual(v, [-0.5, 0.0, 0.0])
        print(f"  [PASS] V: {v}")


class TestFeatureTracking(unittest.TestCase):
    """Test tracking."""
    
    def setUp(self):
        self.ft = FeatureTracking()
    
    def test_update(self):
        """Should update track."""
        self.ft.update_track(0, ImageFeature(10.0, 20.0))
        self.assertEqual(self.ft.num_tracks(), 1)
        print(f"  [PASS] Tracks: {self.ft.num_tracks()}")
    
    def test_velocity(self):
        """Should compute velocity."""
        self.ft.update_track(0, ImageFeature(0.0, 0.0))
        self.ft.update_track(0, ImageFeature(10.0, 20.0))
        v = self.ft.track_velocity(0)
        self.assertEqual(v, (10.0, 20.0))
        print(f"  [PASS] Vel: {v}")


class TestCameraCalibration(unittest.TestCase):
    """Test camera."""
    
    def setUp(self):
        self.cam = CameraCalibration()
    
    def test_project(self):
        """Should project 3D to 2D."""
        p = self.cam.project(Point3D(1.0, 0.0, 1.0))
        self.assertEqual(p.u, 820.0)
        print(f"  [PASS] P: ({p.u}, {p.v})")
    
    def test_backproject(self):
        """Should backproject 2D to 3D."""
        p = self.cam.backproject(ImageFeature(320.0, 240.0))
        self.assertEqual(p.x, 0.0)
        print(f"  [PASS] BP: ({p.x}, {p.y}, {p.z})")


class TestVisualServoing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.vs = VisualServoing()
    
    def test_summary(self):
        """Should summarize."""
        s = self.vs.servoing_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
