"""
Quantum Simulated Annealing Module
Quantum-inspired simulated annealing with tunneling,
parallel replica exchange, and adiabatic optimization
for autonomous combinatorial problem solving.
"""

import math
import random
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass


class ClassicalAnnealing:
    """
    Classical simulated annealing optimizer.
    """
    
    def __init__(self, initial_temp: float = 100.0,
                 cooling_rate: float = 0.995,
                 min_temp: float = 0.01):
        """
        Args:
            initial_temp: Starting temperature
            cooling_rate: Cooling factor per step
            min_temp: Stopping temperature
        """
        self.temp = initial_temp
        self.cooling = cooling_rate
        self.min_temp = min_temp
    
    def acceptance_probability(self, delta_E: float) -> float:
        """
        Compute acceptance probability.
        
        Args:
            delta_E: Energy change (new - current)
        
        Returns:
            Probability [0, 1]
        """
        if delta_E < 0:
            return 1.0
        return math.exp(-delta_E / self.temp)
    
    def step(self, current_energy: float,
            neighbor_energy: float) -> bool:
        """
        Decide whether to accept neighbor.
        
        Args:
            current_energy: Current state energy
            neighbor_energy: Neighbor energy
        
        Returns:
            True if accept
        """
        delta = neighbor_energy - current_energy
        prob = self.acceptance_probability(delta)
        return random.random() < prob
    
    def cool(self):
        """Reduce temperature."""
        self.temp = max(self.min_temp, self.temp * self.cooling)


class QuantumTunneling:
    """
    Quantum tunneling probability model.
    """
    def __init__(self, gamma: float = 1.0):
        """
        Args:
            gamma: Tunneling amplitude
        """
        self.gamma = gamma
    
    def tunnel_probability(self, barrier_height: float,
                          barrier_width: float) -> float:
        """
        Compute tunneling probability.
        
        Args:
            barrier_height: Energy barrier height
            barrier_width: Barrier width
        
        Returns:
            Tunneling probability
        """
        if barrier_height <= 0:
            return 1.0
        # Simplified WKB approximation
        kappa = math.sqrt(2.0 * barrier_height)
        return math.exp(-2.0 * kappa * barrier_width / self.gamma)
    
    def attempt_tunnel(self, current_energy: float,
                      target_energy: float,
                      width: float = 1.0) -> bool:
        """
        Attempt quantum tunnel.
        
        Args:
            current_energy: Current energy
            target_energy: Target energy
            width: Barrier width
        
        Returns:
            True if tunnel succeeds
        """
        barrier = abs(target_energy - current_energy)
        prob = self.tunnel_probability(barrier, width)
        return random.random() < prob


class QuantumAnnealer:
    """
    Quantum annealing optimizer.
    """
    
    def __init__(self, num_qubits: int = 8,
                 initial_gamma: float = 10.0,
                 final_gamma: float = 0.01):
        """
        Args:
            num_qubits: Problem qubits
            initial_gamma: Initial transverse field
            final_gamma: Final transverse field
        """
        self.n = num_qubits
        self.gamma = initial_gamma
        self.gamma_final = final_gamma
        self.state: List[int] = [random.choice([0, 1]) for _ in range(num_qubits)]
        self.energy_history: List[float] = []
    
    def energy(self, state: List[int],
              hamiltonian: Callable[[List[int]], float]) -> float:
        """
        Evaluate Hamiltonian.
        
        Args:
            state: Spin configuration
            hamiltonian: Energy function
        
        Returns:
            Energy
        """
        return hamiltonian(state)
    
    def flip_spin(self, state: List[int], idx: int) -> List[int]:
        """
        Flip a spin.
        
        Args:
            state: Current state
            idx: Spin index
        
        Returns:
            New state
        """
        new_state = state.copy()
        new_state[idx] = 1 - new_state[idx]
        return new_state
    
    def anneal_step(self, hamiltonian: Callable[[List[int]], float]):
        """
        Single annealing step.
        
        Args:
            hamiltonian: Energy function
        """
        current_E = self.energy(self.state, hamiltonian)
        
        # Try random flip with quantum + thermal probability
        idx = random.randint(0, self.n - 1)
        new_state = self.flip_spin(self.state, idx)
        new_E = self.energy(new_state, hamiltonian)
        
        delta = new_E - current_E
        
        # Quantum tunneling term
        tunnel = QuantumTunneling(self.gamma)
        if tunnel.attempt_tunnel(current_E, new_E):
            self.state = new_state
        elif delta < 0:
            self.state = new_state
        elif random.random() < math.exp(-delta / max(self.gamma, 0.001)):
            self.state = new_state
        
        self.energy_history.append(self.energy(self.state, hamiltonian))
    
    def anneal(self, hamiltonian: Callable[[List[int]], float],
              steps: int = 1000):
        """
        Run full annealing schedule.
        
        Args:
            hamiltonian: Energy function
            steps: Number of steps
        """
        for step in range(steps):
            self.anneal_step(hamiltonian)
            # Reduce transverse field
            t = step / steps
            self.gamma = self.gamma * (1.0 - t) + self.gamma_final * t
    
    def best_energy(self) -> float:
        """
        Get best energy found.
        
        Returns:
            Best energy
        """
        if not self.energy_history:
            return 0.0
        return min(self.energy_history)


