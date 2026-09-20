"""
Unit tests for LiDAR processor module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lidar_processor import (PointClass, Point3D, PointCloudFilter,
                             GroundSegmentation, ObstacleDetector,
                             LiDARProcessor)


class TestPointCloudFilter(unittest.TestCase):
    """Test point cloud filter."""
    
    def setUp(self):
        self.pf = PointCloudFilter(range_min_m=0.5, range_max_m=50.0)
        self.points = [
            Point3D(1.0, 0.0, 0.0, intensity=100.0),
            Point3D(10.0, 0.0, 0.0, intensity=80.0),
            Point3D(100.0, 0.0, 0.0, intensity=50.0),
            Point3D(0.1, 0.0, 0.0, intensity=90.0),
        ]
    
    def test_range_filter(self):
        """Should filter by range."""
        filtered = self.pf.range_filter(self.points)
        self.assertEqual(len(filtered), 2)  # 1m and 10m only
        print(f"  [PASS] Range: {len(filtered)} points")
    
    def test_intensity_filter(self):
        """Should filter by intensity."""
        self.pf.intensity_min = 60.0
        filtered = self.pf.intensity_filter(self.points)
        self.assertEqual(len(filtered), 3)
        print(f"  [PASS] Intensity: {len(filtered)} points")
    
    def test_statistical_removal(self):
        """Should remove outliers."""
        # Dense cluster + sparse outliers
        pts = [Point3D(i*0.01, 0.0, 0.0) for i in range(50)]
        pts.append(Point3D(10.0, 0.0, 0.0))
        pts.append(Point3D(-10.0, 0.0, 0.0))
        filtered = self.pf.statistical_outlier_removal(pts, k_neighbors=10, std_dev_threshold=1.0)
        # Should keep most inliers, may remove some outliers
        self.assertGreaterEqual(len(filtered), 45)
        print(f"  [PASS] SOR: {len(filtered)} / {len(pts)}")
    
    def test_filter_all(self):
        """Should apply all filters."""
        filtered = self.pf.filter_all(self.points)
        self.assertLessEqual(len(filtered), len(self.points))
        print(f"  [PASS] All: {len(filtered)} points")


class TestGroundSegmentation(unittest.TestCase):
    """Test ground segmentation."""
    
    def setUp(self):
        self.gs = GroundSegmentation(ground_threshold_m=0.1)
        self.points = [
            Point3D(0.5, 0.5, 0.0), Point3D(0.5, 0.5, 1.0),
            Point3D(1.5, 1.5, 0.0), Point3D(1.5, 1.5, 2.0),
            Point3D(2.5, 2.5, 0.1), Point3D(2.5, 2.5, 1.5),
        ]
    
    def test_find_ground(self):
        """Should find ground points."""
        ground = self.gs.find_ground_plane(self.points, grid_size_m=1.0)
        self.assertGreater(len(ground), 0)
        # Ground points should have low z
        for p in ground:
            self.assertLess(p.z, 0.5)
        print(f"  [PASS] Ground: {len(ground)} points")
    
    def test_segment(self):
        """Should segment ground and non-ground."""
        ground, non_ground = self.gs.segment(self.points)
        self.assertGreater(len(ground), 0)
        self.assertGreater(len(non_ground), 0)
        print(f"  [PASS] Segment: {len(ground)}g / {len(non_ground)}ng")


class TestObstacleDetector(unittest.TestCase):
    """Test obstacle detector."""
    
    def setUp(self):
        self.od = ObstacleDetector(min_obstacle_height_m=0.5)
    
    def test_cluster_points(self):
        """Should cluster points."""
        points = [
            Point3D(0.0, 0.0, 1.0), Point3D(0.2, 0.0, 1.0),
            Point3D(5.0, 0.0, 2.0), Point3D(5.2, 0.0, 2.0),
        ]
        clusters = self.od.cluster_points(points)
        self.assertEqual(len(clusters), 2)
        print(f"  [PASS] Clusters: {len(clusters)}")
    
    def test_detect_obstacles(self):
        """Should detect obstacles."""
        points = [
            Point3D(0.0, 0.0, 0.0), Point3D(0.5, 0.0, 0.0),
            Point3D(0.0, 0.5, 0.0), Point3D(0.5, 0.5, 1.5),
            Point3D(0.0, 0.0, 1.0), Point3D(0.5, 0.0, 1.0),
            Point3D(0.0, 0.5, 1.0), Point3D(0.5, 0.5, 1.0),
        ]
        obstacles = self.od.detect_obstacles(points)
        self.assertGreater(len(obstacles), 0)
        print(f"  [PASS] Obstacles: {len(obstacles)}")
    
    def test_min_height_filter(self):
        """Should filter by height."""
        points = [
            Point3D(0.0, 0.0, 0.0), Point3D(0.5, 0.0, 0.0),
            Point3D(0.0, 0.0, 0.2), Point3D(0.5, 0.0, 0.2),
        ]
        obstacles = self.od.detect_obstacles(points)
        # Height is only 0.2m, below 0.5m threshold
        self.assertEqual(len(obstacles), 0)
        print(f"  [PASS] Height filter: {len(obstacles)} obstacles")


class TestLiDARProcessor(unittest.TestCase):
    """Test unified LiDAR processor."""
    
    def setUp(self):
        self.lp = LiDARProcessor()
        self.cloud = [
            Point3D(1.0, 0.0, 0.0, intensity=100.0),
            Point3D(1.0, 0.0, 1.5, intensity=100.0),
            Point3D(2.0, 0.0, 0.0, intensity=100.0),
            Point3D(2.0, 0.0, 2.0, intensity=100.0),
            Point3D(3.0, 0.0, 0.1, intensity=100.0),
            Point3D(3.0, 0.0, 1.0, intensity=100.0),
        ]
    
    def test_process(self):
        """Should process point cloud."""
        result = self.lp.process(self.cloud)
        self.assertIn("raw_points", result)
        self.assertIn("obstacles", result)
        self.assertEqual(result["raw_points"], 6)
        print(f"  [PASS] Process: {result['raw_points']} -> {result['filtered_points']} points, {result['obstacle_count']} obstacles")
    
    def test_set_params(self):
        """Should set filter params."""
        self.lp.set_filter_params(0.5, 100.0, 50.0)
        self.assertEqual(self.lp.filter.range_max, 100.0)
        print("  [PASS] Params set")
    
    def test_summary(self):
        """Should provide summary."""
        self.lp.process(self.cloud)
        summary = self.lp.processing_summary()
        self.assertEqual(summary["processed_frames"], 1)
        print(f"  [PASS] Summary: {summary['processed_frames']} frames")


if __name__ == '__main__':
    unittest.main(verbosity=2)
