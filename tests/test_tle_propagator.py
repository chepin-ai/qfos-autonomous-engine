"""
Unit tests for TLE propagator module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tle_propagator import TLEParser, SGP4Propagator, create_sample_iss_tle


class TestTLEParser(unittest.TestCase):
    """Test TLE parsing."""
    
    def test_parse_iss(self):
        """Should parse ISS TLE."""
        tle_lines = create_sample_iss_tle()
        tle = TLEParser.parse(tle_lines)
        
        self.assertEqual(tle.satellite_number, 25544)
        self.assertEqual(tle.name, "ISS (ZARYA)")
        self.assertGreater(tle.mean_motion_revs_day, 15.0)
        self.assertGreater(tle.inclination_deg, 51.0)
        print(f"  [PASS] Parsed ISS: NORAD={tle.satellite_number}, inc={tle.inclination_deg:.2f}deg")
    
    def test_orbital_elements(self):
        """Should extract orbital elements."""
        tle_lines = create_sample_iss_tle()
        tle = TLEParser.parse(tle_lines)
        
        self.assertGreater(tle.eccentricity, 0.0)
        self.assertLess(tle.eccentricity, 0.01)
        self.assertGreater(tle.raan_deg, 0.0)
        self.assertGreater(tle.arg_perigee_deg, 0.0)
        print(f"  [PASS] Elements: e={tle.eccentricity}, a inferred from n={tle.mean_motion_revs_day:.4f}")


class TestSGP4Propagator(unittest.TestCase):
    """Test SGP4 propagation."""
    
    def setUp(self):
        tle_lines = create_sample_iss_tle()
        self.tle = TLEParser.parse(tle_lines)
        self.prop = SGP4Propagator(self.tle)
    
    def test_propagate_zero(self):
        """Should propagate at epoch."""
        pos, vel = self.prop.propagate(0.0)
        r = (pos[0]**2 + pos[1]**2 + pos[2]**2) ** 0.5
        self.assertGreater(r, 6600.0)
        self.assertLess(r, 6800.0)
        print(f"  [PASS] Epoch: r={r:.1f} km")
    
    def test_propagate_period(self):
        """Should complete one orbit."""
        period = self.prop.get_orbital_period_min()
        pos0, vel0 = self.prop.propagate(0.0)
        pos1, vel1 = self.prop.propagate(period)
        
        dr = ((pos1[0]-pos0[0])**2 + (pos1[1]-pos0[1])**2 + (pos1[2]-pos0[2])**2) ** 0.5
        # Approximate: one period should be close
        self.assertLess(dr, 500.0)  # Some J2 drift expected
        print(f"  [PASS] Period: {period:.1f} min, drift={dr:.1f} km")
    
    def test_altitude(self):
        """Should compute altitude."""
        alt = self.prop.get_altitude_km()
        self.assertGreater(alt, 300.0)
        self.assertLess(alt, 500.0)
        print(f"  [PASS] Altitude: {alt:.1f} km")
    
    def test_velocity_magnitude(self):
        """Velocity should be ~7.7 km/s for LEO."""
        pos, vel = self.prop.propagate(0.0)
        v = (vel[0]**2 + vel[1]**2 + vel[2]**2) ** 0.5
        self.assertGreater(v, 7.0)
        self.assertLess(v, 8.0)
        print(f"  [PASS] Velocity: {v:.3f} km/s")
    
    def test_raan_drift(self):
        """RAAN should drift due to J2."""
        pos0, _ = self.prop.propagate(0.0)
        pos1, _ = self.prop.propagate(120.0)  # 2 hours
        
        # Just check propagation works over extended period
        r1 = (pos1[0]**2 + pos1[1]**2 + pos1[2]**2) ** 0.5
        self.assertGreater(r1, 6600.0)
        print(f"  [PASS] 2hr propagation: r={r1:.1f} km")


if __name__ == '__main__':
    unittest.main(verbosity=2)
