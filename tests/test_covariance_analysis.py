"""
Unit tests for covariance analysis module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from covariance_analysis import (
    CovarianceMatrix, CovariancePropagator, ObservabilityAnalyzer, ErrorBudget
)


class TestCovarianceMatrix(unittest.TestCase):
    """Test covariance matrix."""
    
    def test_diagonal_creation(self):
        """Should create diagonal covariance."""
        cov = CovarianceMatrix.diagonal(pos_sigma_m=100.0, vel_sigma_m_s=0.1)
        self.assertAlmostEqual(cov.data[0][0], 10000.0, delta=0.1)
        self.assertAlmostEqual(cov.data[3][3], 0.01, delta=0.001)
        print("  [PASS] Diagonal creation")
    
    def test_position_uncertainty(self):
        """Should extract position uncertainty."""
        cov = CovarianceMatrix.diagonal(pos_sigma_m=50.0)
        sx, sy, sz = cov.position_uncertainty()
        self.assertEqual(sx, 50.0)
        print(f"  [PASS] Position sigma: ({sx:.1f}, {sy:.1f}, {sz:.1f}) m")
    
    def test_position_rms(self):
        """Should compute position RMS."""
        cov = CovarianceMatrix.diagonal(pos_sigma_m=10.0)
        rms = cov.position_rms()
        self.assertAlmostEqual(rms, math.sqrt(300), delta=0.1)
        print(f"  [PASS] Position RMS: {rms:.2f} m")


class TestCovariancePropagator(unittest.TestCase):
    """Test covariance propagation."""
    
    def setUp(self):
        self.prop = CovariancePropagator()
    
    def test_state_transition_matrix(self):
        """Should compute STM."""
        pos = (6678.0, 0.0, 0.0)
        vel = (0.0, 7.725, 0.0)
        Phi = self.prop.state_transition_matrix(pos, vel, dt_s=60.0)
        self.assertEqual(len(Phi), 6)
        self.assertEqual(len(Phi[0]), 6)
        print("  [PASS] STM: 6x6 matrix computed")
    
    def test_propagate(self):
        """Should propagate covariance."""
        cov = CovarianceMatrix.diagonal(pos_sigma_m=10.0)
        pos = (6678.0, 0.0, 0.0)
        vel = (0.0, 7.725, 0.0)
        cov_new = self.prop.propagate(cov, pos, vel, dt_s=60.0)
        self.assertGreater(cov_new.position_rms(), cov.position_rms())
        print(f"  [PASS] Propagation: {cov.position_rms():.2f} -> {cov_new.position_rms():.2f} m")
    
    def test_simulate_growth(self):
        """Should simulate uncertainty growth."""
        cov = CovarianceMatrix.diagonal(pos_sigma_m=10.0)
        trajectory = [((6678.0, 0.0, 0.0), (0.0, 7.725, 0.0))] * 5
        covariances = self.prop.simulate_uncertainty_growth(cov, trajectory, dt_s=60.0)
        self.assertEqual(len(covariances), 5)
        print(f"  [PASS] Growth: {len(covariances)} steps")


class TestObservabilityAnalyzer(unittest.TestCase):
    """Test observability analysis."""
    
    def setUp(self):
        self.analyzer = ObservabilityAnalyzer()
    
    def test_range_observability(self):
        """Should analyze range observability."""
        obs = self.analyzer.range_observability(geometry_factor=0.8)
        self.assertTrue(obs["position_observable"])
        self.assertFalse(obs["velocity_observable"])
        print("  [PASS] Range observability")
    
    def test_combined_observability(self):
        """Should analyze combined measurements."""
        obs = self.analyzer.combined_observability(["range", "angle", "doppler"])
        self.assertTrue(obs["full_state_observable"])
        print("  [PASS] Combined: full state observable")
    
    def test_partial_observability(self):
        """Should detect partial observability."""
        obs = self.analyzer.combined_observability(["range"])
        self.assertFalse(obs["full_state_observable"])
        print("  [PASS] Partial: not fully observable")


class TestErrorBudget(unittest.TestCase):
    """Test error budget."""
    
    def test_compute_budget(self):
        """Should compute error budget."""
        budget = ErrorBudget.compute_budget(
            measurement_sigma_m=10.0,
            clock_sigma_m=1.0,
            atmospheric_sigma_m=5.0
        )
        self.assertIn("total_rss_m", budget)
        self.assertGreater(budget["total_rss_m"], 0.0)
        print(f"  [PASS] Budget: total={budget['total_rss_m']:.2f} m")


if __name__ == '__main__':
    unittest.main(verbosity=2)
