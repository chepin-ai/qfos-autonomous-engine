"""
Quantum Swarm Intelligence Module
Particle swarm optimization, quantum-inspired particles,
swarm diversity management, and global convergence tracking.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Particle:
    """Swarm particle."""
    position: List[float]
    velocity: List[float]
    best_position: List[float]
    best_fitness: float


class QuantumParticle:
    """
    Quantum-inspired particle.
    """
    
    def __init__(self, dim: int = 2):
        """
        Args:
            dim: Dimension
        """
        self.dim = dim
        self.position: List[float] = [0.0] * dim
        self.best_position: List[float] = [0.0] * dim
        self.best_fitness = float('inf')
    
    def quantum_update(self, global_best: List[float],
                      alpha: float = 0.5):
        """
        Update using quantum behavior.
        
        Args:
            global_best: Global best position
            alpha: Quantum parameter
        """
        import random
        for i in range(self.dim):
            # Quantum well potential
            phi = random.random()
            u = random.random()
            
            if random.random() > 0.5:
                self.position[i] = (global_best[i] +
                                   alpha * abs(self.best_position[i] - global_best[i]) *
                                   math.log(1.0 / u))
            else:
                self.position[i] = (global_best[i] -
                                   alpha * abs(self.best_position[i] - global_best[i]) *
                                   math.log(1.0 / u))


class SwarmOptimizer:
    """
    Particle swarm optimizer.
    """
    
    def __init__(self, num_particles: int = 30,
                 dim: int = 2,
                 w: float = 0.7,
                 c1: float = 1.5,
                 c2: float = 1.5):
        """
        Args:
            num_particles: Swarm size
            dim: Dimension
            w: Inertia
            c1: Cognitive coefficient
            c2: Social coefficient
        """
        self.num_particles = num_particles
        self.dim = dim
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.particles: List[Particle] = []
        self.global_best: List[float] = []
        self.global_best_fitness = float('inf')
        self._init_swarm()
    
    def _init_swarm(self):
        """Initialize swarm."""
        import random
        for _ in range(self.num_particles):
            pos = [random.uniform(-5, 5) for _ in range(self.dim)]
            vel = [random.uniform(-1, 1) for _ in range(self.dim)]
            self.particles.append(Particle(pos[:], vel[:], pos[:], float('inf')))
        
        self.global_best = self.particles[0].position[:]
    
    def optimize_step(self, fitness_func) -> float:
        """
        Execute one optimization step.
        
        Args:
            fitness_func: Fitness function
        
        Returns:
            Best fitness
        """
        import random
        for p in self.particles:
            fitness = fitness_func(p.position)
            
            if fitness < p.best_fitness:
                p.best_fitness = fitness
                p.best_position = p.position[:]
            
            if fitness < self.global_best_fitness:
                self.global_best_fitness = fitness
                self.global_best = p.position[:]
        
        # Update velocities and positions
        for p in self.particles:
            for i in range(self.dim):
                r1 = random.random()
                r2 = random.random()
                
                p.velocity[i] = (self.w * p.velocity[i] +
                                self.c1 * r1 * (p.best_position[i] - p.position[i]) +
                                self.c2 * r2 * (self.global_best[i] - p.position[i]))
                
                p.position[i] += p.velocity[i]
        
        return self.global_best_fitness


class SwarmDiversityTracker:
    """
    Track swarm diversity.
    """
    
    def __init__(self):
        pass
    
    def diversity(self, particles: List[Particle]) -> float:
        """
        Compute swarm diversity.
        
        Args:
            particles: Particles
        
        Returns:
            Diversity
        """
        if not particles:
            return 0.0
        
        # Mean position
        dim = len(particles[0].position)
        mean = [0.0] * dim
        for p in particles:
            for i in range(dim):
                mean[i] += p.position[i]
        
        n = len(particles)
        mean = [m / n for m in mean]
        
        # Average distance from mean
        total_dist = 0.0
        for p in particles:
            dist = sum((p.position[i] - mean[i])**2 for i in range(dim)) ** 0.5
            total_dist += dist
        
        return total_dist / n
    
    def is_converged(self, particles: List[Particle],
                    threshold: float = 0.01) -> bool:
        """
        Check if swarm converged.
        
        Args:
            particles: Particles
            threshold: Threshold
        
        Returns:
            True if converged
        """
        return self.diversity(particles) < threshold


class QuantumSwarmIntelligence:
    """
    Unified quantum swarm controller.
    """
    
    def __init__(self, num_particles: int = 30, dim: int = 2):
        self.classical_swarm = SwarmOptimizer(num_particles, dim)
        self.quantum_particles: List[QuantumParticle] = []
        self.diversity_tracker = SwarmDiversityTracker()
        self.iteration = 0
        
        for _ in range(num_particles):
            self.quantum_particles.append(QuantumParticle(dim))
    
    def optimize(self, fitness_func, max_iter: int = 100) -> Dict:
        """
        Optimize.
        
        Args:
            fitness_func: Fitness function
            max_iter: Max iterations
        
        Returns:
            Results
        """
        for _ in range(max_iter):
            self.classical_swarm.optimize_step(fitness_func)
            
            # Update quantum particles
            for qp in self.quantum_particles:
                qp.quantum_update(self.classical_swarm.global_best)
            
            self.iteration += 1
        
        return {
            "best_fitness": self.classical_swarm.global_best_fitness,
            "best_position": self.classical_swarm.global_best[:3],
            "iterations": self.iteration
        }
    
    def qsi_summary(self) -> Dict:
        """Get summary."""
        return {
            "particles": self.classical_swarm.num_particles,
            "iterations": self.iteration,
            "diversity": self.diversity_tracker.diversity(self.classical_swarm.particles)
        }
