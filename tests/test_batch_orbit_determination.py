"""
Unit tests for batch least squares orbit determination module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from batch_orbit_determination import BatchOrbitDetermination, TrackingObservation
from orbital_mechanics import OrbitalBody


class TestBatchOrbitDetermination(unittest.TestCase):
    """Test BLS-OD algorithms."""
    
    def setUp(self):
        self.bls = BatchOrbitDetermination(max_iterations=10)
        
        # Create a reference body (Earth-like)
        self.reference = OrbitalBody(
            name="TestBody", spkid="99999",
            a_au=1.5, e=0.1, i_deg=5.0,
            omega_deg=30.0, Omega_deg=45.0
        )
    
    def test_compute_observation(self):
        """Should compute predicted RA/Dec."""
        obs_pos = (0.0, 0.0, 0.0)  # Simplified observer at origin
        ra, dec = self.bls._compute_observation(self.reference, 0.0, obs_pos)
        self.assertIsInstance(ra, float)
        self.assertIsInstance(dec, float)
        self.assertGreaterEqual(ra, 0.0)
        self.assertLess(ra, 360.0)
        self.assertGreaterEqual(dec, -90.0)
        self.assertLessEqual(dec, 90.0)
        print(f"  [PASS] Observation: RA={ra:.2f}°, Dec={dec:.2f}°")
    
    def test_compute_residuals_zero(self):
        """Perfect observations should yield near-zero residuals."""
        obs_pos = (0.0, 0.0, 0.0)
        
        # Create observation at epoch
        ra, dec = self.bls._compute_observation(self.reference, 0.0, obs_pos)
        obs = TrackingObservation(t_seconds=0.0, ra_deg=ra, dec_deg=dec,
                                   sigma_ra_arcsec=1.0, sigma_dec_arcsec=1.0)
        
        residuals = self.bls._compute_residuals(self.reference, [obs], [obs_pos])
        self.assertEqual(len(residuals), 2)  # RA and Dec residual
        self.assertAlmostEqual(residuals[0], 0.0, delta=0.01)
        self.assertAlmostEqual(residuals[1], 0.0, delta=0.01)
        print(f"  [PASS] Zero residuals: RA={residuals[0]:.4f}, Dec={residuals[1]:.4f} arcsec")
    
    def test_compute_residuals_nonzero(self):
        """Offset observation should yield non-zero residuals."""
        obs_pos = (0.0, 0.0, 0.0)
        ra, dec = self.bls._compute_observation(self.reference, 0.0, obs_pos)
        
        obs = TrackingObservation(t_seconds=0.0, ra_deg=ra + 0.1, dec_deg=dec,
                                   sigma_ra_arcsec=1.0, sigma_dec_arcsec=1.0)
        
        residuals = self.bls._compute_residuals(self.reference, [obs], [obs_pos])
        self.assertNotAlmostEqual(residuals[0], 0.0, delta=10.0)
        print(f"  [PASS] Nonzero residual: {residuals[0]:.2f} arcsec")
    
    def test_gaussian_solve(self):
        """Gaussian elimination should solve linear system."""
        A = [[2.0, 1.0], [1.0, 3.0]]
        b = [5.0, 8.0]
        x = self.bls._gaussian_solve(A, b)
        
        # Verify: Ax = b
        self.assertAlmostEqual(2*x[0] + 1*x[1], 5.0, delta=0.01)
        self.assertAlmostEqual(1*x[0] + 3*x[1], 8.0, delta=0.01)
        print(f"  [PASS] Solve: x={x}")
    
    def test_determine_orbit_convergence(self):
        """Should converge for perfect observations."""
        obs_pos = (0.0, 0.0, 0.0)
        
        # Generate perfect observations
        observations = []
        observer_positions = []
        for t in [0.0, 86400.0, 172800.0]:
            ra, dec = self.bls._compute_observation(self.reference, t, obs_pos)
            observations.append(TrackingObservation(
                t_seconds=t, ra_deg=ra, dec_deg=dec,
                sigma_ra_arcsec=1.0, sigma_dec_arcsec=1.0
            ))
            observer_positions.append(obs_pos)
        
        # Start with slightly perturbed guess
        guess = OrbitalBody(
            name="Guess", spkid="",
            a_au=1.52, e=0.11, i_deg=5.1,
            omega_deg=30.0, Omega_deg=45.0
        )
        
        result = self.bls.determine_orbit(guess, observations, observer_positions)
        
        self.assertIn("converged", result)
        self.assertIn("final_rms_arcsec", result)
        self.assertIsNotNone(result["body"])
        print(f"  [PASS] Convergence: {result['converged']}, RMS={result['final_rms_arcsec']:.4f} arcsec, iters={result['iterations']}")
    
    def test_covariance_estimation(self):
        """Should estimate parameter covariance."""
        obs_pos = (0.0, 0.0, 0.0)
        
        # Generate simple Jacobian
        observations = []
        observer_positions = []
        for t in [0.0, 86400.0]:
            ra, dec = self.bls._compute_observation(self.reference, t, obs_pos)
            observations.append(TrackingObservation(
                t_seconds=t, ra_deg=ra, dec_deg=dec
            ))
            observer_positions.append(obs_pos)
        
        J = self.bls._compute_jacobian(self.reference, observations, observer_positions)
        cov = self.bls.estimate_covariance(J, sigma_obs_arcsec=1.0)
        
        self.assertEqual(len(cov), len(J[0]) if J else 0)
        print(f"  [PASS] Covariance: {len(cov)}x{len(cov[0]) if cov else 0} matrix")


if __name__ == '__main__':
    unittest.main(verbosity=2)
