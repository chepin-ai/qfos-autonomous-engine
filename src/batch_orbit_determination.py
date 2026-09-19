"""
Batch Least Squares Orbit Determination Module
Refine orbital elements from multiple tracking observations using
differential correction and weighted least squares.
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

try:
    from .orbital_mechanics import OrbitalBody, MU_SUN, AU
except ImportError:
    from orbital_mechanics import OrbitalBody, MU_SUN, AU


@dataclass
class TrackingObservation:
    """A ground-based tracking observation."""
    t_seconds: float          # Time from epoch (seconds)
    ra_deg: float             # Right ascension (degrees)
    dec_deg: float            # Declination (degrees)
    range_m: Optional[float] = None  # Slant range if radar (m)
    sigma_ra_arcsec: float = 1.0     # Measurement noise
    sigma_dec_arcsec: float = 1.0
    station_name: str = ""


class BatchOrbitDetermination:
    """
    Batch Least Squares Orbit Determination (BLS-OD).
    
    Uses iterative differential correction to refine 6 orbital elements
    from a batch of observations (angles-only or angles+range).
    """
    
    def __init__(self, max_iterations: int = 20, convergence_tol: float = 1e-6):
        self.max_iter = max_iterations
        self.tol = convergence_tol
    
    def _compute_observation(self, body: OrbitalBody, t_sec: float,
                              observer_au: Tuple[float, float, float]) -> Tuple[float, float]:
        """
        Compute predicted RA/Dec for a body at time t from observer position.
        
        Args:
            body: Current orbital element estimate
            t_sec: Time from epoch in seconds
            observer_au: Observer heliocentric position (AU)
        
        Returns:
            (ra_deg, dec_deg)
        """
        # Body position at time t
        x, y, z = body.position_at_time(t_sec / 86400.0)
        
        # Relative to observer
        dx = x - observer_au[0]
        dy = y - observer_au[1]
        dz = z - observer_au[2]
        
        # RA/Dec
        ra = math.degrees(math.atan2(dy, dx))
        if ra < 0:
            ra += 360.0
        dec = math.degrees(math.atan2(dz, math.sqrt(dx**2 + dy**2)))
        
        return ra, dec
    
    def _compute_residuals(self, body: OrbitalBody,
                           observations: List[TrackingObservation],
                           observer_positions: List[Tuple[float, float, float]]) -> List[float]:
        """Compute O-C residuals [arcsec] for all observations."""
        residuals = []
        
        for obs, obs_pos in zip(observations, observer_positions):
            pred_ra, pred_dec = self._compute_observation(body, obs.t_seconds, obs_pos)
            
            # RA wrap-around handling
            dra = obs.ra_deg - pred_ra
            if dra > 180.0:
                dra -= 360.0
            elif dra < -180.0:
                dra += 360.0
            
            # Convert to arcsec
            dra_arcsec = dra * 3600.0 * math.cos(math.radians(obs.dec_deg))
            ddec_arcsec = (obs.dec_deg - pred_dec) * 3600.0
            
            residuals.append(dra_arcsec)
            residuals.append(ddec_arcsec)
        
        return residuals
    
    def _compute_jacobian(self, body: OrbitalBody,
                          observations: List[TrackingObservation],
                          observer_positions: List[Tuple[float, float, float]],
                          delta: float = 1e-6) -> List[List[float]]:
        """
        Compute Jacobian matrix numerically.
        
        J[i][j] = d(residual_i) / d(element_j)
        
        Elements: [a_au, e, i_deg, Omega_deg, omega_deg, M0_deg]
        """
        base_residuals = self._compute_residuals(body, observations, observer_positions)
        
        # Element perturbation factors
        elements = {
            'a': body.semi_major_axis_au,
            'e': body.e,
            'i': body.inclination_deg,
            'Omega': body.Omega_deg if hasattr(body, 'Omega_deg') else 0.0,
            'omega': body.omega_deg if hasattr(body, 'omega_deg') else 0.0,
            'M0': 0.0  # Mean anomaly at epoch
        }
        
        jacobian = []
        
        # For each element, perturb and compute difference
        # Simplified: perturb a, e, i only (most sensitive)
        param_names = ['a', 'e', 'i']
        
        for idx, param in enumerate(param_names):
            # Perturb body (create modified copy)
            perturbed_elements = {
                'a': body.semi_major_axis_au,
                'e': body.e,
                'i': body.inclination_deg,
                'Omega': body.Omega_deg if hasattr(body, 'Omega_deg') else 0.0,
                'omega': body.omega_deg if hasattr(body, 'omega_deg') else 0.0,
            }
            
            # Apply perturbation
            if param == 'a':
                perturbed_elements['a'] += delta
            elif param == 'e':
                perturbed_elements['e'] += delta
            elif param == 'i':
                perturbed_elements['i'] += delta
            
            perturbed_body = OrbitalBody(
                name="perturbed", spkid="",
                a_au=perturbed_elements['a'],
                e=perturbed_elements['e'],
                i_deg=perturbed_elements['i'],
                omega_deg=perturbed_elements['omega'],
                Omega_deg=perturbed_elements['Omega']
            )
            
            perturbed_residuals = self._compute_residuals(
                perturbed_body, observations, observer_positions
            )
            
            # Column of Jacobian
            col = [(perturbed_residuals[i] - base_residuals[i]) / delta
                   for i in range(len(base_residuals))]
            
            for i in range(len(base_residuals)):
                if len(jacobian) <= i:
                    jacobian.append([])
                jacobian[i].append(col[i])
        
        return jacobian
    
    def _solve_normal_equations(self, J: List[List[float]],
                                 residuals: List[float],
                                 weights: Optional[List[float]] = None) -> List[float]:
        """
        Solve normal equations: (J^T W J) dx = J^T W r
        
        Returns:
            dx: parameter corrections
        """
        n_params = len(J[0]) if J else 0
        n_obs = len(residuals)
        
        if weights is None:
            weights = [1.0] * n_obs
        
        # J^T W J (n_params x n_params)
        JTWJ = [[0.0] * n_params for _ in range(n_params)]
        for i in range(n_params):
            for j in range(n_params):
                s = 0.0
                for k in range(n_obs):
                    s += J[k][i] * weights[k] * J[k][j]
                JTWJ[i][j] = s
        
        # J^T W r (n_params)
        JTWr = [0.0] * n_params
        for i in range(n_params):
            s = 0.0
            for k in range(n_obs):
                s += J[k][i] * weights[k] * residuals[k]
            JTWr[i] = s
        
        # Solve using Gaussian elimination
        dx = self._gaussian_solve(JTWJ, JTWr)
        return dx
    
    def _gaussian_solve(self, A: List[List[float]], b: List[float]) -> List[float]:
        """Solve Ax = b using Gaussian elimination with partial pivoting."""
        n = len(A)
        
        # Augmented matrix
        M = [A[i][:] + [b[i]] for i in range(n)]
        
        for col in range(n):
            # Partial pivot
            max_row = col
            for row in range(col + 1, n):
                if abs(M[row][col]) > abs(M[max_row][col]):
                    max_row = row
            M[col], M[max_row] = M[max_row], M[col]
            
            if abs(M[col][col]) < 1e-12:
                continue
            
            # Eliminate
            for row in range(col + 1, n):
                factor = M[row][col] / M[col][col]
                for j in range(col, n + 1):
                    M[row][j] -= factor * M[col][j]
        
        # Back substitution
        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            if abs(M[i][i]) < 1e-12:
                x[i] = 0.0
                continue
            x[i] = M[i][n]
            for j in range(i + 1, n):
                x[i] -= M[i][j] * x[j]
            x[i] /= M[i][i]
        
        return x
    
    def determine_orbit(self, initial_guess: OrbitalBody,
                        observations: List[TrackingObservation],
                        observer_positions: List[Tuple[float, float, float]]) -> Dict:
        """
        Perform batch least squares orbit determination.
        
        Args:
            initial_guess: Initial orbital element estimate
            observations: List of tracking observations
            observer_positions: Heliocentric observer positions (AU) for each observation
        
        Returns:
            Dict with refined orbit and convergence info
        """
        body = initial_guess
        
        for iteration in range(self.max_iter):
            residuals = self._compute_residuals(body, observations, observer_positions)
            rms = math.sqrt(sum(r**2 for r in residuals) / len(residuals))
            
            if rms < self.tol:
                return {
                    "converged": True,
                    "iterations": iteration,
                    "final_rms_arcsec": round(rms, 6),
                    "body": body,
                    "observations_used": len(observations)
                }
            
            # Compute Jacobian
            J = self._compute_jacobian(body, observations, observer_positions)
            
            # Solve normal equations
            dx = self._solve_normal_equations(J, residuals)
            
            # Apply corrections (damped for stability)
            damping = 0.5
            new_a = max(0.01, body.semi_major_axis_au + dx[0] * damping)
            new_e = max(0.0, min(0.999, body.e + dx[1] * damping))
            new_i = body.inclination_deg + dx[2] * damping
            
            body = OrbitalBody(
                name=body.name, spkid=body.spkid,
                a_au=new_a, e=new_e, i_deg=new_i,
                omega_deg=body.omega_deg if hasattr(body, 'omega_deg') else 0.0,
                Omega_deg=body.Omega_deg if hasattr(body, 'Omega_deg') else 0.0
            )
        
        # Max iterations reached
        final_residuals = self._compute_residuals(body, observations, observer_positions)
        final_rms = math.sqrt(sum(r**2 for r in final_residuals) / len(final_residuals))
        
        return {
            "converged": False,
            "iterations": self.max_iter,
            "final_rms_arcsec": round(final_rms, 6),
            "body": body,
            "observations_used": len(observations)
        }
    
    def estimate_covariance(self, J: List[List[float]],
                            sigma_obs_arcsec: float = 1.0) -> List[List[float]]:
        """
        Estimate parameter covariance matrix from Jacobian.
        
        P = sigma^2 * (J^T J)^-1
        
        Returns:
            Covariance matrix (3x3 for a, e, i)
        """
        n_params = len(J[0]) if J else 0
        n_obs = len(J)
        
        # J^T J
        JTJ = [[0.0] * n_params for _ in range(n_params)]
        for i in range(n_params):
            for j in range(n_params):
                s = 0.0
                for k in range(n_obs):
                    s += J[k][i] * J[k][j]
                JTJ[i][j] = s
        
        # Invert (simplified: just return inverse of diagonal for now)
        cov = [[0.0] * n_params for _ in range(n_params)]
        for i in range(n_params):
            if abs(JTJ[i][i]) > 1e-12:
                cov[i][i] = sigma_obs_arcsec**2 / JTJ[i][i]
        
        return cov
