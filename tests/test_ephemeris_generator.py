"""
Unit tests for ephemeris generator module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ephemeris_generator import (EphemerisEntry, LinearInterpolator,
                                 LagrangeInterpolator, TimeScale,
                                 CelestialBody, EphemerisGenerator)


class TestLinearInterpolator(unittest.TestCase):
    """Test linear interpolator."""
    
    def test_interpolate(self):
        """Should linearly interpolate."""
        li = LinearInterpolator()
        val = li.interpolate(0.5, 0, 1, 10, 20)
        self.assertEqual(val, 15.0)
        print(f"  [PASS] Linear: {val}")
    
    def test_interpolate_3d(self):
        """Should interpolate 3D."""
        li = LinearInterpolator()
        p = li.interpolate_3d(0.5, 0, 1, (0, 0, 0), (10, 20, 30))
        self.assertEqual(p, (5.0, 10.0, 15.0))
        print(f"  [PASS] 3D: {p}")


class TestLagrangeInterpolator(unittest.TestCase):
    """Test Lagrange interpolator."""
    
    def setUp(self):
        self.li = LagrangeInterpolator(order=4)
    
    def test_interpolate(self):
        """Should interpolate through points."""
        times = [0, 1, 2, 3]
        values = [0, 1, 4, 9]  # x^2
        val = self.li.interpolate(1.5, times, values)
        self.assertAlmostEqual(val, 2.25, places=1)
        print(f"  [PASS] Lagrange: {val:.2f}")
    
    def test_interpolate_exact(self):
        """Should return exact at sample point."""
        times = [0, 1, 2, 3]
        values = [0, 1, 4, 9]
        val = self.li.interpolate(1.0, times, values)
        self.assertAlmostEqual(val, 1.0, places=5)
        print("  [PASS] Exact: 1.0")


class TestTimeScale(unittest.TestCase):
    """Test time scale."""
    
    def test_jd_to_seconds(self):
        """Should convert JD to seconds."""
        s = TimeScale.jd_to_seconds(2451546.0)
        self.assertEqual(s, 86400.0)
        print(f"  [PASS] JD->s: {s}")
    
    def test_seconds_to_jd(self):
        """Should convert seconds to JD."""
        jd = TimeScale.seconds_to_jd(86400.0)
        self.assertEqual(jd, 2451546.0)
        print(f"  [PASS] s->JD: {jd}")
    
    def test_gmst(self):
        """Should compute GMST."""
        gmst = TimeScale.gmst(2451545.0)
        self.assertGreaterEqual(gmst, 0)
        self.assertLess(gmst, 2 * math.pi)
        print(f"  [PASS] GMST: {math.degrees(gmst):.2f} deg")


class TestCelestialBody(unittest.TestCase):
    """Test celestial body."""
    
    def setUp(self):
        self.body = CelestialBody("Test", orbital_period_days=1.0,
                                  semi_major_axis_km=10000.0,
                                  eccentricity=0.0)
    
    def test_position_at_epoch(self):
        """Should compute position at t=0."""
        pos = self.body.position_at(0)
        self.assertAlmostEqual(pos[0], 10000.0, places=0)
        print(f"  [PASS] Epoch: {pos}")
    
    def test_position_at_half_period(self):
        """Should be opposite at half period."""
        pos = self.body.position_at(self.body.period / 2)
        self.assertLess(pos[0], 0)
        print(f"  [PASS] Half: x={pos[0]:.1f}")


class TestEphemerisGenerator(unittest.TestCase):
    """Test ephemeris generator."""
    
    def setUp(self):
        self.eg = EphemerisGenerator()
        self.eg.add_body(CelestialBody("Sat", 0.07, 26500.0))
    
    def test_add_body(self):
        """Should add body."""
        self.assertIn("Sat", self.eg.bodies)
        print("  [PASS] Add: Sat")
    
    def test_generate(self):
        """Should generate ephemeris."""
        entries = self.eg.generate("Sat", 0, 3600, 600)
        self.assertGreater(len(entries), 5)
        print(f"  [PASS] Generate: {len(entries)} entries")
    
    def test_interpolate_linear(self):
        """Should interpolate linearly."""
        entries = self.eg.generate("Sat", 0, 3600, 600)
        pos = self.eg.interpolate_position(900, entries, "linear")
        self.assertIsNotNone(pos)
        self.assertEqual(len(pos), 3)
        print(f"  [PASS] Interp linear: {pos[0]:.1f}")
    
    def test_interpolate_lagrange(self):
        """Should interpolate with Lagrange."""
        entries = self.eg.generate("Sat", 0, 3600, 600)
        pos = self.eg.interpolate_position(900, entries, "lagrange")
        self.assertIsNotNone(pos)
        print(f"  [PASS] Interp lagrange: {pos[0]:.1f}")
    
    def test_get_entry_at(self):
        """Should find closest entry."""
        entries = self.eg.generate("Sat", 0, 3600, 600)
        entry = self.eg.get_entry_at(950, entries)
        self.assertIsNotNone(entry)
        print(f"  [PASS] Closest: t={entry.timestamp}")
    
    def test_summary(self):
        """Should provide summary."""
        entries = self.eg.generate("Sat", 0, 3600, 600)
        summary = self.eg.ephemeris_summary(entries)
        self.assertEqual(summary["count"], len(entries))
        print(f"  [PASS] Summary: {summary['count']} entries")


if __name__ == '__main__':
    unittest.main(verbosity=2)
