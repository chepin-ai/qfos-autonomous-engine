"""
Quantum Adiabatic Optimization Module
Adiabatic quantum computation with time-dependent Hamiltonian,
ground state evolution, and energy gap monitoring.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


class Hamiltonian:
    """
    Quantum Hamiltonian for adiabatic optimization.
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
    
    def initial_hamiltonian(self) -> List[List[float]]:
        """
        Initial Hamiltonian (transverse field).
        H_0 = -sum_i sigma_x(i)
        
        Returns:
            Hamiltonian matrix
        """
        # Simplified: diagonal approximation
        H = [[0.0] * self.dim for _ in range(self.dim)]
        for i in range(self.dim):
            # Number of 1 bits = energy contribution
            bits = bin(i).count('1')
            H[i][i] = -self.n + 2.0 * bits
        return H
    
    def problem_hamiltonian(self,
                           cost_function: Callable[[int], float]) -> List[List[float]]:
        """
        Problem Hamiltonian (diagonal in computational basis).
        
        Args:
            cost_function: Cost function
        
        Returns:
            Hamiltonian matrix
        """
        H = [[0.0] * self.dim for _ in range(self.dim)]
        for i in range(self.dim):
            H[i][i] = cost_function(i)
        return H
    
    def interpolate(self, H0: List[List[float]],
                   H1: List[List[float]],
                   s: float) -> List[List[float]]:
        """
        Interpolate Hamiltonian: H(s) = (1-s)H0 + sH1.
        
        Args:
            H0: Initial
            H1: Problem
            s: Parameter (0 to 1)
        
        Returns:
            Interpolated Hamiltonian
        """
        return [[(1.0 - s) * H0[i][j] + s * H1[i][j]
                 for j in range(self.dim)]
                for i in range(self.dim)]


class GroundStateSolver:
    """
    Ground state solver for Hamiltonian diagonalization.
    """
    
    def power_iteration(self, H: List[List[float]],
                       iterations: int = 50) -> Tuple[float, List[float]]:
        """
        Power iteration for ground state (lowest eigenvalue).
        Uses inverse iteration via negative shift for ground state.
        
        Args:
            H: Hamiltonian
            iterations: Iterations
        
        Returns:
            (energy, state)
        """
        dim = len(H)
        # For diagonal Hamiltonians, ground state is minimum diagonal element
        diagonal = [H[i][i] for i in range(dim)]
        min_idx = diagonal.index(min(diagonal))
        state = [0.0] * dim
        state[min_idx] = 1.0
        
        # Refine with power iteration on shifted matrix
        shift = max(diagonal) + 1.0
        for _ in range(iterations):
            new_state = [sum((shift - H[i][j]) * state[j] for j in range(dim))
                        for i in range(dim)]
            norm = sum(x**2 for x in new_state) ** 0.5
            if norm > 0:
                state = [x / norm for x in new_state]
        
        energy = sum(sum(H[i][j] * state[j] for j in range(dim)) * state[i]
                    for i in range(dim))
        return energy, state
    
    def energy_gap(self, H: List[List[float]]) -> float:
        """
        Estimate energy gap (ground to first excited).
        Simplified.
        
        Args:
            H: Hamiltonian
        
        Returns:
            Gap
        """
        # Extract diagonal elements
        energies = [H[i][i] for i in range(len(H))]
        sorted_e = sorted(energies)
        if len(sorted_e) >= 2:
            return sorted_e[1] - sorted_e[0]
        return 0.0


class AdiabaticEvolution:
    """
    Adiabatic quantum evolution.
    """
    
    def __init__(self, num_qubits: int = 4,
                 time_steps: int = 100):
        """
        Args:
            num_qubits: Qubits
            time_steps: Time steps
        """
        self.n = num_qubits
        self.steps = time_steps
        self.hamiltonian = Hamiltonian(num_qubits)
        self.solver = GroundStateSolver()
        self.energy_history: List[float] = []
        self.gap_history: List[float] = []
    
    def evolve(self, cost_function: Callable[[int], float]) -> Dict:
        """
        Run adiabatic evolution.
        
        Args:
            cost_function: Cost function
        
        Returns:
            Result
        """
        H0 = self.hamiltonian.initial_hamiltonian()
        H1 = self.hamiltonian.problem_hamiltonian(cost_function)
        
        # Start in ground state of H0
        _, state = self.solver.power_iteration(H0, 20)
        
        for step in range(self.steps + 1):
            s = step / self.steps
            H = self.hamiltonian.interpolate(H0, H1, s)
            
            # Evolve state (simplified: project to ground state)
            energy, state = self.solver.power_iteration(H, 5)
            self.energy_history.append(energy)
            
            gap = self.solver.energy_gap(H)
            self.gap_history.append(gap)
        
        # Find solution (most probable basis state)
        max_prob = max(abs(x)**2 for x in state)
        solution = state.index(max(state, key=lambda x: abs(x)))
        
        return {
            "solution": solution,
            "final_energy": self.energy_history[-1],
            "min_gap": min(self.gap_history) if self.gap_history else 0.0,
            "cost": cost_function(solution)
        }


class QuantumAdiabaticOptimization:
    """
    Unified quantum adiabatic optimization controller.
    """
    
    def __init__(self):
        self.evolution: Optional[AdiabaticEvolution] = None
        self.results: List[Dict] = []
    
    def setup(self, num_qubits: int = 4, time_steps: int = 100):
        """
        Setup evolution.
        
        Args:
            num_qubits: Qubits
            time_steps: Steps
        """
        self.evolution = AdiabaticEvolution(num_qubits, time_steps)
    
    def optimize(self, cost_function: Callable[[int], float]) -> Dict:
        """
        Run optimization.
        
        Args:
            cost_function: Cost function
        
        Returns:
            Result
        """
        if self.evolution is None:
            self.setup()
        
        result = self.evolution.evolve(cost_function)
        self.results.append(result)
        return result
    
    def adiabatic_summary(self) -> Dict:
        """Get summary."""
        if not self.results:
            return {"status": "no_data"}
        
        best = min(self.results, key=lambda r: r["cost"])
        
        return {
            "runs": len(self.results),
            "best_solution": best["solution"],
            "best_cost": best["cost"],
            "min_gap": min(r["min_gap"] for r in self.results)
        }
