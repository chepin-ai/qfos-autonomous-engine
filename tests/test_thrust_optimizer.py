"""
Unit tests for thrust optimizer module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thrust_optimizer import ImpulsiveThrustOptimizer, LowThrustOptimizer


class TestImpulsiveThrustOptimizer(unittest.TestCase):
    """Test impulsive thrust optimization."""
    
    def setUp(self):
        self.opt = ImpulsiveThrustOptimizer(spacecraft_mass_kg=1000.0, isp_seconds=300.0)
    
    def test_simple_plane_change(self):
        """Small plane change should use simple strategy."""
        result = self.opt.optimize_plane_change(v_ms=30000, delta_i_deg=2.0, optimize=True)
        self.assertEqual(result["strategy"], "simple_plane_change")
        self.assertGreater(result["total_dv_ms"], 0)
        self.assertGreater(result["propellant_kg"], 0)
        print(f"  [PASS] 2-deg plane change: {result['total_dv_ms']:.1f} m/s, {result['propellant_kg']:.2f} kg")
    
    def test_large_plane_change(self):
        """Large plane change may use bi-elliptic."""
        result = self.opt.optimize_plane_change(v_ms=30000, delta_i_deg=30.0, optimize=True)
        self.assertIn("strategy", result)
        self.assertGreater(result["total_dv_ms"], 0)
        print(f"  [PASS] 30-deg plane change: strategy={result['strategy']}, dv={result['total_dv_ms']:.1f} m/s")
    
    def test_propellant_calculation(self):
        """Propellant mass should increase with delta-v."""
        m1 = self.opt._propellant_mass(1000, 1000.0)
        m2 = self.opt._propellant_mass(2000, 1000.0)
        self.assertGreater(m2, m1)
        print(f"  [PASS] Propellant: dv=1000m/s -> {m1:.2f}kg, dv=2000m/s -> {m2:.2f}kg")
    
    def test_transfer_sequence(self):
        """Should optimize burn sequence with mass depletion."""
        burns = [(0.0, 500.0), (100.0, 300.0), (200.0, 200.0)]
        maneuvers = self.opt.optimize_transfer_sequence(burns)
        
        self.assertEqual(len(maneuvers), 3)
        # Earlier burns should use more propellant (heavier spacecraft)
        self.assertGreater(maneuvers[0].propellant_kg, maneuvers[1].propellant_kg)
        print(f"  [PASS] 3-burn sequence: {[f'{m.delta_v_magnitude_ms:.0f}m/s ({m.propellant_kg:.2f}kg)' for m in maneuvers]}")
    
    def test_low_thrust_spiral(self):
        """Low-thrust spiral time should be reasonable."""
        time_days = self.opt.low_thrust_spiral_time(
            r1_au=1.0, r2_au=1.524,
            thrust_n=0.1, mass_kg=1000.0
        )
        self.assertGreater(time_days, 100)   # More than 100 days
        self.assertLess(time_days, 5000)     # Less than ~14 years
        print(f"  [PASS] Low-thrust spiral Earth->Mars: {time_days:.0f} days")


class TestLowThrustOptimizer(unittest.TestCase):
    """Test low-thrust trajectory optimization."""
    
    def test_exponential_sinusoid(self):
        """Should generate exponential sinusoid parameters."""
        opt = LowThrustOptimizer()
        result = opt.exponential_sinusoid_trajectory(1.0, 1.524, revolutions=1)
        
        self.assertEqual(result["trajectory_type"], "exponential_sinusoid")
        self.assertGreater(result["total_angle_deg"], 360)
        print(f"  [PASS] Exponential sinusoid: {result['total_angle_deg']:.1f} deg, {result['revolutions']} revs")


if __name__ == '__main__':
    unittest.main(verbosity=2)
