"""
Unit tests for perception pipeline module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from perception_pipeline import (PointCloudProcessor, ObjectDetector, FeatureExtractor,
                                 PerceptionPipeline, Point3D, BoundingBox, DetectedObject)


class TestPointCloudProcessor(unittest.TestCase):
    """Test point cloud processor."""
    
    def setUp(self):
        self.pcp = PointCloudProcessor(voxel_size=1.0)
        self.points = [
            Point3D(0.1, 0.1, 0.1),
            Point3D(0.2, 0.2, 0.2),
            Point3D(5.0, 5.0, 5.0),
        ]
    
    def test_downsample(self):
        """Should downsample points."""
        result = self.pcp.downsample(self.points)
        self.assertLessEqual(len(result), len(self.points))
        print(f"  [PASS] Downsample: {len(self.points)} -> {len(result)}")
    
    def test_filter_distance(self):
        """Should filter by distance."""
        result = self.pcp.filter_distance(self.points, max_distance=2.0)
        self.assertEqual(len(result), 2)
        print(f"  [PASS] Filter: {len(result)} points")
    
    def test_estimate_normals(self):
        """Should estimate normals."""
        normals = self.pcp.estimate_normals(self.points, k=2)
        self.assertEqual(len(normals), len(self.points))
        for n in normals:
            norm = sum(c**2 for c in n) ** 0.5
            self.assertAlmostEqual(norm, 1.0, places=5)
        print("  [PASS] Normals: unit vectors")


class TestObjectDetector(unittest.TestCase):
    """Test object detector."""
    
    def setUp(self):
        self.od = ObjectDetector(cluster_distance=1.0, min_cluster_size=3)
    
    def test_cluster_points(self):
        """Should cluster points."""
        points = [
            Point3D(0, 0, 0), Point3D(0.1, 0.1, 0),
            Point3D(0.2, 0, 0), Point3D(0.15, 0.15, 0),
            Point3D(10, 10, 10), Point3D(10.1, 10.1, 10),
            Point3D(10.2, 10, 10),
        ]
        clusters = self.od.cluster_points(points)
        self.assertGreaterEqual(len(clusters), 1)
        print(f"  [PASS] Clusters: {len(clusters)}")
    
    def test_detect(self):
        """Should detect objects."""
        points = []
        for i in range(20):
            for j in range(20):
                points.append(Point3D(i * 0.1, j * 0.1, 0))
        
        objects = self.od.detect(points)
        self.assertGreaterEqual(len(objects), 1)
        print(f"  [PASS] Detect: {len(objects)} objects")
    
    def test_detect_labels(self):
        """Should assign labels."""
        points = []
        for i in range(30):
            for j in range(30):
                for k in range(30):
                    points.append(Point3D(i * 0.5, j * 0.5, k * 0.5))
        
        objects = self.od.detect(points)
        if objects:
            self.assertIn(objects[0].label, ["small_debris", "medium_object", "large_structure"])
            print(f"  [PASS] Label: {objects[0].label}")


class TestFeatureExtractor(unittest.TestCase):
    """Test feature extractor."""
    
    def test_shape_features(self):
        """Should extract shape features."""
        fe = FeatureExtractor()
        points = [Point3D(0, 0, 0), Point3D(1, 2, 3), Point3D(2, 4, 6)]
        features = fe.extract_shape_features(points)
        self.assertIn("x_span", features)
        self.assertIn("volume", features)
        self.assertGreater(features["volume"], 0)
        print(f"  [PASS] Shape: vol={features['volume']:.1f}")
    
    def test_histogram_features(self):
        """Should extract histogram features."""
        fe = FeatureExtractor()
        points = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(2, 0, 0)]
        hist = fe.extract_histogram_features(points, bins=5)
        self.assertEqual(len(hist), 5)
        self.assertAlmostEqual(sum(hist), 1.0, places=5)
        print(f"  [PASS] Histogram: {len(hist)} bins")


class TestPerceptionPipeline(unittest.TestCase):
    """Test unified perception pipeline."""
    
    def setUp(self):
        self.pp = PerceptionPipeline(voxel_size=1.0)
    
    def test_process_frame(self):
        """Should process frame."""
        points = [Point3D(i * 0.1, j * 0.1, 0) for i in range(50) for j in range(50)]
        objects = self.pp.process_frame(points, max_distance=10.0)
        self.assertIsNotNone(objects)
        print(f"  [PASS] Frame: {len(objects)} objects")
    
    def test_get_features(self):
        """Should get features."""
        points = [Point3D(i * 0.1, j * 0.1, 0) for i in range(50) for j in range(50)]
        self.pp.process_frame(points)
        features = self.pp.get_features()
        self.assertIsInstance(features, list)
        print(f"  [PASS] Features: {len(features)} objects")
    
    def test_summary(self):
        """Should provide summary."""
        points = [Point3D(i * 0.1, j * 0.1, 0) for i in range(50) for j in range(50)]
        self.pp.process_frame(points)
        summary = self.pp.pipeline_summary()
        self.assertIn("objects_detected", summary)
        print(f"  [PASS] Summary: {summary['objects_detected']} objects")


class TestBoundingBox(unittest.TestCase):
    """Test bounding box."""
    
    def test_center(self):
        """Should compute center."""
        bbox = BoundingBox(0, 0, 0, 2, 4, 6)
        self.assertEqual(bbox.center(), (1.0, 2.0, 3.0))
        print("  [PASS] Center: (1, 2, 3)")
    
    def test_volume(self):
        """Should compute volume."""
        bbox = BoundingBox(0, 0, 0, 2, 3, 4)
        self.assertEqual(bbox.volume(), 24.0)
        print("  [PASS] Volume: 24")
    
    def test_contains(self):
        """Should check containment."""
        bbox = BoundingBox(0, 0, 0, 1, 1, 1)
        self.assertTrue(bbox.contains(Point3D(0.5, 0.5, 0.5)))
        self.assertFalse(bbox.contains(Point3D(2, 2, 2)))
        print("  [PASS] Contains: correct")


if __name__ == '__main__':
    unittest.main(verbosity=2)
