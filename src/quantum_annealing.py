"""
Quantum Annealing Module
Ising model, QUBO formulation,
simulated annealing, energy landscapes, and optimization for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpinConfiguration:
    """Ising spin configuration."""
    spins: List[int]
    energy: float


class IsingModel:
    """
    Ising model Hamiltonian.
    """
    
    def __init__(self, num_spins: int = 4):
        """
        Args:
            num_spins: Number of spins
        """
        self.num_spins = num_spins
        self.J: Dict[Tuple[int, int], float] = {}
        self.h: List[float] = [0.0] * num_spins
    
    def set_coupling(self, i: int, j: int, value: float):
        """
        Set coupling J_ij.
        
        Args:
            i: Spin index
            j: Spin index
            value: Coupling strength
        """
        if i < j:
            self.J[(i, j)] = value
        else:
            self.J[(j, i)] = value
    
    def set_field(self, i: int, value: float):
        """
        Set local field h_i.
        
        Args:
            i: Spin index
            value: Field strength
        """
        self.h[i] = value
    
    def energy(self, spins: List[int]) -> float:
        """
        Compute energy of spin configuration.
        
        Args:
            spins: Spin configuration
        
        Returns:
            Energy
        """
        E = 0.0
        
        # Local field terms
        for i in range(self.num_spins):
            E += self.h[i] * spins[i]
        
        # Coupling terms
        for (i, j), J_ij in self.J.items():
            E += J_ij * spins[i] * spins[j]
        
        return E
    
    def ground_state(self) -> SpinConfiguration:
        """
        Find ground state by exhaustive search (small systems).
        
        Returns:
            Ground state configuration
        """
        min_energy = float('inf')
        best_spins = []
        
        for config in range(2 ** self.num_spins):
            spins = [1 if (config >> i) & 1 else -1
                    for i in range(self.num_spins)]
            E = self.energy(spins)
            if E < min_energy:
                min_energy = E
                best_spins = spins.copy()
        
        return SpinConfiguration(best_spins, min_energy)


class QUBO:
    """
    Quadratic Unconstrained Binary Optimization.
    """
    
    def __init__(self, num_variables: int = 4):
        """
        Args:
            num_variables: Number of binary variables
        """
        self.num_variables = num_variables
        self.Q: Dict[Tuple[int, int], float] = {}
    
    def set_coefficient(self, i: int, j: int, value: float):
        """
        Set QUBO coefficient Q_ij.
        
        Args:
            i: Variable index
            j: Variable index
            value: Coefficient
        """
        self.Q[(i, j)] = value
    
    def energy(self, x: List[int]) -> float:
        """
        Compute QUBO energy.
        
        Args:
            x: Binary configuration
        
        Returns:
            Energy
        """
        E = 0.0
        for (i, j), Q_ij in self.Q.items():
            E += Q_ij * x[i] * x[j]
        return E
    
    def to_ising(self) -> IsingModel:
        """
        Convert QUBO to Ising model.
        
        Returns:
            Ising model
        """
        ising = IsingModel(self.num_variables)
        
        for (i, j), Q_ij in self.Q.items():
            if i == j:
                ising.set_field(i, Q_ij / 2.0)
            else:
                ising.set_coupling(i, j, Q_ij / 4.0)
        
        return ising


class SimulatedAnnealing:
    """
    Simulated annealing solver.
    """
    
    def __init__(self, ising: IsingModel,
                 initial_temperature: float = 10.0,
                 cooling_rate: float = 0.95,
                 num_iterations: int = 1000):
        """
        Args:
            ising: Ising model
            initial_temperature: Initial temperature
            cooling_rate: Cooling rate
            num_iterations: Iterations
        """
        self.ising = ising
        self.T0 = initial_temperature
        self.alpha = cooling_rate
        self.iterations = num_iterations
    
    def solve(self) -> SpinConfiguration:
        """
        Solve using simulated annealing.
        
        Returns:
            Best configuration found
        """
        # Random initial state
        spins = [random.choice([-1, 1]) for _ in range(self.ising.num_spins)]
        current_energy = self.ising.energy(spins)
        best_spins = spins.copy()
        best_energy = current_energy
        
        T = self.T0
        
        for _ in range(self.iterations):
            # Random flip
            i = random.randint(0, self.ising.num_spins - 1)
            spins[i] *= -1
            new_energy = self.ising.energy(spins)
            
            delta_E = new_energy - current_energy
            
            if delta_E < 0 or random.random() < math.exp(-delta_E / T):
                current_energy = new_energy
                if current_energy < best_energy:
                    best_energy = current_energy
                    best_spins = spins.copy()
            else:
                spins[i] *= -1  # Revert
            
            T *= self.alpha
        
        return SpinConfiguration(best_spins, best_energy)


class QuantumAnnealing:
    """
    Quantum annealing simulation.
    """
    
    def __init__(self, ising: IsingModel,
                 gamma_schedule: List[float] = None):
        """
        Args:
            ising: Ising model
            gamma_schedule: Transverse field schedule
        """
        self.ising = ising
        self.gamma_schedule = gamma_schedule or [1.0 - i / 100.0 for i in range(100)]
    
    def tunneling_probability(self, barrier_height: float,
                             gamma: float) -> float:
        """
        Compute quantum tunneling probability.
        
        Args:
            barrier_height: Energy barrier
            gamma: Transverse field
        
        Returns:
            Tunneling probability
        """
        if gamma <= 0:
            return 0.0
        return math.exp(-barrier_height / gamma)
    
    def solve(self) -> SpinConfiguration:
        """
        Solve using quantum annealing simulation.
        
        Returns:
            Best configuration found
        """
        spins = [random.choice([-1, 1]) for _ in range(self.ising.num_spins)]
        best_spins = spins.copy()
        best_energy = self.ising.energy(spins)
        
        for gamma in self.gamma_schedule:
            # Thermal + quantum fluctuations
            for _ in range(10):
                i = random.randint(0, self.ising.num_spins - 1)
                spins[i] *= -1
                new_energy = self.ising.energy(spins)
                
                delta_E = new_energy - best_energy
                
                if delta_E < 0:
                    best_energy = new_energy
                    best_spins = spins.copy()
                elif random.random() < self.tunneling_probability(delta_E, gamma):
                    best_energy = new_energy
                    best_spins = spins.copy()
                else:
                    spins[i] *= -1
        
        return SpinConfiguration(best_spins, best_energy)


class QuantumAnnealingController:
    """
    Unified quantum annealing controller.
    """
    
    def __init__(self, num_spins: int = 4):
        self.ising = IsingModel(num_spins)
        self.qubo = QUBO(num_spins)
        self.sa = SimulatedAnnealing(self.ising)
        self.qa = QuantumAnnealing(self.ising)
    
    def qa_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["ising_model", "qubo", "simulated_annealing", "quantum_annealing"],
            "num_spins": self.ising.num_spins
        }
