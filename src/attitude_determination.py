"""
Attitude Determination Module
QUEST algorithm, Wahba's problem solver, and star
tracker simulation for spacecraft attitude estimation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Quaternion:
    """Quaternion attitude representation."""
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def normalize(self):
        """Normalize quaternion."""
        norm = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if norm > 0:
            self.w /= norm
            self.x /= norm
            self.y /= norm
            self.z /= norm
    
    def to_rotation_matrix(self) -> List[List[float]]:
        """Convert to rotation matrix."""
        w, x, y, z = self.w, self.x, self.y, self.z
        return [
            [1 - 2*(y*y + z*z), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x*x + z*z), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x*x + y*y)]
        ]
    
    @classmethod
    def from_axis_angle(cls, axis: Tuple[float, float, float], angle: float) -> "Quaternion":
        """Create quaternion from axis-angle."""
        ax, ay, az = axis
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm == 0:
            return cls(1, 0, 0, 0)
        ax, ay, az = ax/norm, ay/norm, az/norm
        half = angle / 2
        return cls(math.cos(half), ax * math.sin(half), ay * math.sin(half), az * math.sin(half))
    
    def conjugate(self) -> "Quaternion":
        """Quaternion conjugate."""
        return Quaternion(self.w, -self.x, -self.y, -self.z)
    
    def rotate_vector(self, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Rotate a vector by this quaternion."""
        # q * v * q^*
        vx, vy, vz = v
        qw, qx, qy, qz = self.w, self.x, self.y, self.z
        
        rx = qw*qw*vx + 2*qy*qw*vz - 2*qz*qw*vy + qx*qx*vx + 2*qy*qx*vy + 2*qz*qx*vz - qz*qz*vx - qy*qy*vx
        ry = 2*qx*qy*vx + qy*qy*vy + 2*qz*qy*vz + 2*qw*qz*vx - qz*qz*vy + qw*qw*vy - 2*qx*qw*vz - qx*qx*vy
        rz = 2*qx*qz*vx + 2*qy*qz*vy + qz*qz*vz - 2*qw*qy*vx - qy*qy*vz + 2*qw*qx*vy - qx*qx*vz + qw*qw*vz
        
        return (rx, ry, rz)


@dataclass
class VectorMeasurement:
    """A vector measurement in body and reference frames."""
    body_vector: Tuple[float, float, float]
    reference_vector: Tuple[float, float, float]
    weight: float = 1.0


