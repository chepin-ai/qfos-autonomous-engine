"""
Unit tests for radio science module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from radio_science import (
    GravityFieldEstimator, OccultationAnalyzer, OccultationGeometry,
    DopplerMeasurement, RadioScienceSummary
)


class TestGravityFieldEstimator(unittest.TestCase):
    """Test gravity field estimation."""
    
    def test_initialization(self):
        """Should initialize with mu."""
        est = GravityFieldEstimator(398600.4418)
        self.assertEqual(est.mu, 398600.4418)
        print("  [PASS] Init")
    
    def test_for_planet(self):
        """Should create for named planet."""
        est = GravityFieldEstimator.for_planet("Mars")
        self.assertAlmostEqual(est.mu, 42828.375214, delta=0.1)
        print("  [PASS] Planet factory")
    
    def test_compute_range_rate(self):
        """Should compute range rate."""
        est = GravityFieldEstimator.for_planet("Earth")
        sc_pos = (7000.0, 0.0, 0.0)
        sc_vel = (0.0, 7.5, 0.0)
        gs_pos = (6378.0, 0.0, 0.0)
        
        rr = est.compute_range_rate(sc_pos, sc_vel, gs_pos)
        self.assertIsNotNone(rr)
        print(f"  [PASS] Range rate: {rr:.2f} m/s")
    
    def test_gravity_anomaly(self):
        """Should compute J2 acceleration."""
        est = GravityFieldEstimator()
        ax, ay, az = est.gravity_anomaly_acceleration((7000.0, 0.0, 0.0))
        self.assertNotEqual(ax, 0.0)
        print(f"  [PASS] J2: ({ax:.6f}, {ay:.6f}, {az:.6f}) m/s^2")
    
    def test_estimate_j2(self):
        """Should estimate J2 from residuals."""
        est = GravityFieldEstimator()
        measurements = [
            DopplerMeasurement(0.0, 100.0, 0.001),
            DopplerMeasurement(60.0, 100.1, 0.001),
            DopplerMeasurement(120.0, 100.2, 0.001),
        ]
        positions = [(7000.0, 0.0, 0.0)] * 3
        velocities = [(0.0, 7.5, 0.0)] * 3
        
        result = est.estimate_j2_from_residuals(measurements, positions, velocities)
        self.assertIn("j2_estimate", result)
        self.assertIsNotNone(result["rms_residual_ms"])
        print(f"  [PASS] J2 estimate: {result['j2_estimate']}, RMS={result['rms_residual_ms']:.4f}")


class TestOccultationAnalyzer(unittest.TestCase):
    """Test occultation analysis."""
    
    def setUp(self):
        geo = OccultationGeometry(
            planet_radius_km=3390.0,
            atmosphere_scale_height_km=11.0
        )
        self.analyzer = OccultationAnalyzer(geo)
    
    def test_refraction_angle(self):
        """Should compute refraction angle."""
        alpha = self.analyzer.compute_refraction_angle(3400.0, 0.02)
        self.assertGreaterEqual(alpha, 0.0)
        print(f"  [PASS] Refraction: {alpha:.2e} rad")
    
    def test_signal_attenuation(self):
        """Should compute signal attenuation."""
        atten = self.analyzer.compute_signal_attenuation(3400.0)
        self.assertGreater(atten, 0.0)
        print(f"  [PASS] Attenuation: {atten:.2f} dB")
    
    def test_occultation_profile(self):
        """Should generate occultation profile."""
        ips = [3390.0, 3395.0, 3400.0, 3410.0, 3450.0]
        profile = self.analyzer.generate_occultation_profile(ips, base_density_kg_m3=0.02)
        self.assertEqual(len(profile["refraction_angles_rad"]), 5)
        self.assertEqual(len(profile["attenuation_db"]), 5)
        self.assertEqual(len(profile["temperature_k"]), 5)
        print("  [PASS] Occultation profile")
    
    def test_find_occultation_events(self):
        """Should find occultation events."""
        trajectory = [
            (10000.0, 0.0, 0.0),
            (5000.0, 0.0, 0.0),
            (3500.0, 0.0, 0.0),   # Inside occultation
            (2000.0, 0.0, 0.0),   # Inside
            (5000.0, 0.0, 0.0),
            (10000.0, 0.0, 0.0),
        ]
        events = self.analyzer.find_occultation_events(trajectory, (0.0, 0.0, 0.0))
        self.assertGreaterEqual(len(events), 1)
        print(f"  [PASS] Events: {len(events)} found")
    
    def test_below_surface_attenuation(self):
        """Below surface should have total attenuation."""
        atten = self.analyzer.compute_signal_attenuation(3380.0)
        self.assertEqual(atten, 100.0)
        print("  [PASS] Below surface = total loss")


class TestRadioScienceSummary(unittest.TestCase):
    """Test summary report."""
    
    def test_generate_report(self):
        """Should generate summary report."""
        est = GravityFieldEstimator()
        geo = OccultationGeometry(planet_radius_km=6378.0, atmosphere_scale_height_km=8.5)
        analyzer = OccultationAnalyzer(geo)
        
        report = RadioScienceSummary.generate_report(est, analyzer)
        self.assertIn("central_body_mu_km3_s2", report)
        self.assertEqual(report["occultation_experiments"], 1)
        print("  [PASS] Summary report")


if __name__ == '__main__':
    unittest.main(verbosity=2)
