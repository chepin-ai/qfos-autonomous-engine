"""
Unit tests for launch vehicle module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from launch_vehicle import LaunchVehicle


class TestLaunchVehicle(unittest.TestCase):
    """Test launch vehicle performance."""
    
    def test_falcon_9_leo(self):
        """Falcon 9 should have reasonable LEO payload."""
        f9 = LaunchVehicle.falcon_9()
        payload = f9.payload_to_leo()
        self.assertGreater(payload, 20000.0)
        self.assertLess(payload, 25000.0)
        print(f"  [PASS] Falcon 9 LEO: {payload:.0f} kg")
    
    def test_falcon_9_gto(self):
        """Falcon 9 should have reasonable GTO payload."""
        f9 = LaunchVehicle.falcon_9()
        payload = f9.payload_to_gto()
        self.assertGreater(payload, 8000.0)
        self.assertLess(payload, 8500.0)
        print(f"  [PASS] Falcon 9 GTO: {payload:.0f} kg")
    
    def test_falcon_heavy_leo(self):
        """Falcon Heavy should have higher payload than F9."""
        fh = LaunchVehicle.falcon_heavy()
        f9 = LaunchVehicle.falcon_9()
        self.assertGreater(fh.payload_to_leo(), f9.payload_to_leo())
        print(f"  [PASS] FH LEO: {fh.payload_to_leo():.0f} kg > F9: {f9.payload_to_leo():.0f} kg")
    
    def test_inclination_penalty(self):
        """Higher inclination should reduce payload."""
        f9 = LaunchVehicle.falcon_9()
        payload_equatorial = f9.payload_to_leo(inclination_deg=28.5)
        payload_sso = f9.payload_to_leo(inclination_deg=98.0)
        self.assertGreater(payload_equatorial, payload_sso)
        print(f"  [PASS] Inclination penalty: 28.5deg={payload_equatorial:.0f}, 98deg={payload_sso:.0f} kg")
    
    def test_altitude_penalty(self):
        """Higher altitude should reduce payload."""
        f9 = LaunchVehicle.falcon_9()
        payload_200 = f9.payload_to_leo(altitude_km=200.0)
        payload_600 = f9.payload_to_leo(altitude_km=600.0)
        self.assertGreater(payload_200, payload_600)
        print(f"  [PASS] Altitude penalty: 200km={payload_200:.0f}, 600km={payload_600:.0f} kg")
    
    def test_mission_analysis(self):
        """Should analyze mission feasibility."""
        f9 = LaunchVehicle.falcon_9()
        analysis = f9.mission_analysis(
            target_mass_kg=5000.0,
            target_altitude_km=400.0,
            target_inclination_deg=51.6
        )
        self.assertTrue(analysis["feasible"])
        self.assertGreater(analysis["margin_kg"], 0.0)
        print(f"  [PASS] Mission: {analysis['capacity_kg']:.0f} kg capacity, {analysis['margin_kg']:.0f} kg margin")
    
    def test_mission_infeasible(self):
        """Should detect infeasible missions."""
        f9 = LaunchVehicle.falcon_9()
        analysis = f9.mission_analysis(
            target_mass_kg=50000.0,
            target_altitude_km=200.0,
            target_inclination_deg=28.5
        )
        self.assertFalse(analysis["feasible"])
        print(f"  [PASS] Infeasible: margin={analysis['margin_kg']:.0f} kg")
    
    def test_compare_vehicles(self):
        """Should compare vehicles."""
        vehicles = [LaunchVehicle.falcon_9(), LaunchVehicle.falcon_heavy()]
        comparison = LaunchVehicle.compare_vehicles(vehicles, 400.0, 51.6)
        self.assertEqual(len(comparison), 2)
        self.assertGreater(comparison[0]["capacity_kg"], comparison[1]["capacity_kg"])
        print(f"  [PASS] Compare: {comparison[0]['name']}={comparison[0]['capacity_kg']:.0f} kg")
    
    def test_ariane_64(self):
        """Ariane 64 should have GTO payload."""
        a64 = LaunchVehicle.ariane_64()
        self.assertGreater(a64.gto_payload_kg, 10000.0)
        print(f"  [PASS] Ariane 64 GTO: {a64.gto_payload_kg:.0f} kg")


if __name__ == '__main__':
    unittest.main(verbosity=2)