class QUESTSolver:
    """
    QUEST (QUaternion ESTimator) algorithm for Wahba's problem.
    
    Finds optimal attitude quaternion from vector observations.
    """
    
    def __init__(self):
        self.measurements: List[VectorMeasurement] = []
    
    def add_measurement(self, measurement: VectorMeasurement):
        """Add vector measurement."""
        self.measurements.append(measurement)
    
    def _cross_product_matrix(self, v: Tuple[float, float, float]) -> List[List[float]]:
        """Create cross-product matrix [v x]."""
        x, y, z = v
        return [
            [0, -z, y],
            [z, 0, -x],
            [-y, x, 0]
        ]
    
    def _mat_add(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Matrix addition."""
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
    
    def _mat_mul_scalar(self, A: List[List[float]], s: float) -> List[List[float]]:
        """Scalar multiplication."""
        return [[A[i][j] * s for j in range(len(A[0]))] for i in range(len(A))]
    
    def _vec_dot(self, a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
        """Vector dot product."""
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    
    def solve(self) -> Optional[Quaternion]:
        """
        Solve Wahba's problem using QUEST.
        
        Returns:
            Optimal attitude quaternion
        """
        if len(self.measurements) < 2:
            return None
        
        # Build B matrix
        B = [[0.0] * 3 for _ in range(3)]
        total_weight = 0.0
        
        for m in self.measurements:
            bx, by, bz = m.body_vector
            rx, ry, rz = m.reference_vector
            
            # Normalize vectors
            b_norm = math.sqrt(bx*bx + by*by + bz*bz)
            r_norm = math.sqrt(rx*rx + ry*ry + rz*rz)
            if b_norm == 0 or r_norm == 0:
                continue
            
            bx, by, bz = bx/b_norm, by/b_norm, bz/b_norm
            rx, ry, rz = rx/r_norm, ry/r_norm, rz/r_norm
            
            for i in range(3):
                for j in range(3):
                    body = [bx, by, bz][i]
                    ref = [rx, ry, rz][j]
                    B[i][j] += m.weight * body * ref
            
            total_weight += m.weight
        
        # Compute S = B + B^T
        S = [[B[i][j] + B[j][i] for j in range(3)] for i in range(3)]
        
        # Compute z = [B23-B32, B31-B13, B12-B21]^T
        z = [B[1][2] - B[2][1], B[2][0] - B[0][2], B[0][1] - B[1][0]]
        
        # Compute sigma = trace(B)
        sigma = B[0][0] + B[1][1] + B[2][2]
        
        # Characteristic equation: lambda^4 - (a+b)*lambda^2 - c*lambda + d = 0
        # Simplified: find lambda that maximizes the objective
        
        # Use Newton-Raphson to find optimal lambda
        # Initial guess
        lambda_val = total_weight
        
        for _ in range(10):
            # f(lambda) = lambda^2 - (sigma^2 - trace(adj(S))) * lambda - det(S)
            # Simplified iterative refinement
            adj_trace = (S[0][0]*S[1][1] - S[0][1]*S[1][0] +
                        S[1][1]*S[2][2] - S[1][2]*S[2][1] +
                        S[0][0]*S[2][2] - S[0][2]*S[2][0])
            
            f = lambda_val**2 - (sigma**2 - adj_trace)
            df = 2 * lambda_val
            
            if abs(df) < 1e-10:
                break
            
            lambda_val = lambda_val - f / df
        
        # Compute quaternion from lambda
        alpha = lambda_val + sigma
        
        if abs(alpha) < 1e-10:
            alpha = 1e-10
        
        # X = (alpha * I - S)^-1 * z
        # Simplified: solve linear system
        M = [[alpha - S[i][j] if i == j else -S[i][j] for j in range(3)]
             for i in range(3)]
        
        X = self._solve_3x3(M, z)
        
        # Quaternion: q = [X; alpha] / norm
        norm = math.sqrt(X[0]**2 + X[1]**2 + X[2]**2 + alpha**2)
        if norm == 0:
            return Quaternion(1, 0, 0, 0)
        
        q = Quaternion(alpha / norm, X[0] / norm, X[1] / norm, X[2] / norm)
        q.normalize()
        return q
    
    def _solve_3x3(self, A: List[List[float]], b: List[float]) -> List[float]:
        """Solve 3x3 linear system."""
        # Cramer's rule
        det = (A[0][0]*(A[1][1]*A[2][2] - A[1][2]*A[2][1]) -
               A[0][1]*(A[1][0]*A[2][2] - A[1][2]*A[2][0]) +
               A[0][2]*(A[1][0]*A[2][1] - A[1][1]*A[2][0]))
        
        if abs(det) < 1e-10:
            return [0.0, 0.0, 0.0]
        
        def replace_col(A, b, col):
            M = [row[:] for row in A]
            for i in range(3):
                M[i][col] = b[i]
            return M
        
        def det3(M):
            return (M[0][0]*(M[1][1]*M[2][2] - M[1][2]*M[2][1]) -
                   M[0][1]*(M[1][0]*M[2][2] - M[1][2]*M[2][0]) +
                   M[0][2]*(M[1][0]*M[2][1] - M[1][1]*M[2][0]))
        
        x = det3(replace_col(A, b, 0)) / det
        y = det3(replace_col(A, b, 1)) / det
        z = det3(replace_col(A, b, 2)) / det
        
        return [x, y, z]


class StarTracker:
    """
    Star tracker simulation for attitude determination.
    """
    
    def __init__(self, fov_deg: float = 20.0, resolution: int = 1024):
        """
        Args:
            fov_deg: Field of view in degrees
            resolution: Sensor resolution
        """
        self.fov = math.radians(fov_deg)
        self.resolution = resolution
        self.catalog: Dict[str, Tuple[float, float, float]] = {}
    
    def add_star(self, name: str, direction: Tuple[float, float, float]):
        """
        Add star to catalog.
        
        Args:
            name: Star name
            direction: Unit vector direction in inertial frame
        """
        dx, dy, dz = direction
        norm = math.sqrt(dx*dx + dy*dy + dz*dz)
        if norm > 0:
            self.catalog[name] = (dx/norm, dy/norm, dz/norm)
    
    def observe(self, attitude: Quaternion
               ) -> List[Tuple[str, Tuple[float, float, float]]]:
        """
        Simulate star observation in body frame.
        
        Args:
            attitude: Current attitude quaternion
        
        Returns:
            List of (star_name, body_vector) tuples
        """
        observations = []
        
        # boresight direction in body frame (assume +z)
        boresight = (0, 0, 1)
        
        for name, inertial_dir in self.catalog.items():
            # Rotate inertial direction to body frame: q^* * r * q
            q_conj = attitude.conjugate()
            body_dir = q_conj.rotate_vector(inertial_dir)
            
            # Check if in FOV
            cos_angle = body_dir[0]*boresight[0] + body_dir[1]*boresight[1] + body_dir[2]*boresight[2]
            if cos_angle >= math.cos(self.fov / 2):
                observations.append((name, body_dir))
        
        return observations
    
    def identify_pattern(self, observations: List[Tuple[str, Tuple[float, float, float]]]
                        ) -> List[VectorMeasurement]:
        """
        Identify stars and create vector measurements.
        
        Args:
            observations: Observed stars
        
        Returns:
            Vector measurements for attitude determination
        """
        measurements = []
        
        for name, body_vec in observations:
            if name in self.catalog:
                ref_vec = self.catalog[name]
                measurements.append(VectorMeasurement(
                    body_vector=body_vec,
                    reference_vector=ref_vec,
                    weight=1.0
                ))
        
        return measurements


class AttitudeDetermination:
    """
    Unified attitude determination controller.
    """
    
    def __init__(self):
        self.quest = QUESTSolver()
        self.star_tracker = StarTracker()
        self.current_attitude: Optional[Quaternion] = None
    
    def add_vector_measurement(self, body: Tuple[float, float, float],
                              reference: Tuple[float, float, float],
                              weight: float = 1.0):
        """
        Add vector measurement.
        
        Args:
            body: Vector in body frame
            reference: Vector in reference frame
            weight: Measurement weight
        """
        self.quest.add_measurement(VectorMeasurement(body, reference, weight))
    
    def determine_attitude(self) -> Optional[Quaternion]:
        """
        Determine attitude from measurements.
        
        Returns:
            Attitude quaternion or None
        """
        self.current_attitude = self.quest.solve()
        return self.current_attitude
    
    def add_star(self, name: str, direction: Tuple[float, float, float]):
        """Add star to catalog."""
        self.star_tracker.add_star(name, direction)
    
    def observe_stars(self) -> List[Tuple[str, Tuple[float, float, float]]]:
        """
        Observe stars with current attitude.
        
        Returns:
            Observations
        """
        if self.current_attitude is None:
            return []
        return self.star_tracker.observe(self.current_attitude)
    
    def determination_summary(self) -> Dict:
        """Get determination summary."""
        return {
            "measurements": len(self.quest.measurements),
            "stars_cataloged": len(self.star_tracker.catalog),
            "attitude_known": self.current_attitude is not None
        }
