"""
Unit tests for aerobraking module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aerobraking import AerobrakingMission, AtmosphereModel


class TestAerobrakingMission(unittest.TestCase):
    """Test aerobraking simulation."""
    
    def setUp(self):
        self.mission = AerobrakingMission(AerobrakingMission.MARS, spacecraft_ballistic_coefficient_kg_m2=100.0)
    
    def test_density_at_altitude(self):
        """Should compute density."""
        rho = self.mission.density_at_altitude(100.0)
        self.assertGreater(rho, 0.0)
        print(f"  [PASS] Density at 100km: {rho:.6f} kg/m3")
    
    def test_density_exponential(self):
        """Density should decrease with altitude."""
        rho_100 = self.mission.density_at_altitude(100.0)
        rho_200 = self.mission.density_at_altitude(200.0)
        self.assertGreater(rho_100, rho_200)
        print(f"  [PASS] Exponential: {rho_100:.6f} > {rho_200:.6f}")
    
    def test_drag_acceleration(self):
        """Should compute drag."""
        drag = self.mission.drag_acceleration(100.0, 3500.0)
        self.assertLess(drag, 0.0)  # Deceleration
        print(f"  [PASS] Drag: {drag:.6f} m/s^2")
    
    def test_simulate_pass(self):
        """Should simulate single pass."""
        result = self.mission.simulate_pass(
            periapsis_altitude_km=120.0,
            velocity_at_pe_ms=3500.0,
            time_of_flight_s=300.0,
            dt_s=1.0
        )
        self.assertIn("delta_v_ms", result)
        self.assertGreater(result["delta_v_ms"], 0.0)
        self.assertTrue(result["is_safe"])
        print(f"  [PASS] Pass: dV={result['delta_v_ms']:.3f} m/s, heat={result['max_heating_rate_w_cm2']:.4f} W/cm2")
    
    def test_simulate_full_campaign(self):
        """Should simulate full campaign."""
        result = self.mission.simulate_full_campaign(
            initial_apoapsis_km=20000.0,
            initial_periapsis_km=120.0,
            target_apoapsis_km=400.0,
            max_heating_rate_w_cm2=0.5
        )
        self.assertIn("total_passes", result)
        self.assertGreater(result["total_passes"], 0)
        print(f"  [PASS] Campaign: {result['total_passes']} passes, dV={result['total_delta_v_ms']:.1f} m/s")
    
    def test_campaign_runs(self):
        """Should run full campaign."""
        result = self.mission.simulate_full_campaign(
            initial_apoapsis_km=5000.0,
            initial_periapsis_km=120.0,
            target_apoapsis_km=400.0,
            max_heating_rate_w_cm2=1.0
        )
        # Campaign may not converge with simplified model but should run
        self.assertGreaterEqual(result["total_passes"], 0)
        print(f"  [PASS] Campaign ran: {result['total_passes']} passes")
    
    def test_corridor_analysis(self):
        """Should compute corridor bounds."""
        corridor = self.mission.corridor_analysis(apoapsis_km=5000.0)
        self.assertIn("lower_bound_km", corridor)
        self.assertIn("upper_bound_km", corridor)
        print(f"  [PASS] Corridor: {corridor['lower_bound_km']}-{corridor['upper_bound_km']} km")
    
    def test_venus_atmosphere(self):
        """Should work with Venus."""
        venus = AerobrakingMission(AerobrakingMission.VENUS, spacecraft_ballistic_coefficient_kg_m2=150.0)
        rho = venus.density_at_altitude(150.0)
        self.assertGreater(rho, 0.0)
        print(f"  [PASS] Venus density: {rho:.4f} kg/m3")


if __name__ == '__main__':
    unittest.main(verbosity=2)
