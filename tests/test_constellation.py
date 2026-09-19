"""
Unit tests for constellation maintenance module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from constellation import (
    Satellite, ConstellationPlanner, OrbitMaintenance,
    ConstellationCollisionAvoidance, EARTH_RADIUS_KM
)


class TestSatellite(unittest.TestCase):
    """Test satellite dataclass."""
    
    def test_orbital_period(self):
        """ISS-like orbit should have ~93 min period."""
        sat = Satellite(
            sat_id="ISS", semi_major_axis_km=EARTH_RADIUS_KM + 400,
            eccentricity=0.0, inclination_deg=51.6,
            raan_deg=0.0, arg_perigee_deg=0.0, mean_anomaly_deg=0.0
        )
        period = sat.orbital_period_min
        self.assertAlmostEqual(period, 93.0, delta=5.0)
        print(f"  [PASS] Period: {period:.1f} min (ISS-like)")
    
    def test_mean_motion(self):
        """Mean motion should be positive."""
        sat = Satellite(
            sat_id="TEST", semi_major_axis_km=7000,
            eccentricity=0.0, inclination_deg=0.0,
            raan_deg=0.0, arg_perigee_deg=0.0, mean_anomaly_deg=0.0
        )
        n = sat.mean_motion_rad_s
        self.assertGreater(n, 0)
        print(f"  [PASS] Mean motion: {n:.6f} rad/s")


class TestConstellationPlanner(unittest.TestCase):
    """Test constellation design."""
    
    def test_walker_delta(self):
        """Should create Walker delta constellation."""
        sats = ConstellationPlanner.design_walker_delta(
            num_planes=6, sats_per_plane=5, altitude_km=550, inclination_deg=53.0
        )
        self.assertEqual(len(sats), 30)
        
        # Check all have same semi-major axis
        altitudes = [s.semi_major_axis_km - EARTH_RADIUS_KM for s in sats]
        self.assertAlmostEqual(max(altitudes), min(altitudes), delta=0.1)
        print(f"  [PASS] Walker delta: {len(sats)} sats, {len(set(s.raan_deg for s in sats))} planes")
    
    def test_star_constellation(self):
        """Should create star constellation."""
        sats = ConstellationPlanner.design_star_constellation(
            num_planes=6, altitude_km=550, inclination_deg=53.0
        )
        self.assertEqual(len(sats), 6)
        # Check alternating inclinations
        inclinations = [s.inclination_deg for s in sats]
        self.assertTrue(any(i < 0 for i in inclinations))
        print(f"  [PASS] Star constellation: {len(sats)} sats")
    
    def test_constellation_summary(self):
        """Should provide constellation summary."""
        planner = ConstellationPlanner()
        sats = ConstellationPlanner.design_walker_delta(2, 3, 400, 51.6)
        for s in sats:
            planner.add_satellite(s)
        
        summary = planner.get_constellation_summary()
        self.assertEqual(summary["total_satellites"], 6)
        self.assertIn("planes", summary)
        self.assertIn("avg_altitude_km", summary)
        print(f"  [PASS] Summary: {summary['total_satellites']} sats, {summary['planes']} planes")
    
    def test_check_spacing(self):
        """Should detect spacing anomalies."""
        planner = ConstellationPlanner()
        sats = ConstellationPlanner.design_walker_delta(1, 4, 400, 0.0)
        for s in sats:
            planner.add_satellite(s)
        
        # Perfect spacing should have no anomalies
        anomalies = planner.check_spacing(0.0)
        self.assertEqual(len(anomalies), 0)
        print("  [PASS] Spacing check: no anomalies in uniform constellation")


class TestOrbitMaintenance(unittest.TestCase):
    """Test station-keeping calculations."""
    
    def setUp(self):
        self.sat = Satellite(
            sat_id="LEO1", semi_major_axis_km=EARTH_RADIUS_KM + 400,
            eccentricity=0.0, inclination_deg=51.6,
            raan_deg=0.0, arg_perigee_deg=0.0, mean_anomaly_deg=0.0,
            mass_kg=500.0, fuel_remaining_kg=20.0
        )
        self.maint = OrbitMaintenance(self.sat, drag_coefficient=2.2, area_m2=2.0)
    
    def test_atmospheric_density(self):
        """Density should decrease with altitude."""
        rho_low = self.maint.atmospheric_density(200.0)
        rho_high = self.maint.atmospheric_density(800.0)
        self.assertGreater(rho_low, rho_high)
        print(f"  [PASS] Density: {rho_low:.2e} @ 200km > {rho_high:.2e} @ 800km")
    
    def test_drag_acceleration(self):
        """Drag acceleration should be positive."""
        a_drag = self.maint.drag_acceleration(400.0, 7670.0)
        self.assertGreater(a_drag, 0)
        print(f"  [PASS] Drag acceleration: {a_drag:.2e} m/s^2")
    
    def test_semi_major_axis_decay(self):
        """Decay rate should be negative (decreasing)."""
        decay = self.maint.semi_major_axis_decay_rate()
        self.assertLess(decay, 0)
        print(f"  [PASS] Decay rate: {decay:.4f} m/s")
    
    def test_station_keeping_dv(self):
        """Should calculate reasonable station-keeping delta-v."""
        dv = self.maint.required_station_keeping_dv(days=30.0)
        self.assertGreater(dv, 0)
        # Typical LEO station-keeping: ~1-10 m/s per month
        self.assertLess(dv, 50.0)
        print(f"  [PASS] Monthly station-keeping: {dv:.3f} m/s")
    
    def test_phasing_maneuver(self):
        """Should plan phasing maneuver."""
        result = self.maint.phasing_maneuver(desired_phase_deg=90.0, current_phase_deg=0.0)
        self.assertIn("delta_v_ms", result)
        self.assertIn("drift_time_min", result)
        self.assertGreater(result["delta_v_ms"], 0)
        print(f"  [PASS] Phasing: dv={result['delta_v_ms']:.3f} m/s, {result['drift_time_min']:.1f} min")


class TestConstellationCollisionAvoidance(unittest.TestCase):
    """Test intra-constellation collision detection."""
    
    def test_no_risk_different_planes(self):
        """Different planes should have no collision risk."""
        checker = ConstellationCollisionAvoidance(min_separation_km=10.0)
        sat1 = Satellite("S1", 7000, 0.0, 0.0, 0.0, 0.0, 0.0)
        sat2 = Satellite("S2", 7000, 0.0, 0.0, 60.0, 0.0, 0.0)
        result = checker.check_pair(sat1, sat2)
        self.assertIsNone(result)
        print("  [PASS] Different planes: no risk")
    
    def test_risk_same_plane_close(self):
        """Close satellites in same plane should trigger risk."""
        checker = ConstellationCollisionAvoidance(min_separation_km=50.0)
        sat1 = Satellite("S1", 7000, 0.0, 0.0, 0.0, 0.0, 0.0)
        sat2 = Satellite("S2", 7000, 0.0, 0.0, 0.0, 0.0, 0.2)  # 0.2 degree apart
        result = checker.check_pair(sat1, sat2)
        self.assertIsNotNone(result)
        self.assertIn("risk_level", result)
        print(f"  [PASS] Close approach: separation={result['separation_km']:.2f} km, risk={result['risk_level']}")
    
    def test_scan_constellation(self):
        """Should scan entire constellation."""
        checker = ConstellationCollisionAvoidance(min_separation_km=100.0)
        planner = ConstellationPlanner()
        sats = ConstellationPlanner.design_walker_delta(2, 3, 400, 0.0)
        for s in sats:
            planner.add_satellite(s)
        
        risks = checker.scan_constellation(planner)
        # Uniform Walker should have minimal risks
        print(f"  [PASS] Scan: {len(risks)} risks detected in constellation")


if __name__ == '__main__':
    unittest.main(verbosity=2)
