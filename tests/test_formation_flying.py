"""
Unit tests for formation flying module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from formation_flying import (SpacecraftState, RelativeOrbitalElements,
                              FormationKeeping, CoordinatedControl,
                              FormationFlying)


class TestRelativeOrbitalElements(unittest.TestCase):
    """Test ROE computations."""
    
    def setUp(self):
        self.chief = SpacecraftState((7000, 0, 0), (0, 7.5, 0), "chief")
        self.deputy = SpacecraftState((7000.5, 0, 0), (0, 7.5, 0), "dep")
    
    def test_compute_relative(self):
        """Should compute relative state."""
        rel = RelativeOrbitalElements.compute_relative(self.chief, self.deputy)
        self.assertAlmostEqual(rel["dx_km"], 0.5, places=5)
        self.assertGreater(rel["range_km"], 0)
        print(f"  [PASS] Relative: dx={rel['dx_km']:.2f}, range={rel['range_km']:.3f}")
    
    def test_hill_frame(self):
        """Should compute Hill frame."""
        hill = RelativeOrbitalElements.hill_frame(self.chief, self.deputy)
        self.assertIn("radial_km", hill)
        self.assertIn("along_track_km", hill)
        print(f"  [PASS] Hill: R={hill['radial_km']:.3f}, T={hill['along_track_km']:.3f}")


class TestFormationKeeping(unittest.TestCase):
    """Test formation keeping."""
    
    def setUp(self):
        self.fk = FormationKeeping()
        self.chief = SpacecraftState((7000, 0, 0), (0, 7.5, 0), "chief")
        self.deputy = SpacecraftState((7000.5, 0, 0), (0, 7.5, 0), "dep")
    
    def test_station_keeping(self):
        """Should compute station-keeping delta-v."""
        dv = self.fk.station_keeping_delta_v(self.chief, self.deputy, 0.1)
        self.assertEqual(len(dv), 3)
        print(f"  [PASS] dV: ({dv[0]:.6f}, {dv[1]:.6f}, {dv[2]:.6f})")
    
    def test_periodic_correction(self):
        """Should compute periodic correction."""
        dv = self.fk.periodic_correction(self.chief, self.deputy,
                                         {"radial_km": 0, "along_track_km": 0.5})
        self.assertEqual(len(dv), 3)
        print(f"  [PASS] Periodic: ({dv[0]:.6f}, {dv[1]:.6f}, {dv[2]:.6f})")


class TestCoordinatedControl(unittest.TestCase):
    """Test coordinated control."""
    
    def setUp(self):
        self.cc = CoordinatedControl()
        self.cc.register("chief", SpacecraftState((7000, 0, 0), (0, 7.5, 0)))
        self.cc.register("dep1", SpacecraftState((7000.5, 0, 0), (0, 7.5, 0)))
        self.cc.set_desired_geometry("dep1", {"radial_km": 0.5, "along_track_km": 0, "cross_track_km": 0})
    
    def test_register(self):
        """Should register spacecraft."""
        self.assertEqual(len(self.cc.spacecraft), 2)
        print("  [PASS] Register: 2 SC")
    
    def test_compute_corrections(self):
        """Should compute corrections."""
        corr = self.cc.compute_corrections("chief")
        self.assertIn("dep1", corr)
        print(f"  [PASS] Corrections: {list(corr.keys())}")
    
    def test_formation_error(self):
        """Should compute formation errors."""
        err = self.cc.formation_error("chief")
        self.assertIn("range", err)
        print(f"  [PASS] Error: range={err['range']:.3f}")


class TestFormationFlying(unittest.TestCase):
    """Test unified formation flying."""
    
    def setUp(self):
        self.ff = FormationFlying()
        self.ff.add_spacecraft("chief", (7000, 0, 0), (0, 7.5, 0))
        self.ff.add_spacecraft("dep1", (7000.5, 0, 0), (0, 7.5, 0))
        self.ff.set_geometry("dep1", radial=0.5, along_track=0, cross_track=0)
    
    def test_add(self):
        """Should add spacecraft."""
        self.assertEqual(len(self.ff.coord.spacecraft), 2)
        print("  [PASS] Add: 2 SC")
    
    def test_maneuvers(self):
        """Should compute maneuvers."""
        dv = self.ff.compute_maneuvers("chief")
        self.assertIn("dep1", dv)
        print(f"  [PASS] Maneuvers: {list(dv.keys())}")
    
    def test_relative_state(self):
        """Should get relative state."""
        rel = self.ff.get_relative_state("chief", "dep1")
        self.assertGreater(rel["range_km"], 0)
        print(f"  [PASS] Relative: range={rel['range_km']:.3f}")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.ff.flying_summary("chief")
        self.assertEqual(summary["spacecraft"], 2)
        print(f"  [PASS] Summary: {summary['spacecraft']} SC")


if __name__ == '__main__':
    unittest.main(verbosity=2)
