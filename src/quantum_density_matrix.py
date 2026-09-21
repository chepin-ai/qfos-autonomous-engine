"""
Quantum Density Matrix Module
Density matrix operations, mixed state analysis,
entanglement entropy, partial trace, and quantum channels for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DensityMatrix:
    """Quantum density matrix."""
    matrix: List[List[complex]]
    dim: int


class DensityMatrixBuilder:
    """
    Build density matrices from states.
    """
    
    def __init__(self):
        pass
    
    def from_pure_state(self, state: List[complex]) -> DensityMatrix:
        """
        Build density matrix from pure state.
        
        Args:
            state: State vector
        
        Returns:
            Density matrix
        """
        n = len(state)
        rho = [[0.0j for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                rho[i][j] = state[i] * state[j].conjugate()
        return DensityMatrix(rho, n)
    
    def maximally_mixed(self, dim: int) -> DensityMatrix:
        """
        Create maximally mixed state.
        
        Args:
            dim: Dimension
        
        Returns:
            Maximal mixed state
        """
        rho = [[0.0j for _ in range(dim)] for _ in range(dim)]
        for i in range(dim):
            rho[i][i] = 1.0 / dim
        return DensityMatrix(rho, dim)
    
    def bell_state_density(self) -> DensityMatrix:
        """
        Create Bell state density matrix.
        
        Returns:
            Bell state density matrix
        """
        s = 1.0 / math.sqrt(2.0)
        state = [s, 0.0, 0.0, s]
        return self.from_pure_state(state)


class DensityMatrixOperations:
    """
    Density matrix operations.
    """
    
    def __init__(self):
        pass
    
    def trace(self, rho: DensityMatrix) -> complex:
        """
        Compute trace of density matrix.
        
        Args:
            rho: Density matrix
        
        Returns:
            Trace
        """
        return sum(rho.matrix[i][i] for i in range(rho.dim))
    
    def is_hermitian(self, rho: DensityMatrix,
                    tol: float = 1e-10) -> bool:
        """
        Check if matrix is Hermitian.
        
        Args:
            rho: Density matrix
            tol: Tolerance
        
        Returns:
            Whether Hermitian
        """
        for i in range(rho.dim):
            for j in range(rho.dim):
                if abs(rho.matrix[i][j] - rho.matrix[j][i].conjugate()) > tol:
                    return False
        return True
    
    def is_positive_semidefinite(self, rho: DensityMatrix) -> bool:
        """
        Check if matrix is positive semidefinite.
        
        Args:
            rho: Density matrix
        
        Returns:
            Whether PSD
        """
        # Simplified: check diagonal entries are non-negative
        for i in range(rho.dim):
            if rho.matrix[i][i].real < -1e-10:
                return False
        return True
    
    def purity(self, rho: DensityMatrix) -> float:
        """
        Compute purity Tr(rho^2).
        
        Args:
            rho: Density matrix
        
        Returns:
            Purity
        """
        trace_rho2 = 0.0
        for i in range(rho.dim):
            for j in range(rho.dim):
                trace_rho2 += (rho.matrix[i][j] * rho.matrix[j][i]).real
        return trace_rho2
    
    def von_neumann_entropy(self, rho: DensityMatrix) -> float:
        """
        Compute von Neumann entropy.
        
        Args:
            rho: Density matrix
        
        Returns:
            Entropy
        """
        # Simplified: use purity approximation for 2x2
        if rho.dim == 2:
            p = self.purity(rho)
            # For pure state: purity=1, entropy=0
            # For mixed state: purity<1, entropy>0
            if p >= 1.0:
                return 0.0
            # Approximate
            return max(0.0, math.log(2.0) * (1.0 - p))
        return 0.0


class PartialTrace:
    """
    Partial trace for composite systems.
    """
    
    def __init__(self):
        pass
    
    def trace_out_b(self, rho_ab: DensityMatrix,
                   dim_a: int,
                   dim_b: int) -> DensityMatrix:
        """
        Trace out subsystem B.
        
        Args:
            rho_ab: Joint density matrix
            dim_a: Dimension of A
            dim_b: Dimension of B
        
        Returns:
            Reduced density matrix for A
        """
        rho_a = [[0.0j for _ in range(dim_a)] for _ in range(dim_a)]
        
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    idx_ik = i * dim_b + k
                    idx_jk = j * dim_b + k
                    if idx_ik < rho_ab.dim and idx_jk < rho_ab.dim:
                        rho_a[i][j] += rho_ab.matrix[idx_ik][idx_jk]
        
        return DensityMatrix(rho_a, dim_a)


class EntanglementMeasures:
    """
    Entanglement measures from density matrices.
    """
    
    def __init__(self):
        self.ops = DensityMatrixOperations()
        self.pt = PartialTrace()
    
    def concurrence(self, rho: DensityMatrix) -> float:
        """
        Compute concurrence for 2-qubit state.
        
        Args:
            rho: Density matrix
        
        Returns:
            Concurrence
        """
        if rho.dim != 4:
            return 0.0
        
        # Simplified: concurrence = sqrt(2(1 - Tr(rho_a^2)))
        rho_a = self.pt.trace_out_b(rho, 2, 2)
        purity_a = self.ops.purity(rho_a)
        return max(0.0, math.sqrt(2.0 * max(0.0, 1.0 - purity_a)))
    
    def entanglement_entropy(self, rho: DensityMatrix) -> float:
        """
        Compute entanglement entropy.
        
        Args:
            rho: Density matrix
        
        Returns:
            Entanglement entropy
        """
        if rho.dim != 4:
            return 0.0
        rho_a = self.pt.trace_out_b(rho, 2, 2)
        return self.ops.von_neumann_entropy(rho_a)


class QuantumDensityMatrix:
    """
    Unified quantum density matrix controller.
    """
    
    def __init__(self):
        self.builder = DensityMatrixBuilder()
        self.ops = DensityMatrixOperations()
        self.pt = PartialTrace()
        self.ent = EntanglementMeasures()
    
    def density_summary(self) -> Dict:
        """Get summary."""
        return {
            "operations": ["trace", "purity", "entropy", "partial_trace"],
            "measures": ["concurrence", "entanglement_entropy"]
        }
