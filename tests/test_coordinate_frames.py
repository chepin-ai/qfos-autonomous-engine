"""
Unit tests for coordinate frames module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from coordinate_frames import CoordinateFrames


class TestCoordinateFrames(unittest.TestCase):
    """Test coordinate frame transformations."""
    
    def test_rotation_matrix_x(self):
        """Should create rotation matrix about x."""
        R = CoordinateFrames.rotation_matrix_x(math.pi / 2)
        self.assertAlmostEqual(R[1][1], 0.0, delta=0.01)
        self.assertAlmostEqual(R[1][2], -1.0, delta=0.01)
        print("  [PASS] Rotation X")
    
    def test_rotation_matrix_z(self):
        """Should create rotation matrix about z."""
        R = CoordinateFrames.rotation_matrix_z(math.pi / 2)
        self.assertAlmostEqual(R[0][0], 0.0, delta=0.01)
        self.assertAlmostEqual(R[0][1], -1.0, delta=0.01)
        print("  [PASS] Rotation Z")
    
    def test_eci_to_ecef(self):
        """Should convert ECI to ECEF."""
        pos_eci = (6678.0, 0.0, 0.0)
        pos_ecef = CoordinateFrames.eci_to_ecef(pos_eci, gmst_rad=0.0)
        self.assertAlmostEqual(pos_ecef[0], 6678.0, delta=0.1)
        self.assertAlmostEqual(pos_ecef[1], 0.0, delta=0.1)
        print(f"  [PASS] ECI->ECEF: ({pos_ecef[0]:.1f}, {pos_ecef[1]:.1f}, {pos_ecef[2]:.1f})")
    
    def test_ecef_to_eci(self):
        """Should convert ECEF to ECI."""
        pos_ecef = (6678.0, 0.0, 0.0)
        pos_eci = CoordinateFrames.ecef_to_eci(pos_ecef, gmst_rad=0.0)
        self.assertAlmostEqual(pos_eci[0], 6678.0, delta=0.1)
        print("  [PASS] ECEF->ECI roundtrip")
    
    def test_ecef_to_lla(self):
        """Should convert ECEF to LLA."""
        pos_ecef = (6378.137, 0.0, 0.0)
        lat, lon, alt = CoordinateFrames.ecef_to_lla(pos_ecef)
        self.assertAlmostEqual(lat, 0.0, delta=0.1)
        self.assertAlmostEqual(lon, 0.0, delta=0.1)
        self.assertAlmostEqual(alt, 0.0, delta=0.1)
        print(f"  [PASS] ECEF->LLA: lat={lat:.2f}, lon={lon:.2f}, alt={alt:.2f}")
    
    def test_lla_to_ecef_roundtrip(self):
        """LLA->ECEF->LLA should match."""
        lat_in, lon_in, alt_in = 45.0, 30.0, 100.0
        ecef = CoordinateFrames.lla_to_ecef(lat_in, lon_in, alt_in)
        lat_out, lon_out, alt_out = CoordinateFrames.ecef_to_lla(ecef)
        self.assertAlmostEqual(lat_in, lat_out, delta=0.01)
        self.assertAlmostEqual(lon_in, lon_out, delta=0.01)
        self.assertAlmostEqual(alt_in, alt_out, delta=0.01)
        print(f"  [PASS] LLA roundtrip")
    
    def test_eci_to_lvlh(self):
        """Should compute LVLH frame."""
        pos = (6678.0, 0.0, 0.0)
        vel = (0.0, 7.725, 0.0)
        R = CoordinateFrames.eci_to_lvlh(pos, vel)
        self.assertEqual(len(R), 3)
        self.assertEqual(len(R[0]), 3)
        print("  [PASS] LVLH frame: 3x3 matrix")
    
    def test_position_to_lvlh(self):
        """Should convert position to LVLH."""
        pos = (6678.0, 0.0, 0.0)
        vel = (0.0, 7.725, 0.0)
        target = (6679.0, 0.0, 0.0)
        lvlh = CoordinateFrames.position_to_lvlh(pos, vel, target)
        self.assertAlmostEqual(lvlh[0], 1.0, delta=0.01)
        print(f"  [PASS] LVLH position: ({lvlh[0]:.3f}, {lvlh[1]:.3f}, {lvlh[2]:.3f})")
    
    def test_orbital_elements_to_rv(self):
        """Should convert elements to position/velocity."""
        pos, vel = CoordinateFrames.orbital_elements_to_rv(
            a_km=6678.0, e=0.0, i_deg=0.0,
            raan_deg=0.0, arg_peri_deg=0.0, true_anomaly_deg=0.0
        )
        r = math.sqrt(sum(p**2 for p in pos))
        self.assertAlmostEqual(r, 6678.0, delta=0.1)
        print(f"  [PASS] Elements->RV: r={r:.1f} km")
    
    def test_circular_orbit_velocity(self):
        """Circular orbit should have correct velocity."""
        pos, vel = CoordinateFrames.orbital_elements_to_rv(
            a_km=6678.0, e=0.0, i_deg=0.0,
            raan_deg=0.0, arg_peri_deg=0.0, true_anomaly_deg=0.0
        )
        v = math.sqrt(sum(v**2 for v in vel))
        expected_v = math.sqrt(398600.4418 / 6678.0)
        self.assertAlmostEqual(v, expected_v, delta=0.01)
        print(f"  [PASS] Circular velocity: {v:.4f} km/s")
    
    def test_gmst_from_jd(self):
        """Should compute GMST."""
        gmst = CoordinateFrames.gmst_from_jd(2451545.0)  # J2000
        # At J2000 noon, GMST ≈ 280.46° = 4.894 rad
        self.assertGreater(gmst, 0.0)
        print(f"  [PASS] GMST: {math.degrees(gmst):.2f} deg")


if __name__ == '__main__':
    unittest.main(verbosity=2)