class ReplicaExchange:
    """
    Parallel replica exchange Monte Carlo.
    """
    def __init__(self, num_replicas: int = 4,
                 temperatures: Optional[List[float]] = None):
        """
        Args:
            num_replicas: Number of replicas
            temperatures: Replica temperatures
        """
        self.num_replicas = num_replicas
        self.temps = temperatures or [1.0 + i * 2.0 for i in range(num_replicas)]
        self.replicas: List[List[int]] = []
        self.energies: List[float] = []
    
    def init_replicas(self, n: int):
        """
        Initialize replicas.
        
        Args:
            n: State size
        """
        self.replicas = [[random.choice([0, 1]) for _ in range(n)]
                        for _ in range(self.num_replicas)]
    
    def exchange_probability(self, E_i: float, E_j: float,
                            T_i: float, T_j: float) -> float:
        """
        Compute replica exchange probability.
        
        Args:
            E_i, E_j: Energies
            T_i, T_j: Temperatures
        
        Returns:
            Exchange probability
        """
        if T_i <= 0 or T_j <= 0:
            return 0.0
        delta = (E_i - E_j) * (1.0 / T_j - 1.0 / T_i)
        return min(1.0, math.exp(delta))
    
    def attempt_exchange(self, hamiltonian: Callable[[List[int]], float]):
        """
        Attempt replica exchanges.
        
        Args:
            hamiltonian: Energy function
        """
        self.energies = [hamiltonian(r) for r in self.replicas]
        
        for i in range(self.num_replicas - 1):
            j = i + 1
            prob = self.exchange_probability(
                self.energies[i], self.energies[j],
                self.temps[i], self.temps[j]
            )
            if random.random() < prob:
                self.replicas[i], self.replicas[j] = self.replicas[j], self.replicas[i]
                self.energies[i], self.energies[j] = self.energies[j], self.energies[i]


class QuantumSimulatedAnnealing:
    """
    Unified quantum simulated annealing controller.
    """
    def __init__(self):
        self.classical = ClassicalAnnealing()
        self.quantum = QuantumAnnealer()
        self.replica = ReplicaExchange()
        self.results: List[Dict] = []
    
    def solve(self, hamiltonian: Callable[[List[int]], float],
             n: int, method: str = "quantum") -> Dict:
        """
        Solve optimization problem.
        
        Args:
            hamiltonian: Energy function
            n: Number of variables
            method: "classical", "quantum", or "replica"
        
        Returns:
            Results
        """
        if method == "classical":
            state = [random.choice([0, 1]) for _ in range(n)]
            E = hamiltonian(state)
            for _ in range(1000):
                new_state = state.copy()
                idx = random.randint(0, n - 1)
                new_state[idx] = 1 - new_state[idx]
                new_E = hamiltonian(new_state)
                if self.classical.step(E, new_E):
                    state = new_state
                    E = new_E
                self.classical.cool()
            result = {"method": "classical", "energy": E, "state": state}
        
        elif method == "replica":
            self.replica.init_replicas(n)
            for _ in range(100):
                self.replica.attempt_exchange(hamiltonian)
            best_idx = min(range(self.replica.num_replicas),
                          key=lambda i: self.replica.energies[i])
            result = {
                "method": "replica",
                "energy": self.replica.energies[best_idx],
                "state": self.replica.replicas[best_idx]
            }
        
        else:  # quantum
            self.quantum = QuantumAnnealer(n)
            self.quantum.anneal(hamiltonian, 1000)
            result = {
                "method": "quantum",
                "energy": self.quantum.best_energy(),
                "state": self.quantum.state
            }
        
        self.results.append(result)
        return result
    
    def annealing_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.results),
            "methods": list(set(r["method"] for r in self.results)),
            "best_energy": min((r["energy"] for r in self.results), default=0.0)
        }
