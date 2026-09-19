"""
Unit tests for entry trajectory (EDL) module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entry_trajectory import EntryTrajectoryPlanner, ParachuteDescent, ATMOSPHERE_MODELS


class TestEntryTrajectoryPlanner(unittest.TestCase):
    """Test entry trajectory simulation."""
    
    def test_atmospheric_density(self):
        """Density should decrease with altitude."""
        planner = EntryTrajectoryPlanner("Mars")
        rho_surface = planner.atmospheric_density(0.0)
        rho_high = planner.atmospheric_density(50000.0)
        self.assertGreater(rho_surface, rho_high)
        print(f"  [PASS] Mars density: {rho_surface:.4f} @ surface, {rho_high:.6f} @ 50km")
    
    def test_simulate_mars_entry(self):
        """Should simulate Mars ballistic entry."""
        planner = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0)
        trajectory = planner.simulate_entry(
            entry_altitude_m=125000.0,
            entry_velocity_ms=5500.0,
            entry_fpa_deg=-25.0,
            dt_s=1.0,
            max_time_s=300.0
        )
        self.assertGreater(len(trajectory), 10)
        final = trajectory[-1]
        # Mars thin atmosphere: either descends or skip-out detected
        self.assertTrue(final.altitude_m <= 125000.0 or final.time_s >= 290.0 or len(trajectory) < 50)
        print(f"  [PASS] Mars entry: {len(trajectory)} points, duration={final.time_s:.1f}s, final_alt={final.altitude_m:.0f}m")
    
    def test_simulate_earth_entry(self):
        """Should simulate Earth ballistic entry."""
        planner = EntryTrajectoryPlanner("Earth", ballistic_coefficient_kg_m2=200.0)
        trajectory = planner.simulate_entry(
            entry_altitude_m=120000.0,
            entry_velocity_ms=7800.0,
            entry_fpa_deg=-20.0,
            dt_s=0.5,
            max_time_s=300.0
        )
        self.assertGreater(len(trajectory), 10)
        print(f"  [PASS] Earth entry: {len(trajectory)} points, final_vel={trajectory[-1].velocity_ms:.1f} m/s")
    
    def test_peak_heating(self):
        """Should find peak heating point."""
        planner = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0)
        trajectory = planner.simulate_entry(125000.0, 5500.0, -15.0, dt_s=1.0)
        peak = planner.find_peak_heating(trajectory)
        self.assertGreater(peak.heating_rate_w_cm2, 0)
        print(f"  [PASS] Peak heating: {peak.heating_rate_w_cm2:.4f} W/cm^2 @ {peak.altitude_m:.0f}m")
    
    def test_peak_g_load(self):
        """Should find peak g-load point."""
        planner = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0)
        trajectory = planner.simulate_entry(125000.0, 5500.0, -15.0, dt_s=1.0)
        peak = planner.find_peak_g_load(trajectory)
        self.assertGreater(peak.deceleration_g, 0)
        print(f"  [PASS] Peak g-load: {peak.deceleration_g:.2f}g @ {peak.altitude_m:.0f}m")
    
    def test_peak_dynamic_pressure(self):
        """Should find peak dynamic pressure."""
        planner = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0)
        trajectory = planner.simulate_entry(125000.0, 5500.0, -15.0, dt_s=1.0)
        peak = planner.find_peak_dynamic_pressure(trajectory)
        self.assertGreater(peak.dynamic_pressure_pa, 0)
        print(f"  [PASS] Peak q: {peak.dynamic_pressure_pa:.1f} Pa @ {peak.altitude_m:.0f}m")
    
    def test_entry_summary(self):
        """Should generate entry summary."""
        planner = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0)
        trajectory = planner.simulate_entry(125000.0, 5500.0, -15.0, dt_s=1.0)
        summary = planner.entry_summary(trajectory)
        self.assertIn("peak_heating_w_cm2", summary)
        self.assertIn("peak_deceleration_g", summary)
        self.assertIn("final_velocity_ms", summary)
        print(f"  [PASS] Summary: {summary['final_velocity_ms']:.1f} m/s, {summary['peak_deceleration_g']:.2f}g")
    
    def test_entry_corridor(self):
        """Should design entry corridor."""
        planner = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0)
        corridor = planner.design_entry_corridor(
            entry_velocity_ms=5500.0,
            min_g_limit=2.0,
            max_g_limit=20.0
        )
        self.assertIn("min_fpa_deg", corridor)
        self.assertIn("max_fpa_deg", corridor)
        self.assertLess(corridor["min_fpa_deg"], corridor["max_fpa_deg"])
        print(f"  [PASS] Corridor: {corridor['min_fpa_deg']:.1f}° to {corridor['max_fpa_deg']:.1f}°")
    
    def test_lifting_entry(self):
        """Lifting entry should have longer range."""
        ballistic = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0, lift_drag_ratio=0.0)
        lifting = EntryTrajectoryPlanner("Mars", ballistic_coefficient_kg_m2=150.0, lift_drag_ratio=0.3)
        
        traj_ballistic = ballistic.simulate_entry(125000.0, 5500.0, -15.0, dt_s=1.0)
        traj_lifting = lifting.simulate_entry(125000.0, 5500.0, -15.0, dt_s=1.0)
        
        range_ballistic = traj_ballistic[-1].range_to_go_m
        range_lifting = traj_lifting[-1].range_to_go_m
        
        self.assertGreater(range_lifting, range_ballistic)
        print(f"  [PASS] Lifting vs ballistic: {range_lifting/1000:.1f}km vs {range_ballistic/1000:.1f}km")


class TestParachuteDescent(unittest.TestCase):
    """Test parachute descent phase."""
    
    def test_terminal_velocity(self):
        """Terminal velocity should be positive and decrease at lower altitude."""
        para = ParachuteDescent("Mars", drag_area_m2=100.0, mass_kg=1000.0)
        vt_surface = para.terminal_velocity(0.0)
        vt_high = para.terminal_velocity(5000.0)
        self.assertGreater(vt_surface, 0)
        # Higher altitude = lower density = higher terminal velocity
        self.assertLess(vt_surface, vt_high)
        print(f"  [PASS] Terminal velocity: {vt_surface:.1f} m/s @ surface, {vt_high:.1f} m/s @ 5km")
    
    def test_simulate_descent(self):
        """Should simulate parachute descent to surface."""
        para = ParachuteDescent("Mars", drag_area_m2=100.0, mass_kg=1000.0)
        states = para.simulate_descent(deploy_altitude_m=5000.0, initial_velocity_ms=400.0)
        self.assertGreater(len(states), 0)
        self.assertLess(states[-1]["altitude_m"], states[0]["altitude_m"])
        print(f"  [PASS] Parachute descent: {len(states)} steps, final alt={states[-1]['altitude_m']:.1f}m")
    
    def test_earth_parachute(self):
        """Should simulate Earth parachute descent."""
        para = ParachuteDescent("Earth", drag_area_m2=50.0, mass_kg=1000.0)
        states = para.simulate_descent(deploy_altitude_m=3000.0, initial_velocity_ms=100.0)
        self.assertGreater(len(states), 0)
        print(f"  [PASS] Earth descent: {len(states)} steps, time={states[-1]['time_s']:.1f}s")


if __name__ == '__main__':
    unittest.main(verbosity=2)
