"""
Control Allocator Module
Thruster allocation, control distribution, and redundancy
management for spacecraft attitude and translation control.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Thruster:
    """A spacecraft thruster."""
    id: str
    position: Tuple[float, float, float]  # m
    direction: Tuple[float, float, float]  # unit vector
    max_force: float  # N
    is_functional: bool = True
    
    def torque(self) -> Tuple[float, float, float]:
        """Compute torque direction (r x F)."""
        rx, ry, rz = self.position
        fx, fy, fz = self.direction
        return (ry * fz - rz * fy,
                rz * fx - rx * fz,
                rx * fy - ry * fx)
    
    def normalize_direction(self):
        """Normalize direction vector."""
        dx, dy, dz = self.direction
        norm = math.sqrt(dx*dx + dy*dy + dz*dz)
        if norm > 0:
            self.direction = (dx/norm, dy/norm, dz/norm)


@dataclass
class ControlDemand:
    """Required control forces and torques."""
    force: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    torque: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class AllocationResult:
    """Result of control allocation."""
    thruster_forces: Dict[str, float] = field(default_factory=dict)
    residual_force: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    residual_torque: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    is_feasible: bool = False
    total_power: float = 0.0


class PseudoInverseAllocator:
    """
    Control allocation using pseudo-inverse method.
    """
    
    def __init__(self):
        self.thrusters: Dict[str, Thruster] = {}
    
    def add_thruster(self, thruster: Thruster):
        """Add thruster."""
        thruster.normalize_direction()
        self.thrusters[thruster.id] = thruster
    
    def _build_allocation_matrix(self) -> List[List[float]]:
        """
        Build allocation matrix B (6 x n).
        Each column: [Fx, Fy, Fz, Tx, Ty, Tz]^T for one thruster.
        """
        functional = [t for t in self.thrusters.values() if t.is_functional]
        B = []
        
        for t in functional:
            fx, fy, fz = t.direction
            tx, ty, tz = t.torque()
            col = [fx, fy, fz, tx, ty, tz]
            B.append(col)
        
        # Transpose to get 6 x n
        if not B:
            return [[0.0]]
        
        n = len(B)
        result = [[0.0] * n for _ in range(6)]
        for i in range(6):
            for j in range(n):
                result[i][j] = B[j][i]
        
        return result
    
    def _pseudo_inverse(self, A: List[List[float]]) -> List[List[float]]:
        """Compute Moore-Penrose pseudo-inverse with Tikhonov regularization."""
        m = len(A)
        n = len(A[0])
        reg = 1e-6  # Tikhonov regularization parameter
        
        AT = [[A[j][i] for j in range(m)] for i in range(n)]
        
        if m <= n:
            # A * A^T is m x m
            AAT = [[sum(A[i][k] * AT[k][j] for k in range(n))
                    for j in range(m)] for i in range(m)]
            # Add regularization
            for i in range(m):
                AAT[i][i] += reg
            AAT_inv = self._inverse_matrix(AAT)
            # A^+ = A^T * (A * A^T + reg*I)^-1
            return [[sum(AT[i][k] * AAT_inv[k][j] for k in range(m))
                     for j in range(m)] for i in range(n)]
        else:
            # A^T * A is n x n
            ATA = [[sum(AT[i][k] * A[k][j] for k in range(m))
                    for j in range(n)] for i in range(n)]
            # Add regularization
            for i in range(n):
                ATA[i][i] += reg
            ATA_inv = self._inverse_matrix(ATA)
            # A^+ = (A^T * A + reg*I)^-1 * A^T
            return [[sum(ATA_inv[i][k] * AT[k][j] for k in range(n))
                     for j in range(m)] for i in range(n)]
    
    def _inverse_matrix(self, A: List[List[float]]) -> List[List[float]]:
        """Invert a matrix using Gaussian elimination."""
        n = len(A)
        
        # Create augmented matrix [A | I]
        aug = [A[i][:] + [1.0 if i == j else 0.0 for j in range(n)]
               for i in range(n)]
        
        # Forward elimination
        for i in range(n):
            pivot = aug[i][i]
            if abs(pivot) < 1e-10:
                # Find row with non-zero pivot
                for k in range(i + 1, n):
                    if abs(aug[k][i]) > abs(pivot):
                        aug[i], aug[k] = aug[k], aug[i]
                        pivot = aug[i][i]
                        break
                if abs(pivot) < 1e-10:
                    return self._identity(n)
            
            for j in range(2 * n):
                aug[i][j] /= pivot
            
            for k in range(n):
                if k != i:
                    factor = aug[k][i]
                    for j in range(2 * n):
                        aug[k][j] -= factor * aug[i][j]
        
        # Extract inverse
        return [row[n:] for row in aug]
    
    def _identity(self, n: int) -> List[List[float]]:
        """Identity matrix."""
        return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    
    def _mat_vec_mul(self, A: List[List[float]], v: List[float]) -> List[float]:
        """Matrix-vector multiplication."""
        return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]
    
    def allocate(self, demand: ControlDemand) -> AllocationResult:
        """
        Allocate control demand to thrusters.
        
        Args:
            demand: Required force and torque
        
        Returns:
            Allocation result
        """
        functional = [t for t in self.thrusters.values() if t.is_functional]
        
        if not functional:
            return AllocationResult(is_feasible=False)
        
        B = self._build_allocation_matrix()
        B_pinv = self._pseudo_inverse(B)
        
        tau = [demand.force[0], demand.force[1], demand.force[2],
               demand.torque[0], demand.torque[1], demand.torque[2]]
        
        u = self._mat_vec_mul(B_pinv, tau)
        
        # Apply thruster limits
        forces = {}
        for i, t in enumerate(functional):
            force = max(-t.max_force, min(t.max_force, u[i]))
            forces[t.id] = force
        
        # Check feasibility
        actual_tau = self._mat_vec_mul(B, [forces[t.id] for t in functional])
        residual = [tau[i] - actual_tau[i] for i in range(6)]
        
        is_feasible = all(abs(r) < 0.1 for r in residual)
        
        total_power = sum(abs(forces[t.id]) for t in functional)
        
        return AllocationResult(
            thruster_forces=forces,
            residual_force=(residual[0], residual[1], residual[2]),
            residual_torque=(residual[3], residual[4], residual[5]),
            is_feasible=is_feasible,
            total_power=total_power
        )


class RedundancyManager:
    """
    Manage thruster redundancy and fault tolerance.
    """
    
    def __init__(self):
        self.thruster_groups: Dict[str, List[str]] = {}
        self.failed_thrusters: List[str] = []
    
    def add_redundancy_group(self, group_name: str, thruster_ids: List[str]):
        """Add a redundancy group."""
        self.thruster_groups[group_name] = thruster_ids
    
    def mark_failed(self, thruster_id: str):
        """Mark thruster as failed."""
        if thruster_id not in self.failed_thrusters:
            self.failed_thrusters.append(thruster_id)
    
    def mark_recovered(self, thruster_id: str):
        """Mark thruster as recovered."""
        if thruster_id in self.failed_thrusters:
            self.failed_thrusters.remove(thruster_id)
    
    def check_group_health(self, group_name: str) -> Dict:
        """
        Check health of redundancy group.
        
        Args:
            group_name: Group name
        
        Returns:
            Health status
        """
        group = self.thruster_groups.get(group_name, [])
        failed = [t for t in group if t in self.failed_thrusters]
        
        return {
            "group": group_name,
            "total": len(group),
            "failed": len(failed),
            "healthy": len(group) - len(failed),
            "health_rate": (len(group) - len(failed)) / max(1, len(group))
        }
    
    def get_reconfiguration(self, allocator: PseudoInverseAllocator
                           ) -> List[str]:
        """
        Get reconfiguration recommendation.
        
        Args:
            allocator: Current allocator
        
        Returns:
            List of thrusters to activate
        """
        available = [t.id for t in allocator.thrusters.values()
                    if t.is_functional and t.id not in self.failed_thrusters]
        return available


class ControlAllocator:
    """
    Unified control allocation controller.
    """
    
    def __init__(self):
        self.allocator = PseudoInverseAllocator()
        self.redundancy = RedundancyManager()
    
    def add_thruster(self, thruster: Thruster):
        """Add thruster to allocator."""
        self.allocator.add_thruster(thruster)
    
    def allocate(self, force: Tuple[float, float, float],
                torque: Tuple[float, float, float]) -> AllocationResult:
        """
        Allocate control demand.
        
        Args:
            force: Required force (N)
            torque: Required torque (N·m)
        
        Returns:
            Allocation result
        """
        demand = ControlDemand(force=force, torque=torque)
        return self.allocator.allocate(demand)
    
    def handle_failure(self, thruster_id: str):
        """Handle thruster failure."""
        if thruster_id in self.allocator.thrusters:
            self.allocator.thrusters[thruster_id].is_functional = False
        self.redundancy.mark_failed(thruster_id)
    
    def allocator_summary(self) -> Dict:
        """Get allocator summary."""
        total = len(self.allocator.thrusters)
        functional = sum(1 for t in self.allocator.thrusters.values() if t.is_functional)
        return {
            "total_thrusters": total,
            "functional": functional,
            "failed": total - functional,
            "groups": list(self.redundancy.thruster_groups.keys())
        }
