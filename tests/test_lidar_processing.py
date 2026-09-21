"""
Unit tests for LiDAR processing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lidar_processing import (Point3D, PointCloudFilter,
                              DBSCANClustering,
                              GroundSegmentation,
                              BoundingBoxEstimator,
                              LiDARProcessing)


class TestPointCloudFilter(unittest.TestCase):
    """Test filter."""
    
    def setUp(self):
        self.pcf = PointCloudFilter()
    
    def test_range_filter(self):
        """Should filter by range."""
        pts = [Point3D(1.0, 0.0, 0.0), Point3D(5.0, 0.0, 0.0)]
        r = self.pcf.range_filter(pts, 0.5, 3.0)
        self.assertEqual(len(r), 1)
        print(f"  [PASS] Rng: {len(r)}")
    
    def test_height_filter(self):
        """Should filter by height."""
        pts = [Point3D(0.0, 0.0, 0.1), Point3D(0.0, 0.0, 2.0)]
        r = self.pcf.height_filter(pts, 0.0, 1.0)
        self.assertEqual(len(r), 1)
        print(f"  [PASS] Ht: {len(r)}")
    
    def test_voxel_downsample(self):
        """Should downsample."""
        pts = [Point3D(0.05, 0.05, 0.05), Point3D(0.06, 0.06, 0.06)]
        r = self.pcf.voxel_downsample(pts, 0.1)
        self.assertEqual(len(r), 1)
        print(f"  [PASS] Vox: {len(r)}")


class TestDBSCANClustering(unittest.TestCase):
    """Test DBSCAN."""
    
    def setUp(self):
        self.db = DBSCANClustering(1.0, 2)
    
    def test_cluster(self):
        """Should cluster."""
        pts = [Point3D(0.0, 0.0, 0.0), Point3D(0.1, 0.0, 0.0),
               Point3D(5.0, 0.0, 0.0)]
        c = self.db.cluster(pts)
        self.assertGreater(len(c), 0)
        print(f"  [PASS] Clust: {len(c)}")


class TestGroundSegmentation(unittest.TestCase):
    """Test ground."""
    
    def setUp(self):
        self.gs = GroundSegmentation(0.5)
    
    def test_segment(self):
        """Should segment."""
        pts = [Point3D(0.0, 0.0, 0.0), Point3D(1.0, 0.0, 0.1),
               Point3D(0.0, 1.0, 2.0)]
        g, o = self.gs.segment(pts)
        self.assertGreater(len(g), 0)
        self.assertGreater(len(o), 0)
        print(f"  [PASS] Gnd: {len(g)}, Obs: {len(o)}")


class TestBoundingBoxEstimator(unittest.TestCase):
    """Test bbox."""
    
    def setUp(self):
        self.bbe = BoundingBoxEstimator()
    
    def test_bbox(self):
        """Should compute bbox."""
        pts = [Point3D(0.0, 0.0, 0.0), Point3D(1.0, 2.0, 3.0)]
        b = self.bbe.bbox(pts)
        self.assertIn("volume", b)
        self.assertEqual(b["volume"], 6.0)
        print(f"  [PASS] BBox: {b['volume']}")
    
    def test_centroid(self):
        """Should compute centroid."""
        pts = [Point3D(0.0, 0.0, 0.0), Point3D(2.0, 4.0, 6.0)]
        c = self.bbe.centroid(pts)
        self.assertEqual(c.x, 1.0)
        print(f"  [PASS] Cent: ({c.x}, {c.y}, {c.z})")


class TestLiDARProcessing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.lp = LiDARProcessing()
    
    def test_process(self):
        """Should process."""
        pts = [Point3D(0.0, 0.0, 0.0), Point3D(0.1, 0.0, 0.0),
               Point3D(0.0, 0.1, 2.0)]
        r = self.lp.process(pts)
        self.assertIn("num_clusters", r)
        print(f"  [PASS] Proc: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.lp.lp_summary()
        self.assertIn("stages", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
