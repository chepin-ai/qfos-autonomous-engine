"""
Unit tests for landing site selection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from landing_site_selector import LandingSiteSelector, LandingSite


class TestLandingSiteSelector(unittest.TestCase):
    """Test landing site selector."""
    
    def setUp(self):
        self.selector = LandingSiteSelector(
            max_slope_deg=15.0, max_roughness_m=0.5, min_illumination_hours=8.0
        )
        for site in LandingSiteSelector.create_mars_candidates():
            self.selector.add_candidate(site)
    
    def test_safety_score(self):
        """Should compute safety score."""
        site = LandingSite("Flat", 0.0, 0.0, 0.0, 2.0, 0.1)
        score = self.selector.safety_score(site)
        self.assertGreater(score, 0.8)
        print(f"  [PASS] Safe site: {score:.2f}")
    
    def test_safety_score_unsafe(self):
        """Should score unsafe site low."""
        site = LandingSite("Steep", 0.0, 0.0, 0.0, 30.0, 2.0)
        score = self.selector.safety_score(site)
        self.assertLess(score, 0.5)
        print(f"  [PASS] Unsafe site: {score:.2f}")
    
    def test_illumination_score(self):
        """Should score illumination."""
        site = LandingSite("Bright", 0.0, 0.0, 0.0, 1.0, 0.1, illumination_hours=14.0)
        score = self.selector.illumination_score(site)
        self.assertEqual(score, 1.0)
        print("  [PASS] Full illumination: 1.0")
    
    def test_illumination_score_low(self):
        """Should score low illumination."""
        site = LandingSite("Dark", 0.0, 0.0, 0.0, 1.0, 0.1, illumination_hours=4.0)
        score = self.selector.illumination_score(site)
        self.assertEqual(score, 0.0)
        print("  [PASS] Low illumination: 0.0")
    
    def test_overall_score(self):
        """Should compute overall score."""
        site = LandingSite("Good", 0.0, 0.0, 0.0, 3.0, 0.1,
                          illumination_hours=12.0, science_value=0.9, accessibility_score=0.8)
        score = self.selector.overall_score(site)
        self.assertGreater(score, 0.5)
        print(f"  [PASS] Overall: {score:.3f}")
    
    def test_evaluate_all(self):
        """Should evaluate all sites."""
        results = self.selector.evaluate_all()
        self.assertEqual(len(results), 6)
        self.assertGreater(results[0]["overall_score"], results[-1]["overall_score"])
        print(f"  [PASS] Ranked: {results[0]['name']}={results[0]['overall_score']:.3f}")
    
    def test_filter_safe(self):
        """Should filter safe sites."""
        safe = self.selector.filter_safe(min_score=0.5)
        self.assertGreater(len(safe), 0)
        print(f"  [PASS] Safe sites: {len(safe)}/6")
    
    def test_site_separation(self):
        """Should compute separation."""
        s1 = LandingSite("A", 0.0, 0.0, 0.0, 1.0, 0.1)
        s2 = LandingSite("B", 1.0, 0.0, 0.0, 1.0, 0.1)
        sep = self.selector.site_separation_km(s1, s2)
        self.assertGreater(sep, 50.0)
        print(f"  [PASS] Separation: {sep:.1f} km")
    
    def test_diversity_selection(self):
        """Should select diverse sites."""
        selected = self.selector.diversity_selection(num_sites=3, min_separation_km=10.0)
        self.assertGreaterEqual(len(selected), 1)
        print(f"  [PASS] Selected: {len(selected)} sites")
    
    def test_landing_ellipse(self):
        """Should assess ellipse."""
        site = LandingSite("Flat", 0.0, 0.0, 0.0, 3.0, 0.1)
        ellipse = self.selector.landing_ellipse_feasibility(site)
        self.assertTrue(ellipse["feasible"])
        print(f"  [PASS] Ellipse: {ellipse['ellipse_area_km2']:.1f} km2")
    
    def test_mars_candidates(self):
        """Should create Mars candidates."""
        candidates = LandingSiteSelector.create_mars_candidates()
        self.assertEqual(len(candidates), 6)
        print(f"  [PASS] Mars candidates: {len(candidates)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
