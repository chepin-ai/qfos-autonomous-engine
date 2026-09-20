"""
Quantum Annealing Module
Ising model, energy landscape, tunneling, and ground state
search for autonomous quantum optimization.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class SpinState(Enum):
    """Ising spin state."""
    UP = 1
    DOWN = -1


@dataclass
class IsingSpin:
    """An Ising spin variable."""
    index: int
    state: int  # +1 or -1
    local_field: float = 0.0


class IsingModel:
    """
    Ising model Hamiltonian.
    """
    
    def __init__(self, num_spins: int = 10):
        """
        Args:
            num_spins: Number of spins
        """
        self.num_spins = num_spins
        self.h: Dict[int, float] = {}  # Local fields
        self.J: Dict[Tuple[int, int], float] = {}  # Couplings
        self.spins: List[int] = [1] * num_spins
    
    def set_field(self, i: int, h_i: float):
        """Set local field."""
        self.h[i] = h_i
    
    def set_coupling(self, i: int, j: int, J_ij: float):
        """Set coupling between spins."""
        if i < j:
            self.J[(i, j)] = J_ij
        else:
            self.J[(j, i)] = J_ij
    
    def energy(self, spin_config: Optional[List[int]] = None) -> float:
        """
        Compute Hamiltonian energy.
        
        Args:
            spin_config: Spin configuration (default: current)
        
        Returns:
            Energy
        """
        if spin_config is None:
            spin_config = self.spins
        
        energy = 0.0
        
        # Local field terms
        for i, h_i in self.h.items():
            if i < len(spin_config):
                energy += h_i * spin_config[i]
        
        # Coupling terms
        for (i, j), J_ij in self.J.items():
            if i < len(spin_config) and j < len(spin_config):
                energy += J_ij * spin_config[i] * spin_config[j]
        
        return energy
    
    def local_energy(self, i: int) -> float:
        """
        Compute local energy contribution.
        
        Args:
            i: Spin index
        
        Returns:
            Local energy
        """
        e = self.h.get(i, 0.0) * self.spins[i]
        
        for (j, k), J in self.J.items():
            if j == i:
                e += J * self.spins[i] * self.spins[k]
            elif k == i:
                e += J * self.spins[j] * self.spins[i]
        
        return e
    
    def flip_spin(self, i: int):
        """Flip spin i."""
        if 0 <= i < len(self.spins):
            self.spins[i] *= -1
    
    def magnetization(self) -> float:
        """
        Compute total magnetization.
        
        Returns:
            Magnetization
        """
        return sum(self.spins) / len(self.spins)


class EnergyLandscape:
    """
    Analyze energy landscape.
    """
    
    def __init__(self, model: IsingModel):
        self.model = model
    
    def neighbor_states(self, state: List[int]) -> List[Tuple[List[int], float]]:
        """
        Generate single-flip neighbor states.
        
        Args:
            state: Current state
        
        Returns:
            List of (neighbor_state, energy)
        """
        neighbors = []
        
        for i in range(len(state)):
            neighbor = state.copy()
            neighbor[i] *= -1
            e = self.model.energy(neighbor)
            neighbors.append((neighbor, e))
        
        return neighbors
    
    def local_minima(self, state: List[int]) -> bool:
        """
        Check if state is local minimum.
        
        Args:
            state: State to check
        
        Returns:
            True if local minimum
        """
        current_e = self.model.energy(state)
        
        for neighbor, e in self.neighbor_states(state):
            if e < current_e:
                return False
        
        return True
    
    def energy_barrier(self, state1: List[int], state2: List[int]) -> float:
        """
        Estimate energy barrier between states.
        
        Args:
            state1, state2: Two states
        
        Returns:
            Barrier height
        """
        e1 = self.model.energy(state1)
        e2 = self.model.energy(state2)
        
        # Simplified: max energy along path
        max_e = max(e1, e2)
        
        for i in range(len(state1)):
            if state1[i] != state2[i]:
                intermediate = state1.copy()
                intermediate[i] = state2[i]
                e = self.model.energy(intermediate)
                max_e = max(max_e, e)
        
        return max_e - min(e1, e2)


class QuantumAnnealer:
    """
    Quantum annealing optimizer.
    """
    
    def __init__(self, model: IsingModel):
        self.model = model
        self.landscape = EnergyLandscape(model)
        self.gamma = 1.0  # Tunneling amplitude
    
    def tunneling_probability(self, barrier_height: float,
                             tunneling_amplitude: float) -> float:
        """
        Compute tunneling probability through barrier.
        
        Args:
            barrier_height: Energy barrier
            tunneling_amplitude: Gamma parameter
        
        Returns:
            Tunneling probability
        """
        if barrier_height <= 0:
            return 1.0
        
        # Simplified: exponential suppression
        return math.exp(-2.0 * barrier_height / tunneling_amplitude)
    
    def anneal_step(self, temperature: float,
                   gamma: float,
                   num_sweeps: int = 1) -> List[int]:
        """
        Perform one annealing step.
        
        Args:
            temperature: Current temperature
            gamma: Tunneling amplitude
            num_sweeps: Number of Metropolis sweeps
        
        Returns:
            Updated state
        """
        for _ in range(num_sweeps):
            for i in range(self.model.num_spins):
                # Compute energy change for flip
                delta_e = -2.0 * self.model.local_energy(i)
                
                # Metropolis criterion with quantum tunneling
                if delta_e < 0:
                    self.model.flip_spin(i)
                else:
                    # Classical thermal + quantum tunneling
                    p_thermal = math.exp(-delta_e / temperature) if temperature > 0 else 0.0
                    p_tunnel = self.tunneling_probability(delta_e, gamma)
                    
                    if p_thermal + p_tunnel > 1.0 or (p_thermal + p_tunnel) > 0.5:
                        self.model.flip_spin(i)
        
        return self.model.spins.copy()
    
    def anneal(self, T_initial: float = 10.0,
              T_final: float = 0.01,
              gamma_initial: float = 5.0,
              gamma_final: float = 0.01,
              steps: int = 100) -> Tuple[List[int], float]:
        """
        Full quantum annealing schedule.
        
        Args:
            T_initial, T_final: Temperature range
            gamma_initial, gamma_final: Tunneling range
            steps: Number of steps
        
        Returns:
            (final_state, final_energy)
        """
        for step in range(steps):
            # Linear schedule
            ratio = step / max(1, steps - 1)
            T = T_initial + ratio * (T_final - T_initial)
            gamma = gamma_initial + ratio * (gamma_final - gamma_initial)
            
            self.anneal_step(T, gamma, num_sweeps=1)
        
        final_e = self.model.energy()
        return (self.model.spins.copy(), final_e)


class GroundStateSearch:
    """
    Search for ground state.
    """
    
    def __init__(self, model: IsingModel):
        self.model = model
        self.annealer = QuantumAnnealer(model)
        self.best_state: Optional[List[int]] = None
        self.best_energy = float('inf')
    
    def search(self, num_restarts: int = 10) -> Tuple[List[int], float]:
        """
        Search with multiple restarts.
        
        Args:
            num_restarts: Number of random restarts
        
        Returns:
            (best_state, best_energy)
        """
        import random
        
        for _ in range(num_restarts):
            # Random initial state
            self.model.spins = [random.choice([-1, 1]) for _ in range(self.model.num_spins)]
            
            # Anneal
            state, energy = self.annealer.anneal()
            
            if energy < self.best_energy:
                self.best_energy = energy
                self.best_state = state.copy()
        
        return (self.best_state or [], self.best_energy)
    
    def exact_search_small(self) -> Tuple[List[int], float]:
        """
        Exact search (only for small systems).
        
        Returns:
            (ground_state, ground_energy)
        """
        if self.model.num_spins > 15:
            return self.search(num_restarts=10)
        
        best_e = float('inf')
        best_state = None
        
        # Enumerate all states
        for s in range(2 ** self.model.num_spins):
            state = []
            for i in range(self.model.num_spins):
                state.append(1 if (s >> i) & 1 == 1 else -1)
            
            e = self.model.energy(state)
            if e < best_e:
                best_e = e
                best_state = state.copy()
        
        return (best_state or [], best_e)


class QuantumAnnealing:
    """
    Unified quantum annealing controller.
    """
    
    def __init__(self, num_spins: int = 10):
        self.model = IsingModel(num_spins)
        self.annealer = QuantumAnnealer(self.model)
        self.searcher = GroundStateSearch(self.model)
        self.history: List[Tuple[float, List[int]]] = []
    
    def set_problem(self, h: Dict[int, float], J: Dict[Tuple[int, int], float]):
        """
        Set optimization problem.
        
        Args:
            h: Local fields
            J: Couplings
        """
        for i, hi in h.items():
            self.model.set_field(i, hi)
        for (i, j), Jij in J.items():
            self.model.set_coupling(i, j, Jij)
    
    def solve(self, num_restarts: int = 10) -> Tuple[List[int], float]:
        """
        Solve optimization problem.
        
        Args:
            num_restarts: Number of restarts
        
        Returns:
            (solution, energy)
        """
        state, energy = self.searcher.search(num_restarts)
        self.history.append((energy, state))
        return (state, energy)
    
    def annealing_summary(self) -> Dict:
        """Get annealing summary."""
        if not self.history:
            return {"status": "not_run"}
        
        best_e, best_s = min(self.history, key=lambda x: x[0])
        
        return {
            "num_spins": self.model.num_spins,
            "runs": len(self.history),
            "best_energy": best_e,
            "magnetization": sum(best_s) / len(best_s) if best_s else 0.0,
            "ground_state_approx": best_s[:10] if best_s else []
        }
