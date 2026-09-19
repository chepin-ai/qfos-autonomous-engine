"""
Extended Kalman Filter Module
State estimation for spacecraft using nonlinear dynamics and observation models.
"""

import math
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class EKFState:
    """EKF state vector and covariance."""
    x: List[float]        # State vector
    P: List[List[float]]  # Covariance matrix
    timestamp: float = 0.0


class MatrixOps:
    """Basic matrix operations for EKF."""
    
    @staticmethod
    def mat_mult(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Multiply two matrices."""
        rows_a = len(A)
        cols_a = len(A[0])
        cols_b = len(B[0])
        result = [[0.0] * cols_b for _ in range(rows_a)]
        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i][j] += A[i][k] * B[k][j]
        return result
    
    @staticmethod
    def mat_vec_mult(A: List[List[float]], v: List[float]) -> List[float]:
        """Multiply matrix by vector."""
        return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]
    
    @staticmethod
    def mat_add(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Add two matrices."""
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
    
    @staticmethod
    def mat_sub(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Subtract two matrices."""
        return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
    
    @staticmethod
    def mat_transpose(A: List[List[float]]) -> List[List[float]]:
        """Transpose matrix."""
        return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]
    
    @staticmethod
    def mat_scale(A: List[List[float]], s: float) -> List[List[float]]:
        """Scale matrix by scalar."""
        return [[A[i][j] * s for j in range(len(A[0]))] for i in range(len(A))]
    
    @staticmethod
    def identity(n: int) -> List[List[float]]:
        """Create identity matrix."""
        return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    
    @staticmethod
    def invert_2x2(A: List[List[float]]) -> Optional[List[List[float]]]:
        """Invert 2x2 matrix."""
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if abs(det) < 1e-12:
            return None
        return [[A[1][1] / det, -A[0][1] / det],
                [-A[1][0] / det, A[0][0] / det]]
    
    @staticmethod
    def invert_3x3(A: List[List[float]]) -> Optional[List[List[float]]]:
        """Invert 3x3 matrix using cofactor expansion."""
        det = (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
               A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
               A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
        if abs(det) < 1e-12:
            return None
        
        inv = [[0.0] * 3 for _ in range(3)]
        inv[0][0] = (A[1][1] * A[2][2] - A[1][2] * A[2][1]) / det
        inv[0][1] = (A[0][2] * A[2][1] - A[0][1] * A[2][2]) / det
        inv[0][2] = (A[0][1] * A[1][2] - A[0][2] * A[1][1]) / det
        inv[1][0] = (A[1][2] * A[2][0] - A[1][0] * A[2][2]) / det
        inv[1][1] = (A[0][0] * A[2][2] - A[0][2] * A[2][0]) / det
        inv[1][2] = (A[0][2] * A[1][0] - A[0][0] * A[1][2]) / det
        inv[2][0] = (A[1][0] * A[2][1] - A[1][1] * A[2][0]) / det
        inv[2][1] = (A[0][1] * A[2][0] - A[0][0] * A[2][1]) / det
        inv[2][2] = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) / det
        return inv


class ExtendedKalmanFilter:
    """
    Extended Kalman Filter for nonlinear state estimation.
    
    Supports generic state transition and observation models with
    numerical Jacobian computation.
    """
    
    def __init__(self, state_dim: int, measurement_dim: int):
        self.n = state_dim
        self.m = measurement_dim
        self.ops = MatrixOps()
    
    def predict(self, state: EKFState,
                state_transition: Callable[[List[float]], List[float]],
                F_jacobian: Optional[List[List[float]]] = None,
                Q: Optional[List[List[float]]] = None,
                dt: float = 1.0) -> EKFState:
        """
        Prediction step.
        
        Args:
            state: Current state estimate
            state_transition: Function x_k+1 = f(x_k)
            F_jacobian: State transition Jacobian (optional, computed numerically if None)
            Q: Process noise covariance
            dt: Time step
        
        Returns:
            Predicted state
        """
        # State prediction
        x_pred = state_transition(state.x)
        
        # Jacobian
        if F_jacobian is None:
            F = self._compute_jacobian(state_transition, state.x)
        else:
            F = F_jacobian
        
        # Covariance prediction: P = F * P * F^T + Q
        FP = self.ops.mat_mult(F, state.P)
        FT = self.ops.mat_transpose(F)
        FPFT = self.ops.mat_mult(FP, FT)
        
        if Q is None:
            Q = self.ops.mat_scale(self.ops.identity(self.n), 0.01)
        
        P_pred = self.ops.mat_add(FPFT, Q)
        
        return EKFState(x=x_pred, P=P_pred, timestamp=state.timestamp + dt)
    
    def update(self, state: EKFState,
               measurement: List[float],
               observation_model: Callable[[List[float]], List[float]],
               H_jacobian: Optional[List[List[float]]] = None,
               R: Optional[List[List[float]]] = None) -> EKFState:
        """
        Update step.
        
        Args:
            state: Predicted state
            measurement: Actual measurement
            observation_model: Function z = h(x)
            H_jacobian: Observation Jacobian (optional)
            R: Measurement noise covariance
        
        Returns:
            Updated state
        """
        # Predicted measurement
        z_pred = observation_model(state.x)
        
        # Innovation
        y = [measurement[i] - z_pred[i] for i in range(self.m)]
        
        # Observation Jacobian
        if H_jacobian is None:
            H = self._compute_jacobian(observation_model, state.x)
        else:
            H = H_jacobian
        
        # Innovation covariance: S = H * P * H^T + R
        HP = self.ops.mat_mult(H, state.P)
        HT = self.ops.mat_transpose(H)
        HPH = self.ops.mat_mult(HP, HT)
        
        if R is None:
            R = self.ops.mat_scale(self.ops.identity(self.m), 1.0)
        
        S = self.ops.mat_add(HPH, R)
        
        # Kalman gain: K = P * H^T * S^-1
        # For small matrices, compute inverse directly
        S_inv = self._invert_matrix(S)
        if S_inv is None:
            # Singular matrix, skip update
            return state
        
        PHT = self.ops.mat_mult(state.P, HT)
        K = self.ops.mat_mult(PHT, S_inv)
        
        # State update: x = x + K * y
        Ky = self.ops.mat_vec_mult(K, y)
        x_new = [state.x[i] + Ky[i] for i in range(self.n)]
        
        # Covariance update: P = (I - K * H) * P
        KH = self.ops.mat_mult(K, H)
        I_KH = self.ops.mat_sub(self.ops.identity(self.n), KH)
        P_new = self.ops.mat_mult(I_KH, state.P)
        
        return EKFState(x=x_new, P=P_new, timestamp=state.timestamp)
    
    def _compute_jacobian(self, func: Callable[[List[float]], List[float]],
                          x: List[float], delta: float = 1e-6) -> List[List[float]]:
        """Compute Jacobian numerically."""
        f0 = func(x)
        J = []
        
        for i in range(len(x)):
            x_perturbed = x[:]
            x_perturbed[i] += delta
            f_perturbed = func(x_perturbed)
            
            col = [(f_perturbed[j] - f0[j]) / delta for j in range(len(f0))]
            J.append(col)
        
        # Transpose to get J[j][i] = df_j/dx_i
        return [[J[i][j] for i in range(len(x))] for j in range(len(f0))]
    
    def _invert_matrix(self, A: List[List[float]]) -> Optional[List[List[float]]]:
        """Invert matrix based on size."""
        n = len(A)
        if n == 1:
            if abs(A[0][0]) < 1e-12:
                return None
            return [[1.0 / A[0][0]]]
        elif n == 2:
            return self.ops.invert_2x2(A)
        elif n == 3:
            return self.ops.invert_3x3(A)
        else:
            # Fallback to simple diagonal inverse
            return [[1.0 / A[i][i] if i == j and abs(A[i][i]) > 1e-12 else 0.0
                     for j in range(n)] for i in range(n)]


class OrbitEKF:
    """
    Specialized EKF for orbital state estimation.
    
    State: [x, y, z, vx, vy, vz] in km and km/s
    """
    
    MU_EARTH_KM3_S2 = 398600.4418
    
    def __init__(self):
        self.ekf = ExtendedKalmanFilter(state_dim=6, measurement_dim=3)
    
    def state_transition(self, x: List[float], dt_s: float) -> List[float]:
        """
        Propagate orbital state using simple two-body dynamics.
        
        Args:
            x: [x, y, z, vx, vy, vz]
            dt_s: Time step in seconds
        """
        r = math.sqrt(x[0]**2 + x[1]**2 + x[2]**2)
        if r < 1e-6:
            r = 1e-6
        
        # Acceleration
        a = -self.MU_EARTH_KM3_S2 / r**3
        ax = a * x[0]
        ay = a * x[1]
        az = a * x[2]
        
        # Simple Euler integration
        dt = dt_s
        return [
            x[0] + x[3] * dt + 0.5 * ax * dt**2,
            x[1] + x[4] * dt + 0.5 * ay * dt**2,
            x[2] + x[5] * dt + 0.5 * az * dt**2,
            x[3] + ax * dt,
            x[4] + ay * dt,
            x[5] + az * dt
        ]
    
    def position_observation(self, x: List[float]) -> List[float]:
        """Observe position only."""
        return [x[0], x[1], x[2]]
    
    def range_observation(self, x: List[float], station_pos_km: List[float]) -> List[float]:
        """Observe range to ground station."""
        dx = x[0] - station_pos_km[0]
        dy = x[1] - station_pos_km[1]
        dz = x[2] - station_pos_km[2]
        return [math.sqrt(dx**2 + dy**2 + dz**2)]
    
    def initialize(self, position_km: List[float], velocity_km_s: List[float],
                   pos_sigma_km: float = 1.0, vel_sigma_km_s: float = 0.1) -> EKFState:
        """Initialize EKF with position and velocity."""
        x0 = position_km + velocity_km_s
        
        P0 = [
            [pos_sigma_km**2, 0, 0, 0, 0, 0],
            [0, pos_sigma_km**2, 0, 0, 0, 0],
            [0, 0, pos_sigma_km**2, 0, 0, 0],
            [0, 0, 0, vel_sigma_km_s**2, 0, 0],
            [0, 0, 0, 0, vel_sigma_km_s**2, 0],
            [0, 0, 0, 0, 0, vel_sigma_km_s**2]
        ]
        
        return EKFState(x=x0, P=P0, timestamp=0.0)
    
    def filter_step(self, state: EKFState, dt_s: float,
                    measurement: List[float],
                    measurement_type: str = "position",
                    station_pos_km: Optional[List[float]] = None,
                    R: Optional[List[List[float]]] = None) -> EKFState:
        """
        Single prediction + update cycle.
        
        Args:
            state: Current state
            dt_s: Time step
            measurement: Measurement vector
            measurement_type: 'position' or 'range'
            station_pos_km: Ground station position for range measurements
            R: Measurement noise covariance
        """
        # Predict
        def f(x):
            return self.state_transition(x, dt_s)
        
        state_pred = self.ekf.predict(state, f, Q=None, dt=dt_s)
        
        # Update
        if measurement_type == "position":
            h = self.position_observation
            if R is None:
                R = [[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]]
        elif measurement_type == "range":
            def h(x):
                return self.range_observation(x, station_pos_km or [0, 0, 0])
            if R is None:
                R = [[0.1]]
        else:
            return state_pred
        
        return self.ekf.update(state_pred, measurement, h, R=R)
