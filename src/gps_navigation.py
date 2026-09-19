"""
GPS Navigation Module
GNSS receiver models: satellite position computation, pseudorange,
least-squares position fix, and DOP analysis.
"""

import math
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass


@dataclass
class GPSSatellite:
    """GPS satellite ephemeris data."""
    prn: int
    a_km: float = 26560.0  # Semi-major axis (~20200 km altitude)
    e: float = 0.0
    i_deg: float = 55.0
    raan_deg: float = 0.0
    arg_perigee_deg: float = 0.0
    mean_anomaly_deg: float = 0.0
    
    # Almanac orbital rate
    n_revs_day: float = 2.0  # GPS: 2 orbits per sidereal day


@dataclass
class Pseudorange:
    """Pseudorange measurement."""
    prn: int
    range_m: float
    prn_noise_m: float = 0.0  # Simulated noise


class GPSSatellitePosition:
    """Compute GPS satellite positions from simplified almanac."""
    
    MU_KM3_S2 = 398600.4418
    
    def __init__(self, satellites: List[GPSSatellite]):
        self.satellites = {s.prn: s for s in satellites}
    
    def compute_position(self, prn: int, gps_week: int, tow_s: float) -> Tuple[float, float, float]:
        """
        Compute satellite position at given GPS time.
        
        Args:
            prn: Satellite PRN
            gps_week: GPS week number
            tow_s: Time of week in seconds
        
        Returns:
            (x, y, z) in km (ECI-like frame)
        """
        sat = self.satellites.get(prn)
        if not sat:
            raise ValueError(f"Unknown PRN {prn}")
        
        # Mean motion
        n = sat.n_revs_day * 2.0 * math.pi / 86400.0
        
        # Mean anomaly at time
        M = math.radians(sat.mean_anomaly_deg) + n * (gps_week * 604800.0 + tow_s)
        M = M % (2.0 * math.pi)
        
        # Eccentric anomaly (iterative)
        e = sat.e
        E = M
        for _ in range(10):
            f = E - e * math.sin(E) - M
            fp = 1.0 - e * math.cos(E)
            E -= f / fp
        
        # True anomaly
        sin_E = math.sin(E)
        cos_E = math.cos(E)
        sqrt_1me2 = math.sqrt(1.0 - e**2)
        sin_nu = sqrt_1me2 * sin_E / (1.0 - e * cos_E)
        cos_nu = (cos_E - e) / (1.0 - e * cos_E)
        nu = math.atan2(sin_nu, cos_nu)
        
        # Distance
        r = sat.a_km * (1.0 - e * cos_E)
        
        # Orbital plane position
        x_orb = r * cos_nu
        y_orb = r * sin_nu
        
        # Rotate to ECI
        i = math.radians(sat.i_deg)
        raan = math.radians(sat.raan_deg)
        omega = math.radians(sat.arg_perigee_deg)
        
        cos_raan = math.cos(raan)
        sin_raan = math.sin(raan)
        cos_omega = math.cos(omega)
        sin_omega = math.sin(omega)
        cos_i = math.cos(i)
        sin_i = math.sin(i)
        
        R11 = cos_raan * cos_omega - sin_raan * sin_omega * cos_i
        R12 = -cos_raan * sin_omega - sin_raan * cos_omega * cos_i
        R21 = sin_raan * cos_omega + cos_raan * sin_omega * cos_i
        R22 = -sin_raan * sin_omega + cos_raan * cos_omega * cos_i
        R31 = sin_omega * sin_i
        R32 = cos_omega * sin_i
        
        return (
            R11 * x_orb + R12 * y_orb,
            R21 * x_orb + R22 * y_orb,
            R31 * x_orb + R32 * y_orb
        )


