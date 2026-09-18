"""
Unit tests for orbital mechanics module.
Tests use real NASA/JPL SBDB data for validation.
"""

import unittest
import math
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbital_mechanics import OrbitalBody, hohmann_transfer_delta_v, estimate_moid


class TestOrbitalBody(unittest.TestCase):
    """Test orbital body calculations."""
    
    def setUp(self):
        """Create test bodies using real asteroid data."""
        self.earth = OrbitalBody(
            name="Earth", spkid="399", 
            a_au=1.0, e=0.0167, i_deg=0.0
        )
        self.apophis = OrbitalBody(
            name="99942 Apophis", spkid="99942",
            a_au=0.922, e=0.191, i_deg=3.33
        )
        self.bennu = OrbitalBody(
            name="101955 Bennu", spkid="101955",
            a_au=1.126, e=0.204, i_deg=6.03
        )
        self.yr4 = OrbitalBody(
            name="2024 YR4", spkid="",
            a_au=2.516, e=0.66, i_deg=3.41
        )
    
    def test_earth_orbital_period(self):
        """Earth's orbital period should be ~1 year."""
        self.assertAlmostEqual(self.earth.period_years, 1.0, places=2)
        print(f"  [PASS] Earth period: {self.earth.period_years:.3f} years")
    
    def test_apophis_velocity(self):
        """Apophis velocity should be reasonable for near-Earth asteroid."""
        v = self.apophis.orbital_velocity_at(self.apophis.a)
        # Should be close to Earth's ~29.8 km/s since a ~ 1 AU
        self.assertGreater(v, 25000)
        self.assertLess(v, 35000)
        print(f"  [PASS] Apophis velocity: {v/1000:.2f} km/s")
    
    def test_perihelion_aphelion(self):
        """Test perihelion/aphelion calculations."""
        q = self.apophis.perihelion_m / 1.496e11  # AU
        Q = self.apophis.aphelion_m / 1.496e11
        self.assertLess(q, self.apophis.semi_major_axis_au)
        self.assertGreater(Q, self.apophis.semi_major_axis_au)
        print(f"  [PASS] Apophis q={q:.3f} AU, Q={Q:.3f} AU")
    
    def test_kepler_solver(self):
        """Kepler solver should converge for typical values."""
        for M in [0.0, 0.5, 1.0, 2.0, 3.0]:
            E = self.earth.solve_kepler(M)
            # Verify: M = E - e*sin(E)
            residual = abs(E - self.earth.e * math.sin(E) - M)
            self.assertLess(residual, 1e-8)
        print(f"  [PASS] Kepler solver converged for 5 test cases")
    
    def test_position_propagation(self):
        """Test orbit propagation produces closed orbit."""
        x0, y0, z0 = self.earth.position_at_time(0)
        x1, y1, z1 = self.earth.position_at_time(365.25)
        # After 1 year, should return to approximately same position
        dist = math.sqrt((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2)
        self.assertLess(dist, 0.1)  # Less than 0.1 AU drift
        print(f"  [PASS] 1-year propagation drift: {dist:.4f} AU")


class TestHohmannTransfer(unittest.TestCase):
    """Test Hohmann transfer calculations."""
    
    def test_earth_to_mars(self):
        """Earth to Mars transfer should require ~5.5 km/s."""
        dv = hohmann_transfer_delta_v(1.0, 1.524)
        self.assertGreater(dv, 4.0)
        self.assertLess(dv, 7.0)
        print(f"  [PASS] Earth->Mars dV: {dv:.3f} km/s")
    
    def test_same_orbit_zero_dv(self):
        """Transfer to same orbit should require ~0 dV."""
        dv = hohmann_transfer_delta_v(1.0, 1.0)
        self.assertAlmostEqual(dv, 0.0, places=3)
        print(f"  [PASS] Same orbit dV: {dv:.6f} km/s")


class TestMOID(unittest.TestCase):
    """Test Minimum Orbit Intersection Distance."""
    
    def test_earth_apophis(self):
        """Earth-Apophis MOID should be small (NEA)."""
        earth = OrbitalBody(name="Earth", spkid="399", a_au=1.0, e=0.0167, i_deg=0.0)
        apophis = OrbitalBody(name="Apophis", spkid="99942", a_au=0.922, e=0.191, i_deg=3.33)
        moid = estimate_moid(earth, apophis)
        self.assertGreater(moid, 0)
        self.assertLess(moid, 0.5)
        print(f"  [PASS] Earth-Apophis MOID: {moid:.4f} AU")


if __name__ == '__main__':
    unittest.main(verbosity=2)
