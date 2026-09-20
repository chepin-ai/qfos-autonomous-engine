"""
Quantum Optimizer Module
Quantum-inspired gradient-free optimization algorithms
including simulated quantum annealing, quantum particle swarm,
and quantum-behaved evolution for autonomous parameter tuning.
"""

import math
import random
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass


class QuantumParticle:
    """
    Quantum-behaved particle for optimization.
    """
    
    def __init__(self, dim: int, bounds: List[Tuple[float, float]]):
        """
        Args:
            dim: Dimension
            bounds: Search bounds
        """
        self.dim = dim
        self.bounds = bounds
        self.position = [random.uniform(b[0], b[1]) for b in bounds]
        self.best_position = self.position[:]
        self.best_fitness = float('inf')
    
    def update_position(self, mbest: List[float], alpha: float = 0.5):
        """
        Update position using quantum behavior.
        
        Args:
            mbest: Mean best position
            alpha: Contraction-expansion coefficient
        """
        for i in range(self.dim):
            phi = random.uniform(0.0, 1.0)
            p = phi * self.best_position[i] + (1.0 - phi) * mbest[i]
            
            # Quantum tunneling: Levy-flight like update
            u = random.uniform(0.0, 1.0)
            if u > 0.5:
                self.position[i] = p + alpha * abs(self.best_position[i] - mbest[i]) * math.log(1.0 / u)
            else:
                self.position[i] = p - alpha * abs(self.best_position[i] - mbest[i]) * math.log(1.0 / u)
            
            # Bounds check
            lo, hi = self.bounds[i]
            self.position[i] = max(lo, min(hi, self.position[i]))
    
    def evaluate(self, objective: Callable[[List[float]], float]) -> float:
        """
        Evaluate fitness.
        
        Args:
            objective: Objective function
        
        Returns:
            Fitness
        """
        fitness = objective(self.position)
        if fitness < self.best_fitness:
            self.best_fitness = fitness
            self.best_position = self.position[:]
        return fitness


class QuantumParticleSwarm:
    """
    Quantum-behaved particle swarm optimization (QPSO).
    """
    
    def __init__(self, dim: int, bounds: List[Tuple[float, float]],
                 num_particles: int = 20):
        """
        Args:
            dim: Dimension
            bounds: Search bounds
            num_particles: Swarm size
        """
        self.dim = dim
        self.bounds = bounds
        self.swarm = [QuantumParticle(dim, bounds) for _ in range(num_particles)]
        self.global_best = None
        self.global_fitness = float('inf')
        self.history: List[float] = []
    
    def mean_best(self) -> List[float]:
        """
        Compute mean best position.
        
        Returns:
            Mean best
        """
        mbest = []
        for i in range(self.dim):
            val = sum(p.best_position[i] for p in self.swarm) / len(self.swarm)
            mbest.append(val)
        return mbest
    
    def optimize(self, objective: Callable[[List[float]], float],
                max_iter: int = 100,
                alpha: float = 0.5) -> Tuple[List[float], float]:
        """
        Run QPSO optimization.
        
        Args:
            objective: Objective function
            max_iter: Maximum iterations
            alpha: CE coefficient
        
        Returns:
            (best_position, best_fitness)
        """
        for iteration in range(max_iter):
            # Decay alpha
            current_alpha = alpha * (1.0 - iteration / max_iter) + 0.1
            
            # Evaluate all particles
            for particle in self.swarm:
                fitness = particle.evaluate(objective)
                if fitness < self.global_fitness:
                    self.global_fitness = fitness
                    self.global_best = particle.position[:]
            
            # Update positions
            mbest = self.mean_best()
            for particle in self.swarm:
                particle.update_position(mbest, current_alpha)
            
            self.history.append(self.global_fitness)
        
        return self.global_best, self.global_fitness