class GPSReceiver:
    """
    GPS receiver navigation solution.
    
    Computes position from pseudorange measurements using
    weighted least-squares.
    """
    
    SPEED_OF_LIGHT_M_S = 299792458.0
    
    def __init__(self, sat_position: GPSSatellitePosition):
        self.sat_position = sat_position
    
    def compute_pseudorange(self, prn: int, receiver_pos_m: Tuple[float, float, float],
                           gps_week: int, tow_s: float,
                           clock_bias_m: float = 0.0,
                           noise_m: float = 0.0) -> Pseudorange:
        """
        Compute simulated pseudorange to satellite.
        
        Args:
            prn: Satellite PRN
            receiver_pos_m: Receiver position (m)
            gps_week: GPS week
            tow_s: Time of week
            clock_bias_m: Receiver clock bias in meters
            noise_m: Measurement noise
        
        Returns:
            Pseudorange measurement
        """
        sat_pos_km = self.sat_position.compute_position(prn, gps_week, tow_s)
        sat_pos_m = (sat_pos_km[0] * 1000.0, sat_pos_km[1] * 1000.0, sat_pos_km[2] * 1000.0)
        
        dx = sat_pos_m[0] - receiver_pos_m[0]
        dy = sat_pos_m[1] - receiver_pos_m[1]
        dz = sat_pos_m[2] - receiver_pos_m[2]
        
        geometric_range = math.sqrt(dx**2 + dy**2 + dz**2)
        pseudorange = geometric_range + clock_bias_m + noise_m
        
        return Pseudorange(prn=prn, range_m=pseudorange, prn_noise_m=noise_m)
    
    def solve_position(self, pseudoranges: List[Pseudorange],
                       gps_week: int, tow_s: float,
                       initial_guess_m: Optional[Tuple[float, float, float]] = None,
                       max_iterations: int = 10,
                       tol_m: float = 0.1) -> Dict:
        """
        Solve receiver position from pseudoranges.
        
        Uses iterative least-squares (Gauss-Newton).
        
        Args:
            pseudoranges: List of pseudorange measurements
            gps_week: GPS week
            tow_s: Time of week
            initial_guess_m: Initial position guess
            max_iterations: Max iterations
            tol_m: Convergence tolerance
        
        Returns:
            Dictionary with position, clock_bias, residuals, DOP
        """
        if len(pseudoranges) < 4:
            raise ValueError("Need at least 4 satellites for 3D fix")
        
        # Initial guess
        if initial_guess_m:
            x, y, z = initial_guess_m
        else:
            x, y, z = 0.0, 0.0, 0.0
        
        clock_bias = 0.0
        
        for iteration in range(max_iterations):
            # Build geometry matrix and residual vector
            H_rows = []
            residuals = []
            
            for pr in pseudoranges:
                sat_pos_km = self.sat_position.compute_position(pr.prn, gps_week, tow_s)
                sat_pos_m = (sat_pos_km[0] * 1000.0, sat_pos_km[1] * 1000.0, sat_pos_km[2] * 1000.0)
                
                dx = sat_pos_m[0] - x
                dy = sat_pos_m[1] - y
                dz = sat_pos_m[2] - z
                
                predicted_range = math.sqrt(dx**2 + dy**2 + dz**2)
                
                # Line-of-sight unit vector
                los_x = dx / predicted_range
                los_y = dy / predicted_range
                los_z = dz / predicted_range
                
                H_rows.append([los_x, los_y, los_z, 1.0])
                residuals.append(pr.range_m - (predicted_range + clock_bias))
            
            # Normal equations: (H^T H + lambda*I) dx = H^T residual
            n = len(pseudoranges)
            
            # H^T H (4x4)
            HtH = [[0.0] * 4 for _ in range(4)]
            for i in range(4):
                for j in range(4):
                    for k in range(n):
                        HtH[i][j] += H_rows[k][i] * H_rows[k][j]
            
            # Ridge regularization for numerical stability
            for i in range(4):
                HtH[i][i] += 0.001
            
            # H^T residual (4x1)
            HtR = [0.0] * 4
            for i in range(4):
                for k in range(n):
                    HtR[i] += H_rows[k][i] * residuals[k]
            
            # Solve using simple Gaussian elimination (4x4)
            dx_solution = self._solve_4x4(HtH, HtR)
            
            # Damped Gauss-Newton for stability
            damping = 0.5 if iteration < 3 else 1.0
            x += dx_solution[0] * damping
            y += dx_solution[1] * damping
            z += dx_solution[2] * damping
            clock_bias += dx_solution[3] * damping
            
            correction_mag = math.sqrt(sum((d*damping)**2 for d in dx_solution[:3]))
            if correction_mag < tol_m:
                break
        
        # Compute DOP
        dop = self._compute_dop(H_rows)
        
        # Final residuals
        final_residuals = []
        for pr in pseudoranges:
            sat_pos_km = self.sat_position.compute_position(pr.prn, gps_week, tow_s)
            sat_pos_m = (sat_pos_km[0] * 1000.0, sat_pos_km[1] * 1000.0, sat_pos_km[2] * 1000.0)
            dx = sat_pos_m[0] - x
            dy = sat_pos_m[1] - y
            dz = sat_pos_m[2] - z
            predicted = math.sqrt(dx**2 + dy**2 + dz**2)
            final_residuals.append(pr.range_m - (predicted + clock_bias))
        
        return {
            "position_m": (round(x, 3), round(y, 3), round(z, 3)),
            "clock_bias_m": round(clock_bias, 3),
            "gdop": round(dop["gdop"], 3),
            "pdop": round(dop["pdop"], 3),
            "hdop": round(dop["hdop"], 3),
            "vdop": round(dop["vdop"], 3),
            "tdop": round(dop["tdop"], 3),
            "residuals_m": [round(r, 3) for r in final_residuals],
            "num_satellites": len(pseudoranges),
            "converged": correction_mag < tol_m
        }
    
    def _solve_4x4(self, A: List[List[float]], b: List[float]) -> List[float]:
        """Solve 4x4 linear system using Gaussian elimination with partial pivoting."""
        n = 4
        # Augmented matrix
        M = [A[i][:] + [b[i]] for i in range(n)]
        
        for col in range(n):
            # Partial pivot
            max_row = col
            max_val = abs(M[col][col])
            for row in range(col + 1, n):
                if abs(M[row][col]) > max_val:
                    max_val = abs(M[row][col])
                    max_row = row
            M[col], M[max_row] = M[max_row], M[col]
            
            if abs(M[col][col]) < 1e-15:
                continue
            
            # Eliminate below
            for row in range(col + 1, n):
                factor = M[row][col] / M[col][col]
                for j in range(col, n + 1):
                    M[row][j] -= factor * M[col][j]
        
        # Back substitution
        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            x[i] = M[i][n]
            for j in range(i + 1, n):
                x[i] -= M[i][j] * x[j]
            if abs(M[i][i]) > 1e-15:
                x[i] /= M[i][i]
        
        return x
    
    def _compute_dop(self, H_rows: List[List[float]]) -> Dict:
        """Compute DOP from geometry matrix."""
        n = len(H_rows)
        
        # H^T H
        HtH = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(n):
                    HtH[i][j] += H_rows[k][i] * H_rows[k][j]
        
        # Invert (simplified diagonal approximation)
        # For full accuracy, we'd do full matrix inversion
        Q = self._invert_4x4(HtH)
        
        if Q:
            q11, q22, q33, q44 = Q[0][0], Q[1][1], Q[2][2], Q[3][3]
            
            gdop = math.sqrt(q11 + q22 + q33 + q44)
            pdop = math.sqrt(q11 + q22 + q33)
            hdop = math.sqrt(q11 + q22)
            vdop = math.sqrt(q33)
            tdop = math.sqrt(q44)
        else:
            gdop = pdop = hdop = vdop = tdop = float('inf')
        
        return {
            "gdop": gdop, "pdop": pdop, "hdop": hdop,
            "vdop": vdop, "tdop": tdop
        }
    
    def _invert_4x4(self, A: List[List[float]]) -> Optional[List[List[float]]]:
        """Compute inverse of 4x4 matrix."""
        n = 4
        # Augmented with identity
        M = [A[i][:] + [1.0 if j == i else 0.0 for j in range(n)] for i in range(n)]
        
        for col in range(n):
            max_row = col
            max_val = abs(M[col][col])
            for row in range(col + 1, n):
                if abs(M[row][col]) > max_val:
                    max_val = abs(M[row][col])
                    max_row = row
            M[col], M[max_row] = M[max_row], M[col]
            
            if abs(M[col][col]) < 1e-15:
                return None
            
            pivot = M[col][col]
            for j in range(2 * n):
                M[col][j] /= pivot
            
            for row in range(n):
                if row != col:
                    factor = M[row][col]
                    for j in range(2 * n):
                        M[row][j] -= factor * M[col][j]
        
        return [row[n:] for row in M]


def create_gps_constellation() -> List[GPSSatellite]:
    """Create a simplified 24-satellite GPS constellation."""
    satellites = []
    
    # 6 orbital planes, 4 satellites each
    for plane in range(6):
        raan = plane * 60.0
        for sat_in_plane in range(4):
            mean_anomaly = sat_in_plane * 90.0
            prn = plane * 4 + sat_in_plane + 1
            # Add small eccentricity for realistic geometry
            e = 0.002 + (prn % 5) * 0.001
            a_km = 26560.0 + (prn % 7) * 5.0
            satellites.append(GPSSatellite(
                prn=prn,
                a_km=a_km,
                e=e,
                i_deg=55.0,
                raan_deg=raan,
                arg_perigee_deg=prn * 15.0,
                mean_anomaly_deg=mean_anomaly
            ))
    
    return satellites
