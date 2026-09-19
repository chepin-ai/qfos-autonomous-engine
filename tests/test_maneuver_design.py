"""
Unit tests for maneuver design module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from maneuver_design import (
    HohmannTransfer, BiEllipticTransfer, PlaneChangeManeuver,
    FiniteBurnManeuver, ManeuverSequence, Maneuver
)


class TestHohmannTransfer(unittest.TestCase):
    """Test Hohmann transfer."""
    
    def test_design(self):
        """Should design Hohmann transfer."""
        result = HohmannTransfer.design(r1_km=6678.0, r2_km=42164.0)
        self.assertGreater(result["delta_v_total_ms"], 0.0)
        self.assertGreater(result["transfer_time_hr"], 0.0)
        print(f"  [PASS] Hohmann: dV={result['delta_v_total_ms']:.1f} m/s, TOF={result['transfer_time_hr']:.1f} hr")
    
    def test_geo_transfer(self):
        """LEO to GEO should be ~3.9 km/s."""
        result = HohmannTransfer.design(
            r1_km=6678.0,  # ~400km altitude
            r2_km=42164.0  # GEO
        )
        self.assertAlmostEqual(result["delta_v_total_ms"], 3900.0, delta=200.0)
        print(f"  [PASS] LEO->GEO: {result['delta_v_total_ms']:.1f} m/s")


class TestBiEllipticTransfer(unittest.TestCase):
    """Test bi-elliptic transfer."""
    
    def test_design(self):
        """Should design bi-elliptic transfer."""
        result = BiEllipticTransfer.design(
            r1_km=6678.0, r2_km=42164.0,
            r_intermediate_km=80000.0
        )
        self.assertGreater(result["delta_v_total_ms"], 0.0)
        print(f"  [PASS] Bi-elliptic: dV={result['delta_v_total_ms']:.1f} m/s")


class TestPlaneChangeManeuver(unittest.TestCase):
    """Test plane change."""
    
    def test_simple_plane_change(self):
        """Should compute simple plane change."""
        dv = PlaneChangeManeuver.simple_plane_change(
            velocity_ms=7500.0, delta_inclination_deg=28.5
        )
        self.assertGreater(dv, 0.0)
        print(f"  [PASS] Plane change: {dv:.1f} m/s")
    
    def test_combined_plane_change(self):
        """Should compute combined plane change."""
        dv = PlaneChangeManeuver.combined_plane_change(
            v1_ms=7500.0, v2_ms=7500.0, delta_inclination_deg=28.5
        )
        self.assertGreater(dv, 0.0)
        print(f"  [PASS] Combined: {dv:.1f} m/s")
    
    def test_zero_change(self):
        """Zero inclination change should be zero delta-v."""
        dv = PlaneChangeManeuver.simple_plane_change(
            velocity_ms=7500.0, delta_inclination_deg=0.0
        )
        self.assertAlmostEqual(dv, 0.0, delta=0.01)
        print("  [PASS] Zero change: 0 m/s")


class TestFiniteBurnManeuver(unittest.TestCase):
    """Test finite burn."""
    
    def test_burn_duration(self):
        """Should compute burn duration."""
        result = FiniteBurnManeuver.compute_burn_duration(
            delta_v_ms=100.0, initial_mass_kg=500.0
        )
        self.assertGreater(result["burn_duration_s"], 0.0)
        self.assertGreater(result["propellant_mass_kg"], 0.0)
        print(f"  [PASS] Burn: {result['burn_duration_s']:.1f}s, prop={result['propellant_mass_kg']:.3f}kg")
    
    def test_gravity_loss(self):
        """Should estimate gravity loss."""
        loss = FiniteBurnManeuver.gravity_loss(
            delta_v_ideal_ms=100.0, burn_duration_s=60.0
        )
        self.assertGreater(loss, 0.0)
        print(f"  [PASS] Gravity loss: {loss:.2f} m/s")


class TestManeuverSequence(unittest.TestCase):
    """Test maneuver sequence."""
    
    def setUp(self):
        self.seq = ManeuverSequence()
    
    def test_add_maneuver(self):
        """Should add maneuvers."""
        self.seq.add_maneuver(Maneuver("burn1", 100.0, 0.0))
        self.seq.add_maneuver(Maneuver("burn2", 50.0, math.pi))
        self.assertEqual(len(self.seq.maneuvers), 2)
        print("  [PASS] Add maneuvers")
    
    def test_total_delta_v(self):
        """Should compute total delta-v."""
        self.seq.add_maneuver(Maneuver("burn1", 100.0, 0.0))
        self.seq.add_maneuver(Maneuver("burn2", 50.0, 0.0))
        total = self.seq.total_delta_v()
        self.assertEqual(total, 150.0)
        print(f"  [PASS] Total dV: {total:.1f} m/s")
    
    def test_propellant(self):
        """Should compute propellant."""
        self.seq.add_maneuver(Maneuver("burn1", 100.0, 0.0))
        prop = self.seq.total_propellant(initial_mass_kg=500.0)
        self.assertGreater(prop, 0.0)
        print(f"  [PASS] Propellant: {prop:.3f} kg")
    
    def test_summary(self):
        """Should provide summary."""
        self.seq.add_maneuver(Maneuver("burn1", 100.0, 0.0))
        summary = self.seq.get_summary()
        self.assertEqual(summary["maneuver_count"], 1)
        print(f"  [PASS] Summary: {summary['maneuver_count']} maneuvers")


if __name__ == '__main__':
    unittest.main(verbosity=2)
