"""
Unit tests for landing guidance module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from landing_guidance import (LandingSite, HazardDetector,
                              PoweredDescent, TerrainRelativeNav,
                              LandingGuidance)


class TestHazardDetector(unittest.TestCase):
    """Test hazard detector."""
    
    def setUp(self):
        self.hd = HazardDetector(max_slope_deg=15.0, max_roughness=0.3)
    
    def test_safe_site(self):
        """Should score safe site highly."""
        site = LandingSite(0, 0, 0, 5.0, 0.1, 0.0)
        score = self.hd.assess_site(site)
        self.assertGreater(score, 0.75)
        print(f"  [PASS] Safe: {score:.2f}")
    
    def test_unsafe_site(self):
        """Should score unsafe site low."""
        site = LandingSite(0, 0, 0, 30.0, 0.5, 0.8)
        score = self.hd.assess_site(site)
        self.assertLess(score, 0.5)
        print(f"  [PASS] Unsafe: {score:.2f}")
    
    def test_is_safe(self):
        """Should classify safety."""
        safe = LandingSite(0, 0, 0, 5.0, 0.1, 0.0)
        unsafe = LandingSite(0, 0, 0, 30.0, 0.5, 0.8)
        self.assertTrue(self.hd.is_safe(safe))
        self.assertFalse(self.hd.is_safe(unsafe))
        print("  [PASS] Classify: True/False")
    
    def test_rank(self):
        """Should rank sites."""
        sites = [
            LandingSite(0, 0, 0, 5.0, 0.1, 0.0),
            LandingSite(0, 0, 0, 20.0, 0.4, 0.3),
            LandingSite(0, 0, 0, 10.0, 0.2, 0.1),
        ]
        ranked = self.hd.rank_sites(sites)
        self.assertGreater(ranked[0][1], ranked[-1][1])
        print(f"  [PASS] Rank: best={ranked[0][1]:.2f}")


class TestPoweredDescent(unittest.TestCase):
    """Test powered descent."""
    
    def setUp(self):
        self.pd = PoweredDescent(g=1.62, max_thrust=45000.0,
                                 dry_mass=2000.0, isp=310.0)
    
    def test_delta_v(self):
        """Should estimate delta-v."""
        dv = self.pd.delta_v_budget(1000, 100)
        self.assertGreater(dv, 100)
        print(f"  [PASS] DV: {dv:.1f} m/s")
    
    def test_fuel(self):
        """Should estimate fuel."""
        fuel = self.pd.fuel_required(500, 5000)
        self.assertGreater(fuel, 0)
        self.assertLess(fuel, 5000)
        print(f"  [PASS] Fuel: {fuel:.1f} kg")
    
    def test_thrust_profile(self):
        """Should compute thrust."""
        thrust, angle = self.pd.thrust_profile(50, 20, 4000)
        self.assertGreater(thrust, 0)
        self.assertLessEqual(thrust, 45000)
        self.assertGreaterEqual(angle, 0)
        print(f"  [PASS] Thrust: {thrust:.0f}N @ {angle:.1f}deg")
    
    def test_time_to_land(self):
        """Should estimate landing time."""
        t = self.pd.time_to_land(100, 10)
        self.assertEqual(t, 10.0)
        print(f"  [PASS] Time: {t:.1f}s")


class TestTerrainRelativeNav(unittest.TestCase):
    """Test terrain-relative nav."""
    
    def setUp(self):
        self.trn = TerrainRelativeNav(map_resolution=10.0)
        # Flat terrain
        for x in range(-5, 6):
            for y in range(-5, 6):
                self.trn.add_terrain_point(x*10, y*10, 0.0)
        # Slope
        self.trn.add_terrain_point(60, 0, 10.0)
    
    def test_get_elevation(self):
        """Should get elevation."""
        h = self.trn.get_elevation(0, 0)
        self.assertEqual(h, 0.0)
        print(f"  [PASS] Elevation: {h}")
    
    def test_estimate_slope_flat(self):
        """Should estimate flat slope."""
        slope = self.trn.estimate_slope(0, 0)
        self.assertAlmostEqual(slope, 0.0, places=1)
        print(f"  [PASS] Flat slope: {slope:.2f}deg")
    
    def test_estimate_slope_raised(self):
        """Should detect slope."""
        slope = self.trn.estimate_slope(50, 0)
        self.assertGreater(slope, 0)
        print(f"  [PASS] Slope: {slope:.2f}deg")


class TestLandingGuidance(unittest.TestCase):
    """Test unified landing guidance."""
    
    def setUp(self):
        self.lg = LandingGuidance()
        self.lg.add_terrain_data(0, 0, 0)
        self.lg.add_terrain_data(100, 0, 0)
    
    def test_select_site(self):
        """Should select safe site."""
        sites = [
            LandingSite(0, 0, 0, 5.0, 0.1, 0.0),
            LandingSite(0, 0, 0, 25.0, 0.5, 0.6),
        ]
        best = self.lg.select_landing_site(sites)
        self.assertIsNotNone(best)
        self.assertAlmostEqual(best.slope_deg, 5.0)
        print(f"  [PASS] Select: slope={best.slope_deg}")
    
    def test_compute_guidance(self):
        """Should compute guidance."""
        self.lg.update_state(500, 30, 4000)
        cmd = self.lg.compute_guidance()
        self.assertIn("thrust", cmd)
        self.assertIn("fuel_required", cmd)
        self.assertGreater(cmd["thrust"], 0)
        print(f"  [PASS] Guidance: thrust={cmd['thrust']:.0f}N")
    
    def test_summary(self):
        """Should provide summary."""
        self.lg.update_state(100, 10, 3000)
        summary = self.lg.guidance_summary()
        self.assertEqual(summary["altitude"], 100)
        print(f"  [PASS] Summary: alt={summary['altitude']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
