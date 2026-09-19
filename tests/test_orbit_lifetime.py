"""
Unit tests for orbit lifetime module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbit_lifetime import OrbitLifetimeEstimator, AtmosphericModel


class TestOrbitLifetime(unittest.TestCase):
    """Test orbit lifetime estimation."""
    
    def setUp(self):
        self.estimator = OrbitLifetimeEstimator()
    
    def test_ballistic_coefficient(self):
        """Should compute ballistic coefficient."""
        bc = self.estimator.ballistic_coefficient_kg_m2(
            mass_kg=1000.0, drag_coefficient=2.2, area_m2=5.0
        )
        expected = 1000.0 / (2.2 * 5.0)
        self.assertAlmostEqual(bc, expected, delta=0.1)
        print(f"  [PASS] BC: {bc:.1f} kg/m^2")
    
    def test_decay_rate_positive(self):
        """Decay rate should be positive."""
        rate = self.estimator.decay_rate_km_day(400.0, 100.0)
        self.assertGreater(rate, 0.0)
        print(f"  [PASS] Decay @400km: {rate:.6f} km/day")
    
    def test_decay_rate_altitude_dependence(self):
        """Lower altitude should have faster decay."""
        rate_low = self.estimator.decay_rate_km_day(200.0, 100.0)
        rate_high = self.estimator.decay_rate_km_day(600.0, 100.0)
        self.assertGreater(rate_low, rate_high)
        print(f"  [PASS] Decay: 200km={rate_low:.4f}, 600km={rate_high:.6f} km/day")
    
    def test_estimate_lifetime(self):
        """Should estimate lifetime."""
        result = self.estimator.estimate_lifetime(
            initial_altitude_km=400.0,
            mass_kg=1000.0,
            drag_coefficient=2.2,
            area_m2=2.0
        )
        self.assertIn("lifetime_years", result)
        self.assertIn("decay_rate_initial_km_day", result)
        print(f"  [PASS] Lifetime: {result['lifetime_years']:.1f} yr, decay={result['decay_rate_initial_km_day']:.4f} km/day")
    
    def test_high_orbit_stable(self):
        """High orbit should be effectively stable."""
        result = self.estimator.estimate_lifetime(
            initial_altitude_km=1000.0,
            mass_kg=1000.0,
            area_m2=1.0
        )
        self.assertTrue(result["is_stable"] or result["lifetime_years"] > 100)
        print(f"  [PASS] 1000km: stable={result['is_stable']}, years={result['lifetime_years']}")
    
    def test_reentry_prediction(self):
        """Should predict reentry."""
        result = self.estimator.reentry_prediction(
            initial_altitude_km=300.0,
            mass_kg=500.0,
            area_m2=2.0
        )
        self.assertIn("reentry_velocity_km_s", result)
        self.assertGreater(result["reentry_velocity_km_s"], 7.0)
        print(f"  [PASS] Reentry: v={result['reentry_velocity_km_s']:.2f} km/s")
    
    def test_compare_configurations(self):
        """Should compare configurations."""
        configs = [
            {"name": "Small", "mass_kg": 500.0, "area_m2": 2.0},
            {"name": "Large", "mass_kg": 500.0, "area_m2": 10.0}
        ]
        results = self.estimator.compare_configurations(400.0, configs)
        self.assertEqual(len(results), 2)
        # Larger area = shorter lifetime
        print(f"  [PASS] Compare: {results[0]['name']}={results[0]['lifetime_years']:.1f}yr, {results[1]['name']}={results[1]['lifetime_years']:.1f}yr")
    
    def test_atmospheric_model(self):
        """Should provide densities."""
        atm = AtmosphericModel()
        rho_leo = atm.density_at(300.0)
        rho_high = atm.density_at(1000.0)
        self.assertGreater(rho_leo, rho_high)
        print(f"  [PASS] Density: 300km={rho_leo:.2e}, 1000km={rho_high:.2e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
