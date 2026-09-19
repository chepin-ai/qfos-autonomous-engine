"""
Covariance Analysis Module
Navigation accuracy analysis using covariance propagation.
Supports orbit determination error budgets and observability analysis.
"""

import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class CovarianceMatrix:
    """6x6 position/velocity covariance matrix."""
    # Stored as list of lists: P[i][j]
    data: List[List[float]]
    
    @classmethod
    def diagonal(cls, pos_sigma_m: float = 100.0,
                 vel_sigma_m_s: float = 0.1) -> "CovarianceMatrix":
        """Create diagonal covariance."""
        P = [[0.0] * 6 for _ in range(6)]
        for i in range(3):
            P[i][i] = pos_sigma_m**2
            P[i+3][i+3] = vel_sigma_m_s**2
        return cls(P)
    
    def position_uncertainty(self) -> Tuple[float, float, float]:
        """Return 1-sigma position uncertainties in meters."""
        return (math.sqrt(self.data[0][0]),
                math.sqrt(self.data[1][1]),
                math.sqrt(self.data[2][2]))
    
    def velocity_uncertainty(self) -> Tuple[float, float, float]:
        """Return 1-sigma velocity uncertainties in m/s."""
        return (math.sqrt(self.data[3][3]),
                math.sqrt(self.data[4][4]),
                math.sqrt(self.data[5][5]))
    
    def position_rms(self) -> float:
        """RMS position uncertainty."""
        return math.sqrt(self.data[0][0] + self.data[1][1] + self.data[2][2])
    
    def velocity_rms(self) -> float:
        """RMS velocity uncertainty."""
        return math.sqrt(self.data[3][3] + self.data[4][4] + self.data[5][5])


class CovariancePropagator:
    """
    Propagate navigation covariance using state transition matrix.
    
    Models how orbit determination uncertainties grow
    between measurements.
    """
    
    def __init__(self, mu_km3_s2: float = 398600.4418):
        self.mu = mu_km3_s2
    
    def state_transition_matrix(self, position_km: Tuple[float, float, float],
                                 velocity_km_s: Tuple[float, float, float],
                                 dt_s: float) -> List[List[float]]:
        """
        Compute state transition matrix (STM) for orbital state.
        
        Uses simplified two-body STM.
        
        Returns:
            6x6 state transition matrix
        """
        # For small dt, approximate STM as identity + Jacobian * dt
        r = math.sqrt(sum(p**2 for p in position_km))
        if r < 1e-6:
            r = 1e-6
        
        # Jacobian of two-body dynamics
        # dx_dot/dx = [0, I; d(a)/dx, 0]
        # where d(a)/dx = -mu/r^3 * I + 3*mu/r^5 * x*x^T
        
        factor = self.mu / (r**3)
        factor3 = 3.0 * self.mu / (r**5)
        
        F = [[0.0] * 6 for _ in range(6)]
        
        # Position-velocity coupling
        for i in range(3):
            F[i][i+3] = 1.0
        
        # Acceleration Jacobian (in km/s^2 per km)
        for i in range(3):
            for j in range(3):
                F[i+3][j] = (-factor if i == j else 0.0) + \
                           factor3 * position_km[i] * position_km[j]
        
        # STM = I + F*dt (first order approximation)
        Phi = [[0.0] * 6 for _ in range(6)]
        for i in range(6):
            for j in range(6):
                Phi[i][j] = (1.0 if i == j else 0.0) + F[i][j] * dt_s
        
        return Phi
    
    def propagate(self, covariance: CovarianceMatrix,
                  position_km: Tuple[float, float, float],
                  velocity_km_s: Tuple[float, float, float],
                  dt_s: float,
                  process_noise_m2: float = 1.0) -> CovarianceMatrix:
        """
        Propagate covariance forward in time.
        
        P_new = Phi * P * Phi^T + Q
        
        Args:
            covariance: Current covariance
            position_km: Current position
            velocity_km_s: Current velocity
            dt_s: Time step
            process_noise_m2: Process noise added during propagation
        
        Returns:
            Propagated covariance
        """
        Phi = self.state_transition_matrix(position_km, velocity_km_s, dt_s)
        P = covariance.data
        
        # Phi * P
        temp = [[sum(Phi[i][k] * P[k][j] for k in range(6)) for j in range(6)]
                for i in range(6)]
        
        # (Phi * P) * Phi^T
        P_new = [[sum(temp[i][k] * Phi[j][k] for k in range(6)) for j in range(6)]
                 for i in range(6)]
        
        # Add process noise (simplified diagonal)
        for i in range(6):
            P_new[i][i] += process_noise_m2
        
        return CovarianceMatrix(P_new)
    
    def simulate_uncertainty_growth(self,
                                     initial_covariance: CovarianceMatrix,
                                     trajectory: List[Tuple[Tuple[float, float, float],
                                                            Tuple[float, float, float]]],
                                     dt_s: float = 60.0) -> List[CovarianceMatrix]:
        """
        Simulate covariance growth along trajectory.
        
        Args:
            initial_covariance: Starting covariance
            trajectory: List of (position, velocity) tuples
            dt_s: Time step between trajectory points
        
        Returns:
            List of covariance matrices
        """
        covariances = [initial_covariance]
        cov = initial_covariance
        
        for i in range(1, len(trajectory)):
            pos, vel = trajectory[i-1]
            cov = self.propagate(cov, pos, vel, dt_s)
            covariances.append(cov)
        
        return covariances


