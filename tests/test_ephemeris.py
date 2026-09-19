"""
Unit tests for ephemeris module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ephemeris import PlanetaryEphemeris, JulianDate, OrbitalElements


class TestJulianDate(unittest.TestCase):
    """Test Julian date conversions."""
    
    def test_j2000(self):
        """J2000 epoch should be correct."""
        jd = JulianDate.from_calendar(2000, 1, 1, 12.0)
        self.assertAlmostEqual(jd, 2451545.0, delta=0.01)
        print(f"  [PASS] J2000: JD={jd:.2f}")
    
    def test_roundtrip(self):
        """Calendar to JD and back should match."""
        jd = JulianDate.from_calendar(2024, 6, 15, 0.0)
        year, month, day, hour = JulianDate.to_calendar(jd)
        self.assertEqual(year, 2024)
        self.assertEqual(month, 6)
        self.assertEqual(day, 15)
        print(f"  [PASS] Roundtrip: {year}-{month:02d}-{day:02d}")


class TestPlanetaryEphemeris(unittest.TestCase):
    """Test planetary ephemeris."""
    
    def test_compute_elements(self):
        """Should compute orbital elements."""
        elements = PlanetaryEphemeris.compute_elements("Earth", 2451545.0)
        self.assertIsInstance(elements, OrbitalElements)
        self.assertAlmostEqual(elements.a_au, 1.0, delta=0.02)
        print(f"  [PASS] Earth elements: a={elements.a_au:.4f} AU, e={elements.e:.5f}")
    
    def test_earth_position_j2000(self):
        """Earth at J2000 should be near x=1 AU."""
        pos = PlanetaryEphemeris.position("Earth", 2451545.0)
        r = math.sqrt(sum(x**2 for x in pos))
        self.assertAlmostEqual(r, 1.0, delta=0.02)
        print(f"  [PASS] Earth J2000: ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}), r={r:.4f}")
    
    def test_mars_position(self):
        """Should compute Mars position."""
        pos = PlanetaryEphemeris.mars_position(2451545.0)
        r = math.sqrt(sum(x**2 for x in pos))
        self.assertGreater(r, 1.3)
        self.assertLess(r, 1.8)
        print(f"  [PASS] Mars J2000: r={r:.4f} AU")
    
    def test_distance_between(self):
        """Should compute Earth-Mars distance."""
        dist = PlanetaryEphemeris.distance_between("Earth", "Mars", 2451545.0)
        self.assertGreater(dist, 0.3)
        self.assertLess(dist, 2.7)
        print(f"  [PASS] Earth-Mars distance: {dist:.4f} AU")
    
    def test_light_time(self):
        """Should compute light time."""
        lt = PlanetaryEphemeris.light_time("Earth", "Mars", 2451545.0)
        self.assertGreater(lt, 1.0)  # > 1 minute
        self.assertLess(lt, 25.0)    # < 25 minutes
        print(f"  [PASS] Light time: {lt:.2f} min")
    
    def test_all_planets(self):
        """Should work for all planets."""
        bodies = PlanetaryEphemeris.get_available_bodies()
        self.assertEqual(len(bodies), 8)
        for body in bodies:
            pos = PlanetaryEphemeris.position(body, 2451545.0)
            r = math.sqrt(sum(x**2 for x in pos))
            self.assertGreater(r, 0.3)
        print(f"  [PASS] All {len(bodies)} planets computed")
    
    def test_unknown_body(self):
        """Should raise for unknown body."""
        with self.assertRaises(ValueError):
            PlanetaryEphemeris.position("Pluto", 2451545.0)
        print("  [PASS] Unknown body raises error")


if __name__ == '__main__':
    unittest.main(verbosity=2)