class QuantumAnnealingOptimizer:
    """
    Quantum annealing-style optimizer.
    """
    
    def __init__(self, dim: int, bounds: List[Tuple[float, float]]):
        """
        Args:
            dim: Dimension
            bounds: Search bounds
        """
        self.dim = dim
        self.bounds = bounds
        self.best_solution: Optional[List[float]] = None
        self.best_energy = float('inf')
        self.history: List[float] = []
    
    def energy(self, state: List[float],
              objective: Callable[[List[float]], float]) -> float:
        """
        Compute energy.
        
        Args:
            state: State
            objective: Objective
        
        Returns:
            Energy
        """
        return objective(state)
    
    def tunnel_probability(self, delta_E: float, temperature: float) -> float:
        """
        Quantum tunneling probability.
        
        Args:
            delta_E: Energy difference
            temperature: Temperature
        
        Returns:
            Probability
        """
        if temperature <= 0:
            return 0.0
        # Tunneling: probability doesn't decay as fast as classical
        return 1.0 / (1.0 + math.exp(delta_E / temperature))
    
    def neighbor(self, state: List[float],
                scale: float = 0.1) -> List[float]:
        """
        Generate neighbor state.
        
        Args:
            state: Current state
            scale: Perturbation scale
        
        Returns:
            Neighbor
        """
        new_state = []
        for i in range(self.dim):
            val = state[i] + random.gauss(0.0, scale * (self.bounds[i][1] - self.bounds[i][0]))
            val = max(self.bounds[i][0], min(self.bounds[i][1], val))
            new_state.append(val)
        return new_state
    
    def optimize(self, objective: Callable[[List[float]], float],
                max_iter: int = 1000,
                initial_temp: float = 10.0,
                cooling_rate: float = 0.995) -> Tuple[List[float], float]:
        """
        Run quantum annealing.
        
        Args:
            objective: Objective
            max_iter: Iterations
            initial_temp: Starting temperature
            cooling_rate: Cooling rate
        
        Returns:
            (best, energy)
        """
        current = [random.uniform(b[0], b[1]) for b in self.bounds]
        current_energy = self.energy(current, objective)
        self.best_solution = current[:]
        self.best_energy = current_energy
        
        temp = initial_temp
        
        for _ in range(max_iter):
            candidate = self.neighbor(current)
            candidate_energy = self.energy(candidate, objective)
            
            delta_E = candidate_energy - current_energy
            
            if delta_E < 0:
                current = candidate
                current_energy = candidate_energy
                if current_energy < self.best_energy:
                    self.best_energy = current_energy
                    self.best_solution = current[:]
            else:
                prob = self.tunnel_probability(delta_E, temp)
                if random.random() < prob:
                    current = candidate
                    current_energy = candidate_energy
            
            temp *= cooling_rate
            self.history.append(self.best_energy)
        
        return self.best_solution, self.best_energy


class QuantumOptimizer:
    """
    Unified quantum optimizer controller.
    """
    
    def __init__(self):
        self.qpso: Optional[QuantumParticleSwarm] = None
        self.qa: Optional[QuantumAnnealingOptimizer] = None
        self.results: List[Dict] = []
    
    def qpso_optimize(self, objective: Callable[[List[float]], float],
                     dim: int,
                     bounds: List[Tuple[float, float]],
                     num_particles: int = 20,
                     max_iter: int = 100) -> Dict:
        """
        Run QPSO.
        
        Args:
            objective: Objective
            dim: Dimension
            bounds: Bounds
            num_particles: Swarm size
            max_iter: Iterations
        
        Returns:
            Result
        """
        self.qpso = QuantumParticleSwarm(dim, bounds, num_particles)
        best_pos, best_fit = self.qpso.optimize(objective, max_iter)
        
        result = {
            "method": "QPSO",
            "best_position": best_pos,
            "best_fitness": best_fit,
            "iterations": max_iter,
            "final_swarm_size": num_particles
        }
        self.results.append(result)
        return result
    
    def qa_optimize(self, objective: Callable[[List[float]], float],
                   dim: int,
                   bounds: List[Tuple[float, float]],
                   max_iter: int = 1000) -> Dict:
        """
        Run quantum annealing.
        
        Args:
            objective: Objective
            dim: Dimension
            bounds: Bounds
            max_iter: Iterations
        
        Returns:
            Result
        """
        self.qa = QuantumAnnealingOptimizer(dim, bounds)
        best_pos, best_fit = self.qa.optimize(objective, max_iter)
        
        result = {
            "method": "QA",
            "best_position": best_pos,
            "best_fitness": best_fit,
            "iterations": max_iter
        }
        self.results.append(result)
        return result
    
    def optimize(self, objective: Callable[[List[float]], float],
                dim: int,
                bounds: List[Tuple[float, float]],
                method: str = "QPSO") -> Dict:
        """
        Optimize with selected method.
        
        Args:
            objective: Objective
            dim: Dimension
            bounds: Bounds
            method: "QPSO" or "QA"
        
        Returns:
            Result
        """
        if method.upper() == "QA":
            return self.qa_optimize(objective, dim, bounds)
        return self.qpso_optimize(objective, dim, bounds)
    
    def optimizer_summary(self) -> Dict:
        """Get optimizer summary."""
        return {
            "runs": len(self.results),
            "best_fitness_overall": min((r["best_fitness"] for r in self.results), default=0.0),
            "methods_used": list(set(r["method"] for r in self.results))
        }