class ObservabilityAnalyzer:
    """
    Analyze observability of orbital states from measurements.
    
    Determines how well different measurement types
    constrain the orbit.
    """
    
    def __init__(self):
        pass
    
    def range_observability(self, geometry_factor: float = 1.0) -> Dict:
        """
        Observability from range measurements.
        
        Args:
            geometry_factor: 0-1, strength of geometry
        
        Returns:
            Observability metrics
        """
        return {
            "position_observable": True,
            "velocity_observable": False,
            "along_track_uncertainty": "high",
            "cross_track_uncertainty": "medium",
            "geometry_factor": round(geometry_factor, 3)
        }
    
    def angle_observability(self, geometry_factor: float = 1.0) -> Dict:
        """Observability from angle (RA/Dec) measurements."""
        return {
            "position_observable": True,
            "velocity_observable": True,
            "along_track_uncertainty": "medium",
            "cross_track_uncertainty": "low",
            "geometry_factor": round(geometry_factor, 3)
        }
    
    def doppler_observability(self, geometry_factor: float = 1.0) -> Dict:
        """Observability from Doppler measurements."""
        return {
            "position_observable": False,
            "velocity_observable": True,
            "along_track_uncertainty": "low",
            "cross_track_uncertainty": "high",
            "geometry_factor": round(geometry_factor, 3)
        }
    
    def combined_observability(self, measurements: List[str]) -> Dict:
        """
        Combined observability from multiple measurement types.
        
        Args:
            measurements: List of measurement types
        
        Returns:
            Combined observability assessment
        """
        has_range = "range" in measurements
        has_angle = "angle" in measurements
        has_doppler = "doppler" in measurements
        
        position_obs = has_range or has_angle
        velocity_obs = has_angle or has_doppler
        
        return {
            "position_observable": position_obs,
            "velocity_observable": velocity_obs,
            "full_state_observable": position_obs and velocity_obs,
            "measurement_types": measurements,
            "recommended": "range + angle + doppler" if not (has_range and has_angle and has_doppler) else "optimal"
        }


class ErrorBudget:
    """
    Navigation error budget calculator.
    
    Allocates errors across measurement and dynamic sources.
    """
    
    @staticmethod
    def compute_budget(measurement_sigma_m: float = 10.0,
                       dynamic_model_sigma_m_s2: float = 1e-6,
                       clock_sigma_m: float = 1.0,
                       atmospheric_sigma_m: float = 5.0) -> Dict:
        """
        Compute navigation error budget.
        
        Returns:
            Error allocation by source
        """
        # RSS combination
        total_rss = math.sqrt(measurement_sigma_m**2 +
                               dynamic_model_sigma_m_s2**2 * 1e12 +  # scale factor
                               clock_sigma_m**2 +
                               atmospheric_sigma_m**2)
        
        return {
            "measurement_error_m": round(measurement_sigma_m, 3),
            "dynamic_model_error_m": round(dynamic_model_sigma_m_s2 * 1e6, 6),
            "clock_error_m": round(clock_sigma_m, 3),
            "atmospheric_error_m": round(atmospheric_sigma_m, 3),
            "total_rss_m": round(total_rss, 3),
            "allocation_percent": {
                "measurement": round(measurement_sigma_m / total_rss * 100, 1),
                "dynamic": round(dynamic_model_sigma_m_s2 * 1e6 / total_rss * 100, 1),
                "clock": round(clock_sigma_m / total_rss * 100, 1),
                "atmospheric": round(atmospheric_sigma_m / total_rss * 100, 1)
            }
        }
