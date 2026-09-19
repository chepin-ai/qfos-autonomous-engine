"""
Unit tests for visual navigation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visual_navigation import (Feature, Landmark, FeatureMatcher,
                               VisualOdometry, LandmarkNavigator,
                               VisualNavigation)


class TestFeatureMatcher(unittest.TestCase):
    """Test feature matcher."""
    
    def setUp(self):
        self.fm = FeatureMatcher(threshold=0.8)
        self.f1 = [Feature(0, 100, 100, (1.0, 0.0, 0.5)),
                   Feature(1, 200, 150, (0.0, 1.0, 0.5))]
        self.f2 = [Feature(0, 102, 101, (1.0, 0.0, 0.5)),
                   Feature(1, 198, 152, (0.0, 1.0, 0.5))]
    
    def test_match(self):
        """Should match features."""
        matches = self.fm.match(self.f1, self.f2)
        self.assertGreater(len(matches), 0)
        print(f"  [PASS] Matches: {len(matches)}")
    
    def test_same_features(self):
        """Should match identical features."""
        matches = self.fm.match(self.f1, self.f1)
        self.assertEqual(len(matches), len(self.f1))
        print(f"  [PASS] Self-match: {len(matches)}")
    
    def test_count(self):
        """Should count matches."""
        n = self.fm.count_matches(self.f1, self.f2)
        self.assertGreater(n, 0)
        print(f"  [PASS] Count: {n}")


class TestVisualOdometry(unittest.TestCase):
    """Test visual odometry."""
    
    def setUp(self):
        self.vo = VisualOdometry(focal_length_px=500.0)
        self.matches = [
            (Feature(0, 100, 100, ()), Feature(0, 110, 100, ()), 0.1),
            (Feature(1, 200, 100, ()), Feature(1, 210, 100, ()), 0.1),
        ]
    
    def test_estimate_translation(self):
        """Should estimate translation."""
        t = self.vo.estimate_translation(self.matches, depth_scale=10.0)
        self.assertEqual(len(t), 3)
        self.assertNotEqual(t[0], 0)
        print(f"  [PASS] Translation: ({t[0]:.3f}, {t[1]:.3f}, {t[2]:.3f})")
    
    def test_estimate_rotation(self):
        """Should estimate rotation."""
        r = self.vo.estimate_rotation(self.matches)
        self.assertIsInstance(r, float)
        print(f"  [PASS] Rotation: {r:.4f} rad")


class TestLandmarkNavigator(unittest.TestCase):
    """Test landmark navigator."""
    
    def setUp(self):
        self.ln = LandmarkNavigator()
        lm = Landmark("LM1", (100, 0, 0))
        lm.features = [
            Feature(0, 50, 50, (1.0, 0.0, 0.0)),
            Feature(1, 60, 60, (0.0, 1.0, 0.0)),
            Feature(2, 70, 70, (0.0, 0.0, 1.0)),
        ]
        self.ln.add_landmark(lm)
    
    def test_add_landmark(self):
        """Should add landmark."""
        self.assertIn("LM1", self.ln.landmarks)
        print("  [PASS] Add: LM1")
    
    def test_recognize(self):
        """Should recognize landmark."""
        obs = [
            Feature(0, 50, 50, (1.0, 0.0, 0.0)),
            Feature(1, 60, 60, (0.0, 1.0, 0.0)),
            Feature(2, 70, 70, (0.0, 0.0, 1.0)),
        ]
        rec = self.ln.recognize(obs)
        self.assertIn("LM1", rec)
        print(f"  [PASS] Recognize: {rec}")
    
    def test_triangulate(self):
        """Should triangulate position."""
        pos = self.ln.triangulate_position([("LM1", 0.0, 10.0), ("LM1", 90.0, 10.0)])
        self.assertIsNotNone(pos)
        print(f"  [PASS] Triangulate: ({pos[0]:.1f}, {pos[1]:.1f})")


class TestVisualNavigation(unittest.TestCase):
    """Test unified visual navigation."""
    
    def setUp(self):
        self.vn = VisualNavigation()
        self.vn.add_landmark("LM1", (10, 0, 0), [
            Feature(0, 100, 100, (1.0, 0.0)),
            Feature(1, 110, 110, (0.5, 0.5)),
            Feature(2, 120, 120, (0.0, 1.0)),
        ])
    
    def test_extract_features(self):
        """Should extract features."""
        kps = [(100, 100), (200, 150)]
        features = self.vn.extract_features(kps)
        self.assertEqual(len(features), 2)
        print(f"  [PASS] Extract: {len(features)} features")
    
    def test_track_motion(self):
        """Should track motion."""
        f1 = [Feature(0, 100, 100, (1.0, 0.0)), Feature(1, 200, 100, (0.0, 1.0))]
        f2 = [Feature(0, 110, 100, (1.0, 0.0)), Feature(1, 210, 100, (0.0, 1.0))]
        motion = self.vn.track_motion(f1, f2, depth_scale=10.0)
        self.assertIn("dx", motion)
        self.assertIn("matches", motion)
        print(f"  [PASS] Motion: dx={motion['dx']:.3f}, matches={motion['matches']}")
    
    def test_localize(self):
        """Should localize."""
        obs = [
            Feature(0, 100, 100, (1.0, 0.0)),
            Feature(1, 110, 110, (0.5, 0.5)),
            Feature(2, 120, 120, (0.0, 1.0)),
        ]
        pos = self.vn.localize(obs)
        self.assertIsNotNone(pos)
        print(f"  [PASS] Localize: ({pos[0]:.1f}, {pos[1]:.1f})")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.vn.navigation_summary()
        self.assertIn("position", summary)
        self.assertEqual(summary["landmarks_in_map"], 1)
        print(f"  [PASS] Summary: {summary['landmarks_in_map']} landmarks")


if __name__ == '__main__':
    unittest.main(verbosity=2)
