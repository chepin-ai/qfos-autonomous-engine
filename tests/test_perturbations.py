"""
Unit tests for orbit perturbations module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from perturbations import (
    PerturbationModel, EarthGravityModel, AtmosphereParams
)


class TestPerturbationModel(unittest.TestCase):
    """Test perturbation models."""
    
    def setUp(self):
        self.model = PerturbationModel()
    
    def test_j2_acceleration(self):
        """Should compute J2 acceleration."""
        pos = (6678.0, 0.0, 0.0)  # LEO
        ax, ay, az = self.model.j2_acceleration(pos)
        self.assertNotEqual(ax, 0.0)
        print(f"  [PASS] J2: ({ax:.6f}, {ay:.6f}, {az:.6f}) m/s^2")
    
    def test_j2_direction(self):
        """J2 should be small at equator."""
        pos = (6678.0, 0.0, 0.0)
        ax, ay, az = self.model.j2_acceleration(pos)
        # At equator, z-acceleration should be small
        self.assertAlmostEqual(az, 0.0, delta=0.01)
        print(f"  [PASS] J2 equator: az={az:.6f}")
    
    def test_j3_acceleration(self):
        """Should compute J3 acceleration."""
        pos = (6678.0, 0.0, 1000.0)
        ax, ay, az = self.model.j3_acceleration(pos)
        print(f"  [PASS] J3: ({ax:.6f}, {ay:.6f}, {az:.6f}) m/s^2")
    
    def test_atmospheric_drag(self):
        """Should compute drag acceleration."""
        pos = (6678.0, 0.0, 0.0)
        vel = (0.0, 7.725, 0.0)
        atm = AtmosphereParams(density_kg_m3=1.0e-12, cd=2.2, area_m2=2.0, mass_kg=500.0)
        ax, ay, az = self.model.atmospheric_drag(pos, vel, atm)
        self.assertLess(ay, 0.0)  # Opposite to velocity
        print(f"  [PASS] Drag: ({ax:.8f}, {ay:.8f}, {az:.8f}) m/s^2")
    
    def test_third_body_sun(self):
        """Should compute Sun third-body acceleration."""
        pos = (6678.0, 0.0, 0.0)
        sun_pos = (149600000.0, 0.0, 0.0)  # ~1 AU
        ax, ay, az = self.model.third_body_acceleration(pos, sun_pos, self.model.MU_SUN_KM3_S2)
        self.assertNotEqual(ax, 0.0)
        print(f"  [PASS] Sun 3rd body: ({ax:.8f}, {ay:.8f}, {az:.8f}) m/s^2")
    
    def test_third_body_moon(self):
        """Should compute Moon third-body acceleration."""
        pos = (6678.0, 0.0, 0.0)
        moon_pos = (384400.0, 0.0, 0.0)
        ax, ay, az = self.model.third_body_acceleration(pos, moon_pos, self.model.MU_MOON_KM3_S2)
        self.assertNotEqual(ax, 0.0)
        print(f"  [PASS] Moon 3rd body: ({ax:.8f}, {ay:.8f}, {az:.8f}) m/s^2")
    
    def test_solar_radiation_pressure(self):
        """Should compute SRP acceleration."""
        pos = (6678.0, 0.0, 0.0)
        sun_pos = (149600000.0, 0.0, 0.0)
        ax, ay, az = self.model.solar_radiation_pressure(pos, sun_pos, spacecraft_area_m2=2.0, mass_kg=500.0)
        self.assertGreater(ax, 0.0)  # Away from Sun
        print(f"  [PASS] SRP: ({ax:.10f}, {ay:.10f}, {az:.10f}) m/s^2")
    
    def test_total_perturbations(self):
        """Should compute total perturbations."""
        pos = (6678.0, 0.0, 0.0)
        vel = (0.0, 7.725, 0.0)
        result = self.model.total_perturbations(pos, vel, include_j2=True)
        self.assertIn("total", result)
        self.assertIn("components", result)
        self.assertGreater(result["total_magnitude_ms2"], 0.0)
        print(f"  [PASS] Total: {result['total_magnitude_ms2']:.6f} m/s^2")
    
    def test_density_model(self):
        """Should return density for altitude ranges."""
        rho_leo = PerturbationModel.density_harris_priester(300.0)
        rho_high = PerturbationModel.density_harris_priester(1000.0)
        self.assertGreater(rho_leo, rho_high)
        print(f"  [PASS] Density: LEO={rho_leo:.2e}, high={rho_high:.2e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
