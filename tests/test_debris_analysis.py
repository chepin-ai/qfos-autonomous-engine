"""
Unit tests for debris analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from debris_analysis import (
    DebrisFluxModel, CollisionProbability, DebrisObject
)


class TestDebrisFluxModel(unittest.TestCase):
    """Test debris flux model."""
    
    def setUp(self):
        self.model = DebrisFluxModel()
    
    def test_flux_at_altitude(self):
        """Should compute flux at altitude."""
        flux = self.model.flux_at_altitude(altitude_km=800.0)
        self.assertGreater(flux, 0.0)
        print(f"  [PASS] Flux @800km: {flux:.2e} impacts/m2/yr")
    
    def test_flux_size_dependence(self):
        """Smaller particles should have higher flux."""
        flux_small = self.model.flux_at_altitude(800.0, particle_size_m=0.001)
        flux_large = self.model.flux_at_altitude(800.0, particle_size_m=0.1)
        self.assertGreater(flux_small, flux_large)
        print(f"  [PASS] Size: 1mm={flux_small:.2e}, 10cm={flux_large:.2e}")
    
    def test_directional_flux(self):
        """Should compute directional flux."""
        flux = self.model.flux_directional(altitude_km=800.0, inclination_deg=28.5)
        self.assertGreater(flux["total_flux_per_m2_yr"], 0.0)
        self.assertAlmostEqual(
            flux["prograde_fraction"] + flux["retrograde_fraction"] + flux["zenith_fraction"],
            1.0, delta=0.01
        )
        print(f"  [PASS] Directional: pro={flux['prograde_fraction']:.1f}, retro={flux['retrograde_fraction']:.1f}")


class TestCollisionProbability(unittest.TestCase):
    """Test collision probability calculations."""
    
    def setUp(self):
        self.collision = CollisionProbability(spacecraft_radius_m=5.0)
    
    def test_relative_geometry(self):
        """Should compute relative geometry."""
        pos1 = (6678.0, 0.0, 0.0)
        vel1 = (0.0, 7.725, 0.0)
        pos2 = (6678.0, 1.0, 0.0)
        vel2 = (0.0, 7.725, 0.1)
        
        geom = self.collision.compute_relative_geometry(pos1, vel1, pos2, vel2)
        self.assertGreater(geom.relative_velocity_km_s, 0.0)
        self.assertAlmostEqual(geom.miss_distance_km, 1.0, delta=0.01)
        print(f"  [PASS] Geometry: miss={geom.miss_distance_km:.3f}km, vrel={geom.relative_velocity_km_s:.4f}km/s")
    
    def test_patera_probability_zero_miss(self):
        """Zero miss distance should give higher probability."""
        p_zero = self.collision.patera_probability(0.0, 0.1, 1.0)
        p_far = self.collision.patera_probability(1.0, 0.1, 1.0)
        self.assertGreater(p_zero, p_far)
        print(f"  [PASS] Patera: b=0->{p_zero:.2e}, b=1km->{p_far:.2e}")
    
    def test_patera_probability_uncertainty_effect(self):
        """Larger uncertainty should increase probability."""
        p_small = self.collision.patera_probability(0.05, 0.01, 1.0)
        p_large = self.collision.patera_probability(0.05, 1.0, 1.0)
        # Larger uncertainty = less knowledge = higher collision probability
        self.assertGreater(p_large, p_small)
        print(f"  [PASS] Uncertainty: sigma=0.01->{p_small:.2e}, sigma=1.0->{p_large:.2e}")
    
    def test_poisson_collision_rate(self):
        """Should compute collision rate from flux."""
        p = self.collision.poisson_collision_rate(
            flux_per_m2_yr=1.0e-4,
            cross_sectional_area_m2=10.0
        )
        self.assertGreater(p, 0.0)
        self.assertLess(p, 1.0)
        print(f"  [PASS] Poisson: P={p:.2e}")
    
    def test_assess_conjunction(self):
        """Should assess conjunction."""
        primary_pos = (6678.0, 0.0, 0.0)
        primary_vel = (0.0, 7.725, 0.0)
        debris = DebrisObject(
            object_id="DEBRIS-001",
            position_km=(6678.0, 0.5, 0.0),
            velocity_km_s=(0.0, 7.7, 0.05),
            radar_cross_section_m2=2.0,
            diameter_m=0.5
        )
        
        assessment = self.collision.assess_conjunction(
            primary_pos, primary_vel, debris, position_uncertainty_km=0.05
        )
        
        self.assertEqual(assessment["secondary_id"], "DEBRIS-001")
        self.assertIn("risk_level", assessment)
        print(f"  [PASS] Conjunction: P={assessment['collision_probability']:.2e}, risk={assessment['risk_level']}")
    
    def test_screen_catalog(self):
        """Should screen debris catalog."""
        catalog = [
            DebrisObject(f"DEBRIS-{i:03d}", (6678.0, i*0.1, 0.0), (0.0, 7.7, 0.0), 1.0, 0.3)
            for i in range(20)
        ]
        
        threats = self.collision.screen_catalog(
            (6678.0, 0.0, 0.0), (0.0, 7.725, 0.0), catalog, threshold_p=1.0e-8
        )
        
        self.assertIsInstance(threats, list)
        print(f"  [PASS] Catalog: {len(threats)} threats from {len(catalog)} objects")


if __name__ == '__main__':
    unittest.main(verbosity=2)
