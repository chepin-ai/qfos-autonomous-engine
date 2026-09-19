"""
Unit tests for spacecraft system module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from spacecraft_system import SpacecraftSimulator, SpacecraftState, MissionPhase


class TestSpacecraftSimulator(unittest.TestCase):
    """Test spacecraft system simulator."""
    
    def setUp(self):
        state = SpacecraftState(
            position_km=(6678.0, 0.0, 0.0),
            velocity_km_s=(0.0, 7.725, 0.0),
            total_mass_kg=500.0,
            propellant_mass_kg=100.0
        )
        self.sim = SpacecraftSimulator(state)
    
    def test_initialization(self):
        """Should initialize correctly."""
        self.assertEqual(self.sim.state.total_mass_kg, 500.0)
        self.assertEqual(self.sim.state.phase, MissionPhase.LAUNCH)
        print("  [PASS] Initialization")
    
    def test_propagate_orbit(self):
        """Should propagate orbit."""
        initial_pos = self.sim.state.position_km
        self.sim.propagate_orbit(60.0)
        new_pos = self.sim.state.position_km
        self.assertNotEqual(new_pos, initial_pos)
        print(f"  [PASS] Orbit propagation: ({new_pos[0]:.2f}, {new_pos[1]:.2f}, {new_pos[2]:.2f})")
    
    def test_update_power(self):
        """Should update power state."""
        self.sim.state.power_consumption_w = 200.0
        self.sim.update_power(3600.0, solar_distance_au=1.0, eclipse=False)
        self.assertGreater(self.sim.state.solar_power_w, 0.0)
        print(f"  [PASS] Power: solar={self.sim.state.solar_power_w:.1f}W, SOC={self.sim.state.battery_soc:.3f}")
    
    def test_update_thermal(self):
        """Should update thermal state."""
        initial_temp = self.sim.state.temperature_c
        self.sim.update_thermal(3600.0, solar_flux_w_m2=1361.0)
        # Temperature should change
        self.assertNotEqual(self.sim.state.temperature_c, initial_temp)
        print(f"  [PASS] Thermal: {initial_temp:.1f}C -> {self.sim.state.temperature_c:.1f}C")
    
    def test_execute_maneuver(self):
        """Should execute propulsive maneuver."""
        initial_mass = self.sim.state.total_mass_kg
        initial_prop = self.sim.state.propellant_mass_kg
        self.sim.execute_maneuver((10.0, 0.0, 0.0), isp_s=300.0)
        self.assertLess(self.sim.state.total_mass_kg, initial_mass)
        self.assertLess(self.sim.state.propellant_mass_kg, initial_prop)
        print(f"  [PASS] Maneuver: mass {initial_mass:.2f} -> {self.sim.state.total_mass_kg:.2f} kg")
    
    def test_maneuver_insufficient_propellant(self):
        """Should raise on insufficient propellant."""
        self.sim.state.propellant_mass_kg = 1.0
        with self.assertRaises(ValueError):
            self.sim.execute_maneuver((1000.0, 0.0, 0.0), isp_s=300.0)
        print("  [PASS] Insufficient propellant raises error")
    
    def test_collect_science(self):
        """Should collect science data."""
        self.sim.collect_science_data(500.0)
        self.assertEqual(self.sim.state.data_storage_mb, 500.0)
        print("  [PASS] Science data: 500 MB collected")
    
    def test_downlink(self):
        """Should downlink data."""
        self.sim.state.data_storage_mb = 1000.0
        downlinked = self.sim.downlink_data(rate_mbps=10.0, duration_s=100.0)
        self.assertGreater(downlinked, 0.0)
        self.assertLess(self.sim.state.data_storage_mb, 1000.0)
        print(f"  [PASS] Downlink: {downlinked:.1f} MB, remaining={self.sim.state.data_storage_mb:.1f} MB")
    
    def test_check_health(self):
        """Should check health."""
        health = self.sim.check_health()
        self.assertIn("overall", health)
        self.assertIn("subsystems", health)
        print(f"  [PASS] Health: {health['overall']}")
    
    def test_check_health_low_battery(self):
        """Should detect low battery."""
        self.sim.state.battery_soc = 0.1
        health = self.sim.check_health()
        self.assertEqual(health["overall"], "warning")
        print("  [PASS] Low battery detected")
    
    def test_simulate_timestep(self):
        """Should execute full timestep."""
        initial_time = self.sim.state.elapsed_time_s
        self.sim.simulate_timestep(dt_s=60.0, solar_distance_au=1.0)
        self.assertEqual(self.sim.state.elapsed_time_s, initial_time + 60.0)
        print(f"  [PASS] Timestep: t={self.sim.state.elapsed_time_s:.0f}s")
    
    def test_get_summary(self):
        """Should provide summary."""
        summary = self.sim.get_summary()
        self.assertIn("mass_kg", summary)
        self.assertIn("health", summary)
        print(f"  [PASS] Summary: mass={summary['mass_kg']}kg, health={summary['health']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
